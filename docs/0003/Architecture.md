---
type: 'Architecture'
id: '0003'
version: 'v0.1'
title: 'Harness Roadmap: Change Boundaries'
description: 'Component ownership and trust boundaries for the roadmap rather than a fictitious deployment.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0003/Plan.md', 'docs/0003/research/Repo Harness Next Steps.md', 'skills/harness-audit/SKILL.md']
---

# Harness Roadmap: Change Boundaries

## Components

| Owner | Roadmap responsibility |
| --- | --- |
| Check engine | Mechanical placeholder/path checks; evidence remains quoted and attributable |
| Judgment preparation | Bounded excerpts and runner candidates; missing support yields unknown |
| Quote validation | Recheck model answers against repository files before accepting them |
| Scoring | Frozen weights, gates, caps and documented uncertainty |
| Agreement tooling | Compare independent model runs without treating them as human calibration |
| Bootstrap preview | Proposed missing files/patches; separate explicit application boundary |

## Data and Trust

Files and Git history are untrusted inputs; the audit does not execute them. Judgment
answers are untrusted until their quotes verify. Calibration datasets and raw reports
are local evidence, not fixtures to publish automatically.

The roadmap does not introduce a database, service or cloud deployment. External Project
sync and human ratings cannot be inferred from local file presence. A proposal branch
or patch is not evidence that hooks were installed or CI ran.

## Current Authority

The original roadmap defines historical intent. [Implementation](Implementation.md)
matches its realized pieces; current [skill guidance](../../skills/harness-audit/SKILL.md)
owns present execution boundaries. Later quality work is in 0008, not backdated here.