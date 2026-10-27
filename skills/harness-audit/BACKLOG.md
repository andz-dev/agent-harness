---
type: 'Backlog'
---

# harness-audit backlog

Findings and deferred work, recorded 2026-10-26 while drafting v1 (P0). Nothing here blocks v1 unless marked **[v1]**.

Legend: **[v1]** resolve before or during v1, **[v1.1]** harness-triage, **[v2]** bootstrap, doctor, Go, sandbox, **[later]** unscheduled.

## 1. Catalog rough edges (from `checks/catalog.yaml` draft 0.1)

| ID | Item | Target |
|---|---|---|
| B-01 | `ORI-08` and `ORI-09` are LLM-judged gates, so Orientation L3 depends on LLM judgment. Decide whether to keep them as gates or demote to non-gating and let scripts approximate (import lines in CLAUDE.md, link to AGENTS.md). | [v1] |
| B-02 | Doc hygiene has a single gate (`DOC-02`) and no L1 gate. Intentional so repos without a docs site are not punished, but revisit after calibration. | [v1] |
| B-03 | `STA-08` (one config per tool) uses the `git_signal` detector loosely. Needs a real duplicate-config rule per tool (ruff vs flake8 vs pylint is not a conflict; two ruff configs at one scope is). | [v1] |
| B-04 | Entropy penalty formula is a placeholder: `min(10, round(10 * flagged / candidates * 5))`. Tune in P4, freeze before P5. | [v1] |
| B-05 | Regex sets under `sets:` are a first pass (test, lint, type commands). Expect misses on custom wrappers (`make verify`, `tox -e lint`, `hatch run`). | [v1] |
| B-06 | Python runner coverage is thin: hatch, poe, pdm scripts, uv run, and `[tool.*]` scripts in `pyproject.toml` are not parsed as runner targets yet. | [v1] |
| B-07 | Node monorepo tools (pnpm workspaces, turbo, nx, lerna, Bazel as in angular) are not modeled; workspace-level scripts may hide targets. | [v1] |
| B-08 | `ORI-10` carries an `only_if` param (more than one component) that `run_checks.py` must understand. Define the `only_if` vocabulary or remove the param. | [v1] |
| B-09 | `ci_runs` has three jobs mixed in one detector: command match, trigger match, and share-of-run-steps. Consider splitting into `ci_runs`, `ci_trigger`, `ci_ratio`. | [v1] |
| B-10 | `ENT-01` accepts any `package.json`, which every Node repo has. It is a weak L1 gate; require a `scripts` block with at least one entry. | [v1] |
| B-11 | Weights (Verification 25, Orientation 20, Static 15, Entry points 15, Triggers 10, Parity 10, Docs 5) and caps (40, 60, 70) are provisional. | [v1] |
| B-12 | Pass ratio of 0.6 per level is a guess; check sensitivity on the calibration set. | [v1] |

## 2. Data notes on `example-repos.json`

| ID | Item | Target |
|---|---|---|
| B-20 | `n8n` and `opencode` both list exactly 203,000 stars as of 2026-09. Possible copy error; re-check. | [v1] |
| B-21 | Most entries are `verified: false` with null license and creation date. Selection is fine; do not cite them as facts in reports. | [v1] |
| B-22 | `hermes-agent` has `ecosystem: other` and no languages listed, so it is outside v1 scope until its stack is known. | [later] |
| B-23 | Go and Rust repos (urfave-cli, cobra, tinyauth, dynacat, fzf, bat, ollama, kubernetes) are out of v1 scope; reuse them as the v2 Go calibration set. | [v2] |
| B-24 | Mixed Python and Node repos (immich, paperless-ngx, open-webui) drive the per-component design. If detection fails on them, per-component scoring needs rework. | [v1] |

## 3. Design decisions to revisit

