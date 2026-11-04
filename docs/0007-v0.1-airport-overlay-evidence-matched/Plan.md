---
type: 'Plan'
id: '0007'
version: 'v0.1'
title: 'Airport Overlay: Evidence-Matched Plan'
description: 'Observable airport evaluation behavior and remaining production-integration boundaries.'
status: 'active'
doc_scope: 'history'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
stale_after: '2026-11-11'
tags: [documentation, retrospective]
sources: ['docs/0007-v0.1-airport-overlay-evidence-matched/research/airport-assets.md', 'apps/harness-city/DESIGN.md', 'git:8deb536', 'git:90e9a52']
---

# Airport Overlay: Evidence-Matched Plan

## Acceptance Boundaries

| ID | Observable requirement |
| --- | --- |
| A-1 | The airport stays outside the scored districts and never changes the city score. |
| A-2 | L0 is closed; L1 retains an identifiable airfield; L2/L3 have appropriate terminal/stand capacity. |
| A-3 | Only applicable Terraform/Compose/Dockerfile areas control the main airport's visual minimum. |
| A-4 | Devcontainer and Agent guidance grow independently; all applicable area displays remain visible. |
| A-5 | Transport uses the weaker endpoint; buses run at L1 and metro at L2+; stations exist at every city level. |
| A-6 | Underground survives city/option changes, rebuilds preserve resources/materials, and PNG export includes descriptions. |
| A-7 | Real-browser tests cover desktop/mobile and offline behavior with synthetic data. |

## Sequence and Boundaries

The history moves from asset/transit ideas to a separate prototype, then into the real
city and later automated regression fixes. Current behavior is not backdated to the
first proposal. Production report-data integration remains distinct from this evaluator.

## Scope

In scope, as shown by the commits: the asset proposal and variants (`3bfdf2b`, `f85a36d`), the
design contract (`489457f`), the separate prototype and its fixes (`38fab47`, `3f450d5`,
`c2a342f`), the move into the real city (`8deb536`) and the evaluation round with browser
tests (`90e9a52`). The files named in the criteria below, `index.html`, `tests/`,
`tools/check_city.js`, `playwright.config.js`, `package.json`, `Taskfile.yml` and `check.yml`, are
byte-identical at `90e9a52` and in today's tree (`git diff --quiet 90e9a52 HEAD`). `DESIGN.md`
and the app README differ from `90e9a52` by one changed line each, a link path.

Out of scope: the harbor overlay (`a620cd5`, reverted by `f2154c2`), the audit-side
infrastructure levels and their calibration (see [0005](../0005-v0.1-infrastructure-overlay-matched/Plan.md)
and [0006](../0006-v0.1-infrastructure-calibration-retrospective/Plan.md)), a report-data
adapter, making the airport a default view, and any fresh test run by this folder.

## Acceptance Criteria (Given/When/Then)

These restate A-1 to A-7 as checks that the tests and code support. They describe what the
evidence promises, not a replay of the old run. Test names and checks come from
`apps/harness-city/tests/*.spec.js` and `tools/check_city.js` at `90e9a52`. The browser
results are historical: the `90e9a52` commit message says "task check passed (251 skill tests
plus 3 subtests, 13 tooling tests and 18 browser cases)", and the 0008
[implementation record](../0008-v0.1-harness-history-and-quality/Implementation.md) repeats it.
This folder ran none of them.

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-1 (A-1) | the page at `90e9a52` | the code is read | the airport is `AIRP` with key `"airport"`, separate from the seven `PILLARS`, and `DESIGN.md` says it is never part of the 0-100 score; no test asserts that airport controls leave the score unchanged, reviewer judgment inferred from the spec files |
| AC-2 (A-2) | the "n8n-like" preset with Compose and Dockerfile set together | each level in the order 0, 1, 2, 3, 1, 2 is applied (`check_city.js`) | a hangar exists only when the level is above 0, the small terminal only at L1, the regional terminal at L2 and above |
| AC-3 (A-3) | preset "Everything L3" and Compose set to 2 | Devcontainer is set to each of the dash, 0, 1, 2 and 3 (`airport.spec.js`) | `#airportLevel` reads "Airport L2 · limited by Compose L2", one `airport-terminal` exists, and the devcontainer side-terminal is absent only for the dash |
| AC-4 (A-4) | the same preset | Agent guidance and Cross-cutting are set to 0 to 3 in turn (`check_city.js`) | each area keeps its own display marker, each marker looks different at all four levels, and `airport-small-terminal` stays at one so the overall level does not change |
| AC-5 (A-5) | the four synthetic cities | each is chosen (`check_city.js`) | the central station landmark exists for L3, L2, L2 and L0; metro trains number 7, 7, 2 and 0 and buses 14, 14, 9 and 0; the panel says the link is the smaller of the station level and 2 |
| AC-6 (A-6) | the Underground view is on | another city is chosen, the station-link variant is changed, and Compose is toggled six times | the stage keeps its `under` class, material opacity and depth state equal the first reading, and geometry allocation counts are equal: iterations 3 and 6 in `check_city.js`, all six in `airport.spec.js` |
| AC-7 (A-6) | the Export PNG button | it is pressed (`export.spec.js`) | a download starts whose first eight bytes are the PNG signature, the text drawn contains "Score 100", "District legend", "Infrastructure" and "Agent guidance office", and the camera target and zoom are unchanged |
| AC-8 (A-7) | `playwright.config.js` | the suite runs | two projects, `desktop-chromium` and `mobile-chromium`, each run the nine tests, which gives 18 cases |
| AC-9 (A-7) | the offline build `dist/airport-test.html` | every `https?://` request is aborted and the page is opened by `file://` | the city renders, Underground works, a PNG downloads, and the list of attempted requests is empty |
| AC-10 (negative) | the preset "No infrastructure" with Devcontainer 3 and Agent guidance 2 | the scene is inspected (`airport.spec.js`) | both support facilities exist, `airport-terminal` and `airport-hangar` do not, and no `bus` or `metro-train` carries the `AIR:link` pick |
| AC-11 (negative) | `HTMLCanvasElement.prototype.toBlob` is replaced by a function that returns null | Export PNG is pressed | `#exportStatus` contains "PNG export failed: PNG encoding failed." and the button is enabled again |
| AC-12 (edge) | any test in the fixture | the page logs an error or throws | the test fails, because the auto fixture expects the error list to equal an empty list |

