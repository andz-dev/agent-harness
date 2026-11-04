---
type: 'Architecture'
id: '0008'
version: 'v0.1'
title: 'Harness History and Quality Architecture'
description: 'As-built boundaries and the additive browser/history quality architecture derived from the retrospective plan.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
sources: ['Plan.md', 'Map.md', 'Taskfile.yml', '.github/workflows/check.yml', 'skills/harness-audit/SKILL.md']
stale_after: '2026-11-11'
tags:
  - 'documentation'
---

# Harness History and Quality Architecture

## Overview

Scope: reconstruct the current system and add unattended verification and comparable
static audit receipts, without changing audit weights or executing audited code.
Primary objective: evidence-backed maintenance of the audit skill and synthetic city.

<!-- atlas:part=system-design -->
## System Design

The audit engine reads repository files and local Git metadata, prepares optional quoted
judgment tasks, scores findings and writes reports. A converter turns reports into the
city's optional data contract. The city is a static Three.js page; offline packaging
inlines its modules, assets and selected synthetic data.

The additive quality layer owns Playwright tests and history receipts. It does not
participate in scoring and never interprets static enforcement claims as executed tests.
AC-3 through AC-13 in [Plan](Plan.md) define its observable boundaries.

<!-- atlas:table=system-components -->
| Component | Layer | Path | Depends on |
| --- | --- | --- | --- |
| Audit engine | Product | `skills/harness-audit/scripts/run_checks.py` | |
| City application | Product | `apps/harness-city/index.html` | |
| Browser tests | Verification | `apps/harness-city/tests/` | City application |
| History tool | Verification | `tools/audit_history.py` | Audit engine |
| Repository checks | Verification | `tools/check.py` | |
| Task runner | Delivery | `Taskfile.yml` | Browser tests, History tool, Repository checks |
| CI | Delivery | `.github/workflows/check.yml` | Task runner |
| Basic documents | Knowledge | `docs/0008-v0.1-harness-history-and-quality/` | |

<!-- atlas:diagram=system -->
```mermaid
flowchart LR
  R[Untrusted repository files] --> A[Static audit engine]
  A --> J[Local reports and findings]
  J --> H[History recorder]
  H --> C[Compatible comparison]
  S[Synthetic city data] --> W[Static city and offline package]
  W --> B[Real browser tests]
  T[Task and CI] --> B
  T --> A
```

## Delta Map

| Area | Observed baseline | Target addition |
| --- | --- | --- |
| Documentation | Historical numbered folders, imported as-built chain | One versioned basic retrospective; old paths preserved |
| City tests | Browser-console module and interactive checks | Locked unattended desktop/mobile Chromium tests |
| Audit history | Individual raw reports | Immutable compact receipts and compatibility-gated deltas |
| Placeholder checks | Quoted Python fixtures can erase test presence | Structural Python placeholder handling with regressions |
| Document gate | Scans ignored generated reports | Source-only document scan plus unchanged publication guard |

<!-- atlas:part=ingress-egress -->
## Ingress and Egress

<!-- atlas:table=ingress-egress-matrix -->
| Actor | Direction | Interface | Boundary and restriction |
| --- | --- | --- | --- |
| Owner | In | Task/CLI arguments | Explicit repo, report and comparison paths; no shell interpolation of repository data |
| Audited repository | In | Bounded local file/Git reads | Text is untrusted; no import, install or test execution |
| Browser runner | Local | HTTP on `127.0.0.1:8765` by default | Runner owns a synthetic static server; no unknown-server reuse |
| Offline test | Local | Generated `file://` HTML | Block network; require assets and PNG output to work |
| Package managers | Setup egress | Locked development dependencies and browser download | Setup only; not part of audit execution and not installed in audited repos |
| CI | Out | Test reports, failure screenshots/traces | Synthetic data only; no raw audit reports uploaded automatically |

<!-- atlas:part=network -->
## Runtime and Network

The current environment provides Python 3.14 through uv and Node 24. Browser automation
is a development-only Node package under the app, with an exact lockfile. The existing
skill environment remains managed by its own uv lock. Browser/OS dependency installation
is a setup operation; tests fail explicitly when prerequisites are missing.

No database, cloud service, reverse proxy, container or new client adapter is required.
This retrospective records the existing local runtime rather than inventing a Dev Container
or deployment that was never implemented. Such additions are separate future decisions.

