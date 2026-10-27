"""Tests for scripts/detect_infra.py using synthetic trees.

Run: python3 -I tests/test_detect_infra.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import detect_infra  # noqa: E402


def detect(tree):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for rel, text in tree.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        return detect_infra.detect(root)


def tools(result):
    return {(x["tool"], x["scope"]) for x in result["detected"] if not x["sample"]}


class DetectInfraTests(unittest.TestCase):
    def test_terraform_bicep_and_lock(self):
        r = detect({"infra/main.tf": "", "infra/.terraform.lock.hcl": "", "az/main.bicep": "", "az/bicepconfig.json": "{}"})
        self.assertEqual(tools(r), {("terraform", "infra"), ("bicep", "az")})
        self.assertFalse(r["scored"])
        self.assertEqual(next(x for x in r["detected"] if x["tool"] == "terraform")["file_count"], 2)

    def test_docker_compose_devcontainer(self):
        r = detect(
            {
                "Dockerfile": "FROM python:3.12\n",
                "api/Dockerfile.dev": "",
                "compose.yaml": "services: {}\n",
                ".devcontainer/devcontainer.json": "{}",
                "other/devcontainer.json": "{}",
            }
        )
        self.assertEqual(
            tools(r),
            {("docker", "."), ("docker", "api"), ("compose", "."), ("devcontainer", ".devcontainer")},
        )

    def test_terraform_cache_dir_is_ignored(self):
        r = detect({".terraform/modules/x/main.tf": "", "main.tf": ""})
        self.assertEqual(tools(r), {("terraform", ".")})

    def test_kubernetes_manifest_needs_the_marker(self):
        r = detect(
            {
                "k8s/app.yaml": "apiVersion: apps/v1\nkind: Deployment\n",
                "k8s/notes.yaml": "foo: bar\n",
                "config/app.yaml": "apiVersion: v1\nkind: Pod\n",
            }
        )
        self.assertEqual(tools(r), {("kubernetes", "k8s"), ("kubernetes", "config")})

    def test_large_repos_only_sniff_kubernetes_directories(self):
        old = detect_infra.SNIFF_ALL_YAML_LIMIT
        detect_infra.SNIFF_ALL_YAML_LIMIT = 1
        try:
            r = detect(
                {
                    "k8s/app.yaml": "apiVersion: apps/v1\nkind: Deployment\n",
                    "config/app.yaml": "apiVersion: v1\nkind: Pod\n",
                    "other/x.yaml": "a: 1\n",
                }
            )
        finally:
            detect_infra.SNIFF_ALL_YAML_LIMIT = old
        self.assertEqual(tools(r), {("kubernetes", "k8s")})

    def test_cloudformation_and_arm_need_content_marker(self):
        r = detect(
            {
                "cf/template.yaml": "AWSTemplateFormatVersion: '2010-09-09'\n",
                "plain/template.yaml": "name: not cloudformation\n",
                "arm/azuredeploy.json": '{"$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"}',
            }
        )
        self.assertEqual(tools(r), {("cloudformation", "cf"), ("arm", "arm")})

    def test_examples_are_marked_sample_and_not_counted(self):
        r = detect({"examples/demo/main.tf": "", "Dockerfile": ""})
        self.assertEqual(r["tools"], ["docker"])
        self.assertTrue(next(x for x in r["detected"] if x["tool"] == "terraform")["sample"])

    def test_kubernetes_manifest_anywhere_in_a_small_repo(self):
        r = detect({"guestbook/frontend.yaml": "apiVersion: apps/v1\nkind: Deployment\n", "guestbook/notes.yaml": "a: 1\n"})
        self.assertEqual(tools(r), {("kubernetes", "guestbook")})

    def test_archived_directories_are_samples(self):
        r = detect({"_archived/old/main.tf": "", "main.tf": ""})
        self.assertEqual(tools(r), {("terraform", ".")})

    def test_ansible_site_needs_hosts(self):
        r = detect(
            {"a/site.yml": "- hosts: all\n  tasks: []\n", "b/site.yml": "title: docs\n", "roles/web/tasks/main.yml": "- debug: {}\n"}
        )
        self.assertEqual(tools(r), {("ansible", "a"), ("ansible", "roles/web/tasks")})

    def test_no_infra(self):
        r = detect({"src/app.py": "print(1)\n"})
        self.assertEqual(r["detected"], [])


if __name__ == "__main__":
    unittest.main()
