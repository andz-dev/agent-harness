---
type: 'Architecture'
id: '0005'
version: 'v0.1'
title: 'Infrastructure Overlay: Component Boundaries'
description: 'Detection, checks, judgments and separate report-level architecture of the infrastructure overlay.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0005/Plan.md', 'skills/harness-audit/SKILL.md', 'git:8b19edc']
---

# Infrastructure Overlay: Component Boundaries

## Components and Flow

| Component | Responsibility |
| --- | --- |
| detect_infra.py | Discover tool kinds/files and locations without executing them |
| infra_checks.py | Mechanical infrastructure evidence and roll-up/level inputs |
| infra_quality.md judgment prompt | Bounded tasks for safe workflow/environment/credential/check guidance |
| Answer validation | Verify quoted source evidence before accepting judgments |
| Report schema/rendering | Separate infra findings, levels and limitations from the score |

Repository text feeds detection and checks; bounded excerpts feed judgment tasks; verified
findings feed the report. Cross-cutting, agent-guidance and entropy areas retain their
separate roles. No database or deployed service is required by this local pipeline.

## Distinct Level Contracts

The auditor's infrastructure aggregation and the city's visual core/support rule are
different contracts. The current city treats Devcontainer and Agent guidance as benefits;
that does not retroactively change the audit engine's level calculation.

## Trust and Output

No infrastructure commands or audited code run. Raw reports may contain private paths
and excerpts and stay ignored. Detection is not security certification. The proposed
adoption writer is a separate boundary; this overlay does not authorize file application.
The current airport's simulated controls are not a completed production report adapter.

See [Implementation](Implementation.md) for implemented and reverted pieces.