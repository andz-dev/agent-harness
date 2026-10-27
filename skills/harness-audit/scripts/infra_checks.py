#!/usr/bin/env python3
"""Static infrastructure checks for harness-audit (overlay, B-171, B-175, B-176, B-177).

Evaluates Dockerfiles, Compose files, devcontainers and Terraform/OpenTofu directories found by
detect_infra. Files are only read; nothing is executed. Results are reported next to the score and
never change it (decision D1). Each finding is pass, fail or not_applicable with quoted evidence.
"""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

CI_FILES = (
    ".github/workflows/",
    ".gitlab-ci.yml",
    "azure-pipelines",
    ".azure-pipelines/",
    ".circleci/config.yml",
    "Jenkinsfile",
    ".buildkite/",
)
HOOK_FILES = (
    ".pre-commit-config.yaml",
    ".pre-commit-config.yml",
    "lefthook.yml",
    "lefthook.yaml",
    ".husky/",
    "Taskfile",
    "Makefile",
    "justfile",
)
SECRET_NAME = re.compile(r"(PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY|PRIVATE_?KEY|CREDENTIAL)", re.I)
RUNNER_WORDS = re.compile(r"\b(task|make|just|npm|pnpm|yarn|uv|pip|poetry|pdm|nox|tox|bun)\b")
PASS_RATIO = 0.6  # same rule as the pillars: a level needs 60% of its checks
GATES = {"INF-B01", "INF-K06", "INF-D01", "INF-D02", "INF-C01", "INF-C03", "INF-V01", "INF-V03", "INF-T01", "INF-T02", "INF-T06"}
AREAS = {"D": "dockerfile", "C": "compose", "V": "devcontainer", "T": "terraform"}

CHECKS = {
    "INF-D01": ("dockerfile", 1, ".dockerignore exists (next to the Dockerfile or at the repo root)"),
    "INF-D02": ("dockerfile", 2, "Base images are pinned to a tag or digest (no latest, no bare name)"),
    "INF-D03": ("dockerfile", 2, "The image runs as a non-root USER"),
    "INF-D04": ("dockerfile", 3, "HEALTHCHECK is defined"),
    "INF-D05": ("dockerfile", 2, "hadolint is configured or runs in CI or a hook"),
    "INF-D06": ("dockerfile", 2, "No literal secrets in ENV or ARG"),
    "INF-D07": ("dockerfile", 3, "An image build runs in CI"),
    "INF-C01": ("compose", 2, "Service images are pinned to a tag or digest"),
    "INF-C02": ("compose", 3, "Every service defines a healthcheck"),
    "INF-C03": ("compose", 2, "No literal secrets in environment"),
    "INF-C04": ("compose", 2, "A .env.example exists and .env is not tracked"),
    "INF-C05": ("compose", 3, "`compose config` validates the file in CI or a hook"),
    "INF-V01": ("devcontainer", 1, "devcontainer.json parses (JSON with comments)"),
    "INF-V02": ("devcontainer", 2, "Image and features are pinned"),
    "INF-V03": ("devcontainer", 1, "A create or post-create command prepares the environment"),
    "INF-V04": ("devcontainer", 2, "The setup command calls the repository's own runner or installer"),
    "INF-V05": ("devcontainer", 2, "Editor extensions or settings are declared"),
    "INF-V06": ("devcontainer", 3, "CI builds the devcontainer"),
    "INF-T01": ("terraform", 1, "Provider lock file (.terraform.lock.hcl) is committed"),
    "INF-T02": ("terraform", 1, "required_providers declares version constraints"),
    "INF-T03": ("terraform", 2, "fmt, validate or tflint runs in CI or a hook"),
    "INF-T04": ("terraform", 2, "A plan runs in CI"),
    "INF-T05": ("terraform", 3, "A security scanner (tflint, trivy, tfsec, checkov) is configured or runs in CI"),
    "INF-T06": ("terraform", 1, "No state files or tfvars with values are tracked"),
    "INF-B01": ("bicep", 1, "bicepconfig.json configures the linter"),
    "INF-B02": ("bicep", 1, "Parameter files exist (.bicepparam or parameters.json)"),
    "INF-B03": ("bicep", 2, "bicep build or lint runs in CI or a hook"),
    "INF-B04": ("bicep", 2, "A what-if or validate step runs in CI"),
    "INF-B05": ("bicep", 2, "Secret-like parameters are marked @secure()"),
    "INF-B06": ("bicep", 3, "No preview API versions"),
    "INF-K01": ("kubernetes", 2, "Container images are pinned to a tag or digest"),
    "INF-K02": ("kubernetes", 2, "Containers set resource limits"),
    "INF-K03": ("kubernetes", 3, "Containers run non-root (securityContext)"),
    "INF-K04": ("kubernetes", 3, "Readiness and liveness probes are defined"),
    "INF-K05": ("kubernetes", 2, "Manifests are validated in CI (kubeconform, helm lint, kustomize build, conftest, dry-run)"),
    "INF-K06": ("kubernetes", 1, "No Secret manifest with literal data"),
    "INF-K07": ("kubernetes", 3, "Helm chart has values.schema.json"),
    "INF-T07": ("terraform", 3, "A remote backend or cloud block is declared"),
}


