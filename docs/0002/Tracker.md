---
type: "Reference"
id: '0002'
version: "v0.2"
title: "Local Tracker For Complete Agent Harness Qualification"
description: "Parentage, claims, dependencies and resolution rules for the v0.2 harness qualification map."
status: "active"
created: "2026-10-26"
updated: "2026-10-26"
stale_after: "2026-11-09"
generated: "agent"
verified: "unverified"
owner: "Andreas Elser"
tags: ["wayfinder", "tracker", "agent-harness"]
sources:
  - "docs/skills/0036-v0.1-agent-harness-setup/Tracker.md, Wayfinding Operations"
---

<!-- markdownlint-disable-next-line MD025 -->
# Local Markdown Tracker

## As-Built Adoption Amendment

On 2026-10-27 the owner replaced prospective design with reverse engineering of
the existing frozen skill. Tickets with `resolution: superseded` are closed
scope exclusions, not accepted proposals. The three new AFK task records use
`resolution: source-reconstructed`: their evidence is source inspection, not
fabricated live HITL agreement. Run the existing checker without
`charting=True` for this retrospective map. Future changes to the skill still
require a separate owner-approved effort.

## Wayfinding Operations

The canonical map is [Complete Agent Harness Qualification](Map.md). Reuse the
original local-Markdown convention; create no remote issues or research branches.

| Operation | Convention |
| --- | --- |
| Identity | Filename stem under `wayfinder-tickets/`; narrate using linked titles |
| Parent | `map` contains this map's repository-relative path |
| Type | `ticket_type` carries a `wayfinder:` type; grilling is HITL |
| Claim | Set `claimed_by` before working an open ticket; omit while unclaimed |
| Blocking | `blocked_by` lists sibling filename stems; dependencies are acyclic |
| State | `open` or `closed`; derive the frontier rather than storing it |
| Frontier | Open, unclaimed children with all blockers closed, ordered by filename |
| Resolution | Append dated `## Resolution` and live owner confirmation, then close |
| Index | Link only closed child decisions in the map's Decisions So Far |
| Exclusion | Close out-of-scope tickets and link under Out Of Scope, not decisions |

Use JSON-compatible frontmatter for checker fields. Do not write empty claim or
resolution values. Create child identities before adding dependency edges in a
second pass. Charting closes nothing; work at most one HITL ticket per session.
The workflow remains serial without subagent dispatch.

## Query And Validate

Reuse the existing read-only checker without copying it. From the repo root:

```bash
uv run --python 3.14 python -c 'import runpy; from pathlib import Path; ns = runpy.run_path("docs/skills/0032-v0.1-artifact-chain-atlas/scripts/check_wayfinder.py"); check = ns["check"]; check.__globals__["__file__"] = str(Path("docs/0002/scripts/check_wayfinder.py").resolve()); check(charting=True)'
```

The synthetic `__file__` supplies this folder only; no script is created. Remove
`charting=True` after ticket work begins. The checker covers child identity,
parentage, types, states, claims, dependency references/cycles and map closure.
It cannot establish semantic completeness, runtime enforcement or owner review.

## Session Discipline

Claim only an open, unblocked ticket before work. Resolve it only after the live
owner exchange. Release a claim if the owner is unavailable. Closure of the map
requires every child closed, no decision-level fog and explicit owner acceptance
of the specification handoff. Structural validation alone cannot close the map.
