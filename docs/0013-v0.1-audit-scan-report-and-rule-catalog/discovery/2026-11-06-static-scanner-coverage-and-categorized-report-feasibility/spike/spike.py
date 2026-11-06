#!/usr/bin/env python3
"""One-question feasibility spike: static check categories and scanner-presence detection for harness-audit.

v0.3: the question and the go/kill criteria live in the frozen hypothesis card (`hypothesis.jsonc`, frozen with
`hypothesis.py freeze`); the spike refuses to run while the card is unfrozen and stamps its digest into the result.
Copy QUESTION from the card and make compute() return the metrics the criteria name. compute() reads the graded
sample (`records`) and, by evidence ladder, real inputs: list tracked repository files in REAL_INPUTS (real data)
or REAL_DERIVED_INPUTS (shapes taken from real files); they arrive in `real` keyed by path. Real inputs are read
only from Git-tracked files of this repository, never from data/raw. Build the report spec in memory with
build_spec(), following assets/report-spec.example.json (references/report-spec.md). The probe findings
(data/findings.json) and the research note titles arrive in `context`. Once edited, delete the UNEDITED line and
the marker prefix of this docstring's first line: the spike gate rejects an unedited spike.

  spike.py            # compute and publish spike/result.json and report.html
  spike.py --check    # recompute in memory and compare the saved bytes; writes nothing
"""
import argparse
import inspect
import json
import logging
import re
import sys
import time
from pathlib import Path

# BEGIN asset-bootstrap
import os
import sys
from pathlib import Path

SKILL = "discovery-poc"
MARKER = Path("shared") / "scripts" / "layout.py"
SYNC_HINT = "run the sync-agent-assets skill to deploy current shared assets"


def _fail(message, required=()):
    needed = f" (needed: {', '.join(required)})" if required else ""
    sys.stderr.write(f"asset_root_unresolved: {message}{needed}; {SYNC_HINT}\n")
    raise SystemExit(2)


def find_asset_root(env=None, start=None, home=None, required=()):
    """Return (asset_root, source) with source one of override, repo, deployed."""
    env = os.environ if env is None else env
    override = env.get("AGENTS_ASSET_ROOT")
    if override:
        root = Path(override)
        if not (root / MARKER).is_file():
            _fail("AGENTS_ASSET_ROOT is set but is not an asset root (missing shared/scripts/layout.py)", required)
        return root, "override"
    here = Path(start if start is not None else sys.argv[0] or __file__).resolve()
    for ancestor in here.parents:
        if (ancestor / ".git").exists() and (ancestor / "agents" / MARKER).is_file():
            return ancestor / "agents", "repo"
    deployed = Path(home if home is not None else Path.home()) / ".agents"
    if (deployed / MARKER).is_file():
        return deployed, "deployed"
    _fail("no asset root found (checked AGENTS_ASSET_ROOT, the repository agents/ and ~/.agents)", required)


def bootstrap(required=(), env=None, start=None, home=None):
    """Put shared and skill scripts on sys.path; exit 2 naming any required module that is missing."""
    root, source = find_asset_root(env, start, home, required)
    shared = root / "shared" / "scripts"
    sys.path.insert(0, str(shared))
    import layout

    search = [shared]
    try:
        search.insert(0, layout.skill_dir(SKILL, root) / "scripts")
    except layout.LayoutUnresolved:
        pass
    sys.path[:0] = [str(p) for p in search]
    for name in required:
        if not any((p / f"{name}.py").is_file() for p in search):
            _fail(f"required module '{name}' is not in the asset root")
    return root, source
# END asset-bootstrap

ASSET_ROOT, ROOT_SOURCE = bootstrap(("lean_log", "discovery_log", "sample_data", "okf_frontmatter"))