class Repo:
    def __init__(self, root: Path, files: list[str]):
        self.root, self.files = root, files
        self.fileset = set(files)
        self._text: dict[str, str] = {}
        self.ci = "\n".join(self.text(f) for f in files if f.startswith(CI_FILES) or any(f.startswith(c) for c in CI_FILES))
        self.hooks = "\n".join(self.text(f) for f in files if any(f.startswith(h) or f.split("/")[-1].startswith(h) for h in HOOK_FILES))

    def text(self, rel: str) -> str:
        if rel not in self._text:
            try:
                self._text[rel] = (self.root / rel).read_text(encoding="utf-8", errors="replace")[:400_000]
            except OSError:
                self._text[rel] = ""
        return self._text[rel]

    def has(self, pattern: str) -> bool:
        return re.search(pattern, self.ci + "\n" + self.hooks, re.I) is not None


def finding(cid: str, scope: str, status: str, evidence: list[dict], note: str = "") -> dict:
    area, level, title = CHECKS[cid]
    return {
        "check_id": cid,
        "area": area,
        "level": level,
        "title": title,
        "scope": scope,
        "status": status,
        "evidence": evidence[:3],
        "note": note,
    }


def ev(path: str, snippet: str, line: int | None = None) -> dict:
    out = {"path": path, "snippet": snippet[:160]}
    if line:
        out["line"] = line
    return out


def line_of(text: str, pattern: str) -> tuple[int | None, str]:
    for i, ln in enumerate(text.splitlines(), 1):
        if re.search(pattern, ln):
            return i, ln.strip()
    return None, ""


# ---- Dockerfile ----------------------------------------------------------------------------------


