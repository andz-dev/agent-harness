---
type: 'Design Proposal'
title: 'City overlays, road traffic and committed harness evidence'
status: 'draft'
created: '2026-10-28'
updated: '2026-10-28'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags:
  - 'design'
  - 'harness-city'
  - 'harness-audit'
---

<!-- markdownlint-disable-next-line MD025 -->
# City overlays, road traffic and committed harness evidence (draft)

Status: proposal for review. Nothing here changes `DESIGN.md`, `AGENTS.md`, `.gitignore`,
`tools/check.py` or any audit check yet. Decisions that are still open are collected in
section 5.

The proposal has three parts:

1. Three audit topics shown as city overlays: supply chain, data protection, and licenses
   with governance.
2. Traffic that uses the whole road network, with corners, ramps and speed changes.
3. A harness evidence file that lives in the repository, so agents and reruns can use it.

## 1. Overlays

### Common rules

These follow `DESIGN.md` principles 5 to 8 and the airport precedent.

* An overlay is drawn outside the seven districts and never changes the 0-100 score.
* Each overlay has its own L0-L3 level, its own click explanation with a `levelList`, and
  its rows in the asset registry.
* Colours must differ from the seven fixed pillar colours and from the airport teal.
* Placement is deterministic from the repo id. Unknown is not drawn as good; limits are listed.
* New objects are generated in code. No new binary assets without a `NOTICE.md` entry.
* Each overlay starts as a prototype behind a URL flag, as `?airport` did.

### Supply chain: supermarket, goods factory, highway

Owner direction: a supermarket district supplied by a goods factory outside the city,
connected by a highway. Trucks drive in and are checked and recorded on the way.

| Object | Stands for |
| --- | --- |
| Supermarket and its shelves | The dependencies the repo uses |
| Goods factory, outside the city | The upstream ecosystem and registries. Not ours, so it looks the same at every level |
| Highway and ramps | The delivery path from upstream into the repo |
| Trucks | Packages and updates |
| Gantry over the highway | Automated check of every truck; its log is the SBOM |
| Delivery dispatcher | The update bot (Dependabot or Renovate) |

| Level | Picture | Audit meaning |
| --- | --- | --- |
| L0 | Unmarked trucks at an open yard | Nothing pinned or recorded |
| L1 | Numbered plates on every truck | Lockfiles committed, versions pinned |
| L2 | Gantry with scanner and a dispatcher | Update automation, vulnerability scan and SBOM in CI |
| L3 | Sealed trailers with checked seals | Pinned action SHAs, read-only tokens, published SBOM, signed provenance, pinned agent components |

The gantry says "checked and recorded", not "pays toll": the audit does not measure cost.
Routes follow the existing rule that a link is only as good as both ends. The factory is not
graded, so a route's level is the supermarket's level.

### Data protection: protected city archive

Owner decision: a protected city archive, not a prison. Valuable records are protected;
nothing dangerous is locked in.

| Object | Stands for |
| --- | --- |
| Windowless archive, one controlled entrance | The repo's protected data |
| Sign at the gate | The declared data class (the label, not the strength) |
| Fence and tree buffer, no neighbouring houses | Ignored paths, deny rules, nothing sensitive adjacent |
| Guards and scanner at the entrance | Secret scanner in the Git hook and in CI |
| Visitor log | Access rules for agents and people |
| Broken door with an alarm | An exposure. The click text names file and rule, never the value |

| Level | Picture | Audit meaning |
| --- | --- | --- |
| L0 | Records stacked in an open yard, no fence, no sign | Nothing ignored, no class declared |
| L1 | Locked building with a class sign | `.env*` ignored and untracked, class declared |
| L2 | Guarded entrance with scanner and visitor log | Scanner in CI or a hook, a data-handling rule with handling per class |
| L3 | Badge doors, vault wing, shuttered windows, tree buffer | Same scanner in hook and CI, agent deny rules, rule reachable from agent files, redacted reports |

Rules that need an explicit exception first:

* `DESIGN.md` says L0 is a vacant fenced lot. Here L0 is open and unfenced, because the
  point is exposure.
* The archive must look unlike the public library, which is the Doc hygiene pillar
  (purple, open, windows). Closed against open is the intended contrast.
* The PNG export and the standalone HTML follow the same no-values rule as the click text.

### Licenses and governance: court

Owner direction: a court district for the legal aspects. This is the least detailed overlay.

| Level | Picture | Audit meaning |
| --- | --- | --- |
| L0 | Empty lot, no sign | No license file |
| L1 | Small courthouse with a nameplate | License file with holder named, README, license field in package metadata |
| L2 | Courthouse with a records office | SPDX ids, notices cover every vendored component, `SECURITY.md` |
| L3 | Courthouse with a registry wing | REUSE-style tagging, SBOM license data matching the notices, code owners, templates, code of conduct |

The court shows that documents exist. It never rules on license compatibility; that is a
legal question. Police headquarters stays the Static guardrails pillar: police enforce,
the court records.

## 2. Traffic on the whole road network

### Current state

Verified in `apps/harness-city/index.html`: `buildTraffic` puts cars into straight lanes on
each district's front street. A lane has a fixed `z`, a direction of plus or minus one,
and moves only along x. Buses and metro already follow polylines through `shuttle`,
`pathAt`, `pathLen` and `offsetPath`. Trains follow the rail line.

### Requirements

