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
        self.assertEqual({f["status"] for f in r["findings"] if f["area"] == "compose"}, {"not_applicable"})


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
            {"findings": [], "summary": {}, "rollup": [], "levels": {"overall": None, "weakest_area": None, "repo_wide": {}, "areas": {}}},
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

    def test_overall_is_the_weakest_tool_area_and_repo_wide_areas_are_separate(self):
        r = run({"Dockerfile": GOOD_DOCKERFILE, ".dockerignore": "x\n", "main.tf": self.GOOD_TF})
        lv = r["levels"]
        tools = {a: v["level"] for a, v in lv["areas"].items() if a not in ("cross-cutting", "agent-guidance")}
        self.assertEqual(lv["overall"], min(tools.values()))
        self.assertEqual(lv["areas"][lv["weakest_area"]]["level"], lv["overall"])
        self.assertEqual(lv["repo_wide"], {k: lv["areas"][k]["level"] for k in lv["repo_wide"]})

    def test_a_missing_secret_scanner_does_not_pull_down_the_tool_level(self):
        ci = ".github/workflows/ci.yml"
        tree = {"Dockerfile": GOOD_DOCKERFILE, ".dockerignore": "x\n", ci: "run: hadolint Dockerfile\nrun: docker build .\n"}
        lv = run(tree)["levels"]
        self.assertEqual(lv["overall"], 3)
        self.assertEqual(lv["repo_wide"]["cross-cutting"], 1)  # the L1 gate INF-X05 passes; the L2 checks (scanner, CODEOWNERS ...) fail

    def test_no_infra_has_no_level(self):
        self.assertEqual(run({"app.py": "x=1\n"})["levels"], {"overall": None, "weakest_area": None, "repo_wide": {}, "areas": {}})


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


class BicepParentConfigTests(unittest.TestCase):
    def test_bicepconfig_in_a_parent_directory_counts(self):
        r = run({"infra/bicepconfig.json": "{}", "infra/app/main.bicep": "param x string\n"})
        self.assertEqual(status(r, "INF-B01"), "pass")


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


class AnsibleTests(unittest.TestCase):
    def test_good_ansible(self):
        r = run(
            {
                "ansible.cfg": "[defaults]\n",
                "requirements.yml": "collections:\n  - name: community.general\n    version: 8.0.0\n",
                "site.yml": "- hosts: all\n  vars:\n    db_password: !vault |\n      $ANSIBLE_VAULT\n",
                ".ansible-lint": "profile: production\n",
                ".github/workflows/a.yml": "run: ansible-playbook site.yml --syntax-check\n",
            }
        )
        for cid in ("INF-A01", "INF-A02", "INF-A03", "INF-A04"):
            self.assertEqual(status(r, cid), "pass", cid)

    def test_bad_ansible(self):
        r = run({"site.yml": "- hosts: all\n  vars:\n    api_token: abc123\n"})
        for cid in ("INF-A01", "INF-A02", "INF-A03", "INF-A04"):
            self.assertEqual(status(r, cid), "fail", cid)


class CloudFormationTests(unittest.TestCase):
    CF = "AWSTemplateFormatVersion: '2010-09-09'\nParameters:\n  DbPassword:\n    Type: String\n"

    def test_missing_noecho_fails(self):
        r = run({"cf/template.yaml": self.CF})
        self.assertEqual(status(r, "INF-F03"), "fail")
        self.assertEqual(status(r, "INF-F01"), "fail")
        self.assertEqual(status(r, "INF-F02"), "fail")

    def test_good_cloudformation(self):
        cf = self.CF + "    NoEcho: true\n"
        r = run({"cf/template.yaml": cf, ".cfnlintrc": "", ".github/workflows/c.yml": "run: aws cloudformation validate-template\n"})
        for cid in ("INF-F01", "INF-F02", "INF-F03"):
            self.assertEqual(status(r, cid), "pass", cid)


class PulumiTests(unittest.TestCase):
    def test_plaintext_secret_and_missing_lock_fail(self):
        r = run({"Pulumi.yaml": "name: x\nruntime: nodejs\n", "Pulumi.dev.yaml": "config:\n  app:dbPassword: hunter2\n"})
        self.assertEqual(status(r, "INF-P01"), "fail")
        self.assertEqual(status(r, "INF-P02"), "fail")
        self.assertEqual(status(r, "INF-P03"), "fail")

    def test_encrypted_secret_passes(self):
        r = run(
            {
                "Pulumi.yaml": "name: x\nruntime: nodejs\n",
                "package-lock.json": "{}",
                "Pulumi.dev.yaml": "config:\n  app:dbPassword:\n    secure: AAABB\n",
                ".github/workflows/p.yml": "uses: pulumi/actions@v5\n",
            }
        )
        for cid in ("INF-P01", "INF-P02", "INF-P03"):
            self.assertEqual(status(r, cid), "pass", cid)


