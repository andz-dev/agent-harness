---
type: 'Roadmap'
title: 'Repo Harness Next Steps'
status: 'draft'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
sources: ['Owner-provided roadmap note, 2026-10-27; original body preserved']
---

# Repo Harness: Next Steps

Oct 27, 2026 · @Andreas

## Where we are

v1.1 works end to end (audit, fix plan, bootstrap preview) and sits about 5 points from your gut scores, but three things still limit how far the score can be trusted.

- **Shipped:** audit pipeline, judgement layer with verified quotes, frozen weights, fix plan (`triage.md`), bootstrap proposals, 137 tests, downloadable `.skill` package.
- **Trust gap 1:** files with `TODO(human)` placeholders still earn points (express went 33 to 45 with empty stubs).
- **Trust gap 2:** the only reference is one rater, and six calibration scores were "keep it".
- **Trust gap 3:** DOC-06 is unknown on most repos, and long agent files are cut at 250 lines in the judgement excerpts.

Item numbers like B-150 refer to `BACKLOG.md` in the Project.

## Roadmap

&#91;embedded content: roadmap · 3 phases, 2 gates\]

Phase 1 gates the others; weights change only after Phase 2 passes its gate, and bootstrap work in Phase 3 can run beside it.

## Phase 1: make the score trustworthy

Four fixes, about two to three days in total, remove the biggest ways the score can be gamed or left blank.

| Step | What changes | Done when | Backlog |
| --- | --- | --- | --- |
| Sync the Project | Copy the new `SKILL.md` and `requirements.txt` into the Project | Project and the `.skill` package match | - |
| TODO placeholders | The audit treats a file containing `TODO(human)` as incomplete and does not credit it | express with empty stubs stays near 33, not 45 | B-150 |
| DOC-06 by script | A script checks that documented paths exist; only the misses go to the model | DOC-06 has a verdict on most of the 18 repos | B-127, B-142 |
| Bigger excerpts | Send agent files in heading-scoped sections and lift the 80-entry runner list cap | n8n ORI-09 and nextjs ENT-05 get a verdict | B-129 |

After each fix, re-run all 18 repos and check the frozen hashes. Detector fixes are allowed; weights stay frozen.

## Phase 2: check the accuracy

The 5-point accuracy rests on one rater and a model that wrote its own judgement answers, so Phase 2 widens the evidence before any weight moves.

1. **Second rater (B-145 prerequisite).** One more person gives blind gut scores for all 18 repos, before seeing the tool's numbers. Compare the two raters first; if they differ by more than 5 points, the tool's error is within taste.
2. **Standard blind second opinion (B-122, B-134).** Every calibration run gets an `answers2.json` from a separate model plus an agreement report.
3. **STA-09 decision (B-128).** Drop it or turn it into a script check, since it passes on configuration alone and separates no repos.
4. **Formatter-only repos (B-144).** Decide whether rich-style repos get partial credit in Static guardrails. This changes what a check means, so it needs the second rater's view first.
5. **Detector gaps (B-118).** Per-component CI attribution, unused dependencies (ENR-06), and blobless re-clones of the five shallow repos so dead-file checks have history.
6. **Recalibrate (B-145).** Only with new raters and a fresh holdout set: the tool runs 3–5 points high on mature open-source repos. Weights stay frozen until this step, and the old holdout cannot be reused.

## Phase 3: bootstrap and fix plan

Bootstrap becomes useful on your own repos once it covers your pipeline, hooks and monorepo layouts.

| Item | Why | Backlog |
| --- | --- | --- |
| Azure DevOps pipeline proposal | Named in your first request; CI proposals cover GitHub only | B-155 |
| Node git hooks as a `package.json` diff | Node repos get no hooks today; needs a proposed patch, not an edit | B-151 |
| Monorepos | Per-package `AGENTS.md` and runner targets, not only root files | B-152 |
| Pin actions and ruff version | Generated CI uses version tags and a placeholder ruff rev | B-153, B-154 |
| Fix plan: show cheap items | Effort-1 items hidden after step 10 | B-148 |
| Fix plan: real effort numbers | Effort 1/2/3 are guesses; calibrate with actual fix times | B-147 |
| Go support | Detection, checks and templates | B-156 |

The audit itself stays read-only. Only bootstrap writes, and only new files with `--apply`.

## Open decisions

Four answers from you decide the order and scope of the work.

- [ ] Who is the second rater, and can they score all 18 repos blind?
- [ ] Should repos with only formatters (rich) get partial Static guardrails credit?
- [ ] Azure DevOps first, or Node hooks first, for the bootstrap work?
- [ ] Is Go in scope for the next release, or stay Python and Node?
