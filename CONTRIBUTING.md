---
type: 'Development Guide'
title: 'Contributing to Agent Harness'
description: 'Development setup, verification commands and evidence boundaries for changes to this repository.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

# Contributing to Agent Harness

Read [repository rules](AGENTS.md), then the owning app or skill guide. Preserve dirty
working-tree changes that are not yours. Do not create commits, switch branches or
replace test baselines unless the owner explicitly requests that action.

## Setup and Checks

Use Python/uv/Task and Node 22+ (Node 24 is used in CI). Setup installs the existing
locked Python environment and the exact locked browser-test package/matching Chromium:

```bash
task setup
task tools:test
task app:test
task check
```

On Linux, Chromium may require system libraries. CI installs them with the Playwright
installer. If local system dependencies require privilege, ask the owner to install
them; never route a password through an agent or silently skip browser tests.

`task check` is the full merge gate. Focused examples:

```bash
task --dir skills/harness-audit test -- tests/test_run_checks.py
task app:test -- airport.spec.js --project=desktop-chromium
```

Browser tests own loopback port 8765 by default; `CITY_TEST_PORT` can select another
unprivileged free port. They never reuse an unknown server. Screenshots, traces, JSON
and HTML results stay ignored under the app's `test-results/` and `playwright-report/`.
Do not auto-approve new golden images. Inspect failures before changing assertions.

## Audit and History

The [testing/history reference](skills/harness-audit/references/TESTING-AND-HISTORY.md)
defines the static/runtime separation and history commands. Raw audit reports may be
private and stay ignored. Compare only compatible engine/catalog observations; keep
unanswered judgments and untracked-working-tree limits visible.

The auditor does not execute audited repositories. Runtime checks of this trusted
development checkout are separate from auditing arbitrary repositories.

## Changes and Review

- Start with a concrete behavior, source owner and a cheap discriminating check.
- Add a real synthetic regression for bugs and observe it fail before the correction.
- Change city design before changing its metaphor; keep click explanations and levels aligned.
- Preserve source hashes when intentionally updating adapted-runtime baselines.
- Keep docs and current results separate from historical pass records.
- Review the [retrospective bundle](docs/0008-v0.1-harness-history-and-quality/Map.md)
  for the reconstructed history and the current quality work.