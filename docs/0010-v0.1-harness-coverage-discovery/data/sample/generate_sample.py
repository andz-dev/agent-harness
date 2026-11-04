#!/usr/bin/env python3
"""Generate synthetic assurance edge cases; no real repository values are copied."""

import argparse
import logging
from pathlib import Path
import sys

BUNDLE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BUNDLE / "scripts"))
from probe import discovery_log, sample_data

LOGGER = logging.getLogger("sample")
SEED = 20261104
EDGES = [
    {"label": "unknown_stays_unknown", "assurance": "static_only", "runtime_status": "unknown", "expected_valid": True},
    {"label": "declared_is_not_verified", "assurance": "static_only", "runtime_status": "verified", "expected_valid": False},
    {"label": "absent_status_is_not_assurance", "assurance": "static_only", "runtime_status": None, "expected_valid": False},
]


def make_record(rng, index):
    status = rng.choice(["unknown", "verified", "not_applicable"])
    return {"label": f"seeded_{index}", "assurance": "static_only", "runtime_status": status,
            "expected_valid": status == "unknown"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with discovery_log.open_run("sample", sys.argv[1:], log_dir=BUNDLE / "logs", logger=LOGGER):
        operation = sample_data.check_sample if args.check else sample_data.write_sample
        operation(Path(__file__).parent, make_record, EDGES, seed=SEED, count=4,
                  generator="data/sample/generate_sample.py")
        if not args.check:
            discovery_log.record(LOGGER, "sample.generated", grade="synthetic", records=len(EDGES) + 4)
        print("sample check ok" if args.check else "sample generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