def docker_checks(repo: Repo, path: str) -> list[dict]:
    text = repo.text(path)
    out = []
    parent = PurePosixPath(path).parent
    has_ignore = any(f in repo.fileset for f in ((parent / ".dockerignore").as_posix().lstrip("./"), ".dockerignore"))
    out.append(
        finding(
            "INF-D01",
            path,
            "pass" if has_ignore else "fail",
            [ev(path, "FROM ...")] if not has_ignore else [ev(".dockerignore", "present")],
        )
    )

    stages, bad = set(), []
    for i, ln in enumerate(text.splitlines(), 1):
        m = re.match(r"\s*FROM\s+(?:--\S+\s+)?(\S+)(?:\s+AS\s+(\S+))?", ln, re.I)
        if not m:
            continue
        image = m.group(1)
        if image.lower() != "scratch" and image not in stages and "$" not in image and "@sha256:" not in image:
            name = image.rsplit("/", 1)[-1]
            if ":" not in name or name.endswith(":latest"):
                bad.append(ev(path, ln.strip(), i))
        if m.group(2):
            stages.add(m.group(2))
    out.append(finding("INF-D02", path, "fail" if bad else "pass", bad or [ev(path, "all FROM lines pinned")]))

    users = [(i, ln.strip()) for i, ln in enumerate(text.splitlines(), 1) if re.match(r"\s*USER\s+", ln, re.I)]
    last = users[-1] if users else None
    root_user = last is None or re.match(r"\s*USER\s+(root|0)(:|\s|$)", last[1], re.I)
    out.append(
        finding(
            "INF-D03", path, "fail" if root_user else "pass", [ev(path, last[1], last[0])] if last else [ev(path, "no USER instruction")]
        )
    )

    i, ln = line_of(text, r"^\s*HEALTHCHECK\b")
    out.append(finding("INF-D04", path, "pass" if i else "fail", [ev(path, ln, i)] if i else [ev(path, "no HEALTHCHECK instruction")]))

    cfg = [f for f in repo.files if re.search(r"(^|/)\.hadolint\.ya?ml$", f)]
    ran = repo.has(r"hadolint")
    out.append(
        finding(
            "INF-D05",
            path,
            "pass" if cfg or ran else "fail",
            [ev(cfg[0], "hadolint config")]
            if cfg
            else [ev("CI/hooks", "hadolint")]
            if ran
            else [ev(path, "no hadolint config or CI step")],
        )
    )

    leaks = []
    for i, ln in enumerate(text.splitlines(), 1):
        m = re.match(r"\s*(ENV|ARG)\s+([A-Za-z0-9_]+)(?:=|\s+)(\S+)", ln, re.I)
        if m and SECRET_NAME.search(m.group(2)) and not m.group(3).startswith(("$", '""', "''")):
            leaks.append(ev(path, ln.strip().split("=")[0] + "=…", i))
    out.append(finding("INF-D06", path, "fail" if leaks else "pass", leaks or [ev(path, "no secret-like ENV or ARG values")]))

    built = repo.has(r"docker(\s+buildx)?\s+build|docker/build-push-action|compose\s+build|buildah|kaniko")
    out.append(
        finding(
            "INF-D07", path, "pass" if built else "fail", [ev("CI/hooks", "image build")] if built else [ev(path, "no image build in CI")]
        )
    )
    return out


# ---- Compose -------------------------------------------------------------------------------------


