#!/usr/bin/env python3
"""Read-only probe of the harness-audit catalog, infra checks, stack detection and report renderer.

Measures which scan topics have check IDs, whether Go/Rust have adapters and whether report output carries categories.

Rules (do not relax without asking the owner):
  - Read-only: never install, write (except --out), or change state.
  - No secrets: never read keys, tokens, credentials, browser profile data beyond manifests.
  - Bounded: every command has a timeout; every directory walk has a depth limit.
  - A probe never aborts the scan; failures land in the probe's `error` field.
  - The raw JSON may contain host/user/repo names: keep it local, commit counts only.

  - Retention: a default run writes data/findings.json only (--evaluation-only is an alias). Raw evidence is
    kept only after an explicit adopt (scaffold_discovery.py --adopt) and with --retain, which must declare at
    least one output file with --declare REL (exact relative path under --source-root; no globs). Streams are
    retained only as declared files.
  - Logging: finite-mode Lean Logging through lean_log; every record goes through emit, and
    command output, secrets, and absolute private paths are never logged.

  probe.py                              # table on stdout, findings only, nothing retained
  probe.py --retain --declare results/out.json --source-root DIR   # retained run (adopted store required)
  probe.py --evaluation-only --out p.json                 # + full JSON
  probe.py --evaluation-only --summary                    # + counts-only summary line (numbers, booleans, outcomes)
  probe.py --evaluation-only --only os -v                 # subset; -v shows DEBUG on the console, -vv TRACE

Run as `uv run --python 3.14 python probe.py ...`.
"""
import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# BEGIN asset-bootstrap
import os
import sys
from pathlib import Path

SKILL = "discovery-poc"
MARKER = Path("shared") / "scripts" / "layout.py"
SYNC_HINT = "run the sync-agent-assets skill to deploy current shared assets"


def _fail(message, required=()):
    needed = f" (needed: {', '.join(required)})" if required else ""
    sys.stderr.write(f"asset_root_unresolved: {message}{needed}; {SYNC_HINT}\n")
    raise SystemExit(2)


def find_asset_root(env=None, start=None, home=None, required=()):
    """Return (asset_root, source) with source one of override, repo, deployed."""
    env = os.environ if env is None else env
    override = env.get("AGENTS_ASSET_ROOT")
    if override:
        root = Path(override)
        if not (root / MARKER).is_file():
            _fail("AGENTS_ASSET_ROOT is set but is not an asset root (missing shared/scripts/layout.py)", required)
        return root, "override"
    here = Path(start if start is not None else sys.argv[0] or __file__).resolve()
    for ancestor in here.parents:
        if (ancestor / ".git").exists() and (ancestor / "agents" / MARKER).is_file():
            return ancestor / "agents", "repo"
    deployed = Path(home if home is not None else Path.home()) / ".agents"
    if (deployed / MARKER).is_file():
        return deployed, "deployed"
    _fail("no asset root found (checked AGENTS_ASSET_ROOT, the repository agents/ and ~/.agents)", required)


def bootstrap(required=(), env=None, start=None, home=None):
    """Put shared and skill scripts on sys.path; exit 2 naming any required module that is missing."""
    root, source = find_asset_root(env, start, home, required)
    shared = root / "shared" / "scripts"
    sys.path.insert(0, str(shared))
    import layout

    search = [shared]
    try:
        search.insert(0, layout.skill_dir(SKILL, root) / "scripts")
    except layout.LayoutUnresolved:
        pass
    sys.path[:0] = [str(p) for p in search]
    for name in required:
        if not any((p / f"{name}.py").is_file() for p in search):
            _fail(f"required module '{name}' is not in the asset root")
    return root, source
# END asset-bootstrap

ASSET_ROOT, ROOT_SOURCE = bootstrap(("lean_log", "discovery_log", "findings", "retention_inventory",
                                     "storage_preflight", "retention_writer"))

import lean_log  # noqa: E402
import retention_inventory  # noqa: E402
import discovery_log  # noqa: E402
import findings  # noqa: E402
import storage_preflight  # noqa: E402
import retention_writer  # noqa: E402

