import { defineConfig } from "@playwright/test";

const port = Number(process.env.CITY_TEST_PORT || 8765);
if (!Number.isInteger(port) || port < 1024 || port > 65535) {
  throw new Error("CITY_TEST_PORT must be an unprivileged TCP port.");
}
const baseURL = `http://127.0.0.1:${port}`;

export default defineConfig({
  testDir: "./tests",
  timeout: 90000,
  globalTimeout: 900000,
  expect: { timeout: 10000 },
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: 0,
  outputDir: "test-results/artifacts",
  reporter: [
    ["list"],
    ["json", { outputFile: "test-results/results.json" }],
    ["html", { outputFolder: "playwright-report", open: "never" }]
  ],
  use: {
    baseURL,
    browserName: "chromium",
    acceptDownloads: true,
    reducedMotion: "reduce",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    launchOptions: {
      args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
    }
  },
  projects: [
    { name: "desktop-chromium", use: { viewport: { width: 1280, height: 900 } } },
    { name: "mobile-chromium", use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } }
  ],
  webServer: {
    command: `python3 -m http.server ${port} --bind 127.0.0.1 --directory .`,
    url: baseURL,
    reuseExistingServer: false,
    timeout: 15000,
    stdout: "ignore",
    stderr: "pipe"
  }
});