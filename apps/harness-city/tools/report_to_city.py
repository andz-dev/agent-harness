#!/usr/bin/env python3
"""Convert harness-audit output into data/cities.json for Harness City.

Accepted inputs (files or directories, any mix):
  * a scan export   {"format": "harness-audit scan export ...", "repos": [...]}
  * a single report  report.json following harness-audit/schema/report.schema.json
Directories are searched for *.json.

Usage:
  python3 tools/report_to_city.py harness-scan-compact.json -o data/cities.json
  python3 tools/report_to_city.py reports/ --title "Acme Harness City" --source "nightly scan"
  python3 tools/report_to_city.py a.json b.json --gut gut.json   # gut.json: {"repo-name": 70, ...}
"""
import argparse, json, sys, re
from pathlib import Path

PILLARS = ["verification", "orientation", "static_guardrails", "workflow_entry_points",
           "automatic_triggers", "pipeline_parity", "doc_hygiene"]
RENDERED_DECAY = {"ENR-01", "ENR-02", "ENR-04"}   # the decay kinds the page can draw
MAX_STEPS = 3


def short(text):
    text = re.split(r"\s+Why:", text or "")[0].strip()
    return text.rstrip(".")


def steps_from_export(r):
    out = []
    for s in (r.get("fix_plan") or {}).get("steps", [])[:MAX_STEPS]:
        acts = [a.rstrip(".") for a in s.get("actions", [])]
        text = "; ".join([acts[0]] + [a[:1].lower() + a[1:] for a in acts[1:]]) if acts else ""
        text = re.sub(r"\s*\((task, make, npm run[^)]*)\)", "", text)
        out.append({"c": " + ".join(s.get("check_ids", [])), "t": text, "p": s.get("points_gained")})
    if not out:
        for g in (r.get("top_gaps") or [])[:MAX_STEPS]:
            out.append({"c": g["check_id"], "t": short(g.get("fix")), "p": None})
    return out


def entropy(items, warn, name):
    out = []
    for e in items or []:
        if e["check_id"] in RENDERED_DECAY:
            out.append({"c": e["check_id"], "p": e["path"]})
        else:
            warn.append(f"{name}: entropy kind {e['check_id']} is not drawn (skipped)")
    return out


def from_export_repo(r, warn):
    s = r["summary"]
    lv = s["pillar_levels"]
    L = [lv[p] for p in PILLARS]
    caps = []
    if lv["verification"] == 0 and s["score"] <= 40:       # compact export has no cap field
        caps = ["no-tests"]
    fp = r.get("fix_plan") or {}
    return {
        "id": r["id"], "set": r.get("set", ""), "gut": r.get("human_gut_score"),
        "score": s["score"], "L": L, "comp": s.get("components", 1), "files": s.get("tracked_files", 0),
        "pen": s.get("entropy_penalty", 0), "done": fp.get("score_if_all_steps_done"),
        "steps": steps_from_export(r), "ent": entropy((r.get("entropy") or {}).get("items"), warn, r["id"]),
        "caps": caps,
    }


def from_report(d, warn):
    name = d["repo"]["name"]
    by = {p["pillar"]: p["level"] for p in d["pillars"]}
    comps = d.get("stack", {}).get("components", [])
    sc = d["score"]
    return {
        "id": name.split("/")[-1].split(" (")[0], "set": "", "gut": None,
        "score": round(sc["final"]), "L": [by.get(p, 0) for p in PILLARS],
        "comp": len(comps) or 1, "files": sum(c.get("tracked_files", 0) for c in comps),
        "pen": sc.get("entropy_penalty", 0), "done": None,
        "steps": [{"c": g["check_id"], "t": short(g.get("fix")), "p": None} for g in d.get("top_gaps", [])[:MAX_STEPS]],
        "ent": entropy(d.get("entropy", {}).get("items"), warn, name),
        "caps": [cap.get("id", "") if isinstance(cap, dict) else str(cap) for cap in sc.get("caps_applied", [])],
    }


def collect(paths):
    for p in map(Path, paths):
        yield from (sorted(p.rglob("*.json")) if p.is_dir() else [p])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out", default="data/cities.json")
    ap.add_argument("--title", default="Harness City")
    ap.add_argument("--source", default="")
    ap.add_argument("--gut", help="JSON file {repo id: human score} merged into the cities")
    a = ap.parse_args()

    warn, cities, meta = [], [], {"title": a.title}
    for f in collect(a.inputs):
        d = json.loads(Path(f).read_text())
        if "repos" in d:
            cities += [from_export_repo(r, warn) for r in d["repos"]]
            t = d.get("tool", {})
            meta.setdefault("tool", f"{t.get('name', 'harness-audit')} {t.get('version', '')}".strip())
            meta.setdefault("scanDate", d.get("generated", ""))
        elif "pillars" in d and "score" in d:
            cities.append(from_report(d, warn))
            meta.setdefault("tool", f"{d['tool']['name']} {d['tool']['version']}")
            meta.setdefault("scanDate", d.get("generated_at", "")[:10])
        else:
            warn.append(f"{f}: not a recognised harness-audit file (skipped)")
    if not cities:
        sys.exit("no cities found")
    if a.gut:
        gut = json.loads(Path(a.gut).read_text())
        for c in cities:
            if c["id"] in gut:
                c["gut"] = gut[c["id"]]
    meta["source"] = a.source or ", ".join(Path(f).name for f in collect(a.inputs))
    ids = [c["id"] for c in cities]
    for i in {x for x in ids if ids.count(x) > 1}:
        warn.append(f"duplicate city id {i}: the page needs unique ids")
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"meta": meta, "cities": cities}, indent=1))
    print(f"wrote {out}: {len(cities)} cities")
    for w in warn:
        print("warning:", w, file=sys.stderr)


if __name__ == "__main__":
    main()
