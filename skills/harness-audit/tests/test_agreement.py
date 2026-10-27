import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import agreement


def mk(root, repo, ans):
    d = Path(root) / repo
    d.mkdir(parents=True)
    (d / "answers.json").write_text(json.dumps([{"task_id": t, "status": s} for t, s in ans.items()]))


class AgreementTests(unittest.TestCase):
    def test_full_agreement(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for r in (a, b):
                mk(r, "x", {"T1": "pass", "T2": "fail"})
            res = agreement.compare(agreement.load(a), agreement.load(b))
            self.assertEqual(res["rate"], 1.0)
            self.assertEqual(res["diffs"], [])

    def test_disagreement_listed_and_kappa(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            mk(a, "x", {"T1": "pass", "T2": "fail", "T3": "pass"})
            mk(b, "x", {"T1": "pass", "T2": "pass", "T3": "pass"})
            res = agreement.compare(agreement.load(a), agreement.load(b))
            self.assertEqual(res["agree"], 2)
            self.assertEqual(res["diffs"], [("x", "T2", "fail", "pass")])
            self.assertLess(res["kappa"], 1.0)
            self.assertIn("T2", agreement.render(res))

    def test_only_shared_repos_and_tasks(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            mk(a, "x", {"T1": "pass"})
            mk(a, "only_a", {"T1": "pass"})
            mk(b, "x", {"T1": "pass", "T9": "fail"})
            res = agreement.compare(agreement.load(a), agreement.load(b))
            self.assertEqual(res["n"], 1)
            self.assertEqual(res["repos"], ["x"])

    def test_empty(self):
        res = agreement.compare({}, {})
        self.assertIsNone(res["rate"])
        self.assertIsNone(res["kappa"])


if __name__ == "__main__":
    unittest.main()
