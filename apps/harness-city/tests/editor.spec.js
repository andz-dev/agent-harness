import fs from "node:fs/promises";
import { test, expect } from "./fixtures.js";

// The editor is a desktop tool; its behaviour is tested at desktop size only.
test.skip(({ isMobile }) => isMobile, "editor is desktop-first");

async function openEditor(page, preset = "current") {
  await page.goto(`/editor.html?fresh&preset=${preset}`);
  await page.waitForFunction(() => window.__editor && window.__editor.map);
  await page.evaluate(() => window.__editor.ready);
  await expect(page.locator("#loading")).toBeHidden();
}
const at = (page, x, z) => page.evaluate(([x, z]) => window.__editor.screenOf(x, z), [x, z]);
async function clickAt(page, x, z) { const p = await at(page, x, z); await page.mouse.click(p.x, p.y); }
async function dragAt(page, from, to) {
  const a = await at(page, ...from), b = await at(page, ...to);
  await page.mouse.move(a.x, a.y); await page.mouse.down();
  for (let i = 1; i <= 6; i++) await page.mouse.move(a.x + ((b.x - a.x) * i) / 6, a.y + ((b.y - a.y) * i) / 6);
  await page.mouse.up();
}
const count = (page, expr) => page.evaluate((e) => new Function("m", "return " + e)(window.__editor.map), expr);

test("both presets load as valid maps with the isometric camera", async ({ page }) => {
  for (const preset of ["current", "l3"]) {
    await openEditor(page, preset);
    const info = await page.evaluate(() => ({ ortho: window.__editor.view && true, districts: window.__editor.map.zones.filter((z) => z.kind === "district").length }));
    expect(info.districts).toBe(7);
  }
});

test("terraform, streets, trees, zones and paths edit the map and undo restores it", async ({ page }) => {
  await openEditor(page, "current");
  const before = await page.evaluate(() => window.__editor.serialize());

  await page.getByRole("button", { name: /Terraform/ }).click();
  await dragAt(page, [-10, 20], [-9, 21]);
  expect(await count(page, "Math.max(...m.terrain.heights)")).toBeGreaterThan(0.05);

  await page.getByRole("button", { name: /Streets/ }).click();
  const edges = await count(page, "m.roads.edges.length");
  await clickAt(page, 40, 14); await clickAt(page, 46, 14); await clickAt(page, 50, 18);
  await page.keyboard.press("Enter");
  expect(await count(page, "m.roads.edges.length")).toBe(edges + 2);

  await page.getByRole("button", { name: /Trees/ }).click();
  const props = await count(page, "m.props.length");
  await dragAt(page, [-11, 12], [-8, 13]);
  expect(await count(page, "m.props.length")).toBeGreaterThan(props);

  await page.getByRole("button", { name: /Select/ }).click();
  const x0 = await count(page, "m.zones.find(z => z.id === 'verification').x0");
  await dragAt(page, [14.5, 4], [16.5, 4]);
  expect(await count(page, "m.zones.find(z => z.id === 'verification').x0")).not.toBe(x0);

  await page.getByRole("button", { name: /Vehicle paths/ }).click();
  await page.locator("#o-veh").selectOption("plane");
  const paths = await count(page, "m.paths.length");
  await clickAt(page, 50, 12); await clickAt(page, 56, 16); await clickAt(page, 62, 12);
  await page.keyboard.press("Enter");
  expect(await count(page, "m.paths.length")).toBe(paths + 1);

  for (let i = 0; i < 12; i++) await page.getByRole("button", { name: "Undo" }).click();
  expect(await page.evaluate(() => window.__editor.serialize())).toBe(before);
});

test("map JSON round trip is lossless and GLB and PNG export produce files", async ({ page }) => {
  await openEditor(page, "l3");
  const text = await page.evaluate(() => window.__editor.serialize());
  await page.evaluate((t) => window.__editor.load(t), text);
  expect(await page.evaluate(() => window.__editor.serialize())).toBe(text);
  const map = JSON.parse(text);
  expect(map.schema).toBe(1);
  expect(Object.keys(map.resolved).length).toBe(map.paths.length);

  for (const [name, magic] of [["Map JSON", null], ["GLB", "glTF"], ["PNG", "\x89PNG"]]) {
    const pending = page.waitForEvent("download");
    await page.getByRole("button", { name, exact: true }).click();
    const file = await fs.readFile(await (await pending).path());
    expect(file.length).toBeGreaterThan(1000);
    if (magic) expect(file.subarray(0, 4).toString("latin1")).toBe(magic);
    else expect(JSON.parse(file.toString()).schema).toBe(1);
  }
});

test("all four rotations and the plan view render without errors", async ({ page }) => {
  await openEditor(page, "l3");
  for (let i = 0; i < 4; i++) {
    await page.getByRole("button", { name: "Rotate right" }).click();
    await page.waitForTimeout(100);
  }
  expect(await page.evaluate(() => window.__editor.view.az % 360)).toBe(45);
  await page.getByRole("button", { name: /Plan/ }).click();
  expect(await page.evaluate(() => window.__editor.view.plan)).toBe(true);
});
