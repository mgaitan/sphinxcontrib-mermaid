import { test, expect } from "./fixtures.js";

const viewBox = (page, id) =>
  page.locator(`#${id} > .mermaid-viewport > svg`).getAttribute("viewBox");

async function ready(page, path = "/sizing.html") {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto(path);
  await expect(
    page.locator(".mermaid-diagram:not([data-mermaid-state=rendered])"),
  ).toHaveCount(0);
}

test("toolbar visible by default", async ({ page }) => {
  await ready(page);
  const toolbar = page.locator("#small .mermaid-toolbar");
  await expect(toolbar).toBeVisible();
  const opacity = Number(
    await toolbar.evaluate((el) => getComputedStyle(el).opacity),
  );
  expect(opacity).toBeGreaterThan(0.4);
  expect(opacity).toBeLessThan(0.7);
  await expect(
    toolbar.getByRole("button", { name: "View fullscreen" }),
  ).toBeVisible();
  await expect(toolbar.getByRole("button", { name: "Zoom in" })).toHaveCount(0);
});

test("zoom buttons change viewBox and reset restores", async ({ page }) => {
  await ready(page);
  const toolbar = page.locator("#giant .mermaid-toolbar");
  const initial = await viewBox(page, "giant");
  await toolbar.getByRole("button", { name: "Zoom in" }).click();
  expect(await viewBox(page, "giant")).not.toBe(initial);
  await toolbar.getByRole("button", { name: "Reset zoom" }).click();
  expect(await viewBox(page, "giant")).toBe(initial);
});

test("keyboard zoom", async ({ page }) => {
  await ready(page);
  const initial = await viewBox(page, "giant");
  await page.locator("#giant > .mermaid-viewport").focus();
  await page.keyboard.press("=");
  expect(await viewBox(page, "giant")).not.toBe(initial);
  await page.keyboard.press("0");
  expect(await viewBox(page, "giant")).toBe(initial);
});

test("ctrl+wheel zooms, plain wheel scrolls page", async ({ page }) => {
  await ready(page);
  const viewport = page.locator("#giant > .mermaid-viewport");
  await viewport.scrollIntoViewIfNeeded();
  const initial = await viewBox(page, "giant");
  const r = await viewport.boundingBox();
  await page.mouse.move(r.x + r.width / 2, r.y + r.height / 2);
  const scrollBefore = await page.evaluate(() => window.scrollY);
  await page.mouse.wheel(0, 200);
  await expect
    .poll(() => page.evaluate(() => window.scrollY))
    .toBeGreaterThan(scrollBefore);
  expect(await viewBox(page, "giant")).toBe(initial);
  const r2 = await viewport.boundingBox();
  await page.mouse.move(r2.x + r2.width / 2, r2.y + r2.height / 2);
  await page.keyboard.down("Control");
  await page.mouse.wheel(0, -200);
  await page.keyboard.up("Control");
  await expect.poll(() => viewBox(page, "giant")).not.toBe(initial);
});

test("drag pans", async ({ page }) => {
  await ready(page);
  const viewport = page.locator("#giant > .mermaid-viewport");
  const initial = (await viewBox(page, "giant")).split(" ").map(Number);
  const r = await viewport.boundingBox();
  await page.mouse.move(r.x + 200, r.y + 100);
  await page.mouse.down();
  await page.mouse.move(r.x + 100, r.y + 100, { steps: 5 });
  await page.mouse.up();
  const after = (await viewBox(page, "giant")).split(" ").map(Number);
  expect(after[0]).toBeGreaterThan(initial[0]);
  expect(after[2]).toBeCloseTo(initial[2], 3);
});

test("click link still works with zoom", async ({ page }) => {
  await page.route("https://example.com/**", (route) =>
    route.fulfill({ body: "ok" }),
  );
  await ready(page, "/index.html");
  await expect(page.locator("#linked")).toHaveAttribute(
    "data-mermaid-zoom",
    "true",
  );
  const navigation = page.waitForRequest("https://example.com/**");
  await page.locator("#linked").getByText("Example").click();
  await navigation;
});

test("hover mode hides toolbar until hover or focus", async ({ page }) => {
  await ready(page, "http://127.0.0.1:3001/sizing.html");
  const toolbar = page.locator("#small .mermaid-toolbar");
  const opacity = () =>
    toolbar.evaluate((el) => Number(getComputedStyle(el).opacity));
  await page.mouse.move(0, 0);
  await expect.poll(opacity).toBe(0);
  await page.locator("#small").hover();
  await expect.poll(opacity).toBe(1);
  await page.mouse.move(0, 0);
  await toolbar.getByRole("button", { name: "View fullscreen" }).focus();
  await expect.poll(opacity).toBe(1);
});
