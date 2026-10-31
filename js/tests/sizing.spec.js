import { test, expect } from "./fixtures.js";

const svg = (id) => `#${id} > .mermaid-viewport > svg`;

// Rendered pixels per diagram unit; Mermaid draws its 16px font at 16 units.
async function scaleOf(page, id) {
  return page.locator(svg(id)).evaluate((el) => {
    return el.getBoundingClientRect().width / el.viewBox.baseVal.width;
  });
}

async function box(page, selector) {
  return page.locator(selector).evaluate((el) => {
    const r = el.getBoundingClientRect();
    return { width: r.width, height: r.height };
  });
}

test.beforeEach(async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/sizing.html");
  await expect(
    page.locator(".mermaid-diagram[data-mermaid-state=rendered]"),
  ).toHaveCount(9);
});

test("small diagram renders at natural size and hugs content", async ({
  page,
}) => {
  expect(await scaleOf(page, "small")).toBeCloseTo(1, 2);
  const outer = await box(page, "#small");
  const inner = await box(page, svg("small"));
  expect(outer.height - inner.height).toBeLessThan(40);
  expect(outer.height).toBeLessThan(200);
});

test("wide diagram scales to column without overflow", async ({ page }) => {
  await expect(page.locator("#wide")).toHaveAttribute(
    "data-mermaid-overflow",
    "false",
  );
  const outer = await box(page, "#wide");
  const inner = await box(page, svg("wide"));
  expect(inner.width).toBeLessThanOrEqual(outer.width + 0.5);
});

test("giant diagram stops at text floor and gets capped viewport", async ({
  page,
}) => {
  await expect(page.locator("#giant")).toHaveAttribute(
    "data-mermaid-overflow",
    "true",
  );
  const body = await page.evaluate(() =>
    parseFloat(getComputedStyle(document.body).fontSize),
  );
  const floor = (0.7 * body) / 16;
  expect(await scaleOf(page, "giant")).toBeGreaterThanOrEqual(floor - 0.01);
  expect((await box(page, "#giant")).height).toBeLessThanOrEqual(0.7 * 800 + 1);
});

test("fit contain always shrinks to the column", async ({ page }) => {
  await expect(page.locator("#contained")).toHaveAttribute(
    "data-mermaid-overflow",
    "false",
  );
  const outer = await box(page, "#contained");
  const inner = await box(page, svg("contained"));
  expect(inner.width).toBeLessThanOrEqual(outer.width + 0.5);
});

test("explicit size is respected", async ({ page }) => {
  const outer = await box(page, "#sized");
  expect(outer.width).toBeCloseTo(400, 0);
  expect(outer.height).toBeCloseTo(200, 0);
});

test("zoom false overflow uses native scrolling", async ({ page }) => {
  await expect(page.locator("#nozoom")).toHaveAttribute(
    "data-mermaid-overflow",
    "true",
  );
  await expect(page.locator("#nozoom > .mermaid-viewport")).toHaveCSS(
    "overflow-x",
    "auto",
  );
  const outer = await box(page, "#nozoom");
  const inner = await box(page, svg("nozoom"));
  expect(inner.width).toBeGreaterThan(outer.width);
});

test("resize refits rendered diagrams", async ({ page }) => {
  const before = (await box(page, svg("wide"))).width;
  await page.setViewportSize({ width: 375, height: 800 });
  await expect
    .poll(async () => (await box(page, svg("wide"))).width)
    .toBeLessThan(before);
});

test("width-adaptive diagrams fit the column", async ({ page }) => {
  await expect(page.locator("#gantt")).toHaveAttribute(
    "data-mermaid-overflow",
    "false",
  );
  const outer = await box(page, "#gantt");
  const inner = await box(page, svg("gantt"));
  expect(inner.width).toBeLessThanOrEqual(outer.width + 0.5);
});

test("box hugs a narrow diagram so the toolbar sits at its edge", async ({
  page,
}) => {
  const outer = await box(page, "#small");
  const inner = await box(page, svg("small"));
  expect(outer.width - inner.width).toBeLessThan(12);
  const toolbar = await page
    .locator("#small .mermaid-toolbar")
    .evaluate((el) => el.getBoundingClientRect().right);
  const edge = await page
    .locator(svg("small"))
    .evaluate((el) => el.getBoundingClientRect().right);
  expect(Math.abs(toolbar - edge)).toBeLessThan(12);
});

test("alt text labels the rendered svg", async ({ page }) => {
  await expect(page.locator(svg("small"))).toHaveAttribute(
    "aria-label",
    "Client to API to DB",
  );
});

test("a diagram's own fontSize sets its text floor", async ({ page }) => {
  const scale = await page
    .locator("#bigfont")
    .evaluate((el) => Number(el.style.getPropertyValue("--mermaid-scale")));
  expect(scale).toBeLessThan(0.7);
});

test("explicit height keeps text readable under fit auto", async ({ page }) => {
  const body = await page.evaluate(() =>
    parseFloat(getComputedStyle(document.body).fontSize),
  );
  await expect(page.locator("#sized")).toHaveAttribute(
    "data-mermaid-overflow",
    "true",
  );
  expect(await scaleOf(page, "sized")).toBeGreaterThanOrEqual(
    (0.7 * body) / 16 - 0.01,
  );
  expect((await box(page, "#sized")).height).toBeCloseTo(200, 0);
});

test("window height change re-caps overflowing diagrams", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 400 });
  await expect
    .poll(async () => (await box(page, "#giant")).height)
    .toBeLessThanOrEqual(0.7 * 400 + 1);
});
