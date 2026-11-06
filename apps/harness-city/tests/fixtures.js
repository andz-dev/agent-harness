import { execFileSync } from "node:child_process";
import { test as base, expect } from "@playwright/test";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");

export const test = base.extend({
  observedErrors: [async ({ page }, use) => {
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
    await page.route("https://fonts.googleapis.com/**", route => route.fulfill({ contentType: "text/css", body: "" }));
    await use(errors);
    expect(errors, "The city must not emit page or console errors").toEqual([]);
  }, { auto: true }]
});

export { expect };

export async function openCity(page, airport = true, cityData = null) {
  if (cityData) await page.addInitScript(data => { window.HARNESS_CITY_DATA = data; }, cityData);
  await page.goto(airport ? "/?airport" : "/");
  await page.waitForFunction(() => window.__ready && window.__thumbs);
}

export async function convertedCoverageCity() {
  const reportPath = path.join(repoRoot, "skills/harness-audit/schema/example-report.json");
  const converterPath = path.join(repoRoot, "apps/harness-city/tools/report_to_city.py");
  const report = JSON.parse(await fs.readFile(reportPath, "utf8"));
  const topicStates = [
    ["code_standards", "applicable", "declared", "current", ["STA-01"]],
    ["testing", "applicable", "static_implementation_found", "stale", ["VER-01"]],
    ["ci_build", "applicable", "static_implementation_found", "current", ["CIP-01"]],
    ["security", "applicable", "static_implementation_found", "current", ["INF-D06"]],
    ["dependencies", "inapplicable", "unknown", "unknown", ["VER-08"]],
    ["mcp", "unsupported", "unknown", "unknown", ["ORI-02"]],
    ["skills_extensions", "applicable", "unknown", "unknown", ["ORI-10"]]
  ];
  report.meta = { synthetic: true };
  report.quality = { availability: "available", score: report.score.final, reason_codes: [] };
  report.coverage = {
    version: 1,
    components: [{ id: "api", root: ".", languages: ["python"], adapter: "python", applicability: "applicable" }],
    observations: topicStates.map(([topicId, applicability, evidence, freshness, checkIds]) => ({
      id: `api:${topicId}`,
      component_id: "api",
      topic_id: topicId,
      check_ids: checkIds,
      applicability,
      evidence,
      freshness,
      provenance: {
        revision: "0123abc",
        sources: [{ path: "Dockerfile", sha256: "a".repeat(64), locator: "dockerfile_env" }],
        method: "tracked_path_match",
        observed_at: "2026-11-05T00:00:00Z"
      },
      receipt: { outcome: "absent" },
      limitations: ["Synthetic city coverage fixture."]
    })),
    runner_edges: [
      { from: "RAW_COMMAND_SENTINEL", to: "check", resolution: "resolved" },
      { from: "check", to: null, resolution: "unresolved" }
    ],
    collection: {
      outcome: "complete",
      limits: { max_file_bytes: 1, max_total_bytes: 1, max_candidate_paths: 1, max_runner_depth: 1 },
      reason_codes: []
    },
    limitations: []
  };

  const temporaryDirectory = await fs.mkdtemp(path.join(os.tmpdir(), "harness-city-coverage-"));
  const inputPath = path.join(temporaryDirectory, "report.json");
  const outputPath = path.join(temporaryDirectory, "cities.json");
  try {
    await fs.writeFile(inputPath, JSON.stringify(report));
    execFileSync("python3", [converterPath, inputPath, "--out", outputPath], { cwd: repoRoot });
    return JSON.parse(await fs.readFile(outputPath, "utf8"));
  } finally {
    await fs.rm(temporaryDirectory, { recursive: true, force: true });
  }
}

export function areaControl(page, label, value) {
  return page.locator("#airbar .ag").filter({ has: page.getByText(label, { exact: true }) })
    .getByRole("button", { name: String(value), exact: true });
}

export async function countObjects(page, name) {
  return page.evaluate(name => {
    let count = 0;
    window.__t.scene.traverse(object => { if (object.name === name) count++; });
    return count;
  }, name);
}
