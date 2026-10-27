#!/usr/bin/env python3
"""Catalog-driven check engine for harness-audit (P1).

Runs every check in checks/catalog.yaml whose detector can be decided from the
repository files alone, and reports one finding per check (and per component
for ecosystem-specific checks). Nothing in the repository is executed.

Detectors implemented here: file_exists, glob_count, key_present, text_match,
ci_runs, hook_runs, runner_target. Detectors that need git history (git_signal)
or the LLM layer (llm) are reported with status "unknown" and a note; they are
evaluated by later phases.

Usage:
    python3 -I run_checks.py <repo-path> [--catalog FILE] [--only ID,ID] [--compact]

Output: JSON with "meta", "stack", "findings", "warnings".
Exit codes: 0 ok, 2 bad arguments, 3 no supported component.
"""

from __future__ import annotations

import argparse
import bisect
import configparser
import json
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect_stack  # noqa: E402

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

MAX_TEXT = 400_000
UNSCORED_KINDS = ("tooling", "sample")  # components that are not judged on their own
MAX_EVIDENCE = 3
SNIPPET = 200

CI_CMD_KEYS = {"run", "script", "bash", "pwsh", "powershell", "sh", "command", "commands", "before_script", "after_script", "cmd"}
PR_EVENTS = {"pull_request", "pull_request_target", "merge_group", "pr", "merge_request"}


# --------------------------------------------------------------------------
# Glob handling (paths are repo-relative POSIX strings)
# --------------------------------------------------------------------------
def expand_braces(pat: str) -> list[str]:
    m = re.search(r"\{([^{}]*)\}", pat)
    if not m:
        return [pat]
    out: list[str] = []
    for alt in m.group(1).split(","):
        out += expand_braces(pat[: m.start()] + alt + pat[m.end() :])
    return out


