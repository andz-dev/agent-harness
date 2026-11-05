import builtins
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from shutil import copytree
from unittest.mock import patch

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
LEGACY_CORE_BASELINE = {
    "pillars": [
        {"pillar": "verification", "level": 2, "weight": 25, "points": 16.67, "gate_failures": []},
        {"pillar": "orientation", "level": 0, "weight": 20, "points": 0.0, "gate_failures": []},
        {"pillar": "static_guardrails", "level": 0, "weight": 15, "points": 0.0, "gate_failures": ["STA-01"]},
        {"pillar": "workflow_entry_points", "level": 0, "weight": 15, "points": 0.0, "gate_failures": ["ENT-01"]},
        {"pillar": "automatic_triggers", "level": 0, "weight": 10, "points": 0.0, "gate_failures": ["TRG-01"]},
        {"pillar": "pipeline_parity", "level": 1, "weight": 10, "points": 3.33, "gate_failures": ["CIP-02"]},
        {"pillar": "doc_hygiene", "level": 0, "weight": 5, "points": 0.0, "gate_failures": []},
    ],
    "score": {"raw": 20.0, "entropy_penalty": 1.0, "final": 19, "caps_applied": []},
    "entropy": {
        "candidate_files": 3,
        "flagged_files": 1,
        "history_available": False,
        "items": [
            {
                "check_id": "ENR-01",
                "path": "scripts/lonely.sh",
                "verdict": "orphaned",
                "evidence": [
                    {
                        "kind": "searched",
                        "path": "runner/CI/hook files, manifests, docs, other scripts",
                        "snippet": "no file references lonely.sh",
                    }
                ],
            }
        ],
        "penalty": 1.0,
    },
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

    def test_infra_files_never_change_the_score(self):
        """D1: infrastructure is an unscored overlay; adding infra files leaves the 0-100 score unchanged."""
        _, plain = self.run_audit(FILES)
        r, with_infra = self.run_audit(
            {**FILES, "Dockerfile": "FROM python:3.12\n", "infra/main.tf": "", ".devcontainer/devcontainer.json": "{}"}
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        a = json.loads((plain / "report.json").read_text())
        b = json.loads((with_infra / "report.json").read_text())
        self.assertEqual(a["score"], b["score"])
        self.assertEqual([p["level"] for p in a["pillars"]], [p["level"] for p in b["pillars"]])
        self.assertEqual(audit.validate(b), [])
        self.assertEqual(b["infra"]["tools"], ["devcontainer", "docker", "terraform"])
        self.assertTrue(any("not part of the score" in x for x in b["limitations"]))
        self.assertIn("## Infrastructure (detected, not scored)", (with_infra / "report.md").read_text())

    def test_assembler_validates_the_shipped_coverage_catalog(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "target"
            repo_root.mkdir()
            for relative_path, text in FILES.items():
                path = repo_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            catalog = audit.yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text(encoding="utf-8"))
            validator = audit.coverage.validate_topic_catalog

            with patch.object(audit.coverage, "validate_topic_catalog", wraps=validator) as validate_topics:
                report = audit.assemble(repo_root, catalog)

        self.assertEqual(audit.validate(report), [])
        validate_topics.assert_called_once()

    def test_report_collects_catalog_observations_from_tracked_files_only(self):
        fixture = Path(__file__).parent / "fixtures" / "coverage" / "PY-01"
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "repo"
            copytree(fixture, repo_root)
            subprocess.run(["git", "init", "--quiet"], cwd=repo_root, check=True)
            subprocess.run(["git", "-C", str(repo_root), "add", "--", "."], check=True)
            (repo_root / "private.env").write_text("UNTRACKED_SENTINEL", encoding="utf-8")
            taskfile_digest = hashlib.sha256((repo_root / "Taskfile.yml").read_bytes()).hexdigest()
            catalog = audit.yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text(encoding="utf-8"))

            report = audit.assemble(repo_root, catalog)
        observations = {observation["topic_id"]: observation for observation in report["coverage"]["observations"]}
        self.assertIn("ci_build", observations)
        observation = observations["ci_build"]
        self.assertEqual(observation["evidence"], "declared")
        self.assertEqual(observation["applicability"], "applicable")
        self.assertEqual(observation["freshness"], "unknown")
        self.assertEqual(observation["receipt"], {"outcome": "absent"})
        self.assertEqual(
            observation["provenance"]["sources"],
            [
                {
                    "path": "Taskfile.yml",
                    "sha256": taskfile_digest,
                    "locator": "file",
                }
            ],
        )
        self.assertNotIn("UNTRACKED_SENTINEL", json.dumps(report))

    def test_legacy_core_baseline_is_pinned(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "target"
            repo_root.mkdir()
            for relative_path, text in FILES.items():
                path = repo_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            catalog = audit.yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text(encoding="utf-8"))
            report = audit.assemble(repo_root, catalog)

        legacy_report = {key: value for key, value in report.items() if key not in ("coverage", "quality")}
        self.assertEqual(audit.validate(legacy_report), [])
        core = {
            "pillars": [
                {key: pillar[key] for key in ("pillar", "level", "weight", "points", "gate_failures")}
                for pillar in legacy_report["pillars"]
            ],
            "score": legacy_report["score"],
            "entropy": legacy_report["entropy"],
        }
        self.assertEqual(core, LEGACY_CORE_BASELINE)

    def test_supported_report_adds_coverage_quality_without_changing_core(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "target"
            repo_root.mkdir()
            for relative_path, text in FILES.items():
                path = repo_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            catalog = audit.yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text(encoding="utf-8"))
            report = audit.assemble(repo_root, catalog)

        self.assertEqual(audit.validate(report), [])
        self.assertEqual(
            report["quality"],
            {"availability": "available", "score": LEGACY_CORE_BASELINE["score"]["final"], "reason_codes": []},
        )
        self.assertEqual(
            {key: report[key] for key in ("pillars", "score", "entropy")},
            LEGACY_CORE_BASELINE,
        )
        self.assertEqual(report["coverage"]["version"], 1)
        self.assertTrue(report["coverage"]["observations"])
        self.assertTrue({observation["evidence"] for observation in report["coverage"]["observations"]} <= {"declared", "unknown"})
        self.assertEqual(report["coverage"]["runner_edges"], [])
        self.assertEqual(report["coverage"]["limitations"], [])
        self.assertEqual(report["coverage"]["collection"]["outcome"], "complete")
        self.assertEqual(report["coverage"]["collection"]["reason_codes"], [])
        self.assertEqual(
            report["coverage"]["components"],
            [
                {
                    "id": component["id"],
                    "root": component["path"],
                    "languages": [component["ecosystem"]],
                    "adapter": component["ecosystem"],
                    "applicability": "applicable",
                }
                for component in report["stack"]["components"]
            ],
        )

    def test_unsupported_only_report_has_null_quality_and_no_fabricated_core(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "target"
            repo_root.mkdir()
            (repo_root / "Cargo.toml").write_text("[package]\nname = 'fixture'\nversion = '0.1.0'\n", encoding="utf-8")
            catalog = audit.yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text(encoding="utf-8"))

            report = audit.assemble(repo_root, catalog)

        self.assertEqual(audit.validate(report), [])
        self.assertEqual(report["quality"], {"availability": "unavailable", "score": None, "reason_codes": ["no_applicable_core"]})
        self.assertNotIn("pillars", report)
        self.assertNotIn("score", report)
        self.assertNotIn("entropy", report)
        self.assertEqual(
            report["coverage"]["components"],
            [
                {
                    "id": "root-rust",
                    "root": ".",
                    "languages": ["rust"],
                    "adapter": None,
                    "applicability": "unsupported",
                }
            ],
        )
        observations = report["coverage"]["observations"]
        self.assertEqual(len(observations), len(audit.coverage.TOPIC_IDS))
        self.assertEqual({item["topic_id"] for item in observations}, set(audit.coverage.TOPIC_IDS))
        self.assertTrue(all(item["applicability"] == "unsupported" for item in observations))
        self.assertTrue(all(item["evidence"] == "unknown" for item in observations))

    def test_infrastructure_only_report_is_unavailable_without_zero_score(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "target"
            repo_root.mkdir()
            (repo_root / "Dockerfile").write_text("FROM python:3.14\n", encoding="utf-8")
            (repo_root / "compose.yaml").write_text("services: {}\n", encoding="utf-8")
            catalog = audit.yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text(encoding="utf-8"))

            report = audit.assemble(repo_root, catalog)

        self.assertEqual(audit.validate(report), [])
        self.assertEqual(report["quality"]["availability"], "unavailable")
        self.assertIsNone(report["quality"]["score"])
        self.assertEqual(report["coverage"]["components"], [])
        self.assertEqual(report["coverage"]["observations"], [])
        self.assertEqual(report["stack"]["components"], [])
        self.assertEqual(report["stack"]["ecosystems"], [])
        self.assertTrue(report["infra"]["detected"])

    def test_mixed_report_marks_only_unsupported_language_without_score_change(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "target"
            (repo_root / "api").mkdir(parents=True)
            (repo_root / "web").mkdir()
            (repo_root / "native").mkdir()
            (repo_root / "api" / "pyproject.toml").write_text("[project]\nname='api'\nversion='1'\n", encoding="utf-8")
            (repo_root / "web" / "package.json").write_text('{"name":"web"}\n', encoding="utf-8")
            (repo_root / "native" / "Cargo.toml").write_text("[package]\nname='native'\nversion='0.1.0'\n", encoding="utf-8")
            catalog = audit.yaml.safe_load((ROOT / "checks" / "catalog.yaml").read_text(encoding="utf-8"))

            report = audit.assemble(repo_root, catalog)

        self.assertEqual(audit.validate(report), [])
        self.assertEqual(report["quality"]["availability"], "available")
        self.assertEqual(report["quality"]["score"], report["score"]["final"])
        by_language = {component["languages"][0]: component for component in report["coverage"]["components"]}
        self.assertEqual(set(by_language), {"python", "node", "rust"})
        self.assertEqual(by_language["python"]["applicability"], "applicable")
        self.assertEqual(by_language["node"]["applicability"], "applicable")
        self.assertEqual(by_language["rust"]["applicability"], "unsupported")
        self.assertIsNone(by_language["rust"]["adapter"])

        observations = report["coverage"]["observations"]
        topic_ids = {"code_standards", "testing", "ci_build", "security", "dependencies", "mcp", "skills_extensions"}
        self.assertEqual(len(observations), len(report["coverage"]["components"]) * len(topic_ids))
        for component in report["coverage"]["components"]:
            component_observations = [item for item in observations if item["component_id"] == component["id"]]
            self.assertEqual({item["topic_id"] for item in component_observations}, topic_ids)
            if component["adapter"] is None:
                self.assertTrue(all(item["applicability"] == "unsupported" for item in component_observations))
                self.assertTrue(all(item["evidence"] == "unknown" for item in component_observations))
        missing_pair = json.loads(json.dumps(report))
        missing_pair["coverage"]["observations"].pop()
        self.assertTrue(any("exactly one state" in error for error in audit.validate(missing_pair)))
        duplicate_pair = json.loads(json.dumps(report))
        duplicate_pair["coverage"]["observations"].append(duplicate_pair["coverage"]["observations"][0])
        self.assertTrue(any("exactly one state" in error for error in audit.validate(duplicate_pair)))
        unsupported_claim = json.loads(json.dumps(report))
        unsupported_claim["coverage"]["observations"][0]["evidence"] = "execution_observed"
        self.assertTrue(any("execution_observed" in error for error in audit.validate(unsupported_claim)))

    def test_infra_judgement_answers_reach_the_report_without_touching_the_score(self):
        agents = "# Agents\n\nRun `pytest` before committing.\nNever run `terraform apply`.\n"
        files = {**FILES, "AGENTS.md": agents, "infra/main.tf": ""}
        repo, out = make(files), Path(tempfile.mkdtemp())
        script = str(ROOT / "scripts" / "audit.py")
        r = subprocess.run([sys.executable, "-I", script, str(repo), "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        tasks = json.loads((out / "llm_tasks.json").read_text())
        self.assertIn("INF-J01", [t["task_id"] for t in tasks["tasks"]])
        before = json.loads((out / "report.json").read_text())
        quote = {"path": "AGENTS.md", "line": 4, "snippet": "Never run `terraform apply`."}
        answers = out / "answers.json"
        answers.write_text(
            json.dumps([{"task_id": "INF-J01", "status": "pass", "confidence": "high", "evidence": [quote], "note": "forbids apply"}])
        )
        r2 = subprocess.run(
            [sys.executable, "-I", script, str(repo), "--out", str(out), "--llm-answers", str(answers)], capture_output=True, text=True
        )
        self.assertEqual(r2.returncode, 0, r2.stderr)
        after = json.loads((out / "report.json").read_text())
        self.assertEqual(audit.validate(after), [])
        j = next(c for c in after["infra"]["checks"] if c["check_id"] == "INF-J01")
        self.assertEqual((j["area"], j["status"]), ("agent-guidance", "pass"))
        self.assertIn("agent-guidance", after["infra"]["levels"]["areas"])
        self.assertEqual(before["score"]["final"], after["score"]["final"])

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

    def test_unsupported_only_cli_emits_unavailable_report(self):
        r, out = self.run_audit({"Cargo.toml": "[package]\nname = 'fixture'\nversion = '0.1.0'\n"})
        self.assertEqual(r.returncode, 0, r.stderr)
        report = json.loads((out / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(audit.validate(report), [])
        self.assertEqual(report["quality"]["availability"], "unavailable")
        self.assertIsNone(report["quality"]["score"])
        self.assertNotIn("score", report)
        self.assertIn("unavailable", (out / "report.md").read_text(encoding="utf-8"))

    def test_cli_emits_lifecycle_events_to_stderr_and_keeps_summary_on_stdout(self):
        r, _ = self.run_audit(FILES)

        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Static collection started", r.stderr)
        self.assertIn("Static collection completed", r.stderr)
        self.assertIn("Report conversion started", r.stderr)
        self.assertIn("Report conversion completed", r.stderr)
        self.assertFalse(r.stdout.lstrip().startswith("{"))
        self.assertIn("/100 ->", r.stdout)

    def test_conversion_rejection_does_not_emit_raw_validation_details(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "target"
            repo_root.mkdir()
            for relative_path, text in FILES.items():
                path = repo_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            output_path = Path(temporary_directory) / "report"
            stdout = StringIO()
            stderr = StringIO()
            with patch("audit.validate", return_value=["PRIVATE_DIAGNOSTIC_SENTINEL"]):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    exit_code = audit.main([str(repo_root), "--out", str(output_path)])

        self.assertEqual(exit_code, 4)
        self.assertNotIn("PRIVATE_DIAGNOSTIC_SENTINEL", stderr.getvalue())
        self.assertIn("Report conversion rejected", stderr.getvalue())
        self.assertIn("Run ended with exit code 4", stderr.getvalue())

    def test_trace_logging_is_opt_in_and_contains_only_aggregate_counts(self):
        with patch.dict(os.environ, {"LOG_LEVEL": "trace"}):
            result, _ = self.run_audit(FILES)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("TRACE", result.stderr)
        self.assertIn("1 supported and 0 unsupported components", result.stderr)
        self.assertNotIn("scripts/lonely.sh", result.stderr)
        self.assertNotIn("Run ended with exit code", result.stdout)

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

    def test_static_audit_emits_report_without_target_capabilities(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp_root = Path(temporary_directory)
            repo_root = temp_root / "target"
            repo_root.mkdir()
            secret_sentinel = "E2E_DOCKER_SECRET_SENTINEL_7319"
            marker_paths = {name: temp_root / name for name in ("process.marker", "import.marker", "network.marker")}
            files = {
                **FILES,
                ".github/workflows/ci.yml": "jobs:\n  check:\n    steps:\n      - run: task check\n",
                "Taskfile.yml": "version: '3'\ntasks:\n  check:\n    cmds:\n      - python scripts/process_tripwire.py\n",
                "Dockerfile": f"FROM python:3.14\nENV API_TOKEN={secret_sentinel}\n",
                "scripts/process_tripwire.py": f"from pathlib import Path\nPath({str(marker_paths['process.marker'])!r}).write_text('ran')\n",
                "src/target_import_tripwire.py": f"from pathlib import Path\nPath({str(marker_paths['import.marker'])!r}).write_text('imported')\n",
                "src/network_tripwire.py": (
                    "import socket\n"
                    f"from pathlib import Path\nPath({str(marker_paths['network.marker'])!r}).write_text('connected')\n"
                    "socket.socket()\n"
                ),
                "src/app.py": "import target_import_tripwire\nimport network_tripwire\n",
            }
            for relative_path, text in files.items():
                path = repo_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            subprocess.run(["git", "init", "--quiet"], cwd=repo_root, check=True)
            subprocess.run(["git", "-C", str(repo_root), "add", "--", "."], check=True)
            tracked_status = subprocess.run(
                ["git", "-C", str(repo_root), "status", "--porcelain"], capture_output=True, text=True, check=True
            ).stdout
            before = {
                path.relative_to(repo_root).as_posix(): path.read_bytes()
                for path in repo_root.rglob("*")
                if path.is_file() and ".git" not in path.relative_to(repo_root).parts
            }

            process_attempts = []
            import_attempts = []
            socket_attempts = []
            original_run = subprocess.run
            original_popen = subprocess.Popen
            original_import = builtins.__import__

            def is_allowed_git(command):
                return (
                    isinstance(command, (list, tuple))
                    and len(command) > 3
                    and command[0] == "git"
                    and command[1] == "-C"
                    and command[3] in {"ls-files", "rev-parse", "log"}
                )

            def guarded_run(command, *args, **kwargs):
                if not is_allowed_git(command):
                    process_attempts.append(command)
                    raise AssertionError("non-Git target process call blocked")
                return original_run(command, *args, **kwargs)

            def guarded_popen(command, *args, **kwargs):
                if not is_allowed_git(command):
                    process_attempts.append(command)
                    raise AssertionError("non-Git target process call blocked")
                return original_popen(command, *args, **kwargs)

            def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
                if name in {"target_import_tripwire", "network_tripwire"}:
                    import_attempts.append(name)
                    raise AssertionError("target module import blocked")
                return original_import(name, globals, locals, fromlist, level)

            def guarded_socket(*args, **kwargs):
                socket_attempts.append("socket")
                raise AssertionError("network call blocked")

            output_path = temp_root / "report"
            stdout = StringIO()
            stderr = StringIO()
            with (
                patch("subprocess.run", side_effect=guarded_run),
                patch("subprocess.Popen", side_effect=guarded_popen),
                patch("builtins.__import__", side_effect=guarded_import),
                patch("socket.socket", side_effect=guarded_socket),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                exit_code = audit.main([str(repo_root), "--out", str(output_path), "--name", "synthetic/tripwire"])

            report = json.loads((output_path / "report.json").read_text(encoding="utf-8"))
            output_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in output_path.rglob("*") if path.is_file())
            after = {
                path.relative_to(repo_root).as_posix(): path.read_bytes()
                for path in repo_root.rglob("*")
                if path.is_file() and ".git" not in path.relative_to(repo_root).parts
            }
            final_status = subprocess.run(
                ["git", "-C", str(repo_root), "status", "--porcelain"], capture_output=True, text=True, check=True
            ).stdout

            self.assertEqual(exit_code, 0)
            self.assertEqual(audit.validate(report), [])
            self.assertTrue(
                any(edge["resolution"] == "resolved" and edge["to"].endswith("#task:check") for edge in report["coverage"]["runner_edges"])
            )
            self.assertEqual(process_attempts, [])
            self.assertEqual(import_attempts, [])
            self.assertEqual(socket_attempts, [])
            self.assertEqual(before, after)
            self.assertEqual(tracked_status, final_status)
            self.assertFalse(any(path.exists() for path in marker_paths.values()))
            self.assertNotIn(secret_sentinel, stdout.getvalue() + stderr.getvalue() + output_text)


if __name__ == "__main__":
    unittest.main()
