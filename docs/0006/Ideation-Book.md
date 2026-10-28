---
type: 'Ideation Book'
id: '0006'
version: 'v0.1'
title: 'Infrastructure Calibration: Reconstructed Intent'
description: 'Purpose and limitations of the recorded infrastructure-level calibration.'
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

# Infrastructure Calibration: Reconstructed Intent

## Problem and Goal

Infrastructure levels needed comparison with human interpretation before confidence in
their meaning could increase. The recorded exercise compares one rater's area-level
votes with tool outputs and investigates aggregation/gate sensitivity, not new score weights.

## Decisions

Keep infrastructure separate from the main score. Use a standalone voting interface and
explicit sidecar, distinguish before/after rules, and disclose single-rater/anchoring
limits. The original README says the rater did not see tool levels while voting but
could see check lists; that remains a historical account, not a new verification claim.

## Evidence and Risks

`2146078` introduces the README, page and JSON together. The sidecar has 35 rating
records across the README's stated 15 repositories. This reconstruction preserves those
owner-approved historical artifacts and does not invent a second rater or new votes.

See [Plan](Plan.md), [Architecture](Architecture.md), [Implementation](Implementation.md)
and the original [results and limitations](research/README.md).