---
type: 'Plan'
id: '0004'
version: 'v0.1'
title: 'Audit v1.2: Retrospective Acceptance Plan'
description: 'Evidence-derived acceptance boundaries for the recorded v1.2 changes and agreement work.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0004/research/Release-Notes-v1.2.md', 'docs/0004/research/Agreement-Report-v1.2.md']
---

# Audit v1.2: Retrospective Acceptance Plan

## Acceptance Boundaries

| ID | Reconstructed behavior |
| --- | --- |
| V-1 | Placeholder-bearing incomplete guidance does not receive unqualified credit. |
| V-2 | DOC-06 resolves supported path facts mechanically; unresolved cases remain explicit. |
| V-3 | Excerpts and runner candidates use the release's documented budgets. |
| V-4 | Scoring weights/caps remain pinned and model answers remain quote-validated. |
| V-5 | Agreement reports separate verdict agreement, score effects and unresolved differences. |

## Recorded Sequence

`7fddcc3` imports the v1.2 changes and first records. Prompt correction `8c9342f`
precedes the updated agreement report in `b470917`. Later changes such as mechanical
STA-09 and fixture-aware placeholder detection are not mislabeled as original v1.2 work.

## Validation Contract

Objective: match release claims to recorded implementation and declared limits.
Read first: original release/agreement files and [Architecture](Architecture.md).
Constraints: historical datasets/answers are not republished or fabricated; no frozen-weight change.
Validate: `git show --stat 7fddcc3`, `git show --stat b470917` and `python3 tools/check.py`.
Stop when: the historical release and later report are distinguishable from fresh checks.

The release's 141-test and 18-repository figures remain historical claims. Current
execution evidence belongs to the current root `task check`, not this reconstructed plan.