"""Synthetic regression canaries for repository document/publication boundaries."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.check import design, documents, publication  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/harness-audit/scripts"))
import audit as audit_engine  # noqa: E402


class RepositoryQualityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="harness-quality-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "docs/0001-v0.1-standalone-extraction-retrospective").mkdir(parents=True)
        (self.root / "docs/0001-v0.1-standalone-extraction-retrospective/.gitkeep").touch()
        (self.root / "docs/0002-v0.2-harness-audit-as-built-adoption").mkdir()
        for name in ("architecture-model.jsonc", "change-set.jsonc"):
            (self.root / "docs/0002-v0.2-harness-audit-as-built-adoption" / name).write_text(json.dumps({}), encoding="utf-8")

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.root), *arguments], check=True, capture_output=True, text=True)

    def test_private_generated_markdown_does_not_break_source_documents(self):
        for relative in ("reports/audit/report.md", ".data/run/note.md", "apps/city/test-results/error-context.md"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Generated runtime output without source frontmatter\n", encoding="utf-8")
        self.assertEqual(documents(self.root), [])

    def test_authored_markdown_still_requires_frontmatter(self):
        (self.root / "README.md").write_text("# Missing metadata\n", encoding="utf-8")
        self.assertIn("README.md: missing type frontmatter", documents(self.root))

    def test_similarly_named_source_directories_are_not_exempt(self):
        path = self.root / "docs/.dataset/guide.md"
        path.parent.mkdir()
        path.write_text("# Still authored documentation\n", encoding="utf-8")
        self.assertIn("docs/.dataset/guide.md: missing type frontmatter", documents(self.root))

    def test_tracked_private_output_still_fails_publication(self):
        self.git("init", "-q")
        (self.root / ".gitignore").write_text("reports/\n", encoding="utf-8")
        report = self.root / "reports/synthetic.json"
        report.parent.mkdir()
        report.write_text('{"synthetic": true}\n', encoding="utf-8")
        self.git("add", "-f", "reports/synthetic.json")
        self.assertIn("Generated/private output is tracked: reports/synthetic.json", publication(self.root))

    def test_design_check_passes_on_the_repository(self):
        self.assertEqual(design(Path(__file__).resolve().parents[1]), [])

    def test_perspective_camera_fails_the_design_check(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            city = tmp / "apps/harness-city"
            city.mkdir(parents=True)
            for name in ("DESIGN.md", "AGENTS.md"):
                (city / name).write_text((root / "apps/harness-city" / name).read_text(encoding="utf-8"), encoding="utf-8")
            html = (root / "apps/harness-city/index.html").read_text(encoding="utf-8")
            (city / "index.html").write_text(html.replace("THREE.OrthographicCamera", "THREE.PerspectiveCamera"), encoding="utf-8")
            for name in ("AGENTS.md", "CLAUDE.md"):
                (tmp / name).write_text((root / name).read_text(encoding="utf-8"), encoding="utf-8")
            self.assertTrue(any("orthographic" in f for f in design(tmp)))


class CityConverterTests(unittest.TestCase):
    def test_legacy_report_without_coverage_keeps_core_without_inventing_coverage(self):
        root = Path(__file__).resolve().parents[1]
        converter = root / "apps/harness-city/tools/report_to_city.py"
        report_path = root / "skills/harness-audit/schema/example-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        expected_score = round(report["score"]["final"])
        expected_levels = [pillar["level"] for pillar in report["pillars"]]

        with tempfile.TemporaryDirectory(prefix="city-converter-test-") as temporary:
            source = Path(temporary) / "report.json"
            output = Path(temporary) / "cities.json"
            source.write_text(json.dumps(report), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(converter), str(source), "--out", str(output)],
                cwd=root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            city_data = json.loads(output.read_text(encoding="utf-8"))

        city = city_data["cities"][0]
        self.assertEqual(city["score"], expected_score)
        self.assertEqual(city["L"], expected_levels)
        self.assertNotIn("coverage", city)
        self.assertIn("synthetic", city)
        self.assertIsNone(city["synthetic"])

    def test_current_coverage_report_preserves_states_and_safe_provenance(self):
        root = Path(__file__).resolve().parents[1]
        converter = root / "apps/harness-city/tools/report_to_city.py"
        report_path = root / "skills/harness-audit/schema/example-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        topic_states = {
            "code_standards": ("applicable", "declared", "current"),
            "testing": ("applicable", "static_implementation_found", "stale"),
            "ci_build": ("applicable", "prototype_simulated", "unknown"),
            "security": ("undetermined", "unknown", "unknown"),
            "dependencies": ("inapplicable", "unknown", "unknown"),
            "mcp": ("unsupported", "unknown", "unknown"),
            "skills_extensions": ("applicable", "unknown", "unknown"),
        }
        coverage = {
            "version": 1,
            "components": [{"id": "api", "root": ".", "languages": ["python"], "adapter": "python", "applicability": "applicable"}],
            "observations": [
                {
                    "id": f"api:{topic_id}",
                    "component_id": "api",
                    "topic_id": topic_id,
                    "check_ids": ["VER-01"],
                    "applicability": states[0],
                    "evidence": states[1],
                    "freshness": states[2],
                    "provenance": {
                        "revision": "0123abc",
                        "sources": [
                            {
                                "path": "tests/test_api.py" if topic_id == "testing" else "README.md",
                                "sha256": "a" * 64,
                                "locator": "test_health_check" if topic_id == "testing" else f"{topic_id}_declaration",
                            }
                        ],
                        "method": "tracked_path_match",
                        "observed_at": "2026-11-05T00:00:00Z",
                    },
                    "receipt": {"outcome": "present_unverified" if topic_id == "testing" else "absent"},
                    "limitations": ["Synthetic converter fixture."],
                }
                for topic_id, states in topic_states.items()
            ],
            "runner_edges": [],
            "collection": {
                "outcome": "complete",
                "limits": {"max_file_bytes": 1, "max_total_bytes": 1, "max_candidate_paths": 1, "max_runner_depth": 1},
                "reason_codes": [],
            },
            "limitations": [],
        }
        report["quality"] = {"availability": "available", "score": report["score"]["final"], "reason_codes": []}
        report["meta"] = {"synthetic": True}
        report["coverage"] = coverage
        self.assertEqual(audit_engine.validate(report), [])

        with tempfile.TemporaryDirectory(prefix="city-converter-test-") as temporary:
            source = Path(temporary) / "report.json"
            output = Path(temporary) / "cities.json"
            source.write_text(json.dumps(report), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(converter), str(source), "--out", str(output)],
                cwd=root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            city_data = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(city_data["cities"][0].get("coverage"), coverage)
        self.assertIs(city_data["cities"][0]["synthetic"], True)

    def test_unknown_coverage_version_keeps_core_and_drops_future_payload(self):
        root = Path(__file__).resolve().parents[1]
        converter = root / "apps/harness-city/tools/report_to_city.py"
        report_path = root / "skills/harness-audit/schema/example-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["coverage"] = {"version": 999, "observations": [{"note": "FUTURE_PAYLOAD_SENTINEL"}]}
        expected_score = round(report["score"]["final"])
        expected_levels = [pillar["level"] for pillar in report["pillars"]]

        with tempfile.TemporaryDirectory(prefix="city-converter-test-") as temporary:
            source = Path(temporary) / "report.json"
            output = Path(temporary) / "cities.json"
            source.write_text(json.dumps(report), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(converter), str(source), "--out", str(output)],
                cwd=root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output_text = output.read_text(encoding="utf-8")
            city_data = json.loads(output_text)

        city = city_data["cities"][0]
        self.assertEqual(city["score"], expected_score)
        self.assertEqual(city["L"], expected_levels)
        self.assertEqual(
            city.get("coverage"),
            {
                "availability": "unsupported",
                "version": 999,
                "observations": [],
                "limitations": ["Coverage version is unsupported."],
            },
        )
        self.assertIn("Coverage version is unsupported.", city["lim"])
        self.assertNotIn("FUTURE_PAYLOAD_SENTINEL", output_text)

    def test_unknown_report_envelope_major_is_rejected_with_safe_diagnostic(self):
        root = Path(__file__).resolve().parents[1]
        converter = root / "apps/harness-city/tools/report_to_city.py"
        report_path = root / "skills/harness-audit/schema/example-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["schema_version"] = "999.0"
        report["repo"]["name"] = "ENVELOPE_PAYLOAD_SENTINEL"

        with tempfile.TemporaryDirectory(prefix="city-converter-test-") as temporary:
            source = Path(temporary) / "report.json"
            output = Path(temporary) / "cities.json"
            source.write_text(json.dumps(report), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(converter), str(source), "--out", str(output)],
                cwd=root,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.strip(), "unsupported report envelope version")
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("ENVELOPE_PAYLOAD_SENTINEL", result.stdout + result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