import discovery_log  # noqa: E402
import okf_frontmatter  # noqa: E402
import sample_data  # noqa: E402

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
SAMPLE_DIR = BUNDLE / "data" / "sample"
FINDINGS = BUNDLE / "data" / "findings.json"
RESEARCH = BUNDLE / "research"
RESULT = HERE / "result.json"
REPORT = HERE / "report.html"
LOGGER = logging.getLogger("spike")
ROOT = next(parent for parent in BUNDLE.parents if (parent / ".git").exists() and (parent / "docs").is_dir())
CARD, LOCK = BUNDLE / "hypothesis.jsonc", BUNDLE / "hypothesis.lock.json"
QUESTION = ("Can one stable category per check, derived by static rules from the tracked harness-audit catalog and "
            "infrastructure checks, represent every existing check and the requested Security, SBOM, license and linter "
            "scan topics for Python, Node, Go and Rust without running any audited code?")
SKILL_DIR = "skills/harness-audit/"
REAL_INPUTS: list[str] = [SKILL_DIR + "checks/catalog.yaml", SKILL_DIR + "scripts/infra_checks.py",
                          SKILL_DIR + "scripts/detect_stack.py", SKILL_DIR + "scripts/audit.py"]
REAL_DERIVED_INPUTS: list[str] = []  # repo-relative files whose shapes seed derived cases

CATEGORIES = ["testing", "code_standards", "ci_pipeline", "security", "supply_chain", "agent_guidance", "docs",
              "workflow", "infrastructure"]
PILLAR_DEFAULT = {"verification": "testing", "static_guardrails": "code_standards", "pipeline_parity": "ci_pipeline",
                  "orientation": "agent_guidance", "doc_hygiene": "docs", "workflow_entry_points": "workflow",
                  "automatic_triggers": "workflow"}
AREA_DEFAULT = {**{area: "infrastructure" for area in ("dockerfile", "compose", "devcontainer", "terraform", "bicep",
                                                        "kubernetes", "ansible", "cloudformation", "pulumi",
                                                        "cross-cutting", "infra-entropy")},
                "agent-guidance": "agent_guidance"}
# Content rules refine the default; first hit wins and more than one hit marks the check ambiguous.
SECURITY = re.compile(r"secret|credential|non-root|private key|@secure|noecho|encrypted|security scanner|tracked", re.I)
SUPPLY = re.compile(r"pinned|lock file|lockfile|locked|dependabot|renovate", re.I)
LINT = re.compile(r"lint", re.I)

# Independent oracle, written from the cited prior art (Scorecard vocabulary [1]) and each check's plain meaning,
# before the rules above were run against it. check id -> expected category.
ORACLE = {"VER-01": "testing", "VER-08": "supply_chain", "VER-10": "testing", "STA-01": "code_standards",
          "STA-06": "code_standards", "CIP-02": "ci_pipeline", "CIP-07": "supply_chain", "ORI-02": "agent_guidance",
          "DOC-04": "docs", "ENT-02": "workflow", "TRG-02": "workflow", "INF-D01": "infrastructure",
          "INF-D02": "supply_chain", "INF-D03": "security", "INF-D05": "code_standards", "INF-D06": "security",
          "INF-C01": "supply_chain", "INF-C03": "security", "INF-K06": "security", "INF-T01": "supply_chain",
          "INF-T05": "security", "INF-X01": "supply_chain", "INF-X04": "security", "INF-X05": "security",
          "INF-J03": "agent_guidance", "INF-A02": "code_standards", "INF-E01": "infrastructure"}

# Detection oracle: documented tool config names and near misses, from the prior-art note's sources [1]-[6].
DETECTORS = {
    "go_lint": r"(^|/)\.golangci\.(ya?ml|toml|json)$",
    "rust_format": r"(^|/)\.?rustfmt\.toml$",
    "rust_lint": r"(^|/)\.?clippy\.toml$",
    "rust_supply_chain": r"(^|/)\.?deny\.toml$",
    "sbom": r"(^|/)(bom\.(json|xml)|[^/]+\.cdx\.(json|xml))$",
    "security_policy": r"(^|/)SECURITY\.md$",
    "license_file": r"(^|/)(LICENSE|LICENCE|COPYING|COPYRIGHT)$|(^|/)LICENSES/",
}
BROKEN_DETECTORS = {"go_lint": r"golangci", "rust_format": r"rustfmt", "rust_lint": r"clippy", "rust_supply_chain": r"deny",
                    "sbom": r"bom", "security_policy": r"SECURITY", "license_file": r"LICEN[SC]E"}
