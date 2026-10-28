---
type: 'Architecture'
id: '0004'
version: 'v0.1'
title: 'Audit v1.2: Processing and Evidence Boundaries'
description: 'Static checks, bounded judgments, scoring and agreement roles at the v1.2 milestone.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0004/Plan.md', 'docs/0004/research/Release-Notes-v1.2.md', 'skills/harness-audit/SKILL.md']
---

# Audit v1.2: Processing and Evidence Boundaries

## Processing Roles

| Component | Responsibility |
| --- | --- |
| Mechanical check engine | File/config facts and placeholder handling |
| Judgment preparation | Bounded source excerpts and candidate commands |
| Answer validator | Verify quoted evidence and retain unknowns when unsupported |
| Scoring/triage | Frozen arithmetic, gates/caps and counterfactual fix ranking |
| Agreement tool | Compare independent answers and resulting score differences |
| Report/schema | Stable machine-readable findings and explicit limitations |

The flow is files to mechanical findings/judgment tasks, verified answers to findings,
then scoring/reporting. Agreement reads independent results; it does not manufacture
missing answers or turn model agreement into human ground truth.

## Runtime and Storage

The audit remains local static Python processing. It does not import or execute audited
code. Raw repository reports, answer arrays and human calibration data stay outside the
public documentation set. No database or deployed service is implied by these records.

## Historical Limits

The original release describes Python/Node support and GitHub bootstrap proposals.
That does not establish support for all future platforms or detector ideas. The later
current implementation and [Implementation](Implementation.md) supply the change boundary.