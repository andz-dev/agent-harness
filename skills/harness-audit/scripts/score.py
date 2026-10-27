#!/usr/bin/env python3
"""Turn run_checks findings into pillar levels, a 0-100 score and top gaps.

Usage: score.py <run_checks.json> [--catalog checks/catalog.yaml] [--entropy entropy.json] [--compact]
Output: JSON with keys pillars, score, entropy, top_gaps (the report parts that are derived).

Rules (all arithmetic is re-checked by verify_arithmetic):
  level      : pillar reaches level N when every gate check at levels <= N passes and at least
               pass_ratio of the checks at level N pass. Not-applicable checks are excluded from
               the ratio; unknown checks (llm/git_signal not evaluated) are excluded from the
               ratio but a failing OR unknown GATE blocks the level.
  components : a pillar level is computed per component (its own findings plus repo-level ones);
               the pillar level is the mean weighted by tracked files, rounded half down. weakest_component is reported.
  points     : level / 3 * weight
  score      : final = round(min(raw, lowest cap) - entropy_penalty)
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path, PurePosixPath

import yaml

WEIGHTS = {
    "verification": 25,
    "orientation": 20,
    "static_guardrails": 15,
    "workflow_entry_points": 15,
    "automatic_triggers": 10,
    "pipeline_parity": 10,
    "doc_hygiene": 5,
}
CAPS = {  # id -> (limit, reason, check ids that must ALL be non-pass for the cap to apply)
    "no-tests": (40, "No test files found in any component", ["VER-01", "VER-02"]),
    "no-ci": (60, "No CI definition found", ["CIP-01"]),
    "no-orientation": (70, "No README setup section and no agent instruction file", ["ORI-01", "ORI-02"]),
}
PASS_RATIO = 0.6
DEPENDS_ON_VERIFICATION = ("orientation", "workflow_entry_points")  # instructions are worth only what they can verify (B-121)
MAX_ENTROPY = 10
ENTROPY_MIN_CANDIDATES = 20  # a tiny candidate set must not turn one finding into a big penalty


def _level_for(findings: list[dict], pass_ratio: float) -> tuple[int, list[str]]:
    """Level of one pillar for one scope, plus the gate checks that blocked the next level."""
    level, blockers = 0, []
    for n in (1, 2, 3):
        at_n = [f for f in findings if f["level"] == n and f["status"] != "not_applicable"]
        gates = [f for f in findings if f["level"] <= n and f["gate"] and f["status"] != "not_applicable"]
        bad = sorted({f["check_id"] for f in gates if f["status"] != "pass"})
        scored = [f for f in at_n if f["status"] in ("pass", "fail", "error")]
        ratio_ok = True if not scored else sum(f["status"] == "pass" for f in scored) / len(scored) >= pass_ratio
        if bad or not ratio_ok:
            if bad:
                blockers = bad
            elif not blockers:
                blockers = sorted({f["check_id"] for f in scored if f["status"] != "pass"})
            return level, blockers
        level = n
    return level, []


def pillar_results(findings: list[dict], components: list[dict], pass_ratio: float = PASS_RATIO) -> list[dict]:
    scored = [c for c in components if c.get("kind") not in ("tooling", "sample")]
    comp_ids = [c["id"] for c in scored] or [None]
    size = {c["id"]: max(1, int(c.get("tracked_files") or 1)) for c in scored}  # weight = tracked files
    out = []
    for pillar, weight in WEIGHTS.items():
        pf = [f for f in findings if f["pillar"] == pillar]
        levels: dict[str | None, int] = {}
        gate_failures: set[str] = set()
        for cid in comp_ids:
            scope = [f for f in pf if f.get("component") in (None, cid)]
            lvl, blockers = _level_for(scope, pass_ratio)
            levels[cid] = lvl
            gate_failures.update(b for b in blockers if any(f["check_id"] == b and f["gate"] for f in scope))
        total = sum(size.get(c, 1) for c in levels)
        level = math.ceil(sum(lv * size.get(c, 1) for c, lv in levels.items()) / total - 0.5 - 1e-9)  # rounds half down
        res = {
            "pillar": pillar,
            "level": level,
            "weight": weight,
            "points": round(level / 3 * weight, 2),
            "gate_failures": sorted(gate_failures) if level < 3 else [],
        }
        if len(levels) > 1:
            res["by_component"] = [{"component": c, "level": lv} for c, lv in levels.items()]
            res["weakest_component"] = min(levels, key=lambda c: (levels[c], str(c)))
        out.append(res)
    _cap_by_verification(out)
    return out


def caps(findings: list[dict]) -> list[dict]:
    applied = []
    for cid, (limit, reason, ids) in CAPS.items():
        rel = [f for f in findings if f["check_id"] in ids and f["status"] in ("pass", "fail")]
        if rel and not any(f["status"] == "pass" for f in rel):
            applied.append({"id": cid, "limit": limit, "reason": reason})
    return applied


def entropy_part(entropy: dict | None) -> dict:
    e = dict(entropy or {})
    cand, flagged = int(e.get("candidate_files", 0)), int(e.get("flagged_files", 0))
    e.setdefault("items", [])
    e.setdefault("history_available", False)
    e["candidate_files"], e["flagged_files"] = cand, flagged
    units = flagged_units(e["items"]) if e["items"] else flagged
    e["penalty"] = float(min(MAX_ENTROPY, round(20 * units / max(ENTROPY_MIN_CANDIDATES, cand))))
    return e


def flagged_units(items: list[dict]) -> int:
    """Flagged files, with numbered families counted once (image01.py ... image12.py is one finding)."""
    keys = {(i["check_id"], i["verdict"], re.sub(r"\d+", "#", PurePosixPath(i["path"]).name)) for i in items}
    return len(keys)


def top_gaps(findings: list[dict], catalog: dict, pillars: list[dict], limit: int = 5) -> list[dict]:
    weights = {p["pillar"]: p["weight"] for p in pillars}
    seen, cands = set(), []
    for f in findings:
        if f["status"] != "fail" or f["check_id"] in seen:
            continue
        seen.add(f["check_id"])
        # Highest value first: heavy pillar, low level, gates before non-gates.
        cands.append((-(weights[f["pillar"]] * (4 - f["level"]) * (2 if f["gate"] else 1)), f["check_id"]))
    titles = {c["id"]: c for c in catalog["checks"]}
    gaps = []
    for _, cid in sorted(cands)[:limit]:
        c = titles[cid]
        gaps.append({"check_id": cid, "fix": f"{c['title']}. Why: {c['rationale']}"})
    return gaps


def score_part(pillars: list[dict], applied: list[dict], penalty: float) -> dict:
    raw = round(sum(p["points"] for p in pillars), 2)
    cap = min([c["limit"] for c in applied], default=100)
    return {"raw": raw, "caps_applied": applied, "entropy_penalty": penalty, "final": max(0, round(min(raw, cap) - penalty))}


def verify_arithmetic(parts: dict) -> list[str]:
    """Recompute every derived number; return a list of mismatches (empty = consistent)."""
    errs = []
    pillars, score, ent = parts["pillars"], parts["score"], parts["entropy"]
    for p in pillars:
        if abs(p["points"] - round(p["level"] / 3 * p["weight"], 2)) > 0.005:
            errs.append(f"{p['pillar']}: points {p['points']} != level/3*weight")
    if sum(p["weight"] for p in pillars) != 100:
        errs.append("weights do not sum to 100")
    if abs(score["raw"] - round(sum(p["points"] for p in pillars), 2)) > 0.005:
        errs.append("raw != sum(points)")
    cap = min([c["limit"] for c in score["caps_applied"]], default=100)
    want = max(0, round(min(score["raw"], cap) - score["entropy_penalty"]))
    if score["final"] != want:
        errs.append(f"final {score['final']} != round(min(raw, cap) - penalty) = {want}")
    if score["entropy_penalty"] != ent["penalty"]:
        errs.append("score.entropy_penalty != entropy.penalty")
    if not 0 <= ent["penalty"] <= MAX_ENTROPY:
        errs.append("entropy penalty out of range")
    return errs


def build(run: dict, catalog: dict, entropy: dict | None = None) -> dict:
    findings = run["findings"]
    pillars = pillar_results(findings, run["stack"]["components"], float(catalog["level_rule"].get("pass_ratio", PASS_RATIO)))
    ent = entropy_part(entropy)
    score = score_part(pillars, caps(findings), ent["penalty"])
    parts = {"pillars": pillars, "score": score, "entropy": ent, "top_gaps": top_gaps(findings, catalog, pillars)}
    errs = verify_arithmetic(parts)
    if errs:
        raise AssertionError("score arithmetic self-check failed: " + "; ".join(errs))
    return parts


def _cap_by_verification(pillars: list[dict]) -> None:
    """Orientation and entry-point levels cannot exceed Verification level + 1."""
    ver = next((p for p in pillars if p["pillar"] == "verification"), None)
    if ver is None:
        return
    limit = ver["level"] + 1
    for p in pillars:
        if p["pillar"] in DEPENDS_ON_VERIFICATION and p["level"] > limit:
            p["level"] = limit
            p["points"] = round(limit / 3 * p["weight"], 2)
            p["capped_by"] = "verification"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_checks_json")
    ap.add_argument("--catalog", default=str(Path(__file__).resolve().parent.parent / "checks" / "catalog.yaml"))
    ap.add_argument("--entropy")
    ap.add_argument("--compact", action="store_true")
    a = ap.parse_args(argv)
    run = json.loads(Path(a.run_checks_json).read_text())
    catalog = yaml.safe_load(Path(a.catalog).read_text())
    entropy = json.loads(Path(a.entropy).read_text()) if a.entropy else None
    json.dump(build(run, catalog, entropy), sys.stdout, indent=None if a.compact else 2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
