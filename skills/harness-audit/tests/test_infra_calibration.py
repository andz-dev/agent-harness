"""Tests for scripts/infra_calibration.py.

Run: python3 -I tests/test_infra_calibration.py
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import infra_calibration as ic  # noqa: E402


def reports(tmp, data):
    for repo, areas in data.items():
        d = Path(tmp) / repo
        d.mkdir()
        (d / "report.json").write_text(json.dumps({"infra": {"levels": {"areas": {a: {"level": v} for a, v in areas.items()}}}}))
    return Path(tmp)


class CalibrationTests(unittest.TestCase):
    def test_template_hides_the_tool_levels(self):
        with tempfile.TemporaryDirectory() as d:
            t = ic.template(reports(d, {"r": {"dockerfile": 2}}))
        self.assertEqual(t["repos"], {"r": {"dockerfile": None}})

    def test_compare_counts_exact_within_one_and_direction(self):
        tool = {"r": {"a": 3, "b": 1, "c": 0}}
        human = {"r": {"a": 1, "b": 1, "c": 1}}
        res = ic.compare(tool, [human])
        s = res["summary"]
        self.assertEqual((s["n"], s["exact"], s["within_one"]), (3, 0.33, 0.67))
        self.assertEqual((s["tool_too_high"], s["tool_too_low"]), (1, 1))
        self.assertEqual([r["area"] for r in res["big_gaps"]], ["a"])

    def test_two_raters_report_their_own_agreement(self):
        res = ic.compare({"r": {"a": 1}}, [{"r": {"a": 1}}, {"r": {"a": 2}}])
        self.assertEqual(res["summary"]["raters_exact"], 0.0)

    def test_unrated_and_unknown_cells_are_skipped(self):
        res = ic.compare({"r": {"a": 1}}, [{"r": {"zzz": 1}}])
        self.assertEqual(res["summary"]["n"], 0)

    def test_load_ratings_ignores_null_and_out_of_range(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"
            p.write_text(json.dumps({"repos": {"r": {"a": None, "b": 2, "c": 9}}}))
            self.assertEqual(ic.load_ratings(p), {"r": {"b": 2}})


if __name__ == "__main__":
    unittest.main()
