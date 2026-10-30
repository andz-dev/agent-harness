---
type: 'Design Proposal'
title: 'City overlays, road traffic and committed harness evidence'
status: 'draft'
created: '2026-10-28'
updated: '2026-10-30'
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

Status: proposal for review, updated 2026-10-30. The city layout, the highway stages and the
civic quarter are decided and live in the "City map (grid)" section of
`apps/harness-city/DESIGN.md`, which is the source of truth for them. Nothing else here changes
`AGENTS.md`, `.gitignore`, `tools/check.py` or any audit check yet. Decisions that are still open
are collected in section 5. The city and map editor (WN-030) is parked and not part of this
proposal's order of work.

The proposal has four parts:

1. Five audit topics shown as city overlays: supply chain (shopping mall), release and
   publishing (harbor), secrets (bank), data protection (archive), and licenses with
   governance (court).
2. Traffic that uses the whole road network, with corners, ramps and speed changes.
3. A harness evidence file that lives in the repository, so agents and reruns can use it.
4. City growth: a highway that widens with the city and a station that grows with its level.

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

### Supply chain: shopping mall, goods industry, highway

Owner direction: a shopping mall district supplied by a goods industry outside the city,
connected by a highway. Trucks drive in and are checked and recorded on the way.

| Object | Stands for |
| --- | --- |
| Shopping Mall and its shelves | The dependencies the repo uses |
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
graded, so a route's level is the shopping mall's level.

### Data protection: protected city archive

Owner decision: a protected city archive, not a prison. Valuable records are protected;
nothing dangerous is locked in.

| Object | Stands for |
| --- | --- |
| Windowless archive, one controlled entrance | The repo's protected data |
| Sign at the gate | The declared data class (the label, not the strength) |
| Fence and tree buffer, no neighbouring houses | Ignored paths, deny rules, nothing sensitive adjacent |
| Guard at the entrance | The handling rule for the declared class, applied to agents and people |
| Visitor log | Access rules for agents and people |

Secrets and credentials moved to the bank (below) on 2026-10-29. The archive keeps the data
class and the personal-data rules.

| Level | Picture | Audit meaning |
| --- | --- | --- |
| L0 | Records stacked in an open yard, no fence, no sign | No class declared, nothing ignored |
| L1 | Locked building with a class sign | Class declared in a named place, data paths ignored |
| L2 | Guarded entrance with visitor log | A data-handling rule with handling per class |
| L3 | Badge doors, shuttered windows, tree buffer | Agent deny rules for classified paths, rule reachable from agent files, redacted reports, model passes gated by class |

Rules that need an explicit exception first:

* `DESIGN.md` says L0 is a vacant fenced lot. Here L0 is open and unfenced, because the
  point is exposure.
* The archive must look unlike the public library, which is the Doc hygiene pillar
  (purple, open, windows). Closed against open is the intended contrast.
* The PNG export and the standalone HTML follow the same no-values rule as the click text.

### Secrets: bank

Owner direction (2026-10-29): a banking district. It holds secrets and credentials; the
archive holds the data class and personal-data rules, and the court holds licenses.

| Object | Stands for |
| --- | --- |
| Bank building with a vault door | Where secrets are meant to live: a secret store, not files in the repo |
| Guards and scanner at the entrance | Secret scanner in the Git hook and in CI |
| Armored car, L3 only | Secrets delivered to CI and runtime from a store |
| Broken vault door with an alarm | An exposure. The click text names file and rule, never the value, and it is listed apart from the levels |

| Level | Picture | Audit meaning |
| --- | --- | --- |
| L0 | Open counter on the street, cash on the table | No `.env*` ignore rule, no scanner |
| L1 | Small branch with a locked door | `.env*` ignored and untracked, `.env.example` present, no key files tracked |
| L2 | Bank with guards and a scanner at the entrance | Secret scanner configured and run in CI or a hook |
| L3 | Bank with a vault wing and an armored car | Same scanner in hook and CI through one entry point, agent deny rules for secret paths, workflow secrets taken from the platform store |

A tracked live secret is an incident to rotate, not a score input. Old leaks are only visible
with full history, which a shallow clone does not have (skill backlog B-35). The no-values
rule applies to click text, PNG export and standalone HTML, as for the archive.

### Release and publishing: harbor

Owner confirmation (2026-10-29): the harbor is the outbound side. Ships carry sealed
containers out of the city, the mirror of the shopping mall where trucks bring dependencies in.
The earlier harbor idea for infrastructure stays dropped; that is the airport.

| Object | Stands for |
| --- | --- |
| Quay and pier | Where artifacts leave the repo |
| Ships | Releases and published artifacts |
| Sealed containers on the ships | Artifacts with signatures or provenance, with the SBOM attached |
| Harbor master's office | A documented release process and a changelog |
| Customs gate on the quay | Signature and provenance check |

| Level | Picture | Audit meaning |
| --- | --- | --- |
| L0 | Empty quay, no pier | No tagged releases |
| L1 | Small pier with one boat | Versioned releases and a changelog |
| L2 | Working port with a crane | Release automated from CI, artifact or image published from CI |
| L3 | Port with a customs gate and sealed containers | Signed or attested releases, SBOM published with each release, provenance |

Repos that publish nothing get no harbor, as repos without infrastructure get no airport.
Some of this needs registry or GitHub data (Scorecard's Packaging and Signed-Releases checks
cover similar ground), so it would be optional evidence, not a static-scan fact.

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

### Placement: civic quarter and outer ring (decided 2026-10-29)

