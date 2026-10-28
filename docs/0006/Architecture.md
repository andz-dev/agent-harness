---
type: 'Architecture'
id: '0006'
version: 'v0.1'
title: 'Infrastructure Calibration: Evaluation Architecture'
description: 'Standalone voting page, sidecar and separate audit rule-change boundaries.'
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

# Infrastructure Calibration: Evaluation Architecture

## Components and Data Flow

| Component | Responsibility |
| --- | --- |
| infra-level-vote.html | Standalone rating UI with check lists and optional tool-level reveal |
| Browser local storage | Local draft votes until an explicit sidecar save |
| infra-levels-evaluation.json | Historical ratings and before/after comparison state |
| Audit level logic | Separately implemented location aggregation and gate rules |
| README | Reported measures, changes and interpretation limits |

The recorded flow is human votes to sidecar, tool levels to comparison, then documented
rule evaluation. The voting page does not certify the audit's runtime enforcement or
replace report evidence. There is no required database, server or deployment service.

## Trust and Preservation

The sidecar is intentionally tracked historical evidence under the owner's documented
exception. That is not blanket permission to commit new reports, private datasets or
new human ratings. Do not silently normalize or replace the original values.

Before/after calibration results are distinct observations. One rater and check-list
anchoring remain limits; a source commit is not proof of independent reproduction.
See [Plan](Plan.md) and [Implementation](Implementation.md).