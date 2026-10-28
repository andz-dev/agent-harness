import { test, expect, openCity, countObjects } from "./fixtures.js";

test("each synthetic city keeps its station and a contained layout", async ({ page }, testInfo) => {
  await openCity(page);
  for (const [id, station] of [["thriving-demo", 3], ["prosperous-demo", 2], ["working-demo", 2], ["absent-demo", 0]]) {
    await page.locator(`#picker [data-id="${id}"]`).click();
    await expect(page.locator("#cityplate .t")).toHaveText(id);
    expect(await countObjects(page, `central-station-L${station}`)).toBe(1);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.locator("#stage").screenshot({ path: testInfo.outputPath(`${id}.png`) });
  }
});

test("underground is permanent even without an airport", async ({ page }) => {
  await openCity(page, false);
  await page.getByRole("button", { name: "Underground", exact: true }).click();
  await expect(page.locator("#stage")).toHaveClass(/under/);
  await page.locator('#picker [data-id="working-demo"]').click();
  await expect(page.locator("#stage")).toHaveClass(/under/);
  await expect(page.getByRole("button", { name: "Underground", exact: true })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Surface", exact: true }).click();
  await expect(page.locator("#stage")).not.toHaveClass(/under/);
});

test("labels can be hidden and restored through the toolbar", async ({ page }) => {
  await openCity(page);
  const labels = page.getByRole("button", { name: "Show or hide labels", exact: true });
  await labels.click();
  await expect(page.locator("#stage")).toHaveClass(/hide-labels/);
  await labels.click();
  await expect(page.locator("#stage")).not.toHaveClass(/hide-labels/);
});