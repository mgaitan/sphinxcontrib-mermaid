import { test, expect } from "./fixtures.js";

const theme = (page) =>
  page.evaluate(() => window.mermaid.mermaidAPI.getSiteConfig().theme);
const styleText = (page, id) =>
  page.locator(`#${id} > .mermaid-viewport > svg > style`).textContent();
const nodeFill = (page, id) =>
  page
    .locator(`#${id} > .mermaid-viewport > svg .node rect`)
    .first()
    .evaluate((el) => getComputedStyle(el).fill);

async function ready(page, path = "/explicit-theme.html", count = 2) {
  await page.goto(path);
  await expect(
    page.locator(".mermaid-diagram[data-mermaid-state=rendered]"),
  ).toHaveCount(count);
}

test("re-renders on furo-style switch", async ({ page }) => {
  await ready(page);
  expect(await theme(page)).toBe("default");
  const before = await styleText(page, "small");
  await page.evaluate(() => (document.body.dataset.theme = "dark"));
  await expect.poll(() => theme(page)).toBe("dark");
  await expect.poll(() => styleText(page, "small")).not.toBe(before);
  await page.evaluate(() => (document.body.dataset.theme = "light"));
  await expect.poll(() => theme(page)).toBe("default");
});

test("html.dark (fuma/sphinxawesome) switches", async ({ page }) => {
  await ready(page);
  await page.evaluate(() => document.documentElement.classList.add("dark"));
  await expect.poll(() => theme(page)).toBe("dark");
});

test("pydata html[data-theme] switches", async ({ page }) => {
  await ready(page);
  await page.evaluate(() => (document.documentElement.dataset.theme = "dark"));
  await expect.poll(() => theme(page)).toBe("dark");
});

test("explicit per-diagram theme wins", async ({ page }) => {
  await ready(page);
  const forest = await nodeFill(page, "forest");
  const before = await styleText(page, "small");
  await page.evaluate(() => (document.body.dataset.theme = "dark"));
  await expect.poll(() => styleText(page, "small")).not.toBe(before);
  expect(await nodeFill(page, "forest")).toBe(forest);
});

test("ids stay unique and nothing duplicates after switching", async ({
  page,
}) => {
  await ready(page, "/index.html", 6);
  for (const value of ["dark", "light"]) {
    const before = await styleText(page, "small");
    await page.evaluate((v) => (document.body.dataset.theme = v), value);
    await expect.poll(() => styleText(page, "small")).not.toBe(before);
    await expect(
      page.locator(".mermaid-diagram[data-mermaid-state=pending]"),
    ).toHaveCount(0);
  }
  const counts = await page.evaluate(() =>
    [...document.querySelectorAll(".mermaid-diagram")].map((el) => [
      el.querySelectorAll(":scope > .mermaid-viewport > svg").length,
      el.querySelectorAll(":scope > .mermaid-toolbar").length,
    ]),
  );
  for (const [svgs, toolbars] of counts) {
    expect(svgs).toBe(1);
    expect(toolbars).toBeLessThanOrEqual(1);
  }
  // Mermaid's tidy-tree layout repeats node IDs inside its own SVG, so only
  // check that no ID is shared between diagrams.
  const shared = await page.evaluate(() => {
    const owners = new Map();
    for (const el of document.querySelectorAll(
      ".mermaid-viewport svg[id], .mermaid-viewport svg [id]",
    )) {
      const owner = el.closest(".mermaid-diagram").id;
      owners.set(el.id, new Set([...(owners.get(el.id) ?? []), owner]));
    }
    return [...owners].filter(([, set]) => set.size > 1).map(([id]) => id);
  });
  expect(shared).toEqual([]);
});

test("sphinxawesome hsl variables mapped", async ({ page }) => {
  await ready(page);
  await page.evaluate(() => {
    document.documentElement.style.setProperty("--background", "224 71% 4%");
    return window.sphinxcontribMermaid.render();
  });
  const bg = await page
    .locator("#small")
    .evaluate((el) => getComputedStyle(el).getPropertyValue("--mermaid-bg"));
  expect(bg).toContain("hsl");
});

test("dark html background with a transparent body is detected", async ({
  page,
}) => {
  await ready(page);
  await page.evaluate(() => {
    document.documentElement.style.background = "#111";
    document.body.style.background = "transparent";
  });
  await expect.poll(() => theme(page)).toBe("dark");
});

const nodeStroke = (page, id) =>
  page
    .locator(`#${id} > .mermaid-viewport > svg .node rect`)
    .first()
    .evaluate((el) => getComputedStyle(el).stroke);

test("furo colors reach diagrams without their own theme", async ({ page }) => {
  await ready(page);
  expect(await nodeFill(page, "small")).toBe("rgb(236, 236, 255)");
  const forest = await nodeFill(page, "forest");
  await page.evaluate(() => {
    const style = document.body.style;
    style.setProperty("--color-background-primary", "#ffffff");
    style.setProperty("--color-background-secondary", "rgb(1, 2, 3)");
    style.setProperty("--color-brand-primary", "rgb(10, 75, 255)");
    return window.sphinxcontribMermaid.render();
  });
  expect(await nodeFill(page, "small")).toBe("rgb(1, 2, 3)");
  expect(await nodeStroke(page, "small")).toBe("rgb(10, 75, 255)");
  expect(await nodeFill(page, "forest")).toBe(forest);
  await page.evaluate(() => (document.body.dataset.theme = "dark"));
  await expect.poll(() => theme(page)).toBe("dark");
  await expect.poll(() => nodeFill(page, "small")).toBe("rgb(1, 2, 3)");
});

test("sphinxawesome bare hsl colors are converted", async ({ page }) => {
  await ready(page);
  await page.evaluate(() => {
    const style = document.documentElement.style;
    style.setProperty("--background", "0 0% 100%");
    style.setProperty("--primary", "0 100% 50%");
    return window.sphinxcontribMermaid.render();
  });
  expect(await nodeStroke(page, "small")).toBe("rgb(255, 0, 0)");
});

test("dark mode uses readable category colors", async ({ page }) => {
  await ready(page, "/colors.html");
  const slices = () =>
    page
      .locator("#pie path.pieCircle")
      .evaluateAll((els) => els.map((el) => getComputedStyle(el).fill).sort());
  const blend = () =>
    page
      .locator("#sankey .link")
      .first()
      .evaluate((el) => getComputedStyle(el).mixBlendMode);
  expect(await blend()).toBe("multiply");
  await page.evaluate(() => (document.body.dataset.theme = "dark"));
  await expect.poll(slices).toEqual(["rgb(194, 106, 27)", "rgb(59, 110, 165)"]);
  expect(await blend()).toBe("normal");
});
