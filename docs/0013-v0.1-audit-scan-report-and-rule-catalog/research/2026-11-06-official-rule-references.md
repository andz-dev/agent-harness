---
type: 'Research'
title: 'Official audit rules and best practices per category'
description: 'Verified official sources for each of the nine finding categories, used to seed the static rule catalog references.'
status: 'active'
created: '2026-11-06'
updated: '2026-11-06'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [research, harness, catalog, references]
sources:
  - 'https://github.com/ossf/scorecard/blob/main/docs/checks.md'
  - 'https://csrc.nist.gov/pubs/sp/800/218/final'
  - 'https://slsa.dev/spec/v1.0/'
---

# Official audit rules and best practices per category

Retrieved 2026-11-06 by a delegated fetch that loaded each URL and matched its title. A source here is a candidate catalog reference; the implementation must re-verify each link before shipping it and must not copy page text, only title, publisher and URL.

## Verified sources

| Category | Source | Publisher | URL |
|---|---|---|---|
| testing | pytest documentation | pytest-dev | https://docs.pytest.org/en/stable/ |
| testing | Packaging Python Projects | PyPA | https://packaging.python.org/en/latest/tutorials/packaging-projects/ |
| testing | Test runner (Node.js) | OpenJS Foundation | https://nodejs.org/api/test.html |
| testing | Vitest guide | Vitest team | https://vitest.dev/guide/ |
| testing | Jest getting started | OpenJS Foundation | https://jestjs.io/docs/getting-started |
| testing | Coverage.py | Ned Batchelder | https://coverage.readthedocs.io/en/latest/ |
| code_standards | Ruff | Astral | https://docs.astral.sh/ruff/ |
| code_standards | ESLint documentation | OpenJS Foundation | https://eslint.org/docs/latest/ |
| code_standards | EditorConfig specification | EditorConfig project | https://spec.editorconfig.org/ |
| code_standards | PEP 8 | Python Software Foundation | https://peps.python.org/pep-0008/ |
| code_standards | mypy documentation | mypy project | https://mypy.readthedocs.io/en/stable/ |
| code_standards | Pyright | Microsoft | https://microsoft.github.io/pyright/ |
| code_standards | golangci-lint | golangci | https://golangci-lint.run/ |
| code_standards | rustfmt | Rust project | https://rust-lang.github.io/rustfmt/ |
| code_standards | Clippy | Rust project | https://doc.rust-lang.org/clippy/ |
| ci_pipeline | Workflow syntax for GitHub Actions | GitHub | https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax |
| ci_pipeline | Secure use reference (Actions hardening) | GitHub | https://docs.github.com/en/actions/reference/security/secure-use |
| ci_pipeline | About protected branches | GitHub | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches |
| ci_pipeline | Status checks | GitHub | https://docs.github.com/en/pull-requests/reference/status-checks |
| security | Scorecard checks | OpenSSF | https://github.com/ossf/scorecard/blob/main/docs/checks.md |
| security | SP 800-218 SSDF 1.1 | NIST | https://csrc.nist.gov/pubs/sp/800/218/final |
| security | Secrets Management Cheat Sheet | OWASP | https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html |
| security | OWASP Top 10 | OWASP | https://owasp.org/projects/top-ten |
| security | Secret scanning | GitHub | https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning |
| security | Adding a security policy (SECURITY.md) | GitHub | https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/add-security-policy |
| security | CIS Docker Benchmarks | CIS | https://www.cisecurity.org/benchmark/docker |
| security | Docker Engine security | Docker | https://docs.docker.com/engine/security/ |
| supply_chain | CycloneDX specification overview | CycloneDX / OWASP | https://cyclonedx.org/specification/overview/ |
| supply_chain | SPDX Specification 3.0.1 | SPDX / Linux Foundation | https://spdx.github.io/spdx-spec/v3.0.1/ |
| supply_chain | Minimum Elements for an SBOM | NTIA | https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom |
| supply_chain | SLSA specification v1.0 | OpenSSF / SLSA | https://slsa.dev/spec/v1.0/ |
| supply_chain | Open Source Project Security Baseline | OpenSSF | https://baseline.openssf.org/ |
| supply_chain | OpenSSF Best Practices criteria | OpenSSF | https://www.bestpractices.dev/en/criteria |
| supply_chain | Renovate docs | Mend | https://docs.renovatebot.com/ |
| supply_chain | uv project layout and lockfile | Astral | https://docs.astral.sh/uv/concepts/projects/layout/ |
| supply_chain | package-lock.json | npm | https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json/ |
| agent_guidance | AGENTS.md | agents.md community | https://agents.md/ |
| agent_guidance | How Claude remembers your project | Anthropic | https://code.claude.com/docs/en/memory |
| agent_guidance | Repository custom instructions for Copilot | GitHub | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions |
| agent_guidance | Custom instructions in VS Code | Microsoft | https://code.visualstudio.com/docs/agent-customization/custom-instructions |
| docs | markdownlint | David Anson | https://github.com/DavidAnson/markdownlint |
| docs | Diataxis | Daniele Procida | https://diataxis.fr/ |
| docs | Architectural Decision Records | adr.github.io | https://adr.github.io/ |
| docs | Setting guidelines for contributors | GitHub | https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors |
| workflow | pre-commit | pre-commit project | https://pre-commit.com/ |
| workflow | Task | taskfile.dev | https://taskfile.dev/ |
| workflow | githooks | Git project | https://git-scm.com/docs/githooks |
| infrastructure | Dockerfile best practices | Docker | https://docs.docker.com/build/building/best-practices/ |
| infrastructure | Docker Compose | Docker | https://docs.docker.com/compose/ |
| infrastructure | Pod Security Standards | Kubernetes | https://kubernetes.io/docs/concepts/security/pod-security-standards/ |
| infrastructure | Dependency lock file | HashiCorp | https://developer.hashicorp.com/terraform/language/files/dependency-lock |
| infrastructure | Terraform style guide | HashiCorp | https://developer.hashicorp.com/terraform/language/style |
| infrastructure | Use Bicep linter | Microsoft | https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter |
| infrastructure | CloudFormation best practices | AWS | https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html |
| infrastructure | Pulumi secrets handling | Pulumi | https://www.pulumi.com/docs/iac/concepts/secrets/ |
| infrastructure | Development containers | containers.dev | https://containers.dev/ |
| infrastructure | hadolint | hadolint project | https://github.com/hadolint/hadolint |
| infrastructure | kubeconform | yannh | https://github.com/yannh/kubeconform |

## Gotchas / unverified

- The Ansible best-practices page returned HTTP 429 and was dropped; no Ansible source is verified yet.
- No Dependabot-specific page could be verified: the obvious URL redirects to a differently titled page.
- SPDX 2.3 is only a redirect page; 3.0.1 is used.
- Several GitHub, VS Code and Pulumi links redirect; the catalog must store the final URL.
- Every link is a reference for orientation. A catalog entry says which public source a rule resembles, never that the rule implements that standard.

## Implication

Every category has verified official references; Ansible has none yet. The catalog can give every rule a category-level link set and add rule-level links where a source names the same practice (for example Scorecard `SAST`, `SBOM` and `Dependency-Update-Tool`, Docker best practices for non-root and pinned bases). Rule-level mappings are an owner-reviewable table, not an assurance claim.
