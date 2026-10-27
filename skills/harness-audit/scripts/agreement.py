#!/usr/bin/env python3
"""Compare two independent answer sets (answers.json) for the judgement tasks.

Usage: agreement.py A_DIR B_DIR [--out agreement.md]
Each DIR holds <repo>/answers.json (list of {task_id, status, ...}).
Reports per-task agreement, Cohen's kappa over pass/fail/unknown, and every disagreement.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

LABELS = ("pass", "fail", "unknown")


def load(d, name="answers.json"):
    out = {}
    for p in sorted(Path(d).glob("*/" + name)):
        out[p.parent.name] = {a["task_id"]: a.get("status", "unknown") for a in json.loads(p.read_text())}
    return out


def kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[label] * cb[label] for label in LABELS) / (n * n)
    return 1.0 if pe == 1 else round((po - pe) / (1 - pe), 3)


def compare(a, b):
    pairs, diffs, by_task = [], [], {}
    for repo in sorted(set(a) & set(b)):
        for tid in sorted(set(a[repo]) & set(b[repo])):
            x, y = a[repo][tid], b[repo][tid]
            pairs.append((x, y))
            t = by_task.setdefault(tid, [0, 0])
            t[1] += 1
            if x == y:
                t[0] += 1
            else:
                diffs.append((repo, tid, x, y))
    n = len(pairs)
    agree = sum(x == y for x, y in pairs)
    return {
        "n": n,
        "agree": agree,
        "rate": round(agree / n, 3) if n else None,
        "kappa": kappa(pairs),
        "by_task": by_task,
        "diffs": diffs,
        "repos": sorted(set(a) & set(b)),
    }


def render(r):
    L = [
        "# Judgement agreement (two independent runs)",
        "",
        f"Repos: {len(r['repos'])} · answers compared: {r['n']} · agreement: {r['agree']}/{r['n']}"
        f" ({(r['rate'] or 0) * 100:.0f}%) · Cohen's kappa: {r['kappa']}",
        "",
        "| Task | Agree | Total |",
        "| --- | --- | --- |",
    ]
    for t, (ag, tot) in sorted(r["by_task"].items()):
        L.append(f"| {t} | {ag} | {tot} |")
    L += ["", "## Disagreements", "", "| Repo | Task | Run A | Run B |", "| --- | --- | --- | --- |"]
    L += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in r["diffs"]] or ["| none | | | |"]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--out")
    ap.add_argument("--name-a", default="answers.json")
    ap.add_argument("--name-b", default="answers.json")
    args = ap.parse_args(argv)
    r = compare(load(args.a, args.name_a), load(args.b, args.name_b))
    md = render(r)
    if args.out:
        Path(args.out).write_text(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
