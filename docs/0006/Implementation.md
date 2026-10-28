---
type: 'Implementation'
id: '0006'
version: 'v0.1'
title: 'Infrastructure Calibration: Recorded Outcomes'
description: 'The B-215 calibration artifacts and rule changes with unresolved validation limits.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:2146078', 'docs/0006/research/README.md', 'docs/0006/research/infra-levels-evaluation.json']
---

# Infrastructure Calibration: Recorded Outcomes

## Recorded Implementation

- [x] `2146078` introduces the page, 35-record sidecar and calibration README.
- [x] The same commit records B-215 aggregation/gate changes.
- [x] The README preserves reported before/after measures and their interpretation limits.

The README reports exact agreement from 23% to 43%, within-one agreement from 77%
to 91%, and mean absolute difference from 1.00 to 0.66. These are historical figures,
not calculations independently rerun by this documentation reconstruction.

## Unresolved Validation

- [ ] A second independent human rating remains open in the available evidence.
- [ ] The exercise does not establish accuracy across all repositories or L0/L3 ratings.
- [ ] The retained outliers are not silently refitted to improve this one sample.

## Verification Contract

Objective: match artifacts and rule-change provenance without rerunning the experiment.
Read first: [Plan](Plan.md), [Architecture](Architecture.md), original README.
Constraints: preserve original ratings; no new votes or private dataset publication.
Validate: `git show --stat 2146078` and `python3 tools/check.py`.
Stop when: original source hashes and structural evidence match, with human-validation limits retained.