def glob_to_regex(pat: str) -> re.Pattern:
    out, i = [], 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pat.startswith("**", i):
            out.append(".*")
            i += 2
        elif pat[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pat[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pat[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$", re.I)


_REGEX_CACHE: dict[str, list[re.Pattern]] = {}


def compile_globs(pats: list[str]) -> list[re.Pattern]:
    out: list[re.Pattern] = []
    for p in pats:
        if p not in _REGEX_CACHE:
            _REGEX_CACHE[p] = [glob_to_regex(x) for x in expand_braces(p)]
        out += _REGEX_CACHE[p]
    return out


def clip(s: str, n: int = SNIPPET) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


# --------------------------------------------------------------------------
# Repository context
# --------------------------------------------------------------------------
class Scope:
    """Where a check looks: directories (bases) and optionally an owner filter."""

    def __init__(self, bases: list[str], owner: str | None = None, inherit: tuple[str, ...] = (), exclude: tuple[str, ...] = ()):
        self.bases = bases
        self.owner = owner  # component path: restrict to files it owns
        self.inherit = inherit  # tooling roots (workspace roots) whose own files also count for the component
        self.exclude = exclude  # directories never searched (top-level sample/fixture packages)


class Ctx:
    def __init__(self, root: Path, stack: dict, catalog: dict):
        self.root = root
        self.stack = stack
        self.sets = catalog.get("sets", {})
        self.files = detect_stack.list_files(root)
        # Fixture packages own no files: their files belong to the enclosing component (vite: src/node/__tests__).
        self.comp_dirs = {c["path"] for c in stack["components"] if c["kind"] != "sample"}
        self.all_bases = ["."] + sorted(self.comp_dirs - {"."})
        self._runner_texts = None
        self.warnings: list[str] = []
        self._text: dict[str, str | None] = {}
        self._owner: dict[str, str | None] = {}
        self._by_owner: dict[str | None, list[str]] | None = None
        self._sorted: list[str] | None = None
        self._ci = None
        self._hooks = None
        self._targets: dict[tuple, dict] = {}

    # -- parameters ---------------------------------------------------------
    def res(self, v):
        if isinstance(v, dict) and "set" in v:
            return self.sets[v["set"]]
        return v

    # -- files --------------------------------------------------------------
    def owner_of_dir(self, d: str) -> str | None:
        if d in self._owner:
            return self._owner[d]
        cur, result = d, None
        while True:
            if cur in self.comp_dirs:
                result = cur
                break
            if cur in (".", ""):
                break
            cur = PurePosixPath(cur).parent.as_posix()
        self._owner[d] = result
        return result

    def files_under(self, prefix: str) -> list[str]:
        """Tracked files starting with `prefix` (a sorted list makes them one contiguous slice)."""
        if not prefix:
            return self.files
        if self._sorted is None:
            self._sorted = sorted(self.files)
        lo = bisect.bisect_left(self._sorted, prefix)
        hi = bisect.bisect_left(self._sorted, prefix[:-1] + chr(ord(prefix[-1]) + 1))
        return self._sorted[lo:hi]

    def files_owned_by(self, owner: str | None) -> list[str]:
        """Tracked files whose nearest component directory is `owner` (index built once)."""
        if self._by_owner is None:
            self._by_owner = {}
            for f in self.files:
                self._by_owner.setdefault(self.owner_of_dir(detect_stack.dir_of(f)), []).append(f)
        return self._by_owner.get(owner, [])

    def match(self, globs: list[str], scope: Scope) -> list[str]:
        regs = compile_globs(globs)
        found: set[str] = set()
        if scope.owner is not None:
            pool = [f for o in dict.fromkeys((scope.owner, *scope.inherit)) for f in self.files_owned_by(o)]
        else:
            pool = self.files
        excl = tuple(e + "/" for e in scope.exclude)
        for base in scope.bases:
            prefix = "" if base == "." else base + "/"
            for f in pool if scope.owner is not None else self.files_under(prefix):
                if prefix and not f.startswith(prefix):
                    continue
                if excl and f.startswith(excl):
                    continue
                rel = f[len(prefix) :]
                if any(r.match(rel) for r in regs):
                    found.add(f)
        return sorted(found, key=lambda x: (x.count("/"), x))  # shallow paths first

    def text(self, rel: str) -> str | None:
        if rel not in self._text:
            try:
                self._text[rel] = (self.root / rel).read_text(encoding="utf-8", errors="replace")[:MAX_TEXT]
            except OSError:
                self._text[rel] = None
        return self._text[rel]

    def line_of(self, rel: str, needle: str) -> int | None:
        text = self.text(rel)
        if not text or not needle:
            return None
        first = next((ln.strip() for ln in needle.splitlines() if ln.strip()), "")
        if not first:
            return None
        for i, ln in enumerate(text.splitlines(), 1):
            if first in ln:
                return i
        return None

    def has_typescript(self, comp_path: str) -> bool:
        for f in self.files:
            if self.owner_of_dir(detect_stack.dir_of(f)) != comp_path:
                continue
            name = PurePosixPath(f).name
            if PurePosixPath(f).suffix in (".ts", ".tsx", ".mts", ".cts") or name.startswith("tsconfig"):
                return True
        return False

    def line_after(self, rel: str, needle: str, start: int) -> int | None:
        lines = (self.text(rel) or "").splitlines()
        for i in range(max(start - 1, 0), len(lines)):
            if needle in lines[i]:
                return i + 1
        return None

    # -- CI ---------------------------------------------------------------------
    def ci(self) -> list[dict]:
        if self._ci is None:
            self._ci = []
            for f in self.match(self.sets["ci_files"], Scope(["."])):
                self._ci.append(self._parse_ci(f))
        return self._ci

    def _parse_ci(self, f: str) -> dict:
        info = {"path": f, "commands": [], "run_cmds": [], "events": set()}
        text = self.text(f) or ""
        if PurePosixPath(f).name == "Jenkinsfile":
            for i, ln in enumerate(text.splitlines(), 1):
                if re.match(r"^\s*(sh|bat|powershell|pwsh)\b", ln):
                    info["commands"].append((ln.strip(), i))
                    info["run_cmds"].append((ln.strip(), i))
            info["events"] |= {"push", "pull_request"}
            return info
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            self.warnings.append(f"could not parse CI file {f}")
            return info

        def add(cmd: str, is_run: bool) -> None:
            ln = self.line_of(f, cmd) or 1
            info["commands"].append((cmd, ln))
            if is_run:
                info["run_cmds"].append((cmd, ln))

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "uses" and isinstance(v, str):
                        add("uses: " + v, False)
                    elif k in CI_CMD_KEYS:
                        if isinstance(v, str):
                            add(v, True)
                        elif isinstance(v, list):
                            for x in v:
                                if isinstance(x, str):
                                    add(x, True)
                                else:
                                    walk(x)
                        else:
                            walk(v)
                    else:
                        walk(v)
            elif isinstance(node, list):
                for x in node:
                    walk(x)

        walk(data)
        if isinstance(data, dict):
            on = data.get("on", data.get(True))
            if isinstance(on, str):
                info["events"].add(on)
            elif isinstance(on, list):
                info["events"] |= {e for e in on if isinstance(e, str)}
            elif isinstance(on, dict):
                info["events"] |= {e for e in on if isinstance(e, str)}
            if "trigger" in data and data["trigger"] != "none":
                info["events"].add("push")
            if "pr" in data and data["pr"] != "none":
                info["events"].add("pr")
            if PurePosixPath(f).name == ".gitlab-ci.yml":
                info["events"] |= {"push", "merge_request"}
            if "version" in data and "jobs" in data and "workflows" in data:  # CircleCI
                info["events"] |= {"push", "pull_request"}
        return info

    # -- hooks ------------------------------------------------------------------
    def hooks(self) -> list[dict]:
        if self._hooks is None:
            self._hooks = []
            for f in self.match(self.sets["hook_files"], Scope(["."])):
                self._hooks += self._parse_hook(f)
            for f in self.match(["package.json"], Scope(["."])):
                self._hooks += self._parse_package_json_hooks(f)
        return self._hooks

    def _parse_package_json_hooks(self, f: str) -> list[dict]:
        """simple-git-hooks, husky (v4 style) and lint-staged configured inside package.json."""
        try:
            data = json.loads(self.text(f) or "")
        except ValueError:
            return []
        if not isinstance(data, dict):
            return []
        return self._hooks_from_mapping(f, data)

    def _hooks_from_mapping(self, f: str, data: dict) -> list[dict]:
        out: list[dict] = []

        def add(cmd: str, stage: str, key: str) -> None:
            out.append({"path": f, "line": self.line_of(f, key) or 1, "text": cmd, "stage": stage})

        for key in ("simple-git-hooks", "husky"):
            body = data.get(key)
            body = body.get("hooks") if key == "husky" and isinstance(body, dict) else body
            for stage, cmd in body.items() if isinstance(body, dict) else []:
                for c in [cmd] if isinstance(cmd, str) else [x for x in cmd if isinstance(x, str)] if isinstance(cmd, list) else []:
                    add(c, str(stage), f'"{key}"')
        staged = data.get("lint-staged")
        for _glob, cmd in staged.items() if isinstance(staged, dict) else []:
            for c in [cmd] if isinstance(cmd, str) else [x for x in cmd if isinstance(x, str)] if isinstance(cmd, list) else []:
                add(c, "pre-commit", '"lint-staged"')
        return out

    def _parse_hook(self, f: str) -> list[dict]:
        name = PurePosixPath(f).name
        out: list[dict] = []

        def add(cmd: str, stage: str) -> None:
            out.append({"path": f, "line": self.line_of(f, cmd) or 1, "text": cmd, "stage": stage})

        text = self.text(f) or ""
        if name == ".pre-commit-config.yaml":
            try:
                data = yaml.safe_load(text) or {}
            except yaml.YAMLError:
                self.warnings.append(f"could not parse {f}")
                return out
            default = data.get("default_stages") or ["pre-commit"]
            for repo in data.get("repos", []) or []:
                if not isinstance(repo, dict):
                    continue
                for h in repo.get("hooks", []) or []:
                    if not isinstance(h, dict):
                        continue
                    stages = h.get("stages") or default
                    # The repo URL is left out on purpose: org names such as "pre-commit" or
                    # "tox-dev" would otherwise match tool patterns.
                    cmd = " ".join(str(x) for x in [h.get("id", ""), h.get("entry", ""), *(h.get("args") or [])] if x)
                    for st in stages:
                        add(cmd, str(st))
        elif name in ("lefthook.yml", "lefthook.yaml"):
            try:
                data = yaml.safe_load(text) or {}
            except yaml.YAMLError:
                self.warnings.append(f"could not parse {f}")
                return out
            for stage, body in data.items() if isinstance(data, dict) else []:
                if not isinstance(body, dict):
                    continue
                for node in _walk_values(body, {"run"}):
                    add(node, str(stage))
        elif name == "settings.json" or name == "settings.local.json":
            try:
                data = json.loads(text)
            except ValueError:
                self.warnings.append(f"could not parse {f}")
                return out
            for event, groups in (data.get("hooks") or {}).items() if isinstance(data, dict) else []:
                for cmd in _walk_values(groups, {"command"}):
                    add(cmd, f"agent:{event}")
        elif name == ".simple-git-hooks.json" or name.startswith(".lintstagedrc"):
            try:
                data = json.loads(text) if text.lstrip().startswith("{") else yaml.safe_load(text)
            except (ValueError, yaml.YAMLError):
                self.warnings.append(f"could not parse {f}")
                return out
            if isinstance(data, dict):
                key = "simple-git-hooks" if name == ".simple-git-hooks.json" else "lint-staged"
                out += self._hooks_from_mapping(f, {key: data})
        elif name.startswith((".simple-git-hooks.", "lint-staged.config.")):
            out.append({"path": f, "line": 1, "text": text.strip()[:200] or name, "stage": "pre-commit"})
        elif "/_/" in f:
            return out
        else:  # .husky/<stage>, .githooks/<stage>, .claude/hooks/<script>
            stage = name
            for ln in text.splitlines():
                s = ln.strip()
                if s and not s.startswith("#"):
                    add(s, stage)
        return out

    def runner_texts(self) -> list[tuple[str, str, int]]:
        """(file, text, line) for every runner line in the repository.

        package.json contributes only its scripts, so dependency names do not
        count as invocations. TOML/INI section headers and comments are skipped.
        """
        if self._runner_texts is None:
            out: list[tuple[str, str, int]] = []
            for f in self.match(self.sets["runner_files"], Scope(self.all_bases)):
                out += self._commands_in(f)
            self._runner_texts = out
        return self._runner_texts

    def _commands_in(self, f: str) -> list[tuple[str, str, int]]:
        """Command lines a runner file would execute (not its dependency lists)."""
        name, text = PurePosixPath(f).name, self.text(f) or ""
        out: list[tuple[str, str, int]] = []

        def add(cmd: str, line: int | None = None) -> None:
            cmd = cmd.strip()
            if cmd:
                first = cmd.split()[0].strip("\"',[]@-")
                out.append((f, cmd, line or self.line_of(f, cmd) or self.line_of(f, f'"{first}"') or 1))

        if name == "package.json":
            try:
                scripts = json.loads(text).get("scripts") or {}
            except (ValueError, AttributeError):
                return out
            for sname, val in scripts.items():
                if isinstance(val, str):
                    add(val, self.line_of(f, f'"{sname}"'))
        elif name in ("Makefile", "justfile"):
            for i, ln in enumerate(text.splitlines(), 1):
                if ln.startswith(("\t", "    ")) and ln.strip() and not ln.strip().startswith("#"):
                    add(ln.strip().lstrip("@-"), i)
        elif name in ("Taskfile.yml", "Taskfile.yaml"):
            try:
                data = yaml.safe_load(text) or {}
            except yaml.YAMLError:
                return out
            for cmd in _walk_values(data, {"cmd", "cmds"}):
                add(cmd)
            for lst in _walk_lists(data, {"cmds"}):
                for x in lst:
                    if isinstance(x, str):
                        add(x)
        elif name == "tox.ini":
            cp = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                cp.read_string(text)
            except configparser.Error:
                return out
            for sec in cp.sections():
                for key, val in cp.items(sec):
                    if key.startswith("commands"):
                        for ln in val.splitlines():
                            add(ln.lstrip("-!"))
        elif name == "noxfile.py":
            for m in re.finditer(r"session\.(?:run|run_always|install)\((.{0,300}?)\)", text, re.S):
                out.append((f, " ".join(m.group(1).split()), text.count("\n", 0, m.start()) + 1))
        elif name == "pyproject.toml":
            try:
                tool = tomllib.loads(text).get("tool", {})
            except ValueError:
                return out
            tox = tool.get("tox", {}) if isinstance(tool.get("tox"), dict) else {}
            envs = [("env_run_base", tox.get("env_run_base", {}))] + list((tox.get("env") or {}).items())
            for env_name, env in envs:
                header = "[tool.tox.env_run_base]" if env_name == "env_run_base" else f"[tool.tox.env.{env_name}]"
                start = self.line_of(f, header) or 1
                for key in ("commands", "commands_pre", "commands_post"):
                    for cmd in env.get(key, []) if isinstance(env, dict) else []:
                        text_cmd = " ".join(str(x) for x in cmd) if isinstance(cmd, list) else str(cmd)
                        first = text_cmd.split()[0].strip("\"'") if text_cmd.split() else ""
                        add(text_cmd, self.line_after(f, f'"{first}"', start) or start)
            for env in (tool.get("hatch", {}).get("envs") or {}).values():
                for v in (env.get("scripts") or {}).values() if isinstance(env, dict) else []:
                    for cmd in _flatten_commands(v):
                        add(cmd)
            for v in list((tool.get("poe", {}).get("tasks") or {}).values()) + list((tool.get("pdm", {}).get("scripts") or {}).values()):
                for cmd in _flatten_commands(v):
                    add(cmd)
        return out

    # -- runner targets -----------------------------------------------------------
    def targets(self, scope: Scope) -> dict[str, tuple[str, int]]:
        key = tuple(scope.bases)
        if key in self._targets:
            return self._targets[key]
        found: dict[str, tuple[str, int]] = {}
        for f in self.match(self.sets["runner_files"], scope):
            for name in self._targets_in(f):
                found.setdefault(name, (f, self.line_of(f, name) or 1))
        self._targets[key] = found
        return found

    def _targets_in(self, f: str) -> list[str]:
        name, text = PurePosixPath(f).name, self.text(f) or ""
        names: list[str] = []
        if name in ("Taskfile.yml", "Taskfile.yaml"):
            try:
                tasks = (yaml.safe_load(text) or {}).get("tasks") or {}
                names += [str(k) for k in tasks]
            except (yaml.YAMLError, AttributeError):
                self.warnings.append(f"could not parse {f}")
        elif name == "Makefile":
            names += re.findall(r"^([A-Za-z0-9][A-Za-z0-9_.\-/]*)\s*:(?!=)", text, re.M)
        elif name == "justfile":
            names += re.findall(r"^([A-Za-z0-9][A-Za-z0-9_\-]*)\b[^:=\n]*:(?!=)", text, re.M)
        elif name == "package.json":
            try:
                names += list((json.loads(text).get("scripts") or {}).keys())
            except (ValueError, AttributeError):
                self.warnings.append(f"could not parse {f}")
        elif name == "tox.ini":
            names += re.findall(r"^\[testenv:([^\]]+)\]", text, re.M)
        elif name == "noxfile.py":
            names += re.findall(r"^def\s+(\w+)\(\s*session", text, re.M)
            names += re.findall(r"name\s*=\s*[\"']([^\"']+)[\"']", text)
        elif name == "pyproject.toml":
            try:
                tool = tomllib.loads(text).get("tool", {})
            except ValueError:
                return names
            tox = tool.get("tox", {})
            names += [str(e) for e in (tox.get("env_list") or []) if isinstance(e, str)]
            names += list((tox.get("env") or {}).keys())
            names += list((tool.get("poe", {}).get("tasks") or {}).keys())
            names += list((tool.get("pdm", {}).get("scripts") or {}).keys())
            for env in (tool.get("hatch", {}).get("envs") or {}).values():
                if isinstance(env, dict):
                    names += list((env.get("scripts") or {}).keys())
        return names


def _walk_lists(node, keys: set[str]):
    """Yield list values stored under the given keys, at any depth."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in keys and isinstance(v, list):
                yield v
            yield from _walk_lists(v, keys)
    elif isinstance(node, list):
        for x in node:
            yield from _walk_lists(x, keys)


def _flatten_commands(node):
    """Command strings from a hatch/poe/pdm script definition."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for x in node:
            yield from _flatten_commands(x)
    elif isinstance(node, dict):
        for k in ("cmd", "shell", "script", "call", "sequence", "ref", "env-run"):
            if k in node:
                yield from _flatten_commands(node[k])


def _walk_values(node, keys: set[str]):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in keys and isinstance(v, str):
                yield v
            else:
                yield from _walk_values(v, keys)
    elif isinstance(node, list):
        for x in node:
            yield from _walk_values(x, keys)


# --------------------------------------------------------------------------
# Evidence helpers
# --------------------------------------------------------------------------
def found(path: str, snippet: str, line: int | None = None) -> dict:
    ev = {"kind": "found", "path": path, "snippet": clip(snippet)}
    if line:
        ev["line"] = line
    return ev


def searched(path: str, snippet: str) -> dict:
    return {"kind": "searched", "path": path, "snippet": clip(snippet)}


def globs_label(globs: list[str]) -> str:
    return ", ".join(globs[:6]) + (" …" if len(globs) > 6 else "")


# --------------------------------------------------------------------------
# Detectors: (ctx, params, scope) -> (status, evidence, note)
# --------------------------------------------------------------------------
def d_file_exists(ctx: Ctx, p: dict, scope: Scope):
    globs = ctx.res(p["globs"])
    hits = ctx.match(globs, scope)
    if hits:
        return "pass", [found(h, f"matches one of: {globs_label(globs)}") for h in hits[:MAX_EVIDENCE]], None
    return "fail", [searched(globs_label(globs), "no tracked file matches")], None


def d_glob_count(ctx: Ctx, p: dict, scope: Scope):
    globs, need = ctx.res(p["globs"]), int(p.get("min", 1))
    if "only_if" in p and "more than one" in str(p["only_if"]) and len(ctx.stack["components"]) <= 1:
        return "not_applicable", [], "repository has a single component"
    hits = ctx.match(globs, scope)
    if len(hits) >= need:
        return "pass", [found(h, f"{len(hits)} files match (need {need})") for h in hits[:MAX_EVIDENCE]], None
    return "fail", [searched(globs_label(globs), f"{len(hits)} files match, need {need}")], None


def _key_lookup(ctx: Ctx, rel: str, keypath: str | None):
    """Return (present, line) for keypath inside file rel."""
    if not keypath:
        return True, None
    text = ctx.text(rel) or ""
    name = PurePosixPath(rel).name
    if name.endswith(".toml"):
        try:
            node = tomllib.loads(text)
        except ValueError:
            return False, None
        for seg in keypath.split("."):
            if not isinstance(node, dict) or seg not in node:
                return False, None
            node = node[seg]
        return True, ctx.line_of(rel, f"[{keypath}") or ctx.line_of(rel, keypath.split(".")[-1])
    if name.endswith(".json"):
        try:
            node = json.loads(text)
        except ValueError:
            return False, None
        for seg in keypath.split("."):
            if not isinstance(node, dict) or seg not in node:
                return False, None
            node = node[seg]
        return True, ctx.line_of(rel, f'"{keypath.split(".")[-1]}"')
    if name.endswith((".cfg", ".ini")):
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        try:
            cp.read_string(text)
        except configparser.Error:
            return False, None
        return cp.has_section(keypath), ctx.line_of(rel, f"[{keypath}]")
    return False, None


def d_key_present(ctx: Ctx, p: dict, scope: Scope):
    hits, tried = [], []
    for entry in p["any_of"]:
        files = ctx.match([entry["file"]], scope)
        tried.append(entry["file"] + (f" [{entry['path']}]" if entry.get("path") else ""))
        for f in files:
            ok, line = _key_lookup(ctx, f, entry.get("path"))
            if ok:
                hits.append(found(f, f"{entry['path']} present" if entry.get("path") else "file present", line))
    if hits:
        return "pass", hits[:MAX_EVIDENCE], None
    return "fail", [searched(globs_label(tried), "none of these files or keys found")], None


def d_text_match(ctx: Ctx, p: dict, scope: Scope):
    globs = ctx.res(p["files"])
    pattern = ctx.res(p["pattern"])
    rx = re.compile(pattern, re.M)
    need = int(p.get("min_distinct_commands", 1))
    hits, distinct = [], set()
    for f in ctx.match(globs, scope)[:300]:
        text = ctx.text(f)
        if not text:
            continue
        for m in rx.finditer(text):
            distinct.add(m.group(0).strip().lower())
            if len(hits) < MAX_EVIDENCE:
                line = text.count("\n", 0, m.start()) + 1
                hits.append(found(f, m.group(0), line))
    if hits and len(distinct) >= need:
        return "pass", hits, None
    note = f"{len(distinct)} distinct matches, need {need}" if hits else None
    return "fail", hits or [searched(globs_label(globs), "pattern not found in any matching file")], note


SETUP_STEP = re.compile(
    r"^(sudo\s+)?((npm|pnpm|yarn|bun)\s+(ci|install|i|add)\b|(pip3?|uv|poetry|pipx)\s+(install|sync|add)\b"
    r"|apt(-get)?\b|brew\b|echo\b|mkdir\b|cd\b|git\b|curl\b|wget\b|export\b|set\b|corepack\b)",
    re.I,
)
RUNNER_CALL = re.compile(r"\b(tox|nox|make|task|just|poe)\b|\b(npm|pnpm|yarn|bun)\s+(run\s+)?[\w:.\-]+|\bhatch run\b")


def _norm_event(e: str) -> str:
    return "pull_request" if e in PR_EVENTS else e


def d_ci_runs(ctx: Ctx, p: dict, scope: Scope):
    if "rule" in p:
        return "unknown", [], "rule-based CI check not implemented yet"
    ci = ctx.ci()
    if not ci:
        return "fail", [searched(globs_label(ctx.sets["ci_files"]), "no CI definition found")], None

    if "trigger" in p or "trigger_all" in p:
        wanted_any = {_norm_event(e) for e in p.get("trigger", [])}
        wanted_all = {_norm_event(e) for e in p.get("trigger_all", [])}
        evs = [(c["path"], {_norm_event(e) for e in c["events"]}) for c in ci]
        union = set().union(*(e for _, e in evs))
        ok = bool(union & wanted_any) if wanted_any else wanted_all <= union
        if ok:
            ev = [
                found(path, "triggers: " + ", ".join(sorted(e & (wanted_any | wanted_all))), ctx.line_of(path, "on:") or 1)
                for path, e in evs
                if e & (wanted_any | wanted_all)
            ]
            return "pass", ev[:MAX_EVIDENCE], None
        return "fail", [searched(ci[0]["path"], "events found: " + (", ".join(sorted(union)) or "none"))], None

    def hits_for(pattern: str):
        rx = re.compile(ctx.res(pattern))
        # Install/setup commands ("pip install ruff") do not run the tool, so they are skipped
        # unless the check asks for them (include_setup, e.g. dependency caching/locking).
        skip_setup = not p.get("include_setup")
        return [
            (c["path"], t, ln) for c in ci for (t, ln) in c["commands"] if rx.search(t) and not (skip_setup and SETUP_STEP.match(t.strip()))
        ]

    def via_runner(pattern: str):
        """CI calls a runner (tox, make, npm run ...) and the runner file mentions the tool.

        Heuristic: it does not prove the called target is the one that uses the tool.
        """
        calls = [(c["path"], t, ln) for c in ci for (t, ln) in c["run_cmds"] if RUNNER_CALL.search(t)]
        if not calls:
            return None
        rx = re.compile(ctx.res(pattern))
        for f, text, line in ctx.runner_texts():
            if rx.search(text):
                return [found(f, text, line), found(calls[0][0], f"CI calls a runner: {calls[0][1]}", calls[0][2])]
        return None

    if "all_of" in p:
        ev, missing, indirect = [], [], False
        for pat in p["all_of"]:
            h = hits_for(pat)
            if h:
                ev.append(found(h[0][0], h[0][1], h[0][2]))
                continue
            r = via_runner(pat)
            if r:
                ev.append(r[0])
                indirect = True
            else:
                missing.append(pat)
        if not missing:
            return "pass", ev[:MAX_EVIDENCE], "some patterns found via a runner file the CI calls" if indirect else None
        return (
            "fail",
            ev + [searched(ci[0]["path"], f"no CI command matches: {missing[0]}")],
            f"{len(missing)} of {len(p['all_of'])} patterns missing",
        )

    pattern = p["pattern"]
    if "min_share_of_run_steps" in p:
        rx = re.compile(ctx.res(pattern))
        runs = [(c["path"], t, ln) for c in ci for (t, ln) in c["run_cmds"] if not SETUP_STEP.match(t.strip())]
        matching = [r for r in runs if rx.search(r[1])]
        share = len(matching) / len(runs) if runs else 0.0
        note = f"{len(matching)} of {len(runs)} run steps call a local entry point (install and setup steps excluded)"
        if share >= float(p["min_share_of_run_steps"]):
            return "pass", [found(a, b, c) for a, b, c in matching[:MAX_EVIDENCE]], note
        return "fail", [found(a, b, c) for a, b, c in runs[:MAX_EVIDENCE]] or [searched(ci[0]["path"], "no run steps")], note

    h = hits_for(pattern)
    if h:
        return "pass", [found(a, b, c) for a, b, c in h[:MAX_EVIDENCE]], None
    r = via_runner(pattern)
    if r:
        return "pass", r, "found in a runner file that the CI calls (indirect)"
    if p.get("also_check") == "hook_runs":
        status, ev, note = d_hook_runs(ctx, {"pattern": pattern}, scope)
        if status == "pass":
            return "pass", ev, "found in a hook, not in CI"
    return "fail", [searched(ci[0]["path"], "no CI command matches the pattern")], None


def d_hook_runs(ctx: Ctx, p: dict, scope: Scope):
    hooks = ctx.hooks()
    if not hooks:
        return "fail", [searched(globs_label(ctx.sets["hook_files"]), "no hook configuration found")], None
    rx = re.compile(ctx.res(p["pattern"]))
    stages = set(p.get("stages", []))
    hits = [h for h in hooks if rx.search(h["text"]) and (not stages or h["stage"] in stages)]
    if hits:
        return "pass", [found(h["path"], f"[{h['stage']}] {h['text']}", h["line"]) for h in hits[:MAX_EVIDENCE]], None
    return "fail", [searched(hooks[0]["path"], "no hook command matches" + (f" at stages {sorted(stages)}" if stages else ""))], None


def _target_matches(name: str, wanted: str) -> bool:
    n, w = name.lower(), wanted.lower()
    return re.match(rf"^{re.escape(w)}s?([:_.\-/]|$)", n) is not None


def d_runner_target(ctx: Ctx, p: dict, scope: Scope):
    targets = ctx.targets(scope)
    if not targets:
        return "fail", [searched(globs_label(ctx.sets["runner_files"]), "no runner targets found")], None
    if p.get("any_target"):
        items = sorted(targets.items(), key=lambda kv: (kv[1][0].count("/"), kv[1][0], kv[0]))
        return "pass", [found(loc[0], f"target '{n}'", loc[1]) for n, loc in items[:MAX_EVIDENCE]], f"{len(targets)} targets defined"
    all_of, any_of = p.get("all_of", []), p.get("any_of", [])

    def hit(w: str):
        return next(((n, loc) for n, loc in targets.items() if _target_matches(n, w)), None)

    ev, missing = [], []
    for w in all_of:
        h = hit(w)
        (ev.append(found(h[1][0], f"target '{h[0]}'", h[1][1])) if h else missing.append(w))
    any_hit = next((hit(w) for w in any_of if hit(w)), None)
    if any_hit:
        ev.append(found(any_hit[1][0], f"target '{any_hit[0]}'", any_hit[1][1]))
    ok = not missing and (not any_of or any_hit)
    if ok:
        return "pass", ev[:MAX_EVIDENCE], None
    why = [f"missing: {', '.join(missing)}"] if missing else []
    if any_of and not any_hit:
        why.append(f"none of: {', '.join(any_of)}")
    return "fail", ev + [searched(globs_label(sorted({v[0] for v in targets.values()})), "; ".join(why))], None


DETECTORS = {
    "file_exists": d_file_exists,
    "glob_count": d_glob_count,
    "key_present": d_key_present,
    "text_match": d_text_match,
    "ci_runs": d_ci_runs,
    "hook_runs": d_hook_runs,
    "runner_target": d_runner_target,
}
DEFERRED = {"git_signal": "needs git history (later phase)", "llm": "needs the LLM layer (later phase)"}


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
def make_finding(check: dict, status: str, evidence: list, component: str | None = None, note: str | None = None) -> dict:
    f = {
        "check_id": check["id"],
        "pillar": check["pillar"],
        "level": check["level"],
        "status": status,
        "source": "llm" if check["detector"] == "llm" else "script",
        "gate": bool(check.get("gate", False)),
        "evidence": evidence,
    }
    if component:
        f["component"] = component
    if f["source"] == "llm":
        f["confidence"] = "low"
    if note:
        f["note"] = note
    return f


def run(root: Path, catalog: dict, only: set[str] | None = None) -> dict:
    stack_result = detect_stack.detect(root)
    stack = stack_result["stack"]
    ctx = Ctx(root, stack, catalog)
    ctx.warnings += stack_result["warnings"]
    comps = stack["components"]
    all_bases = ["."] + sorted({c["path"] for c in comps if c["path"] != "."})

    tooling_roots = [c["path"] for c in comps if c["kind"] == "tooling"]
    excluded = tuple(
        c["path"]
        for c in comps
        if c["kind"] == "sample" and (ctx.owner_of_dir(detect_stack.dir_of(c["path"] + "/x")) in (None, *tooling_roots))
    )

    findings: list[dict] = []
    for check in catalog["checks"]:
        if only and check["id"] not in only:
            continue
        applies = check.get("applies_to", ["all"])
        if check["detector"] in DEFERRED:
            note = f"not evaluated: {DEFERRED[check['detector']]}"
            targets = [None] if "all" in applies else [c for c in comps if c["ecosystem"] in applies and c["kind"] not in UNSCORED_KINDS]
            for t in targets or [None]:
                findings.append(make_finding(check, "unknown", [], t["id"] if t else None, note))
            continue
        fn = DETECTORS.get(check["detector"])
        if fn is None:
            findings.append(make_finding(check, "error", [], None, f"unknown detector {check['detector']}"))
            continue
        if "all" in applies:
            jobs = [(None, Scope(all_bases, exclude=excluded))]
        else:
            targets = [c for c in comps if c["ecosystem"] in applies and c["kind"] not in UNSCORED_KINDS]
            if not targets:
                findings.append(make_finding(check, "not_applicable", [], None, f"no {'/'.join(applies)} component"))
                continue
            jobs = []
            for c in targets:
                # Workspace-root config (eslint, vitest, CI) applies to every package below it.
                inherit = tuple(t for t in tooling_roots if t == "." or c["path"].startswith(t + "/"))
                bases = [c["path"], *[t for t in inherit if t != c["path"]]]
                jobs.append((c["id"], Scope(bases, owner=c["path"], inherit=inherit, exclude=excluded)))
        for comp_id, scope in jobs:
            only_if = str(check.get("params", {}).get("only_if", ""))
            if "TypeScript" in only_if and scope.owner is not None and not ctx.has_typescript(scope.owner):
                findings.append(make_finding(check, "not_applicable", [], comp_id, "component has no TypeScript"))
                continue
            try:
                status, ev, note = fn(ctx, check.get("params", {}), scope)
            except Exception as exc:  # a broken detector must not abort the run
                status, ev, note = "error", [], f"{type(exc).__name__}: {exc}"
            findings.append(make_finding(check, status, ev, comp_id, note))

    counts: dict[str, int] = {}
    for f in findings:
        counts[f["status"]] = counts.get(f["status"], 0) + 1
    return {
        "meta": {"catalog_version": str(catalog.get("catalog_version")), "findings": len(findings), "by_status": counts},
        "stack": stack,
        "findings": findings,
        "warnings": sorted(set(ctx.warnings)),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run harness-audit catalog checks (static).")
    ap.add_argument("repo")
    ap.add_argument("--catalog", default=str(Path(__file__).resolve().parent.parent / "checks" / "catalog.yaml"))
    ap.add_argument("--only", help="comma-separated check ids")
    ap.add_argument("--compact", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.repo)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    catalog = yaml.safe_load(Path(args.catalog).read_text(encoding="utf-8"))
    only = {x.strip() for x in args.only.split(",")} if args.only else None
    result = run(root.resolve(), catalog, only)
    print(json.dumps(result, indent=None if args.compact else 2))
    return 0 if result["stack"]["components"] else 3


if __name__ == "__main__":
    sys.exit(main())