def compose_checks(repo: Repo, path: str) -> list[dict]:
    text = repo.text(path)
    try:
        doc = yaml.safe_load(text) if yaml else None
    except Exception:  # noqa: BLE001
        doc = None
    services = (doc or {}).get("services") if isinstance(doc, dict) else None
    if not isinstance(services, dict) or not services:
        return [finding(c, path, "not_applicable", [], "no services found") for c in CHECKS if c.startswith("INF-C")]
    out, unpinned, no_health, leaks = [], [], [], []
    for name, svc in services.items():
        if not isinstance(svc, dict):
            continue
        image = svc.get("image")
        if isinstance(image, str) and not svc.get("build") and "$" not in image and "@sha256:" not in image:
            tag = image.rsplit("/", 1)[-1]
            if ":" not in tag or tag.endswith(":latest"):
                i, ln = line_of(text, rf"image:\s*{re.escape(image)}")
                unpinned.append(ev(path, f"{name}: {image}", i))
        if "healthcheck" not in svc and (image or svc.get("build")):
            no_health.append(ev(path, f"service {name} has no healthcheck", line_of(text, rf"^\s*{re.escape(str(name))}:")[0]))
        env = svc.get("environment") or {}
        pairs = env.items() if isinstance(env, dict) else [tuple(str(e).split("=", 1)) + ("",) for e in env if "=" in str(e)]
        for pair in pairs:
            key, val = pair[0], str(pair[1]) if len(pair) > 1 and pair[1] is not None else ""
            if SECRET_NAME.search(str(key)) and val and not val.startswith("$") and not val.startswith("${"):
                leaks.append(ev(path, f"{name}: {key}=…", line_of(text, rf"{re.escape(str(key))}")[0]))
    out.append(finding("INF-C01", path, "fail" if unpinned else "pass", unpinned or [ev(path, "all images pinned")]))
    out.append(finding("INF-C02", path, "fail" if no_health else "pass", no_health or [ev(path, "all services have healthchecks")]))
    out.append(finding("INF-C03", path, "fail" if leaks else "pass", leaks or [ev(path, "no literal secret values")]))
    uses_env = "env_file" in text or "${" in text
    tracked_env = [f for f in repo.files if f.split("/")[-1] == ".env"]
    example = [f for f in repo.files if re.search(r"(^|/)\.env\.(example|sample|template)$", f)]
    if not uses_env:
        out.append(finding("INF-C04", path, "not_applicable", [], "no env_file or variable substitution"))
    else:
        ok = bool(example) and not tracked_env
        out.append(
            finding(
                "INF-C04",
                path,
                "pass" if ok else "fail",
                [ev(example[0], "example present")]
                if ok
                else [ev(tracked_env[0] if tracked_env else path, "tracked .env" if tracked_env else "no .env.example")],
            )
        )
    validated = repo.has(r"compose\s+(-f\s+\S+\s+)?config")
    out.append(
        finding(
            "INF-C05",
            path,
            "pass" if validated else "fail",
            [ev("CI/hooks", "compose config")] if validated else [ev(path, "no `compose config` step")],
        )
    )
    return out


# ---- Devcontainer --------------------------------------------------------------------------------


def strip_jsonc(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?m)^\s*//.*$", "", text)
    text = re.sub(r'(?m)(?<=[,{\[\s"\d])\s//[^"\n]*$', "", text)
    return re.sub(r",(\s*[}\]])", r"\1", text)


def devcontainer_checks(repo: Repo, path: str) -> list[dict]:
    text = repo.text(path)
    try:
        doc = json.loads(strip_jsonc(text))
        if not isinstance(doc, dict):
            raise ValueError
    except ValueError:
        out = [finding("INF-V01", path, "fail", [ev(path, "does not parse as JSON with comments")])]
        return out + [finding(c, path, "not_applicable", [], "unparseable") for c in CHECKS if c.startswith("INF-V") and c != "INF-V01"]
    out = [finding("INF-V01", path, "pass", [ev(path, "valid")])]
    image = doc.get("image")
    problems = []
    if isinstance(image, str) and "@sha256:" not in image and (":" not in image.rsplit("/", 1)[-1] or image.endswith(":latest")):
        problems.append(ev(path, f"image: {image}", line_of(text, r'"image"')[0]))
    for feat in doc.get("features") or {}:
        if not re.search(r":\d|@sha256:", feat):
            problems.append(ev(path, f"feature {feat} has no version", line_of(text, re.escape(feat))[0]))
    if image is None and "build" not in doc and "dockerComposeFile" not in doc:
        problems.append(ev(path, "no image, build or dockerComposeFile"))
    out.append(finding("INF-V02", path, "fail" if problems else "pass", problems or [ev(path, "image and features pinned")]))
    cmds = {k: doc[k] for k in ("onCreateCommand", "updateContentCommand", "postCreateCommand") if doc.get(k)}
    out.append(
        finding(
            "INF-V03",
            path,
            "pass" if cmds else "fail",
            [ev(path, f"{k} defined", line_of(text, k)[0]) for k in cmds] or [ev(path, "no onCreate, updateContent or postCreate command")],
        )
    )
    if not cmds:
        out.append(finding("INF-V04", path, "not_applicable", [], "no setup command"))
    else:
        joined = json.dumps(cmds)
        out.append(finding("INF-V04", path, "pass" if RUNNER_WORDS.search(joined) else "fail", [ev(path, joined[:140])]))
    custom = (doc.get("customizations") or {}).get("vscode") or {}
    declared = bool(custom.get("extensions") or custom.get("settings") or doc.get("extensions") or doc.get("settings"))
    out.append(
        finding(
            "INF-V05",
            path,
            "pass" if declared else "fail",
            [ev(path, "extensions or settings declared")] if declared else [ev(path, "no extensions or settings")],
        )
    )
    built = repo.has(r"devcontainers/ci|devcontainer\s+(build|up)")
    out.append(
        finding(
            "INF-V06",
            path,
            "pass" if built else "fail",
            [ev("CI/hooks", "devcontainer build")] if built else [ev(path, "CI never builds the devcontainer")],
        )
    )
    return out


