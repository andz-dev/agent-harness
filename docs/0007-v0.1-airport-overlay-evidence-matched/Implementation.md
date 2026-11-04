---
type: 'Implementation'
id: '0007'
version: 'v0.1'
title: 'Airport Overlay: Recorded Implementation and Gaps'
description: 'Airport evolution from proposal to the current tested opt-in evaluation.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['git:3bfdf2b', 'git:f85a36d', 'git:38fab47', 'git:8deb536', 'git:90e9a52', 'docs/0008-v0.1-harness-history-and-quality/Implementation.md']
---

# Airport Overlay: Recorded Implementation and Gaps

## Recorded Evolution

- [x] `3bfdf2b`, `f85a36d`: asset proposal and station-link alternatives.
- [x] `38fab47`, `3f450d5`, `c2a342f`: separate prototype, mobile behavior and orthographic camera.
- [x] `8deb536`: evaluator moves inside the real city rather than remaining a separate toy page.
- [x] `90e9a52`: stable rebuilds, permanent underground, L2 metro, PNG export and non-blocking support facilities.
- [x] The same implementation commit includes automated desktop/mobile/offline browser tests.

The 0008 [implementation record](../0008-v0.1-harness-history-and-quality/Implementation.md)
owns the executed test evidence. This documentation pass does not claim a fresh runtime
run. The local generated simulator has no tracked originating commit at its docs path.

## Open Work

- [ ] Integrate actual report infrastructure into the city through an explicit reviewed data contract.
- [ ] Decide whether and when the evaluated airport becomes a default product view.
- [ ] Review remaining proposed assets against actual metaphor value before claiming them implemented.

## Verification Contract

Objective: preserve the current opt-in evaluation and truthful evidence boundary.
Read first: [Plan](Plan.md), [Architecture](Architecture.md), app DESIGN.md.
Constraints: no score changes, private datasets or manually edited generated bundles.
Validate: `task app:test` for runtime work and `python3 tools/check.py` for documentation.
Stop when: required checks pass and remaining prototype/data-integration limits are explicit.

The old harbor was reverted (`a620cd5`, `f2154c2`); its adapter is not counted as current work.

## Phase Detail

Criteria ids AC-1 to AC-12 come from the [Plan](Plan.md). Every check below is a read-only Git
query run on 2026-11-04 unless it says `Not recorded`. No browser test, build or `task check`
was run by this documentation pass.

### Phase 1: Proposal and design contract (AC-1)

Objective: record the asset proposal, the station-link alternatives and the design contract.
Read first: [airport-assets.md](research/airport-assets.md), [Architecture](Architecture.md).
Constraints: keep the proposal text as history; do not treat the tier table as current.
Validate: `git show --stat 3bfdf2b f85a36d 489457f`
Stop when: the output lists `docs/0007/airport-assets.md` (76 and 24 lines) and, for `489457f`,
`apps/harness-city/DESIGN.md` (116 lines), `apps/harness-city/AGENTS.md`, `CLAUDE.md` and
`tools/check.py`.

- [x] `3bfdf2b` (2026-10-27 22:09:16 `+0000`) adds the asset definition.
- [x] `f85a36d` (22:14:31) adds transit findings and variants A, B and C.
- [x] `489457f` (22:17:42) adds the design contract and a `design` check to `tools/check.py`.
- [ ] A current run of `python3 tools/check.py` for the design check: `Not recorded` by this phase.

### Phase 2: Separate prototype (context for AC-2, AC-5)

Objective: record the throwaway page that preceded the integration.
Read first: `git show 38fab47:apps/harness-city/prototypes/airport.html`.
Constraints: the page is history; it was deleted by `8deb536` and must not be restored.
Validate: `git show --stat 38fab47 3f450d5 c2a342f`
Stop when: the output shows a 300-line `prototypes/airport.html`, then changes of 19 and 31
lines to it, and four added lines in `DESIGN.md` for the camera rule.

- [x] `38fab47` (22:41:50) uses a `PerspectiveCamera`, an import map to `three@0.160.0` on
  `cdn.jsdelivr.net`, and a `// second runway at L3` comment.
- [x] `3f450d5` (23:00:01) is a mobile layout, pinch zoom and WebGL fallback message.
- [x] `c2a342f` (23:05:46) switches to the orthographic camera and adds the `## Camera` rule.

### Phase 3: Integration into the real city (AC-2, AC-3)

Objective: move the airport into `index.html` behind `?airport` and `--airport`.
Read first: `git show 8deb536 --stat`, `apps/harness-city/tools/build_standalone.py`.
Constraints: opt-in only; no change to the scored districts; no manual edit of the output.
Validate: `python3 apps/harness-city/tools/build_standalone.py --offline --airport -o apps/harness-city/dist/airport-test.html`
Stop when: the file is written under the ignored `dist/` folder; the Phase 4 suite is the check
of its content. This pass did not run the command.

- [x] `8deb536` (23:21:37) changes 190 lines of `index.html`, adds the `--airport` argument to
  `build_standalone.py` and deletes `prototypes/airport.html` (304 lines).
- [x] The builder writes `window.HARNESS_AIRPORT=true` when the flag is used.

