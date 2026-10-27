import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import bootstrap  # noqa: E402

PY = {
    "pyproject.toml": "[project]\nname='x'\nversion='1'\n[tool.pytest.ini_options]\n",
    "src/x/__init__.py": "",
    "tests/test_a.py": "",
    "README.md": "# x\n",
}
NODE = {
    "package.json": json.dumps({"name": "x", "scripts": {"test": "mocha", "lint": "eslint ."}}),
    "pnpm-lock.yaml": "",
    "lib/index.js": "",
    "test/a.js": "",
}


def make(files, git=True):
    d = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    if git:
        env = ["-c", "user.email=a@b", "-c", "user.name=t"]
        for cmd in (["init", "-q"], ["add", "-A"], [*env, "commit", "-qm", "x"]):
            subprocess.run(["git", "-C", str(d), *cmd], check=True, capture_output=True)
    return d


def report(*failed):
    return {"repo": {"name": "t"}, "findings": [{"check_id": c, "status": "fail"} for c in failed]}


class ProposeTests(unittest.TestCase):
    def test_python_repo_gets_uv_ruff_pytest_files(self):
        p = bootstrap.propose(make(PY), report("ORI-02", "ENT-01", "TRG-01", "CIP-07"))
        by = {x["path"]: x["content"] for x in p["files"]}
        self.assertIn("uv sync", by["Taskfile.yml"])
        self.assertIn("uv run pytest", by["Taskfile.yml"])
        self.assertIn("ruff", by[".pre-commit-config.yaml"])
        self.assertIn("`src/`", by["AGENTS.md"])
        self.assertIn("pip", by[".github/dependabot.yml"])

    def test_node_repo_uses_its_package_manager_and_scripts(self):
        p = bootstrap.propose(make(NODE), report("ENT-01", "TRG-01"))
        by = {x["path"]: x["content"] for x in p["files"]}
        self.assertIn("pnpm run lint", by["Taskfile.yml"])
        self.assertIn("pnpm install --frozen-lockfile", by["Taskfile.yml"])
        self.assertTrue(any(s["path"] == ".pre-commit-config.yaml" for s in p["skipped"]))

    def test_existing_files_are_skipped_not_replaced(self):
        repo = make({**PY, "AGENTS.md": "mine", "Makefile": "test:\n\tpytest\n"})
        p = bootstrap.propose(repo, report("ORI-02", "ENT-01"))
        self.assertEqual(p["files"], [])
        self.assertEqual({s["path"] for s in p["skipped"]}, {"AGENTS.md", "Taskfile.yml"})

    def test_only_failed_checks_produce_files(self):
        p = bootstrap.propose(make(PY), report("ORI-03"))
        self.assertEqual([x["path"] for x in p["files"]], ["CONTRIBUTING.md"])

    def test_unknowns_are_marked_todo_not_invented(self):
        p = bootstrap.propose(make(PY), report("ORI-02"))
        self.assertIn("TODO(human)", p["files"][0]["content"])

    def test_unsupported_repo_gets_nothing(self):
        p = bootstrap.propose(make({"main.go": "package main"}), report("ORI-02"))
        self.assertEqual(p["files"], [])
        self.assertTrue(p["notes"])


class NodeHooksTests(unittest.TestCase):
    def test_node_repo_gets_husky_hook_and_a_patch_proposal(self):
        p = bootstrap.propose(make(NODE), report("TRG-01"))
        by = {x["path"]: x for x in p["files"]}
        self.assertIn("pnpm run lint", by[".husky/pre-commit"]["content"])
        self.assertIn("pnpm add --save-dev husky", by["package.json.patch"]["content"])
        self.assertIs(by["package.json.patch"]["apply"], False)

    def test_missing_scripts_become_todos(self):
        node = {**NODE, "package.json": json.dumps({"name": "x"})}
        p = bootstrap.propose(make(node), report("TRG-01"))
        self.assertIn("TODO(human)", {x["path"]: x for x in p["files"]}[".husky/pre-commit"]["content"])

    def test_existing_hook_manager_is_respected(self):
        p = bootstrap.propose(make({**NODE, "lefthook.yml": "pre-commit: {}\n"}), report("TRG-01"))
        self.assertEqual([x["path"] for x in p["files"]], [])

    def test_apply_never_writes_the_patch_into_the_repository(self):
        repo = make(NODE)
        p = bootstrap.propose(repo, report("TRG-01"))
        bootstrap.write(repo, Path(tempfile.mkdtemp()), p, True)
        self.assertTrue((repo / ".husky" / "pre-commit").exists())
        self.assertFalse((repo / "package.json.patch").exists())

    def test_python_repos_do_not_get_husky(self):
        p = bootstrap.propose(make(PY), report("TRG-01"))
        self.assertNotIn(".husky/pre-commit", [x["path"] for x in p["files"]])


class CliTests(unittest.TestCase):
    def run_cli(self, repo, rep, *extra):
        out = Path(tempfile.mkdtemp())
        rp = out / "report.json"
        rp.write_text(json.dumps(rep))
        r = subprocess.run(
            [
                sys.executable,
                "-I",
                str(HERE.parent / "scripts" / "bootstrap.py"),
                str(repo),
                "--report",
                str(rp),
                "--out",
                str(out / "o"),
                *extra,
            ],
            capture_output=True,
            text=True,
        )
        return r, out / "o"

    def test_default_run_does_not_touch_the_repository(self):
        repo = make(PY)
        r, out = self.run_cli(repo, report("ORI-02"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((out / "proposed" / "AGENTS.md").exists())
        self.assertFalse((repo / "AGENTS.md").exists())

    def test_apply_writes_new_files_and_never_overwrites(self):
        repo = make({**PY, "CONTRIBUTING.md": "keep me"})
        r, _ = self.run_cli(repo, report("ORI-02", "ORI-03"), "--apply")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((repo / "AGENTS.md").exists())
        self.assertEqual((repo / "CONTRIBUTING.md").read_text(), "keep me")


if __name__ == "__main__":
    unittest.main()
