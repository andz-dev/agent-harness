#!/usr/bin/env python3
"""Measure the frozen coverage question against real inputs and independent cases."""

import argparse
from copy import deepcopy
import hashlib
import json
import logging
from pathlib import Path
import sys
import time

BUNDLE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUNDLE / "scripts"))
from probe import (
    allowed_path, assurance_valid, comparison, discovery_log, hypothesis,
    inventory, measure, sample_data,
)

QUESTION = "Can a read-only repository coverage inventory distinguish shipped checks, declarations and missing report-to-city evidence across seven harness topics without treating unknown coverage as assurance?"
RESULT = BUNDLE / "spike/result.json"
LOGGER = logging.getLogger("spike")


def outputs():
    state, _ = hypothesis.frozen_status(BUNDLE)
    if state != "ok":
        raise ValueError(state)
    card, sources, cases, observed = measure()
    if card["question"] != QUESTION:
        raise ValueError("question_differs_from_card")
    sample_path = BUNDLE / "data/sample/sample.json"
    sample_bytes = sample_path.read_bytes()
    provenance = json.loads((BUNDLE / "data/sample/provenance.json").read_text())
    grade = sample_data.validate_provenance(provenance, sample_bytes)
    records = json.loads(sample_bytes)
    rows = inventory(cases, observed, sources)
    corrupt = dict(observed)
    corrupt["core_count"] = -1
    promoted = deepcopy(rows)
    promoted[0]["runtime_status"] = "verified"
    rejected = False
    try:
        allowed_path("../outside-discovery-control", card["evidence"]["real_inputs"])
    except ValueError:
        rejected = True
    synthetic_mismatches = sum(assurance_valid([record]) != record["expected_valid"] for record in records)
    answer = {
        "topics": len({case["topic"] for case in cases}),
        "discriminating_cases": len(cases),
        "mismatches": len(comparison(cases, observed)) + synthetic_mismatches,
        "unsafe_reads": sum(relative not in card["evidence"]["real_inputs"] for relative in sources),
        "unsupported_assurance": sum(not assurance_valid([row]) for row in rows),
        "oracle_controls": {
            "corrupt_fact_detected": "core_count" in comparison(cases, corrupt),
            "unknown_promotion_detected": not assurance_valid(promoted),
            "path_escape_rejected": rejected,
        },
        "real_files": len(sources),
        "synthetic_edge_cases": len(records),
        "mismatched_case_ids": comparison(cases, observed),
    }
    lock = json.loads((BUNDLE / "hypothesis.lock.json").read_text())
    result = {
        "schema": "discovery-spike-result/1", "question": QUESTION, "answer": answer,
        "grade": grade, "sample_sha256": sample_data.digest(sample_bytes),
        "skill_version": discovery_log.SKILL_VERSION, "hypothesis_sha256": lock["sha256"],
        "oracle_sha256": hashlib.sha256((BUNDLE / "data/oracle.json").read_bytes()).hexdigest(),
        "evidence": [{"grade": "real", "input": relative} for relative in sources]
                    + [{"grade": "synthetic", "input": "data/sample/sample.json"}],
        "source_sha256": {relative: hashlib.sha256(text.encode()).hexdigest() for relative, text in sources.items()},
        "limits": [
            "Case kinds were manually curated before spike implementation, not inferred by a new production classifier.",
            "Title searches measure only explicit core catalog titles, not exhaustive absence of all related heuristics.",
            "No repository code was imported or executed; git ls-files was used solely for tracked-input verification.",
            "The unsafe-read metric describes this fixed allowlist reader, not a system-wide security audit.",
        ],
    }
    return sample_data.dumps(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-q", "--quiet", action="count", default=0)
    args = parser.parse_args()
    with discovery_log.open_run("spike", sys.argv[1:], log_dir=BUNDLE / "logs", logger=LOGGER):
        started = time.monotonic()
        data = outputs()
        if args.check:
            if not RESULT.is_file() or RESULT.read_bytes() != data:
                print("spike check failed: result differs")
                return 1
            print("spike check ok")
            return 0
        sample_data.replace_file(RESULT, data)
        discovery_log.record(LOGGER, "spike.done", seconds=round(time.monotonic() - started, 3))
        print("spike result written")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