# ---- Terraform / OpenTofu ------------------------------------------------------------------------


def terraform_checks(repo: Repo, scope: str, files: list[str]) -> list[dict]:
    tf = [f for f in files if f.endswith((".tf", ".tofu", ".tf.json"))]
    if not tf:
        return []
    text = "\n".join(repo.text(f) for f in tf)
    first = tf[0]
    out = []
    lock = [f for f in files if f.endswith(".terraform.lock.hcl")]
    out.append(
        finding("INF-T01", scope, "pass" if lock else "fail", [ev(lock[0], "lock file")] if lock else [ev(first, "no .terraform.lock.hcl")])
    )
    m = re.search(r"required_providers\s*\{(.*?)\n\s*\}\s*\n", text, re.S)
    if not m:
        out.append(finding("INF-T02", scope, "fail", [ev(first, "no required_providers block")]))
    else:
        unversioned = "version" not in m.group(1)
        out.append(
            finding(
                "INF-T02",
                scope,
                "fail" if unversioned else "pass",
                [ev(first, "required_providers without version" if unversioned else "versions declared")],
            )
        )
    fmt = repo.has(r"(terraform|tofu)\s+(fmt|validate)|tflint|pre-commit-terraform|terraform_(fmt|validate)")
    out.append(
        finding(
            "INF-T03",
            scope,
            "pass" if fmt else "fail",
            [ev("CI/hooks", "fmt/validate/tflint")] if fmt else [ev(first, "no fmt, validate or tflint step")],
        )
    )
    plan = repo.has(r"(terraform|tofu)\s+plan|terraform-plan|tofu-plan|atlantis")
    out.append(
        finding("INF-T04", scope, "pass" if plan else "fail", [ev("CI/hooks", "plan")] if plan else [ev(first, "no plan step in CI")])
    )
    scanner = [f for f in repo.files if re.search(r"(^|/)(\.tflint\.hcl|\.tfsec/|\.checkov\.ya?ml|trivy\.ya?ml)", f)]
    ran = repo.has(r"tfsec|trivy|checkov|terrascan|snyk\s+iac")
    out.append(
        finding(
            "INF-T05",
            scope,
            "pass" if scanner or ran else "fail",
            [ev(scanner[0], "scanner config")] if scanner else [ev("CI/hooks", "scanner")] if ran else [ev(first, "no scanner")],
        )
    )
    tracked = [
        f
        for f in repo.files
        if re.search(r"\.tfstate(\.backup)?$", f) or (re.search(r"\.tfvars$", f) and not re.search(r"(example|sample|template)", f))
    ]
    out.append(
        finding(
            "INF-T06",
            scope,
            "fail" if tracked else "pass",
            [ev(t, "tracked state or tfvars") for t in tracked[:3]] or [ev(first, "none tracked")],
        )
    )
    is_root = bool(re.search(r"\bprovider\s+\"|required_providers", text))
    if not is_root:
        out.append(finding("INF-T07", scope, "not_applicable", [], "looks like a module without providers"))
    else:
        i, ln = line_of(text, r"^\s*(backend\s+\"|cloud\s*\{)")
        out.append(
            finding(
                "INF-T07",
                scope,
                "pass" if i or re.search(r"\bbackend\s+\"|\bcloud\s*\{", text) else "fail",
                [ev(first, ln or "backend declared")]
                if re.search(r"\bbackend\s+\"|\bcloud\s*\{", text)
                else [ev(first, "no backend or cloud block")],
            )
        )
    return out


