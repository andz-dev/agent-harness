#!/usr/bin/env python3
"""Compare the overlay's infrastructure levels with human ratings (B-190).

Usage:
  infra_calibration.py template REPORTS_DIR --out ratings.json
      Lists every repository and infrastructure area found in <REPORTS_DIR>/<repo>/report.json with
      null levels for a human to fill in (0 to 3). The tool's own level is NOT written into the file,
      so the rater stays blind.
  infra_calibration.py compare REPORTS_DIR RATINGS... [--out calibration.md]
      Compares the tool's level per repository and area with one or more filled rating files.
      Reports exact agreement, agreement within one level, mean absolute difference, the direction of
      errors (tool too high or too low), and every disagreement of two or more levels.
Ratings files are not committed (see the repository rules for human gut scores).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def tool_levels(reports: Path) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for p in sorted(reports.glob("*/report.json")):
        infra = json.loads(p.read_text()).get("infra") or {}
        areas = (infra.get("levels") or {}).get("areas") or {}
        if areas:
            out[p.parent.name] = {a: v["level"] for a, v in areas.items()}
    return out


def template(reports: Path) -> dict:
    return {
        "levels": "0 none, 1 basics, 2 checked, 3 automated; null = not rated",
        "repos": {r: {a: None for a in areas} for r, areas in tool_levels(reports).items()},
    }


def load_ratings(path: Path) -> dict[str, dict[str, int]]:
    doc = json.loads(path.read_text())
    out: dict[str, dict[str, int]] = {}
    for repo, areas in (doc.get("repos") or {}).items():
        got = {a: int(v) for a, v in areas.items() if isinstance(v, int) and 0 <= v <= 3}
        if got:
            out[repo] = got
    return out


def compare(tool: dict, raters: list[dict]) -> dict:
    rows = []
    for ri, ratings in enumerate(raters):
        for repo, areas in sorted(ratings.items()):
            for area, human in sorted(areas.items()):
                if area in tool.get(repo, {}):
                    rows.append({"rater": ri + 1, "repo": repo, "area": area, "tool": tool[repo][area], "human": human})
    n = len(rows)
    diffs = [r["tool"] - r["human"] for r in rows]
    summary = {
        "n": n,
        "exact": round(sum(d == 0 for d in diffs) / n, 2) if n else None,
        "within_one": round(sum(abs(d) <= 1 for d in diffs) / n, 2) if n else None,
        "mean_abs_diff": round(sum(abs(d) for d in diffs) / n, 2) if n else None,
        "tool_too_high": sum(d > 0 for d in diffs),
        "tool_too_low": sum(d < 0 for d in diffs),
    }
    # agreement between raters on the same cells
    pairs = []
    if len(raters) >= 2:
        for repo, areas in raters[0].items():
            for area, v in areas.items():
                w = raters[1].get(repo, {}).get(area)
                if w is not None:
                    pairs.append((v, w))
    summary["raters_exact"] = round(sum(a == b for a, b in pairs) / len(pairs), 2) if pairs else None
    summary["raters_cells"] = len(pairs)
    return {"summary": summary, "big_gaps": [r for r in rows if abs(r["tool"] - r["human"]) >= 2], "rows": rows}


def render(result: dict) -> str:
    s = result["summary"]
    lines = [
        "# Infrastructure level calibration",
        "",
        f"Compared cells: {s['n']} · exact: {s['exact']} · within one level: {s['within_one']} · mean absolute difference: {s['mean_abs_diff']}",
        f"Tool above human: {s['tool_too_high']} · tool below human: {s['tool_too_low']}",
        f"Rater vs rater exact agreement: {s['raters_exact']} over {s['raters_cells']} cells",
        "",
        "## Gaps of two or more levels",
        "",
        "| Rater | Repo | Area | Tool | Human |",
        "|---|---|---|---|---|",
    ]
    lines += [f"| {r['rater']} | {r['repo']} | {r['area']} | L{r['tool']} | L{r['human']} |" for r in result["big_gaps"]] or [
        "| none | | | | |"
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template")
    t.add_argument("reports")
    t.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("reports")
    c.add_argument("ratings", nargs="+")
    c.add_argument("--out")
    a = ap.parse_args(argv)
    reports = Path(a.reports)
    if not reports.is_dir():
        print(f"not a directory: {reports}", file=sys.stderr)
        return 2
    if a.cmd == "template":
        Path(a.out).write_text(json.dumps(template(reports), indent=2) + "\n")
        return 0
    result = compare(tool_levels(reports), [load_ratings(Path(p)) for p in a.ratings])
    text = render(result)
    if a.out:
        Path(a.out).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
