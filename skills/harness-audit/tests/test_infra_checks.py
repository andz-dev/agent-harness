"""Tests for scripts/infra_checks.py using synthetic trees.

Run: python3 -I tests/test_infra_checks.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import detect_infra  # noqa: E402
import detect_stack  # noqa: E402
import infra_checks  # noqa: E402

GOOD_DOCKERFILE = "FROM python:3.12-slim AS base\nFROM base\nUSER app\nHEALTHCHECK CMD true\nENV PASSWORD=${PASSWORD}\n"


def run(tree):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for rel, text in tree.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        det = detect_infra.detect(root)
        return infra_checks.run(root, detect_stack.list_files(root), det["detected"])


def status(result, cid, scope=None):
    got = [f["status"] for f in result["findings"] if f["check_id"] == cid and (scope is None or f["scope"] == scope)]
    assert got, f"{cid} not evaluated"
    return got[0]


class DockerfileTests(unittest.TestCase):
    def test_good_dockerfile_passes_the_file_checks(self):
        r = run({"Dockerfile": GOOD_DOCKERFILE, ".dockerignore": ".git\n"})
        for cid in ("INF-D01", "INF-D02", "INF-D03", "INF-D04", "INF-D06"):
            self.assertEqual(status(r, cid), "pass", cid)

    def test_latest_bare_root_and_secret_fail(self):
        r = run({"Dockerfile": "FROM node\nFROM python:latest\nENV API_TOKEN=abc123\n"})
        self.assertEqual(status(r, "INF-D01"), "fail")
        self.assertEqual(status(r, "INF-D02"), "fail")
        self.assertEqual(status(r, "INF-D03"), "fail")
        self.assertEqual(status(r, "INF-D04"), "fail")
        self.assertEqual(status(r, "INF-D06"), "fail")

    def test_digest_scratch_and_stage_references_are_pinned(self):
        r = run({"Dockerfile": "FROM scratch AS a\nFROM a AS b\nFROM python@sha256:" + "a" * 64 + "\n"})
        self.assertEqual(status(r, "INF-D02"), "pass")

    def test_hadolint_and_build_in_ci(self):
        ci = ".github/workflows/ci.yml"
        r = run({"Dockerfile": GOOD_DOCKERFILE, ci: "steps:\n  - run: hadolint Dockerfile\n  - run: docker build .\n"})
        self.assertEqual(status(r, "INF-D05"), "pass")
        self.assertEqual(status(r, "INF-D07"), "pass")
        r = run({"Dockerfile": GOOD_DOCKERFILE})
        self.assertEqual(status(r, "INF-D05"), "fail")
        self.assertEqual(status(r, "INF-D07"), "fail")


class ComposeTests(unittest.TestCase):
    def test_pinned_with_healthcheck_passes(self):
        text = "services:\n  db:\n    image: postgres:16\n    healthcheck:\n      test: ['CMD', 'true']\n    environment:\n      POSTGRES_PASSWORD: ${PW}\n"
        r = run({"compose.yaml": text})
        self.assertEqual(status(r, "INF-C01"), "pass")
        self.assertEqual(status(r, "INF-C02"), "pass")
        self.assertEqual(status(r, "INF-C03"), "pass")

    def test_latest_missing_healthcheck_and_literal_secret_fail(self):
        text = "services:\n  web:\n    image: nginx\n    environment:\n      - DB_PASSWORD=hunter2\n"
        r = run({"docker-compose.yml": text})
        self.assertEqual(status(r, "INF-C01"), "fail")
        self.assertEqual(status(r, "INF-C02"), "fail")
        self.assertEqual(status(r, "INF-C03"), "fail")

    def test_locally_built_image_name_is_not_flagged(self):
        r = run({"compose.yaml": "services:\n  app:\n    build: .\n    image: app:latest\n"})
        self.assertEqual(status(r, "INF-C01"), "pass")

    def test_env_example_and_tracked_env(self):
        base = "services:\n  a:\n    image: x:1\n    env_file: .env\n"
        self.assertEqual(status(run({"compose.yaml": base, ".env.example": "A=1\n"}), "INF-C04"), "pass")
        self.assertEqual(status(run({"compose.yaml": base, ".env.example": "A=1\n", ".env": "A=1\n"}), "INF-C04"), "fail")

    def test_file_without_services_is_not_applicable(self):
        r = run({"compose.override.yaml": "x-common: {}\n"})
        self.assertEqual({f["status"] for f in r["findings"]}, {"not_applicable"})


class DevcontainerTests(unittest.TestCase):
    GOOD = """{
  // comment
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {"ghcr.io/devcontainers/features/node:1": {}},
  "postCreateCommand": "uv sync",
  "customizations": {"vscode": {"extensions": ["charliermarsh.ruff"],},},
}"""

    def test_good_config_passes(self):
        r = run({".devcontainer/devcontainer.json": self.GOOD})
        for cid in ("INF-V01", "INF-V02", "INF-V03", "INF-V04", "INF-V05"):
            self.assertEqual(status(r, cid), "pass", cid)
        self.assertEqual(status(r, "INF-V06"), "fail")

    def test_unpinned_and_empty_fail(self):
        r = run({".devcontainer/devcontainer.json": '{"image": "ubuntu", "features": {"ghcr.io/x/y/z": {}}}'})
        self.assertEqual(status(r, "INF-V02"), "fail")
        self.assertEqual(status(r, "INF-V03"), "fail")
        self.assertEqual(status(r, "INF-V05"), "fail")
        self.assertEqual(status(r, "INF-V04"), "not_applicable")

    def test_invalid_json_fails_first_check_only(self):
        r = run({".devcontainer/devcontainer.json": "{not json"})
        self.assertEqual(status(r, "INF-V01"), "fail")
        self.assertEqual(status(r, "INF-V02"), "not_applicable")

    def test_ci_builds_devcontainer(self):
        r = run({".devcontainer/devcontainer.json": self.GOOD, ".github/workflows/dc.yml": "uses: devcontainers/ci@v0.3\n"})
        self.assertEqual(status(r, "INF-V06"), "pass")


class TerraformTests(unittest.TestCase):
    MAIN = (
        'terraform {\n  required_providers {\n    aws = {\n      source  = "hashicorp/aws"\n      version = "~> 5.0"\n    }\n  }\n'
        '  backend "s3" {}\n}\nprovider "aws" {}\n'
    )

    def test_good_root_module(self):
        ci = ".github/workflows/tf.yml"
        r = run(
            {
                "infra/main.tf": self.MAIN,
                "infra/.terraform.lock.hcl": "",
                ".tflint.hcl": "",
                ci: "run: terraform fmt -check\nrun: terraform plan\n",
            }
        )
        for cid in ("INF-T01", "INF-T02", "INF-T03", "INF-T04", "INF-T05", "INF-T06", "INF-T07"):
            self.assertEqual(status(r, cid, "infra"), "pass", cid)

    def test_bare_module_fails_basics(self):
        r = run({"infra/main.tf": 'resource "x" "y" {}\n', "infra/terraform.tfstate": "{}"})
        self.assertEqual(status(r, "INF-T01"), "fail")
        self.assertEqual(status(r, "INF-T02"), "fail")
        self.assertEqual(status(r, "INF-T06"), "fail")
        self.assertEqual(status(r, "INF-T07"), "not_applicable")

    def test_provider_without_version_and_backend_fails(self):
        main = 'terraform {\n  required_providers {\n    aws = { source = "hashicorp/aws" }\n  }\n}\n'
        r = run({"main.tf": main})
        self.assertEqual(status(r, "INF-T02"), "fail")
        self.assertEqual(status(r, "INF-T07"), "fail")

    def test_example_tfvars_is_allowed(self):
        r = run({"main.tf": self.MAIN, "prod.tfvars.example": "", "terraform.tfvars": "a=1\n"})
        self.assertEqual(status(r, "INF-T06"), "fail")
        r = run({"main.tf": self.MAIN, "prod.example.tfvars": ""})
        self.assertEqual(status(r, "INF-T06"), "pass")


class SummaryTests(unittest.TestCase):
    def test_summary_counts_per_area(self):
        r = run({"Dockerfile": GOOD_DOCKERFILE})
        s = r["summary"]["dockerfile"]
        self.assertEqual(s["passed"] + s["failed"] + s["not_applicable"], 7)
        self.assertGreater(s["pass_rate"], 0)

    def test_no_infra_no_findings(self):
        self.assertEqual(run({"app.py": "x=1\n"}), {"findings": [], "summary": {}})


if __name__ == "__main__":
    unittest.main()
