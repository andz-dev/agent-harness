---
type: 'Discovery Map'
id: '0008'
version: 'v0.1'
title: 'Harness History and Quality Map'
description: 'Automatically reconstructed historical constraints and the scope of current quality improvements.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
sources:
  - 'Local Git history through 8deb536, inspected 2026-10-28'
  - 'AGENTS.md and Taskfile.yml, working tree inspected 2026-10-28'
  - 'Owner request for retrospective basic documents and automated tests, 2026-10-28'
stale_after: '2026-11-11'
tags:
  - 'documentation'
---

# Harness History and Quality Map

## Reconstruction Contract

This is an automated, retrospective discovery map, not an interview transcript.
No grilling session occurred. The owner delegated routine decisions while unavailable;
the next free documentation ID is 0008 and this bundle starts at v0.1.

The requested scope is the basic Ideation, Plan, Architecture and Implementation
documents, supported by this map. It is an explicit reduced adaptation of the spec
workflow, not a claim that research, whitepaper, prototype, ontology or dataset stages
were newly completed. Existing historical artifacts remain in their original locations.

## Evidence Boundaries

| Evidence | Meaning | Limit |
| --- | --- | --- |
| Local commit objects | A change exists in this checkout's history | Not proof that its tests ran |
| Current source and configuration | The implementation currently declares that behavior | Not proof of client loading or CI execution |
| Fresh command results | A check ran in the current environment | Not a historical pass record |
| Pre-commit airport changes | Implementation observed when reconstruction began | Must not be attributed to the earlier commit |
| Imported historical documents | Source provenance and prior design intent | Not an instruction to replay old destructive operations |

The committed reconstruction boundary at the start was `8deb536`. Airport corrections, independent
support facilities, permanent underground and PNG export were present as uncommitted
working-tree changes when this retrospective began. The owner subsequently requested
commit `90e9a52`, which records those changes and this basic bundle. Keep the original
reconstruction boundary distinct from that later implementation commit.

## Historical Outline

| Commit | Recorded change | Carry-forward constraint |
| --- | --- | --- |
| `23251df` | Initial standalone audit skill and city extraction | Preserve imported provenance and licenses |
| `7228905` | Synthetic demo covering four city tiers | Public examples stay synthetic |
| `7fddcc3` | Audit v1.2 adoption | Tool/catalog versions matter when comparing reports |
| `a3f9c69` | City explanations and transit network | Every visible object explains an audit fact |
| `20b21f2` | Infrastructure detection overlay | Infrastructure remains separate from the score |
| `6490917` | Infrastructure level and excerpt rules | Static findings are evidence, not execution proof |
| `a620cd5`, `f2154c2` | Harbor implementation and subsequent revert | Reverted experiments are not current architecture |
| `489457f` | City design rules and design gate | Update design before changing visual decisions |
| `38fab47`, `3f450d5`, `c2a342f` | Airport evaluation, mobile and orthographic-camera work | Retain real-city camera and mobile inspection |
| `8deb536` | Airport prototype inside the real city | Build standalone evaluation pages from the app source |
| `90e9a52` | City corrections, browser/CI automation, audit history and basic retrospective | Implementation committed after its original working-tree observations |

Inspect a cited change with `git show --stat <commit>`; inspect its contents with
`git show <commit>:<path>`. These are local commit citations, not fabricated session IDs.

## Current Workstreams

1. Reconstruct concise, versioned basic documents with commit/source provenance.
2. Launch automated browser tests through a reproducible repository command and CI.
3. Keep comparable static self-audit history with explicit tool/catalog compatibility.
4. Teach the audit skill how repository owners run tests separately and compare results.
5. Improve demonstrated harness gaps without weakening existing checks or changing scores.

## Locked Constraints

- The auditor never executes code from an audited repository.
- Browser automation runs only this repository's trusted synthetic city application.
- Audit reports, answers, test output and history records stay in ignored local storage.
- Current verification results never become retrospective evidence for an old commit.
- Original `docs/0001/.gitkeep` and imported `docs/0002/` are preserved; the owner's later
  per-folder reconstruction uses 0001 for the initial extraction retrospective.
- Client configuration, live client loading and external integrations are out of scope.
- No commits, branches, deployments or remote connections are created automatically.

## Initial Findings

The bounded guidance assessor observed `AGENTS.md`, `CLAUDE.md` and CI files, but did
not recognize the Taskfile check entry. That is an assessor coverage limit, not proof
that the check is absent. Client loading and historical CI execution remain unknown.

The local static self-audit reported 33/100 before this work. Its raw report is local
and ignored. Judgment tasks are not treated as answered merely because this document
exists. Exact before/after differences belong in the completed Implementation record.

## Source Pointers

The [requested-folder history crosswalk](../History-Match.md) reconciles the actual
files and content of 0001, 0003, 0004, 0005, 0006 and 0007 with their local commit
history. It preserves those folders rather than replacing them with this retrospective.
The [per-folder navigation matrix](../README.md#per-folder-basic-sets) now links actual
Ideation, Plan, Architecture and Implementation files in each of the six requested folders.
They are new retrospective documents, not backdated original specs.

| Basic artifact | Purpose |
| --- | --- |
| [Ideation Book](Ideation-Book.md) | Reconstructed rationale and quality goals |
| [Plan](Plan.md) | Observable acceptance criteria and exact done contracts |
| [Architecture](Architecture.md) | Boundaries, browser/history design and storage |
| [Implementation](Implementation.md) | Executed evidence, decisions and remaining limits |

The original raw self-audit's 33/100 result was affected by a reproduced detector
false positive. With that engine corrected, the comparable before/after observations
are 55/100 and 55/100, with no mechanical regressions and seven unanswered judgments.
Those are pre-commit observations: untracked files were not credited as committed evidence.
The post-commit audit of `90e9a52` is 42/100 because the Node app is now tracked and
included. It adds six app-scoped checks and records two orientation improvements;
no existing check changed from pass to fail. Node lint configuration is still missing,
and the static detector misses the existing indirect Task-based CI and docs commands.
Do not present the changed coverage as evidence that passing browser tests regressed.

- [Repository rules](../../AGENTS.md)
- [Repository commands](../../Taskfile.yml)
- [Imported source documentation](../0002/README.md)
- [Earlier roadmap](../0003/research/README.md)
- [Airport design decisions](../0007/research/airport-assets.md)
- [Audit workflow](../../skills/harness-audit/SKILL.md)
- [City design](../../apps/harness-city/DESIGN.md)