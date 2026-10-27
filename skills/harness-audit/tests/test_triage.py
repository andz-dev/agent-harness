import json
import sys
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import triage  # noqa: E402

CATALOG = yaml.safe_load((HERE.parent / "checks" / "catalog.yaml").read_text())
FIXES = yaml.safe_load((HERE.parent / "checks" / "fixes.yaml").read_text())
COMPS = [{"id": "root", "ecosystem": "python", "kind": "app", "tracked_files": 10}]


def finding(cid, status):
    c = next(c for c in CATALOG["checks"] if c["id"] == cid)
    return {"check_id": cid, "pillar": c["pillar"], "level": c["level"], "gate": bool(c.get("gate")), "status": status, "component": None}


def report(statuses, penalty=0.0):
    findings = [finding(c, s) for c, s in statuses.items()]
    final, _ = triage.exact_final(findings, COMPS, penalty, 0.6)
    return {
        "findings": findings,
        "stack": {"components": COMPS},
        "score": {"final": round(final), "entropy_penalty": penalty, "caps_applied": []},
        "entropy": {"items": [], "penalty": penalty, "candidate_files": 0, "flagged_files": 0},
        "repo": {"name": "t"},
    }


class CoverageTests(unittest.TestCase):
    def test_every_catalog_check_has_effort_and_action(self):
        self.assertEqual({c["id"] for c in CATALOG["checks"]}, set(FIXES))
        for cid, f in FIXES.items():
            self.assertIn(f["effort"], (1, 2, 3), cid)
            self.assertTrue(f["action"].endswith("."), cid)


class PlanTests(unittest.TestCase):
    def test_single_gate_fix_is_proposed_with_its_gain(self):
        r = report({"ORI-01": "pass", "ORI-02": "fail"})
        t = triage.plan(r, CATALOG, FIXES)
        self.assertEqual(t["steps"][0]["check_ids"], ["ORI-02"])
        self.assertGreater(t["steps"][0]["points_gained"], 0)
        self.assertEqual(t["score_if_all_steps_done"], t["steps"][-1]["score_after"])

    def test_bundle_when_no_single_fix_moves_the_score(self):
        # Level 2 of orientation needs the ORI-04 gate and 2 of 3 checks: no single fix is enough.
        r = report({"ORI-01": "pass", "ORI-02": "pass", "ORI-04": "fail", "ORI-05": "fail", "ORI-06": "fail"})
        t = triage.plan(r, CATALOG, FIXES)
        ids = t["steps"][0]["check_ids"]
        self.assertEqual(len(ids), 2)  # the gate plus one more reaches 2 of 3
        self.assertIn("ORI-04", ids)

    def test_unknown_checks_are_listed_not_proposed(self):
        r = report({"ORI-01": "pass", "ORI-05": "unknown"})
        t = triage.plan(r, CATALOG, FIXES)
        self.assertEqual(t["needs_judgement_answers"], ["ORI-05"])
        self.assertEqual(t["steps"], [])

    def test_passing_report_has_no_steps(self):
        t = triage.plan(report({"ORI-01": "pass"}), CATALOG, FIXES)
        self.assertEqual((t["steps"], t["no_score_effect_yet"]), ([], []))

    def test_markdown_mentions_steps_and_effort_legend(self):
        t = triage.plan(report({"ORI-01": "pass", "ORI-02": "fail"}), CATALOG, FIXES)
        md = triage.render_md(t, "t")
        self.assertIn("ORI-02", md)
        self.assertIn("Effort: 1 = minutes", md)

    def test_does_not_mutate_the_report(self):
        r = report({"ORI-01": "pass", "ORI-02": "fail"})
        before = json.dumps(r, sort_keys=True)
        triage.plan(r, CATALOG, FIXES)
        self.assertEqual(json.dumps(r, sort_keys=True), before)


class CleanupTests(unittest.TestCase):
    def test_entropy_cleanup_reports_points(self):
        r = report({"ORI-01": "pass"}, penalty=0.0)
        items = [{"check_id": "ENR-01", "path": f"scripts/s{i}.sh", "verdict": "orphaned", "evidence": []} for i in range(10)]
        r["entropy"] = {"items": items, "candidate_files": 20, "flagged_files": 10, "penalty": 10.0}
        r["score"]["entropy_penalty"] = 10.0
        t = triage.plan(r, CATALOG, FIXES)
        self.assertEqual(t["cleanup"][0]["check_id"], "ENR-01")
        self.assertEqual(t["cleanup"][0]["points_gained"], 10.0)


if __name__ == "__main__":
    unittest.main()
