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
        self.assertEqual(
            run({"app.py": "x=1\n"}),
            {"findings": [], "summary": {}, "rollup": [], "levels": {"overall": None, "weakest_area": None, "areas": {}}},
        )


class RollupTests(unittest.TestCase):
    def test_rollup_counts_locations_per_check(self):
        r = run({"a/Dockerfile": "FROM node\nUSER app\n", "b/Dockerfile": "FROM python:3.12\nUSER app\n"})
        row = next(x for x in r["rollup"] if x["check_id"] == "INF-D02")
        self.assertEqual((row["passed"], row["failed"]), (1, 1))
        self.assertEqual(row["failing"], ["a/Dockerfile"])
        self.assertEqual(r["rollup"][0]["failed"], max(x["failed"] for x in r["rollup"]))

    def test_empty(self):
        self.assertEqual(run({"app.py": "x=1\n"})["rollup"], [])


class LevelTests(unittest.TestCase):
    GOOD_TF = (
        'terraform {\n  required_providers {\n    aws = {\n      source  = "hashicorp/aws"\n      version = "~> 5.0"\n    }\n  }\n'
        '  backend "s3" {}\n}\nprovider "aws" {}\n'
    )

    def lvl(self, tree, area):
        return run(tree)["levels"]["areas"][area]

    def test_failed_gate_keeps_area_at_level_zero(self):
        a = self.lvl({"Dockerfile": "FROM node\nUSER app\nHEALTHCHECK CMD true\n"}, "dockerfile")
        self.assertEqual(a["level"], 0)
        self.assertEqual(a["blocked_by"], ["INF-D01"])  # the level-2 gate INF-D02 is not looked at before L1 is met

    def test_gates_pass_but_ratio_too_low_stays_below(self):
        a = self.lvl({"Dockerfile": "FROM python:3.12\n", ".dockerignore": "x\n"}, "dockerfile")
        self.assertEqual(a["level"], 1)
        self.assertEqual(a["pass_ratio_by_level"]["1"], 1.0)

    def test_full_marks_reach_level_three(self):
        ci = ".github/workflows/ci.yml"
        tree = {
            "Dockerfile": GOOD_DOCKERFILE,
            ".dockerignore": "x\n",
            ci: "run: hadolint Dockerfile\nrun: docker build .\n",
        }
        a = self.lvl(tree, "dockerfile")
        self.assertEqual(a["level"], 3)
        self.assertEqual(a["blocked_by"], [])

    def test_one_failing_location_fails_the_check(self):
        tree = {"a/Dockerfile": "FROM python:3.12\n", "b/Dockerfile": "FROM node\n", "a/.dockerignore": "x\n", "b/.dockerignore": "x\n"}
        a = self.lvl(tree, "dockerfile")
        self.assertEqual(a["level"], 1)  # L1 met by both locations; INF-D02 is a level-2 gate and fails in b/
        self.assertEqual(a["blocked_by"], ["INF-D02"])

    def test_overall_is_the_weakest_area(self):
        r = run({"Dockerfile": GOOD_DOCKERFILE, ".dockerignore": "x\n", "main.tf": self.GOOD_TF})
        lv = r["levels"]
        self.assertEqual(lv["overall"], min(a["level"] for a in lv["areas"].values()))
        self.assertEqual(lv["areas"][lv["weakest_area"]]["level"], lv["overall"])

    def test_no_infra_has_no_level(self):
        self.assertEqual(run({"app.py": "x=1\n"})["levels"], {"overall": None, "weakest_area": None, "areas": {}})


class BicepTests(unittest.TestCase):
    MAIN = "@secure()\nparam adminPassword string\nparam location string\nresource sa 'Microsoft.Storage/storageAccounts@2023-01-01' = {}\n"

    def test_good_bicep(self):
        ci = ".github/workflows/infra.yml"
        r = run(
            {
                "infra/main.bicep": self.MAIN,
                "infra/bicepconfig.json": "{}",
                "infra/main.bicepparam": "using './main.bicep'\n",
                ci: "run: az bicep build --file infra/main.bicep\nrun: az deployment group what-if\n",
            }
        )
        for cid in ("INF-B01", "INF-B02", "INF-B03", "INF-B04", "INF-B05", "INF-B06"):
            self.assertEqual(status(r, cid), "pass", cid)

    def test_bad_bicep(self):
        main = "param adminPassword string\nresource x 'Microsoft.Web/sites@2022-09-01-preview' = {}\n"
        r = run({"main.bicep": main})
        for cid in ("INF-B01", "INF-B02", "INF-B03", "INF-B04", "INF-B05", "INF-B06"):
            self.assertEqual(status(r, cid), "fail", cid)


class KubernetesTests(unittest.TestCase):
    GOOD = (
        "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\nspec:\n  template:\n    spec:\n      securityContext:\n        runAsNonRoot: true\n"
        "      containers:\n        - name: web\n          image: nginx:1.27\n          resources:\n            limits: {cpu: 1}\n"
        "          readinessProbe: {httpGet: {path: /, port: 80}}\n"
    )

    def test_good_manifest(self):
        r = run({"k8s/web.yaml": self.GOOD, ".github/workflows/k.yml": "run: kubeconform k8s/\n"})
        for cid in ("INF-K01", "INF-K02", "INF-K03", "INF-K04", "INF-K05", "INF-K06"):
            self.assertEqual(status(r, cid), "pass", cid)

    def test_bad_manifest(self):
        bad = (
            "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\nspec:\n  template:\n    spec:\n"
            "      containers:\n        - name: web\n          image: nginx\n"
            "---\napiVersion: v1\nkind: Secret\nmetadata:\n  name: s\nstringData:\n  pw: hunter2\n"
        )
        r = run({"k8s/web.yaml": bad})
        for cid in ("INF-K01", "INF-K02", "INF-K03", "INF-K04", "INF-K05", "INF-K06"):
            self.assertEqual(status(r, cid), "fail", cid)

    def test_helm_chart_needs_values_schema(self):
        r = run({"chart/Chart.yaml": "apiVersion: v2\nname: x\nversion: 0.1.0\n"})
        self.assertEqual(status(r, "INF-K07"), "fail")
        r = run({"chart/Chart.yaml": "apiVersion: v2\nname: x\nversion: 0.1.0\n", "chart/values.schema.json": "{}"})
        self.assertEqual(status(r, "INF-K07"), "pass")

    def test_levels_include_new_areas(self):
        r = run({"k8s/web.yaml": self.GOOD, "main.bicep": "param location string\n"})
        self.assertIn("kubernetes", r["levels"]["areas"])
        self.assertIn("bicep", r["levels"]["areas"])


if __name__ == "__main__":
    unittest.main()
