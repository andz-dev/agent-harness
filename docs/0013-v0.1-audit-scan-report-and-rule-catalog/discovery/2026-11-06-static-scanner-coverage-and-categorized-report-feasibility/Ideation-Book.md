---
type: 'Ideation Book'
id: '0013'
version: 'v0.1'
title: 'Static scanner coverage and categorized report feasibility'
description: 'Discovery run: can one category per check and static scanner-presence detection extend the audit report for Python, Node, Go and Rust.'
doc_scope: 'proposal'
status: 'draft'
created: '2026-11-06'
updated: '2026-11-06'
stale_after: '2026-11-20'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [harness, discovery, report, scanners]
sources:
  - 'research/2026-11-06-gap-analysis.md'
  - 'research/2026-11-06-prior-art-scanner-taxonomy.md'
  - 'hypothesis.jsonc'
  - 'spike/verdict.json'
  - 'https://github.com/ossf/scorecard/blob/main/docs/checks.md'
---

# Static scanner coverage and categorized report feasibility

## Table Of Contents

- [Context](#context)
- [Prompt Analysis](#prompt-analysis)
- [Gap Table](#gap-table)
- [PoC Candidate Result](#poc-candidate-result)
- [Scope Tiers](#scope-tiers)
- [Risks](#risks)
- [Next Actions](#next-actions)
- [References](#references)

## Context

The owner asked to make finding categories visible in the audit report, to bring in the missing Security, SBOM and linter scans, to enrich report data, sidecars and reports, to carry backlog items into the next version, and to leave the city map untouched. This run is in agent mode: it made every choice below without the owner, and each is listed under [Next Actions](#next-actions). The question extends the closed 0011 coverage-expansion subject. The run started under 0011 and was merged into 0013 at the owner's request, which is the follow-on version.

## Prompt Analysis

| Prompt item | Interpretation |
|---|---|
| Categories in the finding report | One stable, unscored category per check, shown in JSON and Markdown |
| Security, SBOM, linters | Static detection of configured scanners and declarations; never proof that a scan ran |
| And so on | Licenses, security policy and coding-standards documents |
| Beautify and enrich report data, sidecars, reports | A category summary and coverage section in `report.md`; matching fields in `report.json`, `triage.json` and `llm_tasks.json` |
| Languages | Python and Node plus Go and Rust, chosen earlier by the owner |
| Backlog into the next version | WN-017, WN-018, WN-029 and report items B-85, B-94 |
| City map untouched | No file under `apps/harness-city/` changes |

## Gap Table

<!-- atlas:table=gaps -->
| Gap | Evidence (measured) | Why it matters |
|---|---|---|
| Findings carry no category | `report.schema_category_keys` | A reader cannot see where problems cluster ([research](research/2026-11-06-gap-analysis.md)) |
| Coverage is absent from Markdown | `report.render_mentions_coverage` | Declared and unknown topic states are invisible |
| Security checks are nearly absent | `scan_topics.secret_scanning_check_ids` | Only secret scanning has a check |
| SBOM and license are unchecked | `scan_topics.sbom_check_ids` | Supply-chain declarations cannot be reported |
| SAST and vulnerability tooling are unchecked | `scan_topics.sast_check_ids` | Presence signals used by Scorecard ([1](#ref-1)) are missing |
| Go and Rust have no checks | `adapters.checks_applying_to_go_or_rust` | Detected components get no quality signal |
| Coding standards documents are unchecked | `scan_topics.coding_standards_doc_check_ids` | Backlog WN-029 stays open |

## PoC Candidate Result

<!-- discovery:verdict -->

**Verdict: GO** (every go criterion met, no kill criterion met)

- Decision informed: Whether the next version adds an unscored category layer plus static scanner-presence checks, or keeps pillar-only reporting and defers the scanners.
- Next: `spec-workflow`, Run the spec workflow for a follow-on version: an unscored category field on findings and coverage, a category summary in report.md, and static scanner-presence checks for Python, Node, Go and Rust.
- Evidence: real (card minimum real)

| Criterion | Role | Expected | Actual | Met |
| --- | --- | --- | --- | --- |
| C1 `mismatches` | go | == 0 | 0 | yes |
| C2 `discriminating_cases` | go | >= 8 | 15 | yes |
| C3 `detection.mismatches` | go | == 0 | 0 | yes |
| C4 `detection.discriminating_negatives` | go | >= 4 | 5 | yes |
| C5 `partition_complete` | go | == true | true | yes |
| C6 `oracle_controls.pillar_mapping_detected` | go | == true | true | yes |
| C7 `oracle_controls.broken_detector_detected` | go | == true | true | yes |
| K1 `ambiguous_check_ids` | kill | > 3 | 1 | no |
| K2 `mismatches` | kill | > 3 | 0 | no |

Open questions (owner, lean):

- Is the nine-category set (testing, code_standards, ci_pipeline, security, supply_chain, agent_guidance, docs, workflow, infrastructure) final? (human; lean: Accept it; categories are unscored labels and can be extended without changing any score.)
- Should new scanner-presence checks ever count toward the 0-100 score or gate a level? (human; lean: No: keep them an overlay like infrastructure, since presence is not proof that a scan ran or passed.)
- Does WN-017 (SBOM generation for this repository in CI) join this version? (human; lean: Keep it separate: it produces an artifact, while this version only detects declarations in audited repositories.)
- Which folder carries the follow-on spec? (agent; lean: A new numbered folder through the spec workflow, because 0011 is closed.)

Does not prove:

- That any scanner ran or passed: detection reports configuration presence only.
- That Go and Rust detection works on a real Go or Rust repository: only documented config names are tested.
- That the oracle is complete: it covers a sample of checks written by the same agent from cited sources, not every check.
- Anything about the Harness City map, which this version leaves untouched.

<!-- /discovery:verdict -->

Evidence grade: `real`. The spike read four tracked harness-audit files, classified all 116 checks into nine categories and compared 27 of them with an oracle written from cited prior art ([1](#ref-1)). Two must-fail controls fire: a pillar-only mapping disagrees with the oracle, and an unanchored detector wrongly accepts near-miss file names. Detection by config name covers the documented names for golangci-lint ([3](#ref-3)), rustfmt ([4](#ref-4)), clippy ([5](#ref-5)), cargo-deny ([6](#ref-6)) and CycloneDX ([2](#ref-2)).

It does not prove that any scanner ran or passed, that detection works on a real Go or Rust repository, that the oracle is complete or independent of its author, or anything about the city map. The mandatory design prototype stage still follows in the spec workflow.

Rerun:

```bash
uv run --python 3.14 python docs/0013-v0.1-audit-scan-report-and-rule-catalog/discovery/2026-11-06-static-scanner-coverage-and-categorized-report-feasibility/spike/spike.py --check
uv run --python 3.14 python ~/.agents/skills/discovery-poc/scripts/hypothesis.py verdict docs/0013-v0.1-audit-scan-report-and-rule-catalog/discovery/2026-11-06-static-scanner-coverage-and-categorized-report-feasibility --check
```

## Scope Tiers

- Tier 1, asked for: category field and summary; Security, SBOM, license and linter presence checks for Python, Node, Go and Rust; richer JSON, sidecars and Markdown.
- Tier 2, evidence-backed: Scorecard-style signals for SAST, vulnerability tooling, dependency updates and security policy ([1](#ref-1)); coverage observations shown in `report.md`.
- Tier 3, deferred: running any scanner, advisory lookups, scoring or gating on these checks, SBOM generation for this repository (WN-017), unused-dependency analysis (B-85) and all city work.

## Risks

- The oracle and rules share an author; the owner should review the nine categories and the oracle cases.
- Presence of a config file can be read as assurance; every report line must say "configured", not "passed".
- Go and Rust checks are tested on documented file names only.

## Next Actions

1. Follow the verdict's route: run the spec workflow for a follow-on version of the audit (open decision below).
2. The owner confirms or overrides each lean in `hypothesis.jsonc`: category set, overlay-only scoring, WN-017 kept separate.
3. Resolved by the owner: the follow-on is the new folder 0013, and this run now lives in it.
4. Decisions taken without the owner: this run first ran in place under 0011 (since merged into 0013); it kept all real evidence in tracked skill files; it omitted the parent repository's audit report from Git and quoted counts only.

## References

- <a id="ref-1"></a>[1] OpenSSF, "Scorecard checks", GitHub, retrieved 2026-11-06. https://github.com/ossf/scorecard/blob/main/docs/checks.md
- <a id="ref-2"></a>[2] CycloneDX, "Specification overview", retrieved 2026-11-06. https://cyclonedx.org/specification/overview/
- <a id="ref-3"></a>[3] golangci-lint, "Configuration file", retrieved 2026-11-06. https://golangci-lint.run/docs/configuration/file/
- <a id="ref-4"></a>[4] Rust project, "rustfmt", retrieved 2026-11-06. https://rust-lang.github.io/rustfmt/
- <a id="ref-5"></a>[5] Rust project, "Clippy configuration", retrieved 2026-11-06. https://doc.rust-lang.org/clippy/configuration.html
- <a id="ref-6"></a>[6] Embark Studios, "cargo-deny config", retrieved 2026-11-06. https://embarkstudios.github.io/cargo-deny/checks/cfg.html
