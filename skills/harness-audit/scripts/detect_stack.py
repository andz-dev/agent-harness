#!/usr/bin/env python3
"""Static stack and component detection for harness-audit (P1).

Reads a repository tree and reports which Python and Node components it
contains. Nothing in the repository is ever executed or installed; manifests
are only parsed as data.

Usage:
    python3 -I detect_stack.py <repo-path> [--compact]

Output is JSON on stdout:
    {
      "stack":   {"ecosystems": [...], "components": [...], "unsupported": [...]},
      "ignored": {...},
      "warnings": [...]
    }
The "stack" object matches the `stack` block of schema/report.schema.json.
Exit codes: 0 ok, 2 bad arguments, 3 no supported (Python or Node) component.
"""

from __future__ import annotations

import argparse
import configparser
import fnmatch
import json
import os
import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from pathlib import Path, PurePosixPath

try:  # PyYAML is only needed for pnpm-workspace.yaml
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".tox",
    ".nox",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "target",
    "vendor",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "site-packages",
    ".idea",
    ".vscode",
}

# Directory names whose packages are fixtures, not components, even when a workspace glob lists them.
FIXTURE_SEGMENTS = {"playground", "playgrounds", "demo", "demos", "__tests__", "tests", "test"}

TEMPLATE_SEGMENT = re.compile(r"(^|[-_.])templates?($|[-_.])", re.I)  # create-vite-template-react

# A manifest below one of these directories is a sample, not a component,
# unless a workspace glob explicitly includes it.
SAMPLE_DIRS = {
    "fixtures",
    "fixture",
    "__fixtures__",
    "testdata",
    "test-data",
    "examples",
    "example",
    "samples",
    "sample",
    "templates",
    "template",
    "snapshots",
    "__snapshots__",
    "docs_src",
    "e2e-fixtures",
}

PY_EXTS = {".py", ".pyi", ".pyx", ".ipynb"}
NODE_EXTS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".vue", ".svelte"}
INFER_MIN_FILES = 5  # source files needed to infer a component without a manifest

UNSUPPORTED = {
    "go.mod": "go",
    "Cargo.toml": "rust",
    "pubspec.yaml": "dart",
    "pom.xml": "java",
    "build.gradle": "java",
    "build.gradle.kts": "java",
    "Gemfile": "ruby",
    "composer.json": "php",
    "Package.swift": "swift",
    "mix.exs": "elixir",
}
UNSUPPORTED_CAP = 50

CANDIDATE_NAMES = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "requirements.txt",
    "package.json",
    "pnpm-workspace.yaml",
    "lerna.json",
}


# --------------------------------------------------------------------------
# File listing
# --------------------------------------------------------------------------
def list_files(root: Path) -> list[str]:
    """Relative POSIX paths of repository files, minus ignored directories."""
    files: list[str] | None = None
    if (root / ".git").exists():
        try:
            out = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z"],
                capture_output=True,
                check=True,
                timeout=120,
            ).stdout
            files = [p for p in out.decode("utf-8", "surrogateescape").split("\0") if p]
        except (OSError, subprocess.SubprocessError):
            files = None
    if files is None:
        files = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
            rel_dir = Path(dirpath).relative_to(root).as_posix()
            for name in sorted(filenames):
                files.append(name if rel_dir == "." else f"{rel_dir}/{name}")
    return sorted(p for p in files if not any(seg in IGNORED_DIRS for seg in p.split("/")))


def dir_of(path: str) -> str:
    parent = PurePosixPath(path).parent.as_posix()
    return parent  # "." for root files


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def glob_match(pattern: str, path: str) -> bool:
    """Match a workspace glob ('*' one segment, '**' any depth) against a directory."""
    pat = [s for s in pattern.strip("/").split("/") if s and s != "."]
    segs = [] if path == "." else path.split("/")

    def rec(i: int, j: int) -> bool:
        if i == len(pat):
            return j == len(segs)
        if pat[i] == "**":
            return any(rec(i + 1, k) for k in range(j, len(segs) + 1))
        if j == len(segs):
            return False
        return fnmatch.fnmatchcase(segs[j], pat[i]) and rec(i + 1, j + 1)

    return rec(0, 0)


def join(base: str, rel: str) -> str:
    return rel if base == "." else f"{base}/{rel}"


