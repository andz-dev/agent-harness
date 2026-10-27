---
type: 'Plan'
id: '0002'
version: 'v0.2'
title: 'Harness Audit As-Built Adoption Plan'
description: 'Checkable criteria for documenting and adopting the frozen harness-audit implementation while retiring the old setup solution.'
status: 'active'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [plan, adoption, harness-audit]
sources: ['Map.md', 'Whitepaper.md', 'Research-Paper.md', 'research/As-Built-Findings.md']
---

<!-- markdownlint-disable-next-line MD025 -->
# Harness Audit As-Built Adoption Plan

## 1. Acceptance Criteria

These describe the adopted source, not a request to change it. Runtime behavior
is a future verification target unless an executed check is explicitly recorded.

| ID | Given / When / Then |
| --- | --- |
| AC-1 | Given the owner-selected source, when this effort ends, then the pinned harness-audit source has no changes and code versions remain unchanged. |
| AC-2 | Given a local repository, when component detection is used, then Python/Node components, sample/tooling exclusions and unsupported ecosystems are represented with limitations. |
| AC-3 | Given the live catalog, when static checks are evaluated, then evidence identifies found/searched paths and supported config/runner/CI/hook conventions without executing target code. |
| AC-4 | Given local Git evidence, when entropy/history checks run, then missing or shallow history remains explicit and no cleanup is performed. |
| AC-5 | Given selected tasks and supplied model answers, when evidence is verified, then unverifiable pass/fail claims and unanswered tasks become unknown rather than successful findings. |
| AC-6 | Given static, Git and LLM findings, when assembled, then check-ID replacement and remaining findings feed one report without inventing independent-vote consensus. |
| AC-7 | Given findings and components, when scored, then gates, 0.6 ratio, tracked-file weighting, seven weights, hard caps, verification dependence and entropy feed arithmetic-checked results. |
| AC-8 | Given assembled results, when the audit emits them, then schema validation precedes report output, CLI exit codes are documented and limitations remain visible. |
| AC-9 | Given failed checks and fixes metadata, when triage is produced, then counterfactual score-gain/effort ordering is distinguished from project business priority. |
| AC-10 | Given an audit report, when bootstrap is requested, then proposals cover failed-check-related missing files, existing alternatives are skipped, placeholders remain explicit and target creation requires --apply. |
| AC-11 | Given a high static level, when results are explained, then no runtime test success, activated hook, rejected commit, security certification or live-client adherence is claimed. |
| AC-12 | Given the stopped 0036 solution, when retirement is recorded, then active source is removed, docs are marked historical, the catalog is refreshed and installed-target retirement is not falsely claimed. |
| AC-13 | Given historical research and current source, when specs are derived, then provenance, version differences, reported results and deferred backlog work stay distinct. |
| AC-14 | Given documentation-only adoption, when handoff occurs, then all chain artifacts and traceability exist, validation results are actual, and logging is N/A because no production code is authored or amended. |

## 2. Problem And Inputs

The original adapter-oriented solution did not fulfill the broader assessment
intent. The owner selected an already-written replacement, prohibiting edits.
Required input is its SKILL.md and controlling source, supported by the supplied
historical backlog/catalog and the three pre-plan artifacts in this folder.

## 3. Scope And Conflicts

| Earlier intent or historical statement | As-built disposition |
| --- | --- |
| Runtime qualification and activation | Not provided by the frozen audit; no target execution |
| Independent agent review of every concern | Selected task/excerpt workflow instead |
| Digest-bound merge/apply | Not implemented; bootstrap is explicit create-only CLI behavior |
| Historical provisional weights/formula | Use current score.py and live catalog, preserving history |
| Documentation v0.2 | Does not change tool 0.1.0 or report/catalog 0.1 |
| Repository stdlib/logging conventions | Document the adopted PyYAML/jsonschema/CLI implementation as-is; do not refactor it |

In scope: source inspection, retirement and retrospective documentation.
Out: new features, skill edits, live-repository audits, installation, deployment,
remote fetch, model calls and bootstrap application. Preserve unrelated work.

## 4. Approach And Risks

Use the closed as-built map, code pin and historical reconciliation. Treat
existing test declarations as verification targets, not proof they ran here.
Static labels and model quote verification have semantic limits. Counterfactual
triage is not an approval to apply proposals. Storage references the shared
policy (historical source reference);
the adopted CLI's `--out` contract is documented without claiming policy migration.

## 5. Milestones And Done Contracts

### M1 Source And Retirement

- Objective: stop the old implementation and preserve the replacement (AC-1, AC-12, AC-13).
- Read first: Map Notes; research/As-Built-Findings.md Source Pin and Retirement Boundary.
- Constraints: no harness-audit edits, deployment cleanup or unrelated changes.
- `validate:` `bash docs/0002/prototype/contract-probe.sh`
- Stop when: frozen source comparison and retirement source checks pass.

### M2 As-Built Specification

- Objective: trace implemented behavior and limitations through the chain (AC-2 through AC-11).
- Read first: section 1; Prototype-Decision.md; Architecture.md sections 4 through 10.
- Constraints: no new promised runtime capability or fabricated test results.
- `validate:` `uv run --python 3.14 python scripts/verify.py --only docs`
- Stop when: actual documentation gates pass and all criteria join to scenarios and records.

### M3 Handoff And Preservation

- Objective: finalize metadata/model/change-set and qualification limits (AC-1, AC-13, AC-14).
- Read first: Test-Plan.md; ontology/ontology.json concept.source_snapshot; Workflow-Report.md.
- Constraints: keep verification gaps visible; no implicit commit or sync.
- `validate:` `git diff --exit-code 766dd40add66b2806bab5c8d0926d3b5d13056a7 -- skills/harness-audit`
- Stop when: source remains unchanged and executed artifact-check outcomes are recorded.

## 6. Open Questions And Next Steps

No product choice blocks as-built documentation. Future runtime execution,
additional ecosystems, merging, privacy hardening and independent-model
evaluation remain backlog/follow-up scope. Produce the prototype record and
architecture before sequential testing, mocking, dataset, ontology and handoff.
