---
type: 'Documentation Index'
title: 'Agent Harness Documentation'
description: 'Entry points for current specifications, historical source records and evaluation notes.'
status: 'active'
created: '2026-10-28'
updated: '2026-11-04'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [documentation, history]
---

# Agent Harness Documentation

## Documentation Alignment

Independent [WN-024](Whats-Next.md#open) tracks the full current-specification and
sidecar alignment with developer-asset-manager's workflow. Start with the
[change overview](Documentation-Alignment.md) and
[lightweight kickoff](lightweight/2026-11-04-documentation-alignment-kickoff.md).
The current chain is not yet complete; imported 0002 and retrospective 0008 are
evidence inputs, not substitutes for newly authored stages or fresh verification.
Every numbered folder now has a [Workflow Report](#folder-rename-map) listing which stages
exist and which were never run; missing historical stages stay absent.

## Per-Folder Basic Sets

Each requested folder now contains the four basic retrospective artifacts, reconstructed
from its own Git history and retained source documents. Original files remain alongside
them; no historical interview or unperformed test is invented.

| Topic | Ideation | Plan | Architecture | Implementation |
| --- | --- | --- | --- | --- |
| 0001: initial extraction | [Ideation](0001-v0.1-standalone-extraction-retrospective/Ideation-Book.md) | [Plan](0001-v0.1-standalone-extraction-retrospective/Plan.md) | [Architecture](0001-v0.1-standalone-extraction-retrospective/Architecture.md) | [Implementation](0001-v0.1-standalone-extraction-retrospective/Implementation.md) |
| 0003: harness roadmap | [Ideation](0003-v0.1-harness-roadmap-evidence-matched/Ideation-Book.md) | [Plan](0003-v0.1-harness-roadmap-evidence-matched/Plan.md) | [Architecture](0003-v0.1-harness-roadmap-evidence-matched/Architecture.md) | [Implementation](0003-v0.1-harness-roadmap-evidence-matched/Implementation.md) |
| 0004: v1.2 and agreement | [Ideation](0004-v0.1-audit-release-retrospective/Ideation-Book.md) | [Plan](0004-v0.1-audit-release-retrospective/Plan.md) | [Architecture](0004-v0.1-audit-release-retrospective/Architecture.md) | [Implementation](0004-v0.1-audit-release-retrospective/Implementation.md) |
| 0005: infrastructure overlay | [Ideation](0005-v0.1-infrastructure-overlay-matched/Ideation-Book.md) | [Plan](0005-v0.1-infrastructure-overlay-matched/Plan.md) | [Architecture](0005-v0.1-infrastructure-overlay-matched/Architecture.md) | [Implementation](0005-v0.1-infrastructure-overlay-matched/Implementation.md) |
| 0006: level calibration | [Ideation](0006-v0.1-infrastructure-calibration-retrospective/Ideation-Book.md) | [Plan](0006-v0.1-infrastructure-calibration-retrospective/Plan.md) | [Architecture](0006-v0.1-infrastructure-calibration-retrospective/Architecture.md) | [Implementation](0006-v0.1-infrastructure-calibration-retrospective/Implementation.md) |
| 0007: airport evaluation | [Ideation](0007-v0.1-airport-overlay-evidence-matched/Ideation-Book.md) | [Plan](0007-v0.1-airport-overlay-evidence-matched/Plan.md) | [Architecture](0007-v0.1-airport-overlay-evidence-matched/Architecture.md) | [Implementation](0007-v0.1-airport-overlay-evidence-matched/Implementation.md) |

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
| [0001](0001-v0.1-standalone-extraction-retrospective/) | Initial-extraction retrospective; original empty scaffold preserved |
| [0002](0002-v0.2-harness-audit-as-built-adoption/README.md) | Imported, relocated source as-built documents; preserve provenance |
| [0003](0003-v0.1-harness-roadmap-evidence-matched/research/README.md) | Earlier proposed roadmap, not a completion claim |
| [0004](0004-v0.1-audit-release-retrospective/research/README.md) | v1.2 agreement and release records |
| [0005](0005-v0.1-infrastructure-overlay-matched/research/README.md) | Infrastructure coverage mapping |
| [0006](0006-v0.1-infrastructure-calibration-retrospective/research/README.md) | Infrastructure-level evaluation material |
| [0007](0007-v0.1-airport-overlay-evidence-matched/research/airport-assets.md) | Airport evaluation and current metaphor decisions |
| [0009](0009-v0.1-city-overlays-road-traffic-harness-evidence/Design-Proposal.md) | Draft proposal: city overlays, road traffic, committed harness evidence |

Amendment 2026-11-04: folders were renamed to the versioned pattern (see the map below);
they are not presented as an original spec workflow, and `doc_scope` marks each artifact
as history, relocated or proposal.
The generated airport simulator is local build output, not a document to commit.
Its reproducible build instructions are in the airport notes.

## Folder Rename Map

IDs are unchanged; 0008 already matched the pattern. Old paths appear only in Git history and
in `.trail/` session notes, which are not rewritten.

| Old path | Current folder | Workflow Report |
| --- | --- | --- |
| `docs/0001/` | [0001-v0.1-standalone-extraction-retrospective](0001-v0.1-standalone-extraction-retrospective/) | [report](0001-v0.1-standalone-extraction-retrospective/Workflow-Report.md) |
| `docs/0002/` | [0002-v0.2-harness-audit-as-built-adoption](0002-v0.2-harness-audit-as-built-adoption/README.md) | [report](0002-v0.2-harness-audit-as-built-adoption/Workflow-Report.md) |
| `docs/0003/` | [0003-v0.1-harness-roadmap-evidence-matched](0003-v0.1-harness-roadmap-evidence-matched/) | [report](0003-v0.1-harness-roadmap-evidence-matched/Workflow-Report.md) |
| `docs/0004/` | [0004-v0.1-audit-release-retrospective](0004-v0.1-audit-release-retrospective/) | [report](0004-v0.1-audit-release-retrospective/Workflow-Report.md) |
| `docs/0005/` | [0005-v0.1-infrastructure-overlay-matched](0005-v0.1-infrastructure-overlay-matched/) | [report](0005-v0.1-infrastructure-overlay-matched/Workflow-Report.md) |
| `docs/0006/` | [0006-v0.1-infrastructure-calibration-retrospective](0006-v0.1-infrastructure-calibration-retrospective/) | [report](0006-v0.1-infrastructure-calibration-retrospective/Workflow-Report.md) |
| `docs/0007/` | [0007-v0.1-airport-overlay-evidence-matched](0007-v0.1-airport-overlay-evidence-matched/) | [report](0007-v0.1-airport-overlay-evidence-matched/Workflow-Report.md) |
| `docs/0008-v0.1-harness-history-and-quality/` | unchanged | [report](0008-v0.1-harness-history-and-quality/Workflow-Report.md) |
| `docs/0009/` | [0009-v0.1-city-overlays-road-traffic-harness-evidence](0009-v0.1-city-overlays-road-traffic-harness-evidence/Design-Proposal.md) | [report](0009-v0.1-city-overlays-road-traffic-harness-evidence/Workflow-Report.md) |

0009 had no recorded version; `v0.1` is assigned at this migration, not a historical claim.

## Reading Evidence

Executed local checks, static findings, historical claims and live client/CI behavior
are separate evidence categories. The recorded post-commit static score for
`90e9a52` was 42/100 after the Node app became tracked and assessed; the prior
corrected working-tree observations were 55/100. Those historical scope differences
are explained in the Implementation record. Seven judgment checks were unanswered
in those observations. Neither the scores nor the historical Python/browser results
are current-run evidence or security certification.

Raw reports, history receipts, browser traces and screenshots remain ignored local
artifacts. See [Contributing](../CONTRIBUTING.md) and
[testing/history guidance](../skills/harness-audit/references/TESTING-AND-HISTORY.md)
for the commands and boundaries.