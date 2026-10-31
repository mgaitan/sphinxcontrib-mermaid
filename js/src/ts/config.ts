import type { SiteConfig } from "./types";

const CONFIG_URL = new URL("config.json", import.meta.url);
// A hash of the site config, so browsers don't reuse a stale config.json.
const version = document.querySelector<HTMLScriptElement>(
  "script[data-mermaid-config]",
)?.dataset.mermaidConfig;
if (version) CONFIG_URL.searchParams.set("v", version);

export async function loadSiteConfig(): Promise<SiteConfig> {
  const response = await fetch(CONFIG_URL);
  return response.json();
}

/** Resolve a URL from config.json, which is relative to config.json itself. */
export function moduleUrl(path: string): string {
  return new URL(path, CONFIG_URL).href;
}
