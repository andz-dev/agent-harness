---
type: 'Backlog'
title: 'What''s Next'
status: 'active'
created: '2026-10-27'
updated: '2026-10-27'
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

## Closed

Finished or abandoned rows (`Done`, `Promoted → … (done)`, `Won't Do`), kept as history only.

| ID | Type | Title | Description | Origin | Initial Approach Sketch | Effort | Depends On | Status |
|---|---|---|---|---|---|---|---|---|
| WN-001 | Feature | ~~Harness City explanations and transit~~ | Clickable buildings, streets, sites, rail and power line with explanations; per-district issues, evidence and level ladder; bus and metro lines from the central station by level. | Owner request: details below L3 (insights, issues, missing files) were not shown on the map. | Catalog checks and findings in the city data; panel cards per clicked object; line level = min(station, district) | Medium | None | Done |
