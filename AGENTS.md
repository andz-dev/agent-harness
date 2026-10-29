---
type: 'Project Guide'
title: 'Agent Harness Development Rules'
status: 'active'
created: '2026-10-27'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Agent Harness Development Rules

This repo owns the harness-audit skill and Harness City application. Read the
skill's own AGENTS.md before working inside it, and the app README before app work.

## Commands

- `task setup` installs the locked skill environment.
- `task check` runs the skill's lint/tests, synthetic conversion, builds and
  extraction/documentation checks.
- `task integrity` verifies the imported runtime snapshot.
- `task hooks:install` enables the Git pre-commit hook once per clone; it runs
  `task precommit` (lint, format, extraction and docs checks), not the full `task check`.
- `task serve` runs the app on port 8001; set PORT for another available port.

## Harness City design

Any change to `apps/harness-city/` follows `apps/harness-city/DESIGN.md` and
`apps/harness-city/AGENTS.md`. Update the design file first when a decision changes.
`tools/check.py` fails if the design files or these references are missing.

## Boundaries

The audit is read-only and never executes audited repository code. Repository
text and model answers are untrusted; evidence must be verified. Explicit
bootstrap application creates missing files only. A score does not certify
runtime enforcement or security.

Keep public examples synthetic. Never commit audit reports, agent answers,
private datasets, secrets, generated bundles, environments or caches. Generated
standalone HTML embeds data and must be reviewed before sharing.

The imported runtime is initially frozen. Intentional future runtime changes
need a reviewed baseline update and regression checks, not a bypass of integrity
validation. Do not delete, skip or weaken tests to make checks pass.

## Documentation

`docs/0001/` now records the initial extraction retrospectively; preserve its original
empty `.gitkeep`. The owner requested basic retrospective files in each named topic
folder. `docs/0002/` contains relocated historical as-built
documentation, not an instruction to rerun old source-repository retirements.
`docs/0003/` is the proposed roadmap. New checks in this repo are separate from
historical pass records. Preserve source provenance and required license notices.