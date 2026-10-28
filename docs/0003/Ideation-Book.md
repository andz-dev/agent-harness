---
type: 'Ideation Book'
id: '0003'
version: 'v0.1'
title: 'Harness Roadmap: Reconstructed Intent'
description: 'Retrospective rationale for improving trust, calibration and bootstrap usefulness.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0003/research/Repo Harness Next Steps.md', 'git:23251df', 'git:7fddcc3']
---

# Harness Roadmap: Reconstructed Intent

## Problem and Goals

The [owner's roadmap](research/Repo%20Harness%20Next%20Steps.md) identifies three trust gaps:
placeholder files earning points, calibration relying on one rater, and unresolved
judgments caused by path checking and excerpt limits. It then proposes more useful
bootstrap and fix-plan behavior. This is reconstructed intent, not a new interview.

## Decisions

Phase 1 addresses obvious trust defects before recalibration. Weights remain frozen
until the proposed calibration gate is met. Bootstrap writes remain separate from the
read-only audit, and proposed merge behavior is not permission to overwrite files.

## Historical Versus Current

`23251df` preserves the roadmap. `7fddcc3` later implements the recorded v1.2 trust
fixes; `54babe0` makes STA-09 mechanical; `37e006f` adds Node hook patch proposals.
Those matches do not establish a second human rater or complete every roadmap phase.

The original open decisions remain preserved. See [Plan](Plan.md),
[Architecture](Architecture.md), [Implementation](Implementation.md) and the
[crosswalk](../History-Match.md#roadmap-match-0003-to-later-work).