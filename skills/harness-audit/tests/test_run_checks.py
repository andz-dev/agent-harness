"""Tests for scripts/run_checks.py using synthetic repositories.

Run: python3 -I tests/test_run_checks.py
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import run_checks  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

REAL_CATALOG = yaml.safe_load((HERE.parent / "checks" / "catalog.yaml").read_text())
SCHEMA = json.loads((HERE.parent / "schema" / "report.schema.json").read_text())
FINDING = Draft202012Validator(dict(SCHEMA["$defs"]["finding"], **{"$defs": SCHEMA["$defs"]}))

PYPROJECT = '[project]\nname = "x"\nversion = "0"\n'
PKG = '{"name": "x", "scripts": {"test": "vitest", "lint": "eslint ."}}'


def make(tree: dict) -> Path:
    root = Path(tempfile.mkdtemp(prefix="run-checks-test-"))
    for rel, content in tree.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return root


def check(detector, params, applies_to=("all",), cid="TST-01", pillar="verification", level=1, gate=False):
    return {
        "id": cid,
        "pillar": pillar,
        "level": level,
        "gate": gate,
        "applies_to": list(applies_to),
        "title": "t",
        "detector": detector,
        "params": params,
        "evidence": "e",
        "rationale": "r",
    }


def run_one(tree, *checks):
    root = make(tree)
    catalog = {"catalog_version": "test", "sets": REAL_CATALOG["sets"], "checks": list(checks)}
    return run_checks.run(root, catalog)["findings"]


class Sta09MechanicalTests(unittest.TestCase):
    """B-128: STA-09 is mechanical. Linters that print rule ids count; formatters do not."""

    def status(self, tree):
        sta09 = next(c for c in REAL_CATALOG["checks"] if c["id"] == "STA-09")
        return run_one(tree, sta09)[0]["status"]

    def test_ruff_and_oxlint_pass(self):
        self.assertEqual(self.status({"pyproject.toml": PYPROJECT + "[tool.ruff]\nline-length = 100\n"}), "pass")
        self.assertEqual(self.status({"package.json": "{}", "oxlint.config.ts": "export default {}\n"}), "pass")

    def test_formatter_only_fails(self):
        self.assertEqual(self.status({"pyproject.toml": PYPROJECT + "[tool.black]\nline-length = 100\n"}), "fail")
        self.assertEqual(self.status({"package.json": "{}", ".prettierrc": "{}"}), "fail")


class DjangoRegressionTests(unittest.TestCase):
    """Holdout (B-139): unittest-based repos with tests/runtests.py have a configured test framework."""

    def test_runtests_script_counts_as_python_test_framework(self):
        ver03 = next(c for c in REAL_CATALOG["checks"] if c["id"] == "VER-03")
        tree = {"pyproject.toml": PYPROJECT, "tests/runtests.py": "import unittest\n"}
        findings = run_one(tree, ver03)
        self.assertEqual([f["status"] for f in findings if f["check_id"] == "VER-03"], ["pass"])


class PlaceholderTests(unittest.TestCase):
    """Bootstrap stubs (B-150): a file with TODO(human) placeholders does not earn a pass."""

    def test_pass_on_file_with_placeholder_becomes_fail(self):
        chk = check("file_exists", {"globs": ["AGENTS.md"]}, cid="TST-02", pillar="orientation")
        done = run_one({"pyproject.toml": PYPROJECT, "AGENTS.md": "# a\nTODO(human): fill\n"}, chk)
        f = [x for x in done if x["check_id"] == "TST-02"][0]
        self.assertEqual(f["status"], "fail")
        self.assertIn("TODO(human)", f["note"])
        self.assertEqual(f["evidence"][-1]["kind"], "searched")

    def test_finished_file_still_passes(self):
        chk = check("file_exists", {"globs": ["AGENTS.md"]}, cid="TST-02", pillar="orientation")
        done = run_one({"pyproject.toml": PYPROJECT, "AGENTS.md": "# a\nreal rules\n"}, chk)
        self.assertEqual([x["status"] for x in done if x["check_id"] == "TST-02"], ["pass"])


class GlobTests(unittest.TestCase):
    def test_brace_expansion(self):
        self.assertEqual(sorted(run_checks.expand_braces("a.{js,ts}")), ["a.js", "a.ts"])

    def test_double_star_matches_any_depth_including_zero(self):
        rx = run_checks.glob_to_regex("tests/**/*.py")
        self.assertTrue(rx.match("tests/a.py"))
        self.assertTrue(rx.match("tests/x/y/a.py"))
        self.assertFalse(rx.match("src/a.py"))

    def test_pattern_without_slash_is_anchored_at_base(self):
        rx = run_checks.glob_to_regex("README*")
        self.assertTrue(rx.match("README.md"))
        self.assertFalse(rx.match("docs/README.md"))


class SampleOwnershipTests(unittest.TestCase):
    def test_files_of_sample_packages_belong_to_the_enclosing_component(self):
        # Regression (vite): tests under a nested __tests__/package.json must count for the package.
        tree = {
            "package.json": '{"name":"core","scripts":{"test":"vitest"}}',
            "src/index.js": "",
            "src/__tests__/package.json": '{"name":"t"}',
            "src/__tests__/a.spec.js": "",
            "src/__tests__/b.spec.js": "",
            "src/__tests__/c.spec.js": "",
        }
        f = run_one(tree, check("glob_count", {"globs": ["**/*.spec.js"], "min": 3}, applies_to=("node",), cid="T-1"))
        self.assertEqual([x["status"] for x in f], ["pass"])


class WorkspaceInheritanceTests(unittest.TestCase):
    TREE = {
        "package.json": '{"name":"r","private":true,"scripts":{"test":"vitest"}}',
        "pnpm-workspace.yaml": "packages:\n  - packages/*\n  - playground/*\n",
        "vitest.config.ts": "export default {}\n",
        "packages/core/package.json": '{"name":"core"}',
        "packages/core/index.js": "",
        "playground/a/package.json": '{"name":"a","devDependencies":{"c8":"1"}}',
        "playground/a/vitest.config.ts": "x",
    }

    def test_component_inherits_workspace_root_config(self):
        # Regression (vite): vitest config and test script live in the workspace root.
        f = run_one(self.TREE, check("file_exists", {"globs": ["vitest.config.*"]}, applies_to=("node",), cid="T-1"))
        self.assertEqual([(x["component"], x["status"]) for x in f], [("packages-core", "pass")])
        self.assertEqual(f[0]["evidence"][0]["path"], "vitest.config.ts")

    def test_top_level_samples_are_not_searched(self):
        # Regression (vite): a c8 dependency in a playground package must not satisfy a repo-wide coverage check.
        f = run_one(self.TREE, check("text_match", {"files": ["**/package.json"], "pattern": "c8"}, cid="T-1"))
        self.assertEqual(f[0]["status"], "fail")


class PackageJsonHookTests(unittest.TestCase):
    def test_simple_git_hooks_and_lint_staged_in_package_json(self):
        # Regression (vite): hooks configured via package.json keys were invisible.
        pkg = (
            '{"name":"x","simple-git-hooks":{"pre-commit":"pnpm exec lint-staged --concurrent false"},'
            '"lint-staged":{"*.js":["oxlint --fix","oxfmt"]}}'
        )
        f = run_one(
            {"package.json": pkg, "index.js": ""},
            check("hook_runs", {"pattern": "."}, cid="T-1"),
            check("hook_runs", {"pattern": "oxfmt", "stages": ["pre-commit"]}, cid="T-2"),
            check("hook_runs", {"pattern": "eslint"}, cid="T-3"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "pass", "fail"])

    def test_standalone_hook_config_files(self):
        f = run_one(
            {"package.json": '{"name":"x"}', "index.js": "", ".simple-git-hooks.json": '{"pre-commit": "npx lint-staged"}'},
            check("hook_runs", {"pattern": "lint-staged"}, cid="T-1"),
        )
        self.assertEqual(f[0]["status"], "pass")

    def test_plain_package_json_has_no_hooks(self):
        f = run_one(
            {"package.json": '{"name":"x","devDependencies":{"lint-staged":"1"}}', "index.js": ""},
            check("hook_runs", {"pattern": "."}, cid="T-1"),
        )
        self.assertEqual(f[0]["status"], "fail")


class DetectorTests(unittest.TestCase):
    def test_file_exists_pass_and_fail_evidence_kinds(self):
        f = run_one(
            {"pyproject.toml": PYPROJECT, "a.py": "", "AGENTS.md": "x"},
            check("file_exists", {"globs": ["AGENTS.md"]}, cid="T-1"),
            check("file_exists", {"globs": ["CLAUDE.md"]}, cid="T-2"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "fail"])
        self.assertEqual(f[0]["evidence"][0]["kind"], "found")
        self.assertEqual(f[1]["evidence"][0]["kind"], "searched")

    def test_glob_count_threshold_and_only_if(self):
        tree = {"pyproject.toml": PYPROJECT, "a.py": "", "tests/test_a.py": "", "tests/test_b.py": ""}
        f = run_one(
            tree,
            check("glob_count", {"globs": ["tests/**/*.py"], "min": 2}, cid="T-1"),
            check("glob_count", {"globs": ["tests/**/*.py"], "min": 3}, cid="T-2"),
            check("glob_count", {"globs": ["**/AGENTS.md"], "min": 2, "only_if": "repo has more than one component"}, cid="T-3"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "fail", "not_applicable"])

    def test_key_present_toml_json_ini(self):
        tree = {
            "pyproject.toml": PYPROJECT + "[tool.ruff]\nline-length = 100\n",
            "package.json": PKG,
            "setup.cfg": "[flake8]\nmax-line-length = 100\n",
            "a.py": "",
        }
        f = run_one(
            tree,
            check("key_present", {"any_of": [{"file": "pyproject.toml", "path": "tool.ruff"}]}, cid="T-1"),
            check("key_present", {"any_of": [{"file": "package.json", "path": "scripts.test"}]}, cid="T-2"),
            check("key_present", {"any_of": [{"file": "setup.cfg", "path": "flake8"}]}, cid="T-3"),
            check("key_present", {"any_of": [{"file": "pyproject.toml", "path": "tool.black"}]}, cid="T-4"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "pass", "pass", "fail"])
        self.assertEqual(f[0]["evidence"][0]["line"], 4)

    def test_text_match_min_distinct(self):
        tree = {"pyproject.toml": PYPROJECT, "AGENTS.md": "Run `make test`.\nAlso `make test` again.\n"}
        pat = r"`[^`]*\b(test|lint)\b[^`]*`"
        f = run_one(
            tree,
            check("text_match", {"files": ["AGENTS.md"], "pattern": pat}, cid="T-1"),
            check("text_match", {"files": ["AGENTS.md"], "pattern": pat, "min_distinct_commands": 2}, cid="T-2"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "fail"])

    def test_ci_direct_match_and_github_on_key(self):
        wf = "on:\n  pull_request:\n  push:\njobs:\n  t:\n    steps:\n      - run: pytest -q\n      - uses: actions/checkout@v4\n"
        tree = {"pyproject.toml": PYPROJECT, "a.py": "", ".github/workflows/ci.yml": wf}
        f = run_one(
            tree,
            check("ci_runs", {"pattern": "pytest"}, cid="T-1"),
            check("ci_runs", {"trigger": ["pull_request"]}, cid="T-2"),
            check("ci_runs", {"trigger_all": ["pull_request", "push"]}, cid="T-3"),
            check("ci_runs", {"trigger_all": ["pull_request", "schedule"]}, cid="T-4"),
            check("ci_runs", {"all_of": ["pytest", "ruff"]}, cid="T-5"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "pass", "pass", "fail", "fail"])
        self.assertEqual(f[0]["evidence"][0]["line"], 7)

    def test_ci_share_of_run_steps(self):
        wf = "on: push\njobs:\n  t:\n    steps:\n      - run: make check\n      - run: ./custom.sh\n      - run: npm ci\n"
        tree = {"pyproject.toml": PYPROJECT, "a.py": "", "Makefile": "check:\n\tpytest\n", ".github/workflows/ci.yml": wf}
        f = run_one(
            tree,
            check("ci_runs", {"pattern": r"make ", "min_share_of_run_steps": 0.5}, cid="T-1"),
            check("ci_runs", {"pattern": r"make ", "min_share_of_run_steps": 0.9}, cid="T-2"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "fail"])

    def test_ci_install_step_is_not_a_tool_run(self):
        # Regression (open-webui): "pip install ruff" must not count as running ruff.
        wf = "on: push\njobs:\n  t:\n    steps:\n      - run: pip install ruff\n"
        tree = {"pyproject.toml": PYPROJECT, "a.py": "", ".github/workflows/ci.yml": wf}
        f = run_one(
            tree, check("ci_runs", {"pattern": "ruff"}, cid="T-1"), check("ci_runs", {"pattern": "ruff", "include_setup": True}, cid="T-2")
        )
        self.assertEqual([x["status"] for x in f], ["fail", "pass"])

    def test_hook_text_excludes_repo_url(self):
        # Regression (paperless): "pre-commit/pre-commit-hooks" URL must not match tool patterns.
        hooks = "repos:\n  - repo: https://github.com/tox-dev/foo\n    rev: v1\n    hooks:\n      - id: trailing-whitespace\n"
        tree = {"pyproject.toml": PYPROJECT, "a.py": "", ".pre-commit-config.yaml": hooks}
        f = run_one(tree, check("hook_runs", {"pattern": "tox"}, cid="T-1"))
        self.assertEqual(f[0]["status"], "fail")

    def test_only_if_typescript_not_applicable_for_plain_js(self):
        pkg = '{"name":"x","scripts":{"test":"mocha"}}'
        c = check("ci_runs", {"pattern": "tsc", "only_if": "component has TypeScript"}, applies_to=("node",), cid="T-1")
        f = run_one({"package.json": pkg, "index.js": ""}, c)
        self.assertEqual(f[0]["status"], "not_applicable")
        f = run_one({"package.json": pkg, "index.ts": ""}, c)
        self.assertNotEqual(f[0]["status"], "not_applicable")

    def test_ci_indirect_via_runner_uses_commands_not_dependency_lists(self):
        # Regression (flask): "mypy" in a dependency list must not count as an invocation.
        wf = "on: push\njobs:\n  t:\n    steps:\n      - run: tox run\n"
        pyproject = PYPROJECT + '[dependency-groups]\ntyping = [\n    "mypy",\n]\n[tool.tox.env.typing]\ncommands = [\n    ["pytest"],\n]\n'
        tree = {"pyproject.toml": pyproject, "a.py": "", ".github/workflows/ci.yml": wf}
        f = run_one(tree, check("ci_runs", {"pattern": "mypy"}, cid="T-1"), check("ci_runs", {"pattern": "pytest"}, cid="T-2"))
        self.assertEqual([x["status"] for x in f], ["fail", "pass"])
        self.assertIn("indirect", f[1]["note"])

    def test_ci_indirect_package_json_scripts_only(self):
        wf = "on: push\njobs:\n  t:\n    steps:\n      - run: npm run lint\n"
        pkg = '{"name": "x", "scripts": {"lint": "eslint ."}, "devDependencies": {"vitest": "1"}}'
        tree = {"package.json": pkg, "a.js": "", ".github/workflows/ci.yml": wf}
        f = run_one(tree, check("ci_runs", {"pattern": "eslint"}, cid="T-1"), check("ci_runs", {"pattern": "vitest"}, cid="T-2"))
        self.assertEqual([x["status"] for x in f], ["pass", "fail"])

    def test_ci_missing(self):
        f = run_one({"pyproject.toml": PYPROJECT, "a.py": ""}, check("ci_runs", {"pattern": "pytest"}))
        self.assertEqual(f[0]["status"], "fail")
        self.assertEqual(f[0]["evidence"][0]["kind"], "searched")

    def test_hook_runs_precommit_husky_lefthook_agent(self):
        precommit = "repos:\n  - repo: https://example.invalid/ruff\n    hooks:\n      - id: ruff-check\n"
        tree = {
            "pyproject.toml": PYPROJECT,
            "a.py": "",
            ".pre-commit-config.yaml": precommit,
            ".husky/pre-push": "#!/bin/sh\nnpm test\n",
            ".claude/settings.json": json.dumps({"hooks": {"PostToolUse": [{"hooks": [{"type": "command", "command": "task lint"}]}]}}),
        }
        f = run_one(
            tree,
            check("hook_runs", {"pattern": "ruff"}, cid="T-1"),
            check("hook_runs", {"pattern": r"npm test", "stages": ["pre-push"]}, cid="T-2"),
            check("hook_runs", {"pattern": r"npm test", "stages": ["pre-commit"]}, cid="T-3"),
            check("hook_runs", {"pattern": r"task lint"}, cid="T-4"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "pass", "fail", "pass"])
        self.assertIn("agent:PostToolUse", f[3]["evidence"][0]["snippet"])

    def test_precommit_check_hook_id_is_not_a_test_hook(self):
        # Regression (flask): 'ruff-check' must not satisfy a "runs tests" pattern.
        precommit = "repos:\n  - repo: https://example.invalid/ruff\n    hooks:\n      - id: ruff-check\n"
        f = run_one(
            {"pyproject.toml": PYPROJECT, "a.py": "", ".pre-commit-config.yaml": precommit},
            check(
                "hook_runs",
                {"pattern": REAL_CATALOG["checks"][[c["id"] for c in REAL_CATALOG["checks"]].index("TRG-03")]["params"]["pattern"]},
            ),
        )
        self.assertEqual(f[0]["status"], "fail")

    def test_runner_targets(self):
        tree = {
            "pyproject.toml": PYPROJECT + '[tool.tox]\nenv_list = ["tests", "style"]\n',
            "a.py": "",
            "Makefile": ".PHONY: lint\nlint:\n\truff .\ncheck: lint\n\tpytest\n",
        }
        f = run_one(
            tree,
            check("runner_target", {"any_target": True}, cid="T-1"),
            check("runner_target", {"all_of": ["test", "lint"], "any_of": ["check", "ci"]}, cid="T-2"),
            check("runner_target", {"all_of": ["deploy"]}, cid="T-3"),
        )
        self.assertEqual([x["status"] for x in f], ["pass", "pass", "fail"])

    def test_runner_target_prefix_and_plural(self):
        tree = {"package.json": '{"name": "x", "scripts": {"test:unit": "vitest", "lint:fix": "eslint --fix"}}', "a.js": ""}
        f = run_one(tree, check("runner_target", {"all_of": ["test", "lint"]}))
        self.assertEqual(f[0]["status"], "pass")

    def test_package_json_without_scripts_has_no_targets(self):
        f = run_one({"package.json": '{"name": "x"}', "a.js": ""}, check("runner_target", {"any_target": True}))
        self.assertEqual(f[0]["status"], "fail")


class OrchestrationTests(unittest.TestCase):
    def test_per_component_findings_and_tooling_root_skipped(self):
        tree = {
            "package.json": '{"name": "root", "private": true, "workspaces": ["web"]}',
            "web/package.json": PKG,
            "web/src/a.test.ts": "",
            "web/src/b.test.ts": "",
            "web/src/c.test.ts": "",
            "svc/pyproject.toml": PYPROJECT,
            "svc/tests/test_a.py": "",
            "svc/tests/test_b.py": "",
            "svc/tests/test_c.py": "",
        }
        f = run_one(
            tree,
            check("glob_count", {"globs": ["**/*.test.ts"], "min": 3}, applies_to=["node"], cid="T-1"),
            check("glob_count", {"globs": ["tests/**/*.py"], "min": 3}, applies_to=["python"], cid="T-2"),
        )
        self.assertEqual({(x["check_id"], x.get("component"), x["status"]) for x in f}, {("T-1", "web", "pass"), ("T-2", "svc", "pass")})

    def test_component_files_are_scoped_to_their_owner(self):
        tree = {
            "web/package.json": PKG,
            "web/a.test.ts": "",
            "other/package.json": PKG,
            "other/x.test.ts": "",
            "other/y.test.ts": "",
            "other/z.test.ts": "",
        }
        f = run_one(tree, check("glob_count", {"globs": ["**/*.test.ts"], "min": 2}, applies_to=["node"]))
        by_comp = {x["component"]: x["status"] for x in f}
        self.assertEqual(by_comp, {"web": "fail", "other": "pass"})

    def test_not_applicable_when_ecosystem_absent(self):
        f = run_one({"package.json": PKG, "a.js": ""}, check("file_exists", {"globs": ["x"]}, applies_to=["python"]))
        self.assertEqual(f[0]["status"], "not_applicable")
        self.assertNotIn("component", f[0])

    def test_deferred_detectors_are_unknown(self):
        f = run_one(
            {"package.json": PKG, "a.js": ""}, check("llm", {"prompt": "p"}, cid="T-1"), check("git_signal", {"rule": "r"}, cid="T-2")
        )
        self.assertEqual([x["status"] for x in f], ["unknown", "unknown"])
        self.assertEqual(f[0]["source"], "llm")
        self.assertEqual(f[0]["confidence"], "low")
        self.assertEqual(f[1]["source"], "script")

    def test_broken_detector_becomes_error_finding(self):
        f = run_one({"package.json": PKG, "a.js": ""}, check("text_match", {"files": ["package.json"], "pattern": "("}))
        self.assertEqual(f[0]["status"], "error")
        self.assertIn("error", f[0]["note"].lower())

    def test_every_finding_validates_against_schema(self):
        tree = {
            "pyproject.toml": PYPROJECT,
            "a.py": "",
            "tests/test_a.py": "",
            "README.md": "## Usage\n",
            ".github/workflows/ci.yml": "on: push\njobs:\n  t:\n    steps:\n      - run: pytest\n",
        }
        root = make(tree)
        result = run_checks.run(root, REAL_CATALOG)
        self.assertGreater(len(result["findings"]), 50)
        for f in result["findings"]:
            errs = [e.message for e in FINDING.iter_errors(f)]
            self.assertEqual(errs, [], (f["check_id"], errs))

    def test_real_catalog_runs_on_empty_ish_repo_without_errors(self):
        root = make({"pyproject.toml": PYPROJECT, "a.py": ""})
        result = run_checks.run(root, REAL_CATALOG)
        self.assertEqual(result["meta"]["by_status"].get("error", 0), 0)

    def test_deterministic(self):
        root = make({"pyproject.toml": PYPROJECT, "a.py": "", "README.md": "## Usage\n"})
        a = json.dumps(run_checks.run(root, REAL_CATALOG))
        b = json.dumps(run_checks.run(root, REAL_CATALOG))
        self.assertEqual(a, b)

    def test_only_filter(self):
        root = make({"pyproject.toml": PYPROJECT, "a.py": ""})
        result = run_checks.run(root, REAL_CATALOG, only={"ORI-01"})
        self.assertEqual([f["check_id"] for f in result["findings"]], ["ORI-01"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
