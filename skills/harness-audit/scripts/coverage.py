"""Bounded, identity-checked reads of tracked regular files."""

from __future__ import annotations

import errno
import fnmatch
import hashlib
import json
import os
import stat
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
MAX_CANDIDATE_PATHS = 2048
TOPIC_IDS = ("code_standards", "testing", "ci_build", "security", "dependencies", "mcp", "skills_extensions")
TOPIC_ADAPTERS = {"python", "node", "repository"}
SUPPORTS_SAFE_DIR_FD = (
    hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY") and os.open in os.supports_dir_fd and os.stat in os.supports_dir_fd
)


@dataclass
class ReadBudget:
    max_file_bytes: int = MAX_FILE_BYTES
    max_total_bytes: int = MAX_TOTAL_BYTES
    max_candidate_paths: int = MAX_CANDIDATE_PATHS
    bytes_read: int = 0
    candidates_seen: int = 0


@dataclass(frozen=True)
class ReadResult:
    outcome: str
    content: bytes | None = None
    sha256: str | None = None
    size: int = 0
    reason: str | None = None


@dataclass(frozen=True)
class ReceiptResult:
    outcome: str
    reason_code: str | None = None


class _ReadRejected(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _file_state(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _open_parent(root: Path, parts: tuple[str, ...]) -> tuple[int, str]:
    if not SUPPORTS_SAFE_DIR_FD:
        raise _ReadRejected("unsupported_platform")

    directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0))
    try:
        for component in parts[:-1]:
            before = os.stat(component, dir_fd=directory_fd, follow_symlinks=False)
            if stat.S_ISLNK(before.st_mode):
                raise _ReadRejected("symlink_rejected")
            if not stat.S_ISDIR(before.st_mode):
                raise _ReadRejected("not_directory")
            child_fd = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
                dir_fd=directory_fd,
            )
            opened = os.fstat(child_fd)
            if _file_state(before) != _file_state(opened):
                os.close(child_fd)
                raise _ReadRejected("identity_changed")
            os.close(directory_fd)
            directory_fd = child_fd
        return directory_fd, parts[-1]
    except Exception:
        os.close(directory_fd)
        raise


def _read_limited(file_fd: int, limit: int) -> bytes:
    chunks = []
    remaining = limit + 1
    while remaining:
        chunk = os.read(file_fd, min(64 * 1024, remaining))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def make_provenance(revision: str, sources: list[dict[str, str]], method: str, observed_at: datetime) -> dict:
    """Return source identity metadata without copying repository content."""
    if not revision or not method or observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("revision, method, and timezone-aware observed_at are required")
    safe_sources = []
    for source in sources:
        path = source.get("path", "")
        parts = path.split("/")
        digest = source.get("sha256", "")
        locator = source.get("locator", "")
        if not path or path.startswith("/") or any(part in ("", ".", "..") for part in parts):
            raise ValueError("source path must be relative and traversal-free")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("source digest must be lowercase SHA-256")
        if not locator:
            raise ValueError("source locator is required")
        safe_sources.append({"path": path, "sha256": digest, "locator": locator})

    moment = observed_at.astimezone(UTC)
    timestamp = moment.isoformat(timespec="microseconds" if moment.microsecond else "seconds").replace("+00:00", "Z")
    return {"revision": revision, "sources": safe_sources, "method": method, "observed_at": timestamp}


def classify_freshness(provenance: Mapping | None, current_revision: str | None, current_sources: Mapping[str, str] | None) -> str:
    """Classify an observation against the current revision and source digests."""
    if not provenance or not current_revision or not current_sources:
        return "unknown"
    observed_revision = provenance.get("revision")
    sources = provenance.get("sources")
    if not observed_revision or not isinstance(sources, list) or not sources:
        return "unknown"
    if observed_revision != current_revision:
        return "stale"

    for source in sources:
        path, digest = source.get("path"), source.get("sha256")
        if not path or not digest or path not in current_sources:
            return "unknown"
        if digest != current_sources[path]:
            return "stale"
    return "current"


def current_observations(observations: Collection[Mapping]) -> list[Mapping]:
    """Return current observations without rewriting stale or unknown history."""
    return [observation for observation in observations if observation.get("freshness") == "current"]


