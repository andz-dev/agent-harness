#!/usr/bin/env python3
"""Static infrastructure detection for harness-audit (overlay, B-166..B-170).

Finds infrastructure-as-code, container and dev-environment files in a repository tree. Nothing is
executed or installed; files are only listed and, for a few ambiguous YAML/JSON names, sniffed for a
marker string. The result is reported next to the score and is NOT part of it (decision D1): the frozen
0-100 score of a repository does not change when infra files exist.

Usage: python3 -I detect_infra.py <repo-path>
Output: JSON {"kinds": [...], "detected": [...], "scored": false}
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import detect_stack  # noqa: E402

NOT_INFRA_DIRS = {".terraform", ".terragrunt-cache", ".pulumi", "cdk.out", ".serverless"}
MAX_FILES_PER_ENTRY = 20
ARCHIVE_DIRS = {"_archived", "archived", "archive", "legacy", "deprecated", "old"}
SNIFF_ALL_YAML_LIMIT = 600  # sniff every YAML file for Kubernetes markers only in repos with at most this many
SNIFF_BYTES = 4096

# (kind, tool, basename globs). Matched case-insensitively on the file's basename.
BY_NAME: list[tuple[str, str, tuple[str, ...]]] = [
    ("iac", "terraform", ("*.tf", "*.tf.json", ".terraform.lock.hcl", "*.tfvars")),
    ("iac", "opentofu", ("*.tofu",)),
    ("iac", "terragrunt", ("terragrunt.hcl",)),
    ("iac", "bicep", ("*.bicep", "*.bicepparam", "bicepconfig.json")),
    ("iac", "helm", ("chart.yaml", "chart.yml")),
    ("iac", "kustomize", ("kustomization.yaml", "kustomization.yml")),
    ("iac", "pulumi", ("pulumi.yaml", "pulumi.yml")),
    ("iac", "cdk", ("cdk.json",)),
    ("iac", "ansible", ("ansible.cfg", "playbook*.yml", "playbook*.yaml", "site.yml", "site.yaml")),
    ("container", "docker", ("dockerfile", "dockerfile.*", "*.dockerfile", "containerfile", "containerfile.*", ".dockerignore")),
    (
        "container",
        "compose",
        ("compose.yml", "compose.yaml", "compose.*.yml", "compose.*.yaml", "docker-compose*.yml", "docker-compose*.yaml"),
    ),
    ("devenv", "devcontainer", ("devcontainer.json", ".devcontainer.json")),
    ("devenv", "gitpod", (".gitpod.yml",)),
    ("devenv", "nix", ("flake.nix", "shell.nix")),
    ("devenv", "mise", ("mise.toml", ".mise.toml", ".tool-versions")),
]

# YAML/JSON names that need a content marker to count (ARM templates, CloudFormation, Kubernetes manifests).
SNIFF: list[tuple[str, str, tuple[str, ...], tuple[str, ...]]] = [
    ("iac", "arm", ("azuredeploy*.json", "maintemplate.json", "*.template.json"), ("deploymenttemplate.json",)),
    (
        "iac",
        "cloudformation",
        ("template.y*ml", "template.json", "*.template.y*ml", "cloudformation*.y*ml"),
        ("AWSTemplateFormatVersion", "AWS::"),
    ),
]
K8S_DIRS = {"k8s", "kubernetes", "manifests", "deploy", "deployment", "deployments", "kube", "base", "overlays"}


def _match(name: str, globs: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatchcase(name, g) for g in globs)


def _head(root: Path, rel: str) -> str:
    try:
        with open(root / rel, "rb") as fh:
            return fh.read(SNIFF_BYTES).decode("utf-8", "replace")
    except OSError:
        return ""


def classify(root: Path, rel: str, sniff_all: bool = False) -> tuple[str, str] | None:
    """(kind, tool) for one file, or None."""
    parts = rel.split("/")
    if any(p in NOT_INFRA_DIRS for p in parts):
        return None
    name = parts[-1].lower()
    for kind, tool, globs in BY_NAME:
        if _match(name, globs):
            if tool == "devcontainer" and name == "devcontainer.json" and ".devcontainer" not in parts[:-1] and len(parts) > 1:
                continue
            if tool == "ansible" and name in ("site.yml", "site.yaml") and "hosts:" not in _head(root, rel):
                continue
            return kind, tool
    for kind, tool, globs, markers in SNIFF:
        if _match(name, globs) and any(m.lower() in _head(root, rel).lower() for m in markers):
            return kind, tool
    if name.endswith((".yaml", ".yml")) and parts[0] != ".github" and (sniff_all or any(p.lower() in K8S_DIRS for p in parts[:-1])):
        head = _head(root, rel)
        if "apiVersion:" in head and "kind:" in head:
            return "iac", "kubernetes"
    if name == "main.yml" and "tasks" in parts[:-1] and "roles" in parts[:-2]:
        return "iac", "ansible"
    return None


def detect(root: Path) -> dict:
    entries: dict[tuple[str, str, str], list[str]] = {}
    files = detect_stack.list_files(root)
    sniff_all = sum(f.endswith((".yaml", ".yml")) for f in files) <= SNIFF_ALL_YAML_LIMIT
    for rel in files:
        hit = classify(root, rel, sniff_all)
        if not hit:
            continue
        scope = str(PurePosixPath(rel).parent)
        entries.setdefault((hit[0], hit[1], scope), []).append(rel)
    detected = []
    for (kind, tool, scope), files in sorted(entries.items()):
        sample = detect_stack.is_sample_location(scope)
        # hidden directories are normal for .devcontainer/.github; only sample directories mark examples
        is_sample = sample == "sample directory" or any(seg.lower() in ARCHIVE_DIRS for seg in scope.split("/"))
        detected.append(
            {
                "kind": kind,
                "tool": tool,
                "scope": scope,
                "file_count": len(files),
                "files": files[:MAX_FILES_PER_ENTRY],
                "sample": is_sample,
                "status": "detected-not-scored",
            }
        )
    real = [d for d in detected if not d["sample"]]
    return {
        "scored": False,
        "tools": sorted({d["tool"] for d in real}),
        "kinds": sorted({d["kind"] for d in real}),
        "detected": detected,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo")
    args = ap.parse_args(argv)
    root = Path(args.repo)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    print(json.dumps(detect(root), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
