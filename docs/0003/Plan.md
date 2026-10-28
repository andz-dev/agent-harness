---
type: 'Plan'
id: '0003'
version: 'v0.1'
title: 'Harness Roadmap: Evidence-Matched Plan'
description: 'Roadmap phases and acceptance boundaries reconciled with later commits.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0003/research/Repo Harness Next Steps.md', 'docs/0004/research/Release-Notes-v1.2.md']
---

# Harness Roadmap: Evidence-Matched Plan

## Acceptance Boundaries

| ID | Observable requirement | Evidence state |
| --- | --- | --- |
| R-1 | Incomplete placeholder guidance does not earn a false pass. | v1.2 implementation; later fixture correction in `90e9a52` |
| R-2 | Script-resolvable paths and larger excerpts reduce avoidable unknowns. | Recorded in `7fddcc3` and release notes |
| R-3 | Calibration precedes any weight change. | Gate preserved; second human rater not established |
| R-4 | Bootstrap proposes reviewable changes separately from static audit. | Existing preview and `37e006f`; generalized adoption remains proposed |

## Phases

1. Make measurements trustworthy: placeholders, DOC-06 and excerpts.
2. Widen calibration evidence and compare independent judgments before recalibration.
3. Improve bootstrap/fix plans within explicit safety boundaries.

This sequencing comes from the original roadmap, not a newly approved implementation
order. Go support, Azure DevOps and a generalized adoption workflow are not silently added.

## Validation Contract

Objective: reconcile roadmap requirements with actual implementation evidence.
Read first: original roadmap, [Architecture](Architecture.md), [Implementation](Implementation.md).
Constraints: frozen weights; audit never executes audited code; no inferred rater approval.
Validate: `git show --stat 7fddcc3` and `python3 tools/check.py`.
Stop when: each historical completion claim has a source and unresolved decisions stay open.
Current runtime changes require their own focused regression and `task check`.