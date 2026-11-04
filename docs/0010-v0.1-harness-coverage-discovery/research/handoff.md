---
type: 'Handoff'
title: 'Harness coverage discovery handoff'
description: 'Read first for the measured scope, derived verdict, unattended decisions and exact rerun commands.'
status: 'active'
created: '2026-11-04'
updated: '2026-11-04'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [discovery, handoff]
sources: ['../Ideation-Book.md', '../hypothesis.jsonc', '../spike/result.json', '../spike/verdict.json']
---

# Discovery Handoff

## 1. State

| Artifact | Path | State |
| --- | --- | --- |
| Ideation and prompt analysis | [Ideation Book](../Ideation-Book.md) | Written from the discovery template; verdict block derived by the hypothesis tool |
| Frozen decision | [Card](../hypothesis.jsonc), [lock](../hypothesis.lock.json) | Frozen before spike code and results |
| Real evidence | [Probe](../scripts/probe.py), [findings](../data/findings.json), [coverage](../data/coverage.json) | Eleven allowlisted tracked files, seven topics |
| Independent expectations | [Oracle](../data/oracle.json) | Sixteen source facts recorded before spike code; kind labels manually curated |
| Synthetic edge cases | [Sample](../data/sample/sample.json), [provenance](../data/sample/provenance.json) | Seven seeded cases; no real values copied |
| Reproducible result | [Spike](../spike/spike.py), [result](../spike/result.json) | Byte-for-byte rerun check |
| Machine decision | [Verdict](../spike/verdict.json) | Authoritative next route and action; do not reconstruct it from prose |
| Prior art | [Research](prior-art.md) | Fetched primary sources; search failure corrected explicitly |
| Measurements and limits | [Findings note](coverage-findings.md) | Bounded source claims, not a general security assessment |
| Legacy editor material | [Original research](../Research.md) | Unchanged and still parked |

Not started: wayfinder, Research-Paper, Whitepaper, Plan, Architecture, production tests or
product implementation. This spike does not replace the mandatory later design prototype.

## 2. Decisions Taken Without The Owner

1. Reused the expressly selected ID 0010, chose v0.1 for the new coverage subject, no cluster,
   and the slug harness-coverage-discovery. Kept the editor research byte-for-byte rather than
   silently repurposing its historical claims.
2. Used unattended agent mode. "Implementation" means executing this discovery only.
3. Grouped the request into seven topics; rules includes technology and infrastructure, while
   security is cross-cutting rather than a new scored pillar.
4. Used this repository as real evidence; no clone acquisition or sample dependency installation.
5. Populated the exact existing folder from discovery contracts because normal scaffolding allocates
   a new ID and rejects an existing target. Imported shared assets rather than copying helper modules.
6. Kept the seven-pillar weights frozen. Implementation-kind labels are curated metadata, not a
   new automated classifier; runtime state remains unknown throughout the inventory.
7. Created no raw store and retained no private source output. Normalized counts, booleans and
   public source paths/digests only; runtime logs stay ignored.
8. Omitted the optional HTML report in agent mode. Did not stage or commit the synthetic sample
   merely to make process gate G1 green.
9. Corrected the delegated Agent Skills search using the official specification; did not preserve
   the unsupported conclusion that no specification existed.
10. Repaired only live references to the renamed research. Preserved historical prose inside the
    original file. Existing documentation-alignment work is not reverted or represented as this work.

## 3. Verified Locally

The probe, seeded sample, frozen card, spike and generated verdict have separate rerun commands.
Validation outcomes are recorded in [artifact metadata](../artifact-meta-ideation.jsonc).
The discovery gate output distinguishes decision gates from optional process warnings.
Final citation checks validate external URL reachability as well as local citation anchors.

| Check | Observed outcome |
| --- | --- |
| Hypothesis and verdict reproduction | Pass; card digest unchanged and generated verdict block matches |
| Discovery decision gates | G0, G2, G4 and G6 pass; G5 logging pairs also pass |
| Discovery process warnings | G1 sample uncommitted; G3 optional HTML report omitted |
| Seeded sample and spike reproduction | Pass; seven synthetic cases, sixteen source facts, zero mismatches |
| Final online citation QA | Ideation Book and prior-art note each have zero errors and zero warnings |
| Bundle docs audit | Seven Markdown files; zero unresolved issues |
| New script diagnostics and symbol lint | No editor errors; Ruff F checks pass |
| Mermaid rendering | Both diagrams render nonempty in isolated Chromium; screenshot inspected, kept in ignored logs |
| Extraction integrity | task integrity passes; no runtime baseline update needed |
| Repository docs/publication check | Fails on the already committed Trail note lacking type frontmatter; no other failure printed |
| Installed logging contract | Nine tests, two failures and one error after resolving shared imports |
| Installed discovery tool suite | 353 tests, 51 failures, 56 errors and six skips; not a green prerequisite-suite result |

