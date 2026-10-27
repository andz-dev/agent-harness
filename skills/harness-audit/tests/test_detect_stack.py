"""Tests for scripts/detect_stack.py using synthetic repositories.

Run: python3 -I tests/test_detect_stack.py
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import detect_stack  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402

SCHEMA = json.loads((HERE.parent / "schema" / "report.schema.json").read_text())
STACK_SCHEMA = dict(SCHEMA["properties"]["stack"], **{"$defs": SCHEMA["$defs"]})
STACK_VALIDATOR = Draft202012Validator(STACK_SCHEMA)

PYPROJECT = '[project]\nname = "x"\nversion = "0"\n'
PKG = '{"name": "x", "scripts": {"test": "vitest"}}'


def make(tree: dict) -> Path:
    root = Path(tempfile.mkdtemp(prefix="detect-stack-test-"))
    for rel, content in tree.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return root


def by_path(result, path, eco=None):
    return [c for c in result["stack"]["components"] if c["path"] == path and (eco is None or c["ecosystem"] == eco)]


class DetectStackTests(unittest.TestCase):
    def check_schema(self, result):
        errors = list(STACK_VALIDATOR.iter_errors(result["stack"]))
        self.assertEqual(errors, [], [e.message for e in errors])

    def test_python_only(self):
        root = make({"pyproject.toml": PYPROJECT, "src/a.py": "", "tests/test_a.py": "", "README.md": ""})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["ecosystems"], ["python"])
        comp = r["stack"]["components"]
        self.assertEqual(len(comp), 1)
        self.assertEqual(comp[0]["id"], "root")
        self.assertEqual(comp[0]["detected_by"], ["pyproject.toml"])
        self.assertEqual(comp[0]["tracked_files"], 4)
        self.check_schema(r)

    def test_node_only(self):
        root = make({"package.json": PKG, "src/index.ts": "", "test/a.test.ts": ""})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["ecosystems"], ["node"])
        self.assertEqual(r["stack"]["components"][0]["detected_by"], ["package.json"])
        self.check_schema(r)

    def test_config_only_pyproject_is_not_a_component(self):
        root = make({"pyproject.toml": "[tool.ruff]\nline-length = 100\n", "package.json": PKG, "a.js": ""})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["ecosystems"], ["node"])

    def test_marker_package_json_is_not_a_component(self):
        root = make({"pyproject.toml": PYPROJECT, "a.py": "", "web/package.json": '{"type": "module"}'})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["ecosystems"], ["python"])

    def test_mixed_monorepo_per_component(self):
        root = make(
            {
                "package.json": '{"name": "root", "private": true, "devDependencies": {"prettier": "1"}}',
                "pnpm-workspace.yaml": "packages:\n  - 'packages/*'\n",
                "packages/web/package.json": PKG,
                "packages/web/src/app.svelte": "",
                "packages/web/src/main.ts": "",
                "services/ml/pyproject.toml": PYPROJECT,
                "services/ml/ml/model.py": "",
                "mobile/pubspec.yaml": "name: app\n",
                "mobile/lib/main.dart": "",
            }
        )
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["ecosystems"], ["node", "python"])
        self.assertEqual({c["path"] for c in r["stack"]["components"]}, {".", "packages/web", "services/ml"})
        self.assertEqual(by_path(r, ".")[0]["kind"], "tooling")
        self.assertEqual(by_path(r, "services/ml")[0]["ecosystem"], "python")
        self.assertEqual(by_path(r, "packages/web")[0]["tracked_files"], 3)
        self.assertEqual(r["stack"]["unsupported"], [{"path": "mobile", "language": "dart", "manifest": "pubspec.yaml"}])
        self.check_schema(r)

    def test_ignored_directories(self):
        root = make(
            {
                "package.json": PKG,
                "node_modules/dep/package.json": PKG,
                ".venv/lib/pyproject.toml": PYPROJECT,
                "dist/package.json": PKG,
            }
        )
        r = detect_stack.detect(root)
        self.assertEqual([c["path"] for c in r["stack"]["components"]], ["."])

    def test_sample_manifests_are_ignored_and_reported(self):
        root = make(
            {
                "package.json": PKG,
                "tests/fixtures/app/package.json": PKG,
                "examples/basic/package.json": PKG,
                ".github/actions/x/package.json": PKG,
            }
        )
        r = detect_stack.detect(root)
        self.assertEqual([c["path"] for c in r["stack"]["components"]], ["."])
        self.assertEqual(r["ignored"]["sample_manifest_count"], 3)

    def test_workspace_glob_overrides_sample_directory(self):
        root = make(
            {
                "package.json": '{"name": "r", "workspaces": ["examples/*"]}',
                "examples/a/package.json": PKG,
                "examples/b/package.json": PKG,
            }
        )
        r = detect_stack.detect(root)
        self.assertEqual({c["path"] for c in r["stack"]["components"]}, {".", "examples/a", "examples/b"})

    def test_docs_requirements_is_not_a_component(self):
        root = make({"pyproject.toml": PYPROJECT, "a.py": "", "docs/requirements.txt": "sphinx\n"})
        r = detect_stack.detect(root)
        self.assertEqual([c["path"] for c in r["stack"]["components"]], ["."])

    def test_requirements_only_root(self):
        root = make({"requirements.txt": "flask\n", "app.py": ""})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["components"][0]["detected_by"], ["requirements.txt"])

    def test_same_directory_two_ecosystems(self):
        root = make(
            {
                "pyproject.toml": PYPROJECT,
                "package.json": PKG,
                "a.py": "",
                "b.py": "",
                "c.py": "",
                "x.ts": "",
                "README.md": "",
            }
        )
        r = detect_stack.detect(root)
        ids = {c["id"] for c in r["stack"]["components"]}
        self.assertEqual(ids, {"root-python", "root-node"})
        counts = {c["ecosystem"]: c["tracked_files"] for c in r["stack"]["components"]}
        self.assertEqual(counts["python"] + counts["node"], 7)  # every file counted once
        self.assertEqual(counts["node"], 1 + 0)  # only x.ts; README goes to the dominant ecosystem
        self.check_schema(r)

    def test_fallback_inference_without_manifest(self):
        root = make({f"s{i}.py": "" for i in range(6)})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["components"][0]["detected_by"], ["(inferred from sources)"])
        self.assertTrue(any("inferred" in w for w in r["warnings"]))

    def test_no_supported_ecosystem_exit_code(self):
        root = make({"go.mod": "module x\n", "main.go": ""})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["components"], [])
        self.assertEqual(r["stack"]["unsupported"][0]["language"], "go")
        self.assertEqual(detect_stack.main([str(root), "--compact"]), 3)

    def test_unparsable_manifest_warns_and_continues(self):
        root = make({"package.json": "{not json", "pyproject.toml": PYPROJECT, "a.py": ""})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["ecosystems"], ["python"])
        self.assertTrue(any("package.json" in w for w in r["warnings"]))

    def test_deterministic_output(self):
        root = make({"pyproject.toml": PYPROJECT, "web/package.json": PKG, "web/a.ts": "", "a.py": ""})
        self.assertEqual(json.dumps(detect_stack.detect(root)), json.dumps(detect_stack.detect(root)))

    def test_ids_are_unique_and_match_schema_pattern(self):
        root = make({"a-b/package.json": PKG, "a/b/package.json": PKG, "@x/y/package.json": PKG})
        r = detect_stack.detect(root)
        ids = [c["id"] for c in r["stack"]["components"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.check_schema(r)

    # --- regressions found on real repositories (2026-10-26) ----------------
    def test_module_named_setup_py_is_not_a_manifest(self):
        # open-webui: backend/.../telemetry/setup.py is application code.
        root = make(
            {
                "pyproject.toml": PYPROJECT,
                "app/a.py": "",
                "app/telemetry/setup.py": "from fastapi import FastAPI\n\ndef setup(app: FastAPI):\n    pass\n",
            }
        )
        r = detect_stack.detect(root)
        self.assertEqual([c["path"] for c in r["stack"]["components"]], ["."])

    def test_real_setup_py_is_a_manifest(self):
        root = make({"lib/setup.py": "from setuptools import setup\nsetup(name='x')\n", "lib/a.py": ""})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["components"][0]["detected_by"], ["setup.py"])

    def test_requirements_under_python_project_is_merged(self):
        # open-webui: root pyproject plus backend/requirements.txt is one project.
        root = make(
            {
                "pyproject.toml": PYPROJECT,
                **{f"backend/m{i}.py": "" for i in range(5)},
                "backend/requirements.txt": "fastapi\n",
            }
        )
        r = detect_stack.detect(root)
        self.assertEqual([c["path"] for c in r["stack"]["components"]], ["."])
        self.assertEqual(r["stack"]["components"][0]["tracked_files"], 7)
        self.assertEqual(r["ignored"]["merged_manifests"][0]["path"], "backend")

    def test_requirements_without_ancestor_stays_a_component(self):
        root = make({"package.json": PKG, "svc/requirements.txt": "x\n", **{f"svc/m{i}.py": "" for i in range(4)}})
        r = detect_stack.detect(root)
        self.assertEqual({(c["path"], c["ecosystem"]) for c in r["stack"]["components"]}, {(".", "node"), ("svc", "python")})

    def test_self_referencing_workspace_is_not_tooling(self):
        # paperless-ngx: src-ui/pnpm-workspace.yaml lists only ".".
        root = make({"src-ui/package.json": PKG, "src-ui/pnpm-workspace.yaml": "packages:\n  - '.'\n"})
        r = detect_stack.detect(root)
        self.assertEqual(r["stack"]["components"][0]["kind"], "unknown")

    def test_unsupported_manifests_collapse_to_outermost(self):
        # immich: mobile/android/app/build.gradle sits under mobile/android/build.gradle.
        root = make(
            {
                "package.json": PKG,
                "mobile/android/build.gradle": "",
                "mobile/android/app/build.gradle": "",
                "mobile/pubspec.yaml": "name: a\n",
                "mobile/packages/ui/pubspec.yaml": "name: b\n",
                "native/Cargo.toml": "",
                "native/crates/core/Cargo.toml": "",
            }
        )
        r = detect_stack.detect(root)
        got = {(u["path"], u["language"]) for u in r["stack"]["unsupported"]}
        self.assertEqual(got, {("mobile/android", "java"), ("mobile", "dart"), ("native", "rust")})

    def test_git_mode_uses_tracked_files_only(self):
        import subprocess

        root = make(
            {
                "pyproject.toml": PYPROJECT,
                "src/a.py": "",
                "node_modules/x/package.json": PKG,  # tracked but vendored: must be ignored
                "web/package.json": PKG,
                "web/i.ts": "",
            }
        )
        git = ["git", "-C", str(root), "-c", "user.email=t@example.invalid", "-c", "user.name=t", "-c", "core.hooksPath=/dev/null"]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "init"], check=True)
        (root / "untracked.py").write_text("")
        r = detect_stack.detect(root)
        self.assertEqual(r["ignored"]["total_files"], 4)
        self.assertEqual({c["path"] for c in r["stack"]["components"]}, {".", "web"})

    def test_component_key_order(self):
        root = make({"pyproject.toml": PYPROJECT})
        keys = list(detect_stack.detect(root)["stack"]["components"][0])
        self.assertEqual(keys[0], "id")

    def test_workspace_listed_playground_packages_are_samples(self):
        # Regression (vite): playground/* packages are listed in the pnpm workspace but are fixtures.
        root = make(
            {
                "package.json": '{"name":"r","private":true}',
                "pnpm-workspace.yaml": "packages:\n  - packages/*\n  - playground/*\n",
                "packages/core/package.json": '{"name":"core"}',
                "playground/css/package.json": '{"name":"css"}',
                "packages/core/src/__tests__/package.json": '{"name":"t"}',
                "packages/create-app/template-react/package.json": '{"name":"tpl"}',
                "packages/create-app-template-vue/package.json": '{"name":"tpl2"}',
            }
        )
        comps = {c["path"]: c["kind"] for c in detect_stack.detect(root)["stack"]["components"]}
        self.assertEqual(comps["playground/css"], "sample")
        self.assertEqual(comps["packages/core/src/__tests__"], "sample")
        self.assertEqual(comps["packages/create-app/template-react"], "sample")
        self.assertEqual(comps["packages/create-app-template-vue"], "sample")
        self.assertNotEqual(comps["packages/core"], "sample")

    def test_missing_directory(self):
        self.assertEqual(detect_stack.main(["/nonexistent/path"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