Bank, archive and court form one civic quarter west of the core (x -20..-7, z 1..15), because
all three are about trust and rules. It connects through the central station: bus only on lower
levels, bus and subway from L2, like the airport. The airport and its station sit west of the
highway (airport x 45..61, station x 37..43). The Shopping Mall (x 50..58, z 11..17) has its
own entry from the highway with the toll gantry. The goods industry sits in the north
(x 48..62, z -18..-8) with a land road to the highway. The harbor quay is in the south
(x 6..32, z 24..30). One west-east power line feeds the harbor, the airport and the industry.
The exact cells are in `DESIGN.md`. Positions stay deterministic from the repo id, and the
standalone file must not grow much (2.8 MB at the last build).

## 2. Traffic, highway and station

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
| R4 | Highway exits and entries are rounded ramps with deceleration and acceleration; a truck slows, takes the ramp and drives on to the shopping mall yard |
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

This work is independent of the overlays, but the shopping mall overlay needs R1 to R5.
The browser tests cannot run in the sandbox used for this draft, so the checks for R1 to R9
need a CI run.

### Highway that grows with the city

Owner direction (2026-10-29): the highway has more than a single on and off lane. Beyond the
city road it gets a lane for the airport and one for the harbor, and the more the city
grows, the wider the roads become.

| Stage | Highway |
| --- | --- |
| 1, Neglected | Narrow: one lane each way, one on and off ramp to the city only |
| 2, Working (score 45+) | Still narrow; adds spurs to the airport and the harbor, where those overlays exist |
| 3, Prosperous (60+) | Full grid width (x 62.5..69.5), two lanes each way, rounded ramps with deceleration lanes |
| 4, Thriving (80+) | Full width, three lanes each way, an interchange and the check gantry of the supply-chain overlay |

Decided 2026-10-29: the stage follows the city's score tier, because the highway belongs to
the whole city; below L2 the highway is narrow, from L2 it has the full width of the grid.
The bus and metro rule (lower level of both ends) stays as it is for transit. A spur is drawn
only when its overlay exists. The road enters the map through a tunnel under the northern
mountains (z -30..-22, portal at z -22) and leaves it over a bridge on pillars across the harbor
water. This depends on the road-network traffic work (WN-019): ramps, corners and slowing
trucks.

### Station that grows with its level

The central station stands for the Workflow entry points pillar, so its level sets its size.

| Level | Station |
| --- | --- |
| L0 | Closed station (as today) |
| L1 | One open platform and a single track |
| L2 | Roofed platforms, tracks entering the city under a roofed approach, underground connection to the metro |
| L3 | Station hall with a glass roof, several tracks, an underground concourse, the airport express platforms |

The underground view keeps working: it fades surface buildings and never shows service
below L2. The station change updates the Transit section of `DESIGN.md` and the registry first.

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

New rows WN-017 to WN-029 in `docs/Whats-Next.md` track this work. WN-030 (city and map
editor) is parked by the owner as of 2026-10-30: too complex for now, no work until it is
resumed. Its code and research stay in the repository.

## 5. Open decisions

1. Overlay colours. Names and places are set in the grid (Shopping Mall, Goods industry,
   Harbor, Bank, Court, City archive). The airport station gap (C7) is decided: the airport
   moved two cells east.
2. Whether the court is confirmed as drawn here, and where governance files belong.
3. Name of the evidence directory and the wording of the `AGENTS.md` carve-out.
4. Staleness limit in days, and whether a scheduled workflow may open refresh pull requests.
5. Whether the model narrative section is wanted at all.
6. OKF is the front matter convention of the docs skills, and this draft follows it. The
   `stale_after` policy for the docs is undecided: 14 days suits living documents, not
   historical records.
7. Level names for data classes, given that L0-L3 is taken, and whether a class is
   declared per repo or per component.
8. ~~Highway stage~~ Decided 2026-10-29: follows the score tier, narrow below L2, full width
   from L2; spurs from the Working tier.
9. ~~Civic quarter and outer ring~~ Decided 2026-10-29: civic quarter west of the core, airport
   and station moved west, mall, industry and harbor as in the grid.
10. Which harbor and bank facts need optional GitHub or registry data rather than the
    static scan.

## 6. Suggested order

1. Decide section 5.
2. Fix the Taskfile-wrapper detection (WN-014).
3. Road-network traffic (WN-019); independent, and the shopping mall needs it.
4. Evidence file (WN-020); independent of the city, and serves WN-005.
5. Station growth (WN-027), then highway growth (WN-026) once traffic exists.
6. Overlays one by one, starting with supply chain, then harbor, bank, archive, court.
7. Coverage map of harness topics (WN-028) before adding more checks (WN-029).

## Layout decisions, 2026-10-29 and 2026-10-30

The agreed L3 layout (airport and station moved west, core connector to the highway, Shopping
Mall, northern goods industry, mountain tunnel, harbor bridge, west-east power line) lives in
the "City map (grid)" section of `apps/harness-city/DESIGN.md`. That file is the source of truth.

Finished on 2026-10-30: the mountain range runs along the whole north edge (z -30..-20) and the
highway comes out of a tunnel portal at z -22 (frame x 61.5..70.5). The isometric orthographic
camera with rotate buttons is pinned in `DESIGN.md`, `AGENTS.md` and `tools/check.py`. The plan
view artifact shows the same grid.

Decided on 2026-10-30: C7, the airport sits two cells further east (airport x 45..61, station
x 37..43). Still open from the grid: the exact position of the central station.