Aggregate validation is **not green**. The repository failure is the existing note
[backlog collision learning](../../../.trail/learnings/2026-11-04-resolve-backlog-id-collisions-on-merge-andreas.md),
whose missing type field was confirmed at HEAD. Historical learnings are not edited here.
The installed tool-suite failures include deployed-layout asset-root fixtures, imports and stale
logging event expectations; not every failure has been triaged. No external skill or test was
changed, skipped or weakened. The frozen experiment's decision gates pass independently, but
these broader failures must not be presented as a fully verified toolchain or unattended-track readiness.

The installed-suite commands used the existing Python runtime and per-command shared import paths:

```bash
PYTHONPATH="$HOME/.agents/shared/scripts:$HOME/.agents/skills/discovery-poc/scripts" \
   skills/harness-audit/.venv/bin/python \
   "$HOME/.agents/skills/discovery-poc/tests/test_logging_contract.py"
PYTHONPATH="$HOME/.agents/shared/scripts:$HOME/.agents/skills/discovery-poc/scripts" \
   skills/harness-audit/.venv/bin/python -m unittest discover \
   -s "$HOME/.agents/skills/discovery-poc/tests" -v
```

### 3.1 Still Unverified

- Cross-repository precision, other-language adapters and technology-complete coverage.
- Actual hook installation, CI execution, branch policies, local trust or installed extensions.
- MCP runtime authorization, process sandboxing, skill authority or supply-chain integrity.
- The production airport integration; the current airport is an explicitly simulated prototype.
- The earlier Docker evidence redaction defect remains unfixed; broader sensitive-topic publishing
  requires its own reviewed correction and regression tests.
- No production runtime/browser test result is claimed by this discovery.

## 4. Probe Usage

Run from the repository root with its existing locked environment. No setup or install is needed
when that environment is present; a missing shared asset is a blocker, not permission to install.

```bash
PY=skills/harness-audit/.venv/bin/python
B=docs/0010-v0.1-harness-coverage-discovery
"$PY" "$B/scripts/probe.py" --list
"$PY" "$B/scripts/probe.py" --evaluation-only --summary
"$PY" "$B/data/sample/generate_sample.py" --check
"$PY" "$B/spike/spike.py" --check
"$PY" "$HOME/.agents/skills/discovery-poc/scripts/hypothesis.py" verdict "$B" --check
"$PY" "$HOME/.agents/skills/discovery-poc/scripts/gate_check.py" "$B"
"$PY" "$HOME/.agents/shared/scripts/citation_qa_workflow.py" "$B/Ideation-Book.md" --mode final
"$PY" "$HOME/.agents/skills/docs-reorg-audit/scripts/docs_audit.py" --root "$B"
```

The probe's --only selection is for focused findings and replaces the latest findings file;
rerun without --only before the full gate check. Spike --check does not replace saved results.
Log files are runtime diagnostics, not evidence to commit or model-ingest as raw output.

## 5. PoC Candidate Result And Verdict

Read [the derived machine contract](../spike/verdict.json) and the generated block in the
Ideation Book. The result uses real tracked evidence plus a separately graded synthetic sample.
It has zero oracle mismatches; controls reject a corrupt count, an unknown-to-verified promotion,
and an escaped input path. Those controls are contract checks, not a full adversarial security test.

## 6. Next Steps

1. Follow the verdict's next route/action, carrying the inventory and measured gaps into clarification.
2. Resolve human-owned questions in the frozen card using their recorded leans: default repository
   scope, frozen weights and the separate committed-summary decision.
3. Carry the agent-owned question on imported execution receipts into the next stage without a
   cloud connection or invented provider verification.
4. Before product work, address safe evidence reads/redaction, task reachability, unsupported
   component reporting and status-preserving report-to-city projection.
5. Obtain owner approval for any adapted-runtime baseline changes, runtime/browser checks,
   external corpus acquisition or host/cloud evidence collection when those become necessary.

No technology commitment or production implementation is authorized merely by this discovery result.
