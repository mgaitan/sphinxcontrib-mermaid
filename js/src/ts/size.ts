import type { Diagram, SiteConfig, SizeResult } from "./types";

const DEFAULT_FONT_PX = 16;

function natural(svg: SVGSVGElement): {
  x: number;
  y: number;
  width: number;
  height: number;
} {
  // Cached: pan/zoom rewrites the viewBox after the first sizing pass.
  if (svg.dataset.mermaidNatural) return JSON.parse(svg.dataset.mermaidNatural);
  let { x, y, width, height } = svg.viewBox.baseVal ?? {};
  if (!width || !height) {
    ({ x, y, width, height } = svg.getBBox());
  }
  const box = { x, y, width, height };
  svg.dataset.mermaidNatural = JSON.stringify(box);
  return box;
}

function diagramFontPx(d: Diagram, site: SiteConfig): number {
  const theme = site.config.themeVariables as
    | Record<string, unknown>
    | undefined;
  const size = parseFloat(
    String(d.options.fontSize ?? site.config.fontSize ?? theme?.fontSize ?? ""),
  );
  return size > 0 ? size : DEFAULT_FONT_PX;
}

function contentWidth(el: HTMLElement): number {
  const style = getComputedStyle(el);
  return (
    el.clientWidth -
    parseFloat(style.paddingLeft) -
    parseFloat(style.paddingRight)
  );
}

/** Convert a CSS length (e.g. "70vh", "300px") to pixels in the context of ``el``. */
function toPx(el: HTMLElement, length: string): number {
  const probe = document.createElement("div");
  probe.style.cssText = `position:absolute;visibility:hidden;height:${length}`;
  el.append(probe);
  const px = probe.getBoundingClientRect().height;
  probe.remove();
  return px;
}

export function zoomActive(d: Diagram, r: SizeResult | null = d.size): boolean {
  return (
    d.options.zoom === true || (d.options.zoom === "auto" && !!r?.overflow)
  );
}

/** Size a rendered diagram per its fit mode, keeping text at a readable size. */
export function applySize(d: Diagram, site: SiteConfig): SizeResult {
  const svg = d.svg!;
  const viewport = svg.parentElement as HTMLElement;
  const { x, y, width: w, height: h } = natural(svg);
  svg.removeAttribute("width");
  svg.removeAttribute("height");
  svg.style.maxWidth = "";
  svg.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);

  d.el.style.width = d.options.width ?? "";
  const parent = d.el.parentElement ?? d.el;
  const available = d.options.width
    ? viewport.clientWidth
    : contentWidth(parent);
  const bodyPx =
    parseFloat(getComputedStyle(parent).fontSize) || DEFAULT_FONT_PX;
  const floor = Math.min(
    1,
    (site.minFontScale * bodyPx) / diagramFontPx(d, site),
  );

  let scale = Math.min(1, available / w);
  let overflow = false;
  let height: number | null = null;
  if (d.options.height) {
    height = toPx(d.el, d.options.height);
    scale = Math.min(scale, height / h);
    // fit: auto keeps text readable inside the requested box; fit: contain shrinks.
    if (d.options.fit === "auto" && scale < floor) {
      scale = floor;
      overflow = true;
    }
  } else if (d.options.fit === "auto" && scale < floor) {
    scale = floor;
    overflow = true;
    height = Math.min(h * floor, toPx(d.el, site.maxHeight));
  }

  svg.style.width = `${w * scale}px`;
  svg.style.height = `${h * scale}px`;
  viewport.style.height = height === null ? "" : `${height}px`;
  // Hug a diagram that fits, so the toolbar sits at its edge rather than the column's.
  if (!overflow && height === null && !d.options.width)
    d.el.style.width = `${w * scale}px`;
  d.el.dataset.mermaidOverflow = String(overflow);
  d.el.style.setProperty("--mermaid-scale", String(scale));
  d.size = { scale, overflow, height };
  d.el.dataset.mermaidZoom = String(zoomActive(d));
  return d.size;
}

/** Call ``cb`` when the diagram's container changes width. */
export function onResize(d: Diagram, cb: () => void): void {
  const target = d.el.parentElement ?? d.el;
  let width = target.clientWidth;
  let height = window.innerHeight;
  let frame = 0;
  const schedule = () => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(cb);
  };
  new ResizeObserver(() => {
    if (target.clientWidth === width) return;
    width = target.clientWidth;
    schedule();
  }).observe(target);
  // Height caps such as 70vh follow the window, not the column.
  window.addEventListener("resize", () => {
    if (window.innerHeight === height) return;
    height = window.innerHeight;
    schedule();
  });
}

/** Make the SVG fill its viewport and show the sized region through its viewBox. */
export function zoomLayout(d: Diagram): void {
  const svg = d.svg!;
  const viewport = svg.parentElement as HTMLElement;
  const { scale, height } = d.size!;
  const n = natural(svg);
  const vw = viewport.clientWidth;
  const vh = height ?? n.height * scale;
  viewport.style.height = `${vh}px`;
  svg.style.width = "100%";
  svg.style.height = "100%";
  const w = vw / scale;
  const h = vh / scale;
  // Center a diagram smaller than its viewport; start an overflowing one at its top left.
  const x = n.x + Math.min(0, (n.width - w) / 2);
  const y = n.y + Math.min(0, (n.height - h) / 2);
  svg.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
}