| ID | Item | Target |
|---|---|---|
| B-30 | v1 never runs repo code, so test speed cannot be measured. L3 "fast subset exists" is inferred from config only. A sandboxed run mode (possibly via App-Gate's container setup) would allow real timings. | [v2] |
| B-31 | Single headline score vs per-pillar only. Kept both with hard caps; watch for gaming and for scores that feel wrong on holdout repos. | [v1] |
| B-32 | Audit is stack-neutral, bootstrap is opinionated (Taskfile + pre-commit + Ruff/ESLint). Consider an L3 bonus for any single entry point that CI also calls, regardless of tool. | [v1] |
| B-33 | Copilot instruction support evolves; re-verify current AGENTS.md and agent-hook support in Copilot before freezing `ORI-08` and `TRG-05`. | [v1] |
| B-34 | Report language is English throughout (assumed; the repos are English). | [v1] |
| B-35 | Shallow clone (`--depth 1`) vs `--filter=blob:none`: entropy checks need history. Decide per check which clone mode it requires and fail soft when only shallow history exists. | [v1] |

## 4. Later versions

### v1.1: `harness-triage`
- Deeper entropy analysis: reference graph across runners, CI, hooks and docs; last-touch dates; dead config detection.
- Verdict workflow: active, stale, orphaned, conflicting, unknown, each with evidence. Never deletes.
- Dependency usage analysis (`ENR-06`) with an allowlist for tooling-only packages.
- HTML triage view reusing repo-atlas rendering.

### v2
- `harness-bootstrap`: proposes and creates missing pieces pillar by pillar, with diffs before applying. Reference stack: Taskfile.dev, pre-commit framework, Ruff, mypy or pyright, pytest, ESLint and Prettier (or Biome), Vitest or Jest, `tsc --noEmit`, CI calling `task ci`.
- `harness-doctor`: Taskfile target that runs the audit locally and in CI without any agent, to show the harness is a repo property.
- Go support (golangci-lint, `go test -race`, goreleaser) and possibly Rust.
- Optional sandboxed run mode for real test timings.
- Score history across audits of the same repo, to show whether a harness is improving.

### Later
- Combined report with App-Gate (safe), repo-atlas (understood) and harness-audit (workable).
- Terraform, Docker Compose and Azure pipeline specifics as extra pillars or components.
- Org-level roll-up across many repos.
- Instruction drift check as a standalone, cheap CI job.

## 4b. Schema findings (from `report.schema.json` draft 0.1)

The schema validates the example report and rejects all 15 negative cases. It cannot enforce everything, so these gaps move into code:

| ID | Item | Target |
|---|---|---|
| B-40 | JSON Schema cannot check arithmetic: `points = level / 3 * weight`, `raw = sum(points)`, `final = round(min(raw, caps) - penalty)`. `score.py` needs a self-check that recomputes and compares, and the example generator should fail loudly on mismatch. | [v1] |
| B-41 | Rule for choosing `top_gaps` is undefined. Proposal: failed gate checks first, ordered by pillar weight, then lowest level; max 5. | [v1] |
| B-42 | `findings[].gate` duplicates `catalog.yaml`. Decide whether the report copies it (self-contained, can drift) or the reader joins on `check_id` (no drift, needs the catalog). | [v1] |
| B-43 | `caps_applied[].id` is a closed enum (`no-tests`, `no-ci`, `no-orientation`). Adding a cap means a schema change; fine for v1, revisit if caps grow. | [v1] |
| B-44 | Findings for `not_applicable` and `unknown` may have empty evidence by design. `unknown` from the LLM layer should always say why in `note`; not enforced yet. | [v1] |
| B-45 | `pass` requires at least one `found` evidence item, `fail` requires at least one item of either kind. Check that real detectors can always produce a `searched` entry that is useful, not just a repeated glob list. | [v1] |
| B-46 | Per-component results exist only on `pillars[].by_component`; findings carry an optional `component`. Verify on immich, paperless-ngx and open-webui that this is enough to explain a weak component. | [v1] |
| B-47 | No field for the audited repo's declared license or visibility. Not needed for scoring; add only if reports get shared. | [later] |
| B-48 | Schema version is pinned with `const: "0.1"`. Define a migration rule before the first non-draft release so old reports stay readable. | [v1.1] |

## 4c. P1 findings (from `scripts/detect_stack.py`)

Detection passes 25 unit tests on synthetic repos, including git mode and a 60,000-file tree (about 2.5 s), and was checked by hand on five real shallow clones (flask, express, paperless-ngx, open-webui, immich). The remaining 14 calibration and holdout repos have not been run yet.

| ID | Item | Target |
|---|---|---|
| B-50 | **Done 2026-10-26:** flask, express, paperless-ngx, open-webui and immich were shallow-cloned and the output checked by hand. Four defects found and fixed (see B-60 to B-63), each with a regression test; 25 tests now pass. Still to do: run on the remaining calibration and holdout repos when their checks exist. | [v1] |
| B-51 | Sample and hidden-directory heuristics (`examples/`, `fixtures/`, `templates/`, dot-dirs) may hide real components, for example a first-party app under `templates/` or a JS action under `.github/actions/`. Hidden manifests are listed under `ignored.sample_manifests` (first 20 only); check on nextjs and vite. | [v1] |
| B-52 | `tracked_files` counts every file type (docs, lockfiles, assets). For size-weighting mixed repos, source files only may be a fairer weight. Decide in P2 when `score.py` needs it. | [v1] |
| B-53 | Standalone `requirements.txt` counts only at the repo root or with at least 3 Python files below it; `setup.cfg` only with `[metadata]` or `[options]`. Both thresholds are guesses. | [v1] |
| B-54 | Unsupported ecosystems (Go, Rust, Dart, Java and others) are listed but not scored, and the list is capped at 50. immich's mobile app and kubernetes will hit this. The report's `limitations` should say which parts were not audited. | [v1] |
| B-55 | Only uv workspaces are read for Python workspace members. Poetry, hatch and pdm multi-project layouts are not modeled. | [v1.1] |
| B-56 | Nx `project.json`, Bazel `BUILD` files and Turborepo pipelines are not read; projects that exist only there are invisible. Relevant for angular (Bazel) and nextjs. | [v1.1] |
| B-57 | A repo with only unsupported manifests exits with code 3 and no components. Decide what the skill reports in that case (a short "out of scope" report vs. an error). | [v1] |
| B-58 | The inference fallback (5 or more source files, no manifest) creates a root component with `detected_by: ["(inferred from sources)"]`. Threshold is a guess; check on small script repos. | [v1] |
| B-59 | Schema gained an optional `stack.unsupported` list; `schema_version` stays `0.1` because the report is still a draft (see B-48). | [v1] |
| B-60 | Fixed: a file named `setup.py` was taken as a manifest (open-webui `utils/telemetry/setup.py` is application code). It now needs an import of setuptools, distutils or skbuild. Files are read as text only. | done |
| B-61 | Fixed: a pnpm workspace that lists only `.` marked paperless-ngx `src-ui` as a workspace root ("tooling"). A root now needs at least one other member component. | done |
| B-62 | Fixed: open-webui's `backend/requirements.txt` became a second Python component beside the root `pyproject.toml`. A `requirements.txt` below an existing Python component is now merged (listed under `ignored.merged_manifests`). **Trade-off:** a monorepo whose root `pyproject.toml` has `[project]` and whose services carry only a `requirements.txt` will be treated as one component. Revisit if a calibration repo shows this. | done |
| B-63 | Fixed: immich reported 10 unsupported manifests, mostly build files nested under one app (`android/app` under `android`). They now collapse to the outermost manifest per language subtree (6 entries). | done |
| B-64 | immich lists `.github` as a Node component because `pnpm-workspace.yaml` names it. Low audit value; consider excluding hidden directories from size weighting or marking them `tooling`. | [v1] |
| B-65 | open-webui's root Node component holds 4,890 files, mostly static assets and translations, against 291 for Python. Confirms B-52: file counts are a poor size weight; count source files by extension instead. | [v1] |
| B-66 | paperless-ngx `src/paperless_mail/templates/package.json` is skipped as a sample directory. It looks like a real email-template package. Part of B-51; the `templates/` entry in `SAMPLE_DIRS` is the likely culprit. | [v1] |
| B-67 | immich's `pnpm-workspace.yaml` names `i18n` and `plugins`, which have no manifest, so they are not components. Probably correct; confirm when file-level checks run. | [v1] |

## 4d. P1 findings (from `scripts/run_checks.py`, hand-checked on flask, express, paperless-ngx, open-webui, immich)

Fixed in v0.1 (each has a regression test): indirect runner match counted dependency lists; tox evidence line numbers; ORI-01 headings; TRG-03 matched "ruff-check"; STA-05 now covers formatter hooks; ENT-02 plural targets; hook text no longer includes the repo URL (false "pre-commit"/"tox" matches); STA-07 is `not_applicable` without TypeScript; `vue-tsc|svelte-check|astro check` added; CIP-05 excludes setup steps from its denominator; DOC-04 no longer accepts `check-yaml`; VER-09 needs a real `markers =` key; CI tool matches skip install steps (`pip install ruff` is not running ruff; CIP-04 opts in with `include_setup`).

- B-68: The indirect runner match (CI calls `tox`/`make`/`npm run` and the runner file mentions the tool) is a heuristic. It does not prove the called target is the one using the tool. Needs target-level resolution (v1.1).
- B-69: ENT-02 may be too strict (express has `test`/`lint`/`test-ci` but no check/ci/verify target). Consider moving the any_of requirement to L3.
- B-70: ENT-03 only recognises target descriptions in Taskfile/Makefile/justfile/README; tox `description` is missed.
- B-71: TRG-01 `.claude/settings.json` match is weak (file exists, hooks key not checked).
- B-72: Per-component CI attribution is not done: a CI job in one workflow counts for every component.
- B-73: VER-10 evidence can point at a dependency name (pytest-cov) rather than a coverage config; weak evidence.
- B-74: CIP-02 on paperless-ngx passes on an `echo "No ..."` line (pattern is too loose); needs a tighter lint/typecheck pattern.
- B-75: Setup-step list (`SETUP_STEP`) is a regex of known commands; unknown wrapper scripts still count as non-setup.
- B-76 (resolved, see section 6): **Holdout contamination.** open-webui is in the Holdout set but was run and hand-checked during P1. Swap it for an untouched repo before P5 (or accept it as calibration and add a new holdout member).
- B-77: Go repos (immich-public-proxy root is go.mod only) yield exit code 3 in detect_stack; run_checks has nothing to do. Expected for v1, covered by v2 Go support.

## 4e. P2 findings (from `scripts/score.py`, run on the five repos)

- B-78 (partly fixed in audit step: components are now weighted by tracked_files and the mean is rounded half down; immich 30 -> 57): Pillar level was the floor of the unweighted mean over components. In monorepos with many non-code components (immich: github, docs, e2e, packages-*) this drags Verification to 0 although server and web are tested. Needs a component weight (by tracked_files or kind) or a `kind` filter so docs/github components are not judged on tests.
- B-79: Gate checks that are unknown (llm, git_signal) block L3 by design. Until P3 runs, no pillar with an L3 llm gate (ORI-08, ORI-09, ENT-05) can exceed 2. The report must say so in `limitations`; the max score without the LLM layer is below 100.
- B-80: A level with no applicable checks is passed vacuously. Real catalog has checks at every level, but a stack with all L3 checks not_applicable would jump to 3.
- B-81: Caps need a non-pass among pass/fail findings. A repo where VER-01/02 are all not_applicable does not get `no-tests`; check that this is intended for repos with only unsupported languages.
- B-82: top_gaps ranking (pillar weight x (4 - level) x 2 for gates) is a first guess; tune in P4.
- B-83: Score values look plausible but are uncalibrated: flask 55, paperless-ngx 50, express 33, open-webui 35 (no-tests cap), immich 30. No ground truth yet; P4 compares them with human ranking.

## 4f. P2 findings (from `scripts/git_signals.py`)

Implemented: STA-08, DOC-05, ENR-01, ENR-02, ENR-04, ENR-07. Not implemented: ENR-06 (unused dependencies), ENR-03/05 (LLM layer). Hand-checked on the five repos; false positives fixed with regression tests: `"prettier": "^3"` dependency read as a config; babel config used implicitly by docusaurus; CI paths inside a cloned repository.

- B-84: Real history checks (last-commit dates, ADR recency, "stale" by age) only run on a non-shallow clone. All five local clones are shallow, so `history_available` is false and DOC-05 stays `unknown` when ADR files exist. The runner needs a `--filter=blob:none` clone for P4.
- B-85: ENR-06 (unused dependencies) is not implemented. Needs an import scan per language and an allowlist for tooling packages.
- B-86: ENR-01 only looks for references by path, basename or Python module name. Scripts invoked through globs, `find`, or generated names are flagged wrongly; orphan chains (A only called by an orphan B) are not found.
- B-87: ENR-04 checks path-like tokens in CI run steps only. Workflows with `cd`, `git clone`, `repository:` or `working-directory` are skipped entirely (conservative).
- B-88: ENR-07 only knows ten tools and implied-by frameworks for babel/eslint/jest. Extend the tables from calibration results.
- B-89 (reworked 2026-10-26): entropy penalty is now min(10, round(20 * flagged_units / max(20, candidate_files))) with numbered file families counted once; still provisional, tune in P4.
- B-90: `candidate_files` is the sum over checks, so a file examined by two checks counts twice.
- B-91: DOC-05 `unknown` with history missing means the L3 doc pillar cannot pass; fine, but the report must list it under limitations.

## 4g. P2 findings (from `scripts/audit.py`, end to end on five repos)

Scores now: flask 55, paperless-ngx 55, immich 57, open-webui 34, express 33 (uncalibrated, shallow clones).

- B-92: Weighting by tracked_files makes one large component decide a pillar. Weakest-component and gate_failures still list the small ones, which can look contradictory (Verification L2 but blocked by VER-01/02 in a tiny component). Consider showing gate failures only for components above a size share.
- B-93: `audit.py` has no clone step. Cloning (shallow vs blobless, size limits, timeouts) belongs in the P4 runner; today it audits a local path and sets `clone_mode` from git state.
- B-94: Report markdown lists only failed checks and top gaps. Passed checks, unknown checks and per-component tables are JSON-only.
- B-95: A schema rule forces a `found` item on every pass; vacuous passes (nothing to flag) need a representative file. STA-08 now returns not_applicable when no tool config exists. Review other "absence" checks (ENR-*) for the same pattern.
- B-96: Stale `.pyc` can make mutation tests lie when a file is edited and restored within one second. Run mutation checks with `PYTHONDONTWRITEBYTECODE=1`.

## 4h. P3 findings (from `scripts/llm_layer.py` and `prompts/`)

Design: the script never calls a model. `audit.py` writes `llm_tasks.json` (numbered excerpts, script-computed facts, candidates); the agent answers per `prompts/*.md`; `audit.py --llm-answers` re-runs and verifies every quote against the files (unverifiable quote -> `unknown`, never a silent pass). Checks with nothing to judge (no agent file, no hooks, AGENTS.md alone) are resolved by script without a model.

- B-97: None of the five dev/calibration repos has an agent file, so the ORI/ENT judgement path was only exercised on synthetic repos and on flask's DOC-06/TRG-06. Use opencode, fastapi and others in P4 to test real agent files.
- B-98: TRG-06 asks about agent hooks vs Git hooks; with Git hooks only (flask) it fails by wording. Should be `not_applicable` when no agent hooks exist.
- B-99: STA-09 sends whole config files (pyproject 274 lines). Select sections (`[tool.ruff*]`, eslint config) instead to cut tokens.
- B-100: Excerpt budget is 700 lines per task; large READMEs/docs are truncated (paperless DOC-06). DOC-06 judges only what the excerpts show; its pass says so in the note, but the report does not yet mark truncated tasks.
- B-101: Quote verification accepts a match within +-2 lines (and a two-line span). Normalisation strips backticks/asterisks; a quote that is a substring of a longer line also passes. Acceptable for evidence, not proof of meaning.
- B-102: Model answers are per check, not per component; repo-wide only (applies_to: all).
- B-103: ENR-03/ENR-05 entropy items are derived from DOC-06/ORI-09 fail evidence (first two quotes), not judged separately; file-level flagging may over- or under-count.
- B-104: No automatic agreement test between two model passes. P4 should run each task twice (or with two prompts) and report disagreement as `low` confidence.
- B-105: The prompt-injection defence is prompt rules plus mechanical verification. A hostile repo can still bias status within the verified quotes; treat LLM findings as `medium` trust and keep them out of hard caps (already the case).

## 4i. P6 findings (self-harness: audit.py run on its own repository)

Added: SKILL.md, AGENTS.md (+ CLAUDE.md importing it), README.md, Taskfile.yml, pyproject.toml (ruff, pytest), .pre-commit-config.yaml and .claude/settings.json hooks calling `task lint`, and CI calling `task check`. Code formatted with ruff. 107 tests pass under pytest.

- B-106: Self-audit scores 90 after the second pass, but the LLM answers were written by the author of the tool and the repo; it is a smoke test, not a calibration point. Do not use it for weight tuning.
- B-107: Open self-audit gaps (real): no type checking (STA-06), no coverage (VER-10), no lockfile (VER-08), no Dependabot (CIP-07), no docs site/markdown lint (DOC-01..05), no CONTRIBUTING or architecture doc (ORI-03, ORI-07, AGENTS.md carries layout instead), hooks not documented as an install step (TRG-04).
- B-108: ORI-03/ORI-07 fail although AGENTS.md covers the same ground; Orientation still reaches L3 because the ratio rule tolerates failed non-gate checks. Consider whether ORI-03 should accept README "Development" sections.
- B-109: `pytest` installed as an isolated uv tool cannot import the project's dependencies; use `uv run pytest` (Taskfile does) or `python3 -m pytest`.
- B-110: Taskfile, CI and hooks were written but never executed here (no `task` binary in this sandbox); only the underlying commands (`ruff check`, `ruff format --check`, `pytest`) were run.
- B-112: The Project cannot store `.claude/settings.json` (path refused as a tool-config file); the Project mirror has it as `claude-settings.example.json`. The working tree is the source of truth.
- B-111: Skill packaging: SKILL.md lives at the repo root. A real skill folder needs scripts/checks/schema/prompts copied or the repo installed as the skill; decide in v1.1 (Andreas keeps a skills repo, see skills-repo-sync).

## 4j. P4 round 1 (script-only calibration on 12 repos, `scripts/calibrate.py`)

Repos: n8n 76, immich 57, flask 55, paperless-ngx 55, vite 54, home-assistant-core 52, immich-public-proxy 45, httpie-cli 44, opencode 42, fastapi 38, open-webui 38, express 33 (table: `samples/calibration-summary.md`). Blobless clones for the seven new repos (history available); the five older ones are shallow. LLM tasks were NOT answered for any of them, so Orientation is capped at L1/L2 and L3 gates stay unknown: compare scores only with each other.

Defects found by the first calibration runs and fixed (each with a regression test): vite counted 240 `playground/*` fixture packages and 17 `create-vite-template-*` packages as components (new component kind `sample`, also for `__tests__`, `tests`, `demo` folders); files of nested sample packages were not credited to the enclosing package; workspace-root config (vitest, eslint, root `package.json` scripts) was not inherited by member packages; hooks configured through `simple-git-hooks`/`lint-staged` in package.json were invisible; oxlint/oxfmt/dprint configs and formatters were not recognised; top-level playground files satisfied repo-wide checks; the entropy penalty over-punished tiny candidate sets and generated script families (fastapi 10 -> 5).

- B-113: Orientation cannot be compared yet: opencode and n8n have agent files but the judgement tasks are unanswered. Round 2 must answer the LLM tasks for every calibration repo (about 9 tasks each) before any weight tuning.
- B-114: No ground truth. Ask Andreas (or another human) to rank the 12 repos by "how well would an agent work here" before round 2, then compare rank correlation with the scores.
- B-115: Performance: n8n (32k files, 101 components) takes about 42 s, vite 2 s. Remaining hot spots are repeated glob matching (git_signals orphan/dead-config corpus building) and regex searches; fine for now, revisit if home-assistant-class repos get slower.
- B-116: Component explosion is still visible (vite 287, opencode 42, n8n 101). Samples are skipped for scoring, but `stack.components` in the report stays long; consider listing samples separately in the schema.
- B-117: Static guardrails reaches L3 for most Python repos on the strength of ruff/mypy config alone; STA-06/07 may be too easy to satisfy. Compare after LLM answers exist.
- B-118: Entropy items on shallow clones lack `last_commit`; fastapi's flagged items (25 numbered screenshot scripts under scripts/playwright) show that ENR-01 cannot tell manual tooling from dead code. Keep the verdict "orphaned" but consider an `unknown` verdict for families.
- B-119: `calibrate.py` iterates every subdirectory of the given directory (an `out/` folder inside it was audited as a repo). Pass a clean directory or add an ignore list.

## 4k. P4 round 2 (partial): human gut scores and LLM answers for two repos

Human gut scores (Andreas, `calibration/human-gut-scores.json`): n8n 80, immich 60, home-assistant-core 60, opencode 50, flask 50, paperless-ngx 50, vite 54, immich-public-proxy 45, httpie-cli 44, fastapi 40, open-webui 40, express 33. Six were "keep the tool's score" (weak signal). Spearman rank correlation with round-1 tool scores: 0.87 over all 12, 0.85 over the 8 explicit ones; mean absolute difference 3.1 points. Largest gaps: home-assistant-core (+8 human), opencode (+8 human), flask and paperless-ngx (-5).

After answering the judgement tasks (round 2, two repos only): opencode 42 -> 60 (Orientation L1 -> L3, Entry points L2 -> L3; human said 50, now 10 too high); home-assistant-core stays 52 (human 60). The honest answers for HA were mostly fails: AGENTS.md has no layout section (ORI-05), `.github/copilot-instructions.md` embeds a full copy of AGENTS.md instead of linking to it (ORI-08), and agents are told to run raw uv/pytest/prek commands (ENT-05).

- B-120: The human score mixes product AI-readiness ("HA has MCP servers", "n8n is built for agentic AI") with repository harness quality. The tool measures only the second. Decide whether calibration targets "harness quality" (then ask the rater again with that wording) or whether a separate product signal is wanted (probably not).
- B-121: Opencode swings +18 points from agent-file judgements. Orientation (20) plus Entry points (15) give one well-written AGENTS.md a lot of weight versus Verification (25) where opencode is only L1. Consider capping Orientation at L2 when Verification is L0/L1, or lowering ORI/ENT weights, once all 12 repos have answers.
- B-122: Round-2 answers were written by the same model that built the tool. Use an independent second pass (B-104) before tuning weights.
- B-123: Fixed: localized READMEs (README.ar.md ...) were sent to the model as "the README"; they are now skipped (regression test).
- B-124: Resolved in 4l: answers written for all repos.

## 4l. P4 round 2 complete: judgement answers for all 12 repos

Tool score after answers (human gut in brackets): n8n 86 (80), immich 57 (60), flask 55 (50), paperless-ngx 55 (50), vite 74 (54), home-assistant-core 52 (60), immich-public-proxy 45 (45), httpie-cli 52 (44), opencode 60 (50), fastapi 38 (40), open-webui 38 (40, no-tests cap applied), express 33 (33). Spearman 0.84, mean absolute error 5.8, mean bias +3.3 (tool higher).

- B-125: Vite is the outlier (+20). It has only a 50-line copilot-instructions file, but ORI-05/06/09, VER-11 and ENT-05 all pass, lifting Orientation and Entry points. The human "keep it" for vite was a weak signal, so re-ask before acting. Same pattern as opencode (B-121): a short, decent agent file buys too many points. Candidate fix: cap Orientation and Entry points at L2 unless the agent file exceeds a minimum substance (e.g. 80 lines or 3 of 4 sections).
- B-126: ENT-05 is a gate with a loose reading. Vite passes because agent files use `pnpm run lint/test`, yet there is no aggregate check target. Tighten: require a single aggregate command (check/verify/ci) for pass; per-tool scripts give partial.
- B-127: DOC-06 returned unknown for all ten new repos. Candidates are mostly illustrative output paths, release-note history and external names, and the evidence rule needs a quotable proof of absence. Consider a mechanical path-exists pass in the script and send only misses to the model.
- B-128 (done, unreleased): STA-09 is now a mechanical key_present check (ruff, pylint, flake8, eslint, biome, oxlint; formatters excluded). Re-scoring all 18 repos left every score unchanged. Original note: STA-09 passes on configuration alone (ruff/eslint/oxlint print rule ids by default). It does not distinguish repos, so it adds no signal. Consider dropping it or making it mechanical (known tool => pass).
- B-129: n8n ORI-09 and TRG-06 stayed unknown because excerpts were truncated at 250 lines and the Claude hook body was not included. Raise the budget for AGENTS.md or send heading-scoped sections.
- B-130: httpie-cli STA-09 unknown (no lint config in the sampled files) while it scored +8 over the human. Check whether a flake8/ruff config lives in `.pre-commit-config.yaml` or tox.
- B-131: All answers were written by the same model that built the tool (see B-122). The independent second pass is still open and must happen before weights change. Weights stay unfrozen; the holdout stays untouched.

## 4m. Independent second opinion (B-122, B-131 addressed)

A separate agent answered all judgement tasks blind (no access to my answers or reports). Agreement: 34 of 51 task answers identical; the 17 differences are 10 where I said unknown and it gave a verdict, 2 where it was unknown and I gave one, 3 unanswered by me (STA-09 on opencode/HA), and only 2 true pass/fail splits (HA ORI-08, n8n TRG-06 unknown vs fail). Re-scoring with its answers changes only n8n (86 -> 84); all other repos keep their score. Conclusion: my answers are not the source of the gaps; the vite (+20) and opencode (+10) overshoots come from the weights and gate leniency (B-121, B-125, B-126), and the next step is weight tuning, not re-answering.

- B-132: Reviewer was stricter on unknowns than I was; for DOC-06 it passed where I abstained. Keep "unknown" as default when no mechanical check exists, and implement the mechanical path-exists check (B-127).
- B-133: HA ORI-08: AGENTS.md and CLAUDE.md are byte-identical with no import line. Decide whether identical copies count as single source (reviewer: pass low). Probably partial credit only.
- B-134: Second-opinion runs are cheap (about 5 minutes); make it a standard step in calibrate.py runs (`answers2.json` plus an agreement report).

## 4n. Tuning step 1: verification cap and stricter ENT-05

Changes: (1) `score._cap_by_verification`: Orientation and Entry-points levels cannot exceed Verification level + 1 (report field `capped_by`); (2) ENT-05 now requires ONE aggregate command that runs lint, types and tests; per-tool scripts are a fail (vite re-answered fail). Tests: 118 pass.

Result (tool, human gut): n8n 86 (80), immich 57 (60), flask 55 (50), paperless-ngx 55 (50), vite 69 (54), home-assistant-core 52 (60), immich-public-proxy 45 (45), httpie-cli 52 (44), opencode 48 (50), fastapi 38 (40), open-webui 33 (40), express 33 (33). Mean absolute error 5.8 -> 5.1, bias +3.3 -> +1.4; opencode +10 -> -2, vite +20 -> +15.

- B-135: Vite is still +15; remaining credit comes from Static guardrails L3 and Workflow L2. Ask Andreas for a fresh gut score for vite (earlier "keep it" was weak) before tuning further.
- B-136: open-webui fell 38 -> 33 because the cap now also trims Orientation/Entry points when Verification is L0. Accepted; human said 40 ("a bit old").
- B-137: HA remains -8 (human 60): the human credit for MCP servers is product-level (B-120) and is out of scope.
- B-138: Weights are NOT yet frozen. Before freezing: ask for the vite re-score, consider holdout run only after that.

## 4o. Holdout run (weights frozen 2026-10-26)

Clones: blobless full history, all six. Judgement answers written by an independent agent that saw no reports (answers in scratchpad `holdout/R/<repo>/answers.json`).

Tool scores: nextjs 83, nestjs 61, fastify 43, vllm 39, rich 35, django 20. Entropy penalties: rich 5, fastify 0, vllm 6, nestjs 7, django 7, nextjs 2. No caps applied. Human gut scores (given after seeing the ranking, mapped in table order: nextjs, nestjs, fastify, vllm, rich, django): 80, 60, 40, 40, 35, 30. Mean absolute error 3.0, bias -0.8, rank order identical; django is the only miss (-10) and coincides with B-139.

- B-139: django Verification L0 although VER-01/02/05/06 pass: the large `root-python` component is L0 (the fine-grained cause is not yet traced; Django runs tests via `tests/runtests.py`, not pytest, with `tests/` as a package). Looks like a detector gap, not a real L0. Investigate after the human scores are in; do not tune on this repo's score.
- B-140: rich Static guardrails L0 (STA-01 linter fail: rich uses black + isort + mypy, no linter). Plausible but harsh; formatters-only should arguably give partial L1.
- B-141: ENR-01 flags 5-7 penalty on rich, nestjs, django, vllm, mostly `scripts/` and `tools/` maintenance scripts. Same pattern as fastapi (B-118): manual tooling is not dead code. Candidate: exempt `scripts/`, `tools/`, `bin/` unless unreferenced AND untouched for 18+ months.
- B-142: DOC-06 unknown for 4 of 6 and `runner_targets` is cut at 80 entries (nextjs). Raise the cap or sort by relevance (B-127).
- B-143: nextjs 83 is the highest of all 18 repos; AGENTS.md at 250+ lines gets truncated for ENT-05 and ORI-09 (B-129). Treat as plausible: Next.js has a large agent file and real test culture.

## 4p. Post-holdout detector fixes (weights untouched)

Fixes: (1) VER-03 accepts `runtests.py` / `tests/runtests.py` as a configured unittest framework (B-139, django regression test); (2) ENR-01 no longer flags an unreferenced script when blobless/full history shows a commit within 540 days (B-141; shallow clones unchanged). Tests: 121 pass. `FROZEN.sha256` regenerated (catalog.yaml and git_signals.py changed on purpose; score.py weights/caps unchanged, pinned by test).

Re-run, all 18 repos (before -> after, human): django 20 -> 41 (30), nestjs 61 -> 67 (60), vllm 39 -> 45 (40), fastapi 38 -> 43 (40), rich 35 -> 36 (35), nextjs 83 -> 84 (80), n8n 86 -> 87 (80), vite 69 -> 70 (54); the other ten unchanged.
Holdout MAE 3.0 -> 5.2 (bias -0.7 -> +3.5): the first result was flattered by two errors that offset (django's detector bug, entropy over-penalty). The honest holdout figure is 5.2, in line with calibration MAE 5.1. Django now overshoots (+11): its Verification now reaches L2 but it has no agent file and weak orientation, so the remaining gap is a weights question, not frozen-set tuning.

- B-144: rich STA-01 (formatters only, no linter) stays L0. Changing it is a check-semantics change; decide after v1 ships, using more repos.
- B-145: Tool is consistently 3-5 points above the human on mature OSS repos. Candidate for v1.1: a mild global recalibration or an "AI-era" bonus structure, but only with a fresh calibration set.

## 4q. v1.1 triage (done)

`scripts/triage.py` + `checks/fixes.yaml`: counterfactual fix plan. For each failed check it re-scores with that check passing (smallest bundle of 1, 2 or 3 checks in one pillar when no single fix moves the score), picks steps by points per effort, lists no-effect items, entropy cleanup with points, and unanswered judgement checks. `audit.py` writes `triage.md` and `triage.json` every run. Tests: 129 pass.

- B-146: Fixed a latent bug: `_cap_by_verification` sat below the `__main__` guard, so `python3 score.py` (script mode) would raise NameError. Function moved above `main`.
- B-147: Triage ranks by score gain, not by importance to the project; effort numbers are rough guesses (1/2/3). Calibrate efforts with real fix times after v1.1 is used on a few repos.
- B-148: Plan stops at 10 steps and bundles of 3. Orientation steps beyond that appear under "no score effect yet" even though several are cheap; consider showing cheap items (effort 1) regardless.
- B-149: Add `--apply-preview` later (v2 bootstrap): generate the file stubs for effort-1 steps (AGENTS.md skeleton, Taskfile skeleton) without writing to the repo.

## 4r. v2 preview: bootstrap (done, preview)

`scripts/bootstrap.py`: proposes AGENTS.md (commands, layout from top-level dirs, generic conventions, single-test hint), CLAUDE.md (`@AGENTS.md`), Taskfile.yml, .pre-commit-config.yaml (Python), CI running `task check`, Dependabot, CONTRIBUTING.md for failed checks only. Output goes to `<out>/proposed/`; `--apply` writes only files that do not exist. Tests: 137 pass.

Experiment: express copy, audit 33, `--apply` of 4 files (AGENTS.md, CLAUDE.md, Taskfile.yml, CONTRIBUTING.md), re-audit 45 (+12) with placeholders unfilled.

- B-150: Stubs raise the score although the TODO(human) parts are empty. Consider making the audit treat a file with `TODO(human)` markers as incomplete (ORI-05/06 judgement should already catch it, but the script checks do not).
- B-151: Pre-commit for Node is not proposed (needs package.json changes: simple-git-hooks/husky). Add a package.json patch proposal (diff, not an edit).
- B-152: Monorepos: only root-level files for the dominant component. Add per-component AGENTS.md (ORI-10) and per-package runner targets.
- B-153: `rev: v0.8.0` for ruff-pre-commit is a placeholder with a TODO; resolve the latest tag offline-safely (pin from uv.lock if present) or document.
- B-154: The CI workflow uses fixed major versions of third-party actions (checkout@v4, setup-uv@v5, setup-task@v2); review for supply-chain pinning by SHA before use.
- B-155: No Azure DevOps pipeline proposal yet (original request mentioned Azure DevOps); add `azure-pipelines.yml` generator.
- B-156: Go support (v2) still open: detection, checks and templates.

## 4s. Phase 1 trust fixes (done)

- B-150 resolved: any passing script check whose evidence file still contains `TODO(human)` becomes a fail with a note (`run_checks.downgrade_placeholders`). Express copy with unfilled bootstrap stubs: 45 -> 38 (the Taskfile still counts, correctly).
- B-127 resolved in part: DOC-06 is resolved by script (pass) when every backticked path in README, docs and agent files exists; history files (changelog, release notes, news) are no longer searched for dead paths (fastapi regression). 8 of 12 calibration repos and 2 of 6 holdout repos now have a script verdict; the rest still go to the model and are mostly `unknown`.
- B-129 resolved in part: judgement excerpts raised to 400 lines per file and 1000 per task; runner target list 80 -> 200. n8n ORI-09 and nextjs ENT-05 need fresh answers to benefit.
- Scores unchanged on all 18 repos (DOC-06 is a level-3 check in a 5-point pillar). Tests: 141 pass.
- B-157: The script DOC-06 pass only knows backticked relative paths with a file extension. Markdown links and commands are not checked; extend before treating it as full coverage.
- B-158: Re-answer the 12 judgement tasks that grew with the bigger excerpts (n8n ORI-09, nextjs ORI-09/ENT-05, django ORI-09) in the next blind second-opinion round.

## 5. Risks carried forward

- Stack-neutral detection is the hard part; the catalog will grow after P1.
- Big repos overwhelm the LLM layer; it must only see script-selected excerpts.
- The score may reward ceremony over substance (a large CI that gates nothing). The "enforced" criteria and the holdout set are the guard.
- Orientation is new territory: many OSS repos will score L0 or L1 there. That is the finding, not a bug.

## 6. Test sets (from the plan)

- Dev (2): flask, express
- Calibration (10): httpie-cli, immich-public-proxy, fastapi, paperless-ngx, opencode, vite, home-assistant-core, n8n, immich, open-webui
- Holdout (6): rich, fastify, vllm, nestjs, django, nextjs

Changes (2026-10-26): open-webui and immich were hand-checked during P1/P2 development, so both moved from Holdout/unlisted to Calibration (B-76 resolved). vllm (Python, mid, untouched) replaces open-webui in Holdout.
Holdout was run once on 2026-10-26 after the weight freeze (section 4o). Do not tune weights on it.

## 4t. Phase 2 start (B-159..B-161)
- B-159 (done): `scripts/agreement.py` compares two independent answer sets (agreement rate, Cohen's kappa, disagreement list). Tests in `tests/test_agreement.py`.
- B-160: First agreement run on the 12 calibration repos: 33/49 agree (67%), kappa 0.36. Most disagreements are `unknown` vs a verdict (11 of 16), not pass vs fail. DOC-06 accounts for 6 of them and is now script-resolved, so the figure is stale for that task; re-run after B-158 re-answers.
- B-161: Real pass-vs-fail splits: home-assistant-core ORI-08, vite ENT-05. Review these two prompts for ambiguity.

## 4u. Phase 2 judgement prompts (B-162..B-163)
- B-162 (done): B-161 review. vite ENT-05 run B passed while its own note said no aggregate command exists; orientation_quality.md rule 7 now requires status to match the note. home-assistant-core ORI-08 split on whether a script-generated copilot file counts; instruction_drift.md rule 8 defines it (symlink, identical copy, import or generated marker pass; hand-written duplicate fails).
- B-163: These prompt changes alter what judgement runs return, so the existing 12 answer sets are not comparable. Re-answer ORI-08 and ENT-05 on all repos (part of B-158), then re-run `scripts/agreement.py`.
- B-164 (done): Second agreement run after the prompt fixes: 47/54 agree (87%), kappa 0.77 (was 67%, 0.36). ENT-05 agrees 7/7. Scoring with A vs B answers: 13 of 15 repos identical, n8n 78 vs 85, opencode 42 vs 48. Report: docs/0004/Agreement-Report-v1.2.md.
- B-165: Remaining real splits: immich-public-proxy VER-11 and opencode ORI-05 (pass vs fail); n8n ORI-09 and home-assistant-core ORI-08/ORI-09 (verdict vs unknown). ORI-09 (drift) is the least stable judgement; consider a mechanical sub-check or a stricter unknown rule. Gut-score check: n8n 80 and opencode 50 fall between the two runs' scores.

## 4v. Infrastructure coverage (B-166..B-190)
Full map: `docs/0005/Infrastructure-Coverage-Map.md`. Today the catalog has no infra check; nothing below is built.
- B-166: Detect Terraform/OpenTofu/Terragrunt, Bicep/ARM, Kubernetes/Helm/Kustomize (Track A).
- B-167: Detect Pulumi, CloudFormation/CDK, Ansible.
- B-168: Detect Dockerfile/Containerfile and Docker Compose files.
- B-169: Detect devcontainers and other dev environments (gitpod, codespaces, nix, mise).
- B-170: Infra component type in `detect_stack` so monorepos score per component.
- B-171: Terraform checks (pinning, lock file, fmt/validate/plan in CI, tflint/trivy, state hygiene, docs, agent workflow).
- B-172: Bicep/ARM checks.
- B-173: Kubernetes/Helm/Kustomize checks.
- B-174: Pulumi, CloudFormation/CDK, Ansible checks.
- B-175: Dockerfile checks (dockerignore, hadolint, pinned base, non-root, healthcheck, secrets, CI build).
- B-176: Docker Compose checks (healthchecks, pinned images, env example, config validation, profiles).
- B-177: Devcontainer checks (valid config, pinned image/features, postCreate = runner setup, tool versions match CI, agent file mentions it).
- B-178: Cross-cutting infra checks (path-filtered CI, CODEOWNERS, Dependabot ecosystems, secrets scanning).
- B-179: Infra entropy (unused variables/modules/services, unbuilt Dockerfiles, stale lockfile, env drift).
- B-180: Judgement prompt `infra_quality.md` (safe plan/apply workflow, environments, forbidden commands).
- B-181: `infra` block in report.json and scan export; schema version bump.
- B-182: Harness City adapter: infra district or layer.
- B-183: Synthetic infra fixtures for demo cities.
- B-184: Report limitations list unsupported or unscored infra so a score never implies infra is fine.
- B-185: Harness adoption skill shell (`harness-adopt`) reading report.json and triage.json. NOT STARTED.
- B-186: Infra proposals in adoption (devcontainer, dockerignore, hadolint, Compose healthchecks, Terraform CI job, tflint, Dependabot).
- B-187: Adoption safety rules (dry run default, reviewable diff, never apply/destroy/deploy).
- B-188: Diff-based merge mode for existing files (supersedes B-151..B-156 scope).
- B-189: Synthetic repos per tool and per pass/fail case in tests.
- B-190: Infra calibration set with two raters; test that infra files never change the frozen 0-100 score until decision D1 is made.
- B-191 (done): ORI-09 gets mechanical candidates (documented `task/make/just/npm run X` commands that no runner defines) and `command_references_checked`; prompt rule 9. Needs a re-answer run to measure the effect on agreement (B-165).
