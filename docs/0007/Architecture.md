---
type: 'Architecture'
id: '0007'
version: 'v0.1'
title: 'Airport Overlay: Current Evaluation Architecture'
description: 'City-owned scene, independent support facilities, transit and standalone build boundaries.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['apps/harness-city/DESIGN.md', 'docs/0007/research/airport-assets.md', 'git:90e9a52']
---

# Airport Overlay: Current Evaluation Architecture

## Components

| Component | Role |
| --- | --- |
| App index.html and scene builders | Single city/airport implementation; real orthographic camera and shared assets |
| Airport control state | Explicit simulated area levels, variants and container requests |
| Core/support classification | Core minimum separate from optional developer terminal and guidance office |
| Transit builders and permanent display state | Weaker-endpoint service plus independent surface/underground mode |
| Renderer/material ownership | Restore shared material baselines; release scene-owned GPU resources only |
| PNG compositor | Separate render plus labels and wrapped descriptions, without changing the live camera |
| Standalone builder | Derive the offline evaluator from app source and selected synthetic data |
| Playwright suite | Trusted local desktop/mobile and network-blocked offline verification |

## Data and Trust

The evaluator's control state feeds deterministic scene construction. It does not
write an audit score or imply that a real report contains those simulated levels.
The original asset document's proposed infra adapter is not current converter behavior.
The auditor's own infrastructure aggregation is not changed by the city's visual rule.

No database or cloud deployment is required. Kit models remain shared; new procedural
objects follow [app design](../../apps/harness-city/DESIGN.md) and license notices.
Generated standalone HTML embeds data and remains local build output, not source to edit.

## Authority and Supersession

Current DESIGN.md and later explicit decisions supersede early two-runway and L3-only
metro ideas. The old separate prototype is historical; the current app is authoritative.
See [Implementation](Implementation.md) for the corresponding commits and remaining gaps.