def validate_topic_catalog(topic_catalog: Mapping, existing_check_ids: Collection[str]) -> list[dict]:
    """Validate and return the versioned unscored topic catalog in its pinned order."""
    if topic_catalog.get("version") != 1 or topic_catalog.get("scope") != "unscored-static-observations":
        raise ValueError("unsupported coverage topic catalog")
    topics = topic_catalog.get("topics")
    if not isinstance(topics, list) or any(not isinstance(topic, dict) for topic in topics):
        raise ValueError("coverage topic catalog must contain topic objects")
    by_id = {topic.get("id"): topic for topic in topics}
    if len(by_id) != len(topics) or set(by_id) != set(TOPIC_IDS):
        raise ValueError("coverage topic IDs do not match the pinned seven-topic set")

    for topic_id in TOPIC_IDS:
        topic = by_id[topic_id]
        adapters = topic.get("adapters")
        check_ids = topic.get("check_ids")
        locators = topic.get("locators")
        limits = topic.get("limits")
        if not isinstance(adapters, list) or not adapters or not set(adapters) <= TOPIC_ADAPTERS:
            raise ValueError("coverage topic adapters are invalid")
        if not isinstance(check_ids, list) or len(check_ids) != len(set(check_ids)) or not set(check_ids) <= set(existing_check_ids):
            raise ValueError("coverage topic check references are invalid")
        if not isinstance(locators, list) or not locators or not all(isinstance(locator, str) and locator for locator in locators):
            raise ValueError("coverage topic locators are invalid")
        if not isinstance(limits, dict):
            raise ValueError("coverage topic limits are invalid")
        max_files, max_bytes = limits.get("max_files"), limits.get("max_bytes")
        if not isinstance(max_files, int) or not 0 < max_files <= MAX_CANDIDATE_PATHS:
            raise ValueError("coverage topic file limit is invalid")
        if not isinstance(max_bytes, int) or not 0 < max_bytes <= MAX_TOTAL_BYTES:
            raise ValueError("coverage topic byte limit is invalid")
    return [by_id[topic_id] for topic_id in TOPIC_IDS]


def collect_topic_sources(root: Path, topic: Mapping, tracked_paths: Collection[str], budget: ReadBudget) -> dict:
    """Collect digest-only source locators for one catalog topic under shared budgets."""
    topic_id = topic["id"]
    locators = topic["locators"]
    limits = topic["limits"]
    candidates = sorted(path for path in tracked_paths if any(fnmatch.fnmatchcase(path, locator) for locator in locators))
    remaining_paths = max(0, min(limits["max_files"], budget.max_candidate_paths - budget.candidates_seen))
    remaining_bytes = max(0, min(limits["max_bytes"], budget.max_total_bytes - budget.bytes_read))
    local_budget = ReadBudget(
        max_file_bytes=budget.max_file_bytes,
        max_total_bytes=remaining_bytes,
        max_candidate_paths=remaining_paths,
    )
    sources = []
    reasons = set()
    selected = candidates[:remaining_paths]
    if len(candidates) > len(selected):
        reasons.add("budget_exceeded")
    for path in selected:
        result = read_tracked_file(root, path, tracked_paths, local_budget)
        if result.outcome == "read":
            sources.append({"path": path, "sha256": result.sha256, "locator": "file"})
        else:
            reasons.add(result.reason or "read_failed")

    budget.bytes_read += local_budget.bytes_read
    budget.candidates_seen += local_budget.candidates_seen
    return {
        "topic_id": topic_id,
        "check_ids": list(topic["check_ids"]),
        "sources": sources,
        "candidate_count": len(selected),
        "outcome": "partial" if reasons else "complete",
        "reason_codes": sorted(reasons),
        "limits": {"max_files": limits["max_files"], "max_bytes": limits["max_bytes"]},
    }


def collect_component_observations(
    root: Path,
    components: Collection[Mapping],
    tracked_paths: Collection[str],
    topic_catalog: Collection[Mapping],
    budget: ReadBudget,
    revision: str | None,
    observed_at: datetime,
) -> tuple[list[dict], list[str]]:
    """Build declared observations from bounded topic locator matches."""
    observations = []
    reason_codes = set()
    for component in components:
        component_path = component["path"]
        adapter = component["ecosystem"]
        for topic in topic_catalog:
            if adapter not in topic["adapters"] and "repository" not in topic["adapters"]:
                continue
            scoped_topic = topic
            if component_path != ".":
                scoped_topic = {**topic, "locators": [f"{component_path}/{locator}" for locator in topic["locators"]]}
            result = collect_topic_sources(root, scoped_topic, tracked_paths, budget)
            reason_codes.update(result["reason_codes"])
            if not result["sources"]:
                continue

            provenance = make_provenance(revision or "unknown", result["sources"], "catalog_locator", observed_at)
            current_revision = revision if revision and revision != "0000000" else None
            current_sources = {source["path"]: source["sha256"] for source in result["sources"]}
            freshness = classify_freshness(provenance, current_revision, current_sources)
            observations.append(
                {
                    "id": f"{component['id']}:{topic['id']}",
                    "component_id": component["id"],
                    "topic_id": topic["id"],
                    "check_ids": list(topic["check_ids"]),
                    "applicability": "applicable",
                    "evidence": "declared",
                    "freshness": freshness,
                    "provenance": provenance,
                    "receipt": {"outcome": "absent"},
                    "limitations": [],
                }
            )
    observations.sort(key=lambda observation: (observation["component_id"], observation["topic_id"]))
    return observations, sorted(reason_codes)


