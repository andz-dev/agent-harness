#!/usr/bin/env python3
"""Bootstrap for harness-audit (v2 preview): propose the missing harness files for a repository.

Opinionated, unlike the audit: Python repos get uv + ruff + pytest + Taskfile + pre-commit, Node repos use their
own package manager and scripts. The tool reads the repository (no code is executed), looks at which checks the
audit reported as failed, and writes proposed files into a separate directory. It never overwrites a file
that already exists, and it only touches the repository itself with --apply.

Anything it cannot know is written as `TODO(human): ...` instead of being invented.

Usage: python3 -I bootstrap.py <repo> --report report.json [--out DIR] [--apply]
Output: DIR/proposed/<path> for every new file, DIR/bootstrap.md (what, why, which checks, what was skipped).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect_stack  # noqa: E402

try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None

DIR_NOTES = {
    "src": "main source code",
    "lib": "main source code",
    "app": "application code",
    "packages": "workspace packages",
    "tests": "tests",
    "test": "tests",
    "__tests__": "tests",
    "docs": "documentation",
    "scripts": "maintenance and helper scripts",
    "examples": "usage examples",
    "benchmarks": "benchmarks",
    "tools": "developer tooling",
    ".github": "CI workflows and GitHub settings",
}


def facts(root: Path) -> dict:
    files = detect_stack.list_files(root)
    fs = set(files)
    stack = detect_stack.detect(root)["stack"]
    comps = [c for c in stack["components"] if c.get("kind") not in ("tooling", "sample")] or stack["components"]
    eco = max(comps, key=lambda c: c.get("tracked_files", 0))["ecosystem"] if comps else "unknown"
    name = root.resolve().name
    f: dict = {"name": name, "ecosystem": eco, "files": fs, "multi": len(comps) > 1}
    tops = {}
    for p in files:
        if "/" in p:
            tops[p.split("/", 1)[0]] = tops.get(p.split("/", 1)[0], 0) + 1
    f["dirs"] = sorted(d for d in tops if d in DIR_NOTES or tops[d] >= 5)
    if eco == "python":
        py = {}
        if "pyproject.toml" in fs and tomllib:
            try:
                py = tomllib.loads((root / "pyproject.toml").read_text(errors="replace"))
            except Exception:
                py = {}
        f["pm"] = "uv" if ("uv.lock" in fs or "uv" in py.get("tool", {})) else ("poetry" if "poetry.lock" in fs else "uv")
        f["has_pytest"] = "pytest" in py.get("tool", {}) or "pytest.ini" in fs or any(re.search(r"(^|/)test_.*\.py$", p) for p in files)
        f["has_ruff"] = "ruff" in py.get("tool", {}) or "ruff.toml" in fs or ".ruff.toml" in fs
        f["layout"] = "src" if any(p.startswith("src/") for p in files) else "flat"
    if eco == "node":
        pkg = {}
        if "package.json" in fs:
            try:
                pkg = json.loads((root / "package.json").read_text(errors="replace"))
            except Exception:
                pkg = {}
        f["scripts"] = pkg.get("scripts", {}) or {}
        f["pm"] = "pnpm" if "pnpm-lock.yaml" in fs else "yarn" if "yarn.lock" in fs else "npm"
    return f


def py_cmds(f: dict) -> dict:
    run = "uv run" if f["pm"] == "uv" else "poetry run"
    return {
        "setup": "uv sync" if f["pm"] == "uv" else "poetry install",
        "test": f"{run} pytest" if f["has_pytest"] else f"{run} python -m unittest discover",
        "one": f"{run} pytest path/to/test_file.py::test_name"
        if f["has_pytest"]
        else f"{run} python -m unittest path.to.test_module.TestClass.test_name",
        "lint": f"{run} ruff check .",
        "fmt_check": f"{run} ruff format --check .",
        "fix": f"{run} ruff check --fix . && {run} ruff format .",
    }


def node_cmds(f: dict) -> dict:
    pm, s = f["pm"], f["scripts"]
    run = {"npm": "npm run", "pnpm": "pnpm run", "yarn": "yarn"}[pm]
    c = {"setup": {"npm": "npm ci", "pnpm": "pnpm install --frozen-lockfile", "yarn": "yarn install --frozen-lockfile"}[pm]}
    for k in ("test", "lint", "build", "format"):
        if k in s:
            c[k] = f"{run} {k}"
    return c


def commands(f: dict) -> dict:
    return py_cmds(f) if f["ecosystem"] == "python" else node_cmds(f) if f["ecosystem"] == "node" else {}


# ---------------------------------------------------------------- generators
def gen_agents(f: dict) -> str:
    c = commands(f)
    L = ["# AGENTS.md", "", f"{f['name']}: TODO(human): one sentence on what this project does.", ""]
    L += ["## Commands", "", "Use the task runner; do not call tools directly.", ""]
    L += ["- `task setup` installs dependencies.", "- `task check` runs lint and the full test suite. Run it before every commit."]
    one = "pass a test file path to run a single test" + (
        " (`-k name` selects by name)" if f["ecosystem"] == "python" and f.get("has_pytest") else ""
    )
    L += [f"- `task test -- <args>` runs tests; {one}."]
    if c.get("one"):
        L += [f"- A single test without the runner: `{c['one']}`."]
    L += ["", "## Layout", ""]
    for d in f["dirs"]:
        L.append(f"- `{d}/`: {DIR_NOTES.get(d, 'TODO(human): purpose')}")
    if not f["dirs"]:
        L.append("- TODO(human): where the main code, tests and config live.")
    L += ["", "## Conventions", ""]
    L += [
        "- Run `task check` before declaring work done; fix failures instead of skipping them.",
        "- Do not edit lockfiles or generated files by hand; use the package manager.",
        "- Do not commit secrets, `.env` files or local settings.",
        "- Keep changes focused: one concern per pull request.",
        "- TODO(human): add the project-specific rules (naming, error handling, forbidden patterns).",
        "",
    ]
    return "\n".join(L)


def gen_taskfile(f: dict) -> str:
    c = commands(f)
    if f["ecosystem"] == "python":
        return f"""version: "3"