### Phase 4: Evaluation behavior and browser tests (AC-3 to AC-12)

Objective: record the support facilities, L2 metro, permanent underground, stable rebuilds, PNG
export and the Playwright suite added together.
Read first: `apps/harness-city/tests/`, `tools/check_city.js`, `playwright.config.js`.
Constraints: synthetic data only; no retries; no skipped or removed assertion.
Validate: `task app:test`
Stop when: the command exits 0 with 18 cases passed. The historical result is in the `90e9a52`
message and in the 0008 [implementation record](../0008-v0.1-harness-history-and-quality/Implementation.md).

- [x] `90e9a52` (2026-10-28 14:09:55 `+0100`) adds `airport.spec.js` (50 lines), `city.spec.js`
  (32), `export.spec.js` (74), `fixtures.js` (32), `playwright.config.js` (46), `package.json`
  (16), `package-lock.json` (63) and `tools/check_city.js` (159).
- [x] The suite has three spec files of three tests each and two projects, which makes 18 cases.
- [x] The same commit changes `Taskfile.yml` (`app:setup`, `app:test`), `check.yml` (Node 24
  setup, timeout 20 minutes) and `.gitignore` (`playwright-report/`, `test-results/`).
- [x] The test server is `python3 -m http.server` on `127.0.0.1`, port 8765 or `CITY_TEST_PORT`.
- [ ] A current run of `task app:test`: `Not recorded`; the 18-case pass is historical.

### Phase 5: Records and the tracked simulator (no criterion)

Objective: record how the documents and the generated simulator came into the tree.
Read first: [History-Match](../History-Match.md), the Recorded Conflicts section of
[Architecture](Architecture.md).
Constraints: do not assign the simulator an originating commit other than the one Git shows;
do not regenerate it.
Validate: `git log --format='%h %s' -- docs/0007/research/city-airport-prototype.html`
Stop when: the output names `7d892f6`, and `git ls-files docs/0007-v0.1-airport-overlay-evidence-matched`
lists `research/city-airport-prototype.html`.

- [x] `1b15eeb` (2026-10-28 22:39:47 `+0100`) adds `docs/0007/Architecture.md`, `Ideation-Book.md`,
  `Implementation.md` and `Plan.md` and moves the asset file to `research/`.
- [x] `7d892f6` (22:41:30 `+0100`, "City Harness Airport Prototype") adds the 1008-line simulator.
- [x] `b745e58` (2026-11-04 14:38:44 `+0100`) renames the folder; the simulator rename is `R100`.

## Acceptance Criteria Traceability

| Criterion | Phase | Evidence |
| --- | --- | --- |
| AC-1 | 1 | `DESIGN.md` statement, `AIRP` outside `PILLARS`, `design` check |
| AC-2 | 3, 4 | `check_city.js` hangar and terminal checks per level |
| AC-3 | 3, 4 | `airport.spec.js` first Devcontainer test |
| AC-4 | 4 | `check_city.js` independent area displays |
| AC-5 | 4 | `check_city.js` per-city station, metro and bus counts |
| AC-6 | 4 | `check_city.js` repeated rebuild check, `airport.spec.js` allocation set |
| AC-7 | 4 | `export.spec.js` PNG test |
| AC-8 | 4 | `playwright.config.js` projects |
| AC-9 | 4 | `export.spec.js` offline test |
| AC-10 | 4 | `airport.spec.js` support-only test |
| AC-11 | 4 | `export.spec.js` encoding-failure test |
| AC-12 | 4 | `fixtures.js` auto fixture |

## Decision Log

| Decision | Basis |
| --- | --- |
| Use `90e9a52` as the evidence anchor | the listed app and test files are identical at `90e9a52` and today; `DESIGN.md` and the app README differ by one link line each |
| Keep existing prose and log conflicts | the simulator tracking, the L3 runway count and the `infra` adapter proposal each disagree with Git evidence, see the Recorded Conflicts section of [Architecture](Architecture.md) and the [Plan](Plan.md) open questions |
| Treat the 18-case pass as historical | it is a statement in the `90e9a52` message and in 0008; this pass did not run browsers |
| Quote both sides of the simulator conflict | this file says "no tracked originating commit at its docs path"; `7d892f6` and `git ls-files` show one |
| Leave unrecorded items as `Not recorded` | no issue, interview or CI log for these decisions is in the tree |

## Resume State

- Current phase: none open; this folder is a finished retrospective.
- Last verified: the Git queries named in each phase, run on 2026-11-04.
- Open items: the owner's decision on the tracked simulator, the default-view decision, the
  harbor revert reason, remote CI result for `90e9a52`, and the report-data contract.
- Next step: run the Phase 4 `Validate:` command before relying on any behavior statement.

## Final Verification

Run `python3 tools/check.py`. It checks documents, links, the design contract, the demo data and
publication rules, and it describes the current tree only. Observed on 2026-11-04 after this
folder was deepened: `python3 tools/check.py` printed
`PASS: extraction integrity, docs, synthetic data and publication checks`. For runtime behavior run
`task app:test` after `task setup`; the 0008 record, not this folder, owns the historical result.