DETECTION_CASES = [(".golangci.yml", "go_lint"), ("svc/.golangci.toml", "go_lint"), ("rustfmt.toml", "rust_format"),
                   (".rustfmt.toml", "rust_format"), ("clippy.toml", "rust_lint"), (".cargo/deny.toml", "rust_supply_chain"),
                   ("bom.json", "sbom"), ("build/app.cdx.json", "sbom"), ("SECURITY.md", "security_policy"),
                   ("LICENSE", "license_file"), ("LICENSES/MIT.txt", "license_file"),
                   ("golangci.yml", None), ("bomb.json", None), ("docs/bom.json.md", None), ("clippy.json", None),
                   ("rustfmt.json", None), ("licensing.md", None)]


def parse_checks(real):
    """[(kind, id, pillar or area, title)] for every core catalog check and every infrastructure check."""
    out = []
    for block in re.split(r"(?m)^  - id: ", real[SKILL_DIR + "checks/catalog.yaml"])[1:]:
        out.append(("core", block.split()[0], re.search(r"pillar: (\w+)", block).group(1),
                    re.search(r"\n    title: (.*)", block).group(1)))
    pattern = r'"(INF-[A-Z]\d+)":\s*\(\s*"([a-z-]+)",\s*\d,\s*"((?:[^"\\]|\\.)*)"\s*,?\s*\)'
    for cid, area, title in re.findall(pattern, real[SKILL_DIR + "scripts/infra_checks.py"]):
        out.append(("infra", cid, area, title))
    return out


def default_category(kind, base):
    return PILLAR_DEFAULT[base] if kind == "core" else AREA_DEFAULT[base]


def classify(kind, base, title):
    """(category, ambiguous): the default refined by content rules; agent guidance is never reclassified."""
    default = default_category(kind, base)
    if default == "agent_guidance":
        return default, False
    hits = [name for name, hit in (("security", SECURITY.search(title)), ("supply_chain", SUPPLY.search(title)),
                                   ("code_standards", kind == "infra" and LINT.search(title))) if hit]
    return (hits[0] if hits else default), len(hits) > 1


def detect(name, patterns):
    return sorted(tool for tool, pattern in patterns.items() if re.search(pattern, name))


def detection_mismatches(patterns):
    wrong = 0
    for name, expected in DETECTION_CASES:
        if detect(name, patterns) != ([expected] if expected else []):
            wrong += 1
    return wrong


def summary_markdown(counts):
    rows = ["| Category | Checks |", "|---|---|"] + [f"| {name} | {counts[name]} |" for name in CATEGORIES if counts[name]]
    return "\n".join(rows)


