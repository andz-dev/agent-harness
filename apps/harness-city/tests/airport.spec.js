import { test, expect, openCity, areaControl, countObjects } from "./fixtures.js";

test("full airport regression preserves levels, materials, GPU state and PNG output", async ({ page }) => {
  await openCity(page);
  const result = await page.evaluate(async () => {
    const { checkCity } = await import("/tools/check_city.js");
    return checkCity();
  });
  expect(result.passed.length).toBeGreaterThanOrEqual(6);
  expect(new Set(result.allocations).size).toBe(1);
});

test("real support-control clicks cannot downgrade core infrastructure", async ({ page }, testInfo) => {
  await openCity(page);
  await page.getByRole("button", { name: "Everything L3", exact: true }).click();
  await areaControl(page, "Compose", 2).click();
  for (const value of ["–", "0", "1", "2", "3"]) {
    await areaControl(page, "Devcontainer", value).click();
    await expect(page.locator("#airportLevel")).toHaveText("Airport L2 · limited by Compose L2");
    expect(await countObjects(page, "airport-terminal")).toBe(1);
    expect(await countObjects(page, "airport-support-devcontainer")).toBe(value === "–" ? 0 : 1);
  }
  await areaControl(page, "Agent guidance · repo-wide", 0).click();
  await areaControl(page, "Cross-cutting · repo-wide", 0).click();
  await expect(page.locator("#airportLevel")).toHaveText("Airport L2 · limited by Compose L2");
  expect(await countObjects(page, "airport-support-agent")).toBe(1);
  await page.evaluate(() => window.__t.select(null, "AIR:gate:devcontainer"));
  await expect(page.locator("#panel")).toContainText("Optional benefit");
  await page.locator("#stage").screenshot({ path: testInfo.outputPath("support-facility.png") });
});

test("support-only configurations do not invent a main airport or service", async ({ page }) => {
  await openCity(page);
  await page.getByRole("button", { name: "No infrastructure", exact: true }).click();
  await areaControl(page, "Devcontainer", 3).click();
  await areaControl(page, "Agent guidance · repo-wide", 2).click();
  await expect(page.locator("#airportLevel")).toContainText("No main airport");
  expect(await countObjects(page, "airport-support-devcontainer")).toBe(1);
  expect(await countObjects(page, "airport-support-agent")).toBe(1);
  expect(await countObjects(page, "airport-terminal")).toBe(0);
  expect(await countObjects(page, "airport-hangar")).toBe(0);
  const service = await page.evaluate(() => {
    const found = [];
    window.__t.scene.traverse(object => {
      if (["bus", "metro-train"].includes(object.name) && object.userData.pick?.kind === "AIR:link") found.push(object.name);
    });
    return found;
  });
  expect(service).toEqual([]);
});