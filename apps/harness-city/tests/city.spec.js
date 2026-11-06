import { test, expect, openCity, countObjects, convertedCoverageCity } from "./fixtures.js";

test("default city has selectable physical landmarks without coverage or simulation", async ({ page }, testInfo) => {
  await openCity(page, false);
  const score = await page.locator("#cityplate .m").textContent();
  const landmarks = ["airport", "factory", "mall", "bank", "archive", "highway", "mountains", "tunnel", "bridge"];
  for (const name of landmarks) expect(await countObjects(page, `landmark-${name}`), name).toBe(1);
  await expect(page.locator("#airbar")).toHaveCount(0);
  const inventory = page.getByRole("region", { name: "City landmarks" });
  await expect(inventory.getByRole("button")).toHaveCount(landmarks.length);
  for (const name of landmarks) {
    const button = inventory.locator(`[data-kind="LAND:${name}"]`);
    await button.focus();
    await page.keyboard.press("Enter");
    await expect(page.locator("#panel")).toContainText("not audit evidence");
    await expect(page.locator("#cityplate .m")).toHaveText(score);
    await page.locator("#stage canvas").scrollIntoViewIfNeeded();
    const point = await page.evaluate(id => {
      const { city, camera, canvas } = window.__city;
      const position = city.getObjectByName(`landmark-${id}`).position.clone();
      position.y = id === "tunnel" ? 5.1 : id === "bridge" ? 1.6 : 0.4;
      position.project(camera);
      const rectangle = canvas.getBoundingClientRect();
      return { x: rectangle.left + (position.x + 1) * rectangle.width / 2, y: rectangle.top + (1 - position.y) * rectangle.height / 2 };
    }, name);
    await page.mouse.click(point.x, point.y);
    await expect(button).toHaveAttribute("aria-pressed", "true");
  }
  await page.locator("#fit").click();
  await page.locator("#lbl").click();
  for (let rotation = 0; rotation < 4; rotation++) {
    expect(await page.evaluate(names => {
      const { city, camera } = window.__city;
      return names.every(name => {
        const object = city.getObjectByName(`landmark-${name}`);
        const point = object.position.clone().project(camera);
        return Math.abs(point.x) < 1 && Math.abs(point.y) < 1 && Math.abs(point.z) < 1;
      });
    }, landmarks)).toBe(true);
    await page.locator("#stage").screenshot({ path: testInfo.outputPath(`landmarks-rotation-${rotation}.png`) });
    await page.locator("#rotR").click();
    await page.waitForFunction(angle => Math.abs(window.__city.view.az - angle) < 0.01, 45 + (rotation + 1) * 90);
  }
  const colorCount = await page.evaluate(() => {
    const { renderer, scene, camera, canvas } = window.__city;
    renderer.render(scene, camera);
    const image = document.createElement("canvas");
    image.width = canvas.width; image.height = canvas.height;
    const context = image.getContext("2d");
    context.drawImage(canvas, 0, 0);
    const pixels = context.getImageData(0, 0, image.width, image.height).data;
    const colors = new Set();
    for (let index = 0; index < pixels.length; index += 388) colors.add(pixels.slice(index, index + 4).join(","));
    return colors.size;
  });
  expect(colorCount).toBeGreaterThan(20);
});

async function clickCoverageAnchor(page, anchor) {
  const point = await page.evaluate(anchorId => {
    const marker = window.__city.city.getObjectByName(`coverage-anchor-${anchorId}`);
    if (!marker) return null;
    const position = marker.position.clone();
    position.x += 0.7;
    position.project(window.__city.camera);
    const rectangle = window.__city.canvas.getBoundingClientRect();
    return { x: rectangle.left + (position.x + 1) * rectangle.width / 2, y: rectangle.top + (1 - position.y) * rectangle.height / 2 };
  }, anchor);
  expect(point).not.toBeNull();
  await page.mouse.click(point.x, point.y);
}

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

test("coverage inventory exposes topic states and provenance through keyboard selection", async ({ page }) => {
  const cityData = await convertedCoverageCity();
  await openCity(page, true, cityData);

  const inventory = page.getByRole("region", { name: "Coverage topics" });
  await expect(inventory.getByRole("button")).toHaveCount(7);

  const security = inventory.getByRole("button", { name: /security/i });
  await security.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#panel")).toContainText("security");
  await expect(page.locator("#panel")).toContainText("applicable");
  await expect(page.locator("#panel")).toContainText("static implementation found");
  await expect(page.locator("#panel")).toContainText("current");
  await expect(page.locator("#panel")).toContainText("Dockerfile");
  await expect(page.locator("#panel")).toContainText("dockerfile_env");
  await page.locator("#panel").getByRole("button", { name: "airport", exact: true }).click();
  await expect(page.locator("#panel")).toContainText("Coverage anchor");
  await expect(page.locator("#panel")).toContainText("security");
  const airportFocus = await page.evaluate(() => window.__city.view.target.toArray());
  expect(airportFocus[0]).toBe(53);
  expect(airportFocus[2]).toBe(4.5);

  const dependencies = inventory.locator("li").filter({ hasText: "dependencies" });
  const mcp = inventory.locator("li").filter({ hasText: "mcp" });
  await expect(dependencies).toContainText("inapplicable");
  await expect(mcp).toContainText("unsupported");
});