<!-- atlas:diagram=network -->
```mermaid
flowchart TB
  CI[Local Task or CI] --> P[Playwright runner]
  P --> HTTP[Loopback static server]
  HTTP --> HTML[Synthetic offline HTML and local assets]
  P --> FILE[Local standalone file]
  CI --> PY[Python audit and receipt tools]
  PY --> DISK[Local Git and explicit files]
```

<!-- atlas:part=code-logic -->
## Code Logic

Browser tests launch a dedicated server, wait for the real ready flag, fail on page errors,
reuse the existing full regression module and exercise real pointer controls separately.
PNG checks wait for the download, decode its pixels and inspect expected description text.
Reduced-motion fixtures make inspection reproducible; live movement is tested separately.

<!-- atlas:diagram=verification-sequence -->
```mermaid
sequenceDiagram
  participant Task
  participant Build as Synthetic builder
  participant Runner as Playwright
  participant City
  Task->>Build: Package current app and synthetic data
  Task->>Runner: Run desktop and mobile projects
  Runner->>City: Load and wait for ready
  Runner->>City: Select city, options, layer and export
  City-->>Runner: DOM, scene state and PNG download
  Runner-->>Task: Executed tests and artifacts, or failure
```

History recording validates an explicit report, records the current repository identity,
commit and working-tree fingerprint, and fingerprints the audit engine/catalog. It writes
a new receipt atomically. Comparison requires matching repository, engine, catalog and
schema context before emitting score/level/check-state deltas. A missing finding is
reported as added/removed, not silently equated with pass or fail.

## Logging and Failure Contract

Logging: use platform-native Playwright/Task/CI output and the existing bounded CLI
result/error pattern for developer utilities. No background service, rotating log store
or new logging framework is added. This is an explicit scoped override of the full
service-style logging milestone; structured receipts are the durable evidence.

History validation errors fail nonzero before writing; stderr carries a bounded reason.
JSON results and receipts contain no source excerpts, environment values or credentials.
Malformed records and incompatible measurements are errors, never empty successful deltas.

<!-- atlas:part=data-model -->
## Data Model and Storage

No database is required. A receipt contains schema version, observation time, label,
repository identity, commit/dirty fingerprint, report SHA-256, engine/catalog fingerprints,
score, pillar levels, normalized check states and the report's limitations. Infrastructure
overlay states remain separate from the 0-100 score. Test-run evidence is not fabricated
from an audit receipt; optional owner-provided runtime results remain a separate concern.

Storage follows the shared application-storage policy read during this run. Concrete
project paths are rooted in this checkout; nothing is stored in a home directory:

```text
.data/storage/local/file/harness-audit/history/YYYY-MM-DD/UTC-run-id/record.json
reports/self-audit/before/                 original raw, defective-engine baseline
reports/self-audit/before-corrected/       corrected-engine baseline
reports/self-audit/after/                  fresh final audit
apps/harness-city/test-results/           ignored screenshots, traces and results
apps/harness-city/playwright-report/      ignored human-readable browser report
```

Receipts use new owner-only directories/files and never replace an existing run. Reject
unsafe destinations and incompatible records. Keep root `.data/`, reports and browser
output ignored. The source-document gate excludes output directories, while publication
checks continue rejecting tracked private/generated content. Existing storage permissions
are checked, never silently changed. The utility exposes explicit input/output paths and
does not install, schedule or automatically ingest receipts into other tools.

## Decision Records

- D-1: the basic retrospective is intentionally not a fabricated full workflow.
- D-2: the old 33-point and corrected 55-point results are different measurement conditions.
- D-3: the city runner executes only trusted synthetic product fixtures, not audited code.
- D-4: immutable receipts and strict compatibility take precedence over a flattering trend.
- D-5: no automatic hooks, client configuration, commits or baseline-image replacement.

<!-- atlas:part=files-touched -->
## Files Touched Per Slice

