import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import llm_layer  # noqa: E402

CATALOG = yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text())
SCHEMA = json.loads((ROOT / "schema" / "report.schema.json").read_text())
PYPROJECT = "[project]\nname='x'\nversion='1'\n"
AGENTS = (
    "# Agents\n\n## Layout\n\n- `src/x/` holds the library\n- `tests/` mirrors it\n\n"
    "## Commands\n\nRun `task check` before every commit.\nSee `docs/guide.md` and `docs/gone.md`.\n"
)
TREE = {
    "pyproject.toml": PYPROJECT,
    "src/x/a.py": "",
    "AGENTS.md": AGENTS,
    "README.md": "# x\n",
    "docs/guide.md": "guide\n",
    "Taskfile.yml": "version: '3'\ntasks:\n  check:\n    cmds: [pytest]\n",
}


def make(tree):
    d = Path(tempfile.mkdtemp())
    for rel, text in tree.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d


def prepared(tree):
    root = make(tree)
    return root, llm_layer.plan(root, CATALOG)


def task(plan, cid):
    return next(t for t in plan["tasks"] if t["task_id"] == cid)


def ans(tid, status="pass", ev=None, conf="high", note="ok"):
    return {"task_id": tid, "status": status, "confidence": conf, "evidence": ev or [], "note": note}


