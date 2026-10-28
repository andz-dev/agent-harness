---
type: 'Plan'
id: '0005'
version: 'v0.1'
title: 'Infrastructure Overlay: Matched Plan'
description: 'Coverage tracks and observable boundaries reconciled with implementation commits.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0005/research/Infrastructure-Coverage-Map.md', 'git:0aaec6f', 'git:8b19edc', 'git:12c28e8']
---

# Infrastructure Overlay: Matched Plan

## Acceptance Boundaries

| ID | Observable requirement |
| --- | --- |
| I-1 | Detected infrastructure is attributed by kind and location. |
| I-2 | Static findings include evidence and distinguish pass/fail/unknown/not-applicable. |
| I-3 | Infrastructure levels and roll-ups remain separate from pillar points and score. |
| I-4 | Judgment answers require verified quotes and retain unsupported unknowns. |
| I-5 | No terraform/docker/kubectl/devcontainer execution occurs during audit. |

## Matched Workstreams

Detection precedes initial container/Terraform checks, report output, area levels and
broader tool coverage. Judgment and entropy arrive through later commits. The historical
harbor city adapter was implemented then reverted; the current airport is a separate
opt-in evaluation. A proposed generalized adoption skill is not treated as delivered.

## Validation Contract

Objective: identify implemented tracks without claiming every proposed check exists.
Read first: original coverage map, [Architecture](Architecture.md), [Implementation](Implementation.md).
Constraints: frozen main score; read-only audit; no deployment or owner-file overwrite.
Validate: `git show --stat 20b21f2`, `git show --stat 12c28e8` and `python3 tools/check.py`.
Stop when: each completion has a source/commit and unimplemented proposals remain explicit.
New detector work still requires focused synthetic regressions and the current `task check`.