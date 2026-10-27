---
type: 'Roadmap'
title: 'Infrastructure Coverage Map'
status: 'proposed'
created: '2026-10-27'
updated: '2026-10-27'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
---

<!-- markdownlint-disable-next-line MD025 -->
# Infrastructure Coverage Map

Scope of this map: what harness-audit must detect, check and report for infrastructure as code (IaC),
containers, Docker Compose and devcontainers, and how that reaches the repo scan JSON. Everything here is a
proposal; the items are tracked as B-166 to B-190 in the skill's [BACKLOG](../../skills/harness-audit/BACKLOG.md).

## Starting point (verified in this repo)

- Detection now exists as an overlay (`scripts/detect_infra.py`). The check catalog still has no infrastructure check. `Dockerfile`, Compose files, `.devcontainer/`, Terraform and
  Kubernetes files are neither detected nor scored.
- `detect_stack.py` knows Python and Node (Go is out of scope). It has no notion of an infra component; the overlay detector lists infra by location instead.
- The scan JSON for Harness City has pillar levels only; it has no infra block.
- The audit is read-only and never runs audited code. That rule extends to `terraform`, `docker`, `kubectl`
  and `devcontainer`: infra is judged from files, never by running a plan, build or container.
- The harness adoption skill (the part that applies fixes, today only the `bootstrap.py` preview) is **not
  started**. It is Track F below.

## Design decisions

Confirmed by the owner on 2026-10-27: D1 overlay, and the overlay has its own level L0 to L3 (implemented, B-198); D3 order as recommended. Go is out of scope (B-156 dropped).

| # | Decision | Recommendation | Why |
| --- | --- | --- |
| D1 (decided: overlay with its own level) | Fold infra checks into the frozen 0-100 score, or report an infra overlay next to it? | Overlay first (own 0-100 and levels), fold in only after recalibration | Weights are frozen; adding checks to existing pillars changes scores of repos that ship a Dockerfile (immich, n8n, home-assistant-core) and would invalidate the calibration |
| D2 | Infra as an 8th pillar or as `applies_to` kinds inside the seven pillars? | Kinds inside the pillars for the overlay; no new pillar until recalibration | Keeps the pillar model and the city districts stable |
| D3 (decided) | Which IaC tools first? | Terraform/OpenTofu, then Bicep, then Helm/Kubernetes manifests, then Pulumi, CloudFormation/CDK, Ansible | Matches the owner's stack (Azure, Terraform) |
| D4 | Does the audit ever run `terraform validate` or `docker compose config`? | No | Read-only rule; static parsing only |

## Tracks

Status key: `todo` = nothing built; `partly done` = some items built. Done so far (all as an overlay that never changes the score):

- Track A, detection of all listed tools: `scripts/detect_infra.py` (B-166 to B-169, B-184).
- Track B, first set of checks for Dockerfile, Compose, devcontainer and Terraform/OpenTofu: `scripts/infra_checks.py`, 25 checks (B-171, B-175 to B-177), with a per-check roll-up (B-194) and the overlay's own level per area and overall (B-198, uncalibrated: B-202).
- Track E, the `infra` block in `report.json` and the Infrastructure section in `report.md` (B-181).

Still `todo`: the component model (B-170), Bicep, Kubernetes/Helm and the other IaC checks (B-172 to B-174), cross-cutting checks (B-178), infra entropy (B-179), the judgement prompt (B-180), the city adapter (B-182, B-183), the adoption skill (Track F), fixtures and calibration (Track G).

### Track A: Detection (prerequisite for everything)

| Item | Detect by | Backlog |
| --- | --- | --- |
| Terraform / OpenTofu / Terragrunt | `*.tf`, `*.tofu`, `terragrunt.hcl`, `.terraform.lock.hcl` | B-166 |
| Bicep / ARM | `*.bicep`, `azuredeploy.json`, `*.bicepparam` | B-166 |
| Kubernetes, Helm, Kustomize | `Chart.yaml`, `kustomization.yaml`, manifests with `apiVersion`/`kind` | B-166 |
| Pulumi, CloudFormation, CDK, Ansible | `Pulumi.yaml`, `template.yaml` with `AWSTemplateFormatVersion`, `cdk.json`, `playbook*.yml`, `ansible.cfg` | B-167 |
| Dockerfile, Containerfile | `Dockerfile*`, `Containerfile*`, `*.dockerfile` | B-168 |
| Docker Compose | `compose*.y?ml`, `docker-compose*.y?ml` | B-168 |
| Devcontainer | `.devcontainer/devcontainer.json`, `.devcontainer.json`, `.devcontainer/*/devcontainer.json` | B-169 |
| Other dev environments | `.gitpod.yml`, `.codespaces/`, `flake.nix`, `mise.toml`, `.tool-versions` | B-169 |
| Component model | An `infra` component type with kind, path and the files it owns, so monorepos with several stacks are scored per component | B-170 |

Detection must ignore vendored and generated paths (`.terraform/`, `node_modules/`, examples under `docs/`).

### Track B: Checks per area

Each check follows the catalog format (id, pillar, level, gate, `applies_to`, detector, evidence, rationale)
and is mechanical wherever possible. The pillar column says where it would sit.

**Terraform / OpenTofu (B-171)**

