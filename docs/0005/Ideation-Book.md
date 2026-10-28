---
type: 'Ideation Book'
id: '0005'
version: 'v0.1'
title: 'Infrastructure Overlay: Reconstructed Intent'
description: 'Rationale for reporting infrastructure readiness separately from the frozen harness score.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0005/research/Infrastructure-Coverage-Map.md', 'git:3106ad5', 'git:20b21f2']
---

# Infrastructure Overlay: Reconstructed Intent

## Problem and Goal

The seven-pillar harness score does not describe the maturity of Terraform, containers,
deployment manifests and development environments. The goal is attributable static
infrastructure evidence without changing the frozen 0-100 score or executing infrastructure.

## Decisions

The [coverage map](research/Infrastructure-Coverage-Map.md) records overlay-first design and
tool ordering. It mixes its starting proposal with later "done so far" updates.
Its blanket proposal-only language is therefore not a reliable current completion claim.
Original text remains preserved; this set supplies the reconciled interpretation.

## Scope and Risks

Detect locations, evaluate tool-specific/cross-cutting checks, prepare quote-validated
judgments, and expose separate report levels/roll-ups. Text detection is heuristic;
presence of a tool or config is not proof a plan/build/check ran. Generalized adoption
and multi-rater calibration are separate proposals, not automatic consequences of detection.

See [Plan](Plan.md), [Architecture](Architecture.md), [Implementation](Implementation.md)
and the [commit crosswalk](../History-Match.md#coverage-tracks-0005).