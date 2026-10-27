---
type: 'Project Guide'
title: 'Infrastructure Level Calibration'
status: 'proposed'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Infrastructure Level Calibration

First comparison of the infrastructure overlay levels (L0 to L3, never part of the 0-100 score) with a human rating.
One rater, 35 cells (one cell is one infrastructure area in one repository), 15 repositories. The rater did not see the
tool's levels while voting.

## Files

| File | Purpose |
|---|---|
| `infra-level-vote.html` | Standalone configurator. Shows every infrastructure area with the checks per level, examples and the cells to rate. Open it in a browser; no server needed. |
| `infra-levels-evaluation.json` | Sidecar with the rater's 35 ratings and the tool's levels before and after the changes below. Load it with "Load sidecar", save changes with "Save sidecar". |

The page opens with the ratings embedded; "Show tool levels" reveals the tool's level next to each vote. Votes are kept
in the browser's local storage until you save a sidecar.

## Result

| Run | Exact match | Within one level | Mean absolute difference | Tool above / below rater |
|---|---|---|---|---|
| Before the changes | 23% | 77% | 1.00 | 4 / 23 |
| After the changes | 43% | 91% | 0.66 | 6 / 14 |

Changes applied (B-215): a check holds for an area when at least 60% of its locations pass (the secret checks `INF-X05`,
`INF-F03`, `INF-P03`, `INF-K06`, `INF-C03`, `INF-T06` stay all-or-nothing, and the worst locations stay in the roll-up);
`.dockerignore` (`INF-D01`) and the devcontainer create command (`INF-V03`) are no longer gates and sit at level 2;
`INF-A01` (pinned Ansible collections) moved to level 2.

## Limits

- One rater: the numbers show direction, not accuracy. A second rater is still open (B-190).
- The rater could see the check lists while voting, which may anchor the ratings.
- The rater never used L0 or L3. After the change the tool reaches L3 in 2 cells, both rated L2.
- Three cells still differ by two levels (Terraform in `examples` and `n8n`, Pulumi in `examples`): the lock file and
  version-constraint gates (`INF-T01`, `INF-T02`) and the Pulumi lock file check hold them at L0. They were left as they
  are to avoid fitting the tool to a single rater.
- The sidecar is the rater's own judgement of public repositories, committed on purpose at the owner's request.
