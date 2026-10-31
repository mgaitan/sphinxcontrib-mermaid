import type { Diagram, DiagramOptions, Mermaid, SiteConfig } from "./types";

let mermaid: Mermaid;
let site: SiteConfig;
let queue: Promise<void> = Promise.resolve();
let counter = 0;
const registry = new Map<HTMLElement, Diagram>();
const hooks: ((d: Diagram) => void)[] = [];
const beforeHooks: ((d: Diagram) => void)[] = [];
const waiting = new ResizeObserver((entries) => {
  for (const entry of entries) {
    const d = registry.get(entry.target as HTMLElement);
    if (d && isVisible(d.el)) {
      waiting.unobserve(d.el);
      renderDiagram(d);
    }
  }
});

export function setup(instance: Mermaid, config: SiteConfig): void {
  mermaid = instance;
  site = config;
}

export function onAfterRender(hook: (d: Diagram) => void): void {
  hooks.push(hook);
}

export function onBeforeRender(hook: (d: Diagram) => void): void {
  beforeHooks.push(hook);
}

export function diagrams(): Diagram[] {
  return [...registry.values()];
}

export function initializeMermaid(dark: boolean): void {
  mermaid.initialize({
    ...site.config,
    startOnLoad: false,
    darkMode: dark,
    theme: (site.config.theme ??
      (dark ? site.darkTheme : site.lightTheme)) as never,
  });
}

function isVisible(el: HTMLElement): boolean {
  return el.getClientRects().length > 0;
}

function collect(root: ParentNode): Diagram[] {
  const found: Diagram[] = [];
  for (const el of root.querySelectorAll<HTMLElement>(".mermaid-diagram")) {
    let d = registry.get(el);
    if (!d) {
      // textContent, not innerHTML: search highlighting wraps words in spans
      const source = el.querySelector("pre.mermaid")?.textContent ?? "";
      const options: DiagramOptions = JSON.parse(
        el.dataset.mermaidOptions || "{}",
      );
      d = { el, source, options, svg: null, size: null };
      registry.set(el, d);
      el.dataset.mermaidState = "pending";
    }
    found.push(d);
  }
  return found;
}

async function draw(d: Diagram): Promise<void> {
  const id = `mermaid-svg-${++counter}`;
  try {
    // Render in a scratch box as wide as the diagram so width-adaptive diagrams
    // (gantt) measure the column; Mermaid empties the container it is given.
    const scratch = document.createElement("div");
    scratch.className = "mermaid-scratch";
    d.el.append(scratch);
    let result;
    try {
      result = await mermaid.render(id, d.source, scratch);
    } finally {
      scratch.remove();
    }
    const { svg, bindFunctions } = result;
    for (const hook of beforeHooks) hook(d);
    let viewport = d.el.querySelector<HTMLElement>(
      ":scope > .mermaid-viewport",
    );
    if (!viewport) {
      viewport = document.createElement("div");
      viewport.className = "mermaid-viewport";
      d.el.prepend(viewport);
    }
    viewport.innerHTML = svg;
    d.el.querySelector(":scope > pre.mermaid")?.remove();
    d.el.querySelector(":scope > .mermaid-error")?.remove();
    d.svg = viewport.querySelector("svg");
    const alt = d.el.getAttribute("aria-label");
    if (alt) d.svg?.setAttribute("aria-label", alt);
    bindFunctions?.(viewport);
    d.el.dataset.mermaidState = "rendered";
    for (const hook of hooks) hook(d);
  } catch (error) {
    document.getElementById(`d${id}`)?.remove();
    d.el.querySelector(":scope > .mermaid-error")?.remove();
    const message = document.createElement("pre");
    message.className = "mermaid-error";
    message.textContent =
      error instanceof Error ? error.message : String(error);
    d.el.append(message);
    d.el.dataset.mermaidState = "error";
    console.error("sphinxcontrib-mermaid: rendering failed", error);
  }
}

/** Render one diagram; renders are serialized because Mermaid is not re-entrant. */
export function renderDiagram(d: Diagram): Promise<void> {
  queue = queue.then(() => draw(d));
  return queue;
}

/** Render every diagram under ``root``; hidden ones render when they get a layout box. */
export async function renderAll(root: ParentNode = document): Promise<void> {
  const pending: Promise<void>[] = [];
  for (const d of collect(root)) {
    if (isVisible(d.el)) pending.push(renderDiagram(d));
    else waiting.observe(d.el);
  }
  await Promise.all(pending);
}