| ID | Requirement |
| --- | --- |
| R1 | Cars and trucks use every road, along x and along z, and cross junctions |
| R2 | Vehicles drive corners on rounded curves; the heading follows the curve |
| R3 | Speed depends on curvature and on the distance to a junction or exit; trucks are slower than cars, the highway is faster |
| R4 | Highway exits and entries are rounded ramps with deceleration and acceleration; a truck slows, takes the ramp and drives on to the supermarket yard |
| R5 | Routes are deterministic from the repo id. Cosmetic flicker in the animation loop stays allowed, as the design file says |
| R6 | Traffic still shows the level: no traffic on a closed road, density and speed grow with level, a route's level is the lower of its two ends |
| R7 | Vehicles keep a gap in their lane and do not overlap; junctions use simple deterministic priority, not a full simulation |
| R8 | Shared geometry and cheap per-frame updates; the standalone HTML stays near its current size (2.8 MB at the last build) |
| R9 | Path and speed functions are pure and unit-testable without a browser; browser tests check movement on both axes |

### Approach sketch

1. Model the roads as a graph: junctions as nodes, straight segments as edges.
2. Turn a route into a polyline and round its corners with a fillet of fixed radius.
3. Reuse `pathLen`, `pathAt` and `offsetPath` for lane offsets and positions.
4. Speed along the path is the lower of the vehicle's top speed and a limit derived from
   curvature, with braking zones before corners, exits and junctions.
5. Replace the straight lane objects in `buildTraffic` step by step, keeping the level rules.

This work is independent of the overlays, but the supermarket overlay needs R1 to R5.
The browser tests cannot run in the sandbox used for this draft, so the checks for R1 to R9
need a CI run.

## 3. Harness evidence in the repository

### Why

The audit evidence should live in the repo so that:

* agents and harnesses read the same ground truth: what exists, what is enforced, what is weak;
* a rerun can tell when the last audit is outdated;
* the repo can audit itself, the project's own dogfooding.

### Conflict with the current rules (verified)

* `AGENTS.md`: never commit audit reports, agent answers or generated bundles.
* `.gitignore` ignores `reports/`, `answers*.json`, `llm_tasks.json` and `build/`.
* `tools/check.py` fails on tracked files under `reports`, `dist`, `.venv`, `.data` or `logs`,
  and `tests/test_repo_quality.py` asserts that.

A carve-out has to be narrow: one named directory, files written only by the evidence
command, and `reports/` stays forbidden.

### Files (name of the directory is open; `.harness/` used here)

| File | Role |
| --- | --- |
| `.harness/audit.json` | Machine evidence, a trimmed form of the report: schema, tool and catalog version, audited commit and time, clone mode, score, pillar and overlay levels, failed checks with file paths, unanswered judgement checks, limitations, harness fingerprint. No snippets, no values |
| `.harness/AUDIT.md` | Short agent-facing summary with the same front matter fields as the docs: what was audited and when, what works, what is weak or missing, how to run the checks, what to do before finishing a change, limits |

`CLAUDE.md` would import `AUDIT.md` and `AGENTS.md` would link it; Copilot gets the
equivalent instruction later.

### Deterministic summary, optional model narrative

The owner asked for a markdown file written by a model. My recommendation is that the
markdown is generated from the JSON by a script, so no number can drift and the check can
regenerate and compare it. A model-written narrative is allowed as a clearly marked
section (`generated: agent`, `verified: unverified`) that carries guidance only, never
figures. `AGENTS.md` already treats model answers as untrusted; this keeps it true.

### Freshness

* The harness fingerprint is a hash over the files the checks read (instruction files,
  Taskfile, CI workflows, hook and linter configs), excluding `.harness/` itself. This avoids
  the self-reference problem, because writing the evidence does not change its own fingerprint.
* The evidence is stale when the fingerprint changed, or when it is older than a set number
  of days. The owner called two months old outdated; the exact limit is open.
* `task evidence:check` is read-only and exits non-zero when stale. CI and the pre-flight
  check can call it, which connects to WN-005.
* `task evidence` runs the audit read-only, then explicitly writes only `.harness/`.
  The audit itself stays read-only.
* A scheduled workflow could open a pull request with a refresh. That needs write
  permission and is a decision, not a default.

### Privacy and other repos

* Paths and check ids only. The existing publication check runs over `.harness/` too.
* The declared data class decides whether a private repo may commit its evidence.
* For other repos, the evidence command writes only on explicit request and only into the
  named directory. The current bootstrap rule is "creates missing files only"; updating a
  generated file with a marker header is a small extension that needs a decision.

## 4. Backlog

New rows WN-017 to WN-023 in `docs/Whats-Next.md` track this work.

## 5. Open decisions

1. Overlay names and colours, and where each sits next to the airport.
2. Whether the court is confirmed as drawn here, and where governance files belong.
3. Name of the evidence directory and the wording of the `AGENTS.md` carve-out.
4. Staleness limit in days, and whether a scheduled workflow may open refresh pull requests.
5. Whether the model narrative section is wanted at all.
6. The term OKF was mentioned; I could not tell what it refers to, so this draft uses the
   front matter fields already used in `docs/`. Please say what it should mean.
7. Level names for data classes, given that L0-L3 is taken, and whether a class is
   declared per repo or per component.

## 6. Suggested order

1. Decide section 5.
2. Fix the Taskfile-wrapper detection (WN-014).
3. Road-network traffic (WN-019); independent, and the supermarket needs it.
4. Evidence file (WN-020); independent of the city, and serves WN-005.
5. Overlays one by one, starting with supply chain, then archive, then court.
