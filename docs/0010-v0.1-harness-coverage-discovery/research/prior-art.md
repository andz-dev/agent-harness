---
type: 'Research'
title: 'Harness coverage: primary-source boundaries'
description: 'Prior art informing the distinction between declared controls, observed execution and trust.'
status: 'active'
created: '2026-11-04'
updated: '2026-11-04'
generated: 'agent'
verified: 'unverified'
owner: 'Andreas Elser'
tags: [research, harness, evidence]
sources:
  - 'Primary sources fetched on 2026-11-04; references below'
---

# Primary-Source Research

## Findings

| Source | Fetched fact | Implication for discovery |
| --- | --- | --- |
| CycloneDX | Defines bill-of-materials representations, including software components and relationships. ([1](#ref-1)) | A BOM artifact, its validation, and its association with a particular build are separate evidence questions. |
| OpenSSF Scorecard | Documents distinct checks for repository security practices, including CI, update tooling and token permissions. ([2](#ref-2)) | Keep an inventory of individual controls; a composite score must not conceal unknown evidence sources. |
| MCP security guidance | Describes local startup-command risks, explicit consent and sandboxing recommendations, and authorization threats. ([3](#ref-3)) | Static analysis can inspect declared commands without executing them; runtime authorization and sandbox behavior remain unverified. |
| VS Code Workspace Trust | Describes Restricted Mode and how workspace trust affects tasks, debugging and extension behavior. ([4](#ref-4)) | Repository recommendations do not establish which extensions are installed or the user's local trust state. |
| Agent Skills | Requires name and description in a skill's metadata; optional allowed-tools support is experimental and may vary by implementation. ([5](#ref-5)) | Metadata validation is useful, but a permission field is not portable enforcement proof. |

These implications are the author's scoping judgments, not security guarantees made by the sources.
No product or library is selected by this research.

## Gotchas / Unverified

- The first delegated search did not locate the Agent Skills specification. A direct fetch of
  the official specification corrected that search failure; absence of a discovered URL was
  not evidence that no standard existed. ([5](#ref-5))
- Source pages are mutable. Fetch dates identify this observation, not an immutable standards baseline.
- No live Scorecard scan, MCP connection, OAuth exchange, extension installation or CI API query
  was performed. Provider-specific runtime behavior is unverified.
- No tool-ecosystem counts, adoption figures or exhaustive claims from the delegated summary are
  relied on. They are unnecessary for this decision.
- A later specification must decide how independently supplied execution receipts are admitted,
  bound to revisions, expired and contradicted. This discovery does not design that integration.

## Implication

The proposed scope needs independent dimensions for topic applicability, artifact provenance,
check outcome and assurance depth. A declared check should not become "enforced" merely because
its workflow or skill file exists. MCP, skills and extensions require repository-scoped inventory
first; host state and remote execution evidence are separate opt-in sources.

## References

### ref-1

[1] CycloneDX, "CycloneDX", accessed 2026-11-04. https://cyclonedx.org/

### ref-2

[2] OpenSSF, "Scorecard Checks", accessed 2026-11-04. https://github.com/ossf/scorecard/blob/main/docs/checks.md

### ref-3

[3] Model Context Protocol, "Security Best Practices", accessed 2026-11-04. https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices

### ref-4

[4] Microsoft, "Workspace Trust", accessed 2026-11-04. https://code.visualstudio.com/docs/editor/workspace-trust

### ref-5

[5] Agent Skills, "Specification", accessed 2026-11-04. https://agentskills.io/specification