tasks:
  default:
    desc: List all tasks
    cmds:
      - task --list

  setup:
    desc: Install dependencies
    cmds:
      - {c["setup"]}

  doctor:
    desc: Check that the required tools are installed
    cmds:
      - python3 --version
      - {"uv --version" if f["pm"] == "uv" else "poetry --version"}
      - task --version

  lint:
    desc: Lint and check formatting (no changes)
    cmds:
      - {c["lint"]}
      - {c["fmt_check"]}

  fix:
    desc: Apply lint fixes and formatting
    cmds:
      - {c["fix"]}

  test:
    desc: Run the tests (pass pytest arguments after --)
    cmds:
      - {c["test"]} {{{{.CLI_ARGS}}}}

  check:
    desc: Lint plus tests; run before every commit
    cmds:
      - task: lint
      - task: test
"""
    lint = c.get("lint", "echo 'TODO(human): add a lint script to package.json' && exit 1")
    test = c.get("test", "echo 'TODO(human): add a test script to package.json' && exit 1")
    return f"""version: "3"

tasks:
  default:
    desc: List all tasks
    cmds:
      - task --list

  setup:
    desc: Install dependencies
    cmds:
      - {c["setup"]}

  doctor:
    desc: Check that the required tools are installed
    cmds:
      - node --version
      - {f["pm"]} --version
      - task --version

  lint:
    desc: Lint (no changes)
    cmds:
      - {lint}

  test:
    desc: Run the tests (pass arguments after --)
    cmds:
      - {test} {{{{.CLI_ARGS}}}}

  check:
    desc: Lint plus tests; run before every commit
    cmds:
      - task: lint
      - task: test
"""


def gen_precommit(f: dict) -> str:
    return """repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0  # TODO(human): pin to the current release
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: task-check
        name: task check
        entry: task check
        language: system
        pass_filenames: false
        stages: [pre-push]
"""


def gen_ci(f: dict) -> str:
    if f["ecosystem"] == "python":
        setup = "      - uses: astral-sh/setup-uv@v5\n" if f["pm"] == "uv" else "      - run: pipx install poetry\n"
    else:
        setup = "      - uses: actions/setup-node@v4\n        with:\n          node-version: lts/*\n"
        if f["pm"] == "pnpm":
            setup = "      - uses: pnpm/action-setup@v4\n" + setup
    return f"""name: ci
on:
  pull_request:
  push:
    branches: [main]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
{setup}      - uses: arduino/setup-task@v2
        with:
          version: 3.x
          repo-token: ${{{{ secrets.GITHUB_TOKEN }}}}
      - run: task setup
      - run: task check
"""


def gen_dependabot(f: dict) -> str:
    eco = "pip" if f["ecosystem"] == "python" else "npm"
    return f"""version: 2
updates:
  - package-ecosystem: {eco}
    directory: "/"
    schedule:
      interval: weekly
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
"""


def gen_contributing(f: dict) -> str:
    return f"""# Contributing to {f["name"]}

1. `task setup` to install dependencies.
2. Make a focused change on a branch.
3. `task check` must pass before you open a pull request.
4. Describe what changed and why in the pull request; link the issue.

