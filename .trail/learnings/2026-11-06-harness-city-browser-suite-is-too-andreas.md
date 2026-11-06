---
type: 'Learning'
title: Harness City browser suite is too slow for agent sessions
author: Andreas
date: 2026-11-06
branch: main
touches:
  - apps/harness-city/DESIGN.md
  - apps/harness-city/README.md
  - apps/harness-city/data/cities.json
  - apps/harness-city/index.html
  - apps/harness-city/tests/city.spec.js
  - apps/harness-city/tests/export.spec.js
  - apps/harness-city/tests/fixtures.js
  - apps/harness-city/tools/report_to_city.py
  - docs/0011-v0.1-harness-coverage-expansion/Architecture.md
  - docs/0011-v0.1-harness-coverage-expansion/Golden-Dataset/dataset.json
---

## Decided
0011 closed with fast gates (tools:test, skill check, app:check, integrity, city_grid --check, a real audit run). The full Harness City browser suite is WN-031 and runs on CI or a GPU machine.

## Tried and ruled out
Running `task app:test` (42 tests, one worker, SwiftShader) in an agent session: it exceeds the 900 s global timeout (21 passed, 21 not run), and after an interrupt the agent restarted the whole suite from scratch. `--global-timeout` alone did not help.

## Watch out
In agent sessions run one spec file and one project at a time, e.g. `CITY_TEST_PORT=18765 task app:test -- city.spec.js --project=desktop-chromium`. Port 8765 may already be taken; use CITY_TEST_PORT. Mobile skips the five editor tests on purpose (desktop-only).
