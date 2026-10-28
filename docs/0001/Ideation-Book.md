---
type: 'Ideation Book'
id: '0001'
version: 'v0.1'
title: 'Standalone Extraction: Reconstructed Intent'
description: 'Retrospective rationale for the initial standalone audit skill and city snapshot.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['EXTRACTION.md', 'git:23251df', 'docs/0002/README.md']
---

# Standalone Extraction: Reconstructed Intent

## Context

Retrospective reconstruction, not an original pre-implementation session. Commit
`23251df` introduced the standalone repository and reserved this folder as an empty
scaffold. The owner later requested basic documents in the named folders; this folder
now records that initial extraction while preserving its original `.gitkeep`.

## Problem and Goals

Make the existing audit skill and city usable independently of the source monorepo.
Keep the imported implementation traceable, publish only allowlisted material, and
provide synthetic demonstrations rather than private reports or invented findings.

## Decisions and Limits

- Clean snapshot, not an import of the source repository's complete Git history.
- Original source hashes are provenance; do not assume those commits exist locally.
- Imported 0039 documents live in 0002 and retain their historical evidence limits.
- Runtime integrity and publication checks are useful, not security certification.
- No historical interview, missing requirement or original pass result is invented here.

## Source and Handoff

[Extraction provenance](../../EXTRACTION.md) owns the source pin, allowlist and exclusions.
Continue with [Plan](Plan.md), [Architecture](Architecture.md) and
[Implementation](Implementation.md). The [history crosswalk](../History-Match.md)
separates this topic from later roadmap and airport work.