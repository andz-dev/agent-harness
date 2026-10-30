---
type: 'Documentation Index'
title: 'Agent Harness Documentation'
description: 'Entry points for current specifications, historical source records and evaluation notes.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [documentation, history]
---

# Agent Harness Documentation

## Per-Folder Basic Sets

Each requested folder now contains the four basic retrospective artifacts, reconstructed
from its own Git history and retained source documents. Original files remain alongside
them; no historical interview or unperformed test is invented.

| Topic | Ideation | Plan | Architecture | Implementation |
| --- | --- | --- | --- | --- |
| 0001: initial extraction | [Ideation](0001/Ideation-Book.md) | [Plan](0001/Plan.md) | [Architecture](0001/Architecture.md) | [Implementation](0001/Implementation.md) |
| 0003: harness roadmap | [Ideation](0003/Ideation-Book.md) | [Plan](0003/Plan.md) | [Architecture](0003/Architecture.md) | [Implementation](0003/Implementation.md) |
| 0004: v1.2 and agreement | [Ideation](0004/Ideation-Book.md) | [Plan](0004/Plan.md) | [Architecture](0004/Architecture.md) | [Implementation](0004/Implementation.md) |
| 0005: infrastructure overlay | [Ideation](0005/Ideation-Book.md) | [Plan](0005/Plan.md) | [Architecture](0005/Architecture.md) | [Implementation](0005/Implementation.md) |
| 0006: level calibration | [Ideation](0006/Ideation-Book.md) | [Plan](0006/Plan.md) | [Architecture](0006/Architecture.md) | [Implementation](0006/Implementation.md) |
| 0007: airport evaluation | [Ideation](0007/Ideation-Book.md) | [Plan](0007/Plan.md) | [Architecture](0007/Architecture.md) | [Implementation](0007/Implementation.md) |

0001 was initially reserved; under the owner's requested per-folder reconstruction and
delegated routine decisions it now records the initial extraction. Its zero-byte
`.gitkeep` and the original provenance documents remain unchanged.

## Cross-Cutting Quality Bundle

Start with [the history map](0008-v0.1-harness-history-and-quality/Map.md).
The separate cross-cutting history/quality specification set is:

- [Ideation Book](0008-v0.1-harness-history-and-quality/Ideation-Book.md)
- [Plan](0008-v0.1-harness-history-and-quality/Plan.md)
- [Architecture](0008-v0.1-harness-history-and-quality/Architecture.md)
- [Implementation and results](0008-v0.1-harness-history-and-quality/Implementation.md)

This is a reduced retrospective, reconstructed from local commits and source evidence.
No historical grilling or invented session was performed. Commit `90e9a52` contains
the implementation and original retrospective; the handoff distinguishes pre-commit
observations from the subsequent committed-scope audit.

## Preserved History

The [folder/file Git crosswalk](History-Match.md) matches the requested 0001, 0003,
0004, 0005, 0006 and 0007 contents to their actual commits, identifies superseded
statements, and separates roadmap proposals from implementation and evaluation evidence.

| Folder | Role |
| --- | --- |
| [0001](0001/) | Initial-extraction retrospective; original empty scaffold preserved |
| [0002](0002/README.md) | Imported, relocated source as-built documents; preserve provenance |
| [0003](0003/research/README.md) | Earlier proposed roadmap, not a completion claim |
| [0004](0004/research/README.md) | v1.2 agreement and release records |
| [0005](0005/research/README.md) | Infrastructure coverage mapping |
| [0006](0006/research/README.md) | Infrastructure-level evaluation material |
| [0007](0007/research/airport-assets.md) | Airport evaluation and current metaphor decisions |
| [0009](0009/Design-Proposal.md) | Draft proposal: city overlays, road traffic, committed harness evidence; [asset research](0009/Asset-Research.md) |
| [0010](0010/Research.md) | Research: city and map editor (skills, frameworks, CC0 assets, export format) |

Old paths are preserved rather than renamed into a fictitious original spec workflow.
The generated airport simulator is local build output, not a document to commit.
Its reproducible build instructions are in the airport notes.

## Reference

- [Entropy catalog](Entropy-Catalog.md): the seven entropy checks, verdicts and penalty rule.
- [What's Next](Whats-Next.md): the project backlog.

## Reading Evidence

Executed local checks, static findings, historical claims and live client/CI behavior
are separate evidence categories. The post-commit static score is 42/100 after the
Node app became tracked and assessed; the prior corrected working-tree observations
were 55/100. Those scope differences are explained in the Implementation record.
Seven judgment checks remain unanswered. A static score does not override the
demonstrated Python and real-browser test results or certify security.

Raw reports, history receipts, browser traces and screenshots remain ignored local
artifacts. See [Contributing](../CONTRIBUTING.md) and
[testing/history guidance](../skills/harness-audit/references/TESTING-AND-HISTORY.md)
for the commands and boundaries.