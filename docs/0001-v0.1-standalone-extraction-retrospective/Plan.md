---
type: 'Plan'
id: '0001'
version: 'v0.1'
title: 'Standalone Extraction: Retrospective Plan'
description: 'Evidence-derived acceptance boundaries for the initial standalone snapshot.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['EXTRACTION.md', 'git:23251df', 'docs/0001-v0.1-standalone-extraction-retrospective/Ideation-Book.md']
---

# Standalone Extraction: Retrospective Plan

## Acceptance Boundaries

| ID | Observable requirement reconstructed from the extraction |
| --- | --- |
| E-1 | Included skill/runtime/assets have explicit source-to-target provenance and hashes. |
| E-2 | Private reports, original datasets, secrets, environments and generated bundles are excluded. |
| E-3 | Synthetic city examples are distinguished from real audit findings. |
| E-4 | Existing code remains usable through local setup/check/build entry points. |

## Scope and Sequence

In scope: the initial snapshot at commit `23251df` and the synthetic-demo expansion at
`7228905`. Out of scope: audit v1.2, the infrastructure overlay, calibration and the airport
work, which later folders record, and any claim about the source monorepo's own history.

The recorded sequence is extraction, provenance/packaging, synthetic demonstration and
standalone checks. Later city changes, audit v1.2 and new quality tooling are not
retroactively attributed to the initial snapshot.

## Acceptance Criteria (Given/When/Then)

These restate E-1 to E-4 as observable checks against the current tree. They describe what
the extraction promised, not a replay of the old run.

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-1 (E-1) | the manifest lists each copied file with a source path and checksum | `python3 tools/check.py --integrity-only` runs | it passes, or names the mismatched target |
| AC-2 (E-2) | the Excluded list in `EXTRACTION.md` | the publication check scans tracked and untracked files | no private path, credential-shaped string or tracked report is found |
| AC-3 (E-3) | `apps/harness-city/data/cities.json` | the demo check runs | it requires synthetic provenance, four distinct cities and levels L0 to L3 |
| AC-4 (E-4) | a clean checkout | `task setup` then `task check` run | both complete without the source monorepo |
| AC-5 (edge) | a copied runtime file was intentionally changed | the integrity check runs | it compares against the recorded `sha256`, not `source_sha256`, for `adapted-runtime` entries |
| AC-6 (negative) | `docs/0001-v0.1-standalone-extraction-retrospective/.gitkeep` is missing or non-empty | the docs check runs | it fails with a message naming the file |

## Assumptions

- The source commit `c3e1120` and tree `e5c34a5` are recorded in `EXTRACTION.md` and are not
  fetched here. Source commits are provenance, not objects in this repository.
- Pattern checks catch common leaks only; they are not a security review.
- The 137-test result and the browser observations in `EXTRACTION.md` are historical
  statements and are not repeated by this folder.

## Milestones and Delivery Slices

| Slice | Evidence | Outcome |
| --- | --- | --- |
| M1 Import | commit `23251df` | skill, city, manifest, checks, CI and relocated 0002 records |
| M2 Demo | commit `7228905` | synthetic profiles across all four tiers |
| M3 Provenance upkeep | `adapted-runtime` entries in the manifest | reviewed baselines for later changes |

Each slice maps to at least one acceptance criterion: M1 to AC-1, AC-2, AC-4 and AC-6; M2 to
AC-3; M3 to AC-5.

## Risks and Mitigations

| Risk | Mitigation recorded in the tree |
| --- | --- |
| A later edit silently changes a hash-pinned file | integrity check fails until the manifest is deliberately re-baselined |
| Historical results are read as current | each statement here is labeled historical or current |
| The empty scaffold is removed | `tools/check.py` requires it to exist and be empty |

## Validation Contract

Objective: preserve the snapshot's traceability without replaying source operations.
Read first: [provenance](../../EXTRACTION.md), [Architecture](Architecture.md).
Constraints: retain source hashes, license notices and the empty scaffold; never execute
untrusted audited code or import excluded source data.
Validate: `task integrity` and `python3 tools/check.py` validate the current adaptation.
Stop when: provenance and current integrity agree, with historical results still labeled
as historical rather than newly executed by this retrospective.

## Open Limits

Original source operations and historical remote CI are not reproduced here. Current
runtime verification belongs to the current implementation gate, not to an invented
initial test session. See [Implementation](Implementation.md).

## Open Questions

- Which remote CI result belongs to the first push? `Not recorded` in this tree.
- Should the standalone build's CDN import map carry an integrity attribute? Not decided.