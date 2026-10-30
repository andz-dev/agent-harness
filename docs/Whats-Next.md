---
type: 'Backlog'
title: 'What''s Next'
status: 'active'
created: '2026-10-27'
updated: '2026-10-30'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags:
  - 'documentation'
---

<!-- markdownlint-disable-next-line MD025 -->
# What's Next

A running backlog of raised topics — features, issues, bugs and discoveries — not yet spec'd
into a real versioned `Plan.md`. Append-only: never delete, renumber or rewrite rows. Open work
is in the first table; finished rows (struck through) move to the second as history. See the
`whats-next-backlog` skill for how to add, promote or close an entry.

## Open

New, triaged and promoted-but-unfinished rows. Append new rows at the end.

| ID | Type | Title | Description | Origin | Initial Approach Sketch | Effort | Depends On | Status |
|---|---|---|---|---|---|---|---|---|
| WN-002 | Issue | Synthetic demo shows no issues | The four demo cities carry no findings, so the district panel can list only the checks per level, never real issues or missing files. | Harness City detail work: the demo stays finding-free because EXTRACTION.md forbids fabricated detector findings. | TBD; e.g. an explicitly labelled synthetic findings profile, if the owner allows it | TBD | WN-001 | New |
| WN-003 | Issue | Review adapted-runtime baseline rule | Copied runtime files may now change when recorded as `adapted-runtime` in extraction-manifest.json; tools/check.py verifies their new `sha256`. | Harness City changes touched hash-pinned app files; AGENTS.md requires a reviewed baseline update. | Owner reviews the rule and the three adapted records | Low | WN-001 | New |
| WN-004 | Discovery | Compact scan export lacks findings | The compact scan export has no findings or gate failures, so cities built from it show levels but no evidence; only full reports do. | Found while extending tools/report_to_city.py to carry findings, gate failures and limitations. | TBD; add findings to the export or convert full reports | TBD | None | New |
| WN-005 | Feature | Per-run graph freshness gates | Ensure agentic workflows use current Trail code-graph and Atlas docs-graph state on every run, and do not proceed when required graph checks or refreshes fail. | Session discussion established that query-time refresh and agent instructions alone do not guarantee both graphs are used and fresh for every run. | Add shared preflight and freshness receipts, then integrate them with GitHub Copilot in VS Code and Claude Code; enforce graph use where harness hooks allow and document instruction-only limits elsewhere. | TBD | None | New |
| WN-006 | Issue | Backlog skill referenced but missing | This file points to a `whats-next-backlog` skill for adding, promoting and closing entries, but `skills/` contains only `harness-audit`. | Verification pass 2026-10-28. | Add the skill to `skills/` (for example from the private skills repo) or reword the reference to say where it lives | Low | None | New |
| WN-007 | Issue | Session hook files documented but not tracked | `.trail/README.md` describes `hook.cjs` and `.claude/settings.json`, but neither file is tracked, so the documented session-start hook does not exist in a fresh clone. | Verification pass 2026-10-28; self-audit TRG-05. | Commit both files, or reword the README to match the repo | Low | None | New |
| WN-008 | Issue | No Git or agent hooks | Self-audit scores Automatic triggers at L0: no pre-commit, husky, lefthook or `.githooks`, and no agent hooks (TRG-01, TRG-02, TRG-03, TRG-05, TRG-06). | Dogfood run of harness-audit on this repo, 2026-10-28 (41/100). | One hook config and one `.claude/settings.json` hooks block, both calling the same Taskfile targets | Medium | WN-007 | New |
| WN-009 | Issue | Node app lacks linter, formatter and coverage | `apps/harness-city` has no ESLint, Biome or Prettier config (STA-02) and no coverage setup (VER-10); the skill side has no coverage either. | Dogfood run, 2026-10-28. | Pick one Node lint/format tool and add it to `task check`; add coverage for the Python skill first (smallest effort) | Medium | None | New |
| WN-010 | Issue | No Python type checking | `skills/harness-audit/pyproject.toml` configures only ruff and pytest; no mypy or pyright runs locally or in CI (STA-06). | Dogfood run, 2026-10-28; verified in pyproject.toml. | Add a type checker to the skill's `task check`; start non-strict | Medium | None | New |
| WN-011 | Issue | No dependency update automation | No Dependabot or Renovate config (CIP-07) although the workflow pins action SHAs and the repo has lockfiles, so updates will not arrive on their own. | Dogfood run, 2026-10-28; verified, `.github/dependabot.yml` absent. | Add Dependabot for github-actions, npm and uv | Low | None | New |
| WN-012 | Issue | Markdown lint and front matter not enforced | Docs carry `markdownlint-disable` comments but no markdownlint config exists (DOC-03), and `tools/check.py` checks no front matter although all docs use it (DOC-04). | Dogfood run, 2026-10-28; verified by file search and reading `tools/check.py`. | Add a markdownlint config and a front matter check to `tools/check.py` with a test | Low | None | New |
| WN-013 | Issue | Orphaned tools/refresh_docs.py | Nothing in Taskfile, CI, README or CONTRIBUTING references `tools/refresh_docs.py` (ENR-01, verified by search). | Dogfood run, 2026-10-28. | Wire it in as a task (for example `docs:refresh`) or document when to run it; do not delete without the owner | Low | None | New |
| WN-014 | Discovery | Self-audit misses checks behind Taskfile wrappers | VER-06 and STA-04 report Node tests and lint as not run in CI, yet CI runs `task check`, which runs `app:test`. This is the wrapper blind spot already described in skill BACKLOG B-05 and B-06, seen on this repo. | Dogfood run, 2026-10-28; cross-checked against Taskfile.yml and check.yml. | Resolve `task:` and `task` indirection in the detector, with a regression test named after agent-harness; needs a reviewed baseline update because the runtime is frozen | Medium | WN-003 | New |
| WN-015 | Discovery | Architecture and decisions not found by the audit | ORI-07 and DOC-05 fail because docs live in `docs/000N/Architecture.md` and per-topic plans, not in `docs/architecture*` or an ADR folder. Partly a detector limit, partly a missing top-level overview. | Dogfood run, 2026-10-28. | Add a short `docs/ARCHITECTURE.md` index; decide whether decisions need an ADR folder or the detector should learn this layout | Low | None | New |
| WN-016 | Issue | Stale remote branches | `origin` still has `feat/harness-audit-v1.2` and `feat/harness-city-airport`; the airport branch points at the same commit as main. The intent was that only main remains. | Verification pass 2026-10-28 (`git ls-remote`). | Owner deletes both on GitHub after confirming nothing is unmerged | Low | None | New |
| WN-017 | Feature | SBOM generation in CI | Generate a CycloneDX SBOM for the Python skill and the Node app in CI and publish it as a workflow artifact or release asset, not as a committed file. Vendored assets are added as manual components. | Owner idea, 2026-10-28; docs/0009. | `npm sbom --sbom-format cyclonedx` for the app; export from `uv.lock` for the skill (verify the flag on the pinned uv) | Low | WN-011 | New |
| WN-018 | Feature | Audit overlays: supply chain, data protection, licenses and governance | Three overlay topics with their own levels beside the frozen score: SBOM and update automation, secret scanner and data class with a handling rule, license and notice checks plus community files. | Owner request, 2026-10-28; overview document and docs/0009. | Design note first, then catalog checks with a reviewed baseline update; optional Scorecard result as evidence for GitHub-side checks | High | WN-014 | New |
| WN-019 | Feature | City traffic on the whole road network | Cars and trucks use every road along both axes, drive rounded corners, and slow down for curves, ramps and junctions. Today cars only move along x in straight lanes on each district street. | Owner request, 2026-10-28; requirements R1 to R9 in docs/0009. | Road graph, routes with rounded corners, reuse the path helpers, speed from curvature | High | None | New |
| WN-020 | Feature | Committed self-audit evidence | `.harness/audit.json` plus a deterministic markdown summary with front matter, a harness fingerprint for staleness, and `task evidence` / `task evidence:check`. Conflicts with the AGENTS.md rule, the `reports/` ignore and the `tools/check.py` publication check, so it needs a narrow carve-out first. | Owner request, 2026-10-28. | See docs/0009 section 3 | Medium | None; related WN-005 | New |
| WN-021 | Feature | City overlay: shopping mall, factory and highway | Supply-chain overlay with gantry, trucks and update dispatcher; the factory is upstream and ungraded. | Owner direction, 2026-10-28; docs/0009 section 1. | Prototype behind a URL flag, as with the airport | High | WN-018, WN-019 | New |
| WN-022 | Feature | City overlay: protected archive | Data-protection overlay: windowless archive, class sign, scanner at the entrance, broken door for an exposure. Needs the L0 exception in DESIGN.md and no-values export rules first. | Owner decision, 2026-10-28; docs/0009 section 1. | Prototype behind a URL flag | High | WN-018 | New |
| WN-023 | Feature | City overlay: court | Licenses and governance overlay; shows that documents exist and never rules on compatibility. | Owner direction, 2026-10-28; docs/0009 section 1. | Prototype behind a URL flag | Medium | WN-018 | New |
| WN-024 | Feature | City overlay: harbor (release and publishing) | Outbound side of the supply chain: ships with sealed containers for releases, artifacts, signatures and SBOM; no harbor for repos that publish nothing. | Owner confirmation, 2026-10-29; docs/0009 section 1. | Prototype behind a URL flag; some facts need optional registry or GitHub data | High | WN-018, WN-019 | New |
| WN-025 | Feature | City overlay: bank (secrets) | Secrets and credentials: vault, scanner at the entrance, `.env` handling; an exposure shows as a broken vault door, never with the value. Split from the archive. | Owner direction, 2026-10-29; docs/0009 section 1. | Prototype behind a URL flag; no-values rule for click text and exports | High | WN-018 | New |
| WN-026 | Feature | Highway that grows with the city | The highway widens with the city and gets spurs to the airport and the harbor from the Working tier; stages follow the score tier (reading to confirm). | Owner direction, 2026-10-29; docs/0009 section 2. | Stage table in DESIGN.md first, then road graph with ramps | High | WN-019 | New |
| WN-027 | Feature | Growing central station | The station grows with the Workflow entry points level: open platform, roofed platforms and roofed approach with metro link, glass hall with concourse and airport express. | Owner idea, 2026-10-29; docs/0009 section 2. | Update the Transit section and registry in DESIGN.md first | Medium | None | New |
| WN-028 | Feature | Coverage map of harness topics | One map listing each topic by layer (core score, overlay, optional evidence) and status (checked, planned, out of scope); languages as adapters instead of per-language duplicate checks. | Owner request, 2026-10-29, after the scope grew across supply chain, data, licenses and governance. | Draft the map from the existing topics, then research current practice | Medium | WN-018 | New |
| WN-029 | Issue | No coding-standards or language-linter coverage | No check looks for a coding standards file, style guide or `.editorconfig`; linter checks exist only for Python and Node, other languages are detected but not scored. | Owner question, 2026-10-29; verified in checks/catalog.yaml and detect_stack.py. | Language adapters and a standards-document check, designed with the coverage map | Medium | WN-028 | New |
| WN-030 | Feature | City and map editor with export | Editor for terrain, trees, guided and free streets and tracks, vehicle paths for trucks, ships and planes, CC0 asset palette and district editing; exports a versioned `city-map.json` for the harness setup. | Owner request, 2026-10-29; research in docs/0010/Research.md. | First version built (commits 07fa31e, aab73a4); parked by the owner on 2026-10-30 as too complex for now. Resume with the viewer reading `city-map.json`, then more CC0 kits | High | WN-019, WN-026 | Parked |

