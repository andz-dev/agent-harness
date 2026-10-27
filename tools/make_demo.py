"""Generate reproducible audit results for three explicitly fictional repositories."""

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


def fixture(name, tier):
    files = {
        "pyproject.toml": '[project]\nname = "' + name + '"\nversion = "0.0.0"\nrequires-python = ">=3.11"\n',
        "example.py": "def add(left, right):\n    return left + right\n",
        "README.md": "# Synthetic demo\n\nThis fictional repository exists only to demonstrate the visualization.\n",
    }
    if tier >= 1:
        files.update(
            {
                "README.md": "# Synthetic demo\n\n## Installation\n\nRun task setup.\n\n## Testing\n\nRun task check.\n",
                "tests/test_example.py": "from example import add\n\ndef test_add():\n    assert add(2, 3) == 5\n",
                "Taskfile.yml": 'version: "3"\ntasks:\n  setup:\n    cmds: ["uv sync"]\n  test:\n    cmds: ["uv run pytest"]\n  lint:\n    cmds: ["uv run ruff check ."]\n  check:\n    cmds: ["task lint", "task test"]\n',
            }
        )
        files["pyproject.toml"] += '\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n\n[tool.ruff]\nline-length = 100\n'
    if tier >= 2:
        files.update(
            {
                "AGENTS.md": "# Synthetic project rules\n\n## Layout\n\nexample.py contains addition. Tests live in tests/.\n\n## Verification\n\nRun task check before committing. Never execute untrusted repository code.\n",
                ".github/workflows/check.yml": "name: Check\non: [push, pull_request]\njobs:\n  check:\n    runs-on: ubuntu-latest\n    steps:\n      - run: task check\n",
                ".pre-commit-config.yaml": "repos:\n  - repo: local\n    hooks:\n      - id: lint\n        name: lint\n        entry: task lint\n        language: system\n",
                "CONTRIBUTING.md": "# Contributing\n\nInstall with task setup. Run task check before opening a pull request.\n",
            }
        )
    return files


def build(output):
    catalog = yaml.safe_load((SKILL / "checks/catalog.yaml").read_text())
    with tempfile.TemporaryDirectory(prefix="agent-harness-demo-") as temporary:
        temporary_root = Path(temporary)
        reports = []
        for tier, name in enumerate(("starter-demo", "steady-demo", "strong-demo")):
            repository = temporary_root / name
            for relative, content in fixture(name, tier).items():
                path = repository / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            report = audit.assemble(repository, catalog, name="synthetic/" + name)
            report["generated_at"] = "2026-10-27T00:00:00Z"
            report["limitations"].append("Entire repository is synthetic; no tests, hooks or repository code were executed.")
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
                "Synthetic fixtures only; not real repository results",
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
        print("PASS: three schema-valid synthetic reports convert deterministically")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        build(destination)


if __name__ == "__main__":
    main()