def read_json(root: Path, rel: str, warnings: list[str]):
    try:
        return json.loads((root / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        warnings.append(f"could not parse {rel}: {type(exc).__name__}")
        return None


def read_toml(root: Path, rel: str, warnings: list[str]):
    try:
        return tomllib.loads((root / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        warnings.append(f"could not parse {rel}: {type(exc).__name__}")
        return None


def is_sample_location(d: str) -> str | None:
    """Reason a directory is not a component location, or None."""
    segs = [] if d == "." else d.split("/")
    for seg in segs:
        if seg.startswith("."):
            return "hidden directory"
        if seg.lower() in SAMPLE_DIRS:
            return "sample directory"
    return None


# --------------------------------------------------------------------------
# Manifest classification
# --------------------------------------------------------------------------
SETUP_PY_IMPORT = re.compile(r"^\s*(from|import)\s+(setuptools|distutils|skbuild|numpy\.distutils)\b", re.M)


def is_packaging_setup_py(path: Path) -> bool:
    """A file named setup.py is a manifest only if it imports a packaging tool.

    Plain modules that happen to be called setup.py (common in application
    code) are not manifests. The file is read as text, never executed.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:200_000]
    except OSError:
        return False
    return bool(SETUP_PY_IMPORT.search(text))


def python_manifests(root: Path, d: str, names: set[str], py_count: int, warnings: list[str]) -> list[str]:
    found: list[str] = []
    if "pyproject.toml" in names:
        data = read_toml(root, join(d, "pyproject.toml"), warnings)
        if isinstance(data, dict):
            tool = data.get("tool", {}) if isinstance(data.get("tool"), dict) else {}
            if (
                "project" in data
                or "build-system" in data
                or any(k in tool for k in ("poetry", "setuptools", "flit", "hatch", "pdm", "uv", "maturin"))
            ):
                found.append("pyproject.toml")
    if "setup.py" in names and is_packaging_setup_py(root / join(d, "setup.py")):
        found.append("setup.py")
    if "Pipfile" in names:
        found.append("Pipfile")
    if "setup.cfg" in names:
        if found:
            found.append("setup.cfg")
        else:
            cp = configparser.ConfigParser(interpolation=None)
            try:
                cp.read(root / join(d, "setup.cfg"), encoding="utf-8")
                if cp.has_section("metadata") or cp.has_section("options"):
                    found.append("setup.cfg")
            except (configparser.Error, OSError, UnicodeDecodeError):
                warnings.append(f"could not parse {join(d, 'setup.cfg')}")
    if not found and "requirements.txt" in names and (d == "." or py_count >= 3):
        found.append("requirements.txt")
    return found


def node_manifests(root: Path, d: str, names: set[str], warnings: list[str]) -> tuple[list[str], list | None]:
    """Return (manifest names, workspace globs declared in package.json or None)."""
    if "package.json" not in names:
        return [], None
    data = read_json(root, join(d, "package.json"), warnings)
    if not isinstance(data, dict):
        return [], None
    keys = ("name", "scripts", "dependencies", "devDependencies", "workspaces", "main", "bin", "exports")
    if not any(k in data for k in keys):
        return [], None
    ws = data.get("workspaces")
    if isinstance(ws, dict):
        ws = ws.get("packages")
    return ["package.json"], ws if isinstance(ws, list) else None


def workspace_globs(root: Path, d: str, names: set[str], pkg_ws: list | None, warnings: list[str]) -> list[str]:
    """Workspace globs declared in directory d, as root-relative patterns."""
    raw: list[str] = list(pkg_ws or [])
    if "pnpm-workspace.yaml" in names and yaml is not None:
        try:
            data = yaml.safe_load((root / join(d, "pnpm-workspace.yaml")).read_text(encoding="utf-8")) or {}
            raw += [p for p in data.get("packages", []) if isinstance(p, str)]
        except (OSError, yaml.YAMLError):
            warnings.append(f"could not parse {join(d, 'pnpm-workspace.yaml')}")
    if "lerna.json" in names:
        data = read_json(root, join(d, "lerna.json"), warnings)
        if isinstance(data, dict):
            raw += [p for p in data.get("packages", []) if isinstance(p, str)]
    if "pyproject.toml" in names:
        data = read_toml(root, join(d, "pyproject.toml"), warnings)
        try:
            raw += [p for p in data["tool"]["uv"]["workspace"]["members"] if isinstance(p, str)]
        except (KeyError, TypeError):
            pass
    return [join(d, p.removeprefix("./")) for p in raw if isinstance(p, str) and not p.startswith("!")]


# --------------------------------------------------------------------------
# Detection
# --------------------------------------------------------------------------
def make_ids(comps: list[dict]) -> None:
    by_path: dict[str, set[str]] = defaultdict(set)
    for c in comps:
        by_path[c["path"]].add(c["ecosystem"])
    used: set[str] = set()
    for c in comps:
        base = "root" if c["path"] == "." else re.sub(r"[^a-z0-9._-]+", "-", c["path"].lower()).strip("-._")
        base = base or "component"
        if len(by_path[c["path"]]) > 1:
            base = f"{base}-{c['ecosystem']}"
        cid, n = base, 2
        while cid in used:
            cid, n = f"{base}-{n}", n + 1
        used.add(cid)
        c["id"] = cid


def detect(root: Path) -> dict:
    warnings: list[str] = []
    files = list_files(root)

    by_dir: dict[str, set[str]] = defaultdict(set)
    py_files_by_dir: dict[str, int] = defaultdict(int)
    for f in files:
        d = dir_of(f)
        by_dir[d].add(PurePosixPath(f).name)
        if PurePosixPath(f).suffix in PY_EXTS:
            py_files_by_dir[d] += 1

    def py_count_under(d: str) -> int:
        prefix = "" if d == "." else d + "/"
        return sum(n for dd, n in py_files_by_dir.items() if dd == d or (prefix and dd.startswith(prefix)) or d == ".")

    candidate_dirs = sorted(d for d, names in by_dir.items() if names & CANDIDATE_NAMES)

    # Pass 1: collect workspace globs from regular (non-sample) locations.
    globs: list[str] = []
    dir_globs: dict[str, list[str]] = {}
    for d in candidate_dirs:
        if is_sample_location(d):
            continue
        _, pkg_ws = node_manifests(root, d, by_dir[d], warnings)
        dir_globs[d] = workspace_globs(root, d, by_dir[d], pkg_ws, warnings)
        globs += dir_globs[d]

    # Pass 2: classify manifests into components.
    comps: list[dict] = []
    ignored_samples: list[dict] = []
    for d in candidate_dirs:
        reason = is_sample_location(d)
        if reason and any(glob_match(g, d) for g in globs):
            reason = None  # explicitly declared as a workspace member
        names = by_dir[d]
        py = python_manifests(root, d, names, py_count_under(d), [] if reason else warnings)
        nd, _ = node_manifests(root, d, names, [] if reason else warnings)
        for eco, manifests in (("python", py), ("node", nd)):
            if not manifests:
                continue
            if reason:
                ignored_samples.append({"path": d, "ecosystem": eco, "reason": reason})
                continue
            comps.append({"path": d, "ecosystem": eco, "kind": "unknown", "detected_by": manifests})

    # A requirements.txt below an existing Python component is that project's
    # dependency list, not a second component.
    merged: list[dict] = []
    py_paths = {c["path"] for c in comps if c["ecosystem"] == "python" and c["detected_by"] != ["requirements.txt"]}
    kept: list[dict] = []
    for c in comps:
        if (
            c["ecosystem"] == "python"
            and c["detected_by"] == ["requirements.txt"]
            and c["path"] != "."
            and any(p == "." or c["path"].startswith(p + "/") for p in py_paths)
        ):
            merged.append({"path": c["path"], "ecosystem": "python", "reason": "requirements.txt under an ancestor Python component"})
        else:
            kept.append(c)
    comps = kept

    # A workspace root is "tooling" only if it has members other than itself.
    for c in comps:
        if c["ecosystem"] != "node":
            continue
        own = dir_globs.get(c["path"], [])
        if any(o is not c and o["path"] != c["path"] and any(glob_match(g, o["path"]) for g in own) for o in comps):
            c["kind"] = "tooling"

    # Packages inside playgrounds, demos or test folders are fixtures even when a workspace lists them.
    for c in comps:
        if c["kind"] == "unknown" and any(seg.lower() in FIXTURE_SEGMENTS or TEMPLATE_SEGMENT.search(seg) for seg in c["path"].split("/")):
            c["kind"] = "sample"

    # Fallback: no manifest at all, but plenty of source files.
    if not comps:
        py_n = sum(1 for f in files if PurePosixPath(f).suffix in PY_EXTS)
        nd_n = sum(1 for f in files if PurePosixPath(f).suffix in NODE_EXTS)
        for eco, n in (("python", py_n), ("node", nd_n)):
            if n >= INFER_MIN_FILES:
                comps.append({"path": ".", "ecosystem": eco, "kind": "unknown", "detected_by": ["(inferred from sources)"]})
        if comps:
            warnings.append("no Python or Node manifest found; components inferred from source files")

    comps.sort(key=lambda c: (c["path"], c["ecosystem"]))
    make_ids(comps)

    # Assign every file to the deepest enclosing component directory.
    comp_dirs = sorted({c["path"] for c in comps}, key=lambda p: (-len(p.split("/")) if p != "." else 0, p))
    ecos_by_dir: dict[str, list[dict]] = defaultdict(list)
    for c in comps:
        c["tracked_files"] = 0
        ecos_by_dir[c["path"]].append(c)
    lang_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"python": 0, "node": 0})
    unassigned = 0
    owner_of: dict[str, str | None] = {}
    for f in files:
        d = dir_of(f)
        owner = None
        for cd in comp_dirs:
            if cd == "." or d == cd or d.startswith(cd + "/"):
                owner = cd
                break
        owner_of[f] = owner
        ext = PurePosixPath(f).suffix
        if owner is not None:
            if ext in PY_EXTS:
                lang_counts[owner]["python"] += 1
            elif ext in NODE_EXTS:
                lang_counts[owner]["node"] += 1
    for f in files:
        owner = owner_of[f]
        if owner is None:
            unassigned += 1
            continue
        group = ecos_by_dir[owner]
        if len(group) == 1:
            group[0]["tracked_files"] += 1
            continue
        ext = PurePosixPath(f).suffix
        if ext in PY_EXTS:
            target = "python"
        elif ext in NODE_EXTS:
            target = "node"
        else:  # configs, docs: go to the dominant ecosystem, python on a tie
            lc = lang_counts[owner]
            target = "node" if lc["node"] > lc["python"] else "python"
        for c in group:
            if c["ecosystem"] == target:
                c["tracked_files"] += 1

    # Unsupported ecosystems, reported so they are not silently missed.
    unsupported: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for f in files:
        name = PurePosixPath(f).name
        if name in UNSUPPORTED and not is_sample_location(dir_of(f)):
            key = (dir_of(f), UNSUPPORTED[name])
            if key not in seen:
                seen.add(key)
                unsupported.append({"path": key[0], "language": key[1], "manifest": name})
    # Keep only the outermost manifest per language subtree (drops android/app under android).
    unsupported.sort(key=lambda u: (u["language"], 0 if u["path"] == "." else len(u["path"].split("/")), u["path"]))
    collapsed: list[dict] = []
    for u in unsupported:
        if not any(
            k["language"] == u["language"] and (k["path"] == "." or u["path"] == k["path"] or u["path"].startswith(k["path"] + "/"))
            for k in collapsed
        ):
            collapsed.append(u)
    unsupported = sorted(collapsed, key=lambda u: (u["path"], u["language"]))
    if len(unsupported) > UNSUPPORTED_CAP:
        warnings.append(f"{len(unsupported)} unsupported manifests found; showing {UNSUPPORTED_CAP}")
        unsupported = unsupported[:UNSUPPORTED_CAP]

    order = ("id", "path", "ecosystem", "kind", "tracked_files", "detected_by")
    comps = [{k: c[k] for k in order} for c in comps]
    ecosystems = sorted({c["ecosystem"] for c in comps})
    stack = {"ecosystems": ecosystems, "components": comps}
    if unsupported:
        stack["unsupported"] = unsupported
    return {
        "stack": stack,
        "ignored": {
            "sample_manifest_count": len(ignored_samples),
            "sample_manifests": ignored_samples[:20],
            "merged_manifests": merged[:20],
            "unassigned_files": unassigned,
            "total_files": len(files),
        },
        "warnings": sorted(set(warnings)),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Detect Python and Node components in a repository (static).")
    ap.add_argument("repo", help="path to the repository root")
    ap.add_argument("--compact", action="store_true", help="single-line JSON")
    args = ap.parse_args(argv)
    root = Path(args.repo)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    result = detect(root.resolve())
    print(json.dumps(result, indent=None if args.compact else 2, sort_keys=False))
    return 0 if result["stack"]["components"] else 3


if __name__ == "__main__":
    sys.exit(main())
