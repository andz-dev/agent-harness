"""Synthetic regression canaries for repository document/publication boundaries."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.check import design, documents, publication  # noqa: E402


class RepositoryQualityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="harness-quality-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "docs/0001").mkdir(parents=True)
        (self.root / "docs/0001/.gitkeep").touch()
        (self.root / "docs/0002").mkdir()
        for name in ("architecture-model.jsonc", "change-set.jsonc"):
            (self.root / "docs/0002" / name).write_text(json.dumps({}), encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
