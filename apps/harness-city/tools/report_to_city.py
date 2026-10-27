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

Check titles and levels come from the harness-audit catalog (--catalog, default: the
sibling skill's checks/catalog.yaml when present) so the page can explain every level.
"""
import argparse, json, sys, re
from pathlib import Path

PILLARS = ["verification", "orientation", "static_guardrails", "workflow_entry_points",
           "automatic_triggers", "pipeline_parity", "doc_hygiene"]
RENDERED_DECAY = {"ENR-01", "ENR-02", "ENR-04"}   # the decay kinds the page can draw
MAX_STEPS = 3
MAX_EVIDENCE = 3
MAX_SNIPPET = 200
DEFAULT_CATALOG = Path(__file__).resolve().parents[3] / "skills/harness-audit/checks/catalog.yaml"


def catalog_checks(path):
    """Read id, pillar, level, gate, applies_to, title and rationale of each pillar check (no YAML package needed)."""
    checks, cur = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^  - id:\s*(\S+)", line)
        if m:
            cur = checks.setdefault(m.group(1), {})
            continue
        if re.match(r"^\S", line):
            cur = None
        m = re.match(r"^    (pillar|level|gate|applies_to|title|rationale):\s*(.*?)\s*$", line)
        if cur is not None and m:
            cur[m.group(1)] = m.group(2)
    out = {}
    for cid, c in checks.items():
        if c.get("pillar") not in PILLARS:
            continue
        out[cid] = {"p": PILLARS.index(c["pillar"]), "l": int(c.get("level", 0)), "g": c.get("gate") == "true",
                    "a": c.get("applies_to", "[all]").strip("[]"), "t": c.get("title", ""), "w": c.get("rationale", "")}
    return out


def findings(items):
    out = []
    for f in items or []:
        ev = [{"k": e.get("kind", ""), "p": e.get("path", ""), "l": e.get("line"), "x": (e.get("snippet") or "")[:MAX_SNIPPET]}
              for e in (f.get("evidence") or [])[:MAX_EVIDENCE]]
        item = {"c": f["check_id"], "s": f.get("status", "unknown"), "e": ev}
        if f.get("component"):
            item["m"] = f["component"]
        if f.get("note"):
            item["n"] = f["note"][:MAX_SNIPPET]
        out.append(item)
    return out


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
        "caps": caps, "f": findings(r.get("findings")),
    }


MAX_INFRA_ROWS = 10


def infra_block(d):
    """Overlay data for the infrastructure harbor: levels per area and the failing checks. Never part of the score."""
    infra = d.get("infra") or {}
    lv = infra.get("levels") or {}
    areas = lv.get("areas") or {}
    if not areas:
        return None
    wide = set(lv.get("repo_wide") or {})
    return {
        "l": lv.get("overall"),
        "w": lv.get("weakest_area"),
        "n": sum(1 for x in infra.get("detected", []) if not x.get("sample")),
        "tools": sorted(infra.get("tools") or []),
        "a": [
            {"k": k, "l": v["level"], "b": v.get("blocked_by", []), "wide": k in wide}
            for k, v in sorted(areas.items(), key=lambda kv: (kv[0] in wide, kv[0]))
        ],
        "r": [
            {"c": r["check_id"], "t": short(r["title"]), "a": r["area"], "f": r["failed"], "p": r["passed"], "x": r["failing"][:3]}
            for r in infra.get("rollup", [])
            if r["failed"]
        ][:MAX_INFRA_ROWS],
    }


def from_report(d, warn):
    name = d["repo"]["name"]
    by = {p["pillar"]: p["level"] for p in d["pillars"]}
    gates = {p["pillar"]: p.get("gate_failures", []) for p in d["pillars"]}
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
        "G": [gates.get(p, []) for p in PILLARS], "f": findings(d.get("findings")),
        "lim": d.get("limitations", []),
        **({"infra": ib} if (ib := infra_block(d)) else {}),
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
    ap.add_argument("--catalog", help="harness-audit checks/catalog.yaml (check titles for the explanations)")
    a = ap.parse_args()

    warn, cities, meta = [], [], {"title": a.title}
    catalog = Path(a.catalog) if a.catalog else DEFAULT_CATALOG
    if catalog.is_file():
        meta["checks"] = catalog_checks(catalog)
    elif a.catalog:
        sys.exit(f"catalog not found: {catalog}")
    else:
        warn.append("no check catalog found: the page shows levels without per-check explanations")
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
    if "checks" in meta:
        meta["checks"] = meta.pop("checks")
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