| Check idea | Pillar |
| --- | --- |
| Provider and module versions pinned (`required_providers` with versions, committed `.terraform.lock.hcl`) | Verification |
| `terraform fmt -check` and `validate` run in CI or a hook | Pipeline parity / Triggers |
| A plan runs on pull requests; apply only from a protected branch or tagged job | Pipeline parity |
| tflint, trivy/tfsec/checkov configured | Static guardrails |
| Remote state backend declared; no state files or `*.tfvars` with secrets tracked | Static guardrails |
| Variables have descriptions and types; outputs documented (terraform-docs) | Doc hygiene |
| Agent file states the safe workflow (plan only, no apply or destroy by an agent) | Orientation |

**Bicep / ARM (B-172):** `bicep build`/`lint` config (`bicepconfig.json`), what-if in CI, parameter files per
environment, pinned API versions.

**Kubernetes / Helm / Kustomize (B-173):** `helm lint` and `kubeconform` or `kubeval` in CI, values schema,
no `latest` image tags, resource limits present, a chart README.

**Pulumi, CloudFormation/CDK, Ansible (B-174):** `cfn-lint`, `ansible-lint`, preview step in CI, pinned
collections and requirements.

**Dockerfile (B-175)**

| Check idea | Pillar |
| --- | --- |
| `.dockerignore` exists | Static guardrails |
| hadolint configured and run in CI or a hook | Static guardrails / Parity |
| Base image pinned by version or digest (no `latest`) | Verification |
| Non-root `USER`, multi-stage build, `HEALTHCHECK` | Static guardrails |
| No secrets in `ENV`/`ARG`; no unpinned download piped into a shell | Static guardrails |
| Image build runs in CI (build only, no push on pull requests) | Pipeline parity |

**Docker Compose (B-176):** healthchecks, pinned images, no secrets inline, `.env.example` instead of `.env`
tracked, named volumes, a documented `docker compose up` workflow, `compose config` validated in CI,
profiles for dev/test separation, and port conflicts noted.

**Devcontainer (B-177)**

| Check idea | Pillar |
| --- | --- |
| `devcontainer.json` exists and is valid JSONC | Orientation |
| Image or Dockerfile pinned; features pinned | Verification |
| `postCreateCommand` runs the repo's setup entry point (same as the runner's setup target) | Workflow entry points |
| Extensions and settings include the repo's linter/formatter | Static guardrails |
| Same tool versions as CI (devcontainer vs CI matrix) | Pipeline parity |
| Agent file mentions the devcontainer and how an agent uses it | Orientation |
| CI builds the devcontainer (devcontainers/ci) | Pipeline parity |

**Cross-cutting (B-178):** infra changes trigger their own CI path filter; CODEOWNERS covers `infra/`;
Dependabot/Renovate covers Terraform, Docker and Actions ecosystems; secrets scanning (gitleaks) is configured.

### Track C: Entropy for infra (B-179)

Unused Terraform variables and modules, Compose services nothing references, Dockerfiles not built by any
CI job or Compose file, stale lockfile, duplicated environment folders, drift between `.env.example` and the
variables the code reads. These sit next to the existing orphan checks (ENR-*).

### Track D: Judgement layer (B-180)

New prompt `prompts/infra_quality.md`: does the agent file explain how to plan, validate and apply safely, which
environments exist, which commands are forbidden for agents, where secrets live. Same rules as the other
prompts: verbatim quotes, `unknown` when unsupported, status must match the note.

### Track E: Scan JSON and Harness City (B-181 to B-184)

- Add an `infra` block to `report.json` and to the scan export: detected kinds, files, per-area levels, findings.
- Schema change in `schema/report.schema.json` with a version bump, and an adapter update for Harness City
  (a new district or building layer for infra).
- Synthetic infra fixtures for the demo cities, clearly labelled synthetic.
- Show unsupported infra (found but not scored) in the report limitations so a score is never read as
  "infra is fine".

### Track F: Harness adoption skill (not started) (B-185 to B-188)

The adoption skill turns an audit into applied changes. Today only the proposal preview exists
(`scripts/bootstrap.py`, creates missing files only, never merges).

| Item | Detail | Backlog |
| --- | --- | --- |
| Skill shell | A separate `harness-adopt` skill that reads `report.json` and `triage.json`; the audit stays read-only | B-185 |
| Infra proposals | devcontainer.json wired to the runner's setup target, `.dockerignore`, hadolint config, Compose healthcheck stubs, Terraform CI job (fmt, validate, plan), tflint config, Dependabot ecosystems | B-186 |
| Safety | Dry run by default; one reviewable branch or diff; never touches existing files without a diff the user approves; never runs apply, destroy, `docker run` or any deploy | B-187 |
| Merge mode | Diff-based edits for existing files (Node hooks, Azure DevOps, monorepos) from B-151 to B-156 | B-188 |

### Track G: Fixtures, tests and calibration (B-189, B-190)

- Synthetic repos for each tool and each pass/fail case under the tests (no real project files).
- Calibration set for infra: pick 8 to 10 public repos with Terraform, Compose and devcontainers, collect gut
  scores from at least two raters before any weights are set (see B-145).
- A rule that infra checks must not change the frozen 0-100 score of the 18 calibration repos until D1 is
  decided; the overlay is verified by a test that compares the main score with and without infra files.

## Suggested order

1. A: detection and the `infra` component model (B-166 to B-170).
2. Terraform, Dockerfile, Compose, devcontainer checks (B-171, B-175, B-176, B-177) as an overlay.
3. Scan JSON and city adapter (B-181 to B-184) so results become visible.
4. Judgement prompt and entropy (B-179, B-180).
5. Bicep, Kubernetes, Helm, then the other IaC tools (B-172 to B-174).
6. Adoption skill (Track F) once at least the overlay checks are stable.
7. Calibration with new raters (Track G).
