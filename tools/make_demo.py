"""Generate four illustrative city profiles, not observed repository audits."""

import argparse
import importlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/harness-audit"
sys.path.insert(0, str(SKILL / "scripts"))
audit = importlib.import_module("audit")
infra_checks = importlib.import_module("infra_checks")
score = importlib.import_module("score")


PROFILES = (
    ("thriving-demo", (3, 3, 3, 3, 3, 3, 3)),
    ("prosperous-demo", (2, 2, 2, 2, 2, 2, 2)),
    ("working-demo", (2, 1, 1, 2, 1, 1, 1)),
    ("absent-demo", (0, 0, 0, 0, 0, 0, 0)),
)

# Illustrative infrastructure overlay per profile: area levels and the checks that still fail (not observed).
INFRA = {
    "thriving-demo": {
        "areas": {"dockerfile": 3, "compose": 3, "devcontainer": 3, "terraform": 3, "kubernetes": 3, "cross-cutting": 2, "agent-guidance": 3, "infra-entropy": 3},
        "failing": [],
    },
    "prosperous-demo": {
        "areas": {"dockerfile": 2, "compose": 2, "terraform": 2, "devcontainer": 3, "cross-cutting": 2, "agent-guidance": 2},
        "failing": [("INF-D04", 1, 1), ("INF-C02", 1, 1), ("INF-T05", 1, 1)],
    },
    "working-demo": {
        "areas": {"dockerfile": 2, "compose": 1, "ansible": 1, "cross-cutting": 1},
        "failing": [("INF-C01", 1, 2), ("INF-D05", 0, 1), ("INF-A02", 0, 1), ("INF-X04", 0, 1)],
    },
    "absent-demo": {
        "areas": {"dockerfile": 0, "terraform": 0, "cross-cutting": 0},
        "failing": [("INF-D02", 0, 1), ("INF-T01", 0, 1), ("INF-T02", 0, 1), ("INF-X05", 0, 1)],
    },
}
TOOL_FOR = {"dockerfile": "docker", "compose": "compose", "devcontainer": "devcontainer", "terraform": "terraform", "kubernetes": "kubernetes", "ansible": "ansible"}
FILE_FOR = {"dockerfile": "Dockerfile", "compose": "compose.yaml", "devcontainer": ".devcontainer/devcontainer.json", "terraform": "main.tf", "kubernetes": "k8s/deployment.yaml", "ansible": "playbook.yml"}


def infra_overlay(name):
    spec = INFRA[name]
    areas = spec["areas"]
    wide = [a for a in areas if a in infra_checks.REPO_WIDE]
    tool_areas = [a for a in areas if a not in wide]
    weakest = min(tool_areas, key=lambda a: (areas[a], a)) if tool_areas else None
    detected = [
        {"kind": "iac", "tool": TOOL_FOR[a], "scope": ".", "file_count": 1, "files": [FILE_FOR[a]], "sample": False, "status": "detected-not-scored"}
        for a in tool_areas
    ]
    rollup = []
    for check_id, passed, failed in spec["failing"]:
        area, level, title = infra_checks.CHECKS[check_id]
        rollup.append({"check_id": check_id, "area": area, "level": level, "title": title, "passed": passed, "failed": failed, "not_applicable": 0, "failing": ["."]})
    return {
        "scored": False,
        "tools": sorted(TOOL_FOR[a] for a in tool_areas),
        "kinds": sorted({"container" if a in ("dockerfile", "compose") else "devenv" if a == "devcontainer" else "iac" for a in tool_areas}),
        "detected": detected,
        "checks": [],
        "summary": {},
        "rollup": rollup,
        "levels": {
            "overall": areas[weakest] if weakest else None,
            "weakest_area": weakest,
            "repo_wide": {a: areas[a] for a in wide},
            "areas": {a: {"level": lvl, "blocked_by": [], "pass_ratio_by_level": {}} for a, lvl in areas.items()},
        },
    }


def illustration(name, levels, catalog_version):
    pillars = [
        {"pillar": pillar, "level": level, "weight": weight, "points": round(level / 3 * weight, 2), "gate_failures": []}
        for (pillar, weight), level in zip(score.WEIGHTS.items(), levels, strict=True)
    ]
    entropy = score.entropy_part(None)
    return {
        "schema_version": "0.1",
        "tool": {"name": "harness-audit", "version": audit.VERSION, "catalog_version": str(catalog_version)},
        "generated_at": "2026-10-27T00:00:00Z",
        "repo": {"name": "synthetic/" + name, "commit": "0000000", "clone_mode": "local"},
        "stack": {"ecosystems": ["python"], "components": [{"id": name, "path": ".", "ecosystem": "python", "kind": "app"}]},
        "pillars": pillars,
        "findings": [],
        "score": score.score_part(pillars, [], entropy["penalty"]),
        "entropy": entropy,
        "top_gaps": [],
        "infra": infra_overlay(name),
        "limitations": ["Illustrative synthetic levels only; no repository was audited and no checks or runtime behavior were observed."],
    }


def build(output):
    catalog = yaml.safe_load((SKILL / "checks/catalog.yaml").read_text())
    with tempfile.TemporaryDirectory(prefix="agent-harness-demo-") as temporary:
        temporary_root = Path(temporary)
        reports = []
        for name, levels in PROFILES:
            report = illustration(name, levels, catalog["catalog_version"])
            errors = audit.validate(report)
            if errors:
                raise ValueError(errors)
            path = temporary_root / (name + ".json")
            path.write_text(json.dumps(report, indent=2) + "\n")
            reports.append(path)
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "apps/harness-city/tools/report_to_city.py"),
                *map(str, reports),
                "--title",
                "Synthetic Harness City",
                "--source",
                "Illustrative synthetic profiles only; not audited repository results",
                "-o",
                str(output),
            ],
            check=True,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    destination = ROOT / "apps/harness-city/data/cities.json"
    if arguments.check:
        with tempfile.TemporaryDirectory(prefix="agent-harness-demo-check-") as temporary:
            generated = Path(temporary) / "cities.json"
            build(generated)
            if not destination.is_file() or generated.read_bytes() != destination.read_bytes():
                raise SystemExit("Synthetic demo differs: regenerate explicitly with task demo")
        print("PASS: four schema-valid illustrative profiles convert deterministically")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        build(destination)


if __name__ == "__main__":
    main()