TODO(human): branching model, commit message style, review expectations.
"""


# check id -> (path, generator, extra checks the file also covers)
PLAN = [
    ("AGENTS.md", gen_agents, ["ORI-02", "ORI-04", "ORI-05", "ORI-06", "ENT-05", "VER-11"], None),
    ("CLAUDE.md", lambda f: "@AGENTS.md\n", ["ORI-08"], None),
    ("Taskfile.yml", gen_taskfile, ["ENT-01", "ENT-02", "ENT-03", "ENT-04", "ENT-06"], ("python", "node")),
    (".pre-commit-config.yaml", gen_precommit, ["TRG-01", "TRG-02", "TRG-03"], ("python",)),
    (".github/workflows/ci.yml", gen_ci, ["CIP-01", "CIP-02", "CIP-03", "CIP-05"], ("python", "node")),
    (".github/dependabot.yml", gen_dependabot, ["CIP-07"], ("python", "node")),
    ("CONTRIBUTING.md", gen_contributing, ["ORI-03"], None),
]
EXISTING_ALTERNATIVES = {
    "AGENTS.md": ["AGENTS.md"],
    "CLAUDE.md": ["CLAUDE.md"],
    "Taskfile.yml": ["Taskfile.yml", "Taskfile.yaml", "Makefile", "makefile", "justfile"],
    ".pre-commit-config.yaml": [".pre-commit-config.yaml", ".husky", "lefthook.yml", ".lefthook.yml"],
    ".github/workflows/ci.yml": [".github/workflows/ci.yml", "azure-pipelines.yml", ".gitlab-ci.yml"],
    ".github/dependabot.yml": [".github/dependabot.yml", "renovate.json", ".github/renovate.json"],
    "CONTRIBUTING.md": ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"],
}


def propose(root: Path, report: dict) -> dict:
    f = facts(root)
    failed = {x["check_id"] for x in report["findings"] if x["status"] in ("fail", "error")}
    out = {"facts": {k: v for k, v in f.items() if k != "files"}, "files": [], "skipped": [], "notes": []}
    if f["ecosystem"] not in ("python", "node"):
        out["notes"].append("No Python or Node component found; nothing proposed.")
        return out
    if f["multi"]:
        out["notes"].append(
            "Several components found: files are proposed for the dominant one at the repository root; review per component."
        )
    agents_planned = "AGENTS.md" in {p for p, _, cov, _ in PLAN if failed & set(cov)}
    for path, gen, covers, ecos in PLAN:
        want = sorted(failed & set(covers))
        if path == "CLAUDE.md" and not want and agents_planned and "CLAUDE.md" not in f["files"]:
            want = ["ORI-08"] if "ORI-08" in failed else []
        if not want:
            continue
        if ecos and f["ecosystem"] not in ecos:
            out["skipped"].append({"path": path, "reason": f"not proposed for {f['ecosystem']} repositories", "checks": want})
            continue
        present = [a for a in EXISTING_ALTERNATIVES.get(path, [path]) if a in f["files"] or any(x.startswith(a + "/") for x in f["files"])]
        if present:
            out["skipped"].append({"path": path, "reason": f"{present[0]} already exists; add the missing parts by hand", "checks": want})
            continue
        if path == "Taskfile.yml" and f["ecosystem"] == "node" and "test" not in f["scripts"] and "lint" not in f["scripts"]:
            out["notes"].append("Taskfile proposed with TODO placeholders because package.json has no test or lint script.")
        out["files"].append({"path": path, "content": gen(f), "checks": want})
    return out


def render_md(p: dict, name: str) -> str:
    L = [
        f"# Bootstrap proposal: {name}",
        "",
        "Nothing has been written to the repository. Review each file, fill every `TODO(human)`, then copy or run with `--apply`.",
        "",
    ]
    L += [f"Detected: {p['facts'].get('ecosystem')} / {p['facts'].get('pm', '?')}", ""]
    L += ["## Proposed files", ""]
    if not p["files"]:
        L.append("None.")
    for x in p["files"]:
        todos = x["content"].count("TODO(human)")
        L.append(f"- `{x['path']}` covers {', '.join(x['checks'])}" + (f" ({todos} TODO to fill)" if todos else ""))
    if p["skipped"]:
        L += ["", "## Skipped", ""] + [f"- `{s['path']}` ({', '.join(s['checks'])}): {s['reason']}" for s in p["skipped"]]
    if p["notes"]:
        L += ["", "## Notes", ""] + [f"- {n}" for n in p["notes"]]
    L += ["", "Re-run the audit after merging; the TODO placeholders do not count as documentation of project rules."]
    return "\n".join(L) + "\n"


def write(root: Path, out: Path, p: dict, apply: bool) -> list[str]:
    written = []
    for x in p["files"]:
        dst = out / "proposed" / x["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(x["content"])
        if apply:
            target = root / x["path"]
            if target.exists():
                continue  # never overwrite
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(x["content"])
            written.append(x["path"])
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--report", required=True, help="report.json from audit.py")
    ap.add_argument("--out", default="build/bootstrap")
    ap.add_argument("--apply", action="store_true", help="also write the proposed files into the repository (never overwrites)")
    a = ap.parse_args(argv)
    root = Path(a.repo)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    report = json.loads(Path(a.report).read_text())
    p = propose(root, report)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    written = write(root, out, p, a.apply)
    (out / "bootstrap.md").write_text(render_md(p, report["repo"]["name"]))
    (out / "bootstrap.json").write_text(
        json.dumps(
            {**p, "files": [{k: v for k, v in x.items() if k != "content"} for x in p["files"]], "applied": written}, indent=2, default=list
        )
        + "\n"
    )
    print(
        f"{report['repo']['name']}: {len(p['files'])} files proposed, {len(p['skipped'])} skipped, {len(written)} applied -> {out}/bootstrap.md"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
