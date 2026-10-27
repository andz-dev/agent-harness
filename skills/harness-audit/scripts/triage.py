#!/usr/bin/env python3
"""Triage for harness-audit (v1.1): turn report.json into a ranked, step-by-step fix plan.

For every failed check the tool asks "what would the score be if this passed?" by re-running the
scoring rules on a copy of the findings (counterfactual), then picks steps greedily by points gained per
unit of effort. When no single fix moves the score (a level needs two gates), it looks at pairs inside one
pillar. Effort and the action sentence come from checks/fixes.yaml.

Read-only: it only reads a report and writes a plan. Unknown (unanswered judgement) checks are listed
separately and never proposed as fixes.

Usage: python3 -I triage.py report.json [--out DIR] [--max-steps N]
Output: triage.json and triage.md (in DIR, default next to the report).
"""

from __future__ import annotations

import argparse
import copy
import itertools
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIXABLE = ("fail", "error")


def exact_final(findings: list[dict], components: list[dict], penalty: float, pass_ratio: float) -> tuple[float, list[dict]]:
    pillars = score.pillar_results(findings, components, pass_ratio)
    raw = sum(p["points"] for p in pillars)
    cap = min([c["limit"] for c in score.caps(findings)], default=100)
    return min(raw, cap) - penalty, pillars


def _with_fixed(findings: list[dict], ids: set[str]) -> list[dict]:
    out = copy.deepcopy(findings)
    for f in out:
        if f["check_id"] in ids and f["status"] in FIXABLE:
            f["status"] = "pass"
    return out


def plan(report: dict, catalog: dict, fixes: dict, max_steps: int = 10) -> dict:
    findings, comps = report["findings"], report["stack"]["components"]
    penalty = float(report["score"]["entropy_penalty"])
    ratio = float(catalog["level_rule"].get("pass_ratio", score.PASS_RATIO))
    titles = {c["id"]: c for c in catalog["checks"]}
    base, _ = exact_final(findings, comps, penalty, ratio)

    steps, cur, cur_score = [], findings, base
    for _ in range(max_steps):
        open_ids = sorted({f["check_id"] for f in cur if f["status"] in FIXABLE})
        if not open_ids:
            break
        best = None  # (gain per effort, gain, ids, effort)
        for size in (1, 2, 3):
            if size == 1:
                cands = [(i,) for i in open_ids]
            else:
                cands = [c for c in itertools.combinations(open_ids, size) if len({titles[i]["pillar"] for i in c}) == 1]
            for ids in cands:
                s, _ = exact_final(_with_fixed(cur, set(ids)), comps, penalty, ratio)
                gain = s - cur_score
                if gain <= 0.005:
                    continue
                effort = sum(fixes[i]["effort"] for i in ids)
                if best is None or (gain / effort, gain) > (best[0], best[1]):
                    best = (gain / effort, gain, ids, effort)
            if best is not None:
                break  # smallest bundle that moves the score; bigger bundles only when smaller ones cannot
        if best is None:
            break
        _, gain, ids, effort = best
        nxt = _with_fixed(cur, set(ids))
        s, pillars = exact_final(nxt, comps, penalty, ratio)
        before = {p["pillar"]: p["level"] for p in score.pillar_results(cur, comps, ratio)}
        moved = [
            {"pillar": p["pillar"], "from": before[p["pillar"]], "to": p["level"]} for p in pillars if p["level"] != before[p["pillar"]]
        ]
        steps.append(
            {
                "check_ids": list(ids),
                "actions": [fixes[i]["action"] for i in ids],
                "titles": [titles[i]["title"] for i in ids],
                "effort": effort,
                "points_gained": round(gain, 1),
                "score_after": max(0, round(s)),
                "levels": moved,
            }
        )
        cur, cur_score = nxt, s
    remaining = sorted({f["check_id"] for f in cur if f["status"] in FIXABLE})
    unknown = sorted({f["check_id"] for f in findings if f["status"] == "unknown"})
    return {
        "score_now": report["score"]["final"],
        "score_if_all_steps_done": max(0, round(cur_score)),
        "steps": steps,
        "no_score_effect_yet": [{"check_id": i, "action": fixes[i]["action"]} for i in remaining],
        "needs_judgement_answers": unknown,
        "cleanup": _cleanup(report),
        "caps": [c["id"] for c in report["score"]["caps_applied"]],
    }


