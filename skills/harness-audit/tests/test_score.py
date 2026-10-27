import json
import sys
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import score  # noqa: E402

CATALOG = yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text())
SCHEMA = json.loads((ROOT / "schema" / "report.schema.json").read_text())


def f(cid, pillar, level, status, gate=False, comp=None):
    return {"check_id": cid, "pillar": pillar, "level": level, "status": status, "gate": gate, "component": comp}


def stop_at(pillar, level, comp=None):
    """A failing gate one level above `level`, so vacuously-empty higher levels cannot be reached."""
    return f("STOP", pillar, level + 1, "fail", True, comp)


def lvl(findings):
    return score._level_for(findings, 0.6)[0]


class LevelTests(unittest.TestCase):
    def test_gate_failure_blocks_even_with_high_ratio(self):
        fs = [f("A", "orientation", 1, "pass", True), f("B", "orientation", 1, "pass"), f("C", "orientation", 1, "fail", True)]
        self.assertEqual(lvl(fs), 0)

    def test_ratio_needed_at_level(self):
        fs = [f(f"A{i}", "orientation", 1, s) for i, s in enumerate(["pass", "pass", "fail", "fail", "fail"])]
        self.assertEqual(lvl(fs), 0)  # 2/5 < 0.6
        fs = [f(f"A{i}", "orientation", 1, s) for i, s in enumerate(["pass", "pass", "pass", "fail", "fail"])]
        self.assertEqual(lvl(fs + [stop_at("orientation", 1)]), 1)  # 3/5 == 0.6

    def test_unknown_gate_blocks_but_unknown_nongate_is_ignored(self):
        base = [f("A", "orientation", 1, "pass", True), f("B", "orientation", 2, "pass", True)]
        self.assertEqual(lvl(base + [f("C", "orientation", 3, "unknown", True)]), 2)
        self.assertEqual(lvl(base + [f("C", "orientation", 2, "unknown", False)]), 3)
        self.assertEqual(lvl(base + [f("C", "orientation", 3, "unknown", False)]), 3)

    def test_not_applicable_excluded(self):
        fs = [f("A", "orientation", 1, "pass", True), f("B", "orientation", 1, "not_applicable", True), stop_at("orientation", 1)]
        self.assertEqual(lvl(fs), 1)

    def test_level_needs_lower_levels(self):
        fs = [f("A", "orientation", 1, "fail", True), f("B", "orientation", 2, "pass", True)]
        self.assertEqual(lvl(fs), 0)


class PillarTests(unittest.TestCase):
    def test_component_mean_floor_and_weakest(self):
        comps = [{"id": "a", "kind": "service"}, {"id": "b", "kind": "service"}]
        fs = [f("V1", "verification", 1, "pass", True, "a"), f("V1", "verification", 1, "fail", True, "b"), stop_at("verification", 1, "a")]
        res = {p["pillar"]: p for p in score.pillar_results(fs, comps)}
        v = res["verification"]
        self.assertEqual((v["level"], v["weakest_component"]), (0, "b"))
        self.assertEqual(v["gate_failures"], ["STOP", "V1"])

    def test_component_weighting_by_tracked_files(self):
        # Regression (immich): a big tested service must outweigh small docs/tooling packages.
        comps = [
            {"id": "big", "kind": "service", "tracked_files": 900},
            {"id": "docs", "kind": "unknown", "tracked_files": 10},
            {"id": "gh", "kind": "unknown", "tracked_files": 5},
        ]
        fs = [
            f("V1", "verification", 1, "pass", True, "big"),
            f("V1", "verification", 1, "fail", True, "docs"),
            f("V1", "verification", 1, "fail", True, "gh"),
            stop_at("verification", 1, "big"),
        ]
        res = {p["pillar"]: p for p in score.pillar_results(fs, comps)}
        self.assertEqual(res["verification"]["level"], 1)
        self.assertEqual(res["verification"]["weakest_component"], "docs")

    def test_repo_level_findings_apply_to_every_component(self):
        comps = [{"id": "a", "kind": "service"}, {"id": "b", "kind": "service"}]
        fs = [f("O1", "orientation", 1, "pass", True), stop_at("orientation", 1)]
        res = {p["pillar"]: p for p in score.pillar_results(fs, comps)}
        self.assertEqual(res["orientation"]["level"], 1)

    def test_tooling_components_skipped_and_schema_valid(self):
        comps = [{"id": "r", "kind": "tooling"}, {"id": "p", "kind": "sample"}, {"id": "a", "kind": "service"}]
        pillars = score.pillar_results([], comps)
        self.assertEqual(len(pillars), 7)
        v = Draft202012Validator({"$ref": "#/$defs/pillar_result", "$defs": SCHEMA["$defs"]})
        for p in pillars:
            v.validate(p)
            self.assertNotIn("by_component", p)  # only one scored component


