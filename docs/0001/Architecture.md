---
type: 'Architecture'
id: '0001'
version: 'v0.1'
title: 'Standalone Extraction: As-Built Boundaries'
description: 'Initial extracted components, trust boundaries and provenance layout.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['EXTRACTION.md', 'extraction-manifest.json', 'git:23251df']
---

# Standalone Extraction: As-Built Boundaries

## Components

| Component | Role at extraction |
| --- | --- |
| skills/harness-audit | Read-only audit pipeline, schema, catalog, prompts and tests |
| apps/harness-city | Static visualization, adapter, assets and vendor modules |
| extraction-manifest.json | Allowlisted source/target mappings and checksums |
| tools and Taskfile | Local checks, synthetic demo and standalone packaging |
| docs/0002 | Relocated source as-built records, not a new execution request |
| docs/0003 | Owner-provided future roadmap |

## Trust and Data Flow

Repository files feed the static audit; reports feed the city adapter; synthetic data
feeds the public demo. The audit never runs audited code. Standalone HTML embeds its
selected data and must be reviewed before sharing.

The source repository's commit/tree pins remain in [EXTRACTION.md](../../EXTRACTION.md).
Only `23251df` is the local initial-extraction anchor. Source prehistory, private local
stores and report datasets were not imported.

## Runtime and Storage

The skill is Python-based; the city is a static browser application. No new database or
cloud deployment is inferred. Generated reports/builds/caches remain ignored. Original
licenses and [third-party notices](../../THIRD_PARTY_LICENSES.md) are retained.

Later `adapted-runtime` entries preserve the original source hash separately from the
current reviewed hash. This is intentional evolution, not proof the current tree is
byte-identical to the initial snapshot. See [Plan](Plan.md) and [Implementation](Implementation.md).