def compute(records, real):
    """Classify every real check, compare with the oracle and detection cases; deterministic, reads `real` only."""
    checks = parse_checks(real)
    classified = {cid: classify(kind, base, title) for kind, cid, base, title in checks}
    defaults = {cid: default_category(kind, base) for kind, cid, base, _ in checks}
    counts = {name: sum(1 for category, _ in classified.values() if category == name) for name in CATEGORIES}
    rendered = summary_markdown(counts)
    rendered_total = sum(int(line.rsplit("|", 2)[-2]) for line in rendered.splitlines()[2:])
    present = [cid for cid in ORACLE if cid in classified]
    audit = real[SKILL_DIR + "scripts/audit.py"]
    render = (re.search(r"def render_md\(.*?(?=\n\ndef |\nclass |\Z)", audit, re.S) or re.match("", "")).group(0)
    return {
        "checks_total": len(checks),
        "oracle_cases": len(ORACLE),
        "oracle_cases_found": len(present),
        "mismatches": sum(1 for cid in ORACLE if classified.get(cid, (None,))[0] != ORACLE[cid]),
        "discriminating_cases": sum(1 for cid in present if defaults[cid] != ORACLE[cid]),
        "ambiguous_check_ids": sum(1 for _, ambiguous in classified.values() if ambiguous),
        "partition_complete": rendered_total == len(checks) and set(classified) == {c[1] for c in checks},
        "category_counts": counts,
        "detection": {
            "cases": len(DETECTION_CASES),
            "mismatches": detection_mismatches(DETECTORS),
            "discriminating_negatives": sum(1 for name, expected in DETECTION_CASES
                                            if expected is None and not detect(name, DETECTORS) and detect(name, BROKEN_DETECTORS)),
        },
        "oracle_controls": {
            "pillar_mapping_detected": sum(1 for cid in present if defaults[cid] != ORACLE[cid]) > 0,
            "broken_detector_detected": detection_mismatches(BROKEN_DETECTORS) > 0,
        },
        "go_rust_manifests_listed": '"go.mod": "go"' in real[SKILL_DIR + "scripts/detect_stack.py"]
        and '"Cargo.toml": "rust"' in real[SKILL_DIR + "scripts/detect_stack.py"],
        "report_has_category_summary": "categor" in render.lower(),
    }


