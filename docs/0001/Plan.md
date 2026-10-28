---
type: 'Plan'
id: '0001'
version: 'v0.1'
title: 'Standalone Extraction: Retrospective Plan'
description: 'Evidence-derived acceptance boundaries for the initial standalone snapshot.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['EXTRACTION.md', 'git:23251df', 'docs/0001/Ideation-Book.md']
---

# Standalone Extraction: Retrospective Plan

## Acceptance Boundaries

| ID | Observable requirement reconstructed from the extraction |
| --- | --- |
| E-1 | Included skill/runtime/assets have explicit source-to-target provenance and hashes. |
| E-2 | Private reports, original datasets, secrets, environments and generated bundles are excluded. |
| E-3 | Synthetic city examples are distinguished from real audit findings. |
| E-4 | Existing code remains usable through local setup/check/build entry points. |

## Scope and Sequence

The recorded sequence is extraction, provenance/packaging, synthetic demonstration and
standalone checks. Later city changes, audit v1.2 and new quality tooling are not
retroactively attributed to the initial snapshot.

## Validation Contract

Objective: preserve the snapshot's traceability without replaying source operations.
Read first: [provenance](../../EXTRACTION.md), [Architecture](Architecture.md).
Constraints: retain source hashes, license notices and the empty scaffold; never execute
untrusted audited code or import excluded source data.
Validate: `task integrity` and `python3 tools/check.py` validate the current adaptation.
Stop when: provenance and current integrity agree, with historical results still labeled
as historical rather than newly executed by this retrospective.

## Open Limits

Original source operations and historical remote CI are not reproduced here. Current
runtime verification belongs to the current implementation gate, not to an invented
initial test session. See [Implementation](Implementation.md).