# ---- Bicep ---------------------------------------------------------------------------------------


def bicep_checks(repo: Repo, scope: str, files: list[str]) -> list[dict]:
    templates = [f for f in files if f.endswith(".bicep")]
    if not templates:
        return []
    first = templates[0]
    base = scope if scope != "." else ""
    near = lambda name: any(f == (f"{base}/{name}" if base else name) or f == name for f in repo.files)  # noqa: E731
    cfg = near("bicepconfig.json")
    out = [
        finding(
            "INF-B01", scope, "pass" if cfg else "fail", [ev("bicepconfig.json", "present")] if cfg else [ev(first, "no bicepconfig.json")]
        )
    ]
    params = [
        f
        for f in repo.files
        if f.endswith(".bicepparam") or re.search(r"\.parameters(\.[\w-]+)?\.json$", f) or f.endswith("/parameters.json")
    ]
    out.append(
        finding(
            "INF-B02",
            scope,
            "pass" if params else "fail",
            [ev(params[0], "parameter file")] if params else [ev(first, "no parameter files")],
        )
    )
    built = repo.has(r"az\s+bicep\s+(build|lint)|bicep\s+(build|lint)|bicep-build|azure/bicep")
    out.append(
        finding(
            "INF-B03",
            scope,
            "pass" if built else "fail",
            [ev("CI/hooks", "bicep build or lint")] if built else [ev(first, "no build or lint step")],
        )
    )
    whatif = repo.has(r"what-?if|az\s+deployment\s+\w+\s+validate|azure/arm-deploy")
    out.append(
        finding(
            "INF-B04",
            scope,
            "pass" if whatif else "fail",
            [ev("CI/hooks", "what-if or validate")] if whatif else [ev(first, "no what-if or validate step")],
        )
    )
    bad = []
    for f in templates:
        lines = repo.text(f).splitlines()
        for i, ln in enumerate(lines, 1):
            m = re.match(r"\s*param\s+(\w+)\s+string", ln)
            if m and SECRET_NAME.search(m.group(1)) and not any("@secure()" in x for x in lines[max(0, i - 4) : i - 1]):
                bad.append(ev(f, ln.strip(), i))
    out.append(finding("INF-B05", scope, "fail" if bad else "pass", bad or [ev(first, "secret-like params are @secure()")]))
    preview = []
    for f in templates:
        for i, ln in enumerate(repo.text(f).splitlines(), 1):
            if re.search(r"@\d{4}-\d{2}-\d{2}-preview", ln):
                preview.append(ev(f, ln.strip(), i))
    out.append(finding("INF-B06", scope, "fail" if preview else "pass", preview or [ev(first, "no preview API versions")]))
    return out


# ---- Kubernetes ----------------------------------------------------------------------------------


def _documents(text: str) -> list[dict]:
    if not yaml:
        return []
    try:
        return [d for d in yaml.safe_load_all(text) if isinstance(d, dict) and d.get("kind") and d.get("apiVersion")]
    except Exception:  # noqa: BLE001
        return []


def _pod_spec(doc: dict) -> dict | None:
    kind = doc.get("kind")
    spec = doc.get("spec") or {}
    if kind == "Pod":
        return spec
    if kind in ("Deployment", "StatefulSet", "DaemonSet", "ReplicaSet", "Job"):
        return (spec.get("template") or {}).get("spec")
    if kind == "CronJob":
        return (((spec.get("jobTemplate") or {}).get("spec") or {}).get("template") or {}).get("spec")
    return None


