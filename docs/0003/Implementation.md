---
type: 'Implementation'
id: '0003'
version: 'v0.1'
title: 'Harness Roadmap: Matched Outcomes'
description: 'Implemented roadmap pieces and unresolved decisions, separated by evidence.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:7fddcc3', 'git:b470917', 'git:54babe0', 'git:37e006f', 'docs/0003/research/Repo Harness Next Steps.md']
---

# Harness Roadmap: Matched Outcomes

## Recorded Implementation

- [x] `7fddcc3`: v1.2 placeholder handling, DOC-06 and excerpt changes.
- [x] `b470917`: updated independent model-agreement record, not a second human rater.
- [x] `54babe0`: STA-09 becomes mechanical.
- [x] `37e006f`: Node hook/package patch proposals, not automatic installation.
- [x] `90e9a52`: later Python fixture placeholder correction with regression evidence.

## Still Open in the Available Evidence

- [ ] Establish a second independent human calibration rater and fresh holdout evidence.
- [ ] Resolve remaining formatter, generalized adoption and platform-scope decisions.
- [ ] Independently establish external Project/package synchronization if needed.

These are evidence dispositions, not a new authorization to execute the roadmap.
Do not mark all three original phases complete because selected later commits exist.

## Verification and Handoff

Objective: preserve the phase/commit correspondence without rerunning old experiments.
Read first: [Plan](Plan.md), original roadmap and v1.2 records in 0004.
Constraints: no weight changes, fabricated ratings or implicit bootstrap application.
Validate: `git show --stat 54babe0` and `python3 tools/check.py`.
Stop when: claimed source changes match Git and remaining decisions are explicit.
Historical counts are not fresh test results; current checks live in the root Taskfile.