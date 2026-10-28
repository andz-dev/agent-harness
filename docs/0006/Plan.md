---
type: 'Plan'
id: '0006'
version: 'v0.1'
title: 'Infrastructure Calibration: Retrospective Plan'
description: 'Evaluation inputs, comparison boundaries and limits for the recorded calibration.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0006/research/README.md', 'docs/0006/research/infra-levels-evaluation.json', 'git:2146078']
---

# Infrastructure Calibration: Retrospective Plan

## Acceptance Boundaries

| ID | Reconstructed evaluation requirement |
| --- | --- |
| C-1 | Preserve per-area votes and corresponding before/after tool levels in an explicit sidecar. |
| C-2 | Keep tool-level reveal separate from voting and support saving/loading the sidecar. |
| C-3 | Report exact/within-one agreement and error measures without disguising the sample limits. |
| C-4 | Rule changes do not change the frozen main score; sensitive secret gates retain their strictness. |
| C-5 | One-rater evidence is not generalized to independent multi-rater validation. |

## Recorded Sequence

Collect ratings, compare original outputs, evaluate aggregation/gate changes and retain
before/after results. The actual recorded changes are the location-majority rule and
specific gate/level demotions described in the original README, not a new formula inferred here.

## Validation Contract

Objective: preserve the recorded evaluation's structure and honest interpretation.
Read first: original README, JSON sidecar and [Architecture](Architecture.md).
Constraints: do not modify votes, create a new rater or claim the calibration was rerun.
Validate: `git show --stat 2146078` and `python3 tools/check.py`.
Stop when: the three original artifacts remain intact and comparison limits are explicit.

Any future calibration needs a separately defined sample/rater protocol and fresh evidence.