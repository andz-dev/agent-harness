---
type: 'History Reconciliation'
title: 'Requested Documentation Folders and Git History'
description: 'File-level reconciliation of folders 0001, 0003, 0004, 0005, 0006 and 0007 with local commits.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
stale_after: '2026-11-11'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [documentation, history, provenance]
sources:
  - 'Path-specific local Git history for docs/0001 and docs/0003 through docs/0007, inspected 2026-10-28'
  - 'Current documents in those six folders, inspected 2026-10-28'
---

# Requested Documentation Folders and Git History

## Scope and Method

This crosswalk covers exactly the requested folders: 0001, 0003, 0004, 0005, 0006
and 0007. The newer 0008 retrospective does not replace them. Folder numbers record
topics and chronology, not stages of a single original spec workflow.

Matches come from `git log --reverse --name-status -- <folder>` and the documents'
contents. A commit proves a recorded source change, not a historical test pass or
an independently reproduced calibration. Original evidence is retained under the owner's
`research/` layout; relative links and manifest targets follow those moves. Following
the owner's clarification, all six folders now contain new basic
retrospective files. The initially reserved 0001 is used for the initial extraction,
under delegated routine decisions, while its original zero-byte `.gitkeep` is preserved.
The [per-folder navigation matrix](README.md#per-folder-basic-sets) links all 24 files.

## Folder Match

| Folder | Git anchor | Document role | Reconciled status |
| --- | --- | --- | --- |
| [0001](0001/) | `23251df` | Initial extraction; originally reserved scaffold | New retrospective set grounded in extraction provenance, not claimed as original specs |
| [0003](0003/research/README.md) | `23251df` | Owner roadmap copied during extraction | Historical proposals; later implementation must be matched per item |
| [0004](0004/research/README.md) | `7fddcc3`, `b470917` | v1.2 release and agreement records | Historical implementation/evaluation evidence, not a current full acceptance gate |
| [0005](0005/research/README.md) | `3106ad5` through `12c28e8` | Infrastructure coverage and backlog map | Mixed: later commits implement substantial detection/check/level work; remaining plans stay proposals |
| [0006](0006/research/README.md) | `2146078` | Infrastructure-level calibration page and sidecar | Historical single-rater evaluation and related rule changes, with stated limits |
| [0007](0007/research/airport-assets.md) | `3bfdf2b` through `90e9a52` | Airport evaluation and evolving city metaphor | Implemented opt-in prototype; current support/transport choices supersede earlier variants where stated |

## File Match

All commit dates below are 2026-10-27 unless the row names `90e9a52`, dated
2026-10-28. These are local abbreviated commit IDs; no source-repository prehistory
is inferred before the standalone extraction.

This table describes the 12 original tracked files and one generated local file. Links
point to their current locations; the first/latest commit columns describe their historical
paths before the research-folder move. The 24 newly authored retrospective files are
separate additions; their source commits are cited inside them, not falsely recorded
as their creation commits. The original empty scaffold remains at its original path.

| File | Introduced | Latest path change at this review | Interpretation |
| --- | --- | --- | --- |
| [0001 scaffold](0001/.gitkeep) | `23251df` | `23251df` | Reserved empty file, not a spec artifact |
| [0003 index](0003/research/README.md) | `23251df` | `23251df` | Warns that roadmap claims are historical and proposed |
| [Roadmap](0003/research/Repo%20Harness%20Next%20Steps.md) | `23251df` | `23251df` | Preserved owner-provided body; do not silently tick its open decisions |
| [0004 index](0004/research/README.md) | `7fddcc3` | `7fddcc3` | Points to v1.2 records and the earlier roadmap |
| [v1.2 release notes](0004/research/Release-Notes-v1.2.md) | `7fddcc3` | `7fddcc3` | Release-time behavior, verification and limitations |
| [v1.2 agreement report](0004/research/Agreement-Report-v1.2.md) | `7fddcc3` | `b470917` | Updated second agreement run; not a new experiment in this reconciliation |
| [0005 index](0005/research/README.md) | `3106ad5` | `3106ad5` | Original blanket proposal-only wording became stale as implementation followed |
| [Infrastructure coverage map](0005/research/Infrastructure-Coverage-Map.md) | `3106ad5` | `12c28e8` | Incrementally updated alongside infrastructure implementation |
| [0006 index and results](0006/research/README.md) | `2146078` | `2146078` | Documents B-215 changes and explicitly limited calibration results |
| [Calibration configurator](0006/research/infra-level-vote.html) | `2146078` | `2146078` | Intentionally tracked evaluation tool, not the current generated city bundle |
| [Calibration sidecar](0006/research/infra-levels-evaluation.json) | `2146078` | `2146078` | Historical ratings intentionally committed at owner request; do not rewrite as synthetic data |
| [Airport asset decisions](0007/research/airport-assets.md) | `3bfdf2b` | `90e9a52` | Proposal developed into the real-city opt-in prototype and later support-facility rules |
| [Local airport simulator](0007/research/city-airport-prototype.html) | No tracked introduction at this path | Untracked generated output | Derived from app source; do not assign it a fabricated originating commit or commit the bundle |

The table records the committed history before this reconciliation. The original 0005
index is hash-pinned imported material now located under `research/`. Its blanket
"nothing implemented" statement is superseded by the implementation trail below, not
silently rewritten. Original source hashes are retained; reviewed target hashes account
for necessary relative-link repairs after the moves.

## Infrastructure Implementation Trail

| Commit | Match to 0005 |
| --- | --- |
| `3106ad5` | Adds the coverage map and command-candidate work |
| `20b21f2` | Adds infrastructure detection and updates the map |
| `21d8ef0` | Adds Dockerfile, Compose, Devcontainer and Terraform check implementation |
| `0aaec6f` | Documents the overlay and per-check roll-up; updates the map |
| `8b19edc` | Adds infrastructure area/overall levels and updates the map |
| `83d6a88` | Adds Bicep and Kubernetes/Helm checks and updates coverage |
| `44da439` | Adds Ansible, CloudFormation, Pulumi and cross-cutting checks |
| `12c28e8` | Adds infrastructure judgment tasks and updates the map |
| `2146078` | Adds the calibration bundle in 0006 and changes level aggregation/gates |

This establishes an implementation trail, not proof that every row or proposed
adoption/bootstrap feature in the coverage map was completed.

## Roadmap Match: 0003 to Later Work

| Roadmap topic | Later evidence | Status that can be claimed |
| --- | --- | --- |
| Phase 1 placeholder handling, DOC-06 and larger excerpts | `7fddcc3` and the 0004 release notes | Local implementation recorded; `90e9a52` later refines Python fixture placeholder handling |
| Phase 1 external Project/package sync | 0004 release/package claims | Historically reported, but external Project synchronization is not independently established by this checkout |
| Blind second model opinion | `b470917` and the updated agreement report | Historical two-model comparison, not a second human rater |
| Mechanical STA-09 | `54babe0` | Implemented later; the roadmap's undecided wording is historical |
| Node hook patch proposals | `37e006f` | Bootstrap proposal implementation, not proof that hooks were installed or activated |
| Second human rater and recalibration gate | Roadmap open decisions; 0006 still documents one rater | Not shown complete by these artifacts |
| Azure DevOps, generalized adoption/merge behavior and Go support | Roadmap proposal tables | No completion inferred from unrelated later commits |

The original roadmap body and its unchecked decisions remain preserved. A later
implementation match is recorded here rather than rewriting the owner's historical note.

## Release and Calibration Match: 0004 and 0006

- The 0004 release notes record 141 tests and an 18-repository re-score at release time.
  These are historical claims, not tests rerun during this documentation match.
- The agreement report introduced in `7fddcc3` was updated in `b470917`. Its current
  body describes a second run: 47/54 agreement (87%) and kappa 0.768. The index's
  older "first comparison" description is not the latest body state.
- `2146078` introduced all three 0006 files together and changed aggregation/gates.
  The JSON contains 35 rating records, matching the README's 35 cells. This structural
  count does not revalidate the votes or reproduce the reported accuracy figures.
- The 0006 README reports exact agreement increasing from 23% to 43% and within-one-level
  agreement from 77% to 91%, under its stated one-rater and anchoring limitations.
  Its `proposed` metadata does not make the already-recorded experiment a future-only plan.
- Keep model agreement, human calibration and fresh runtime-test results separate.
  None establishes security, remote CI success or a second independent human calibration.

## Coverage Tracks: 0005

| Track | Matching evidence | Reconciliation |
| --- | --- | --- |
| A: detection | `20b21f2`; `scripts/detect_infra.py` | Implemented detector trail, not merely a proposal |
| B: checks, roll-up and levels | `21d8ef0`, `0aaec6f`, `8b19edc`, `83d6a88`, `44da439` | Substantial implementation recorded; not every proposed idea is necessarily checked |
| C: infrastructure entropy | Later `6490917` history and current skill's separate infra-entropy description | Earlier "still todo" wording is not a reliable current completion boundary |
| D: infrastructure judgment | `12c28e8`; subsequent `330bcb4` and `b71d7db` record agreement/calibration work | Prompt/tasks exist; each historical evaluation keeps its own scope and limitations |
| E: report output and city | Report overlay in `0aaec6f`; harbor `a620cd5` reverted by `f2154c2`; airport `8deb536`, `90e9a52` | Report implementation, reverted city experiment and current opt-in prototype are distinct |
| F: separate adoption skill | Coverage-map proposal | Do not call the proposed generalized adoption/merge workflow implemented |
| G: fixtures/calibration | Tool-specific implementation/test commits and the 0006 bundle | Some evidence exists; the requested multi-rater calibration is not established |

The coverage map's opening "everything is a proposal" and "starting point" paragraphs
are historical context. Its later "done so far" track list already contradicts a blanket
unimplemented reading. This crosswalk resolves that reading without changing the pinned source.

## Airport Match: 0007

| Decision or artifact | Git/source match | Current interpretation |
| --- | --- | --- |
| Airport asset idea | `3bfdf2b` | Initial design proposal |
| Transit options A/B/C | `f85a36d`; city baseline `a3f9c69` | Evaluation alternatives, not three different production integrations |
| Design authority and checks | `489457f` | Current app DESIGN.md governs visual decisions |
| Earlier separate prototype | `38fab47` adds `apps/harness-city/prototypes/airport.html`; `3f450d5`, `c2a342f` refine it | Historical prototype, not the current generated docs/0007 file |
| Prototype in the real city | `8deb536` | Replaces the separate prototype with the real app's opt-in airport |
| Current support facilities, metro, underground and PNG | `90e9a52` | Implemented evaluation behavior with automated browser evidence recorded separately |
| L3 two-runway table entry | Earlier proposal versus the document's later explicit one-runway decision | Superseded proposal; the later decision and current DESIGN.md take precedence |
| Panel/report adapter and detected-image container counts | "Panel and data" proposal versus current converter and evaluation controls | Not established as production integration: report_to_city.py has no infra adapter; controls simulate airport values |

Devcontainer and Agent guidance are non-blocking city support facilities under the
current visual contract. That does not rewrite the auditor's own infrastructure-level
calculation. The airport remains opt-in and its simulated control values must not be
presented as audited report findings.

## Match to the Basic Spec Workflow

| Folder | Existing material can support | Must not be invented |
| --- | --- | --- |
| 0001 | Initial-extraction rationale, acceptance boundaries and provenance architecture | A claim that these new retrospective files existed in the original extraction |
| 0003 | Ideation/problem context and phased Plan proposals | Resolved owner decisions or completed later phases without evidence |
| 0004 | Implementation/release and historical validation evidence | Original requirements or newly executed validation |
| 0005 | Plan workstreams and architecture/design constraints | A fully completed adoption architecture from proposal text alone |
| 0006 | Calibration/validation evidence informing later plans | A new calibration run or second rater |
| 0007 | Visual ideation, prototype decisions and architecture notes | Default production integration or completion of all proposed assets |

The new four-file sets in each requested folder use these roles to reconstruct its own
topic. The basic 0008 documents remain the separate cross-cutting quality topic. All are
explicitly retrospective, not claimed as original pre-implementation artifacts.

## What Was Not Reconstructed

No human discovery/grilling sessions, new human ratings, historical CI passes,
claims of original pre-implementation spec stages or pre-extraction commits are fabricated. Raw reports
and new audit receipts remain ignored. Existing calibration exceptions and provenance
are preserved rather than generalized into permission to publish new private datasets.

## Related Entry Points

Validation for the initial reconciliation matched 12 tracked files to their first-add/latest
path commits and committed blobs. The subsequent research-folder moves retain that
provenance, with explicit link/manifest repairs rather than a claim of unchanged paths.
One local simulator is generated output; all 28 cited commit objects exist. The
calibration sidecar contains 35 rating records.
The repository documentation, source-integrity and publication gate passes. No historical
evaluation or runtime test was rerun or invented by this documentation-only match.

- [Documentation index](README.md)
- [Current basic retrospective](0008-v0.1-harness-history-and-quality/Map.md)
- [Current city design authority](../apps/harness-city/DESIGN.md)
- [Audit skill and limits](../skills/harness-audit/SKILL.md)