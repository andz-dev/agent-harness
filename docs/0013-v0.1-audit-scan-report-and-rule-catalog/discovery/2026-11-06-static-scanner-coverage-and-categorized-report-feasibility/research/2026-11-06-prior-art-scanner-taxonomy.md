---
type: 'Research'
title: 'Prior art: scanner topics, SBOM names and Go/Rust tool config files'
description: 'Independent source for the finding-category taxonomy and for static detection of scanner configuration in Python, Node, Go and Rust.'
status: 'active'
created: '2026-11-06'
updated: '2026-11-06'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [research, harness, scanners]
sources:
  - 'https://github.com/ossf/scorecard/blob/main/docs/checks.md'
  - 'https://cyclonedx.org/specification/overview/'
  - 'https://golangci-lint.run/docs/configuration/file/'
  - 'https://rust-lang.github.io/rustfmt/'
  - 'https://doc.rust-lang.org/clippy/configuration.html'
  - 'https://embarkstudios.github.io/cargo-deny/checks/cfg.html'
---

# Prior art: scanner topics, SBOM names and Go/Rust tool config files

Retrieved 2026-11-06 by a delegated read-only fetch; each claim carries its source number.

## Findings

- OpenSSF Scorecard names eight checks that match the requested scan categories: `SAST`, `Vulnerabilities`, `SBOM`, `License`, `Dependency-Update-Tool`, `Pinned-Dependencies`, `Security-Policy` and `Fuzzing` [1].
- Scorecard detects these by presence signals only: CodeQL or SonarCloud in a workflow for SAST, OSV usage for vulnerabilities, Dependabot or Renovate for update tools, `SECURITY.md` for policy, `LICENSE`-style files for license [1]. That is the same static-presence class this audit is limited to.
- Scorecard has no secret-scanning check and no linting check [1]. Both categories need this audit's own definition.
- CycloneDX documents `bom.json` and `bom.xml` as conventional names and `*.cdx.json` / `*.cdx.xml` as recognised patterns [2].
- golangci-lint reads `.golangci.yml`, `.golangci.yaml`, `.golangci.toml` or `.golangci.json` [3].
- rustfmt reads `rustfmt.toml` or `.rustfmt.toml` [4]; clippy reads `clippy.toml` or `.clippy.toml` and also `[lints.clippy]` in `Cargo.toml` [5]; cargo-deny reads `deny.toml`, `.deny.toml`, `.cargo/deny.toml` or `.config/deny.toml` [6].

## Gotchas / unverified

- SPDX file-name conventions were not verified: the specification pages fetched state none.
- cargo-audit's `.cargo/audit.toml` comes from an example file in the project repository, not from its documentation. Treat as unverified.
- govulncheck showed no config file in the fetched tutorial; a config file is unverified and probably does not exist, so detection must rely on workflow text.
- The clippy page marks its config file as unstable [5].

## Implication

A static category set can reuse Scorecard's presence-based vocabulary (SAST, vulnerabilities, SBOM, license, dependency updates, security policy) and add secret scanning and coding standards/linting from this audit's own catalog. Go and Rust linter and scanner detection is feasible from config file names and workflow text without running any tool. Detection says a tool is configured, never that a scan ran or passed.

## References

[1] OpenSSF Scorecard checks, https://github.com/ossf/scorecard/blob/main/docs/checks.md, retrieved 2026-11-06.
[2] CycloneDX specification overview, https://cyclonedx.org/specification/overview/, retrieved 2026-11-06.
[3] golangci-lint configuration file, https://golangci-lint.run/docs/configuration/file/, retrieved 2026-11-06.
[4] rustfmt configuration, https://rust-lang.github.io/rustfmt/, retrieved 2026-11-06.
[5] Clippy configuration, https://doc.rust-lang.org/clippy/configuration.html, retrieved 2026-11-06.
[6] cargo-deny config, https://embarkstudios.github.io/cargo-deny/checks/cfg.html, retrieved 2026-11-06.
