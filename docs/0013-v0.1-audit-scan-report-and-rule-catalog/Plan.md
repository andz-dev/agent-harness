---
type: 'Plan'
id: '0013'
version: 'v0.1'
title: 'Audit Scan Coverage, Categorized Report and Static Rule Catalog Plan'
description: 'Acceptance criteria and delivery slices for finding categories, static scanner-presence checks, a per-run rule catalog and the backlog items promoted into this version.'
doc_scope: 'proposal'
status: 'draft'
created: '2026-11-06'
updated: '2026-11-06'
stale_after: '2026-12-06'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
skills: [harness-audit]
tags: [plan, harness, report, catalog, scanners]
sources:
  - 'Ideation-Book.md'
  - 'discovery/2026-11-06-static-scanner-coverage-and-categorized-report-feasibility/Ideation-Book.md'
  - 'research/2026-11-06-official-rule-references.md'
  - '../Whats-Next.md'
  - '../0011-v0.1-harness-coverage-expansion/Plan.md'
---

# Audit Scan Coverage, Categorized Report and Static Rule Catalog Plan

## 1. Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| AC-1 | A supported baseline repository | The new fields are added or removed | Score, seven pillar levels, weights, caps and entropy are byte-equivalent after removing only the additive fields; no category, scanner or catalog field affects arithmetic |
| AC-2 | Any core check, infrastructure check, coverage observation or scanner-presence result | A report is built | Each carries exactly one category from the closed set `testing`, `code_standards`, `ci_pipeline`, `security`, `supply_chain`, `agent_guidance`, `docs`, `workflow`, `infrastructure`; a missing or unknown category fails validation; legacy reports without categories stay valid |
| AC-3 | A report | `report.md` is rendered | It shows per-category counts by status (pass, fail, unknown, not applicable), failed checks grouped by category with their pillar kept, a coverage section with each topic's applicability, evidence and freshness, and an appendix of passed and unknown checks and per-component results |
| AC-4 | Python, Node, Go, Rust and repository-neutral inputs | Scanner-presence checks run | Security (secret scanning, SAST, dependency-vulnerability tooling, security policy), SBOM declaration, license file, dependency-update tool, Go and Rust linter or formatter config and a coding-standards document are reported as `configured`, `not_found` or `unknown` with a safe locator; wording never says passed or clean; Go and Rust stay without a quality score |
| AC-5 | Any audit run | The run finishes | It writes `catalog.md` and `catalog.json` beside the report: every rule with id, category, title, level, gate, detector kind, what it inspects, limits, rationale and applicability; the content is deterministic for one catalog version and carries a digest recorded in `report.json` |
| AC-6 | A catalog rule | It is displayed | It links to verified official or standards-body sources from `checks/references.yaml` (title, publisher, URL, retrieved date, relation `resembles` or `informed_by`); the catalog states that links are orientation, not a conformance claim; no source text is copied |
| AC-7 | A finding in `report.md` or `report.json` | It is read | It links to or names its catalog entry, so a reader can see the rule, its limits and its references |
| AC-8 | `triage.json`, `triage.md`, `llm_tasks.json` and the run receipt | They are written | Each item carries its category and the catalog digest; schema versions move additively; older consumers keep working |
| AC-9 | The existing city converter and every file under `apps/harness-city/` | New reports are converted | The converter accepts the additive fields unchanged and `git diff` shows no change under `apps/harness-city/` |
| AC-10 | CI of this repository | The workflow runs | CycloneDX SBOMs for the skill and the app are produced as workflow artifacts, not committed (WN-017); this is separate from AC-4 |
| AC-11 | Python and Node components | Unused-dependency analysis runs (B-85) | Candidates are listed report-only with an allowlist for tooling packages and no entropy penalty or score effect |
| AC-12 | Every new runnable stage | Normal, verbose, error and termination paths run | The shipped lean-logging contract holds, collected content never appears in logs, logs stay uncommitted |
| AC-13 | Links in `checks/references.yaml` | `task check` runs | Structure, https scheme, retrieved date and category coverage are tested offline; a separate opt-in task checks reachability, because the audit itself stays static and offline |
| AC-14 | Every check id in the catalog | Tests run | Each has a category, a catalog entry and at least a category-level reference; a must-fail control proves a check without category is rejected |

## 2. Problem Statement

The report shows failures only by scored pillar, hides coverage, has no category view and says nothing about
Security, SBOM, license or Go and Rust linting. A reader also cannot see what a rule means or which public practice
it resembles. This version adds presentation and presence evidence around the frozen score, never a new verdict.

## 3. Inputs Analyzed