class ScoreTests(unittest.TestCase):
    def test_caps(self):
        fs = [
            f("VER-01", "verification", 1, "fail"),
            f("VER-02", "verification", 1, "fail"),
            f("CIP-01", "pipeline_parity", 1, "pass"),
            f("ORI-01", "orientation", 1, "pass"),
            f("ORI-02", "orientation", 1, "fail"),
        ]
        self.assertEqual([c["id"] for c in score.caps(fs)], ["no-tests"])
        fs.append(f("VER-02", "verification", 1, "pass"))
        self.assertEqual(score.caps(fs), [])

    def test_cap_needs_evidence_not_absence(self):
        self.assertEqual(score.caps([]), [])
        self.assertEqual(score.caps([f("VER-01", "verification", 1, "not_applicable")]), [])

    def test_final_is_min_of_raw_and_cap_minus_penalty(self):
        pillars = [{"pillar": p, "level": 3, "weight": w, "points": float(w), "gate_failures": []} for p, w in score.WEIGHTS.items()]
        s = score.score_part(pillars, [{"id": "no-ci", "limit": 60, "reason": "x"}], 4.0)
        self.assertEqual((s["raw"], s["final"]), (100.0, 56))

    def test_entropy_formula_and_clamp(self):
        item = lambda p: {"check_id": "ENR-01", "path": p, "verdict": "orphaned", "evidence": []}  # noqa: E731
        two = [item("scripts/a.sh"), item("scripts/b.sh")]
        self.assertEqual(
            score.entropy_part({"candidate_files": 100, "flagged_files": 2, "items": two})["penalty"], 0.0 + round(20 * 2 / 100)
        )
        self.assertEqual(
            score.entropy_part({"candidate_files": 10, "flagged_files": 2, "items": two})["penalty"], 2.0
        )  # floor of 20 candidates
        many = [item(f"s/{c}.sh") for c in "abcdefghijklmnop"]
        self.assertEqual(score.entropy_part({"candidate_files": 20, "flagged_files": 16, "items": many})["penalty"], 10.0)
        self.assertEqual(score.entropy_part(None)["penalty"], 0.0)
        self.assertFalse(score.entropy_part(None)["history_available"])

    def test_numbered_families_count_once(self):
        # Regression (fastapi): 25 generated image01.py-style scripts are one finding, not 25.
        fam = [
            {"check_id": "ENR-01", "path": f"scripts/p/{n}/image0{i}.py", "verdict": "orphaned", "evidence": []}
            for n in "abcde"
            for i in (1, 2)
        ]
        self.assertEqual(score.flagged_units(fam), 1)
        other = fam + [{"check_id": "ENR-01", "path": "scripts/format.sh", "verdict": "orphaned", "evidence": []}]
        self.assertEqual(score.flagged_units(other), 2)

    def test_self_check_detects_tampering(self):
        run = {"findings": [f("ORI-01", "orientation", 1, "pass", True)], "stack": {"components": [{"id": "a", "kind": "service"}]}}
        parts = score.build(run, CATALOG)
        self.assertEqual(score.verify_arithmetic(parts), [])
        parts["score"]["final"] += 1
        self.assertTrue(score.verify_arithmetic(parts))
        parts["score"]["final"] -= 1
        parts["pillars"][0]["points"] += 1
        self.assertTrue(score.verify_arithmetic(parts))

    def test_top_gaps_limit_and_order(self):
        fs = [
            f("ORI-04", "orientation", 2, "fail", True),
            f("DOC-03", "doc_hygiene", 1, "fail"),
            f("VER-05", "verification", 2, "fail", True),
        ]
        pillars = [{"pillar": p, "weight": w} for p, w in score.WEIGHTS.items()]
        gaps = score.top_gaps(fs, CATALOG, pillars)
        self.assertEqual([g["check_id"] for g in gaps], ["VER-05", "ORI-04", "DOC-03"])
        self.assertTrue(all(g["fix"] for g in gaps))
        many = [f(c["id"], c["pillar"], c["level"], "fail", c["gate"]) for c in CATALOG["checks"]]
        self.assertEqual(len(score.top_gaps(many, CATALOG, pillars)), 5)

    def test_full_build_on_real_catalog_findings_validates(self):
        import tempfile

        import run_checks

        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "pyproject.toml").write_text("[project]\nname='x'\nversion='1'\n")
            (Path(d) / "a.py").write_text("")
            run = run_checks.run(Path(d), CATALOG)
        parts = score.build(run, CATALOG)
        for key, ref in (
            ("pillars", "#/properties/pillars"),
            ("score", "#/properties/score"),
            ("entropy", "#/properties/entropy"),
            ("top_gaps", "#/properties/top_gaps"),
        ):
            Draft202012Validator({"$ref": ref, **{k: SCHEMA[k] for k in ("$defs", "properties")}}).validate(parts[key])