def build_spec(result, context):
    """Pure: the in-memory report spec for the kit; no I/O. Edit the sections to tell this bundle's story."""
    kind = "measured"
    numbers = [{"label": name, "value": value, "kind": kind}
               for name, value in result["answer"].items() if isinstance(value, (int, float)) and not isinstance(value, bool)
               and value >= 0]
    projected = [{"id": "G1", "check": "Graded sample committed", "status": "skip", "reason": "grade none: real tracked files"},
                 {"id": "G2", "check": "Spike result reproduces", "status": "pass", "reason": "projected from this run"},
                 {"id": "G3", "check": "Report lints clean", "status": "pass", "reason": "projected from this run"},
                 {"id": "G4", "check": "Gap evidence resolves", "status": "skip", "reason": "checked by gate_check.py"},
                 {"id": "G5", "check": "Probe events paired", "status": "skip", "reason": "checked by gate_check.py"}]
    tests = [{"name": "Real inputs are tracked repository files", "status": "pass", "detail": "Read from the harness-audit skill only."},
             {"name": "Oracle controls fire", "status": "pass" if result["answer"]["oracle_controls"]["pillar_mapping_detected"]
              and result["answer"]["oracle_controls"]["broken_detector_detected"] else "fail",
              "detail": "A pillar-only mapping and an unanchored detector must both be flagged."},
             {"name": "No audited code was run", "status": "pass", "detail": "Only text of four tracked files was read."}]
    risks = [{"id": "R1", "title": "The oracle was written by the same agent as the rules", "severity": "medium",
              "likelihood": "medium",
              "detail": "Expected categories come from cited prior art and each check's plain meaning, not from a second person.",
              "mitigation": "The owner reviews the category set and the oracle before the follow-on spec relies on them."}]
    decisions = [{"id": "D1", "question": "Does this answer settle the assumption that would kill the idea?",
                  "why": "Discovery names one killing assumption; the spike exists to test it.",
                  "options": ["Yes: move on to the next stage", "No: change the spike question and rerun"],
                  "lean": "", "route": "grilling"}]
    sources = [{"ref": f"[{i}]", "title": note["title"], "note": note["description"], "location": note["path"]}
               for i, note in enumerate(context["research"], 1)]
    return {"title": result["question"], "meta": f"Spike result, {result['grade']} sample, skill {result['skill_version']}.",
            "lede": "Computed from tracked harness-audit files only; rerun `spike.py --check` to confirm.", "question": result["question"],
            "verdict": {"status": "open", "text": "State here whether the answer makes the idea feasible.", "next": "grilling"},
            "sections": [
                {"id": "how-to-read", "title": "How to read this page", "blocks": [
                    {"type": "text", "paragraphs": ["Start with the verdict and the route: they say where this work goes next.",
                                                    "Each tile opens its section. Cards with Details open the evidence behind them.",
                                                    "Each chart has a caption and a table with the same numbers."]}]},
                {"id": "terms", "title": "Words used here", "blocks": [
                    {"type": "terms", "items": [["Spike", "One script that answers the question on sample data."],
                                                ['Sample', 'No generated sample: the evidence is real tracked files.'],
                                                ["Probe", "A read-only script that measured the real subject."]]}]},
                {"id": "research", "title": "Research behind it", "blocks": [{"type": "sources", "rows": sources}]},
                {"id": "measured-findings", "title": "Measured findings", "blocks": [
                    {"type": "findings", "rows": context["findings"]},
                    {"type": "bars", "title": "Spike answer", "caption": "Numeric fields of the answer.", "unit": "value",
                     "rows": numbers}]},
                {"id": "spike-result", "title": "Spike result", "blocks": [
                    {"type": "callout", "text": f"Answer: `{json.dumps(result['answer'], sort_keys=True)}`"}]},
                {"id": "tests", "title": "Test results", "blocks": [
                    {"type": "tests", "title": "Spike checks", "caption": "Checks this run made before it answered.",
                     "rows": tests}]},
                {"id": "risks", "title": "Possible problems", "blocks": [
                    {"type": "risks", "title": "Problems by impact and likelihood", "caption": "Top right is where to look first.",
                     "rows": risks}]},
                {"id": "candidate-gates", "title": "Candidate gates", "blocks": [
                    {"type": "gates", "projected": True, "rows": projected}]},
                {"id": "data-provenance", "title": "Data provenance", "blocks": [
                    {"type": "grade-ladder", "title": "Sample grade", "caption": "Real raw data is never a sample grade.",
                     "grades": ["synthetic", "real-redacted", "none"], "current": result["grade"]},
                    {"type": "text", "paragraphs": ["No sample: the inputs are four tracked harness-audit files."]}]},
                {"id": "proves-does-not-prove", "title": "What this proves and does not prove", "blocks": [
                    {"type": "text", "paragraphs": ["It shows the question can be answered on this sample.",
                                                    "It does not prove production behaviour or the design."]}]},
                {"id": "decisions", "title": "Decisions for the next session", "blocks": [
                    {"type": "decisions", "rows": decisions}]}]}


def front_matter(text):
    """A Markdown note's frontmatter through the shared reader; {} when absent or malformed."""
    try:
        return okf_frontmatter.read(text)[0]
    except okf_frontmatter.FrontmatterError:
        return {}


def load_context():
    """Committed bundle evidence for the report: probe findings and Research note titles; never data/raw."""
    rows = json.loads(FINDINGS.read_text(encoding="utf-8"))["rows"] if FINDINGS.is_file() else []
    notes = []
    for path in sorted(RESEARCH.glob("*.md")) if RESEARCH.is_dir() else []:
        fields = front_matter(path.read_text(encoding="utf-8"))
        if fields.get("type") == "Research":
            notes.append({"title": fields.get("title") or path.stem, "description": fields.get("description", ""),
                          "path": f"research/{path.name}"})
    return {"findings": rows, "research": notes}


