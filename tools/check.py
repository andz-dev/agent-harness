"""Check extraction integrity, safe demo data and portable documentation."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", "dist", "build"}


def integrity(root):
    manifest = json.loads((root / "extraction-manifest.json").read_text())
    failures = []
    for record in manifest["files"]:
        if record["kind"] not in ("unchanged-source", "adapted-runtime"):
            continue
        # adapted-runtime: a reviewed, intentional change; verify against the new baseline
        expected = record["source_sha256"] if record["kind"] == "unchanged-source" else record["sha256"]
        path = root / record["target"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append("Source checksum mismatch: " + record["target"])
    return failures


def documents(root):
    failures = []
    scaffold = root / "docs/0001/.gitkeep"
    if not scaffold.is_file() or scaffold.stat().st_size != 0:
        failures.append("docs/0001/.gitkeep must exist and be empty")
    for path in root.rglob("*.md"):
        if SKIP.intersection(path.relative_to(root).parts):
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root).as_posix()
        if not text.startswith("---\n") or not re.search(r"^type:", text.split("---", 2)[1], re.MULTILINE):
            failures.append(relative + ": missing type frontmatter")
        visible = re.sub(r"```[\s\S]*?```", "", text)
        for raw in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", visible):
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(root) or not destination.exists():
                failures.append(relative + ": broken local link " + raw)
    for path in (root / "docs/0002").rglob("*.jsonc"):
        try:
            text = re.sub(r"^\s*//.*$", "", path.read_text(), flags=re.MULTILINE)
            json.loads(text)
        except ValueError:
            failures.append(str(path.relative_to(root)) + ": invalid JSONC")
    for name in ("architecture-model.jsonc", "change-set.jsonc"):
        path = root / "docs/0002" / name
        document = json.loads(path.read_text())
        for source in document.get("based_on", []):
            original = root / source["path"]
            if not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest() != source["sha256"]:
                failures.append(name + ": stale source hash " + source["path"])
        if name == "change-set.jsonc" and document.get("entries"):
            failures.append("Imported historical removals must not remain active operations")
    return failures


def demo(root):
    path = root / "apps/harness-city/data/cities.json"
    if not path.is_file():
        return ["Synthetic city dataset is missing"]
    document = json.loads(path.read_text())
    failures = []
    if "synthetic" not in document["meta"].get("source", "").lower():
        failures.append("Demo provenance must explicitly say synthetic")
    cities = document.get("cities", [])
    if len(cities) != 4 or len({city["id"] for city in cities}) != 4:
        failures.append("Expected four distinct synthetic demo cities")
    tiers = {sum(city["score"] >= threshold for threshold in (45, 60, 80)) for city in cities}
    if tiers != {0, 1, 2, 3}:
        failures.append("Synthetic demo must show Neglected, Working, Prosperous and Thriving cities")
    if {level for city in cities for level in city["L"]} != {0, 1, 2, 3}:
        failures.append("Synthetic demo must include district levels L0 through L3")
    for city in cities:
        if len(city["L"]) != 7 or any(level not in (0, 1, 2, 3) for level in city["L"]):
            failures.append("Invalid demo pillar levels")
        if not city["id"].endswith("-demo"):
            failures.append("Demo identifiers must be explicitly fictional")
    return failures


def publication(root):
    failures = []
    output = subprocess.check_output(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"]).decode()
    names = sorted(set(filter(None, output.split("\0"))))
    private = re.compile(r"/(?:home|Users)/[^/\s]+|https?://[^/\s]+:[^@\s]+@|https?://dev\.azure\.com/", re.IGNORECASE)
    secret = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)")
    for name in names:
        path = root / name
        if not path.is_file():
            continue
        if path.is_symlink():
            failures.append("Publication must not include symlinks: " + name)
            continue
        if any(part in {"dist", "reports", ".venv", ".data", "logs"} for part in Path(name).parts):
            failures.append("Generated/private output is tracked: " + name)
        if path.suffix.lower() not in {
            ".py",
            ".md",
            ".json",
            ".jsonc",
            ".yaml",
            ".yml",
            ".html",
            ".js",
            ".mjs",
            ".txt",
            ".sh",
            ".toml",
            ".lock",
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if name != "tools/check.py" and private.search(text):
            failures.append("Private-source marker requires review: " + name)
        if secret.search(text):
            failures.append("Credential-shaped content requires review: " + name)
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--integrity-only", action="store_true")
    arguments = parser.parse_args()
    failures = integrity(ROOT)
    if not arguments.integrity_only:
        failures += documents(ROOT) + demo(ROOT) + publication(ROOT)
    for failure in failures:
        print("FAIL: " + failure)
    if failures:
        return 1
    print("PASS: extraction integrity" + ("" if arguments.integrity_only else ", docs, synthetic data and publication checks"))
    print("LIMIT: pattern checks do not certify absence of all sensitive information")
    return 0


if __name__ == "__main__":
    sys.exit(main())
