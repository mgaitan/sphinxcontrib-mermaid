import { test, expect } from "./fixtures.js";

test("every gallery diagram renders", async ({ guarded }) => {
  const { page, errors, remote } = guarded;
  await page.goto("http://127.0.0.1:3002/src/examples.html");
  const diagrams = page.locator(".mermaid-diagram");
  await expect(diagrams).not.toHaveCount(0);
  await expect(
    page.locator(".mermaid-diagram:not([data-mermaid-state=rendered])"),
  ).toHaveCount(0, { timeout: 30000 });
  expect(remote).toEqual([]);
  expect(errors).toEqual([]);
});
