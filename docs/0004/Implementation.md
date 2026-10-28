---
type: 'Implementation'
id: '0004'
version: 'v0.1'
title: 'Audit v1.2: Recorded Release and Agreement'
description: 'Commit-backed release outcomes and the historical agreement result without new experiment claims.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:7fddcc3', 'git:8c9342f', 'git:b470917', 'docs/0004/research/Agreement-Report-v1.2.md']
---

# Audit v1.2: Recorded Release and Agreement

## Recorded Outcomes

- [x] `7fddcc3` introduces v1.2 code and the three original development-record files.
- [x] `8c9342f` records judgment prompt tightening before the later agreement update.
- [x] `b470917` updates the report to the second independent model comparison.

The report records 47/54 agreement (87%), kappa 0.768, and identical scores for 13
of 15 repositories. These numbers are retained historical statements. No new blind
model run, human rating or original 141-test environment was executed by this reconstruction.

## Unresolved Evidence

- [ ] Independent human calibration beyond the original rater remains unestablished here.
- [ ] Historical external package/Project synchronization is not independently revalidated.

## Verification Contract

Objective: preserve the release/agreement distinction and its limitations.
Read first: [Plan](Plan.md), original release notes and agreement report.
Constraints: no invented answers, raw private reports or retrospective pass claims.
Validate: `git show --stat b470917` and `python3 tools/check.py`.
Stop when: files, commits and historical figures agree with their sources.

The original index's "first comparison" description is older than the report body;
the later body and its Git update identify the current historical run.