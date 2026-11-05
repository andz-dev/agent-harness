"""Tests for the bounded coverage reader using real temporary Git repositories."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from shutil import copytree
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import coverage  # noqa: E402
import detect_stack  # noqa: E402
import infra_checks  # noqa: E402
import score  # noqa: E402


class SafeReaderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temporary_directory.name) / "repo"
        self.repo_root.mkdir()
        subprocess.run(["git", "init", "--quiet"], cwd=self.repo_root, check=True)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def add_tracked_file(self, relative_path, content):
        path = self.repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        subprocess.run(["git", "add", "--", relative_path], cwd=self.repo_root, check=True)
        return path

    def tracked_paths(self):
        output = subprocess.run(
            ["git", "-C", str(self.repo_root), "ls-files", "-z"],
            capture_output=True,
            check=True,
        ).stdout
        return set(output.decode("utf-8", "surrogateescape").split("\0")) - {""}

    def test_safe_read_tracked_regular_file_and_accounts_for_budget(self):
        content = b"synthetic tracked source\n"
        self.add_tracked_file("src/example.py", content)
        budget = coverage.ReadBudget()

        result = coverage.read_tracked_file(self.repo_root, "src/example.py", self.tracked_paths(), budget)

        self.assertEqual(result.outcome, "read")
        self.assertEqual(result.content, content)
        self.assertEqual(result.sha256, hashlib.sha256(content).hexdigest())
        self.assertEqual(result.size, len(content))
        self.assertEqual(budget.candidates_seen, 1)
        self.assertEqual(budget.bytes_read, len(content))

    def test_safe_read_treats_shell_metacharacters_in_paths_as_literal(self):
        relative_path = "src/$(touch marker); space.txt"
        content = b"literal filename"
        self.add_tracked_file(relative_path, content)

        result = coverage.read_tracked_file(self.repo_root, relative_path, self.tracked_paths(), coverage.ReadBudget())

        self.assertEqual((result.outcome, result.content), ("read", content))
        self.assertFalse((self.repo_root / "marker").exists())

    def test_safe_read_rejects_parent_escape_and_untracked_file(self):
        outside_path = Path(self.temporary_directory.name) / "outside.txt"
        outside_path.write_text("OUTSIDE_SENTINEL", encoding="utf-8")
        untracked_path = self.repo_root / "private.env"
        untracked_path.write_text("UNTRACKED_SENTINEL", encoding="utf-8")
        tracked = self.tracked_paths()

        escape = coverage.read_tracked_file(self.repo_root, "../outside.txt", {"../outside.txt"}, coverage.ReadBudget())
        untracked = coverage.read_tracked_file(self.repo_root, "private.env", tracked, coverage.ReadBudget())

        self.assertEqual((escape.outcome, escape.reason, escape.content), ("unknown", "path_escape", None))
        self.assertEqual((untracked.outcome, untracked.reason, untracked.content), ("unknown", "untracked", None))
        self.assertNotIn("OUTSIDE_SENTINEL", repr(escape))
        self.assertNotIn("UNTRACKED_SENTINEL", repr(untracked))

    def test_safe_read_rejects_file_and_directory_symlinks_after_tracking(self):
        final_file = self.add_tracked_file("nested/secret.txt", b"FINAL_LINK_SENTINEL")
        directory_file = self.add_tracked_file("linked/secret.txt", b"DIRECTORY_LINK_SENTINEL")
        tracked = self.tracked_paths()
        outside_directory = Path(self.temporary_directory.name) / "outside"
        outside_directory.mkdir()
        outside_file = outside_directory / "secret.txt"
        outside_file.write_text("OUTSIDE_LINK_SENTINEL", encoding="utf-8")

        final_file.unlink()
        final_file.symlink_to(outside_file)
        directory_file.unlink()
        directory_file.parent.rmdir()
        directory_file.parent.symlink_to(outside_directory, target_is_directory=True)

        final_result = coverage.read_tracked_file(self.repo_root, "nested/secret.txt", tracked, coverage.ReadBudget())
        directory_result = coverage.read_tracked_file(self.repo_root, "linked/secret.txt", tracked, coverage.ReadBudget())

        self.assertEqual((final_result.outcome, final_result.reason, final_result.content), ("unknown", "symlink_rejected", None))
        self.assertEqual(
            (directory_result.outcome, directory_result.reason, directory_result.content), ("unknown", "symlink_rejected", None)
        )
        for result in (final_result, directory_result):
            self.assertNotIn("FINAL_LINK_SENTINEL", repr(result))
            self.assertNotIn("DIRECTORY_LINK_SENTINEL", repr(result))
            self.assertNotIn("OUTSIDE_LINK_SENTINEL", repr(result))

    def test_safe_read_rejects_file_identity_swap_between_check_and_open(self):
        tracked_file = self.add_tracked_file("secret.txt", b"ORIGINAL_CONTENT")
        replacement_file = self.repo_root / "replacement.txt"
        replacement_file.write_bytes(b"SWAPPED_SENTINEL")
        tracked = self.tracked_paths()
        original_open = os.open

        def swap_then_open(path, flags, mode=0o777, *, dir_fd=None):
            if path == "secret.txt" and dir_fd is not None:
                os.replace(replacement_file, tracked_file)
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with patch("coverage.os.open", side_effect=swap_then_open):
            result = coverage.read_tracked_file(self.repo_root, "secret.txt", tracked, coverage.ReadBudget())

        self.assertEqual((result.outcome, result.reason, result.content), ("unknown", "identity_changed", None))
        self.assertNotIn("SWAPPED_SENTINEL", repr(result))

    def test_safe_read_rejects_file_replacement_during_read(self):
        tracked_file = self.add_tracked_file("secret.txt", b"READ_CONTENT_SENTINEL")
        replacement_file = self.repo_root / "replacement.txt"
        replacement_file.write_bytes(b"REPLACEMENT_CONTENT")
        tracked = self.tracked_paths()
        original_read = os.read
        replaced = False

        def read_then_replace(file_descriptor, size):
            nonlocal replaced
            content = original_read(file_descriptor, size)
            if not replaced:
                os.replace(replacement_file, tracked_file)
                replaced = True
            return content

        with patch("coverage.os.read", side_effect=read_then_replace):
            result = coverage.read_tracked_file(self.repo_root, "secret.txt", tracked, coverage.ReadBudget())

        self.assertEqual((result.outcome, result.reason, result.content), ("unknown", "identity_changed", None))
        self.assertNotIn("READ_CONTENT_SENTINEL", repr(result))
        self.assertNotIn("REPLACEMENT_CONTENT", repr(result))

    def test_safe_read_file_total_and_candidate_budgets_reject_exhausted_reads(self):
        self.add_tracked_file("first.txt", b"1234")
        self.add_tracked_file("second.txt", b"5678")
        tracked = self.tracked_paths()

        file_limited = coverage.read_tracked_file(self.repo_root, "first.txt", tracked, coverage.ReadBudget(max_file_bytes=3))
        total_budget = coverage.ReadBudget(max_total_bytes=5)
        first_total_read = coverage.read_tracked_file(self.repo_root, "first.txt", tracked, total_budget)
        second_total_read = coverage.read_tracked_file(self.repo_root, "second.txt", tracked, total_budget)
        candidate_budget = coverage.ReadBudget(max_candidate_paths=1)
        first_candidate_read = coverage.read_tracked_file(self.repo_root, "first.txt", tracked, candidate_budget)
        second_candidate_read = coverage.read_tracked_file(self.repo_root, "second.txt", tracked, candidate_budget)

        for result in (file_limited, second_total_read, second_candidate_read):
            self.assertEqual((result.outcome, result.reason, result.content), ("unknown", "budget_exceeded", None))
        self.assertEqual(first_total_read.outcome, "read")
        self.assertEqual(total_budget.bytes_read, 4)
        self.assertEqual(first_candidate_read.outcome, "read")
        self.assertEqual(candidate_budget.candidates_seen, 1)

    def test_safe_read_permission_failure_is_content_free(self):
        secret = b"PERMISSION_SENTINEL"
        self.add_tracked_file("locked.txt", secret)
        tracked = self.tracked_paths()
        original_open = os.open

        def deny_locked_file(path, flags, mode=0o777, *, dir_fd=None):
            if path == "locked.txt" and dir_fd is not None:
                raise PermissionError("private path and contents must not be reported")
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with patch("coverage.os.open", side_effect=deny_locked_file):
            result = coverage.read_tracked_file(self.repo_root, "locked.txt", tracked, coverage.ReadBudget())

        self.assertEqual((result.outcome, result.reason, result.content), ("unknown", "permission_denied", None))
        self.assertNotIn("PERMISSION_SENTINEL", repr(result))


class ProvenanceTests(unittest.TestCase):
    def test_builds_safe_provenance_with_utc_timestamp(self):
        observed_at = datetime(2026, 11, 5, 12, 30, 45, tzinfo=UTC)

        provenance = coverage.make_provenance(
            "a" * 40,
            [{"path": "src/example.py", "sha256": "b" * 64, "locator": "function:build"}],
            "static_scan",
            observed_at,
        )

        self.assertEqual(
            provenance,
            {
                "revision": "a" * 40,
                "sources": [{"path": "src/example.py", "sha256": "b" * 64, "locator": "function:build"}],
                "method": "static_scan",
                "observed_at": "2026-11-05T12:30:45Z",
            },
        )

    def test_provenance_normalizes_aware_offsets_and_rejects_unsafe_identity(self):
        offset_time = datetime(2026, 11, 5, 14, 30, 45, tzinfo=timezone(timedelta(hours=2)))
        provenance = coverage.make_provenance(
            "a" * 40,
            [{"path": "src/example.py", "sha256": "b" * 64, "locator": "function:build"}],
            "static_scan",
            offset_time,
        )
        self.assertEqual(provenance["observed_at"], "2026-11-05T12:30:45Z")

        for path, digest in (("/absolute/path", "b" * 64), ("../outside", "b" * 64), ("src/file", "B" * 64)):
            with self.subTest(path=path, digest=digest[:2]):
                with self.assertRaises(ValueError):
                    coverage.make_provenance(
                        "a" * 40,
                        [{"path": path, "sha256": digest, "locator": "line:1"}],
                        "static_scan",
                        datetime(2026, 11, 5, tzinfo=UTC),
                    )

    def test_freshness_uses_revision_and_source_digests(self):
        digest = "b" * 64
        provenance = coverage.make_provenance(
            "a" * 40,
            [{"path": "src/example.py", "sha256": digest, "locator": "function:build"}],
            "static_scan",
            datetime(2026, 11, 5, 12, 30, 45, tzinfo=UTC),
        )

        self.assertEqual(coverage.classify_freshness(provenance, "a" * 40, {"src/example.py": digest}), "current")
        self.assertEqual(coverage.classify_freshness(provenance, "a" * 40, {"src/example.py": "c" * 64}), "stale")
        self.assertEqual(coverage.classify_freshness(provenance, "d" * 40, {"src/example.py": digest}), "stale")
        self.assertEqual(coverage.classify_freshness(provenance, None, {"src/example.py": digest}), "unknown")
        self.assertEqual(coverage.classify_freshness(None, "a" * 40, {"src/example.py": digest}), "unknown")

    def test_current_summary_excludes_stale_and_unknown_history_without_mutation(self):
        observations = [
            {"id": "current", "freshness": "current", "evidence": "declared"},
            {"id": "stale", "freshness": "stale", "evidence": "static_implementation_found"},
            {"id": "missing", "freshness": "unknown", "evidence": "unknown"},
        ]

        current = coverage.current_observations(observations)

        self.assertEqual([observation["id"] for observation in current], ["current"])
        self.assertEqual(observations[1]["evidence"], "static_implementation_found")
        self.assertEqual(observations[1]["freshness"], "stale")

    def test_binds_stale_provenance_without_rewriting_observed_evidence(self):
        observation = {"id": "sample", "evidence": "static_implementation_found"}
        provenance = coverage.make_provenance(
            "a" * 40,
            [{"path": "src/example.py", "sha256": "b" * 64, "locator": "function:build"}],
            "static_scan",
            datetime(2026, 11, 5, 12, 30, 45, tzinfo=UTC),
        )

        bound = coverage.bind_provenance(observation, provenance, "d" * 40, {"src/example.py": "b" * 64})

        self.assertEqual(bound["freshness"], "stale")
        self.assertEqual(bound["evidence"], "static_implementation_found")
        self.assertNotIn("freshness", observation)
        self.assertNotIn("provenance", observation)
        self.assertEqual(coverage.current_observations([bound]), [])


class ReceiptTests(unittest.TestCase):
    def receipt(self, status="success", revision="a" * 40):
        return json.dumps(
            {
                "status": status,
                "revision": revision,
                "run_id": "synthetic-run",
                "observed_at": "2026-11-05T12:30:45Z",
                "sources": [{"path": "src/example.py", "sha256": "b" * 64}],
                "evidence": "execution_observed",
                "command": "unsafe command sentinel",
                "issuer": "untrusted local text",
            }
        ).encode()

    def test_receipt_outcomes_never_promote_self_claimed_execution(self):
        current_sources = {"src/example.py": "b" * 64}
        cases = (
            (None, "absent", None),
            (self.receipt(), "present_unverified", "a" * 40),
            (b"{malformed", "invalid", "a" * 40),
            (self.receipt(revision="c" * 40), "stale", "a" * 40),
            (self.receipt(status="partial"), "partial", "a" * 40),
            (self.receipt(status="failed"), "failed", "a" * 40),
        )
        for raw_receipt, expected_outcome, current_revision in cases:
            with self.subTest(outcome=expected_outcome):
                result = coverage.classify_receipt(raw_receipt, current_revision, current_sources)
                self.assertEqual(result.outcome, expected_outcome)
                self.assertNotIn("execution_observed", repr(result))
                self.assertNotIn("unsafe command sentinel", repr(result))
                self.assertNotIn("untrusted local text", repr(result))

    def test_receipt_with_changed_source_digest_is_stale(self):
        result = coverage.classify_receipt(
            self.receipt(),
            "a" * 40,
            {"src/example.py": "c" * 64},
        )

        self.assertEqual((result.outcome, result.reason_code), ("stale", "source_mismatch"))

    def test_oversized_receipt_is_invalid_and_content_free(self):
        result = coverage.classify_receipt(b"x" * (coverage.MAX_FILE_BYTES + 1), "a" * 40, {})

        self.assertEqual((result.outcome, result.reason_code), ("invalid", "oversized"))
        self.assertNotIn("x" * 32, repr(result))


class ComponentFixtureTests(unittest.TestCase):
    def test_golden_component_recipes_are_materialized_and_deterministic(self):
        fixtures_root = Path(__file__).parent / "fixtures" / "coverage"
        cases = {
            "PY-01": ({"python"}, set()),
            "PY-02": ({"python"}, set()),
            "NODE-01": ({"node"}, set()),
            "NODE-02": ({"node"}, set()),
            "MIXED-01": ({"python", "node"}, {("native", "rust")}),
            "INFRA-01": (set(), set()),
            "RUST-01": (set(), {(".", "rust")}),
        }
        for case_id, (expected_supported, expected_unsupported) in cases.items():
            with self.subTest(case_id=case_id):
                fixture = fixtures_root / case_id
                self.assertTrue(fixture.is_dir(), case_id)
                first = detect_stack.detect(fixture)
                second = detect_stack.detect(fixture)
                supported = {component["ecosystem"] for component in first["stack"]["components"]}
                unsupported = {(item["path"], item["language"]) for item in first["stack"].get("unsupported", [])}
                self.assertEqual(supported, expected_supported)
                self.assertEqual(unsupported, expected_unsupported)
                self.assertEqual(first, second)


class TopicCatalogTests(unittest.TestCase):
    def test_seven_topic_catalog_links_existing_checks_deterministically(self):
        catalog_path = Path(__file__).parent.parent / "checks" / "coverage-topics.yaml"
        catalog_text = catalog_path.read_text(encoding="utf-8")
        topic_catalog = yaml.safe_load(catalog_text)
        core_catalog = yaml.safe_load((Path(__file__).parent.parent / "checks" / "catalog.yaml").read_text(encoding="utf-8"))
        existing_check_ids = {check["id"] for check in core_catalog["checks"]} | set(infra_checks.CHECKS)

        topics = coverage.validate_topic_catalog(topic_catalog, existing_check_ids)

        self.assertEqual(
            [topic["id"] for topic in topics],
            ["code_standards", "testing", "ci_build", "security", "dependencies", "mcp", "skills_extensions"],
        )
        self.assertEqual(topics, coverage.validate_topic_catalog(yaml.safe_load(catalog_text), existing_check_ids))
        self.assertTrue(all(set(topic["check_ids"]) <= existing_check_ids for topic in topics))
        self.assertTrue(all(0 < topic["limits"]["max_files"] <= 2048 for topic in topics))
        self.assertTrue(all(0 < topic["limits"]["max_bytes"] <= coverage.MAX_TOTAL_BYTES for topic in topics))
        self.assertTrue(all(topic["id"] not in score.WEIGHTS for topic in topics))
        schema = json.loads((Path(__file__).parent.parent / "schema" / "report.schema.json").read_text(encoding="utf-8"))
        check_id_validator = Draft202012Validator(schema["$defs"]["coverage_check_id"])
        self.assertTrue(all(check_id_validator.is_valid(check_id) for topic in topics for check_id in topic["check_ids"]))

        invalid_catalog = yaml.safe_load(catalog_text)
        invalid_catalog["topics"][0]["check_ids"].append("BAD-99")
        with self.assertRaisesRegex(ValueError, "check references"):
            coverage.validate_topic_catalog(invalid_catalog, existing_check_ids)

    def test_topic_source_collection_reads_only_matching_tracked_files(self):
        fixture = Path(__file__).parent / "fixtures" / "coverage" / "PY-01"
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "repo"
            copytree(fixture, repo_root)
            subprocess.run(["git", "init", "--quiet"], cwd=repo_root, check=True)
            subprocess.run(["git", "-C", str(repo_root), "add", "--", "."], check=True)
            tracked_paths = detect_stack.list_files(repo_root)
            topic_catalog = yaml.safe_load((Path(__file__).parent.parent / "checks" / "coverage-topics.yaml").read_text(encoding="utf-8"))
            topic = next(item for item in topic_catalog["topics"] if item["id"] == "ci_build")

            result = coverage.collect_topic_sources(repo_root, topic, tracked_paths, coverage.ReadBudget())

        self.assertEqual(result["outcome"], "complete")
        self.assertEqual(result["topic_id"], "ci_build")
        self.assertEqual([source["path"] for source in result["sources"]], ["Taskfile.yml"])
        self.assertEqual(result["sources"][0]["locator"], "file")
        self.assertEqual(result["check_ids"], topic["check_ids"])
        self.assertNotIn("python -m unittest", repr(result))

    def test_topic_source_collection_reports_path_and_byte_budget_exhaustion(self):
        fixture = Path(__file__).parent / "fixtures" / "coverage" / "PY-01"
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory) / "repo"
            copytree(fixture, repo_root)
            subprocess.run(["git", "init", "--quiet"], cwd=repo_root, check=True)
            subprocess.run(["git", "-C", str(repo_root), "add", "--", "."], check=True)
            tracked_paths = detect_stack.list_files(repo_root)
            topic_catalog = yaml.safe_load((Path(__file__).parent.parent / "checks" / "coverage-topics.yaml").read_text(encoding="utf-8"))
            topic = next(item for item in topic_catalog["topics"] if item["id"] == "ci_build")

            path_limited = coverage.collect_topic_sources(repo_root, topic, tracked_paths, coverage.ReadBudget(max_candidate_paths=0))
            byte_limited = coverage.collect_topic_sources(repo_root, topic, tracked_paths, coverage.ReadBudget(max_total_bytes=1))

        self.assertEqual((path_limited["outcome"], path_limited["reason_codes"]), ("partial", ["budget_exceeded"]))
        self.assertEqual((byte_limited["outcome"], byte_limited["reason_codes"]), ("partial", ["budget_exceeded"]))
        self.assertEqual(path_limited["sources"], [])
        self.assertEqual(byte_limited["sources"], [])

    def test_golden_topic_fixtures_have_safe_static_sources(self):
        fixtures_root = Path(__file__).parent / "fixtures" / "coverage"
        expected = {
            "PY-01": ("ci_build", ["Taskfile.yml"]),
            "PY-02": ("code_standards", ["pyproject.toml"]),
            "NODE-01": ("testing", ["test/demo.test.js"]),
            "NODE-02": ("dependencies", ["package-lock.json", "package.json"]),
            "TOPIC-SECURITY": ("security", ["SECURITY.md"]),
            "TOPIC-MCP": ("mcp", [".mcp.json"]),
            "TOPIC-SKILLS": ("skills_extensions", [".agents/skills/synthetic/SKILL.md"]),
        }
        topic_catalog = yaml.safe_load((Path(__file__).parent.parent / "checks" / "coverage-topics.yaml").read_text(encoding="utf-8"))
        topics = {topic["id"]: topic for topic in topic_catalog["topics"]}

        for case_id, (topic_id, expected_paths) in expected.items():
            with self.subTest(case_id=case_id):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    repo_root = Path(temporary_directory) / "repo"
                    copytree(fixtures_root / case_id, repo_root)
                    subprocess.run(["git", "init", "--quiet"], cwd=repo_root, check=True)
                    subprocess.run(["git", "-C", str(repo_root), "add", "--", "."], check=True)
                    tracked_paths = detect_stack.list_files(repo_root)
                    result = coverage.collect_topic_sources(
                        repo_root,
                        topics[topic_id],
                        tracked_paths,
                        coverage.ReadBudget(),
                    )
                self.assertEqual(result["outcome"], "complete", case_id)
                self.assertEqual([source["path"] for source in result["sources"]], expected_paths, case_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
