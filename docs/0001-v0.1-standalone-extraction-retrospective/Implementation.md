---
type: 'Implementation'
id: '0001'
version: 'v0.1'
title: 'Standalone Extraction: Recorded Implementation'
description: 'Commit-backed extraction outcomes with explicit historical verification limits.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:23251df', 'git:7228905', 'EXTRACTION.md']
---

# Standalone Extraction: Recorded Implementation

## Recorded Outcomes

- [x] `23251df` introduces the standalone skill, city, provenance and documentation layout.
- [x] The original zero-byte `.gitkeep` remains present.
- [x] `7228905` subsequently expands the synthetic demonstration across all city tiers.
- [x] Original included/excluded categories are recorded in [EXTRACTION.md](../../EXTRACTION.md).

These checkboxes record source/commit evidence, not a new replay of the extraction.
The provenance document's 137-test and browser observations are historical statements;
this retrospective does not claim to have rerun that old environment.

## Phase Detail

### Phase 1: Import and provenance (AC-1, AC-2, AC-4, AC-6)

Objective: record that the snapshot, manifest and checks exist as of `23251df`.
Read first: [Plan](Plan.md), [EXTRACTION.md](../../EXTRACTION.md), `extraction-manifest.json`.
Constraints: keep source hashes and the empty `.gitkeep`; import no excluded category.
Validate: `python3 tools/check.py --integrity-only`
Stop when: the command exits 0 and `git show 23251df --stat` lists the skill, city,
manifest, checks and CI file.

- [x] `git ls-tree -r --name-only 23251df` lists `extraction-manifest.json`, `tools/check.py`,
  `Taskfile.yml` and `.github/workflows/check.yml`.
- [x] The commit tree contains no Dockerfile, compose or devcontainer file.

### Phase 2: Synthetic demonstration (AC-3)

Objective: record the demo expansion at `7228905`.
Read first: [Architecture](Architecture.md) section Data and Storage.
Constraints: no fabricated findings; demo only.
Validate: `python3 tools/check.py`
Stop when: the demo check passes in the current tree and the commit message names the
four-tier expansion.

- [x] Commit `7228905` follows `23251df`.
- [ ] A current run of the demo check is `Not recorded` by this folder.

### Phase 3: Provenance upkeep (AC-5)

Objective: explain how later changes stay verifiable.
Read first: `extraction-manifest.json` kinds `unchanged-source` and `adapted-runtime`.
Constraints: re-baseline only deliberately; never edit `source_sha256`.
Validate: `python3 tools/check.py --integrity-only`
Stop when: every `adapted-runtime` target matches its recorded `sha256`.

- [x] The integrity function compares `adapted-runtime` files to `sha256`.

## Acceptance Criteria Traceability

| Criterion | Phase | Evidence |
| --- | --- | --- |
| AC-1 | 1 | manifest and `task integrity` |
| AC-2 | 1 | Excluded list and publication check |
| AC-3 | 2 | `7228905` and the demo check |
| AC-4 | 1 | `Taskfile.yml` and the CI file |
| AC-5 | 3 | `adapted-runtime` handling in `tools/check.py` |
| AC-6 | 1 | the docs check on `.gitkeep` |

## Decision Log

| Decision | Basis |
| --- | --- |
| Treat historical pass counts as historical | `EXTRACTION.md` says they are not new results |
| Mark network edges from the commit tree | `build_standalone.py` references a CDN; recorded in [Architecture](Architecture.md) |
| Leave unrecorded items as `Not recorded` | no session or CI log for the first push exists in this tree |

## Resume State

- Current phase: none open; this folder is a finished retrospective.
- Last verified: the commit-tree searches above, run when this document was deepened.
- Open items: remote CI result for the first push; CDN integrity attribute.
- Next step: run Phase 1 `validate:` before relying on any provenance statement.

## Final Verification

Run `python3 tools/check.py`. It passes when integrity, docs, synthetic data and publication
checks pass. The result describes the current tree only.

## Verification Contract

Objective: verify the current adaptation's integrity, not re-execute old monorepo actions.
Read first: [Plan](Plan.md), [Architecture](Architecture.md), extraction provenance.
Constraints: preserve original pins and notices; no source retirement, deployment or
private dataset import.
Validate: `task integrity` and `python3 tools/check.py`.
Stop when: current integrity/publication checks pass or a specific mismatch is disclosed.

## Handoff

The original reserved slot is now used for this owner-requested retrospective only.
Do not treat that as authorization to rerun extraction or destructive source operations.
Later work is recorded in 0003 onward and the [history crosswalk](../History-Match.md).