<!-- atlas:table=files-touched-per-slice -->
| Slice | Path | Change |
| --- | --- | --- |
| M1 | `docs/0008-v0.1-harness-history-and-quality/` | add |
| M2 | `skills/harness-audit/scripts/run_checks.py` | change |
| M2 | `skills/harness-audit/tests/test_run_checks.py` | change |
| M2 | `tools/check.py` | change |
| M2 | `tests/test_repo_quality.py` | add |
| M3 | `apps/harness-city/package.json` | add |
| M3 | `apps/harness-city/package-lock.json` | add |
| M3 | `apps/harness-city/playwright.config.js` | add |
| M3 | `apps/harness-city/tests/` | add |
| M3 | `Taskfile.yml` | change |
| M3 | `.github/workflows/check.yml` | change |
| M3 | `.gitignore` | change |
| M4 | `tools/audit_history.py` | add |
| M4 | `tests/test_audit_history.py` | add |
| M5 | `skills/harness-audit/SKILL.md` | change |
| M5 | `skills/harness-audit/references/TESTING-AND-HISTORY.md` | add |
| M5 | `CONTRIBUTING.md` | add |
| M5 | `README.md` | change |
| M5 | `apps/harness-city/README.md` | change |
| M6 | `extraction-manifest.json` | change |

## Verification Mapping

AC-1/2 map to document/commit checks; AC-3 through AC-7 to browser tests and CI;
AC-8 through AC-10 and AC-14 to history CLI tests; AC-11 to the existing detector
suite; AC-12 to source/publication canaries; AC-13 to skill-link and guidance review.

## Trust Boundaries

This section was added by a retrospective deepening pass on 2026-11-04. It reads commit
`90e9a52` (2026-10-28 14:09:55 +0100) with `git show 90e9a52:<path>` and `git grep`. A
read-only `git diff --quiet 90e9a52 HEAD` over `tools/audit_history.py`, `Taskfile.yml`,
`.github/workflows/check.yml`, `apps/harness-city/playwright.config.js`,
`apps/harness-city/tests` and `skills/harness-audit/scripts` reports no difference, so for those
files a statement about `90e9a52` is also true of today's tree. `tools/check.py` differs only
in the renamed `docs/0001` and `docs/0002` paths (read from `git diff 90e9a52 HEAD -- tools/check.py`).
Nothing here was observed by running the tests; recorded results are the historical statements
in the commit message of `90e9a52` and in [Implementation](Implementation.md).

