import { test, expect } from "./fixtures.js";

test("renders every diagram offline", async ({ guarded }) => {
  const { page, errors, remote } = guarded;
  const requested = [];
  page.on("request", (request) => requested.push(request.url()));
  await page.goto("/index.html");
  await expect(
    page.locator(
      ".mermaid-diagram[data-mermaid-state=rendered] > .mermaid-viewport > svg",
    ),
  ).toHaveCount(6);
  await expect(page.locator("#zen > .mermaid-viewport > svg")).toHaveCount(1);
  await expect(page.locator("#tidy > .mermaid-viewport > svg")).toHaveCount(1);
  expect(
    requested.some((url) => url.includes("mermaid-layout-tidy-tree/chunks/")),
  ).toBe(true);
  expect(requested.some((url) => url.includes("mermaid-zenuml/chunks/"))).toBe(
    true,
  );
  expect(
    requested.some((url) => /config\.json\?v=[0-9a-f]{12}$/.test(url)),
  ).toBe(true);
  expect(remote).toEqual([]);
  expect(errors).toEqual([]);
});

test("nested page loads assets", async ({ guarded }) => {
  const { page, errors } = guarded;
  await page.goto("/sub/nested.html");
  await expect(
    page.locator(
      ".mermaid-diagram[data-mermaid-state=rendered] > .mermaid-viewport > svg",
    ),
  ).toHaveCount(1);
  expect(errors).toEqual([]);
});

test("search highlight does not break parsing", async ({ guarded }) => {
  const { page } = guarded;
  await page.goto("/index.html?highlight=Client");
  await expect(
    page.locator(
      "#small[data-mermaid-state=rendered] > .mermaid-viewport > svg",
    ),
  ).toHaveCount(1);
});

test("hidden diagram renders when shown", async ({ guarded }) => {
  const { page } = guarded;
  await page.goto("/hidden.html");
  const diagram = page.locator("#tab .mermaid-diagram");
  await expect(diagram).toHaveAttribute("data-mermaid-state", "pending");
  await page.click("#show");
  await expect(diagram).toHaveAttribute("data-mermaid-state", "rendered");
  await expect(diagram.locator(":scope > .mermaid-viewport > svg")).toHaveCount(
    1,
  );
});

test("error does not stop later diagrams", async ({ guarded }) => {
  const { page } = guarded;
  await page.goto("/errors.html");
  const diagrams = page.locator(".mermaid-diagram");
  await expect(diagrams.nth(0)).toHaveAttribute("data-mermaid-state", "error");
  await expect(diagrams.nth(0).locator(".mermaid-error")).toBeVisible();
  await expect(diagrams.nth(1)).toHaveAttribute(
    "data-mermaid-state",
    "rendered",
  );
});

test("public api re-renders", async ({ guarded }) => {
  const { page } = guarded;
  await page.goto("/index.html");
  await expect(
    page.locator(".mermaid-diagram[data-mermaid-state=rendered]"),
  ).toHaveCount(6);
  await page.evaluate(() => window.sphinxcontribMermaid.render());
  expect(await page.evaluate(() => typeof window.mermaid.render)).toBe(
    "function",
  );
  await expect(page.locator("#small > .mermaid-viewport > svg")).toHaveCount(1);
});

test("source readable without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/index.html");
  await expect(page.locator("#small pre")).toContainText("flowchart LR");
  await context.close();
});

test("sandboxed rendering keeps the iframe output", async ({ guarded }) => {
  const { page, errors } = guarded;
  await page.goto("/index.html");
  await expect(
    page.locator(".mermaid-diagram[data-mermaid-state=rendered]"),
  ).toHaveCount(6);
  await page.evaluate(async () => {
    window.mermaid.initialize({ startOnLoad: false, securityLevel: "sandbox" });
    await window.sphinxcontribMermaid.render();
  });
  await expect(page.locator("#small")).toHaveAttribute(
    "data-mermaid-state",
    "rendered",
  );
  await expect(page.locator("#small > .mermaid-viewport > iframe")).toHaveCount(
    1,
  );
  expect(errors).toEqual([]);
});