def _cleanup(report: dict) -> list[dict]:
    ent = report["entropy"]
    out = []
    by: dict[str, list[dict]] = {}
    for it in ent.get("items", []):
        by.setdefault(it["check_id"], []).append(it)
    for cid, its in sorted(by.items()):
        rest = [i for i in ent["items"] if i["check_id"] != cid]
        e = score.entropy_part({**ent, "items": rest, "flagged_files": len({i["path"] for i in rest})})
        out.append(
            {
                "check_id": cid,
                "verdict": its[0]["verdict"],
                "files": [i["path"] for i in its][:10],
                "count": len(its),
                "points_gained": round(ent["penalty"] - e["penalty"], 1),
                "note": "Review each file; the tool only reports, a human decides whether to delete or wire it up.",
            }
        )
    return out


def render_md(t: dict, name: str) -> str:
    L = [f"# Fix plan: {name}", "", f"**Score now {t['score_now']}; after all steps below about {t['score_if_all_steps_done']}.**", ""]
    if t["caps"]:
        L += [f"Caps in force: {', '.join(t['caps'])}. Fix these first, they limit the whole score.", ""]
    L += ["Effort: 1 = minutes, 2 = about an hour, 3 = a day or more.", "", "## Steps (best value first)", ""]
    if not t["steps"]:
        L.append("No single or paired fix changes the score.")
    for n, s in enumerate(t["steps"], 1):
        ids = " + ".join(s["check_ids"])
        L.append(f"{n}. **{ids}** (effort {s['effort']}, +{s['points_gained']} points, score {s['score_after']})")
        for a in s["actions"]:
            L.append(f"   - {a}")
        for m in s["levels"]:
            L.append(f"   - {m['pillar']}: L{m['from']} to L{m['to']}")
    if t["no_score_effect_yet"]:
        L += ["", "## Worth doing, but no score effect until the steps above are done", ""]
        L += [f"- **{x['check_id']}**: {x['action']}" for x in t["no_score_effect_yet"]]
    if t["cleanup"]:
        L += ["", "## Cleanup (entropy)", ""]
        for c in t["cleanup"]:
            L.append(
                f"- **{c['check_id']}** {c['verdict']}: {c['count']} files (+{c['points_gained']} points), e.g. {', '.join(c['files'][:3])}"
            )
    if t["needs_judgement_answers"]:
        L += [
            "",
            "## Unanswered judgement checks",
            "",
            "Answer these first (see SKILL.md), they may change the plan: " + ", ".join(t["needs_judgement_answers"]),
        ]
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--out")
    ap.add_argument("--max-steps", type=int, default=10)
    ap.add_argument("--catalog", default=str(ROOT / "checks" / "catalog.yaml"))
    ap.add_argument("--fixes", default=str(ROOT / "checks" / "fixes.yaml"))
    a = ap.parse_args(argv)
    report = json.loads(Path(a.report).read_text())
    catalog = yaml.safe_load(Path(a.catalog).read_text())
    fixes = yaml.safe_load(Path(a.fixes).read_text())
    t = plan(report, catalog, fixes, a.max_steps)
    out = Path(a.out) if a.out else Path(a.report).parent
    out.mkdir(parents=True, exist_ok=True)
    (out / "triage.json").write_text(json.dumps(t, indent=2) + "\n")
    (out / "triage.md").write_text(render_md(t, report["repo"]["name"]))
    print(f"{report['repo']['name']}: {t['score_now']} -> {t['score_if_all_steps_done']} in {len(t['steps'])} steps -> {out / 'triage.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