def kubernetes_checks(repo: Repo, scope: str, files: list[str]) -> list[dict]:
    manifests = [
        f
        for f in files
        if f.endswith((".yaml", ".yml")) and not f.endswith(("Chart.yaml", "Chart.yml", "kustomization.yaml", "kustomization.yml"))
    ]
    containers, secrets = [], []
    for f in manifests:
        text = repo.text(f)
        for doc in _documents(text):
            if doc["kind"] == "Secret" and (doc.get("data") or doc.get("stringData")):
                secrets.append(
                    ev(
                        f,
                        "Secret " + str((doc.get("metadata") or {}).get("name", "")) + " has literal data",
                        line_of(text, r"kind:\s*Secret")[0],
                    )
                )
            pod = _pod_spec(doc)
            if pod:
                for c in (pod.get("containers") or []) + (pod.get("initContainers") or []):
                    if isinstance(c, dict):
                        containers.append((f, text, pod, c))
    out = []
    if containers:
        unpinned = [
            ev(f, f"{c.get('name')}: {c.get('image')}", line_of(t, re.escape(str(c.get("image"))))[0])
            for f, t, _, c in containers
            if isinstance(c.get("image"), str)
            and "$" not in c["image"]
            and "{{" not in c["image"]
            and "@sha256:" not in c["image"]
            and (":" not in c["image"].rsplit("/", 1)[-1] or c["image"].endswith(":latest"))
        ]
        out.append(finding("INF-K01", scope, "fail" if unpinned else "pass", unpinned or [ev(containers[0][0], "all images pinned")]))
        nolimit = [
            ev(f, f"container {c.get('name')} has no resource limits", line_of(t, rf"name:\s*{re.escape(str(c.get('name')))}")[0])
            for f, t, _, c in containers
            if not (c.get("resources") or {}).get("limits")
        ]
        out.append(finding("INF-K02", scope, "fail" if nolimit else "pass", nolimit or [ev(containers[0][0], "limits set")]))
        root = [
            ev(f, f"container {c.get('name')} may run as root", line_of(t, rf"name:\s*{re.escape(str(c.get('name')))}")[0])
            for f, t, pod, c in containers
            if not (
                (c.get("securityContext") or {}).get("runAsNonRoot")
                or (pod.get("securityContext") or {}).get("runAsNonRoot")
                or (c.get("securityContext") or {}).get("runAsUser")
            )
        ]
        out.append(finding("INF-K03", scope, "fail" if root else "pass", root or [ev(containers[0][0], "runAsNonRoot set")]))
        noprobe = [
            ev(f, f"container {c.get('name')} has no readiness/liveness probe", line_of(t, rf"name:\s*{re.escape(str(c.get('name')))}")[0])
            for f, t, _, c in containers
            if not (c.get("readinessProbe") or c.get("livenessProbe") or c.get("startupProbe"))
        ]
        out.append(finding("INF-K04", scope, "fail" if noprobe else "pass", noprobe or [ev(containers[0][0], "probes set")]))
    validated = repo.has(
        r"kubeconform|kubeval|kubectl\s+.*--dry-run|helm\s+(lint|template)|kustomize\s+build|conftest|kube-linter|kubescape"
    )
    out.append(
        finding(
            "INF-K05",
            scope,
            "pass" if validated else "fail",
            [ev("CI/hooks", "manifest validation")] if validated else [ev(files[0], "no validation step")],
        )
    )
    out.append(finding("INF-K06", scope, "fail" if secrets else "pass", secrets or [ev(files[0], "no Secret with literal data")]))
    charts = [f for f in files if f.endswith(("Chart.yaml", "Chart.yml"))]
    for chart in charts:
        d = str(PurePosixPath(chart).parent)
        has_schema = (f"{d}/values.schema.json" if d != "." else "values.schema.json") in repo.fileset
        out.append(
            finding(
                "INF-K07",
                d,
                "pass" if has_schema else "fail",
                [ev(chart, "values.schema.json present" if has_schema else "no values.schema.json")],
            )
        )
    return out


# ---- entry point ---------------------------------------------------------------------------------


