#!/usr/bin/env python3
"""Read the frozen repository allowlist and emit normalized discovery evidence."""

import argparse
import ast
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BUNDLE = Path(__file__).resolve().parents[1]
ROOT = BUNDLE.parents[1]
ASSET_ROOT = Path(os.environ.get("AGENTS_ASSET_ROOT", Path.home() / ".agents"))
sys.path.insert(0, str(ASSET_ROOT / "shared/scripts"))
import layout

sys.path.insert(0, str(layout.skill_dir("discovery-poc", ASSET_ROOT) / "scripts"))
import discovery_log
import findings
import hypothesis
import sample_data

LOGGER = logging.getLogger("probe")
LIMIT = 1_000_000


def allowed_path(relative, allowlist):
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or relative not in allowlist:
        raise ValueError("input_not_allowed")
    current = ROOT
    for component in candidate.parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("symlink_not_allowed")
    if ROOT not in current.resolve().parents:
        raise ValueError("input_outside_repository")
    return current


def read_sources(card):
    allowlist = card["evidence"]["real_inputs"]
    tracked = subprocess.run(
        ["git", "ls-files", "-z", "--", *allowlist], cwd=ROOT,
        capture_output=True, check=True, timeout=20,
    ).stdout.decode().split("\0")
    sources = {}
    for relative in allowlist:
        if relative not in tracked:
            raise ValueError("input_not_tracked")
        path = allowed_path(relative, allowlist)
        if not path.is_file():
            raise ValueError("input_not_regular_file")
        with path.open("rb") as handle:
            content = handle.read(LIMIT + 1)
        if len(content) > LIMIT:
            raise ValueError("input_too_large")
        sources[relative] = content.decode("utf-8")
    return sources


def assignment(text, name):
    tree = ast.parse(text)
    return next(
        ast.literal_eval(node.value) for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
    )


def observe(sources):
    catalog = sources["skills/harness-audit/checks/catalog.yaml"]
    titles = re.findall(r"^    title:\s*(.+)$", catalog, re.M)
    infrastructure = assignment(sources["skills/harness-audit/scripts/infra_checks.py"], "CHECKS")
    weights = assignment(sources["skills/harness-audit/scripts/score.py"], "WEIGHTS")
    audit = ast.parse(sources["skills/harness-audit/scripts/audit.py"])
    assemble = next(node for node in audit.body if isinstance(node, ast.FunctionDef) and node.name == "assemble")
    early_exit = any(
        isinstance(node, ast.If) and "components" in ast.unparse(node.test)
        and any(isinstance(child, ast.Raise) for child in ast.walk(node))
        for node in assemble.body[:4]
    )
    converter = ast.parse(sources["apps/harness-city/tools/report_to_city.py"])
    from_report = next(node for node in converter.body if isinstance(node, ast.FunctionDef) and node.name == "from_report")
    constants = {node.value for node in ast.walk(from_report) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    package = json.loads(sources["apps/harness-city/package.json"])
    dependencies = set(package.get("dependencies", {})) | set(package.get("devDependencies", {}))
    taskfile = sources["Taskfile.yml"]
    git_signals = sources["skills/harness-audit/scripts/git_signals.py"]
    return {
        "core_count": len(re.findall(r"^  - id:", catalog, re.M)),
        "infra_count": len(infrastructure),
        "pillar_weight": sum(weights.values()),
        "unsupported_early_exit": early_exit,
        "node_lint_dependency": bool(dependencies & {"eslint", "@biomejs/biome", "prettier", "oxlint"}),
        "python_lint_check": "ruff check" in taskfile,
        "ci_task_check": bool(re.search(r"^\s*- run: task check\s*$", sources[".github/workflows/check.yml"], re.M)),
        "root_app_test": "- task: app:test" in taskfile,
        "hook_task_precommit": bool(re.search(r"^task precommit\s*$", sources[".githooks/pre-commit"], re.M)),
        "core_sbom_titles": sum(bool(re.search(r"\b(SBOM|CycloneDX|SPDX)\b", title, re.I)) for title in titles),
        "core_mcp_titles": sum(bool(re.search(r"\bMCP\b|Model Context Protocol", title, re.I)) for title in titles),
        "core_skill_provenance_titles": sum(bool(re.search(r"skill.*provenance|provenance.*skill", title, re.I)) for title in titles),
        "infra_extension_declaration": "extensions or settings" in infrastructure["INF-V05"][2],
        "converter_infra_projection": "infra" in constants,
        "airport_demo_preset": 'AIR_PRESETS["n8n-like (Compose + Docker)"]' in sources["apps/harness-city/index.html"],
        "unused_dependency_unimplemented": "ENR-06" in git_signals and "not implemented yet" in git_signals,
    }


def comparison(cases, observed):
    return [case["id"] for case in cases if type(observed.get(case["id"])) is not type(case["expected"])
            or observed.get(case["id"]) != case["expected"]]


def inventory(cases, observed, sources):
    return [
        {
            "id": case["id"], "topic": case["topic"], "kind": case["kind"],
            "value": observed[case["id"]], "source": case["source"],
            "sha256": hashlib.sha256(sources[case["source"]].encode()).hexdigest(),
            "assurance": "static_only", "runtime_status": "unknown",
        }
        for case in cases
    ]


def assurance_valid(rows):
    return all(row.get("assurance") == "static_only" and row.get("runtime_status") == "unknown" for row in rows)


def measure():
    card, _ = hypothesis.load_card(BUNDLE)
    sources = read_sources(card)
    oracle = json.loads((BUNDLE / "data/oracle.json").read_text())
    observed = observe(sources)
    return card, sources, oracle["cases"], observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--evaluation-only", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-q", "--quiet", action="count", default=0)
    args = parser.parse_args()
    with discovery_log.open_run("probe", sys.argv[1:], log_dir=BUNDLE / "logs", logger=LOGGER,
                                asset_root_source="override" if "AGENTS_ASSET_ROOT" in os.environ else "deployed"):
        _, sources, cases, observed = measure()
        topics = sorted({case["topic"] for case in cases})
        if args.list:
            print("\n".join(topics))
            return 0
        results = {}
        for topic in topics:
            if args.only and topic not in args.only.split(","):
                continue
            started = time.monotonic()
            discovery_log.record(LOGGER, "probe.start", probe=topic)
            values = {case["id"]: observed[case["id"]] for case in cases if case["topic"] == topic}
            results[topic] = values
            discovery_log.record(LOGGER, "probe.done", probe=topic, metrics=len(values),
                                 seconds=round(time.monotonic() - started, 3))
        if not results:
            raise ValueError("no_matching_topics")
        findings.write_findings(BUNDLE / "data/findings.json", findings.rows_from_results(results),
                                subject="agent-harness-coverage")
        rows = inventory(cases, observed, sources)
        sample_data.replace_file(BUNDLE / "data/coverage.json", sample_data.dumps({"schema": "harness-coverage/1", "cases": rows}))
        discovery_log.record(LOGGER, "run.summary", probes=len(results))
        print("summary " + json.dumps({"summary": results, "retentionOutcome": "not_retained"}, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
