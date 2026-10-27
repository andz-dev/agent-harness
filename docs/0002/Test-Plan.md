---
type: 'Test Plan'
id: '0002'
version: 'v0.2'
title: 'Frozen Harness Audit Verification Map'
description: 'Criterion-traced tests and evidence limits for source-only adoption; existing behavioral suites are mapped, not claimed executed.'
status: 'draft'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [testing, traceability, harness-audit]
sources: ['Plan.md section 1', 'Architecture.md sections 5 through 11', 'Prototype-Decision.md']
---

<!-- markdownlint-disable-next-line MD025 -->
# Frozen Harness Audit Verification Map

## Scope And Entry Points

The adopted skill's AGENTS.md requires its task runner. A future approved
behavioral rerun uses `task --dir skills/harness-audit check`;
one file uses `task --dir skills/harness-audit test -- tests/test_score.py`.
No `task setup`, dependency installation, target audit or model call is
authorized by documenting these commands. This run checks documentation and
the source-only prototype; all behavioral rows below are verification targets.

## Criterion And Scenario Matrix

| Scenario | Type | Criteria | Boundary Or Expected Result | Existing Evidence Pointer |
| --- | --- | --- | --- | --- |
| INF-01 | Infrastructure | AC-1 | No frozen-source diff; original versions retained | contract-probe.sh |
| UNIT-02 | Unit | AC-2 | Python/Node, workspace, sample and unsupported cases | test_detect_stack.py |
| INT-03 | Integration | AC-3 | Real synthetic config/runner/CI/hook files yield path evidence; target code never runs | test_run_checks.py |
| INT-04 | Integration | AC-4 | Full/shallow/non-Git history and entropy remain distinct | test_git_signals.py |
| UNIT-05 | Unit | AC-5 | Invalid, absent, duplicate and unverified agent answers do not produce unsupported passes | test_llm_layer.py |
| E2E-06 | End-to-end | AC-6 | First pass, agent tasks, second pass and specialized check-ID replacement | test_audit.py |
| UNIT-07 | Unit | AC-7 | Gate, ratio, component, cap, entropy and arithmetic boundaries | test_score.py |
| SMOKE-08 | Smoke | AC-8 | Valid report outputs; no supported component exit 3; invalid report exit 4 | test_audit.py |
| UNIT-09 | Unit | AC-9 | Triage gain/effort ordering stays counterfactual | test_triage.py |
| E2E-10 | End-to-end | AC-10 | Proposal leaves target unchanged; explicit apply creates missing files and preserves existing ones | test_bootstrap.py |
| INT-11 | Integration | AC-11 | Documentation never equates static L2 with observed runtime enforcement | Plan section 3; Architecture section 8 |
| INF-12 | Infrastructure | AC-12 | Old active entry point absent, retirement manifest and historical notices present | source probe; repository catalog gate |
| UNIT-13 | Unit | AC-13 | Historical/live hashes differ and tool/doc versions are not conflated | research/As-Built-Findings.md |
| SMOKE-LOG | Smoke | AC-14 | Logging N/A: docs and declared throwaway probe only; frozen CLI instrumentation unchanged | Architecture section 6 |

All eight named Python test modules are under
`skills/harness-audit/tests/`. They are not copied, edited,
unskipped or weakened. The observed 137 declarations are not a collection count.
The category README files in this folder are documentation placeholders, not tests.

## Negative Controls And Limitations

Future approved behavioral verification must include invented quotes, unknown
task IDs, arithmetic corruption, unsupported components, empty/missing evidence,
existing bootstrap files and failed output validation. It must not execute a
private target's code to prove a static detector. A high score is not a test
success or enforcement certificate. No fake report replaces the real
end-to-end path. Isolated Git fixtures must avoid user credentials/network.

## Current Verification Status

Source-contract probe: executed, pass, structural only. Behavioral suite, model
agreement, calibration and live repository qualification: not run. Documentation
gates and cross-artifact joins are recorded in Workflow-Report.md after the
consolidated pass. Storage follows the review boundary in Architecture section 10.