## Closed

Finished or abandoned rows (`Done`, `Promoted → … (done)`, `Won't Do`), kept as history only.

| ID | Type | Title | Description | Origin | Initial Approach Sketch | Effort | Depends On | Status |
|---|---|---|---|---|---|---|---|---|
| WN-001 | Feature | ~~Harness City explanations and transit~~ | Clickable buildings, streets, sites, rail and power line with explanations; per-district issues, evidence and level ladder; bus and metro lines from the central station by level. | Owner request: details below L3 (insights, issues, missing files) were not shown on the map. | Catalog checks and findings in the city data; panel cards per clicked object; line level = min(station, district) | Medium | None | Done |

## Verification log

Appended notes; the rows above are unchanged.

### 2026-10-28

Checked against main at `7d892f6` (37 commits, only `main` locally).

| ID | Result | Evidence |
|---|---|---|
| WN-001 | Stays Done | Skill, tools and demo checks pass locally; browser tests were not run in this session (no Chromium), so CI is the proof. |
| WN-002 | Open, no longer blocked | WN-001 is done. All four demo cities in `apps/harness-city/data/cities.json` have zero findings and zero gate failures. |
| WN-003 | Open, premise outdated | The manifest has 76 `adapted-runtime` records (4 in `apps/harness-city`, 25 in `skills/harness-audit`, the rest docs), not three. `tools/check.py` integrity passes. The owner review has to cover the larger set. |
| WN-004 | Open, path outdated | The converter is `apps/harness-city/tools/report_to_city.py`, not `tools/`. Its own comment confirms the compact export has no cap field. `harness-scan-compact.json` is not in the repo, only in the Project docs. |
| WN-005 | Open | No freshness gate, receipt or hook exists in the repo; related to WN-007 and WN-008. |

Not reviewed: skill `BACKLOG.md` items B-01 to B-35 against the current code.