test("coverage anchors use the resolved airport, rail and reservation layout", async ({ page }) => {
  await openCity(page);
  const layout = await page.evaluate(() => window.__city.layoutNow());
  const railEnd = await page.evaluate(() => {
    const rail = window.__city.city.children.find(object => object.userData.pick?.kind === "rail");
    const bed = rail.children[0];
    return bed.position.x + bed.geometry.parameters.width / 2;
  });

  expect(layout.airport.dx).toBe(-2);
  expect(railEnd).toBeCloseTo(43.5, 1);
  expect(layout.meadow.keepOut).toEqual(expect.arrayContaining([
    [49.5, 58.5, 10.5, 17.5],
    [47.5, 62.5, -18.5, -7.5],
    [61.5, 70.5, -30, 40]
  ]));
});

test("factory and highway anchors are real pointer targets with shared topic details", async ({ page }) => {
  await openCity(page, true, await convertedCoverageCity());
  const inventory = page.getByRole("region", { name: "Coverage topics" });
  const dependencies = inventory.getByRole("button", { name: "dependencies" });
  await dependencies.focus();
  await page.keyboard.press("Enter");
  await page.locator("#panel").getByRole("button", { name: "factory", exact: true }).click();
  await clickCoverageAnchor(page, "factory");
  await expect(page.locator("#panel")).toContainText("Coverage anchor");
  await expect(page.locator("#panel")).toContainText("dependencies");

  await inventory.getByRole("button", { name: "ci_build" }).click();
  await page.locator("#panel").getByRole("button", { name: "highway", exact: true }).click();
  await clickCoverageAnchor(page, "highway");
  await expect(page.locator("#panel")).toContainText("Coverage anchor");
  await expect(page.locator("#panel")).toContainText("ci_build");
  await expect(page.locator("#panel")).toContainText("2 configured runner relationships");
  await expect(page.locator("#panel")).toContainText("1 resolved");
  await expect(page.locator("#panel")).toContainText("1 unresolved");
  await expect(page.locator("#panel")).not.toContainText("RAW_COMMAND_SENTINEL");
});

test("factory and highway markers appear only for projected anchor topics", async ({ page }) => {
  const cityData = await convertedCoverageCity();
  cityData.cities[0].coverage.observations = cityData.cities[0].coverage.observations
    .filter(observation => observation.topic_id === "security");
  await openCity(page, true, cityData);

  expect(await countObjects(page, "coverage-anchor-factory")).toBe(0);
  expect(await countObjects(page, "coverage-anchor-highway")).toBe(0);
  await expect(page.getByRole("region", { name: "Coverage topics" })).toContainText("security");
});

test("coverage labels declutter across rotations at desktop and mobile viewports", async ({ page }, testInfo) => {
  const viewport = testInfo.project.name === "mobile-chromium"
    ? { width: 390, height: 844 }
    : { width: 1440, height: 1000 };
  await page.setViewportSize(viewport);
  await openCity(page, true, await convertedCoverageCity());
  expect(await page.evaluate(() => ({ width: innerWidth, height: innerHeight }))).toEqual(viewport);

  const security = page.getByRole("region", { name: "Coverage topics" }).getByRole("button", { name: /security/i });
  await security.focus();
  await page.keyboard.press("Enter");
  const focus = await page.evaluate(() => ({ target: window.__city.view.target.toArray(), zoom: window.__city.view.zoom }));
  expect(focus.target[0]).toBe(53);
  expect(focus.zoom).toBeGreaterThan(1);
  await page.locator("#fit").click();

  for (let rotation = 0; rotation < 4; rotation++) {
    await page.evaluate(() => new Promise(requestAnimationFrame));
    const overlaps = await page.evaluate(() => {
      const visible = [...document.querySelectorAll("#labels > *")]
        .filter(element => getComputedStyle(element).display !== "none")
        .map(element => ({ name: element.textContent.trim(), rect: element.getBoundingClientRect() }));
      const collisions = [];
      for (let left = 0; left < visible.length; left++) {
        for (let right = left + 1; right < visible.length; right++) {
          const a = visible[left].rect, b = visible[right].rect;
          if (a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top) {
            collisions.push([visible[left].name, visible[right].name]);
          }
        }
      }
      return collisions;
    });
    expect(overlaps, `overlapping labels at rotation ${rotation}`).toEqual([]);
    await page.locator("#stage").screenshot({ path: testInfo.outputPath(`coverage-${testInfo.project.name}-${rotation}.png`) });
    const pixelColors = await page.evaluate(() => {
      const { renderer, scene, camera, canvas } = window.__city;
      renderer.render(scene, camera);
      const image = document.createElement("canvas");
      image.width = canvas.width; image.height = canvas.height;
      const context = image.getContext("2d");
      context.drawImage(canvas, 0, 0);
      const pixels = context.getImageData(0, 0, image.width, image.height).data;
      const colors = new Set();
      for (let index = 0; index < pixels.length; index += 388) colors.add(pixels.slice(index, index + 4).join(","));
      return colors.size;
    });
    expect(pixelColors).toBeGreaterThan(20);
    await page.locator("#rotR").click();
    await page.waitForFunction(angle => Math.abs(window.__city.view.az - angle) < 0.01, 45 + (rotation + 1) * 90);
  }
});
