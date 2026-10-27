import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import git_signals  # noqa: E402
import score  # noqa: E402

CATALOG = yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text())
PYPROJECT = "[project]\nname='x'\nversion='1'\n"


def make(tree, commit_date=None):
    d = Path(tempfile.mkdtemp())
    for rel, text in tree.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    if commit_date:
        env = {
            **os.environ,
            "GIT_AUTHOR_DATE": commit_date,
            "GIT_COMMITTER_DATE": commit_date,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        }
        for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
            subprocess.run(["git", "-C", str(d), *cmd], check=True, env=env, capture_output=True)
    return d


def audit(tree, **kw):
    return git_signals.run(make(tree, **kw), CATALOG)


def items(res, cid):
    return [i for i in res["entropy"]["items"] if i["check_id"] == cid]


class OrphanTests(unittest.TestCase):
    def test_recently_touched_unreferenced_script_is_maintained_tooling(self):
        """Holdout (rich, django, nestjs): manual maintenance scripts are not dead code."""
        tree = {"pyproject.toml": PYPROJECT, "a.py": "", "scripts/release.sh": "echo"}
        recent = audit(tree, commit_date=date.today().isoformat() + "T12:00:00")
        self.assertEqual(items(recent, "ENR-01"), [])
        old = audit(tree, commit_date="2019-01-01T12:00:00")
        self.assertEqual([i["path"] for i in items(old, "ENR-01")], ["scripts/release.sh"])

    def test_referenced_script_is_active_unreferenced_is_orphaned(self):
        res = audit(
            {
                "pyproject.toml": PYPROJECT,
                "a.py": "",
                "scripts/used.sh": "echo",
                "scripts/lonely.sh": "echo",
                "Makefile": "build:\n\t./scripts/used.sh\n",
            }
        )
        self.assertEqual([i["path"] for i in items(res, "ENR-01")], ["scripts/lonely.sh"])

    def test_script_does_not_keep_itself_alive(self):
        res = audit({"pyproject.toml": PYPROJECT, "a.py": "", "scripts/self.sh": "# usage: scripts/self.sh\n"})
        self.assertEqual(len(items(res, "ENR-01")), 1)

    def test_doc_reference_counts_and_python_module_path(self):
        res = audit(
            {
                "pyproject.toml": PYPROJECT,
                "a.py": "",
                "scripts/doc.py": "",
                "scripts/mod.py": "",
                "README.md": "Run scripts/doc.py first.\n",
                "Makefile": "x:\n\tpython -m scripts.mod\n",
            }
        )
        self.assertEqual(items(res, "ENR-01"), [])


class ConfigTests(unittest.TestCase):
    def test_duplicate_tool_config_same_dir(self):
        res = audit({"pyproject.toml": PYPROJECT + "[tool.ruff]\nline-length=100\n", "ruff.toml": "line-length = 80\n", "a.py": ""})
        self.assertEqual(len(items(res, "ENR-02")), 1)
        self.assertEqual(items(res, "ENR-02")[0]["verdict"], "conflicting")
        self.assertEqual(next(f for f in res["findings"] if f["check_id"] == "STA-08")["status"], "fail")

    def test_sta08_pass_has_found_evidence_and_na_without_configs(self):
        # The report schema requires a "found" item for every pass.
        res = audit({"pyproject.toml": PYPROJECT + "[tool.ruff]\n", "a.py": ""})
        f = next(x for x in res["findings"] if x["check_id"] == "STA-08")
        self.assertEqual((f["status"], f["evidence"][0]["kind"]), ("pass", "found"))
        res = audit({"pyproject.toml": PYPROJECT, "a.py": ""})
        self.assertEqual(next(x for x in res["findings"] if x["check_id"] == "STA-08")["status"], "not_applicable")

    def test_same_tool_in_different_dirs_is_fine(self):
        res = audit({"pyproject.toml": PYPROJECT, "a.py": "", "web/package.json": "{}", "web/.prettierrc": "{}", ".prettierrc": "{}"})
        self.assertEqual(items(res, "ENR-02"), [])

    def test_prettier_dependency_is_not_a_config(self):
        # Regression (open-webui): "prettier": "^3.0.0" in devDependencies is not a config.
        pkg = '{"devDependencies": {"prettier": "^3.0.0"}}'
        res = audit({"package.json": pkg, "index.js": "", ".prettierrc": "{}"})
        self.assertEqual(items(res, "ENR-02"), [])
        pkg = '{"prettier": {"semi": false}}'
        res = audit({"package.json": pkg, "index.js": "", ".prettierrc": "{}"})
        self.assertEqual(len(items(res, "ENR-02")), 1)

    def test_dead_config_and_implied_tool(self):
        res = audit({"pyproject.toml": PYPROJECT, "a.py": "", ".flake8": "[flake8]\n", "babel.config.js": ""})
        self.assertEqual([i["path"] for i in items(res, "ENR-07")], [".flake8", "babel.config.js"])
        res = audit({"package.json": '{"scripts":{"build":"docusaurus build"}}', "i.js": "", "babel.config.js": ""})
        self.assertEqual(items(res, "ENR-07"), [])
        res = audit({"pyproject.toml": PYPROJECT, "a.py": "", ".flake8": "", "Makefile": "lint:\n\tflake8 .\n"})
        self.assertEqual(items(res, "ENR-07"), [])


