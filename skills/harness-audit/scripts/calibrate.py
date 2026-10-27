#!/usr/bin/env python3
"""Run audit.py over many repositories and summarise the results in one table.

Usage: python3 -I calibrate.py <repos-dir> --out <dir> [--only a,b,c] [--weights example-repos.json]
Each subdirectory of <repos-dir> is audited into <out>/<name>/. Output: <out>/summary.md and summary.json.
Used in P4 to compare scores with human judgement and to find crashes and slow repositories.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PILLARS = [
    "verification",
    "orientation",
    "static_guardrails",
    "workflow_entry_points",
    "automatic_triggers",
    "pipeline_parity",
    "doc_hygiene",
]
SHORT = ["Ver", "Ori", "Sta", "Ent", "Trg", "Cip", "Doc"]


def audit_one(repo: Path, out: Path, weight: str | None, timeout: int) -> dict:
    cmd = [sys.executable, "-I", str(HERE / "audit.py"), str(repo), "--out", str(out), "--name", repo.name]
    if weight:
        cmd += ["--weight", weight]
    start = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"name": repo.name, "status": "timeout", "seconds": timeout}
    row = {"name": repo.name, "seconds": round(time.time() - start, 1), "exit": r.returncode}
    if r.returncode != 0:
        row["status"] = {3: "unsupported", 4: "invalid"}.get(r.returncode, "error")
        row["message"] = (r.stderr or r.stdout).strip().splitlines()[-1][:200] if (r.stderr or r.stdout).strip() else ""
        return row
    rep = json.loads((out / "report.json").read_text())
    levels = {p["pillar"]: p["level"] for p in rep["pillars"]}
    statuses: dict[str, int] = {}
    for f in rep["findings"]:
        statuses[f["status"]] = statuses.get(f["status"], 0) + 1
    row.update(
        status="ok",
        score=rep["score"]["final"],
        raw=rep["score"]["raw"],
        caps=[c["id"] for c in rep["score"]["caps_applied"]],
        penalty=rep["score"]["entropy_penalty"],
        levels=[levels[p] for p in PILLARS],
        components=len(rep["stack"]["components"]),
        ecosystems=rep["stack"]["ecosystems"],
        clone_mode=rep["repo"]["clone_mode"],
        statuses=statuses,
        llm_tasks=(out / "llm_tasks.json").exists(),
    )
    return row


def render(rows: list[dict]) -> str:
    lines = [
        "| Repo | Score | " + " | ".join(SHORT) + " | Caps | Pen | Comp | Fail/Pass/Unk | Clone | s |",
        "|---|---|" + "---|" * len(SHORT) + "---|---|---|---|---|---|",
    ]
    for r in sorted(rows, key=lambda x: -x.get("score", -1)):
        if r["status"] != "ok":
            lines.append(
                f"| {r['name']} | {r['status']} | "
                + " | ".join("" for _ in SHORT)
                + f" | | | | {r.get('message', '')} | | {r.get('seconds', '')} |"
            )
            continue
        st = r["statuses"]
        lines.append(
            f"| {r['name']} | {r['score']} | "
            + " | ".join(f"L{v}" for v in r["levels"])
            + f" | {','.join(r['caps']) or '-'} | {r['penalty']} | {r['components']} | "
            f"{st.get('fail', 0)}/{st.get('pass', 0)}/{st.get('unknown', 0)} | {r['clone_mode']} | {r['seconds']} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repos_dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only")
    ap.add_argument("--weights", help="example-repos.json, to pass each repo's weight class")
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args(argv)
    weights = {}
    if a.weights:
        weights = {r["id"]: r["weight"] for r in json.loads(Path(a.weights).read_text())["repos"]}
    only = set(a.only.split(",")) if a.only else None
    out = Path(a.out)
    rows = []
    for repo in sorted(p for p in Path(a.repos_dir).iterdir() if p.is_dir() and not p.name.startswith(".")):
        if only and repo.name not in only:
            continue
        rows.append(audit_one(repo, out / repo.name, weights.get(repo.name), a.timeout))
        print(f"{repo.name}: {rows[-1]['status']} {rows[-1].get('score', '')}", flush=True)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(rows, indent=2) + "\n")
    (out / "summary.md").write_text(render(rows) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
