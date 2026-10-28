"""Record and compare compact static audit observations; never execute audited code."""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

MAX_BYTES = 10_000_000
PILLARS = {
    "verification",
    "orientation",
    "static_guardrails",
    "workflow_entry_points",
    "automatic_triggers",
    "pipeline_parity",
    "doc_hygiene",
}
STATES = {"pass", "fail", "unknown", "error", "not_applicable"}
LABEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
CHECK_ID = re.compile(r"[A-Z]{3}-(?:[A-Z])?[0-9]{2}\Z")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def safe_file(path, root=None):
    path = Path(path).absolute()
    if path.suffix != ".json" or path.name.startswith(".env"):
        raise ValueError("An explicit non-secret JSON file is required")
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise ValueError("Symlinked inputs are not accepted")
    if root is not None and not path.resolve().is_relative_to(root):
        raise ValueError("The report must be inside the selected repository")
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Input is missing, not a regular file, or exceeds the size limit")
    return path


def load_json(path, root=None):
    path = safe_file(path, root)
    data = path.read_bytes()
    try:
        value = json.loads(data)
    except (ValueError, UnicodeError) as error:
        raise ValueError("Invalid JSON input") from error
    if not isinstance(value, dict):
        raise ValueError("A JSON object is required")
    return value, digest(data)


def git(root, *arguments):
    command = ["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", "--no-pager", "-C", str(root), *arguments]
    result = subprocess.run(
        command, capture_output=True, timeout=30, check=False, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"}
    )
    if result.returncode or len(result.stdout) > MAX_BYTES:
        raise ValueError("Local Git observation failed or exceeded its output bound")
    return result.stdout


def fingerprint_engine(root, generated_at):
    root = Path(root).absolute()
    if any(parent.is_symlink() for parent in (root, *root.parents)):
        raise ValueError("Symlinked engine roots are not accepted")
    required = [
        root / relative
        for relative in (
            "scripts/audit.py",
            "scripts/run_checks.py",
            "scripts/score.py",
            "checks/catalog.yaml",
            "schema/report.schema.json",
        )
    ]
    if not all(path.is_file() for path in required):
        raise ValueError("The selected engine is incomplete")
    sources = sorted(set((root / "scripts").glob("*.py")) | set((root / "schema").glob("*.json")))
    sources += [path for path in (root / "requirements.txt", root / "uv.lock") if path.is_file()]
    catalogs = sorted((root / "checks").glob("*.yaml"))
    hashes = []
    for group in (sources, catalogs):
        entries = []
        for path in group:
            if (
                any(parent.is_symlink() for parent in (path, *path.parents))
                or not path.resolve().is_relative_to(root)
                or path.stat().st_size > MAX_BYTES
            ):
                raise ValueError("Unsafe or oversized engine input")
            if path.stat().st_mtime > generated_at.timestamp() + 1:
                raise ValueError("Engine files changed after the report; generate a fresh audit before recording")
            entries.append([path.relative_to(root).as_posix(), digest(path.read_bytes())])
        hashes.append(digest(encoded(entries)))
    return {"engine": hashes[0], "catalog": hashes[1]}


def normalized_checks(items):
    if not isinstance(items, list):
        raise ValueError("Findings must be a list")
    output = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Invalid finding")
        check, component = item.get("check_id"), item.get("component", "repo")
        if not isinstance(check, str) or not CHECK_ID.fullmatch(check):
            raise ValueError("Invalid check identifier")
        if not isinstance(component, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,200}", component):
            raise ValueError("Invalid component identifier")
        state, source = item.get("status"), item.get("source", "script")
        if state not in STATES or source not in {"script", "llm"}:
            raise ValueError("Invalid finding state or source")
        key = check + "@" + component
        if key in output:
            raise ValueError("Duplicate finding identifier")
        output[key] = {"status": state, "source": source}
    return output


def report_projection(report):
    for field in ("tool", "score", "repo"):
        if not isinstance(report.get(field), dict):
            raise ValueError("Report " + field + " must be an object")
    if not isinstance(report.get("pillars"), list) or not all(isinstance(item, dict) for item in report["pillars"]):
        raise ValueError("Report pillars must be a list of objects")
    if not isinstance(report.get("infra", {}), dict):
        raise ValueError("Report infrastructure must be an object")
    if report.get("schema_version") != "0.1" or report.get("tool", {}).get("name") != "harness-audit":
        raise ValueError("Unsupported audit report schema or tool")
    for field in ("version", "catalog_version"):
        value = report["tool"].get(field)
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9._+-]{1,64}", value):
            raise ValueError("Invalid tool version metadata")
    score = report.get("score", {}).get("final")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError("Invalid audit score")
    levels = {}
    for item in report.get("pillars", []):
        name, level = item.get("pillar"), item.get("level")
        if name not in PILLARS or name in levels or type(level) is not int or level not in range(4):
            raise ValueError("Invalid or duplicate pillar level")
        levels[name] = level
    if set(levels) != PILLARS:
        raise ValueError("Every pillar level is required")
    findings = normalized_checks(report.get("findings"))
    if not findings:
        raise ValueError("An empty audit is not a comparable observation")
    limitations = report.get("limitations", [])
    if not isinstance(limitations, list) or not all(isinstance(item, str) for item in limitations):
        raise ValueError("Invalid report limitations")
    return {
        "score": score,
        "levels": levels,
        "checks": findings,
        "infrastructure_checks": normalized_checks(report.get("infra", {}).get("checks", [])),
        "limitations": {
            "count": len(limitations),
            "sha256": digest(encoded(limitations)),
            "unanswered_judgments": sorted(key for key, value in findings.items() if value == {"status": "unknown", "source": "llm"}),
        },
    }


