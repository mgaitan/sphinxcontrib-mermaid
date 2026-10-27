import { test, expect } from "./fixtures.js";

const inlineSvg = "#giant > .mermaid-viewport > svg";
const dialog = "dialog.mermaid-fullscreen";

async function ready(page) {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/sizing.html");
  await expect(
    page.locator(".mermaid-diagram:not([data-mermaid-state=rendered])"),
  ).toHaveCount(0);
}

async function open(page) {
  await page
    .locator("#giant .mermaid-toolbar")
    .getByRole("button", { name: "View fullscreen" })
    .click();
  await expect(page.locator(dialog)).toBeVisible();
}

test("opens, fits, zooms, closes on Escape and restores focus", async ({
  page,
}) => {
  await ready(page);
  const before = await page.locator(inlineSvg).getAttribute("viewBox");
  await open(page);
  const svg = page.locator(`${dialog} svg`).first();
  const r = await svg.boundingBox();
  expect(r.width).toBeLessThanOrEqual(1280);
  expect(r.width).toBeGreaterThan(640);
  await expect(page.locator(inlineSvg)).toHaveCount(0);
  const fit = await svg.getAttribute("viewBox");
  await page.locator(dialog).getByRole("button", { name: "Zoom in" }).click();
  expect(await svg.getAttribute("viewBox")).not.toBe(fit);
  await page.keyboard.press("Escape");
  await expect(page.locator(dialog)).toBeHidden();
  await expect(page.locator(inlineSvg)).toHaveCount(1);
  expect(await page.locator(inlineSvg).getAttribute("viewBox")).toBe(before);
  await expect(
    page.locator("#giant").getByRole("button", { name: "View fullscreen" }),
  ).toBeFocused();
  const focused = await page.evaluate(
    () =>
      document.activeElement?.closest(".mermaid-diagram")?.id +
      "/" +
      document.activeElement?.getAttribute("aria-label"),
  );
  expect(focused).toBe("giant/View fullscreen");
});

test("backdrop click closes", async ({ page }) => {
  await ready(page);
  await open(page);
  await page.mouse.click(5, 5);
  await expect(page.locator(dialog)).toBeHidden();
  await expect(page.locator(inlineSvg)).toHaveCount(1);
});

test("close button closes", async ({ page }) => {
  await ready(page);
  await open(page);
  await page
    .locator(dialog)
    .getByRole("button", { name: "Close fullscreen" })
    .click();
  await expect(page.locator(dialog)).toBeHidden();
});

test("body scroll locked while open", async ({ page }) => {
  await ready(page);
  await open(page);
  expect(await page.evaluate(() => document.body.style.overflow)).toBe(
    "hidden",
  );
  await page.keyboard.press("Escape");
  await expect(page.locator(dialog)).toBeHidden();
  await expect
    .poll(() => page.evaluate(() => document.body.style.overflow))
    .toBe("");
});

test("fullscreen disabled per diagram", async ({ page }) => {
  await ready(page);
  await expect(
    page.locator("#nofs").getByRole("button", { name: "View fullscreen" }),
  ).toHaveCount(0);
});

test("theme switch while fullscreen keeps one svg and restores focus", async ({
  page,
}) => {
  await ready(page);
  await open(page);
  await page.evaluate(() => (document.body.dataset.theme = "dark"));
  await expect
    .poll(() =>
      page.evaluate(() => window.mermaid.mermaidAPI.getSiteConfig().theme),
    )
    .toBe("dark");
  // Wait until #giant has been re-drawn: either the overlay closed for it, or a
  // new SVG landed in its inline viewport while the old one is still shown.
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          !document.querySelector("dialog.mermaid-fullscreen")?.open ||
          !!document.querySelector("#giant > .mermaid-viewport > svg"),
      ),
    )
    .toBe(true);
  await page.keyboard.press("Escape");
  await expect(page.locator(dialog)).toBeHidden();
  await expect(page.locator("#giant > .mermaid-viewport > svg")).toHaveCount(1);
  await expect(
    page.locator("#giant").getByRole("button", { name: "View fullscreen" }),
  ).toBeFocused();
});

test("closing after a resize re-fits the inline diagram", async ({ page }) => {
  await ready(page);
  const width = () =>
    page
      .locator("#wide > .mermaid-viewport > svg")
      .evaluate((el) => el.getBoundingClientRect().width);
  const before = await width();
  await page
    .locator("#wide .mermaid-toolbar")
    .getByRole("button", { name: "View fullscreen" })
    .click();
  await expect(page.locator(dialog)).toBeVisible();
  await page.setViewportSize({ width: 375, height: 800 });
  await page.keyboard.press("Escape");
  await expect(page.locator(dialog)).toBeHidden();
  await expect.poll(width).toBeLessThan(before);
});