if __name__ == "__main__":
    unittest.main()


class VerificationCapTests(unittest.TestCase):
    """B-121 (opencode): one good agent file must not outrun weak verification."""

    def test_orientation_and_entry_points_capped_at_verification_plus_one(self):
        pillars = [
            {"pillar": "verification", "level": 1, "weight": 25, "points": 8.33, "gate_failures": []},
            {"pillar": "orientation", "level": 3, "weight": 20, "points": 20, "gate_failures": []},
            {"pillar": "workflow_entry_points", "level": 3, "weight": 15, "points": 15, "gate_failures": []},
            {"pillar": "static_guardrails", "level": 3, "weight": 15, "points": 15, "gate_failures": []},
        ]
        score._cap_by_verification(pillars)
        by = {p["pillar"]: p for p in pillars}
        self.assertEqual((by["orientation"]["level"], by["orientation"]["capped_by"]), (2, "verification"))
        self.assertEqual(by["workflow_entry_points"]["points"], 10.0)
        self.assertEqual(by["static_guardrails"]["level"], 3)
        self.assertNotIn("capped_by", by["static_guardrails"])

    def test_no_cap_when_verification_high(self):
        pillars = [
            {"pillar": "verification", "level": 2, "weight": 25, "points": 16.67, "gate_failures": []},
            {"pillar": "orientation", "level": 3, "weight": 20, "points": 20, "gate_failures": []},
        ]
        score._cap_by_verification(pillars)
        self.assertEqual(pillars[1]["level"], 3)


class FrozenWeightsTests(unittest.TestCase):
    """Weights frozen 2026-10-26 (calibration/WEIGHTS-FROZEN.md). Change deliberately, with the holdout report."""

    def test_weights_and_caps_are_frozen(self):
        self.assertEqual(
            score.WEIGHTS,
            {
                "verification": 25,
                "orientation": 20,
                "static_guardrails": 15,
                "workflow_entry_points": 15,
                "automatic_triggers": 10,
                "pipeline_parity": 10,
                "doc_hygiene": 5,
            },
        )
        self.assertEqual({k: v[0] for k, v in score.CAPS.items()}, {"no-tests": 40, "no-ci": 60, "no-orientation": 70})
        self.assertEqual((score.PASS_RATIO, score.MAX_ENTROPY), (0.6, 10))
