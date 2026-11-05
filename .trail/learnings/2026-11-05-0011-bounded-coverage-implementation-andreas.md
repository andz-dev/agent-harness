---
type: 'Learning'
title: 0011 bounded coverage implementation
author: Andreas
date: 2026-11-05
branch: main
touches:
  - docs/0011-v0.1-harness-coverage-expansion/Architecture.md
  - docs/0011-v0.1-harness-coverage-expansion/Implementation.md
  - extraction-manifest.json
  - skills/harness-audit/README.md
  - skills/harness-audit/SKILL.md
  - skills/harness-audit/checks/coverage-topics.yaml
  - skills/harness-audit/pyproject.toml
  - skills/harness-audit/schema/report.schema.json
  - skills/harness-audit/scripts/audit.py
  - skills/harness-audit/scripts/coverage.py
---

## Decided
- Keep the scored core unchanged; represent quality availability separately from the unscored coverage envelope.
- Treat local receipts as unverified, and build observations only from tracked, bounded, digest-only sources selected by the seven-topic catalog.
- Update extraction-manifest adapted-runtime hashes for intentional imported snapshot changes; preserve original source hashes.

## Tried and ruled out
- Broad package.json/pyproject locators falsely imply testing evidence; use test-specific paths/configs for the testing topic.
- Do not promote self-claimed receipt success to execution_observed or include raw receipt fields in results/logs.

## Watch out
- M3.3 applicability/evidence state matrix and M3.4 runner traversal remain open; current report collection must retain its partial limitation.
- Root task check timed out in Playwright after 21 passes, 5 skips, and 2 tests not run. Precommit is blocked only by the pre-existing Trail learning missing type frontmatter.
