import fs from "node:fs/promises";
import { test, expect } from "./fixtures.js";

// The editor is a desktop tool; its behaviour is tested at desktop size only.
test.skip(({ isMobile }) => isMobile, "editor is desktop-first");

async function openEditor(page, preset = "current") {
  await page.goto(`/editor.html?fresh&preset=${preset}`);
  await page.waitForFunction(() => window.__editor && window.__editor.host && window.__editor.map);
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
const viewer = (page, expr) => page.evaluate((e) => new Function("c", "return " + e)(window.__editor.host), expr);

test("the editor draws the city with the viewer's own renderer and camera", async ({ page }) => {
  await openEditor(page, "current");
  expect(await viewer(page, "c.camera.isOrthographicCamera")).toBe(true);
  expect(await viewer(page, "c.scene.getObjectByName('central-station-L3') !== undefined")).toBe(true);
  expect(await viewer(page, "Object.keys(c.assets).length")).toBeGreaterThan(50);
  expect(await count(page, "m.zones.filter(z => z.kind === 'district').length")).toBe(7);
});

test("moving a district and adding road tiles change the viewer's layout", async ({ page }) => {
  await openEditor(page, "current");
  await page.getByRole("button", { name: /Select/ }).click();
  await dragAt(page, [14.5, 4], [16.5, 4]);
  expect(await count(page, "m.zones.find(z => z.id === 'verification').x0")).toBe(12);
  expect(await viewer(page, "c.DIST.verification.x0")).toBe(12);

  await page.getByRole("button", { name: /Streets/ }).click();
  const tiles = await count(page, "m.layout.roads.length");
  await dragAt(page, [36, 13], [41, 13]);
  expect(await count(page, "m.layout.roads.length")).toBe(tiles + 6);
  expect(await viewer(page, "c.ROADS.has('41,13')")).toBe(true);
});

test("terraform, trees, free streets and paths edit the map and undo restores it", async ({ page }) => {
  await openEditor(page, "current");
  const before = await page.evaluate(() => window.__editor.serialize());

  await page.getByRole("button", { name: /Terraform/ }).click();
  await dragAt(page, [-11, 22], [-10, 23]);
  expect(await count(page, "Math.max(...m.terrain.heights)")).toBeGreaterThan(0.05);

  await page.getByRole("button", { name: /Streets/ }).click();
  await page.locator("#o-rmode").selectOption("free");
  await clickAt(page, 40, 20); await clickAt(page, 46, 21); await clickAt(page, 50, 24);
  await page.keyboard.press("Enter");
  expect(await count(page, "m.roads.edges.length")).toBe(2);

  await page.getByRole("button", { name: /Trees/ }).click();
  const props = await count(page, "m.props.length");
  await dragAt(page, [-12, 12], [-9, 13]);
  expect(await count(page, "m.props.length")).toBeGreaterThan(props);

  await page.getByRole("button", { name: /Vehicle paths/ }).click();
  await page.locator("#o-veh").selectOption("plane");
  const paths = await count(page, "m.paths.length");
  await clickAt(page, 50, 12); await clickAt(page, 56, 16); await clickAt(page, 62, 12);
  await page.keyboard.press("Enter");
  expect(await count(page, "m.paths.length")).toBe(paths + 1);

  await page.evaluate(async () => { while (window.__editor.state.undo.length) await window.__editor.undo(); });
  expect(await page.evaluate(() => window.__editor.serialize())).toBe(before);
});

test("map JSON round trip is lossless and GLB and PNG export produce files", async ({ page }) => {
  await openEditor(page, "l3");
  const text = await page.evaluate(() => window.__editor.serialize());
  await page.evaluate((t) => window.__editor.load(t), text);
  expect(await page.evaluate(() => window.__editor.serialize())).toBe(text);
  const map = JSON.parse(text);
  expect(map.schema).toBe(2);
  expect(map.layout.airport.dx).toBe(-2);
  expect(map.resolved.v1.length).toBeGreaterThan(10);

  for (const [name, magic] of [["Map JSON", null], ["GLB", "glTF"], ["PNG", "\x89PNG"]]) {
    const pending = page.waitForEvent("download", { timeout: 60000 });
    await page.getByRole("button", { name, exact: true }).click();
    const file = await fs.readFile(await (await pending).path());
    expect(file.length).toBeGreaterThan(1000);
    if (magic) expect(file.subarray(0, 4).toString("latin1")).toBe(magic);
    else expect(JSON.parse(file.toString()).schema).toBe(2);
  }
});

test("all four rotations and the plan view keep the orthographic camera", async ({ page }) => {
  await openEditor(page, "l3");
  for (let i = 0; i < 4; i++) {
    await page.getByRole("button", { name: "Rotate right" }).click();
    await page.waitForTimeout(150);
  }
  await expect.poll(() => viewer(page, "c.view.az % 360"), { timeout: 10000 }).toBe(45);
  await page.getByRole("button", { name: /Plan/ }).click();
  expect(await page.evaluate(() => window.__editor.view.plan)).toBe(true);
  expect(await viewer(page, "c.camera.isOrthographicCamera")).toBe(true);
});