## Assumptions

- The synthetic dataset in `apps/harness-city/data/cities.json` holds the four demo cities named
  in `city.spec.js`; the tests use no private data.
- "Weakest applicable core area" means the minimum over the non-null values of Terraform,
  Compose and Dockerfile, read from `airInfra` in `index.html`.
- The 18-case count follows from nine tests and two projects; the pass result is only the
  commit message's statement.
- The offline file is built with `--offline --airport` by `task app:test`, then font links are
  removed; the test uses that file, not the tracked simulator.
- Software-rendered Chromium (`--use-angle=swiftshader`) is accepted as the rendering path.

## Milestones and Delivery Slices

| Slice | Evidence | Outcome | Criteria |
| --- | --- | --- | --- |
| M1 Proposal | `3bfdf2b`, `f85a36d` (2026-10-27 22:09 and 22:14) | asset definition and variants A, B, C | context for A-2 to A-5 |
| M2 Contract | `489457f` (22:17) | `DESIGN.md`, app `AGENTS.md`, `design` check in `tools/check.py` | AC-1 |
| M3 Prototype | `38fab47`, `3f450d5`, `c2a342f` (22:41 to 23:05) | separate page, mobile layout, orthographic camera | context for A-2, A-5 |
| M4 Integration | `8deb536` (23:21) | airport inside `index.html`, `--airport` build flag | AC-2, AC-3 |
| M5 Evaluation | `90e9a52` (2026-10-28 14:09 `+0100`) | support facilities, L2 metro, permanent underground, PNG export, 18 browser cases | AC-3 to AC-12 |
| M6 Records | `1b15eeb`, `7d892f6`, `b745e58` | retrospective documents, tracked simulator, folder rename | none |

## Risks and Mitigations

| Risk | Mitigation recorded in the tree |
| --- | --- |
| Simulated levels read as audit results | the exported image names synthetic data and simulated overrides; `History-Match.md` repeats the limit |
| Rebuilds leak GPU memory | `releaseCity` plus the allocation assertion in AC-6 |
| Offline build reaches a remote host | `offline_fonts.py` and the blocked-request test in AC-9 |
| Software rendering makes tests slow | the 90-second per-test limit and 15-minute run limit in `playwright.config.js`; 0008 records a 652.0 second run |
| Proposal text read as current behavior | the Authority and Supersession section in [Architecture](Architecture.md) |

## Validation Contract

Objective: keep the current airport metaphor and evaluation behavior consistent.
Read first: [Architecture](Architecture.md), app DESIGN.md and original asset notes.
Constraints: deterministic layout, synthetic public data, no scoring changes or new private reports.
Validate: `task app:test` for runtime changes; `python3 tools/check.py` for this docs-only reconstruction.
Stop when: the relevant gate passes and known integration/prototype limits remain explicit.

## Open Questions

- Conflict, simulator tracking. [Implementation](Implementation.md) says "The local generated
  simulator has no tracked originating commit at its docs path", the Architecture says it is
  "local build output", and `History-Match.md` says "Untracked generated output". Git shows
  `7d892f6` adding `docs/0007/research/city-airport-prototype.html` (1008 lines) and the file is
  tracked today (4,722,659 bytes, blob `25c88a38`). All statements stay as written; the owner
  decides which is intended.
- Conflict, runways. `research/airport-assets.md` has a tier row with "2 runways" at L3 and a
  later decision "one runway at every level"; `38fab47` has a second runway at L3, `AP.rw:1`
  sets one at `90e9a52`. The later decision governs, per the Authority section.
- Conflict, report adapter. The asset document proposes an `infra` block from
  `tools/report_to_city.py`; the script has no `infra` text at `90e9a52` or today.
- Should the airport become a default view? `Not recorded`.
- Why was the harbor overlay reverted? `Not recorded`; `f2154c2` names only B-182 and B-183.
- Why was the size rule changed from "overall infra level (weakest tool area)" to the weakest
  applicable core area? `Not recorded`; the change is visible between `3bfdf2b` and `90e9a52`.
- Is a remote CI run for `90e9a52` available? `Not recorded` in this tree.
- Which browser download host and protocol does `playwright install chromium` use?
  `Not recorded` in the repository.
- Does the `data` query parameter need a restriction for non-synthetic use? `Not recorded`; the
  tests never pass it.