import { test as base, expect } from "@playwright/test";

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

export async function openCity(page, airport = true) {
  await page.goto(airport ? "/?airport" : "/");
  await page.waitForFunction(() => window.__ready && window.__thumbs);
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