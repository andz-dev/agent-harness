#!/usr/bin/env python3
"""LLM layer for harness-audit: task preparation and answer verification (P3).

This script never calls a model. It splits the work into two mechanical steps around the model:

  prepare : python3 -I llm_layer.py prepare <repo> --out tasks.json
            Selects excerpts per llm check, resolves checks that need no judgement (for example no agent
            file at all), and writes numbered excerpts plus the prompt path for the rest.
  apply   : python3 -I llm_layer.py apply <repo> --tasks tasks.json --answers answers.json --out findings.json
            Verifies every quoted snippet against the real file. Unverifiable evidence is dropped; an answer
            left with no verified quote becomes "unknown". Writes schema-valid findings.

Repository text is untrusted: the prompts tell the model to treat it as data, and `apply` accepts only
what it can verify (status words, known task ids, quotes that exist in the files).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect_stack  # noqa: E402
import run_checks  # noqa: E402
import yaml  # noqa: E402
from run_checks import Ctx, Scope, found, searched  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
MAX_FILE_LINES = 250
MAX_TASK_LINES = 700
DOC_GLOBS = ["README*", "CONTRIBUTING*", ".github/CONTRIBUTING*", "docs/*.md", "docs/**/*.md"]
PATH_IN_DOC = re.compile(r"`((?:\./)?(?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,5})`")
STATUS = {"pass", "fail", "unknown"}
CONFIDENCE = {"low", "medium", "high"}
OTHER_AGENT_FILES = ["CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md", ".cursorrules"]


def excerpt(ctx: Ctx, rel: str, limit: int = MAX_FILE_LINES) -> dict | None:
    text = ctx.text(rel)
    if text is None:
        return None
    lines = text.splitlines()[:limit]
    return {"path": rel, "start_line": 1, "end_line": len(lines), "text": "\n".join(f"{i:>4}| {ln}" for i, ln in enumerate(lines, 1))}


LOCALIZED_README = re.compile(r"^readme[._-][a-z]{2,3}([_-][a-z]{2,4})?\.(md|rst|txt)$", re.I)  # README.ar.md, README.zh-CN.md


def _files(ctx: Ctx, globs: list[str]) -> list[str]:
    """Matching files, without translated READMEs, main README first."""
    found = [f for f in ctx.match(globs, Scope(["."])) if not LOCALIZED_README.match(PurePosixPath(f).name)]
    return sorted(found, key=lambda f: (f.count("/"), not PurePosixPath(f).name.lower().startswith("readme.md"), f))


def _budget(excerpts: list[dict]) -> list[dict]:
    out, used = [], 0
    for e in excerpts:
        n = e["end_line"]
        if used + n > MAX_TASK_LINES:
            keep = max(0, MAX_TASK_LINES - used)
            if keep < 20:
                break
            lines = e["text"].splitlines()[:keep]
            e = {**e, "end_line": keep, "text": "\n".join(lines)}
            n = keep
        out.append(e)
        used += n
    return out


def missing_paths(ctx: Ctx, docs: list[str]) -> list[dict]:
    tracked = set(ctx.files)
    out = []
    for d in docs:
        for i, ln in enumerate((ctx.text(d) or "").splitlines(), 1):
            for m in PATH_IN_DOC.finditer(ln):
                rel = m.group(1)[2:] if m.group(1).startswith("./") else m.group(1)
                if rel.startswith(run_checks_generated()) or "*" in rel or "<" in rel:
                    continue
                base = str(PurePosixPath(d).parent)
                rel_to_doc = (PurePosixPath(base) / rel).as_posix() if base != "." else rel
                if rel in tracked or rel_to_doc in tracked or any(t.endswith("/" + rel) for t in tracked):
                    continue
                out.append({"path": d, "line": i, "text": rel})
    return out[:60]


def run_checks_generated() -> tuple[str, ...]:
    return ("dist/", "build/", "out/", "node_modules/", "target/", "coverage/", "tmp/", ".venv/", "venv/", "site/", "htmlcov/")


def plan(root: Path, catalog: dict) -> dict:
    stack = detect_stack.detect(root)["stack"]
    ctx = Ctx(root, stack, catalog)
    agent = _files(ctx, ctx.sets["agent_files"])
    docs = _files(ctx, DOC_GLOBS)
    targets = sorted(ctx.targets(Scope(ctx.all_bases)))
    hooks = ctx.hooks()
    llm_checks = [c for c in catalog["checks"] if c["detector"] == "llm"]
    # ENR-03 and ENR-05 are not asked separately: apply_answers derives them from the DOC-06 and ORI-09 answers.
    tasks, resolved = [], []

    def resolve(check, status, evidence, note):
        f = run_checks.make_finding({**check, "detector": "script"}, status, evidence, None, note)
        resolved.append(f)

    for c in llm_checks:
        cid, prompt = c["id"], c["params"]["prompt"]
        facts: dict = {}
        candidates: list[dict] = []
        files: list[str]
        contributing = _files(ctx, ["CONTRIBUTING*", ".github/CONTRIBUTING*"])
        if cid in ("ORI-05", "ORI-06", "VER-11", "ENT-05", "ORI-08", "ORI-09") and not agent and not (cid == "VER-11" and contributing):
            resolve(
                c,
                "fail",
                [searched(", ".join(ctx.sets["agent_files"][:4]) + " …", "no agent instruction file found")],
                "Nothing to judge: no agent instruction file.",
            )
            continue
        if cid in ("ORI-05", "ORI-06", "ENT-05"):
            files = agent
            if cid == "ENT-05":
                facts["runner_targets"] = targets[:80]
        elif cid == "VER-11":
            files = agent + contributing
        elif cid == "ORI-08":
            others = [f for f in OTHER_AGENT_FILES if f in set(ctx.files)]
            if "AGENTS.md" in set(ctx.files) and not others:
                resolve(
                    c,
                    "pass",
                    [found("AGENTS.md", "AGENTS.md is the only agent instruction file", 1)],
                    "No tool-specific file exists that could duplicate it.",
                )
                continue
            if "AGENTS.md" not in set(ctx.files):
                resolve(
                    c,
                    "fail",
                    [searched("AGENTS.md", "not found; tool-specific files exist: " + ", ".join(others))],
                    "Tool-specific agent files exist but there is no canonical AGENTS.md.",
                )
                continue
            files = ["AGENTS.md"] + others
        elif cid == "ORI-09":
            files = agent + _files(ctx, ["README*"])[:1]
            facts["runner_targets"] = targets[:80]
        elif cid == "TRG-06":
            hook_files = sorted({h["path"] for h in hooks})
            if not hook_files:
                resolve(
                    c,
                    "fail",
                    [searched(", ".join(ctx.sets["hook_files"][:4]) + " …", "no hook configuration found")],
                    "No hooks to compare.",
                )
                continue
            is_agent = lambda path: path.startswith((".claude/", ".github/hooks/"))  # noqa: E731
            if not any(is_agent(h) for h in hook_files) or all(is_agent(h) for h in hook_files):
                resolve(c, "not_applicable", [], "Needs both agent hooks and Git hooks; only one kind exists.")
                continue
            files = hook_files
            facts["runner_targets"] = targets[:80]
            facts["hook_commands"] = [
                {"path": h["path"], "line": h["line"], "stage": h["stage"], "text": h["text"][:160]} for h in hooks[:40]
            ]
        elif cid == "DOC-06":
            files = docs[:6] + agent
            facts["runner_targets"] = targets[:80]
            candidates = missing_paths(ctx, docs + agent)
            if not docs and not agent:
                resolve(c, "fail", [searched(", ".join(DOC_GLOBS[:3]), "no documentation files found")], "Nothing to check.")
                continue
        elif cid == "STA-09":
            files = _files(
                ctx,
                [
                    "pyproject.toml",
                    "ruff.toml",
                    ".ruff.toml",
                    ".eslintrc*",
                    "eslint.config.*",
                    "biome.json*",
                    ".pre-commit-config.yaml",
                    ".flake8",
                    "setup.cfg",
                    "package.json",
                ],
            )[:6]
            if not files:
                resolve(c, "fail", [searched("linter configs", "no linter config found")], "Nothing to judge.")
                continue
        else:
            continue
        ex = _budget([e for f in dict.fromkeys(files) if (e := excerpt(ctx, f))])
        if not ex:
            continue
        tasks.append(
            {
                "task_id": cid,
                "check_id": cid,
                "pillar": c["pillar"],
                "level": c["level"],
                "gate": bool(c.get("gate")),
                "question": c["params"].get("question") or c["title"],
                "title": c["title"],
                "prompt": prompt,
                "facts": facts,
                "candidates": candidates,
                "excerpts": ex,
            }
        )
    return {
        "schema": "llm-tasks/0.1",
        "tasks": tasks,
        "resolved": resolved,
        "instructions": "Read each task's prompt file, then answer every task. See prompts/*.md for the answer format.",
    }


def _norm(s: str) -> str:
    return " ".join(s.split()).strip("`*_ ")


def verify_evidence(root: Path, task: dict, ev: dict) -> dict | None:
    """Return a clean evidence item if the quote really is in the file near the claimed line."""
    path, snippet = ev.get("path"), ev.get("snippet")
    line = ev.get("line")
    if not isinstance(path, str) or not isinstance(snippet, str) or not isinstance(line, int) or line < 1:
        return None
    spans = [e for e in task["excerpts"] if e["path"] == path]
    if not spans:
        return None
    try:
        lines = (root / path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    want = _norm(snippet)
    if len(want) < 3:
        return None
    window = range(max(1, line - 2), min(len(lines), line + 2) + 1)
    for n in window:
        if want in _norm(lines[n - 1]):
            return {"kind": "found", "path": path, "line": n, "snippet": run_checks.clip(snippet)}
    # a quote spanning two lines
    for n in window:
        if n < len(lines) and want in _norm(lines[n - 1] + " " + lines[n]):
            return {"kind": "found", "path": path, "line": n, "snippet": run_checks.clip(snippet)}
    return None


def apply_answers(root: Path, tasks_doc: dict, answers: list) -> dict:
    by_id = {t["task_id"]: t for t in tasks_doc["tasks"]}
    findings, rejected, seen = [], [], set()
    for a in answers if isinstance(answers, list) else []:
        tid = a.get("task_id") if isinstance(a, dict) else None
        if tid not in by_id or tid in seen:
            rejected.append({"task_id": tid, "reason": "unknown or duplicate task id"})
            continue
        seen.add(tid)
        t = by_id[tid]
        status = a.get("status") if a.get("status") in STATUS else "unknown"
        conf = a.get("confidence") if a.get("confidence") in CONFIDENCE else "low"
        note = str(a.get("note") or "")[:300]
        ev = [v for e in (a.get("evidence") or [])[:6] if isinstance(e, dict) and (v := verify_evidence(root, t, e))]
        dropped = len(a.get("evidence") or []) - len(ev)
        if status in ("pass", "fail") and not ev:
            status, note = "unknown", (note + " " if note else "") + "[quotes could not be verified against the files]"
            conf = "low"
        if dropped and status != "unknown":
            note = (note + " " if note else "") + f"[{dropped} quote(s) discarded: not found in the file]"
            conf = "low" if conf == "high" and not ev else conf
        f = {
            "check_id": t["check_id"],
            "pillar": t["pillar"],
            "level": t["level"],
            "status": status,
            "source": "llm",
            "confidence": conf,
            "gate": t["gate"],
            "evidence": ev,
        }
        if note:
            f["note"] = note
        findings.append(f)
    for tid, t in by_id.items():
        if tid not in seen:
            findings.append(
                {
                    "check_id": t["check_id"],
                    "pillar": t["pillar"],
                    "level": t["level"],
                    "status": "unknown",
                    "source": "llm",
                    "confidence": "low",
                    "gate": t["gate"],
                    "evidence": [],
                    "note": "no answer provided",
                }
            )
    items = []
    for f in findings:
        verdict = {"DOC-06": ("ENR-03", "stale"), "ORI-09": ("ENR-05", "conflicting")}.get(f["check_id"])
        if verdict and f["status"] == "fail":
            for e in f["evidence"][:2]:
                items.append(
                    {
                        "check_id": verdict[0],
                        "path": e["path"],
                        "verdict": verdict[1],
                        "evidence": [e] + ([{"kind": "searched", "path": e["path"], "snippet": f["note"][:300]}] if f.get("note") else []),
                    }
                )
    return {"findings": findings, "entropy_items": items, "rejected": rejected}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("prepare", "apply"):
        p = sub.add_parser(name)
        p.add_argument("repo")
        p.add_argument("--catalog", default=str(HERE / "checks" / "catalog.yaml"))
        p.add_argument("--out", required=True)
    sub.choices["apply"].add_argument("--tasks", required=True)
    sub.choices["apply"].add_argument("--answers", required=True)
    a = ap.parse_args(argv)
    root = Path(a.repo)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    catalog = yaml.safe_load(Path(a.catalog).read_text())
    if a.cmd == "prepare":
        result = plan(root, catalog)
    else:
        result = apply_answers(root, json.loads(Path(a.tasks).read_text()), json.loads(Path(a.answers).read_text()))
    Path(a.out).write_text(json.dumps(result, indent=2) + "\n")
    print(f"{a.cmd}: wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
