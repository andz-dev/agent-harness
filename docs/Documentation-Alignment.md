---
type: 'Change Overview'
title: 'Agent Harness Documentation Alignment'
description: 'Independent change inventory for completing the current specification chain and its sidecars; read before authoring or reviewing the alignment work.'
doc_scope: 'proposal'
status: 'draft'
created: '2026-11-04'
updated: '2026-11-04'
stale_after: '2026-11-18'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [documentation, specification, alignment]
sources:
  - 'Owner request, 2026-11-04: separate backlog and begin documentation changes'
  - 'Snapshot 19277973cdb3d31396cfd9fd2176fec9d2861e92'
  - 'developer-asset-manager: docs/AGENTS.md'
  - 'developer-asset-manager: agents/skills/engineering/spec-workflow-orchestrator/SKILL.md'
  - 'developer-asset-manager: agents/shared/references/artifact-handoff-contracts.md'
  - 'developer-asset-manager: agents/shared/references/artifact-meta-sidecar-schema.md'
  - 'developer-asset-manager: agents/shared/references/okf-frontmatter-template.md'
---

# Agent Harness Documentation Alignment

## Scope and Tracking

This is independent documentation work: local [WN-032](Whats-Next.md#open),
tracked by the tooling repository as WN-122, with no dependency on another bundle
or evaluation. The [lightweight kickoff](lightweight/2026-11-04-documentation-alignment-kickoff.md)
records the first delivered slice; this overview is not a completed specification chain.

Source evidence is pinned to `19277973cdb3d31396cfd9fd2176fec9d2861e92`.
The authoring work changes the working tree, not that evidence baseline. No fetch,
branch switch, reset, clean, push, installation or runtime-test permission is implied.

Use the developer-asset-manager full `spec-workflow-orchestrator` contracts and
owning stage templates, not the separate reduced agent track. Resolve the installed
skill and shared-reference paths explicitly; do not copy shared policies into this repo.

## Existing Material

| Area | Observed role | Treatment |
| --- | --- | --- |
| [0002](0002-v0.2-harness-audit-as-built-adoption/README.md) | Relocated full source chain, including stage sidecars, dataset and ontology | Preserve source provenance and imported validation; not a current chain |
| [0008](0008-v0.1-harness-history-and-quality/Implementation.md) | Reduced retrospective and historical quality receipts | Preserve M1-M6 results and dated scores; use cited facts as inputs |
| 0001 and 0003-0007 | Basic retrospective documents and retained topic research | Classify historical/proposal claims; do not fabricate omitted historical stages |
| [0009](0009-v0.1-city-overlays-road-traffic-harness-evidence/Design-Proposal.md) | Future city and audit proposals | Keep separate from implemented behavior and from this documentation work |

Adopt a living bundle under a topic cluster with a unique four-digit ID and version.
Reserve the exact folder at the planning handoff, after a target-local ID census.

Amendment 2026-11-04 (supersedes "do not rename historical folders"): the owner asked
to adjust folders 0001-0009 to the `NNNN-vX.Y-slug` pattern, so they were renamed with
IDs unchanged. Contents and provenance were preserved; see the rename map in
[the docs index](README.md#folder-rename-map). No new numbered bundle was created.

## Full Artifact Inventory

The required artifacts below are missing from, or need adaptation for, the living
chain even when an imported equivalent exists. The owning stage must produce its
own designed content; reverse extraction does not replace that stage.

| Artifact | Required content or change | Owning stage |
| --- | --- | --- |
| Map.md and decision tickets | Current constraints, decisions, unknowns and readiness; no invented historical interview | Wayfinder |
| Ideation-Book.md | Alignment objective, goals/non-goals, risks and locked decisions | ideation-book |
| Research-Paper.md | Pinned source/history evidence, methodology and limitations | research-paper |
| Whitepaper.md | System narrative, trade-offs and evidence boundaries | technical-whitepaper |
| Plan.md | Reviewed, testable ACs for completeness and semantic alignment | specs-gatekeeper |
| Prototype-Decision.md | A defined uncertainty, actual decision evidence and carry-forward constraints | prototype |
| Architecture.md | Inputs, AC decisions, component layers, ingress/egress, runtime, trust, data/storage, diagrams and files touched | architecture-gatekeeper |
| Test-Plan.md | Every AC mapped to scenarios, boundaries, failure paths and applicable test categories | testing-gatekeeper |
| Mocking-Plan.md | External-boundary mocks, fidelity, failures and consumer scenarios; internal logic stays real | mocking-gatekeeper |
| Golden-Dataset/dataset.json and dataset-guide.md | Deterministic synthetic positive, edge and negative records, schema and scenario mapping | golden-dataset-gatekeeper |
| ontology/Ontology.md and ontology.json | Canonical terms, aliases, source traces and AC/scenario/dataset joins | ontology-gatekeeper |
| Implementation.md | New alignment tasks, dependencies, phase exit criteria, decision log and resume state | implementation-document-gatekeeper |
| Workflow-Report.md | Stage status, dependencies, actual checks, warnings and blockers | spec-workflow-orchestrator |

Include `research/`, decision-ticket and test-scaffold directories where their
stages require them. Existing executable tests are inventoried and linked, not
copied or reported as new passing scaffolds. OWL, CSV and an extra implementation
checklist remain optional. A prototype file's presence is not a passed stage.

## Sidecars and Supporting Data

| Group | Required outputs |
| --- | --- |
| Root stage run state | artifact-meta-wayfinder.jsonc, artifact-meta-ideation.jsonc, artifact-meta-research.jsonc, artifact-meta-whitepaper.jsonc, artifact-meta-plan.jsonc, artifact-meta-prototype.jsonc, artifact-meta-architecture.jsonc, artifact-meta-testing.jsonc, artifact-meta-mocking.jsonc, artifact-meta-implementation.jsonc |
| Nested stage run state | Golden-Dataset/artifact-meta.jsonc and ontology/artifact-meta.jsonc |
| Citation QA | citation-qa.jsonc in each generated document folder requiring citation validation |
| Architecture projection | architecture-model.jsonc derived from component-layer and files-touched tables |
| Planned operations | change-set.jsonc for the new alignment operations only |
| Evidence supplements | evidence.jsonc; Trace.md and artifact-meta-trace.jsonc when adopting the code tier |
| Lightweight kickoff | artifact-meta-2026-11-04-documentation-alignment-kickoff.jsonc derived by specs-lightweight |

Each stage sidecar follows the shared schema: artifact, generatedAt, mode, inputs,
outputs, validation.status/checks and optional notes. The aggregate 0008 sidecar
does not replace individual run records for new stages. Do not copy its historical
pass claims into the new sidecars. Unrun checks remain warnings or blockers.

Frontmatter owns durable metadata: type, title, description, lifecycle, dates,
owner, sources, trust and applicable id/version/doc_scope. Use history, relocated,
proposal or as-built according to the claims; split mixed claims where needed.
JSON artifacts retain their own metadata shape, not YAML frontmatter.

## Semantic Corrections and Evidence

The rows below are code-observed findings at the pin, not newly executed tests.
Each living-chain claim must also record its exact document section/line, source
function, relevant test/check, evidence class and aligned/drift/incomplete/unknown result.

| Document claim | Implementation anchor | Change to carry forward |
| --- | --- | --- |
| Drift prompt rules 2 and 9; catalog ORI-09 | skills/harness-audit/scripts/llm_layer.py: missing_commands and plan; scripts/run_checks.py: Ctx.targets | Parsed bare target names are pooled across runners; selected excerpts and positive counts are not exhaustive command/cwd correctness |
| Drift prompt rules 5 and 6 | skills/harness-audit/scripts/llm_layer.py: verify_evidence and apply_answers | Normalized nearby file quotes and one surviving quote are validated; excerpt spans, two-source reasoning and candidate disposition are not mechanically enforced |
| Canonical pointers and judgment confidence | skills/harness-audit/scripts/llm_layer.py: plan and apply_answers | Separate scripted special cases from semantic reviewer obligations |
| Setup and check guidance | Taskfile.yml and skills/harness-audit/Taskfile.yml | Root setup also installs browsers; skill guidance must agree with its runner; setup network effects differ from static audit execution |
| Receipt written atomically | tools/audit_history.py: record | Exclusive non-overwrite creation writes directly to the final path; it is not atomic publication |
| Current score and verification wording | docs/0008-v0.1-harness-history-and-quality/Implementation.md: M6, Final Results and Post-Commit Handoff | Preserve 2026-10-28 receipts and commit 90e9a52 as history, not current runs |
| Design consistency | tools/check.py: design | One-way check: matched HTML pillar colors must occur in DESIGN.md; no full semantic consistency claim |

The [code-tier skill](https://github.com/andz-dev/developer-asset-manager/blob/main/agents/skills/engineering/reverse-docs-from-code/SKILL.md)
supplies as-built inventories and source evidence. The
[history-tier skill](https://github.com/andz-dev/developer-asset-manager/blob/main/agents/skills/engineering/reverse-docs-from-git-history/SKILL.md)
supplies commit-backed chronology, not proof that commit intent succeeded.
Use owned generated regions only; preserve owner prose. Keep any history Plan
separate from the designed acceptance Plan. No frozen dataset or scored holdout changes.

## Delivery Sequence

1. Kickoff: separate backlog, lightweight receipt, this overview and index pointers.
2. Discovery and pre-plan: settle placement/scope, record decisions, then ideation, research and whitepaper.
3. Design: reviewed Plan, mandatory prototype decision and Architecture.
4. Downstream artifacts: Testing, Mocking, Dataset, Ontology and Implementation in that order; reconcile stable AC joins.
5. Consolidated documentation verification: metadata, links/anchors, schemas, citations, rendered diagrams, evidence joins, model and change-set.
6. Guidance corrections and optional gate integration: separately reviewed where they touch frozen baselines or executable tooling.

Every phase uses Objective, Read first, Constraints, validate, Stop when and a
Document note. New tasks stay open until their own criteria hold; old M6 checkboxes
are not new-task completion. Template examples do not authorize new runtime architecture.

## Validation and Boundaries

The permitted kickoff check is `python3 tools/check.py` from this repository root.
It checks extraction integrity, docs/design patterns, synthetic demo data and
publication patterns; it does not prove full workflow or semantic correctness.
Validate the kickoff sidecar with the explicitly resolved specs-lightweight tool.

The new chain needs its owning validators, citation/diagram checks and a recorded
AC-to-decision-to-scenario-to-fixture-to-concept-to-task reconciliation. Resolve
tool paths once and record checks actually run. New validator integration is proposed,
not silently added to `task check`.

Skill/prompt edits are adapted-runtime baseline changes: disclose affected records
and obtain review before changing their hashes. Preserve source_sha256 provenance.
No task check, application/browser tests, dependency installation or audited code
execution is authorized by this documentation kickoff. Raw reports remain local.
