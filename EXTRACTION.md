---
type: 'Provenance'
title: 'Standalone Extraction'
status: 'active'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Standalone Extraction

This repository starts with a clean snapshot from `andz-dev/developer-asset-manager`
at commit `c3e1120ec7bfb9e24486865196af7211687d73e6`. Its source repository and
uncommitted work were not moved or modified.

The audit source tree is `e5c34a57bd87454c2857bb9f907aea24805b11d8`.
[extraction-manifest.json](extraction-manifest.json) records the allowlisted
source/target mapping and checksums. `task integrity` verifies copied runtime
files and assets against that baseline. Documentation adaptations are separated
from unchanged source records; historical Git hashes are provenance, not commits
that exist in this clean repository.

## Included

- The existing skill code, tests, catalog, schema, prompts, dependency lock and
  cleared explanatory files, under `skills/harness-audit/`.
- Harness City runtime, adapter/build tools, vendor modules and model assets.
- An empty `docs/0001/.gitkeep` scaffold.
- The authored 0039 documentation, relocated into `docs/0002/` without generated logs.
- The owner-selected next-steps note, under `docs/0003/`.
- New root packaging, CI/checks, licensing and synthetic demo generation.

## Excluded

Original app datasets, generated HTML bundles, audit/sample reports, human scoring
inputs, private checkouts, local stores, credentials, environments, caches, logs,
unrelated documents and the source monorepo's Git history are not published.
The retained optional calibration helper needs separately provided and cleared
inputs; its original human-score dataset and sample reports are not included.

## Evidence Limits

The imported docs describe a historical adoption effort. Old pass counts, source
retirement operations and deployment warnings are not new execution results.
Use this repo's `task check`, not historical commands that refer to the former
monorepo. The relocated source-contract probe delegates to `task integrity`.

The demo contains four authored illustration profiles spanning all four city
tiers and district levels L0 through L3. No repository is audited to produce
these profiles, and no detector findings are fabricated. Scores are computed
with the unchanged weight/arithmetic functions. All four report-shaped objects
pass schema and arithmetic validation before the unchanged adapter converts
them. They are illustrations, not benchmark results or evidence that any real
project is secure or ready for agents. The earlier three fixture-audit examples
were replaced because they all fell in the lowest city tier.

Before public sharing, inspect the exact tracked content and embedded build
payloads. Automated pattern checks are useful but do not certify the absence of
all confidential information. Standalone HTML builds embed their selected data.

## Standalone Validation

The extracted skill passed its unchanged lint/format checks and all 137 tests.
Four synthetic illustration objects validated against its schema and converted
deterministically through the unchanged app adapter. Online and offline builds
completed; optional remote-font links are removed from offline output by the
root build wrapper, not by changing the copied app source.

Browser checks observed nonblank WebGL geometry and loaded assets at a desktop
viewport of 911 by 632 and a mobile viewport of 390 by 844, with no horizontal
overflow. Repository selection, camera rotation, zoom and fit controls were
exercised. The offline file rendered with HTTP(S) blocked, no network attempts,
no page errors and all 28 district/level asset previews present. Screenshots
are validation artifacts outside Git, not app assets.

Structural inspection found 62 GLB files with embedded resources. The source
roadmap body was preserved, and 0001 contains an empty .gitkeep. Integrity and
publication-pattern checks pass; these do not constitute a security guarantee.
Remote CI results are verified separately after the first push.

## Runtime Changes

Intentional changes to copied runtime files are recorded in the manifest as
`adapted-runtime`: `source_sha256` keeps the imported baseline and `sha256` the
reviewed new content, which `task integrity` verifies. The Harness City page,
adapter and app README were adapted on 2026-10-27 to explain districts, levels,
traffic, rail, power line and a new transit network, and to show per-check
findings and evidence. The synthetic demo still contains no findings.