class PlanTests(unittest.TestCase):
    def test_no_agent_file_resolves_without_a_model(self):
        root, plan = prepared({"pyproject.toml": PYPROJECT, "a.py": "", "README.md": "# x\n"})
        res = {f["check_id"]: f for f in plan["resolved"]}
        for cid in ("ORI-05", "ORI-06", "ORI-08", "ORI-09", "ENT-05"):
            self.assertEqual(res[cid]["status"], "fail", cid)
            self.assertEqual(res[cid]["source"], "script")
        self.assertNotIn("ORI-05", [t["task_id"] for t in plan["tasks"]])

    def test_contributing_alone_still_gets_a_ver11_task(self):
        # Regression: VER-11 may be answered from CONTRIBUTING without any agent file.
        _, plan = prepared({"pyproject.toml": PYPROJECT, "a.py": "", "CONTRIBUTING.md": "Run `pytest tests/test_a.py` for one test.\n"})
        self.assertIn("VER-11", [t["task_id"] for t in plan["tasks"]])

    def test_agents_md_alone_passes_ori08_and_conflict_fails(self):
        _, plan = prepared(TREE)
        self.assertEqual({f["check_id"]: f["status"] for f in plan["resolved"]}["ORI-08"], "pass")
        _, plan = prepared({**TREE, "CLAUDE.md": "x\n"})
        self.assertIn("ORI-08", [t["task_id"] for t in plan["tasks"]])
        t = {**TREE}
        del t["AGENTS.md"]
        _, plan = prepared({**t, "CLAUDE.md": "x\n"})
        self.assertEqual({f["check_id"]: f["status"] for f in plan["resolved"]}["ORI-08"], "fail")

    def test_trg06_not_applicable_without_both_hook_kinds(self):
        # Regression (flask): Git hooks only is not a failure of agent/Git hook sharing.
        git_only = {**TREE, ".pre-commit-config.yaml": "repos:\n  - repo: x\n    hooks:\n      - id: ruff-check\n"}
        _, plan = prepared(git_only)
        self.assertEqual({f["check_id"]: f["status"] for f in plan["resolved"]}["TRG-06"], "not_applicable")
        both = {
            **git_only,
            ".claude/settings.json": '{"hooks": {"PostToolUse": [{"hooks": [{"type": "command", "command": "task check"}]}]}}',
        }
        _, plan = prepared(both)
        self.assertIn("TRG-06", [t["task_id"] for t in plan["tasks"]])

    def test_excerpts_are_numbered_and_facts_hold_runner_targets(self):
        _, plan = prepared(TREE)
        t = task(plan, "ENT-05")
        self.assertIn("   5| - `src/x/` holds the library", t["excerpts"][0]["text"])
        self.assertEqual(t["facts"]["runner_targets"], ["check"])

    def test_translated_readmes_are_not_selected(self):
        # Regression (opencode): README.ar.md sorted before README.md and was sent to the model.
        tree = {**TREE, "README.ar.md": "x\n", "README.zh-CN.md": "x\n", "README.md": "# x\n\nSee `docs/guide.md`.\n"}
        _, plan = prepared(tree)
        paths = [e["path"] for e in task(plan, "ORI-09")["excerpts"]]
        self.assertIn("README.md", paths)
        self.assertNotIn("README.ar.md", paths)
        self.assertNotIn("README.zh-CN.md", [e["path"] for e in task(plan, "DOC-06")["excerpts"]])

    def test_missing_path_candidates(self):
        _, plan = prepared(TREE)
        got = [c["text"] for c in task(plan, "DOC-06")["candidates"]]
        self.assertEqual(got, ["docs/gone.md"])

    def test_excerpt_budget(self):
        big = "\n".join(f"line {i}" for i in range(2000))
        _, plan = prepared({**TREE, "AGENTS.md": big, "README.md": big})
        self.assertLessEqual(sum(e["end_line"] for e in task(plan, "ORI-09")["excerpts"]), llm_layer.MAX_TASK_LINES)


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.root, self.plan = prepared(TREE)

    def apply(self, *answers):
        return llm_layer.apply_answers(self.root, self.plan, list(answers))

    def test_verified_quote_keeps_status_and_fixes_line(self):
        r = self.apply(ans("ORI-05", ev=[{"path": "AGENTS.md", "line": 4, "snippet": "`src/x/` holds the library"}]))
        f = next(x for x in r["findings"] if x["check_id"] == "ORI-05")
        self.assertEqual((f["status"], f["evidence"][0]["line"]), ("pass", 5))  # claimed 4, real 5

    def test_forged_quote_downgrades_to_unknown(self):
        r = self.apply(ans("ORI-05", ev=[{"path": "AGENTS.md", "line": 5, "snippet": "tests live in /secret/dir"}]))
        f = next(x for x in r["findings"] if x["check_id"] == "ORI-05")
        self.assertEqual((f["status"], f["confidence"]), ("unknown", "low"))
        self.assertIn("could not be verified", f["note"])

    def test_quote_from_file_outside_the_task_is_rejected(self):
        r = self.apply(ans("ORI-05", ev=[{"path": "README.md", "line": 1, "snippet": "# x"}]))
        self.assertEqual(next(x for x in r["findings"] if x["check_id"] == "ORI-05")["status"], "unknown")

    def test_far_line_number_is_rejected(self):
        r = self.apply(ans("ORI-05", ev=[{"path": "AGENTS.md", "line": 10, "snippet": "# Agents"}]))
        self.assertEqual(next(x for x in r["findings"] if x["check_id"] == "ORI-05")["status"], "unknown")

    def test_trivially_short_quote_is_rejected(self):
        # "a" occurs in nearly every line, so it proves nothing.
        r = self.apply(ans("ORI-05", ev=[{"path": "AGENTS.md", "line": 5, "snippet": "a"}]))
        self.assertEqual(next(x for x in r["findings"] if x["check_id"] == "ORI-05")["status"], "unknown")

    def test_partial_evidence_keeps_good_quote_and_notes_discard(self):
        r = self.apply(
            ans(
                "ORI-05",
                ev=[
                    {"path": "AGENTS.md", "line": 6, "snippet": "`tests/` mirrors it"},
                    {"path": "AGENTS.md", "line": 1, "snippet": "made up"},
                ],
            )
        )
        f = next(x for x in r["findings"] if x["check_id"] == "ORI-05")
        self.assertEqual((f["status"], len(f["evidence"])), ("pass", 1))
        self.assertIn("discarded", f["note"])

    def test_bad_status_unknown_task_duplicates_and_missing_answers(self):
        r = self.apply(
            ans("ORI-05", status="definitely", ev=[{"path": "AGENTS.md", "line": 1, "snippet": "# Agents"}]), ans("NOPE"), ans("ORI-05")
        )
        f = {x["check_id"]: x for x in r["findings"]}
        self.assertEqual(f["ORI-05"]["status"], "unknown")
        self.assertEqual(len(r["rejected"]), 2)
        self.assertEqual(f["ORI-06"]["note"], "no answer provided")  # unanswered tasks stay unknown

    def test_instruction_injection_in_note_cannot_change_status(self):
        r = self.apply(ans("ORI-05", status="fail", note="x" * 1000, ev=[{"path": "AGENTS.md", "line": 1, "snippet": "# Agents"}]))
        f = next(x for x in r["findings"] if x["check_id"] == "ORI-05")
        self.assertLessEqual(len(f["note"]), 330)

    def test_entropy_items_derived_from_doc06_fail(self):
        r = self.apply(
            ans(
                "DOC-06",
                status="fail",
                ev=[{"path": "AGENTS.md", "line": 10, "snippet": "`docs/gone.md`"}],
                note="docs/gone.md does not exist",
            )
        )
        self.assertEqual([(i["check_id"], i["verdict"], i["path"]) for i in r["entropy_items"]], [("ENR-03", "stale", "AGENTS.md")])

    def test_findings_validate_against_schema(self):
        r = self.apply(
            ans("ORI-05", ev=[{"path": "AGENTS.md", "line": 5, "snippet": "holds the library"}]),
            ans("ORI-06", status="fail", ev=[{"path": "AGENTS.md", "line": 3, "snippet": "## Layout"}]),
        )
        v = Draft202012Validator({"$ref": "#/$defs/finding", "$defs": SCHEMA["$defs"]})
        for f in r["findings"]:
            v.validate(f)


if __name__ == "__main__":
    unittest.main()
