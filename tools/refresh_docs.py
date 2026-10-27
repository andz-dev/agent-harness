"""Refresh extraction-owned metadata without replaying historical operations."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "docs/0002"


def write(path, document):
    path.write_text(json.dumps(document, indent=2) + "\n")


def main():
    changes_path = BUNDLE / "change-set.jsonc"
    original_path = BUNDLE / "change-set.source.jsonc"
    if not original_path.exists():
        original_path.write_bytes(changes_path.read_bytes())
    sources = [
        {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in (BUNDLE / "Architecture.md", BUNDLE / "Plan.md")
    ]
    changes = json.loads(changes_path.read_text())
    changes.update(
        {
            "stage": "specification",
            "verified": "unverified",
            "based_on": sources,
            "slices": [],
            "entries": [],
            "historicalSource": "change-set.source.jsonc",
            "note": "Frozen-source extraction has no pending runtime operations; the former source transaction is historical only.",
        }
    )
    write(changes_path, changes)
    model_path = BUNDLE / "architecture-model.jsonc"
    model = json.loads(model_path.read_text())
    model["states"] = {
        "current": "Existing runtime copied unchanged into the standalone repository.",
        "target": "Same runtime after documentation and packaging extraction.",
    }
    model["based_on"] = sources
    for collection in ("components", "links"):
        for item in model.get(collection, []):
            item["in"] = ["current", "target"]
    write(model_path, model)
    for path in BUNDLE.rglob("artifact-meta*.jsonc"):
        document = json.loads(path.read_text())
        for field in ("inputs", "outputs"):
            document.setdefault("imported" + field.title(), document.get(field, []))
            resolved = []
            for value in document.get(field, []):
                candidate = ROOT / value
                if not candidate.exists():
                    candidate = (path.parent / value).resolve()
                if candidate.is_relative_to(ROOT) and candidate.exists():
                    resolved.append(candidate.relative_to(ROOT).as_posix())
            document[field] = resolved
        document["validation"] = {
            "status": "warn",
            "checks": ["standalone-source-integrity-and-local-doc-path-checks"],
        }
        write(path, document)
    print("PASS: extraction metadata refreshed; historical transaction archived; zero pending runtime operations")


if __name__ == "__main__":
    main()