def run(root: Path, files: list[str], detected: list[dict]) -> dict:
    repo = Repo(root, files)
    findings: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for d in detected:
        if d["sample"]:
            continue
        if d["tool"] == "docker":
            findings += [x for p in d["files"] if PurePosixPath(p).name.lower() != ".dockerignore" for x in docker_checks(repo, p)]
        elif d["tool"] == "compose":
            findings += [x for p in d["files"] for x in compose_checks(repo, p)]
        elif d["tool"] == "devcontainer":
            findings += [x for p in d["files"] for x in devcontainer_checks(repo, p)]
        elif d["tool"] == "bicep":
            findings += bicep_checks(repo, d["scope"], d["files"])
        elif d["tool"] in ("kubernetes", "helm", "kustomize"):
            key = ("k8s", d["scope"])
            if key not in seen:
                seen.add(key)
                findings += kubernetes_checks(
                    repo,
                    d["scope"],
                    [
                        f
                        for x in detected
                        if x["scope"] == d["scope"] and x["tool"] in ("kubernetes", "helm", "kustomize")
                        for f in x["files"]
                    ],
                )
        elif d["tool"] in ("terraform", "opentofu"):
            findings += terraform_checks(repo, d["scope"], d["files"])
    summary: dict[str, dict] = {}
    for f in findings:
        s = summary.setdefault(f["area"], {"passed": 0, "failed": 0, "not_applicable": 0})
        s[{"pass": "passed", "fail": "failed"}.get(f["status"], "not_applicable")] += 1
    for s in summary.values():
        total = s["passed"] + s["failed"]
        s["pass_rate"] = round(s["passed"] / total, 2) if total else None
    rows = rollup(findings)
    return {"findings": findings, "summary": summary, "rollup": rows, "levels": levels(rows)}


def rollup(findings: list[dict]) -> list[dict]:
    """One row per check: how many locations pass, fail or do not apply, and the failing paths (B-194)."""
    rows: dict[str, dict] = {}
    for f in findings:
        row = rows.setdefault(
            f["check_id"],
            {
                "check_id": f["check_id"],
                "area": f["area"],
                "level": f["level"],
                "title": f["title"],
                "passed": 0,
                "failed": 0,
                "not_applicable": 0,
                "failing": [],
            },
        )
        key = {"pass": "passed", "fail": "failed"}.get(f["status"], "not_applicable")
        row[key] += 1
        if f["status"] == "fail" and len(row["failing"]) < 5:
            row["failing"].append(f["scope"])
    return sorted(rows.values(), key=lambda r: (-r["failed"], r["check_id"]))


def levels(rows: list[dict]) -> dict:
    """Overlay level per area (L0-L3) and overall (weakest area). Same rule as the pillars (B-198).

    A check passes in an area only when it fails nowhere and passes somewhere; one failing location fails
    the check. Level N needs every gate check up to N to pass and 60% of the applicable checks at each level up to N.
    """
    areas: dict[str, dict] = {}
    for area in sorted({r["area"] for r in rows}):
        mine = [r for r in rows if r["area"] == area and r["passed"] + r["failed"] > 0]
        reached, blocked, ratios = 0, [], {}
        for lvl in (1, 2, 3):
            at = [r for r in mine if r["level"] == lvl]
            passed = [r for r in at if r["failed"] == 0]
            ratios[str(lvl)] = round(len(passed) / len(at), 2) if at else None
            gates = [r["check_id"] for r in mine if r["level"] <= lvl and r["check_id"] in GATES and r["failed"] > 0]
            if gates or (at and len(passed) / len(at) < PASS_RATIO):
                blocked = gates or [r["check_id"] for r in at if r["failed"]][:3]
                break
            reached = lvl
        areas[area] = {"level": reached, "blocked_by": blocked, "pass_ratio_by_level": ratios}
    if not areas:
        return {"overall": None, "weakest_area": None, "areas": {}}
    weakest = min(areas, key=lambda a: (areas[a]["level"], a))
    return {"overall": areas[weakest]["level"], "weakest_area": weakest, "areas": areas}