class CrossCuttingTests(unittest.TestCase):
    def test_nothing_configured_fails(self):
        r = run({"main.tf": "", "Dockerfile": "FROM x:1\n"})
        self.assertEqual(status(r, "INF-X01"), "fail")
        self.assertEqual(status(r, "INF-X02"), "fail")
        self.assertEqual(status(r, "INF-X03"), "fail")
        self.assertEqual(status(r, "INF-X04"), "fail")
        self.assertEqual(status(r, "INF-X05"), "pass")

    def test_dependabot_must_list_each_ecosystem(self):
        dep = 'updates:\n  - package-ecosystem: "docker"\n    directory: /\n'
        r = run({"main.tf": "", "Dockerfile": "FROM x:1\n", ".github/dependabot.yml": dep})
        f = next(x for x in r["findings"] if x["check_id"] == "INF-X01")
        self.assertEqual(f["status"], "fail")
        self.assertEqual([e["snippet"] for e in f["evidence"]], ["missing ecosystem: terraform"])
        dep += "  - package-ecosystem: terraform\n    directory: /\n"
        self.assertEqual(status(run({"main.tf": "", "Dockerfile": "FROM x:1\n", ".github/dependabot.yml": dep}), "INF-X01"), "pass")

    def test_codeowners_path_filter_scanner_and_tracked_keys(self):
        tree = {
            "infra/main.tf": "",
            ".github/CODEOWNERS": "/infra/ @platform-team\n",
            ".github/workflows/tf.yml": "on:\n  push:\n    paths:\n      - 'infra/**'\n",
            ".gitleaks.toml": "",
            "deploy/server.pem": "x",
        }
        r = run(tree)
        self.assertEqual(status(r, "INF-X02"), "pass")
        self.assertEqual(status(r, "INF-X03"), "pass")
        self.assertEqual(status(r, "INF-X04"), "pass")
        self.assertEqual(status(r, "INF-X05"), "fail")

    def test_env_with_only_secret_manager_references_is_not_a_leak(self):
        refs = 'export TOKEN="op://vault/item/field"\nDB=${DB_URL}\n'
        self.assertEqual(status(run({"main.tf": "", "deploy/.env": refs}), "INF-X05"), "pass")
        self.assertEqual(status(run({"main.tf": "", "deploy/.env": "TOKEN=abc123\n"}), "INF-X05"), "fail")

    def test_not_run_without_infra(self):
        self.assertEqual([f for f in run({"app.py": "x=1\n"})["findings"]], [])


class InfraEntropyTests(unittest.TestCase):
    def test_unreferenced_dockerfile_is_flagged(self):
        tree = {
            "web/Dockerfile": "FROM x:1\n",
            "misc/Dockerfile": "FROM x:1\n",
            "compose.yaml": "services:\n  web:\n    build:\n      context: ./web\n",
        }
        r = run(tree)
        f = next(x for x in r["findings"] if x["check_id"] == "INF-E01")
        self.assertEqual(f["status"], "fail")
        self.assertEqual([e["path"] for e in f["evidence"]], ["misc/Dockerfile"])

    def test_root_dockerfile_used_by_ci_build(self):
        r = run({"Dockerfile": "FROM x:1\n", ".github/workflows/b.yml": "run: docker build .\n"})
        self.assertEqual(status(r, "INF-E01"), "pass")

    def test_unused_terraform_variable_and_loose_module(self):
        tree = {
            "main.tf": 'variable "used" {}\nvariable "dead" {}\nmodule "a" { source = "./modules/a" }\nresource "x" "y" { n = var.used }\n',
            "modules/a/main.tf": "",
            "modules/b/main.tf": "",
        }
        r = run(tree)
        e2 = next(x for x in r["findings"] if x["check_id"] == "INF-E02")
        self.assertEqual(e2["status"], "fail")
        self.assertIn("dead", e2["evidence"][0]["snippet"])
        e3 = next(x for x in r["findings"] if x["check_id"] == "INF-E03")
        self.assertEqual([e["path"] for e in e3["evidence"]], ["modules/b/"])

    def test_entropy_is_reported_beside_not_inside_the_tool_level(self):
        tree = {"misc/Dockerfile": "FROM x:1\n"}
        lv = run(tree)["levels"]
        self.assertIn("infra-entropy", lv["repo_wide"])
        self.assertNotEqual(lv["weakest_area"], "infra-entropy")


if __name__ == "__main__":
    unittest.main()
