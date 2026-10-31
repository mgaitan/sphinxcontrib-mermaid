import { test as base, expect } from "@playwright/test";

export const test = base.extend({
  // Pages must never reach the network: abort and record anything not served locally.
  guarded: async ({ page }, use) => {
    const errors = [];
    const remote = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.route("**/*", (route) => {
      const url = route.request().url();
      if (url.startsWith("http://127.0.0.1:")) return route.continue();
      remote.push(url);
      return route.abort();
    });
    await use({ page, errors, remote });
  },
});

export { expect };
