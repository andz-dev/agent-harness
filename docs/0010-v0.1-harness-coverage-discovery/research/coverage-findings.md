---
type: 'Research'
title: 'Measured harness coverage and implementation gaps'
description: 'A bounded inventory of current source facts, outstanding controls and evidence-to-city gaps.'
status: 'active'
created: '2026-11-04'
updated: '2026-11-04'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [harness, coverage, discovery]
sources: ['../data/oracle.json', '../data/findings.json', '../data/coverage.json', '../spike/result.json']
---

# Measured Coverage

Observation: 2026-11-04, repository HEAD `3fb0c80da21cf5469b127ce26800ada9df62bc79`.
Inputs are tracked working-tree files, not a detached committed snapshot. Source digests are
recorded in the [spike result](../spike/result.json). The independent [oracle](../data/oracle.json)
predates spike code; its implementation-kind labels are curated, not automatically inferred.

| Topic | Measured fact | Status and limit | Evidence |
| --- | --- | --- | --- |
| Rules, technology and infrastructure | 56 core checks; 60 infrastructure checks; pillar weights total 100 | Shipped static logic; four infrastructure checks are judgments. Other-language and infrastructure-only repositories can exit before a report. | `rules.core_count`, `rules.infra_count`, `rules.unsupported_early_exit` |
| Lint | A root ruff command is declared; no ESLint, Biome, Prettier or oxlint dependency in the app manifest | Declaration plus a bounded missing-dependency observation, not a run or exhaustive config audit | `lint.python_lint_check`, `lint.node_lint_dependency` |
| Pipelines | CI calls task check; root declares app:test; hook calls task precommit | Task indirection exists; this spike does not resolve its complete call graph or prove hook installation | `pipelines.ci_task_check`, `pipelines.root_app_test`, `pipelines.hook_task_precommit` |
| SBOM | No core title explicitly names SBOM, CycloneDX or SPDX; unused-dependency analysis is explicitly unimplemented | Missing dedicated title coverage, not proof every related heuristic is absent | `sbom.core_sbom_titles`, `sbom.unused_dependency_unimplemented` |
| MCP | No core title explicitly names MCP or Model Context Protocol | Dedicated coverage not demonstrated by the core catalog; no server launch or host config read | `mcp.core_mcp_titles` |
| Skills | No core title names skill provenance | Orientation checks are not a skill provenance assessment | `skills.core_skill_provenance_titles` |
| Extensions | Infrastructure check INF-V05 names declared extensions or settings | Declaration coverage exists; installation, enabled state and trust are unknown | `extensions.infra_extension_declaration` |
| City evidence | Converter omits infrastructure; airport prototype uses a preset | Report-to-airport integration is not implemented; explicitly labeled prototype remains a prototype | `rules.converter_infra_projection`, `rules.airport_demo_preset` |

Numeric and boolean rows are validated through the discovery skill's shared findings helper.
The [normalized inventory](../data/coverage.json) stores identifiers, states, source paths and
digests only. It stores no source excerpts, server commands, endpoint identities or credentials.

## Prompt Gaps And Tiers

- Tier 1: the seven requested topic groups, technology-aware applicability, report provenance,
  unknown states, and a city view that represents audit evidence rather than simulated maturity.
- Tier 2: target-level pipeline attribution, safe redaction and bounded file reads, unsupported-stack
  reporting, source freshness and independent execution receipts. These are evidence-backed
  follow-up questions, not shipped features.
- Tier 3: machine-level installed tools, cloud connections, fleet rollups, recalibrated scores,
  elaborate traffic and editor expansion. No permission or feasibility result is inferred for them.

The [existing proposal](../../0009-v0.1-city-overlays-road-traffic-harness-evidence/Design-Proposal.md)
already describes supply-chain, release, secrets, data-protection and governance overlays.
The [backlog](../../Whats-Next.md) tracks WN-017, WN-018, WN-020, WN-028 and WN-029.
Generating this repository's SBOM (WN-017) is distinct from auditing another project's SBOM.

## Safety Leads

The preceding assessment found that a Docker space-delimited ENV value can remain in the
evidence expression at [infra_checks.py](../../../skills/harness-audit/scripts/infra_checks.py#L233).
That lead was independently checked with a synthetic string before this discovery; it is not
a new result of the frozen spike and no real credential was read. It remains unfixed.
Treat source-contained reads and output redaction as prerequisites before broader secret/MCP checks.

## Gotchas / Unverified

- Eleven real files and sixteen discriminating facts are not a representative repository corpus.
- A title search cannot establish semantic completeness or security effectiveness.
- The unknown-assurance control tests the inventory contract, not production client enforcement.
- The escaped-path control rejects an unlisted relative path before opening it. It is not a full
  symlink-race or operating-system sandbox test.
- The earlier private static self-audit is not an input to this spike and is not copied into this bundle.
- No production tests, browser suite, new checks, cloud state or score calibration were executed here.

## Implication

The next stage should settle applicability, provenance, check status, assurance depth and compatible
report-to-city projection before choosing more checks or visuals. Existing weights and prototype
labels remain unchanged. The discovery verdict authorizes only its recorded next route, not shipping.