[Discovery verdict](discovery/2026-11-06-static-scanner-coverage-and-categorized-report-feasibility/Ideation-Book.md#poc-candidate-result):
GO on real evidence. [Official source list](research/2026-11-06-official-rule-references.md). Backlog rows WN-017,
WN-018, WN-029 and skill items B-85 and B-94 ([backlog](../Whats-Next.md)). The 0011 contracts (bounded reads, no
execution, partial reports) carry over unchanged.

## 4. Scope

In: category contract and data; report, triage and sidecar enrichment; static catalog with references; scanner
presence for Python, Node, Go and Rust plus repository-neutral checks; this repository's SBOM in CI; report-only
unused-dependency candidates.

Out: running any scanner, advisory lookups, scoring or gating on scanner presence, other languages, host or cloud
evidence, publishing real reports, and every change to the Harness City map, viewer, converter or design files.
WN-019 to WN-027, WN-030, WN-031 and WN-033 stay separate.

## 5. Decisions

| ID | Decision | Status |
|---|---|---|
| D1 | The nine categories are final | Owner-confirmed 2026-11-06 |
| D2 | Scanner-presence results are an unscored overlay, like infrastructure | Proposed; the owner asked for the reasoning, see below |
| D3 | WN-017 is in this version as its own slice, separate from audit detection | Taken from the owner's request to bring backlog items in |
| D4 | The catalog is static, deterministic and written on every run | Owner request |
| D5 | Category is stored as data per check and validated by test; the discovery classifier only seeded it | Agent decision, open to review |
| D6 | B-85 is report-only, because an entropy penalty would change the score and break AC-1 | Agent decision, open to review |
| D7 | The city map stays untouched | Owner instruction |

### Why scanner presence stays out of the score (D2)

- A configured tool does not prove a scan ran or passed; a number would suggest assurance the audit cannot give.
- The weights are frozen and calibrated against human scores (mean error about 5 points); new inputs would need a
  new calibration and would make old and new scores incomparable.
- Go and Rust have no scored adapter, so adding them would reward or punish repositories the score cannot read.
- A scoring signal for tool presence invites adding a config file to gain points.
- The infrastructure overlay already follows this pattern, and AC-1 from 0011 requires byte-equivalent scores.

The owner can reverse D2 later; that would be a separate calibrated version, not a silent change.

## 6. Backlog Disposition

Statuses in [Whats-Next](../Whats-Next.md) are `Promoted` to this plan and stay open until the work is finished.
The skill's own `BACKLOG.md` is hash-pinned in the extraction manifest, so its items are recorded here, not edited.

| Item | Disposition |
|---|---|
| WN-017 SBOM generation in CI | In scope, slice M5 (AC-10) |
| WN-018 audit overlays (supply chain, data protection, licenses, governance) | In scope as scanner-presence topics, slice M4 (AC-4); governance beyond license and security policy deferred |
| WN-029 coding standards and language linters | In scope for Go, Rust and a standards document, slice M4; first promoted to 0011 |
| WN-034, WN-035 | New rows for the categorized report and catalog, and for scanner presence |
| B-85 unused-dependency analysis | In scope report-only, slice M6 (AC-11) |
| B-94 passed, unknown and per-component tables in the Markdown report | In scope, slice M2 (AC-3) |
| WN-019 to WN-027, WN-030, WN-031, WN-033 | Not in scope; city, editor, browser-suite and host work stay separate |

## 7. Milestones

| Slice | Outcome | ACs | Depends on |
|---|---|---|---|
| M1 | Category data in catalog and infrastructure checks, schema fields, validation | AC-1, AC-2, AC-14 | None |
| M2 | Markdown and JSON enrichment, triage and llm_tasks sidecars | AC-3, AC-7, AC-8, AC-9, AC-12 | M1 |
| M3 | Reference data, catalog artifact, per-finding links, offline tests | AC-5, AC-6, AC-13 | M1 |
| M4 | Scanner-presence checks for Python, Node, Go, Rust and neutral topics | AC-4 | M1 |
| M5 | SBOM artifacts in this repository's CI | AC-10 | None |
| M6 | Report-only unused-dependency candidates | AC-11 | M2 |
| M7 | Full regression, integrity baseline review, docs, city-untouched check | all | M1 to M6 |

## 8. Risks

A catalog link can rot or be read as certification: keep wording to orientation and test structure offline.
Presence wording can be read as assurance: ban "passed" and "clean" for these results. Runtime files are hash
pinned: review baseline updates separately as in 0011. B-85 import scanning can misfire on tooling packages:
allowlist and report-only.

## 9. Validation And Definition Of Done

Commands are implementation gates, not results of this docs run. Run from the repository root.

**validate:** `task --dir skills/harness-audit check` and `task integrity`, then
`git diff --stat -- apps/harness-city` shows nothing.

**Stop when:** every AC maps to a passing test with a must-fail control, a real-repository audit run shows the
category summary, the coverage section and a catalog whose digest matches `report.json`, and the owner has
reviewed the category assignments and the reference mapping.

## 10. Next Stages

Architecture, Test Plan, Mocking Plan, Golden Dataset, Ontology and Implementation are not yet written. The
mandatory design prototype stage still applies to the report and catalog layout.