class CiReferenceTests(unittest.TestCase):
    def wf(self, run, extra=""):
        return f"on: push\n{extra}jobs:\n  t:\n    steps:\n      - run: {run}\n"

    def test_missing_script_flagged_existing_not(self):
        base = {"pyproject.toml": PYPROJECT, "a.py": "", "scripts/ok.sh": "x"}
        res = audit({**base, ".github/workflows/ci.yml": self.wf("bash scripts/ok.sh && bash scripts/gone.sh")})
        got = items(res, "ENR-04")
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["verdict"], "stale")
        self.assertEqual(got[0]["evidence"][1]["path"], "scripts/gone.sh")

    def test_generated_cloned_and_cd_paths_skipped(self):
        base = {"pyproject.toml": PYPROJECT, "a.py": ""}
        for run in ("node dist/cli.js", "cd other && bash tools/x.sh", "git clone u r && bash r/x.sh"):
            self.assertEqual(items(audit({**base, ".github/workflows/ci.yml": self.wf(run)}), "ENR-04"), [], run)
        wf = "on: push\njobs:\n  t:\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          repository: o/r\n      - run: bash tools/x.sh\n"
        self.assertEqual(items(audit({**base, ".github/workflows/ci.yml": wf}), "ENR-04"), [])


class HistoryTests(unittest.TestCase):
    def test_no_git_means_no_history_and_adr_unknown(self):
        res = audit({"pyproject.toml": PYPROJECT, "a.py": "", "docs/adr/0001.md": "x"})
        self.assertFalse(res["entropy"]["history_available"])
        adr = next(f for f in res["findings"] if f["check_id"] == "DOC-05")
        self.assertEqual(adr["status"], "unknown")

    def test_adr_recency_with_history(self):
        tree = {"pyproject.toml": PYPROJECT, "a.py": "", "docs/adr/0001.md": "x"}
        new = (date.today() - timedelta(days=30)).isoformat() + "T12:00:00"
        old = (date.today() - timedelta(days=900)).isoformat() + "T12:00:00"
        r_new, r_old = audit(tree, commit_date=new), audit(tree, commit_date=old)
        self.assertTrue(r_new["entropy"]["history_available"])
        self.assertEqual(next(f for f in r_new["findings"] if f["check_id"] == "DOC-05")["status"], "pass")
        self.assertEqual(next(f for f in r_old["findings"] if f["check_id"] == "DOC-05")["status"], "fail")

    def test_adr_missing_fails_and_last_commit_recorded(self):
        res = audit({"pyproject.toml": PYPROJECT, "a.py": "", "scripts/lonely.sh": "x"}, commit_date="2024-01-02T12:00:00")
        self.assertEqual(next(f for f in res["findings"] if f["check_id"] == "DOC-05")["status"], "fail")
        self.assertEqual(items(res, "ENR-01")[0]["last_commit"], "2024-01-02")

    def test_shallow_clone_has_no_history(self):
        src = make({"pyproject.toml": PYPROJECT, "a.py": ""}, commit_date="2024-01-02T12:00:00")
        (src / "b.py").write_text("x")
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        subprocess.run(["git", "-C", str(src), "add", "-A"], check=True, env=env)
        subprocess.run(["git", "-C", str(src), "commit", "-q", "-m", "2"], check=True, env=env)
        dst = Path(tempfile.mkdtemp()) / "c"
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{src}", str(dst)], check=True)
        self.assertFalse(git_signals.history_available(dst))
        self.assertTrue(git_signals.history_available(src))


class OutputTests(unittest.TestCase):
    def test_not_evaluated_listed_and_entropy_shape_validates(self):
        import json

        from jsonschema import Draft202012Validator

        res = audit({"pyproject.toml": PYPROJECT, "a.py": "", "scripts/lonely.sh": "x"})
        self.assertEqual([n["check_id"] for n in res["not_evaluated"]], ["ENR-03", "ENR-05", "ENR-06"])
        schema = json.loads((ROOT / "schema" / "report.schema.json").read_text())
        Draft202012Validator({"$ref": "#/properties/entropy", "$defs": schema["$defs"], "properties": schema["properties"]}).validate(
            score.entropy_part(res["entropy"])
        )


if __name__ == "__main__":
    unittest.main()
