import { loadSiteConfig, moduleUrl } from "./config";
import {
  diagrams,
  initializeMermaid,
  onAfterRender,
  onBeforeRender,
  renderAll,
  renderDiagram,
  setup,
} from "./render";
import { closeFullscreen, openFullscreen } from "./fullscreen";
import { PanZoom } from "./panzoom";
import { applySize, onResize, zoomActive, zoomLayout } from "./size";
import { isDark, mapThemeColors, watchTheme } from "./theme";
import { createToolbar } from "./toolbar";
import type { Diagram, Mermaid, SiteConfig } from "./types";

const decorations = new WeakMap<
  HTMLElement,
  { zoom: PanZoom | null; toolbar: HTMLElement | null }
>();

/** Size a rendered diagram, then attach pan/zoom and the toolbar it needs. */
function decorate(d: Diagram, site: SiteConfig): void {
  const previous = decorations.get(d.el);
  const focused = previous?.toolbar?.contains(document.activeElement)
    ? document.activeElement?.getAttribute("aria-label")
    : null;
  previous?.zoom?.destroy();
  previous?.toolbar?.remove();
  decorations.delete(d.el);
  // securityLevel "sandbox" renders into an iframe, which has no SVG to size or zoom.
  if (!d.svg) return;
  applySize(d, site);
  let zoom: PanZoom | null = null;
  if (zoomActive(d)) {
    zoomLayout(d);
    zoom = new PanZoom(d.svg!, d.svg!.parentElement as HTMLElement);
  }
  const toolbar =
    zoom || d.options.fullscreen
      ? createToolbar({
          zoom,
          fullscreen: d.options.fullscreen
            ? (trigger) => {
                const width = d.el.parentElement?.clientWidth;
                // Re-fit if the column changed width while the overlay was open.
                openFullscreen(d, trigger, () => {
                  if (d.el.parentElement?.clientWidth !== width)
                    decorate(d, site);
                });
              }
            : null,
          mode: site.toolbar,
        })
      : null;
  if (toolbar) d.el.append(toolbar);
  decorations.set(d.el, { zoom, toolbar });
  if (focused)
    toolbar?.querySelector<HTMLElement>(`[aria-label="${focused}"]`)?.focus();
}

async function load<T>(url: string): Promise<T> {
  return (await import(moduleUrl(url))).default;
}

// The ZenUML bundle declares generic tokens (--background, --border, ...) on
// :root, clobbering same-named theme tokens. Confine them to the diagram.
function descopeZenumlStyles(): void {
  const descope = (node: Node) => {
    if (!(node instanceof HTMLStyleElement) || node.dataset.zenumlDescoped)
      return;
    const css = node.textContent || "";
    if (!css.includes("--occurance-border")) return;
    node.dataset.zenumlDescoped = "true";
    node.textContent = css.replace(/:root\b/g, ".zenuml");
  };
  new MutationObserver((records) => {
    for (const record of records) record.addedNodes.forEach(descope);
  }).observe(document.head, { childList: true });
}

function register(mermaid: Mermaid, value: unknown): void {
  for (const item of Array.isArray(value) ? value : [value]) {
    if (item && typeof item === "object" && "detector" in item) {
      mermaid.registerExternalDiagrams([item]);
    } else if (item && typeof item === "object" && "loader" in item) {
      mermaid.registerLayoutLoaders([item]);
    }
  }
}

async function boot(): Promise<void> {
  const site = await loadSiteConfig();
  const mermaid = await load<Mermaid>(site.mermaid);
  window.mermaid = mermaid;
  window.sphinxcontribMermaid = {
    render: async (root?: ParentNode) => {
      mapThemeColors();
      await renderAll(root);
    },
  };
  setup(mermaid, site);

  mermaid.registerIconPacks(
    Object.entries(site.iconPacks).map(([name, url]) => ({
      name,
      loader: () => fetch(moduleUrl(url)).then((response) => response.json()),
    })),
  );
  descopeZenumlStyles();
  const modules = await Promise.allSettled(
    [...site.layouts, ...site.diagrams, ...site.extensions].map(load),
  );
  for (const result of modules) {
    if (result.status === "fulfilled") register(mermaid, result.value);
    else console.error("sphinxcontrib-mermaid: failed to load", result.reason);
  }

  document.documentElement.style.setProperty(
    "--mermaid-max-height",
    site.maxHeight,
  );
  const watched = new WeakSet<HTMLElement>();
  // A diagram shown fullscreen goes back inline before it is re-drawn.
  onBeforeRender((d) => closeFullscreen(d));
  onAfterRender((d) => {
    decorate(d, site);
    if (watched.has(d.el)) return;
    watched.add(d.el);
    // Touch has no hover: a tap reveals a hover-mode toolbar. Mark it once the
    // tap's click has passed, so that tap can't hit a still-hidden button.
    let touch = false;
    d.el.addEventListener(
      "pointerdown",
      (e) => (touch = e.pointerType === "touch"),
    );
    d.el.addEventListener("click", () => {
      if (touch) d.el.dataset.touched = "";
    });
    // Skip while the SVG is shown fullscreen; it is re-sized when it returns.
    onResize(d, () => d.svg && d.el.contains(d.svg) && decorate(d, site));
  });

  mapThemeColors();
  initializeMermaid(isDark());
  watchTheme((dark) => {
    mapThemeColors();
    initializeMermaid(dark);
    for (const d of diagrams()) {
      if (d.el.dataset.mermaidState !== "pending") renderDiagram(d);
    }
  });
  await renderAll();
}

boot();