SAMPLE = 10
HOME = Path.home()
BUNDLE = Path(__file__).resolve().parent.parent
LOGGER = logging.getLogger("probe")
SUBJECT = "harness-audit scan and report coverage"
ROOT = next(p for p in BUNDLE.parents if (p / ".git").exists() and (p / "docs").is_dir())
SKILL_DIR = "skills/harness-audit"


def run(cmd, timeout=20):
    """stdout text, or None if the tool is missing, times out, or prints nothing."""
    if {Path(cmd[0]).name, Path(cmd[0]).stem.lower()} & storage_preflight.FORBIDDEN_EXECUTABLES:
        lean_log.emit(LOGGER, logging.WARNING, "probe.skipped", tool=Path(cmd[0]).name, reason="prohibited")
        return None
    if not shutil.which(cmd[0]):
        lean_log.emit(LOGGER, logging.DEBUG, "probe.skipped", tool=cmd[0], reason="not on PATH")
        return None
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL,
                           env={**os.environ, "LC_ALL": "C", "NO_COLOR": "1"})
    except (subprocess.TimeoutExpired, OSError) as exc:
        lean_log.emit(LOGGER, logging.DEBUG, "probe.skipped", tool=cmd[0], reason=type(exc).__name__)
        return None
    out = p.stdout.strip()
    lean_log.emit(LOGGER, logging.DEBUG, "probe.command", tool=cmd[0], rc=p.returncode,
                  seconds=round(time.monotonic() - t0, 2), bytes=len(out))
    return out or None


def lines(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def res(present, items=None, version=None, **extra):
    items = items or []
    return {"present": bool(present), "count": len(items), "version": version, "sample": items[:SAMPLE], **extra}


def tracked_text(rel):
    """Text of one repository file; empty when missing. Only fixed in-repo paths are read."""
    path = ROOT / SKILL_DIR / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def definitions():
    """(check id, definition text) for every core catalog check and every infrastructure check."""
    out = []
    catalog = tracked_text("checks/catalog.yaml")
    for block in re.split(r"(?m)^  - id: ", catalog)[1:]:
        out.append((block.split()[0], block))
    for line in tracked_text("scripts/infra_checks.py").splitlines():
        m = re.match(r'\s+"(INF-[A-Z]\d+)": \(', line)
        if m:
            out.append((m.group(1), line))
    return out


def p_checks():
    defs = definitions()
    core = [i for i, _ in defs if not i.startswith("INF-")]
    infra = [i for i, _ in defs if i.startswith("INF-")]
    return res(defs, [i for i, _ in defs], None, core_check_ids=len(core), infra_check_ids=len(infra))


SCAN_TOPICS = {
    "secret_scanning": r"gitleaks|trufflehog|detect-secrets",
    "sast": r"semgrep|codeql|bandit|gosec|njsscan",
    "dependency_vulnerability": r"pip-audit|npm audit|osv-scanner|govulncheck|cargo[ -]audit|grype|trivy",
    "sbom": r"sbom|cyclonedx|spdx|syft",
    "license": r"licen[sc]e|scancode|\breuse\b",
    "go_lint": r"golangci|staticcheck|go vet",
    "rust_lint": r"clippy|rustfmt|cargo fmt",
    "coding_standards_doc": r"editorconfig|coding standard|style guide",
}


def p_scan_topics():
    defs = definitions()
    extra = {f"{topic}_check_ids": sum(1 for _, text in defs if re.search(pattern, text, re.I))
             for topic, pattern in SCAN_TOPICS.items()}
    return res(True, [], None, topics_without_checks=sum(1 for v in extra.values() if v == 0), **extra)


def p_adapters():
    stack = tracked_text("scripts/detect_stack.py")
    catalog = tracked_text("checks/catalog.yaml")
    applies = re.findall(r"(?m)^    applies_to: \[([^\]]*)\]", catalog)
    return res(True, [], None,
               go_rust_manifests_listed=bool(re.search(r'"go\.mod": "go"', stack) and re.search(r'"Cargo\.toml": "rust"', stack)),
               checks_applying_to_go_or_rust=sum(1 for a in applies if re.search(r"\b(go|rust)\b", a)),
               checks_applying_to_python_or_node=sum(1 for a in applies if re.search(r"\b(python|node)\b", a)))


def p_report():
    audit = tracked_text("scripts/audit.py")
    m = re.search(r"def render_md\(.*?(?=\n\ndef |\nclass |\Z)", audit, re.S)
    render = m.group(0) if m else ""
    schema = tracked_text("schema/report.schema.json")
    return res(bool(render), [], None,
               render_mentions_coverage="coverage" in render,
               render_mentions_category="categor" in render.lower(),
               render_groups_by_pillar="PILLAR_LABEL" in render,
               schema_category_keys=len(re.findall(r'"category"', schema)))


PROBES = {"checks": p_checks, "scan_topics": p_scan_topics, "adapters": p_adapters, "report": p_report}

EXIT_FINDINGS_INVALID = 1
RAW_STORE_MISSING = "raw_store_missing"
EXIT_INVENTORY_BLOCKED = 2
EXIT_PREFLIGHT_BLOCKED = 3
EXIT_RETENTION_INCOMPLETE = 5
PROBE_IDENTITY = {"name": "probe", "version": "0.1"}


def collection_result(results):
    """succeeded when no probe errored, failed when every probe did, partial otherwise."""
    errors = sum(1 for r in results.values() if r.get("error"))
    if not errors:
        return retention_writer.SUCCEEDED
    return retention_writer.FAILED if errors == len(results) else retention_writer.PARTIAL


def counts_summary(results, collection, retention):
    """Numeric and boolean fields per probe plus both outcomes, from in-memory results only (AC-21).
    String, list, and mapping fields are dropped, so no name, path, or version can be printed."""
    kept = findings.summary_from_rows(findings.rows_from_results(results))
    return {"summary": kept, "collectionOutcome": collection, "retentionOutcome": retention}


def print_summary(results, collection, retention):
    print("summary " + json.dumps(counts_summary(results, collection, retention), sort_keys=True))


def produce(declared, source_root, results, table):
    """Write the declared outputs this skeleton knows how to make: *.json is the result data, *.txt the
    printed table. A producer replaces this; a path it cannot make stays missing and is rejected."""
    for rel in declared:
        text = json.dumps({"probes": results}, indent=2, default=str) if rel.endswith(".json") else (
            table if rel.endswith(".txt") else None)
        if text is None:
            continue
        target = Path(source_root) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)


