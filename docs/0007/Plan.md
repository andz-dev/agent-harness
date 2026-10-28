---
type: 'Plan'
id: '0007'
version: 'v0.1'
title: 'Airport Overlay: Evidence-Matched Plan'
description: 'Observable airport evaluation behavior and remaining production-integration boundaries.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0007/research/airport-assets.md', 'apps/harness-city/DESIGN.md', 'git:8deb536', 'git:90e9a52']
---

# Airport Overlay: Evidence-Matched Plan

## Acceptance Boundaries

| ID | Observable requirement |
| --- | --- |
| A-1 | The airport stays outside the scored districts and never changes the city score. |
| A-2 | L0 is closed; L1 retains an identifiable airfield; L2/L3 have appropriate terminal/stand capacity. |
| A-3 | Only applicable Terraform/Compose/Dockerfile areas control the main airport's visual minimum. |
| A-4 | Devcontainer and Agent guidance grow independently; all applicable area displays remain visible. |
| A-5 | Transport uses the weaker endpoint; buses run at L1 and metro at L2+; stations exist at every city level. |
| A-6 | Underground survives city/option changes, rebuilds preserve resources/materials, and PNG export includes descriptions. |
| A-7 | Real-browser tests cover desktop/mobile and offline behavior with synthetic data. |

## Sequence and Boundaries

The history moves from asset/transit ideas to a separate prototype, then into the real
city and later automated regression fixes. Current behavior is not backdated to the
first proposal. Production report-data integration remains distinct from this evaluator.

## Validation Contract

Objective: keep the current airport metaphor and evaluation behavior consistent.
Read first: [Architecture](Architecture.md), app DESIGN.md and original asset notes.
Constraints: deterministic layout, synthetic public data, no scoring changes or new private reports.
Validate: `task app:test` for runtime changes; `python3 tools/check.py` for this docs-only reconstruction.
Stop when: the relevant gate passes and known integration/prototype limits remain explicit.