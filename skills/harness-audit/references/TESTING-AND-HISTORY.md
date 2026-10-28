---
type: 'Reference'
title: 'Automated Tests and Audit History'
description: 'Read when repeating audits, comparing regressions or separating repository tests from a static harness assessment.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
sources: ['../SKILL.md', '../../../tools/audit_history.py', '../../../Taskfile.yml']
---

# Automated Tests and Audit History

## Two Evidence Paths

The static auditor reads files and Git metadata. It does not import, install, build,
plan infrastructure, start services or execute tests from an audited repository.
Seeing tests, hooks or CI configuration is not proof that they ran.

Runtime verification is a separate owner-authorized activity. Before that activity,
disclose the exact repository/ref, command, dependency/setup effects, network/secrets
requirements and output locations. Treat repository scripts as untrusted until the owner
authorizes execution in an appropriate isolated environment. Never infer test permission
from an audit request, static score or a previous approval for another repository/ref.

Record a runtime test result separately: commit and dirty state, exact command, runtime
and lockfile identity, observation time, executed/passed/failed/skipped counts, exit code,
artifact locations and relevant environment limits. A skipped or empty suite is not a pass.
Do not promote this receipt into a static finding or claim a historical CI run occurred.

## Repeated Static Audits

1. Keep each raw report in a new ignored output directory. Review before sharing:
   reports and judgment answers may contain private repository excerpts.
2. Record repository/ref, tool version, catalog version/hash, engine fingerprint,
   clone mode, judgment coverage and the report digest.
3. Use the same engine, catalog and judgment conditions for a controlled comparison.
   Engine fixes or catalog changes require a fresh baseline, not a flattering score trend.
4. Compare individual check states and pillar levels, not just the final score. Keep
   added, removed, unknown, not-applicable and changed states distinct. Separate script
   regressions from changes in model verdicts or newly answered judgments.
5. Keep shallow/blobless-history and unsupported-stack limitations explicit. A dirty
   working tree and untracked files are not identical to a committed snapshot.
6. To assess an old revision, read an explicitly selected local snapshot with the same
   current trusted engine. Do not execute code from that revision or silently check out,
   reset, clean or rewrite the owner's working tree.

## Development Repository Commands

These commands belong to the Agent Harness development checkout. A copied skill may
not include its root-level developer tools; do not claim they were installed elsewhere.

From the development repository root, run a new static observation:

```bash
task --dir skills/harness-audit audit -- ../.. --out ../../reports/self-audit/run-name --name agent-harness
python3 tools/audit_history.py record --repo . --report reports/self-audit/run-name/report.json --label run-name
python3 tools/audit_history.py compare .data/path-to-before/record.json .data/path-to-after/record.json
```

Use the exact receipt path printed by `record`, not the illustrative `.data/path-to-*`
names above. The recorder creates an immutable owner-only run under
`.data/storage/local/file/harness-audit/history/YYYY-MM-DD/UTC-run-id/record.json`.
It stores normalized check states and fingerprints, not source excerpts, report names,
remote URLs, credentials or raw limitation text. The raw report remains the source for
explanation; receipt limitation counts/digests and unanswered judgment IDs preserve the
fact that coverage is incomplete without republishing its contents.

The selected repo must already ignore `.data/`. Existing storage must be owner-only;
unsafe paths, symlinks, tracked storage and incompatible records fail without changing
permissions or overwriting prior runs. A report older than a changed engine is refused.
Current engine fingerprints are not a signed attestation of the original process;
working-tree Git observations are captured at recording, and untracked contents are
not fingerprinted. Regenerate reports close to recording for meaningful provenance.

## This Repository's Runtime Tests

The owner authorizes these development checks separately from auditing another repo:

```bash
task setup
task tools:test
task app:test
task check
```

`task app:test` launches real Chromium against only this trusted app's synthetic data,
including desktop/mobile layouts, actual option controls, rebuild/material/GPU stability,
PNG decoding and a network-blocked offline build. It owns its loopback server and does
not reuse an unknown service. Missing browser prerequisites and page/console errors fail.

`task check` also runs the existing skill suite, local tool tests, deterministic demo
conversion, packaging and integrity/documentation/publication checks. Native runner output
and ignored reports are execution evidence; the presence of the command in this reference
is only declared guidance. CI uses the same entry point; local success does not prove a
remote CI run or client instruction loading.

## Regression Discipline

For a real defect, add a minimal synthetic regression at the affected public boundary,
observe red, implement the smallest correction and rerun the same check. Keep negative
canaries for unsafe input and gate bypasses. Never delete, skip or weaken tests to make
the score or suite pass. Keep public examples synthetic and raw histories local.