def bind_provenance(
    observation: Mapping,
    provenance: Mapping,
    current_revision: str | None,
    current_sources: Mapping[str, str] | None,
) -> dict:
    """Add provenance and computed freshness while preserving the original evidence label."""
    return {
        **observation,
        "provenance": dict(provenance),
        "freshness": classify_freshness(provenance, current_revision, current_sources),
    }


def classify_receipt(
    raw_receipt: bytes | None,
    current_revision: str | None,
    current_sources: Mapping[str, str] | None,
    max_bytes: int = MAX_FILE_BYTES,
) -> ReceiptResult:
    """Classify an untrusted local receipt without admitting execution claims."""
    if raw_receipt is None:
        return ReceiptResult("absent")
    if not isinstance(raw_receipt, bytes):
        return ReceiptResult("invalid", "invalid_format")
    if len(raw_receipt) > max_bytes:
        return ReceiptResult("invalid", "oversized")
    try:
        receipt = json.loads(raw_receipt)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return ReceiptResult("invalid", "invalid_format")
    if not isinstance(receipt, dict) or receipt.get("status") not in {"success", "partial", "failed"}:
        return ReceiptResult("invalid", "invalid_format")
    if receipt["status"] in {"partial", "failed"}:
        return ReceiptResult(receipt["status"], f"self_reported_{receipt['status']}")

    revision = receipt.get("revision")
    sources = receipt.get("sources")
    if current_revision and isinstance(revision, str) and revision != current_revision:
        return ReceiptResult("stale", "revision_mismatch")
    if current_revision and current_sources and isinstance(revision, str) and isinstance(sources, list) and sources:
        freshness = classify_freshness({"revision": revision, "sources": sources}, current_revision, current_sources)
        if freshness == "stale":
            return ReceiptResult("stale", "source_mismatch")
    return ReceiptResult("present_unverified", "issuer_unverified")


def read_tracked_file(root: Path, relative_path: str, tracked_paths: Collection[str], budget: ReadBudget) -> ReadResult:
    """Read one tracked regular file without following links or exceeding budgets."""
    if budget.candidates_seen >= budget.max_candidate_paths:
        return ReadResult("unknown", reason="budget_exceeded")
    budget.candidates_seen += 1

    if not isinstance(relative_path, str) or not relative_path or "\x00" in relative_path:
        return ReadResult("unknown", reason="invalid_path")
    raw_parts = relative_path.split("/")
    if relative_path.startswith("/") or any(part in ("", ".", "..") for part in raw_parts):
        return ReadResult("unknown", reason="path_escape")
    if not PurePosixPath(relative_path).parts or relative_path not in tracked_paths:
        return ReadResult("unknown", reason="untracked")

    max_read = min(budget.max_file_bytes, budget.max_total_bytes - budget.bytes_read)
    if max_read < 0:
        return ReadResult("unknown", reason="budget_exceeded")

    root_path = Path(root)
    file_fd = None
    directory_fd = None
    try:
        root_path = root_path.resolve(strict=True)
        if not root_path.is_dir():
            return ReadResult("unknown", reason="invalid_root")
        directory_fd, filename = _open_parent(root_path, tuple(raw_parts))
        before = os.stat(filename, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISLNK(before.st_mode):
            raise _ReadRejected("symlink_rejected")
        if not stat.S_ISREG(before.st_mode):
            raise _ReadRejected("not_regular_file")
        if before.st_size > max_read:
            raise _ReadRejected("budget_exceeded")

        file_fd = os.open(
            filename,
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
            dir_fd=directory_fd,
        )
        opened = os.fstat(file_fd)
        if not stat.S_ISREG(opened.st_mode) or _file_state(before) != _file_state(opened):
            raise _ReadRejected("identity_changed")

        content = _read_limited(file_fd, max_read)
        if len(content) > max_read:
            raise _ReadRejected("budget_exceeded")
        after_fd = os.fstat(file_fd)
        after_path = os.stat(filename, dir_fd=directory_fd, follow_symlinks=False)
        if _file_state(opened) != _file_state(after_fd) or _file_state(opened) != _file_state(after_path):
            raise _ReadRejected("identity_changed")

        budget.bytes_read += len(content)
        return ReadResult("read", content, hashlib.sha256(content).hexdigest(), len(content))
    except _ReadRejected as exc:
        return ReadResult("unknown", reason=exc.reason)
    except PermissionError:
        return ReadResult("unknown", reason="permission_denied")
    except OSError as exc:
        reason = "symlink_rejected" if exc.errno == errno.ELOOP else "read_failed"
        return ReadResult("unknown", reason=reason)
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if directory_fd is not None:
            os.close(directory_fd)