def main():
    global SAMPLE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    ap.add_argument("--only", help="comma list of probe keys or prefixes")
    ap.add_argument("--sample", type=int, default=SAMPLE)
    ap.add_argument("--list", action="store_true")
    modes = ap.add_mutually_exclusive_group()
    modes.add_argument("--evaluation-only", action="store_true",
                       help="alias of the default: write findings only, retain nothing")
    modes.add_argument("--retain", action="store_true",
                       help="retain declared outputs; needs an adopted raw store (scaffold_discovery.py --adopt)")
    ap.add_argument("--declare", action="append", default=[], metavar="REL",
                    help="exact relative output path under --source-root; repeat per file, no globs")
    ap.add_argument("--source-root", default=None, help="run-owned source root for declared files")
    ap.add_argument("--summary", action="store_true",
                    help="print a counts-only summary (numbers, booleans, both outcomes); read this, never retained files")
    ap.add_argument("--log-level", default=None, help="file log level, e.g. DEBUG")
    ap.add_argument("-v", "--verbose", action="count", default=0)
    ap.add_argument("-q", "--quiet", action="count", default=0)
    a = ap.parse_args()
    SAMPLE = a.sample
    mode = retention_inventory.resolve_mode(not a.retain)
    run_log = discovery_log.open_run("probe", sys.argv[1:], log_dir=BUNDLE / "logs", name="probe", logger=LOGGER,
                                     asset_root_source=ROOT_SOURCE)
    with run_log:
        if a.list:
            print("\n".join(PROBES))
            return 0
        lean_log.emit(LOGGER, logging.INFO, "retention.run.requested", mode=mode, declared=len(a.declare))
        if a.retain and not (BUNDLE / storage_preflight.RAW_STORE).is_dir():
            lean_log.emit(LOGGER, logging.ERROR, "retention.preflight.blocked", blocker=RAW_STORE_MISSING)
            run_log.exit_code = EXIT_FINDINGS_INVALID
            return EXIT_FINDINGS_INVALID
        inventory = retention_inventory.Inventory(mode)
        try:
            for declared in a.declare:
                inventory.declare(declared)
            inventory.require_nonempty()
        except retention_inventory.InventoryError as exc:
            lean_log.emit(LOGGER, logging.ERROR, "retention.preflight.blocked", blocker=exc.code)
            run_log.exit_code = EXIT_INVENTORY_BLOCKED
            return EXIT_INVENTORY_BLOCKED
        if mode == retention_inventory.NORMAL:
            lean_log.emit(LOGGER, logging.WARNING, "probe.advisory", **storage_preflight.BACKUP_SYNC_ADVISORY)
            lean_log.emit(LOGGER, logging.WARNING, "probe.advisory", **storage_preflight.LIFETIME_ADVISORY)
            blockers = storage_preflight.run_preflight(BUNDLE).blockers
            for blocker in blockers:
                lean_log.emit(LOGGER, logging.ERROR, "retention.preflight.blocked", blocker=blocker)
            if blockers:
                run_log.exit_code = EXIT_PREFLIGHT_BLOCKED
                return EXIT_PREFLIGHT_BLOCKED
            if not a.source_root:
                lean_log.emit(LOGGER, logging.ERROR, "retention.preflight.blocked", blocker="source_root_required")
                run_log.exit_code = EXIT_INVENTORY_BLOCKED
                return EXIT_INVENTORY_BLOCKED
        only = [s for s in (a.only or "").split(",") if s]
        results = {}
        for key, fn in PROBES.items():
            if only and not any(key == o or key.startswith(o + ".") for o in only):
                continue
            s = time.monotonic()
            discovery_log.record(LOGGER, "probe.start", probe=key)
            try:
                results[key] = fn()
            except Exception as exc:  # a probe must never abort the scan
                results[key] = {"present": False, "count": 0, "error": f"{type(exc).__name__}: {exc}"}
                discovery_log.record(LOGGER, "probe.failed", probe=key, reason=type(exc).__name__)
            results[key]["seconds"] = round(time.monotonic() - s, 2)
            if not results[key].get("error"):
                discovery_log.record(LOGGER, "probe.done", probe=key, seconds=results[key]["seconds"],
                                     metrics=len(findings.rows_from_results({key: results[key]})))
        table = [f"{'probe':30} {'present':8} {'count':>6}  version/notes"]
        for k, r in results.items():
            table.append(f"{k:30} {str(r['present']):8} {r.get('count', 0):>6}  {str(r.get('version') or r.get('error') or '')[:60]}")
        print("\n".join(table))
        try:
            findings.write_findings(BUNDLE / "data" / "findings.json", findings.rows_from_results(results),
                                    subject=SUBJECT)
        except findings.FindingsError as exc:
            discovery_log.record(LOGGER, "probe.failed", probe="findings", reason=exc.code)
            run_log.exit_code = EXIT_FINDINGS_INVALID
            return EXIT_FINDINGS_INVALID
        discovery_log.record(LOGGER, "run.summary", probes=len(results))
        if a.out:
            Path(a.out).write_text(json.dumps({"probes": results}, indent=2, default=str))
        if mode != retention_inventory.NORMAL:
            if a.summary:
                print_summary(results, collection_result(results), "not_retained")
            return 0
        root = Path(a.source_root)
        produce(a.declare, root, results, "\n".join(table) + "\n")
        for declared in a.declare:
            try:
                inventory.finalize(root, declared)
            except retention_inventory.InventoryError:
                pass  # stays unfinished or missing; retention rejects it with a stable code
        outcome = retention_writer.retain(BUNDLE, root, inventory, collection=collection_result(results),
                                          probe=PROBE_IDENTITY, invocation=sys.argv[1:], logger=LOGGER)
        if outcome.attempt_dir is not None:  # a refused attempt is reported by the ERROR record, not a second sink
            print(f"attempt {outcome.attempt_id}: collection {outcome.collection_outcome}, "
                  f"retention {outcome.retention_outcome}, {len(outcome.reviewable)}/{len(outcome.files)} verified")
        if a.summary:
            print_summary(results, outcome.collection_outcome, outcome.retention_outcome)
        exit_code = 0 if outcome.retention_outcome == retention_writer.SUCCEEDED else EXIT_RETENTION_INCOMPLETE
        run_log.exit_code = exit_code
        return exit_code


if __name__ == "__main__":
    sys.exit(main())
