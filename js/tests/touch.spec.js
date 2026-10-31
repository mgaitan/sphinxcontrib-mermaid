import { test, expect } from "./fixtures.js";

test.use({
  viewport: { width: 393, height: 851 },
  hasTouch: true,
  isMobile: true,
});

async function ready(page, path) {
  await page.goto(path);
  await expect(
    page.locator(".mermaid-diagram:not([data-mermaid-state=rendered])"),
  ).toHaveCount(0);
}

test("vertical swipe over a zoomable diagram scrolls the page", async ({
  page,
}) => {
  await ready(page, "/sizing.html");
  const viewport = page.locator("#giant > .mermaid-viewport");
  await viewport.scrollIntoViewIfNeeded();
  await expect(page.locator("#giant")).toHaveAttribute(
    "data-mermaid-zoom",
    "true",
  );
  const r = await viewport.boundingBox();
  const before = await page.evaluate(() => window.scrollY);
  const cdp = await page.context().newCDPSession(page);
  const x = Math.round(r.x + r.width / 2);
  const y = Math.round(r.y + r.height / 2);
  // Raw touch events: Linux headless Chromium ignores Input.synthesizeScrollGesture.
  const touch = (type, py) =>
    cdp.send("Input.dispatchTouchEvent", {
      type,
      touchPoints: type === "touchEnd" ? [] : [{ x, y: py }],
    });
  await touch("touchStart", y);
  for (let dy = 10; dy <= 200; dy += 10) await touch("touchMove", y - dy);
  await touch("touchEnd", y - 200);
  await expect
    .poll(() => page.evaluate(() => window.scrollY))
    .toBeGreaterThan(before + 50);
});

test("first tap after a touch pan follows a link", async ({ page }) => {
  await page.route("https://example.com/**", (route) =>
    route.fulfill({ body: "ok" }),
  );
  await ready(page, "/index.html");
  const viewport = page.locator("#linked > .mermaid-viewport");
  await viewport.scrollIntoViewIfNeeded();
  const r = await viewport.boundingBox();
  const cdp = await page.context().newCDPSession(page);
  const x = Math.round(r.x + r.width / 2);
  const y = Math.round(r.y + r.height / 2);
  const touch = (type, px) =>
    cdp.send("Input.dispatchTouchEvent", {
      type,
      touchPoints: type === "touchEnd" ? [] : [{ x: px, y }],
    });
  await touch("touchStart", x);
  for (let dx = 10; dx <= 60; dx += 10) await touch("touchMove", x - dx);
  await touch("touchEnd", x - 60);
  // Linux Chromium drops a tap within its 300ms double-tap window after a
  // touch the page handled, with or without this extension.
  await page.waitForTimeout(400);
  const navigation = page.waitForRequest("https://example.com/**", {
    timeout: 5000,
  });
  const label = await page
    .locator("#linked")
    .getByText("Example")
    .boundingBox();
  await page.touchscreen.tap(
    label.x + label.width / 2,
    label.y + label.height / 2,
  );
  await navigation;
});

test("hover-mode toolbar ignores taps until revealed", async ({ page }) => {
  await ready(page, "http://127.0.0.1:3001/sizing.html");
  const button = await page
    .locator("#small")
    .getByRole("button", { name: "View fullscreen" })
    .boundingBox();
  const tap = () =>
    page.touchscreen.tap(
      button.x + button.width / 2,
      button.y + button.height / 2,
    );
  await tap();
  await expect(page.locator("dialog.mermaid-fullscreen[open]")).toHaveCount(0);
  await tap();
  await expect(page.locator("dialog.mermaid-fullscreen[open]")).toHaveCount(1);
});
