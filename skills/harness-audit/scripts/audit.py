#!/usr/bin/env python3
"""harness-audit entry point: run all script-based layers and write report.json + report.md.

Usage: python3 -I audit.py <repo-path> [--out DIR] [--name NAME] [--url URL] [--weight low|mid|high]
                           [--catalog FILE]
Layers: detect_stack -> run_checks -> git_signals -> score. The LLM layer is not part of this
script; its checks are reported as "unknown" and listed under limitations.
The report is validated against schema/report.schema.json before it is written.
Exit codes: 0 ok, 2 bad arguments, 3 no supported component, 4 report failed validation.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect_infra  # noqa: E402
import detect_stack  # noqa: E402
import git_signals  # noqa: E402
import llm_layer  # noqa: E402
import run_checks  # noqa: E402
import score  # noqa: E402
import triage  # noqa: E402
import yaml  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
VERSION = "1.2.0"
PILLAR_LABEL = {
    "orientation": "Orientation",
    "verification": "Verification",
    "static_guardrails": "Static guardrails",
    "workflow_entry_points": "Workflow entry points",
    "automatic_triggers": "Automatic triggers",
    "pipeline_parity": "Pipeline parity",
    "doc_hygiene": "Doc hygiene",
}


def repo_meta(root: Path, name: str | None, url: str | None, weight: str | None) -> dict:
    commit = (git_signals.git(root, "rev-parse", "HEAD") or "").strip()
    if git_signals.git(root, "rev-parse", "--git-dir") is None:
        mode = "local"
    elif git_signals.history_available(root):
        mode = "full"
    else:
        mode = "shallow"
    meta = {"name": name or root.resolve().name, "commit": commit or "0000000", "clone_mode": mode}
    if url:
        meta["url"] = url
    if weight:
        meta["weight"] = weight
    return meta


def limitations(root_meta: dict, stack_result: dict, run: dict, git: dict, findings: list[dict]) -> list[str]:
    out = []
    if root_meta["commit"] == "0000000":
        out.append("Not a git repository: file list came from the directory, history checks were skipped.")
    elif not git["entropy"]["history_available"]:
        out.append("Shallow clone: last-commit dates and ADR recency were not evaluated.")
    llm = sorted({f["check_id"] for f in findings if f["source"] == "llm" and f["status"] == "unknown"})
    if llm:
        out.append(f"LLM judgement missing or unverifiable for {len(llm)} checks ({', '.join(llm)}).")
    blocked = sorted({f["check_id"] for f in findings if f["gate"] and f["status"] == "unknown"})
    if blocked:
        out.append(f"Not-evaluated gate checks ({', '.join(blocked)}) keep their pillars below level 3.")
    for n in git["not_evaluated"]:
        if n["check_id"] in ("ENR-03", "ENR-05") and any(f["source"] == "llm" and f["status"] != "unknown" for f in findings):
            continue  # derived from the LLM answers
        out.append(f"{n['check_id']} not evaluated: {n['reason']}.")
    unsup = stack_result["stack"].get("unsupported") or []
    if unsup:
        langs = sorted({u["language"] for u in unsup})
        out.append(f"Components in unsupported languages were not audited: {', '.join(langs)} ({len(unsup)} manifests).")
    tooling = [c["id"] for c in stack_result["stack"]["components"] if c["kind"] == "tooling"]
    if tooling:
        out.append(f"Tooling-only workspace roots are not scored per component: {', '.join(tooling)}.")
    samples = [c["id"] for c in stack_result["stack"]["components"] if c["kind"] == "sample"]
    if samples:
        out.append(f"{len(samples)} sample/fixture packages (playground, demo, tests) are not scored per component.")
    errors = sorted({f["check_id"] for f in findings if f["status"] == "error"})
    if errors:
        out.append(f"Detector errors: {', '.join(errors)}.")
    out += [f"Warning: {w}" for w in (run.get("warnings") or [])[:5]]
    return out


def infra_limitations(infra: dict) -> list[str]:
    real = [d for d in infra["detected"] if not d["sample"]]
    if not real:
        return []
    return [
        f"Infrastructure found but not scored: {', '.join(infra['tools'])} ({len(real)} locations). "
        "The score says nothing about it (see the Infrastructure section)."
    ]


def assemble(root: Path, catalog: dict, name=None, url=None, weight=None, llm_answers=None, tasks_out=None) -> dict:
    stack_result = detect_stack.detect(root)
    stack = stack_result["stack"]
    if not stack["components"]:
        raise SystemExit_(3, "no supported component (Python or Node) found")
    run = run_checks.run(root, catalog)
    git = git_signals.run(root, catalog)
    plan = llm_layer.plan(root, catalog)
    if tasks_out is not None:
        tasks_out.update(plan)
    llm_findings = list(plan["resolved"])
    entropy = git["entropy"]
    if llm_answers is not None:
        applied = llm_layer.apply_answers(root, plan, llm_answers)
        llm_findings += applied["findings"]
        entropy = {**entropy, "items": entropy["items"] + applied["entropy_items"]}
        entropy["flagged_files"] = len({i["path"] for i in entropy["items"]})
    replaced = {f["check_id"] for f in git["findings"]} | {f["check_id"] for f in llm_findings}
    findings = [f for f in run["findings"] if f["check_id"] not in replaced] + git["findings"] + llm_findings
    parts = score.build({"findings": findings, "stack": stack}, catalog, entropy)
    meta = repo_meta(root, name, url, weight)
    infra = detect_infra.detect(root)
    stack_out = dict(stack)
    stack_out["ecosystems"] = sorted({c["ecosystem"] for c in stack["components"]})
    return {
        "schema_version": "0.1",
        "tool": {"name": "harness-audit", "version": VERSION, "catalog_version": str(catalog["catalog_version"])},
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": meta,
        "stack": stack_out,
        "infra": infra,
        "pillars": parts["pillars"],
        "findings": findings,
        "score": parts["score"],
        "entropy": parts["entropy"],
        "top_gaps": parts["top_gaps"],
        "limitations": limitations(meta, stack_result, run, git, findings) + infra_limitations(infra),
    }


class SystemExit_(Exception):
    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code, self.msg = code, msg


def validate(report: dict) -> list[str]:
    schema = json.loads((HERE / "schema" / "report.schema.json").read_text())
    errs = [
        f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}" for e in Draft202012Validator(schema).iter_errors(report)
    ]
    errs += score.verify_arithmetic(report)
    return errs


def render_md(r: dict, titles: dict[str, str]) -> str:
    s = r["score"]
    lines = [
        f"# Harness audit: {r['repo']['name']}",
        "",
        f"**Score: {s['final']} / 100** (raw {s['raw']}, entropy penalty {s['entropy_penalty']})",
        "",
        f"Commit `{r['repo']['commit'][:12]}`, clone mode {r['repo']['clone_mode']}, "
        f"catalog {r['tool']['catalog_version']}, generated {r['generated_at']}",
        "",
    ]
    if s["caps_applied"]:
        lines += (
            ["## Caps applied", ""] + [f"- **{c['id']}** caps the score at {c['limit']}: {c['reason']}" for c in s["caps_applied"]] + [""]
        )
    lines += ["## Pillars", "", "| Pillar | Level | Points | Blocked by | Weakest component |", "|---|---|---|---|---|"]
    for p in r["pillars"]:
        lines.append(
            f"| {PILLAR_LABEL[p['pillar']]} | L{p['level']} | {p['points']} / {p['weight']} | "
            f"{', '.join(p['gate_failures']) or '-'} | {p.get('weakest_component', '-')} |"
        )
    lines += [""]
    if r["top_gaps"]:
        lines += ["## Top gaps", ""] + [f"{i}. **{g['check_id']}** {g['fix']}" for i, g in enumerate(r["top_gaps"], 1)] + [""]
    fails = {}
    for f in r["findings"]:
        if f["status"] == "fail":
            fails.setdefault(f["pillar"], {}).setdefault(f["check_id"], []).append(f)
    if fails:
        lines += ["## Failed checks", ""]
        for pillar in PILLAR_LABEL:
            if pillar not in fails:
                continue
            lines += [f"### {PILLAR_LABEL[pillar]}", ""]
            for cid, fs in fails[pillar].items():
                comps = [f.get("component") for f in fs if f.get("component")]
                ev = next((e for f in fs for e in f["evidence"]), None)
                where = f" ({', '.join(comps[:4])}{'…' if len(comps) > 4 else ''})" if comps else ""
                tail = f" - {ev['path']}{':' + str(ev['line']) if ev.get('line') else ''}: {ev['snippet']}" if ev else ""
                lines.append(f"- **{cid}**{where} {titles.get(cid, '')}{tail}")
            lines.append("")
    e = r["entropy"]
    lines += [
        "## Entropy",
        "",
        f"{e['flagged_files']} of {e['candidate_files']} examined files flagged "
        f"(history {'available' if e.get('history_available') else 'not available'}). Nothing is deleted; a human decides.",
        "",
    ]
    for it in e["items"][:20]:
        ev = it["evidence"][-1]
        lines.append(f"- {it['verdict']}: `{it['path']}` ({it['check_id']}) {ev['snippet']}")
    if e["items"]:
        lines.append("")
    real = [d for d in r.get("infra", {}).get("detected", []) if not d["sample"]]
    if real:
        lines += ["## Infrastructure (detected, not scored)", "", "| Kind | Tool | Location | Files |", "|---|---|---|---|"]
        lines += [f"| {d['kind']} | {d['tool']} | `{d['scope']}` | {d['file_count']} |" for d in real[:25]]
        lines += ["", f"{len(real)} locations; the list is capped at 25 rows. Infrastructure checks are planned (B-171 and later).", ""]
    if r["limitations"]:
        lines += ["## Limitations", ""] + [f"- {x}" for x in r["limitations"]] + [""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--out", default=".")
    ap.add_argument("--name")
    ap.add_argument("--url")
    ap.add_argument("--weight", choices=["low", "mid", "high"])
    ap.add_argument("--catalog", default=str(HERE / "checks" / "catalog.yaml"))
    ap.add_argument("--llm-answers", help="JSON array of answers to the tasks in llm_tasks.json (second pass)")
    a = ap.parse_args(argv)
    root = Path(a.repo)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    catalog = yaml.safe_load(Path(a.catalog).read_text())
    try:
        answers = json.loads(Path(a.llm_answers).read_text()) if a.llm_answers else None
        tasks: dict = {}
        report = assemble(root, catalog, a.name, a.url, a.weight, answers, tasks)
    except SystemExit_ as exc:
        print(exc.msg, file=sys.stderr)
        return exc.code
    errs = validate(report)
    if errs:
        print("report failed validation:\n  " + "\n  ".join(errs[:20]), file=sys.stderr)
        return 4
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    if tasks.get("tasks"):
        (out / "llm_tasks.json").write_text(json.dumps(tasks, indent=2) + "\n")
    titles = {c["id"]: c["title"] for c in catalog["checks"]}
    (out / "report.md").write_text(render_md(report, titles) + "\n")
    fix_plan = triage.plan(report, catalog, yaml.safe_load((Path(__file__).resolve().parent.parent / "checks" / "fixes.yaml").read_text()))
    (out / "triage.json").write_text(json.dumps(fix_plan, indent=2) + "\n")
    (out / "triage.md").write_text(triage.render_md(fix_plan, report["repo"]["name"]))
    print(f"{report['repo']['name']}: {report['score']['final']}/100 -> {out}/report.json, report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
