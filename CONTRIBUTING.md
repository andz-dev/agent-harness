---
type: 'Development Guide'
title: 'Contributing to Agent Harness'
description: 'Development setup, verification commands and evidence boundaries for changes to this repository.'
status: 'active'
created: '2026-10-28'
updated: '2026-10-30'
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

## Pi and Pendant

The [Pi](https://pi.dev) coding agent runs here in two hosts that share one agent
directory (`~/.pi/agent`): the `pi` terminal CLI and the **Pendant** VS Code extension
(`cdervis.vscode-pi`). Pendant bundles its own Pi SDK, so a VS Code checkout needs no
`pi` CLI on PATH; both read the same extensions, settings and MCP configuration.

```bash
code --install-extension cdervis.vscode-pi   # Pendant (also recommended in .vscode/extensions.json)
trail build                                  # local code graph for the trail MCP server
trail build --check                          # fail if that graph is stale
```

`.pi/mcp.json` declares one project MCP server, `trail`, which answers code-map
queries (`trail_find_code`, `trail_find_all`, `trail_trace_calls`, `trail_file_api`,
`trail_repo_map`). It serves the graph `trail build` writes to `.trail/cache/`, which
is git-ignored and rebuilt per machine; without a build the server starts and exposes
no tools. Rerun `trail build` after a large change, or let its automatic refresh handle
normal edits.

Two per-machine gates sit outside the repository, so a fresh clone stays inert until
it is approved locally: Pi project trust (`~/.pi/agent/trust.json`, one entry per
repository) and the MCP adapter's admission policy (`settings.projectServers` in
`~/.pi/agent/mcp-adapter.json`). Neither is committed. Pendant additionally starts only
in a VS Code workspace you have trusted; that editor trust is a third, separate gate.

`.vscode/settings.json` keeps the agent's sandbox at `workspace`: writes stay inside the
checkout, network access is allowed, and `.env` is denied on top of Pi's built-in
credential denials. Loosen it in your own user settings, not in this tracked file.

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