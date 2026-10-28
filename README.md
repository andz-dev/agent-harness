---
type: 'Project Guide'
title: 'Agent Harness'
status: 'active'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Agent Harness

Audit a Python or Node repository's agent harness, inspect its evidence and fix
plan, and explore the results in Harness City.

- [harness-audit](skills/harness-audit/SKILL.md) performs static and local Git
  checks, prepares bounded agent-judgment tasks, validates quoted answers, and
  produces a scored report and counterfactual fix plan.
- [Harness City](apps/harness-city/README.md) visualizes report data as an
  interactive 3D city. The checked-in demo is synthetic, not a real audit.
- [Adoption documentation](docs/0002/README.md) records the source implementation
  and its limitations. [Next steps](docs/0003/Repo%20Harness%20Next%20Steps.md)
  remain proposals, not implemented capabilities.
- [History and quality](docs/0008-v0.1-harness-history-and-quality/Map.md) reconstructs
  local commits and the current implementation in a basic versioned spec bundle.
- [Development guide](CONTRIBUTING.md) explains automated browser tests and safe audit history.

The demo includes four illustrative cities: Absent/Neglected, Working,
Prosperous, and Thriving. Together they show district levels L0 through L3;
Thriving is the default view. Their scores follow the existing pillar weights,
but their levels are deliberately authored examples, not detector findings.

The audit never runs the audited repository's code. A static score or its
"Enforced" level is not proof of actual test execution, hook activation, CI
success, security, or agent compliance. Bootstrap is separate and proposal-first;
explicit `--apply` creates missing files but never merges existing ones.

## Run

Install Python 3.11+, uv, and Task. From this checkout:

```bash
task setup
task check
task serve
```

Setup includes the locked city browser-test package and matching Chromium. Node 22+
is required (CI uses Node 24). `task check` executes the Python suite, local tool
regressions and real desktop/mobile browser tests, not only file-presence checks.
Use `task app:test` for city-only browser verification. Test output stays ignored.

`task serve` opens the static app at <http://localhost:8001>. Set `PORT` to use
another available port. No cloud service or API key is required for the demo.

Audit a local repository using the unchanged skill's own task runner:

```bash
task --dir skills/harness-audit audit -- /path/to/repository --out /path/to/reports/example
```

Follow the [skill workflow](skills/harness-audit/SKILL.md) for the optional
quote-validated agent-answer pass. Review data before sharing it: reports may
include repository paths, names and excerpts. Reports, model answers, build
output and local secrets are excluded from Git by default.

## Convert And Build

```bash
python3 apps/harness-city/tools/report_to_city.py /path/to/report.json -o apps/harness-city/data/cities.json
task app:build
```

Both network-backed and offline standalone HTML builds go to the app's ignored
`dist/` directory. They embed the selected data: rebuild from synthetic or
explicitly cleared data before publishing. Do not commit private datasets.
Use `task app:build` for offline distribution: it also removes the copied
builder's optional Google Fonts links, so the offline file uses local fallback
fonts without making network requests. The online version still uses CDN
modules and optional remote fonts.

## Layout

| Path | Purpose |
| --- | --- |
| `skills/harness-audit/` | Audit implementation, catalog, schema, prompts and tests; intentional adaptations are hash-pinned |
| `apps/harness-city/` | Static visualization, model assets and report adapter |
| `docs/0001/.gitkeep` | Reserved empty documentation scaffold |
| `docs/0002/` | Imported and relocated 0039 as-built documentation |
| `docs/0003/` | Owner-provided future roadmap |
| `docs/0008-v0.1-harness-history-and-quality/` | Basic retrospective and current quality implementation |
| `tools/` | Extraction integrity, public-demo and documentation checks |

This repository starts from an allowlisted snapshot, not the source monorepo's
history. Original datasets, calibration reports, generated HTML bundles and
private checkouts are not imported. See [provenance](EXTRACTION.md).

## License

Project code is MIT licensed; see [LICENSE](LICENSE). Preserve the app's
[third-party notices](apps/harness-city/NOTICE.md) and
[third-party license texts](THIRD_PARTY_LICENSES.md) when redistributing assets
or vendor modules.
