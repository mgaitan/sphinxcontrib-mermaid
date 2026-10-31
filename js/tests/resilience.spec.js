import { test, expect } from "./fixtures.js";

test("a plugin that fails to load does not block other diagrams", async ({
  guarded,
}) => {
  const { page } = guarded;
  await page.route("**/mermaid-zenuml.esm.min.mjs", (route) =>
    route.fulfill({ status: 404, body: "" }),
  );
  await page.goto("/index.html");
  await expect(page.locator("#small")).toHaveAttribute(
    "data-mermaid-state",
    "rendered",
  );
  await expect(page.locator("#zen")).toHaveAttribute(
    "data-mermaid-state",
    "error",
  );
});
