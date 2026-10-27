#!/usr/bin/env python3
"""Entropy and git-signal checks for harness-audit (P2).

Evaluates the catalog checks with detector git_signal (STA-08, DOC-05) and the entropy
checks ENR-01, ENR-02, ENR-04 and ENR-07. ENR-03 and ENR-05 need the LLM layer and ENR-06
(unused dependencies) is not implemented yet; both are reported as not evaluated.

The tool never deletes or changes anything. Each flagged file gets a verdict
(orphaned, stale, conflicting) with evidence; a human decides.

Usage: python3 -I git_signals.py <repo-path> [--catalog FILE] [--compact]
Output: JSON {"findings": [...], "entropy": {...}, "not_evaluated": [...]}.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect_stack  # noqa: E402
import run_checks  # noqa: E402
import yaml  # noqa: E402
from run_checks import Ctx, Scope, found, searched  # noqa: E402

# tool -> standalone config globs, and where the same tool can be configured elsewhere in a file
TOOL_CONFIGS = {
    "ruff": {"files": ["ruff.toml", ".ruff.toml"], "embedded": [("pyproject.toml", r"(?m)^\[tool\.ruff[\].]")]},
    "eslint": {
        "files": [
            ".eslintrc",
            ".eslintrc.js",
            ".eslintrc.cjs",
            ".eslintrc.json",
            ".eslintrc.yml",
            ".eslintrc.yaml",
            "eslint.config.js",
            "eslint.config.mjs",
            "eslint.config.cjs",
            "eslint.config.ts",
        ],
        "embedded": [("package.json", r'"eslintConfig"\s*:')],
    },
    "prettier": {
        "files": [
            ".prettierrc",
            ".prettierrc.json",
            ".prettierrc.yml",
            ".prettierrc.yaml",
            ".prettierrc.js",
            ".prettierrc.cjs",
            ".prettierrc.toml",
            "prettier.config.js",
            "prettier.config.cjs",
            "prettier.config.mjs",
        ],
        "embedded": [("package.json", r'"prettier"\s*:\s*(?:\{|"(?![\d^~<>=*]))')],
    },
    "flake8": {"files": [".flake8"], "embedded": [("setup.cfg", r"(?m)^\[flake8\]"), ("tox.ini", r"(?m)^\[flake8\]")]},
    "mypy": {"files": ["mypy.ini", ".mypy.ini"], "embedded": [("setup.cfg", r"(?m)^\[mypy"), ("pyproject.toml", r"(?m)^\[tool\.mypy")]},
    "pytest": {
        "files": ["pytest.ini"],
        "embedded": [("pyproject.toml", r"(?m)^\[tool\.pytest"), ("tox.ini", r"(?m)^\[pytest\]"), ("setup.cfg", r"(?m)^\[tool:pytest\]")],
    },
    "black": {"files": [], "embedded": [("pyproject.toml", r"(?m)^\[tool\.black\]")]},
    "isort": {"files": [".isort.cfg"], "embedded": [("pyproject.toml", r"(?m)^\[tool\.isort\]"), ("setup.cfg", r"(?m)^\[isort\]")]},
    "jest": {
        "files": ["jest.config.js", "jest.config.ts", "jest.config.mjs", "jest.config.cjs", "jest.config.json"],
        "embedded": [("package.json", r'"jest"\s*:\s*\{')],
    },
    "coverage": {"files": [".coveragerc"], "embedded": [("pyproject.toml", r"(?m)^\[tool\.coverage"), ("setup.cfg", r"(?m)^\[coverage:")]},
}
# Standalone config files whose tool must still be present somewhere (ENR-07).
DEAD_CHECK_TOOLS = [
    "ruff",
    "eslint",
    "prettier",
    "flake8",
    "mypy",
    "black",
    "isort",
    "jest",
    "pylint",
    "stylelint",
    "commitlint",
    "markdownlint",
    "babel",
    "tslint",
]
# Frameworks that read a tool's config implicitly, so the tool never appears by name.
IMPLIED_BY = {
    "babel": ["docusaurus", "next", "jest", "webpack", "react-scripts", "expo", "metro", "gatsby", "vite", "rollup", "react-native"],
    "eslint": ["next", "react-scripts"],
    "jest": ["react-scripts", "vue-cli"],
}
EXTRA_CONFIGS = {
    "pylint": [".pylintrc", "pylintrc"],
    "stylelint": [".stylelintrc", ".stylelintrc.json", "stylelint.config.js"],
    "commitlint": ["commitlint.config.js", ".commitlintrc", ".commitlintrc.json"],
    "markdownlint": [".markdownlint.json", ".markdownlint.yaml", ".markdownlint.yml", ".markdownlint-cli2.yaml"],
    "babel": [".babelrc", "babel.config.js", "babel.config.json"],
    "tslint": ["tslint.json"],
}
MANIFEST_GLOBS = [
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "requirements*.txt",
    "requirements/*.txt",
    "package.json",
    "Pipfile",
    "tox.ini",
    "noxfile.py",
    "environment.yml",
    "Dockerfile*",
    "docker-compose*.yml",
    "compose*.yml",
]
DOC_GLOBS = ["README*", "CONTRIBUTING*", "docs/**/*.md", "docs/*.md", "*.md", "AGENTS.md", "CLAUDE.md", ".github/**/*.md"]
SCRIPT_DIRS = ["scripts/**", "tools/**", "bin/**"]
SCRIPT_EXT = {".sh", ".bash", ".py", ".js", ".mjs", ".cjs", ".ts", ".ps1", ".rb", ".pl", ".bat", ".cmd"}
PATH_TOKEN = re.compile(r"(?<![\w$/.{}-])((?:\./)?(?:[\w.-]+/)*[\w.-]+\.(?:sh|bash|py|js|mjs|cjs|ts|ps1|rb|pl|ya?ml|json|toml))\b")
GENERATED = ("dist/", "build/", "out/", "node_modules/", "target/", "coverage/", "tmp/", ".venv/", "venv/", "site/", "htmlcov/", "bin/")


# --------------------------------------------------------------------------
def git(root: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def history_available(root: Path) -> bool:
    """True only when the repository has real history (not a depth-limited clone)."""
    if git(root, "rev-parse", "--git-dir") is None:
        return False
    shallow = (git(root, "rev-parse", "--is-shallow-repository") or "").strip()
    return shallow == "false"


def last_commit(root: Path, rel: str, hist: bool) -> str | None:
    if not hist:
        return None
    out = (git(root, "log", "-1", "--format=%cs", "--", rel) or "").strip()
    return out or None


def _recently_touched(root: Path, rel: str) -> bool:
    lc = last_commit(root, rel, True)
    try:
        return bool(lc) and (date.today() - date.fromisoformat(lc)).days <= ACTIVE_DAYS
    except ValueError:
        return False


def _in_dirs(path: str, globs: list[str]) -> bool:
    return any(r.match(path) for r in run_checks.compile_globs(globs))


def _mentions(text: str, needle: str) -> bool:
    return bool(re.search(r"(?<![\w.-])" + re.escape(needle) + r"(?![\w-])", text))


# --------------------------------------------------------------------------
ACTIVE_DAYS = 540  # an unreferenced script touched within ~18 months is maintained tooling, not dead code (B-141)


def orphaned_scripts(ctx: Ctx, params: dict, root: Path | None = None, hist: bool = False) -> tuple[list[dict], int]:
    cands = [f for f in ctx.files if _in_dirs(f, params.get("globs", SCRIPT_DIRS)) and PurePosixPath(f).suffix.lower() in SCRIPT_EXT]
    sources: dict[str, str] = {}
    for g in ctx.sets["runner_files"] + ctx.sets["ci_files"] + ctx.sets["hook_files"] + MANIFEST_GLOBS + DOC_GLOBS:
        for f in ctx.match([g], Scope(ctx.all_bases)):
            t = ctx.text(f)
            if t:
                sources[f] = t
    # scripts may call each other, but a script never keeps itself alive
    for f in ctx.files:
        if (
            _in_dirs(f, params.get("globs", SCRIPT_DIRS))
            and f not in sources
            and PurePosixPath(f).suffix.lower() in SCRIPT_EXT | {".json", ".yml", ".yaml"}
        ):
            t = ctx.text(f)
            if t:
                sources[f] = t
    items = []
    for c in cands:
        p = PurePosixPath(c)
        names = {c, p.name}
        if p.suffix == ".py":
            names.add(".".join(p.with_suffix("").parts))
        refs = [s for s, t in sources.items() if s != c and any(_mentions(t, n) for n in names)]
        if not refs and hist and root is not None and _recently_touched(root, c):
            continue
        if not refs:
            items.append(
                {
                    "path": c,
                    "verdict": "orphaned",
                    "evidence": [
                        searched(", ".join(["runner/CI/hook files", "manifests", "docs", "other scripts"]), f"no file references {p.name}")
                    ],
                }
            )
    return items, len(cands)


def duplicate_configs(ctx: Ctx) -> tuple[list[dict], list[str]]:
    tracked = set(ctx.files)
    items, considered = [], set()
    dirs = {detect_stack.dir_of(f) for f in ctx.files}
    for d in sorted(dirs):
        for tool, spec in TOOL_CONFIGS.items():
            pre = "" if d == "." else d + "/"
            paths = [pre + f for f in spec["files"] if pre + f in tracked]
            for emb, rx in spec["embedded"]:
                if pre + emb in tracked and re.search(rx, ctx.text(pre + emb) or ""):
                    paths.append(pre + emb)
            considered.update(paths)
            if len(paths) > 1:
                items.append(
                    {
                        "path": paths[0],
                        "verdict": "conflicting",
                        "tool": tool,
                        "evidence": [found(p, f"{tool} is configured here") for p in paths[:3]],
                    }
                )
    return items, sorted(considered)


def dead_configs(ctx: Ctx) -> tuple[list[dict], int]:
    tracked = set(ctx.files)
    corpus_files = set()
    for g in ctx.sets["runner_files"] + ctx.sets["ci_files"] + ctx.sets["hook_files"] + MANIFEST_GLOBS:
        corpus_files.update(ctx.match([g], Scope(ctx.all_bases)))
    corpus = "\n".join((ctx.text(f) or "") for f in sorted(corpus_files)).lower()
    items, considered = [], 0
    for tool in DEAD_CHECK_TOOLS:
        files = (TOOL_CONFIGS.get(tool, {}).get("files") or []) + EXTRA_CONFIGS.get(tool, [])
        cfgs = sorted(f for f in tracked if PurePosixPath(f).name in set(files))
        considered += len(cfgs)
        names = [tool] + IMPLIED_BY.get(tool, [])
        if cfgs and not any(re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w])", corpus) for n in names):
            for c in cfgs:
                items.append(
                    {
                        "path": c,
                        "verdict": "orphaned",
                        "tool": tool,
                        "evidence": [searched("manifests, runners, CI, hooks", f"{tool} is not mentioned anywhere")],
                    }
                )
    return items, considered


def broken_ci_references(ctx: Ctx) -> tuple[list[dict], int]:
    tracked = set(ctx.files)
    items, seen = [], set()
    for ci in ctx.ci():
        # Workflows that check out another repository or change directory resolve paths elsewhere.
        if re.search(r"(?m)^\s*(repository|working-directory)\s*:", ctx.text(ci["path"]) or ""):
            continue
        for text, line in ci["run_cmds"]:
            if re.search(r"\b(git clone|cd|pushd)\b", text):
                continue
            for m in PATH_TOKEN.finditer(text):
                tok = m.group(1)
                rel = tok[2:] if tok.startswith("./") else tok
                if rel.startswith(GENERATED) or "*" in rel or rel.startswith(("http", "www.")) or "/" not in tok and "." not in tok:
                    continue
                if rel in tracked or any(t.endswith("/" + rel) for t in tracked):
                    continue
                # URLs and package names like "foo.js" without a directory are too ambiguous
                if "/" not in rel:
                    continue
                if (ci["path"], rel) in seen:
                    continue
                seen.add((ci["path"], rel))
                items.append(
                    {
                        "path": ci["path"],
                        "verdict": "stale",
                        "evidence": [found(ci["path"], text, line), searched(rel, "no tracked file at this path")],
                    }
                )
    return items, len(ctx.ci())


# --------------------------------------------------------------------------
def adr_finding(ctx: Ctx, check: dict, hist: bool) -> dict:
    p = check["params"]
    files = ctx.match(p["globs"], Scope(["."]))
    if not files:
        return run_checks.make_finding(check, "fail", [searched(", ".join(p["globs"]), "no ADR files found")])
    if not hist:
        return run_checks.make_finding(
            check, "unknown", [found(files[0], "ADR file exists")], note="recency not evaluated: shallow clone has no history"
        )
    cutoff = date.today() - timedelta(days=30 * int(p.get("recent_within_months", 12)))
    dated = [(last_commit(ctx.root, f, True), f) for f in files[:200]]
    recent = [(d, f) for d, f in dated if d and date.fromisoformat(d) >= cutoff]
    if recent:
        d, f = max(recent)
        return run_checks.make_finding(check, "pass", [found(f, f"last touched {d}")])
    d, f = max((x for x in dated if x[0]), default=(None, files[0]))
    return run_checks.make_finding(
        check,
        "fail",
        [found(f, f"newest ADR last touched {d}" if d else "no commit date")],
        note=f"no ADR touched within {p.get('recent_within_months', 12)} months",
    )


def duplicate_finding(check: dict, items: list[dict], configs: list[str]) -> dict:
    if not configs:
        return run_checks.make_finding(check, "not_applicable", [], note="no linter or formatter config found")
    if not items:
        return run_checks.make_finding(
            check, "pass", [found(configs[0], f"each tool has one config per directory ({len(configs)} config files checked)")]
        )
    ev = [e for it in items[:2] for e in it["evidence"]][:3]
    return run_checks.make_finding(
        check, "fail", ev, note=f"{len(items)} tool(s) configured more than once: " + ", ".join(sorted({it["tool"] for it in items}))
    )


def run(root: Path, catalog: dict) -> dict:
    stack = detect_stack.detect(root)["stack"]
    ctx = Ctx(root, stack, catalog)
    hist = history_available(root)
    by_id = {c["id"]: c for c in catalog["checks"]}
    ent_checks = {c["id"]: c for c in catalog["entropy"]["checks"]}
    findings, items = [], []

    dup, dup_configs = duplicate_configs(ctx)
    if "STA-08" in by_id:
        findings.append(duplicate_finding(by_id["STA-08"], dup, dup_configs))
    if "DOC-05" in by_id:
        findings.append(adr_finding(ctx, by_id["DOC-05"], hist))

    runs = {
        "ENR-01": lambda: orphaned_scripts(ctx, ent_checks["ENR-01"]["params"], root, hist),
        "ENR-02": lambda: (dup, len(dup_configs)),
        "ENR-04": lambda: broken_ci_references(ctx),
        "ENR-07": lambda: dead_configs(ctx),
    }
    flagged_paths, cand_paths = set(), 0
    for cid, fn in runs.items():
        found_items, n = fn()
        cand_paths += n
        for it in found_items:
            flagged_paths.add(it["path"])
            lc = last_commit(root, it["path"], hist)
            row = {"check_id": cid, "path": it["path"], "verdict": it["verdict"], "evidence": it["evidence"]}
            if lc:
                row["last_commit"] = lc
            items.append(row)
    entropy = {"candidate_files": cand_paths, "flagged_files": len(flagged_paths), "history_available": hist, "items": items}
    not_eval = [
        {"check_id": "ENR-03", "reason": "needs the LLM layer"},
        {"check_id": "ENR-05", "reason": "needs the LLM layer"},
        {"check_id": "ENR-06", "reason": "not implemented yet (see BACKLOG)"},
    ]
    return {"findings": findings, "entropy": entropy, "not_evaluated": not_eval}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--catalog", default=str(Path(__file__).resolve().parent.parent / "checks" / "catalog.yaml"))
    ap.add_argument("--compact", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.repo)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    catalog = yaml.safe_load(Path(a.catalog).read_text())
    json.dump(run(root, catalog), sys.stdout, indent=None if a.compact else 2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