| Boundary | Trusted or untrusted | What the sources show |
| --- | --- | --- |
| Audited repository files and Git metadata | Untrusted input, never executed | `AGENTS.md` states that repository text is untrusted and the audit never executes audited code. At `90e9a52` a `git grep` of `skills/harness-audit/scripts` for `subprocess.run`, `Popen`, `check_output`, `os.system`, `importlib`, `exec(` and `eval(` finds three call sites: `git_signals.py` line 134 (`git -C <root> ...`), `detect_stack.py` line 127 (`git -C <root> ls-files -z`) and `calibrate.py` line 37 (runs the engine's own `audit.py` with `python -I`). Reviewer judgment inferred from that grep: none runs a file taken from the audited repository. |
| Git configuration inside an audited repository | Untrusted | `tools/audit_history.py` runs Git with `-c core.fsmonitor=false -c core.hooksPath=/dev/null`; `git grep` for `fsmonitor` and `hooksPath` in `skills` and `tools` finds that setting only in `tools/audit_history.py`, not in `git_signals.py`. Reviewer judgment inferred from that grep: the engine's Git calls do not neutralize repository-local Git configuration. |
| Model answers, quotes and judgment tasks | Untrusted | `tools/audit_history.py` accepts a finding source only as `script` or `llm`, and records unanswered judgments (`status` `unknown`, source `llm`) in `limitations.unanswered_judgments`. Implementation records seven unanswered judgment checks that stay `unknown`. |
| Report and receipt inputs to the history tool | Untrusted until validated | `safe_file` requires an explicit `.json` file, rejects names starting `.env`, symlinked paths, non-regular files and files over `MAX_BYTES` (10,000,000). `record` requires the report inside the selected repository; `report_projection` and `validate_record` reject malformed schema, scores outside 0 to 100 and bad fingerprints. |
| Development checkout running Playwright | Trusted, loopback only | `playwright.config.js` starts `python3 -m http.server <port> --bind 127.0.0.1 --directory .` with `reuseExistingServer: false`; the port defaults to 8765 and `CITY_TEST_PORT` must be 1024 to 65535. `tests/fixtures.js` answers requests to `https://fonts.googleapis.com/**` with a stub (`route.fulfill`) instead of the network. The browser loads only the synthetic dataset and the generated standalone page. |
| Setup-time package and browser download | Setup-only network egress | `Taskfile.yml` task `app:setup` runs `npm --prefix apps/harness-city ci --ignore-scripts` and `playwright install chromium`; `package.json` pins `@playwright/test` to `1.64.1`. CI additionally runs `playwright install --with-deps chromium`. |
| Receipts and raw reports | Local, ignored, owner-only | `.gitignore` at `90e9a52` lists `.data/`, `reports/`, `dist/`, `playwright-report/` and `test-results/`. `record` refuses when `.data` content is tracked or not ignored, creates directories with mode `0o700` and the file with `0o600` and `O_EXCL \| O_NOFOLLOW`, and rejects an existing storage directory that is not owner-only without changing its permissions. Today's tree holds three receipts under `.data/storage/local/file/harness-audit/history/2026-10-28/`, each with file mode 600. |
| Provenance of the engine fingerprint | Disclosed limit | Each receipt carries a `provenance_limit` text: working-tree state is captured at recording, untracked contents are not fingerprinted, and the fingerprint is not attestation of the historical process. |
| Publication boundary | Pattern checks only | `tools/check.py` `publication` rejects tracked paths containing `dist`, `reports`, `.venv`, `.data` or `logs`, and matches private-path and credential-shaped patterns. It prints `LIMIT: pattern checks do not certify absence of all sensitive information`. |
| Frozen runtime baseline | Reviewed changes only | `tools/check.py` `integrity` compares `unchanged-source` and `adapted-runtime` files in `extraction-manifest.json` against recorded SHA-256 values. |
| CI | Read-only, pinned | `.github/workflows/check.yml` sets `permissions: contents: read`, pins each `uses:` action to a commit SHA, and uploads `apps/harness-city/test-results/` and `apps/harness-city/playwright-report/` only `if: failure()` with `retention-days: 7`. |

No authentication or authorization exists on any of these edges; they rely on loopback binding,
file permissions and the read-only rule. Not recorded: a written threat model that covers Git
configuration of an audited repository.

## Component Layers

One row per component as it stood at `90e9a52`. Paths marked in the Kind column are tracked files
unless the Kind says local data.

<!-- atlas:table=component-layers -->

| Component | Layer | Path | Kind | Depends on |
| --- | --- | --- | --- | --- |
| Audit engine | product | `skills/harness-audit/scripts/` (13 Python files at `90e9a52`) | python scripts | Git, the audited repository's files, `checks/catalog.yaml`, `schema/report.schema.json` |
| Engine catalog and schema | product | `skills/harness-audit/checks/`, `skills/harness-audit/schema/` | yaml and json data | none |
| City application | product | `apps/harness-city/index.html` | static page | `data/cities.json`, `assets/assets.json`, `vendor/` |
| Standalone builder | tooling | `apps/harness-city/tools/build_standalone.py` | python script | `index.html`, `vendor/`, data |
| Offline font stripper | tooling | `tools/offline_fonts.py` | python script | built HTML |
| Demo generator | tooling | `tools/make_demo.py` | python script | the skill's uv environment (`Taskfile.yml` task `demo`), `apps/harness-city/data/cities.json` |
| Browser tests | verification | `apps/harness-city/tests/`, `apps/harness-city/playwright.config.js` | Playwright 1.64.1, 3 spec files with 3 tests each, 2 projects | Node, Chromium, `dist/airport-test.html` |
| In-page regression module | verification | `apps/harness-city/tools/check_city.js` | javascript module | the running page |
| History tool | verification | `tools/audit_history.py` | python CLI (`record`, `compare`) | audit engine files, Git, report JSON |
| Python tool tests | verification | `tests/test_audit_history.py`, `tests/test_repo_quality.py` | unittest, 9 and 4 tests | History tool, repository checks |
| Repository checks | verification | `tools/check.py` | python script | `extraction-manifest.json`, docs, city design files |
| Task runner | delivery | `Taskfile.yml` | go-task file | all tools above, `uv`, `npm` |
| CI | delivery | `.github/workflows/check.yml` | GitHub Actions workflow | Task runner, uv 0.11.23, Task 3.51.1, Node 24, Python 3.14 |
| Receipts | storage | `.data/storage/local/file/harness-audit/history/` | local data, ignored | History tool |
| Self-audit reports | storage | `reports/self-audit/` | local data, ignored | audit engine |
| Retrospective documents | knowledge | `docs/0008-v0.1-harness-history-and-quality/` | markdown and jsonc | none |