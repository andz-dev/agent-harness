---
type: 'Research'
title: 'Gap analysis: scan coverage and report categories in harness-audit'
description: 'Measured gaps between the requested scan and report scope and what the catalog, detectors and renderer provide today.'
status: 'active'
created: '2026-11-06'
updated: '2026-11-06'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [research, harness, gap-analysis]
sources:
  - '../data/findings.json'
  - 'research/2026-11-06-prior-art-scanner-taxonomy.md'
---

# Gap analysis: scan coverage and report categories in harness-audit

Subject kind: docs/repository (the harness-audit skill in this repository). Counts are a 2026-11-06 snapshot.

## Prompt items

| Prompt word | Interpretation | Registry | Measured size |
|---|---|---|---|
| categories in the finding report | a stable category on every finding, visible in JSON and Markdown | none today | 116 check ids, 0 schema `category` keys |
| Security | secret scanning, SAST, dependency-vulnerability tooling, security policy | partial | 1 secret-scanning check id |
| SBOM | SBOM file or generation declaration found statically | none | 0 check ids |
| Linters | linter and formatter config per ecosystem | Python and Node only | 0 Go/Rust check ids |
| and so on | licenses, coding-standards documents | none | 0 check ids each |

## Local evidence (counts only)

The probe in `scripts/probe.py` reads tracked skill files and writes `data/findings.json`.

- 56 core and 60 infrastructure check ids exist: `checks.core_check_ids`, `checks.infra_check_ids`.
- Six of eight scan topics have no check id: `scan_topics.topics_without_checks`.
- Secret scanning has one check id (`scan_topics.secret_scanning_check_ids`) and dependency-vulnerability tooling one (`scan_topics.dependency_vulnerability_check_ids`, a Terraform-only scanner list).
- No check id mentions SAST, SBOM, license, Go or Rust linters or coding-standards documents (`scan_topics.sast_check_ids`, `scan_topics.sbom_check_ids`, `scan_topics.license_check_ids`, `scan_topics.go_lint_check_ids`, `scan_topics.rust_lint_check_ids`, `scan_topics.coding_standards_doc_check_ids`).
- Go and Rust manifests are already detected as unsupported ecosystems (`adapters.go_rust_manifests_listed`), but no check applies to them (`adapters.checks_applying_to_go_or_rust`).
- The report renderer groups failures by scored pillar only (`report.render_groups_by_pillar`); it mentions neither coverage nor categories (`report.render_mentions_coverage`, `report.render_mentions_category`).

## Local report evidence (one run, not committed)

The 2026-11-06 run of the audit on the parent repository has 42 coverage observations over six components and seven topics: security 2 declared and 4 unknown, code standards 2 declared and 4 unknown, dependencies 6 declared, MCP and skills 0 declared. Its Markdown report shows none of this. Command: `jq` over its `report.json` (counts only; the report belongs to another repository and stays out of Git).

## Gap table

<!-- atlas:table=gaps -->
| Gap | Evidence (measured) | Why it matters |
|---|---|---|
| Findings carry no category | `report.schema_category_keys` | A reader cannot see where problems cluster |
| Coverage is absent from Markdown | `report.render_mentions_coverage` | Declared and unknown topic states are invisible |
| Security checks are nearly absent | `scan_topics.secret_scanning_check_ids` | Secret scanning is the only security topic with a check |
| SBOM and license are unchecked | `scan_topics.sbom_check_ids` | Supply-chain declarations cannot be reported |
| SAST and vulnerability tooling are unchecked | `scan_topics.sast_check_ids` | Scorecard-style presence signals [1] are missing |
| Go and Rust have no checks | `adapters.checks_applying_to_go_or_rust` | Detected components get no quality signal |
| Coding standards documents are unchecked | `scan_topics.coding_standards_doc_check_ids` | Backlog WN-029 stays open |

## Observations that change the design

- Category must be separate from pillar: a check such as the lockfile or dependency-bot check sits in a pillar but belongs to a dependency category.
- Presence detection is the honest ceiling: no check may claim a scan ran or passed [1].

## References

[1] OpenSSF Scorecard checks, https://github.com/ossf/scorecard/blob/main/docs/checks.md, retrieved 2026-11-06 (see the prior-art note).