def private_directory(path):
    if path.is_symlink():
        raise ValueError("Symlinked storage is not accepted")
    if path.exists():
        if not path.is_dir() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
            raise ValueError("Existing storage must be an owner-only directory; permissions were not changed")
    else:
        path.mkdir(mode=0o700)


def record(args):
    root = Path(args.repo).absolute()
    if not root.is_dir() or any(parent.is_symlink() for parent in (root, *root.parents)):
        raise ValueError("Select a regular repository root without symlinks")
    if not LABEL.fullmatch(args.label):
        raise ValueError("The label must be a safe short non-secret name")
    report, report_hash = load_json(args.report, root)
    projection = report_projection(report)
    try:
        generated = datetime.fromisoformat(report["generated_at"].replace("Z", "+00:00"))
    except (KeyError, ValueError, TypeError) as error:
        raise ValueError("A valid audit observation timestamp is required") from error
    if generated.tzinfo is None or generated.timestamp() > datetime.now(UTC).timestamp() + 300:
        raise ValueError("The report timestamp must have a valid explicit timezone")
    engine = fingerprint_engine(args.engine_root, generated)
    head = git(root, "rev-parse", "HEAD").decode().strip()
    observed_commit = report.get("repo", {}).get("commit", "")
    if not re.fullmatch(r"[0-9a-f]{7,40}", observed_commit) or not head.startswith(observed_commit):
        raise ValueError("The report commit does not match the selected checkout")
    clone_mode = report["repo"].get("clone_mode")
    if clone_mode not in {"full", "shallow", "blobless", "local"}:
        raise ValueError("Invalid clone mode")
    if git(root, "ls-files", "--", ".data").strip():
        raise ValueError("Storage content is tracked; nothing was changed")
    ignored = subprocess.run(
        [
            "git",
            "-c",
            "core.fsmonitor=false",
            "-C",
            str(root),
            "check-ignore",
            "-q",
            "--no-index",
            ".data/storage/local/file/harness-audit/history/probe.json",
        ],
        capture_output=True,
        timeout=30,
    )
    if ignored.returncode != 0:
        raise ValueError("The selected repository must ignore .data/ before recording")
    status = git(root, "status", "--porcelain=v1", "-z")
    difference = git(root, "diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD")
    now = datetime.now(UTC)
    receipt = {
        "schema_version": 1,
        "label": args.label,
        "recorded_at": now.isoformat(),
        "report_generated_at": report["generated_at"],
        "report_sha256": report_hash,
        "report_schema": report["schema_version"],
        "tool": {key: report["tool"][key] for key in ("name", "version", "catalog_version")},
        "repository_id": digest(git(root, "rev-list", "--max-parents=0", "HEAD")),
        "commit": head,
        "clone_mode": clone_mode,
        "fingerprints": engine,
        "working_tree_at_recording": {"dirty": bool(status), "status_sha256": digest(status), "tracked_diff_sha256": digest(difference)},
        "provenance_limit": "Working-tree state is captured at recording, not embedded by the auditor. Untracked contents are not fingerprinted. Engine fingerprints are current at recording and files must predate the report; this is not attestation of the historical process.",
        **projection,
    }
    directory = root
    for component in (".data", "storage", "local", "file", "harness-audit", "history", now.strftime("%Y-%m-%d")):
        directory = directory / component
        private_directory(directory)
    directory = directory / (now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12])
    directory.mkdir(mode=0o700)
    destination = directory / "record.json"
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {"record": destination.relative_to(root).as_posix(), "score": projection["score"], "label": args.label}