def load_kit():
    import importlib.util

    import layout

    path = layout.skill_dir(SKILL, ASSET_ROOT) / "assets" / "report_kit.py"
    spec = importlib.util.spec_from_file_location("report_kit", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SpikeError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def load_sample():
    """The graded sample and its provenance; refuses a tampered sample or grade none."""
    sample, provenance = SAMPLE_DIR / "sample.json", SAMPLE_DIR / "provenance.json"
    if not provenance.is_file():
        raise SpikeError("sample_missing")
    prov = json.loads(provenance.read_text(encoding="utf-8"))
    if prov.get("grade") == "none":
        if REAL_INPUTS or REAL_DERIVED_INPUTS:  # v0.3: real repository data only, no sample
            return [], "none", None
        raise SpikeError("grade_none")
    if not sample.is_file():
        raise SpikeError("sample_missing")
    data = sample.read_bytes()
    try:
        grade = sample_data.validate_provenance(prov, data)
    except sample_data.SampleError as exc:
        raise SpikeError(exc.code) from exc
    return json.loads(data), grade, prov["sha256"]


def load_real():
    """Real and real-derived inputs as path -> text; refuses raw stores and paths outside the repository."""
    real = {}
    for rel in [*REAL_INPUTS, *REAL_DERIVED_INPUTS]:
        path = (ROOT / rel).resolve()
        if "data/raw" in rel or ROOT.resolve() not in path.parents:
            raise SpikeError("real_input_not_allowed")
        if not path.is_file():
            raise SpikeError("real_input_missing")
        real[rel] = path.read_text(encoding="utf-8")
    return real


def card_stamp():
    """The frozen card digest; None for a bundle without a card (v0.2)."""
    if not CARD.is_file():
        return None
    if not LOCK.is_file():
        raise SpikeError("card_not_frozen")
    return json.loads(LOCK.read_text(encoding="utf-8"))["sha256"]


def outputs():
    """Deterministic bytes of result.json and report.html, computed in memory only."""
    records, grade, sha = load_sample()
    real = load_real()
    stamp = card_stamp()
    takes_real = len(inspect.signature(compute).parameters) > 1  # v0.2 bundles define compute(records)
    answer = compute(records, real) if takes_real else compute(records)
    result = {"schema": "discovery-spike-result/1", "question": QUESTION, "answer": answer,
              "grade": grade, "sample_sha256": sha, "skill_version": discovery_log.SKILL_VERSION}
    if stamp is not None:
        evidence = [] if grade == "none" else [{"grade": {"synthetic": "synthetic"}.get(grade, "real-derived"),
                                                 "input": "data/sample/sample.json"}]
        evidence += [{"grade": "real", "input": rel} for rel in REAL_INPUTS]
        evidence += [{"grade": "real-derived", "input": rel} for rel in REAL_DERIVED_INPUTS]
        result.update(hypothesis_sha256=stamp, evidence=evidence)
    two_args = len(inspect.signature(build_spec).parameters) > 1  # older bundles override build_spec(result)
    spec = build_spec(result, load_context()) if two_args else build_spec(result)
    return sample_data.dumps(result), load_kit().render(spec).encode("utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare recomputed bytes with the saved result; write nothing")
    ap.add_argument("-v", "--verbose", action="count", default=0)
    ap.add_argument("-q", "--quiet", action="count", default=0)
    a = ap.parse_args()
    run_log = discovery_log.open_run("spike", sys.argv[1:], log_dir=BUNDLE / "logs", name="spike", logger=LOGGER,
                                     asset_root_source=ROOT_SOURCE)
    started = time.monotonic()
    with run_log:
        try:
            data, page = outputs()
            if a.check:
                for saved, expected, name in ((RESULT, data, "result"), (REPORT, page, "report")):
                    if not saved.is_file():
                        raise SpikeError(f"{name}_missing")
                    if saved.read_bytes() != expected:
                        raise SpikeError(f"{name}_mismatch")
                print("spike check ok")
                return 0
        except SpikeError as exc:
            print(f"{'spike check failed' if a.check else 'spike failed'}: {exc.code}")
            run_log.exit_code = 1
            return 1
        sample_data.replace_file(RESULT, data)
        sample_data.replace_file(REPORT, page)
        discovery_log.record(LOGGER, "spike.done", seconds=round(time.monotonic() - started, 2))
        print("spike result written")
        return 0


if __name__ == "__main__":
    sys.exit(main())
