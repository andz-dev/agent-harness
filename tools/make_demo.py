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
score = importlib.import_module("score")


PROFILES = (
    ("thriving-demo", (3, 3, 3, 3, 3, 3, 3)),
    ("prosperous-demo", (2, 2, 2, 2, 2, 2, 2)),
    ("working-demo", (2, 1, 1, 2, 1, 1, 1)),
    ("absent-demo", (0, 0, 0, 0, 0, 0, 0)),
)


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
