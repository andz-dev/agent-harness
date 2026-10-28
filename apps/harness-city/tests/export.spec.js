import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { test, expect, openCity } from "./fixtures.js";

async function downloadPNG(page) {
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export PNG", exact: true }).click();
  const download = await pending;
  expect(await download.failure()).toBeNull();
  const bytes = await fs.readFile(await download.path());
  expect([...bytes.subarray(0, 8)]).toEqual([137, 80, 78, 71, 13, 10, 26, 10]);
  const decoded = await page.evaluate(async encoded => {
    const blob = await (await fetch("data:image/png;base64," + encoded)).blob();
    const bitmap = await createImageBitmap(blob), canvas = document.createElement("canvas");
    canvas.width = bitmap.width; canvas.height = bitmap.height;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    context.drawImage(bitmap, 0, 0); bitmap.close();
    const pixels = context.getImageData(32, 32, Math.floor(canvas.width * .4), Math.min(canvas.height - 64, 1200)).data;
    const colors = new Set();
    for (let index = 0; index < pixels.length; index += 388) colors.add(pixels.slice(index, index + 4).join(","));
    return { width: canvas.width, height: canvas.height, mapColors: colors.size };
  }, bytes.toString("base64"));
  expect(decoded.width).toBeGreaterThan(800);
  expect(decoded.height).toBeGreaterThan(500);
  expect(decoded.mapColors).toBeGreaterThan(20);
  await expect(page.locator("#exportStatus")).toHaveText("PNG exported.");
  return download.suggestedFilename();
}

test("PNG download includes descriptions without changing the live camera", async ({ page }) => {
  await openCity(page);
  await page.evaluate(() => {
    window.__t.select(null, "AIR:gate:agent");
    window.__exportWords = [];
    const original = CanvasRenderingContext2D.prototype.fillText;
    CanvasRenderingContext2D.prototype.fillText = function(text, ...args) {
      window.__exportWords.push(String(text));
      return original.call(this, text, ...args);
    };
  });
  await page.getByRole("button", { name: "Underground", exact: true }).click();
  const camera = await page.evaluate(() => ({ target: window.__t.view.target.toArray(), zoom: window.__t.view.zoom }));
  expect(await downloadPNG(page)).toMatch(/thriving-demo-underground\.png$/);
  const result = await page.evaluate(() => ({
    camera: { target: window.__t.view.target.toArray(), zoom: window.__t.view.zoom },
    words: window.__exportWords.join(" ")
  }));
  expect(result.camera).toEqual(camera);
  for (const text of ["Score 100", "District legend", "Infrastructure", "benefit", "Agent guidance office"]) expect(result.words).toContain(text);
});

test("PNG encoding failure restores the control and reports the failure", async ({ page }) => {
  await openCity(page);
  await page.evaluate(() => { HTMLCanvasElement.prototype.toBlob = callback => callback(null); });
  await page.getByRole("button", { name: "Export PNG", exact: true }).click();
  await expect(page.locator("#exportStatus")).toContainText("PNG export failed: PNG encoding failed.");
  await expect(page.getByRole("button", { name: "Export PNG", exact: true })).toBeEnabled();
});

test("offline standalone renders and exports with all network requests blocked", async ({ page }) => {
  const attempted = [];
  await page.route(/^https?:\/\//, route => {
    attempted.push(route.request().url());
    return route.abort();
  });
  const offline = pathToFileURL(path.resolve("dist/airport-test.html")).href;
  await page.goto(offline);
  await page.waitForFunction(() => window.__ready && window.__thumbs);
  await page.getByRole("button", { name: "Underground", exact: true }).click();
  await expect(page.locator("#stage")).toHaveClass(/under/);
  await downloadPNG(page);
  expect(attempted).toEqual([]);
});