def validate_record(value):
    if value.get("schema_version") != 1 or value.get("report_schema") != "0.1":
        raise ValueError("Unsupported history schema")
    score = value.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError("Invalid history score")
    levels = value.get("levels")
    if (
        not isinstance(levels, dict)
        or set(levels) != PILLARS
        or any(type(level) is not int or level not in range(4) for level in levels.values())
    ):
        raise ValueError("Invalid history pillar levels")
    fingerprints = value.get("fingerprints")
    if not isinstance(fingerprints, dict) or set(fingerprints) != {"engine", "catalog"}:
        raise ValueError("Invalid history fingerprints")
    for fingerprint in [value.get("repository_id"), value.get("report_sha256"), *fingerprints.values()]:
        if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
            raise ValueError("Invalid history fingerprint")
    if value.get("clone_mode") not in {"full", "shallow", "blobless", "local"}:
        raise ValueError("Invalid history clone mode")
    tool = value.get("tool")
    if not isinstance(tool, dict) or tool.get("name") != "harness-audit" or set(tool) != {"name", "version", "catalog_version"}:
        raise ValueError("Invalid history tool metadata")
    for field in ("checks", "infrastructure_checks"):
        checks = value.get(field)
        if not isinstance(checks, dict) or (field == "checks" and not checks):
            raise ValueError("Invalid or empty history checks")
        for key, finding in checks.items():
            check, separator, component = key.partition("@")
            if not separator or not isinstance(finding, dict) or set(finding) != {"status", "source"}:
                raise ValueError("Invalid history finding")
            normalized_checks([{"check_id": check, "component": component, **finding}])
    limitations = value.get("limitations")
    if not isinstance(limitations, dict) or type(limitations.get("count")) is not int or limitations["count"] < 0:
        raise ValueError("Invalid history limitations")
    pending = limitations.get("unanswered_judgments")
    if not isinstance(pending, list) or not all(isinstance(item, str) and item in value["checks"] for item in pending):
        raise ValueError("Invalid history judgment coverage")


def check_delta(before, after):
    shared = before.keys() & after.keys()
    return {
        "added": [{"check": key, **after[key]} for key in sorted(after.keys() - before.keys())],
        "removed": [{"check": key, **before[key]} for key in sorted(before.keys() - after.keys())],
        "changed": [
            {
                "check": key,
                "before": before[key]["status"],
                "after": after[key]["status"],
                "source_before": before[key]["source"],
                "source_after": after[key]["source"],
            }
            for key in sorted(shared)
            if before[key] != after[key]
        ],
    }


def compare(args):
    before, _ = load_json(args.before)
    after, _ = load_json(args.after)
    validate_record(before)
    validate_record(after)
    for field in ("repository_id", "report_schema", "tool", "fingerprints", "clone_mode"):
        if before[field] != after[field]:
            raise ValueError("Incomparable history records: different " + field)
    changes = check_delta(before["checks"], after["checks"])
    warnings = [
        "Engine fingerprints describe files at recording, not attested historical execution. Working-tree provenance remains limited to the receipt's disclosed Git observations."
    ]
    if before["limitations"]["unanswered_judgments"] or after["limitations"]["unanswered_judgments"]:
        warnings.append("Unanswered judgment checks remain; the score is not a complete runtime or security assessment.")
    if any(item["source_before"] == "llm" or item["source_after"] == "llm" for item in changes["changed"]):
        warnings.append("Judgment verdicts or coverage changed; separate them from mechanical regressions.")
    return {
        "compatible": True,
        "score": {"before": before["score"], "after": after["score"], "delta": after["score"] - before["score"]},
        "levels": [
            {"pillar": key, "before": before["levels"][key], "after": after["levels"][key]}
            for key in sorted(PILLARS)
            if before["levels"][key] != after["levels"][key]
        ],
        "checks": changes,
        "infrastructure_checks": check_delta(before["infrastructure_checks"], after["infrastructure_checks"]),
        "mechanical_regressions": [
            item["check"]
            for item in changes["changed"]
            if item["before"] == "pass" and item["after"] in {"fail", "error"} and item["source_before"] == item["source_after"] == "script"
        ],
        "limitations": {
            "before_count": before["limitations"]["count"],
            "after_count": after["limitations"]["count"],
            "before_unanswered": before["limitations"]["unanswered_judgments"],
            "after_unanswered": after["limitations"]["unanswered_judgments"],
        },
        "warnings": warnings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    recorder = commands.add_parser("record", help="Record an explicit fresh audit into ignored local history")
    recorder.add_argument("--repo", required=True)
    recorder.add_argument("--report", required=True)
    recorder.add_argument("--label", required=True)
    recorder.add_argument("--engine-root", default=str(Path(__file__).resolve().parents[1] / "skills/harness-audit"))
    comparator = commands.add_parser("compare", help="Compare compatible static observations; reject metric drift")
    comparator.add_argument("before")
    comparator.add_argument("after")
    args = parser.parse_args(argv)
    try:
        result = record(args) if args.operation == "record" else compare(args)
    except (ValueError, OSError, subprocess.SubprocessError, TypeError, KeyError) as error:
        print(json.dumps({"error": str(error)[:400]}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
