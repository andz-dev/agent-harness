import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import audit  # noqa: E402

FILES = {
    "pyproject.toml": "[project]\nname='x'\nversion='1'\n[tool.pytest.ini_options]\n",
    "src/x.py": "def f():\n    return 1\n",
    "tests/test_a.py": "",
    "tests/test_b.py": "",
    "tests/test_c.py": "",
    "README.md": "# x\n\n## Installation\n\npip install x\n",
    "scripts/lonely.sh": "echo hi\n",
    ".github/workflows/ci.yml": "on: [push, pull_request]\njobs:\n  t:\n    steps:\n      - run: pytest\n",
}


def make(files):
    d = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d


class AuditTests(unittest.TestCase):
    def run_audit(self, files, *extra):
        repo, out = make(files), Path(tempfile.mkdtemp())
        r = subprocess.run(
            [sys.executable, "-I", str(ROOT / "scripts" / "audit.py"), str(repo), "--out", str(out), *extra], capture_output=True, text=True
        )
        return r, out

    def test_end_to_end_report_is_valid_and_consistent(self):
        files = {**FILES, "AGENTS.md": "# Agents\n\nRun `pytest` before committing.\n"}
        r, out = self.run_audit(files, "--name", "demo/x", "--weight", "low")
        self.assertEqual(r.returncode, 0, r.stderr)
        report = json.loads((out / "report.json").read_text())
        self.assertEqual(audit.validate(report), [])
        self.assertEqual(report["repo"]["name"], "demo/x")
        self.assertEqual(report["repo"]["clone_mode"], "local")
        self.assertEqual(len(report["pillars"]), 7)
        ids = [f["check_id"] for f in report["findings"] if f["check_id"] in ("STA-08", "DOC-05")]
        self.assertEqual(sorted(ids), ["DOC-05", "STA-08"])  # replaced, not duplicated
        md = (out / "report.md").read_text()
        self.assertIn("# Harness audit: demo/x", md)
        self.assertIn("## Limitations", md)
        self.assertIn("LLM judgement missing", md)
        self.assertTrue(any(i["path"] == "scripts/lonely.sh" for i in report["entropy"]["items"]))

    def test_second_pass_with_llm_answers(self):
        files = {**FILES, "AGENTS.md": "# Agents\n\nRun `pytest` before committing.\n"}
        r, out = self.run_audit(files)
        self.assertEqual(r.returncode, 0, r.stderr)
        tasks = json.loads((out / "llm_tasks.json").read_text())
        self.assertIn("ORI-05", [t["task_id"] for t in tasks["tasks"]])
        answers = out / "answers.json"
        answers.write_text(
            json.dumps(
                [
                    {
                        "task_id": "ORI-06",
                        "status": "pass",
                        "confidence": "medium",
                        "note": "ok",
                        "evidence": [{"path": "AGENTS.md", "line": 3, "snippet": "Run `pytest` before committing."}],
                    },
                    {
                        "task_id": "ORI-05",
                        "status": "pass",
                        "confidence": "high",
                        "note": "forged",
                        "evidence": [{"path": "AGENTS.md", "line": 3, "snippet": "src/ holds the code"}],
                    },
                ]
            )
        )
        r, out2 = self.run_audit(files, "--llm-answers", str(answers))
        self.assertEqual(r.returncode, 0, r.stderr)
        report = json.loads((out2 / "report.json").read_text())
        self.assertEqual(audit.validate(report), [])
        st = {f["check_id"]: f["status"] for f in report["findings"]}
        self.assertEqual((st["ORI-06"], st["ORI-05"]), ("pass", "unknown"))  # forged quote -> unknown

    def test_no_supported_component_exits_3(self):
        r, out = self.run_audit({"main.go": "package main\n", "go.mod": "module x\n"})
        self.assertEqual(r.returncode, 3)
        self.assertFalse((out / "report.json").exists())

    def test_bad_directory_exits_2(self):
        r = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "audit.py"), "/nonexistent-dir"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_validation_catches_tampering(self):
        r, out = self.run_audit(FILES)
        report = json.loads((out / "report.json").read_text())
        report["score"]["final"] = (report["score"]["final"] + 7) % 100
        self.assertTrue(audit.validate(report))
        report = json.loads((out / "report.json").read_text())
        report["findings"][0]["status"] = "pass"
        report["findings"][0]["evidence"] = []
        self.assertTrue(audit.validate(report))


if __name__ == "__main__":
    unittest.main()
