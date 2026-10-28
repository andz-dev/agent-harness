"""Public CLI tests for compact static audit-history receipts."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

CLI = Path(__file__).resolve().parents[1] / "tools/audit_history.py"
PILLARS = (
    "verification",
    "orientation",
    "static_guardrails",
    "workflow_entry_points",
    "automatic_triggers",
    "pipeline_parity",
    "doc_hygiene",
)


class AuditHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="audit-history-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        (self.root / ".gitignore").write_text(".data/\nreports/\n", encoding="utf-8")
        self.git("add", ".gitignore")
        self.git(
            "-c",
            "user.name=Synthetic",
            "-c",
            "user.email=synthetic@example.test",
            "-c",
            "core.hooksPath=/dev/null",
            "commit",
            "-qm",
            "Synthetic initial state",
        )
        self.commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.engine = self.root / "engine"
        for relative in (
            "scripts/audit.py",
            "scripts/run_checks.py",
            "scripts/score.py",
            "checks/catalog.yaml",
            "schema/report.schema.json",
        ):
            path = self.engine / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n" if relative.endswith(".json") else "synthetic\n", encoding="utf-8")
        self.report = self.root / "reports/report.json"
        self.report.parent.mkdir()
        self.payload = {
            "schema_version": "0.1",
            "tool": {"name": "harness-audit", "version": "1.2.0", "catalog_version": "0.1"},
            "generated_at": datetime.now(UTC).isoformat(),
            "repo": {"name": "synthetic", "commit": self.commit, "clone_mode": "full"},
            "score": {"final": 55},
            "pillars": [{"pillar": name, "level": 2} for name in PILLARS],
            "findings": [
                {
                    "check_id": "VER-01",
                    "status": "pass",
                    "source": "script",
                    "evidence": [{"snippet": "private excerpt must not be copied"}],
                }
            ],
            "limitations": ["Synthetic unanswered judgments"],
        }
        self.write_report()

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.root), *arguments], capture_output=True, text=True, check=True)

    def write_report(self):
        self.report.write_text(json.dumps(self.payload), encoding="utf-8")

    def cli(self, *arguments):
        return subprocess.run([sys.executable, str(CLI), *map(str, arguments)], capture_output=True, text=True)

    def record(self, label="baseline"):
        result = self.cli("record", "--repo", self.root, "--report", self.report, "--engine-root", self.engine, "--label", label)
        self.assertEqual(result.returncode, 0, result.stderr)
        relative = json.loads(result.stdout)["record"]
        path = self.root / relative
        return path, json.loads(path.read_text(encoding="utf-8"))

    def test_record_is_compact_immutable_and_owner_only(self):
        first, record = self.record()
        second, _ = self.record()
        self.assertNotEqual(first, second)
        self.assertEqual(record["score"], 55)
        self.assertNotIn("private excerpt", first.read_text(encoding="utf-8"))
        self.assertEqual(first.stat().st_mode & 0o777, 0o600)
        self.assertEqual(first.parent.stat().st_mode & 0o777, 0o700)

    def test_compare_reports_explicit_check_and_score_changes(self):
        before, _ = self.record("before")
        self.payload["score"]["final"] = 60
        self.payload["findings"][0]["status"] = "fail"
        self.write_report()
        after, _ = self.record("after")
        result = self.cli("compare", before, after)
        self.assertEqual(result.returncode, 0, result.stderr)
        comparison = json.loads(result.stdout)
        self.assertEqual(comparison["score"]["delta"], 5)
        self.assertEqual(comparison["checks"]["changed"][0]["before"], "pass")
        self.assertEqual(comparison["checks"]["changed"][0]["after"], "fail")

    def test_compare_refuses_different_engine_fingerprints(self):
        before, record = self.record()
        record["fingerprints"]["engine"] = "0" * 64
        incompatible = self.root / "incompatible.json"
        incompatible.write_text(json.dumps(record), encoding="utf-8")
        result = self.cli("compare", before, incompatible)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fingerprints", result.stderr)

    def test_compare_refuses_repository_catalog_and_clone_mismatches(self):
        before, record = self.record()
        for field in ("repository_id", "catalog", "clone_mode"):
            with self.subTest(field=field):
                changed = json.loads(json.dumps(record))
                if field == "catalog":
                    changed["fingerprints"][field] = "1" * 64
                else:
                    changed[field] = "1" * 64 if field == "repository_id" else "shallow"
                path = self.root / "different.json"
                path.write_text(json.dumps(changed), encoding="utf-8")
                result = self.cli("compare", before, path)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Incomparable", result.stderr)

    def test_invalid_report_fails_without_creating_history(self):
        self.payload["score"]["final"] = "55"
        self.write_report()
        result = self.cli("record", "--repo", self.root, "--report", self.report, "--engine-root", self.engine, "--label", "invalid")
        self.assertEqual(result.returncode, 2)
        self.assertIn("score", result.stderr)
        self.assertFalse((self.root / ".data").exists())

    def test_non_object_report_fields_return_structured_errors(self):
        self.payload["tool"] = []
        self.write_report()
        result = self.cli("record", "--repo", self.root, "--report", self.report, "--engine-root", self.engine, "--label", "invalid")
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", json.loads(result.stderr))

    def test_symlinked_report_is_rejected(self):
        link = self.root / "linked.json"
        link.symlink_to(self.report)
        result = self.cli("record", "--repo", self.root, "--report", link, "--engine-root", self.engine, "--label", "unsafe")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Symlink", result.stderr)

    def test_world_readable_existing_storage_is_not_silently_changed(self):
        storage = self.root / ".data"
        storage.mkdir(mode=0o755)
        os.chmod(storage, 0o755)
        result = self.cli("record", "--repo", self.root, "--report", self.report, "--engine-root", self.engine, "--label", "unsafe")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(storage.stat().st_mode & 0o777, 0o755)

    def test_stale_report_is_not_fingerprinted_as_a_new_engine(self):
        self.payload["generated_at"] = "2000-01-01T00:00:00Z"
        self.write_report()
        result = self.cli("record", "--repo", self.root, "--report", self.report, "--engine-root", self.engine, "--label", "stale")
        self.assertEqual(result.returncode, 2)
        self.assertIn("generate a fresh audit", result.stderr)


if __name__ == "__main__":
    unittest.main()
