import { ICONS } from "./icons";
import type { PanZoom } from "./panzoom";

export function button(
  label: string,
  icon: string,
  onClick: () => void,
): HTMLButtonElement {
  const el = document.createElement("button");
  el.type = "button";
  el.className = "mermaid-toolbar-button";
  el.setAttribute("aria-label", label);
  el.title = label;
  el.innerHTML = icon;
  el.addEventListener("click", onClick);
  return el;
}

export function createToolbar(opts: {
  zoom: PanZoom | null;
  fullscreen: ((trigger: HTMLElement) => void) | null;
  close?: () => void;
  mode: "always" | "hover";
}): HTMLElement {
  const bar = document.createElement("div");
  bar.className = "mermaid-toolbar";
  bar.dataset.mode = opts.mode;
  const { zoom, fullscreen, close } = opts;
  if (zoom) {
    bar.append(
      button("Zoom out", ICONS.zoomOut, () => zoom.zoomBy(0.8)),
      button("Zoom in", ICONS.zoomIn, () => zoom.zoomBy(1.25)),
      button("Reset zoom", ICONS.reset, () => zoom.reset()),
    );
  }
  if (fullscreen) {
    const open = button("View fullscreen", ICONS.fullscreen, () =>
      fullscreen(open),
    );
    bar.append(open);
  }
  if (close) bar.append(button("Close fullscreen", ICONS.close, close));
  return bar;
}
