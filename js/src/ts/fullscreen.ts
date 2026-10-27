import { PanZoom } from "./panzoom";
import { createToolbar } from "./toolbar";
import type { Diagram } from "./types";

let dialog: HTMLDialogElement | null = null;
let active: { d: Diagram; cleanup: () => void } | null = null;

/** Close the overlay now (cleanup runs synchronously) if it is showing ``d``, or any diagram. */
export function closeFullscreen(d?: Diagram): void {
  if (!active || (d && active.d !== d)) return;
  const { cleanup } = active;
  // close() restores focus to the element focused before showModal; clean up
  // afterwards so focus lands on the current fullscreen button instead.
  dialog?.close();
  cleanup();
}

function getDialog(): HTMLDialogElement {
  if (dialog) return dialog;
  const created = document.createElement("dialog");
  created.className = "mermaid-fullscreen";
  created.setAttribute("aria-label", "Diagram");
  // The dialog's own padding is the backdrop: a click there closes it.
  created.addEventListener("click", (e) => {
    if (e.target === created) closeFullscreen();
  });
  // Chrome ignores Escape on a modal dialog until it has seen user activation
  // inside it, so close explicitly.
  created.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    e.preventDefault();
    closeFullscreen();
  });
  document.body.append(created);
  dialog = created;
  return created;
}

const SAVED = ["viewBox", "preserveAspectRatio", "style"] as const;

/** Show a diagram's live SVG in a full-window overlay with pan/zoom always on. */
export function openFullscreen(
  d: Diagram,
  returnFocus: HTMLElement,
  onClose: () => void = () => {},
): void {
  const svg = d.svg;
  if (!svg) return;
  const home = svg.parentElement as HTMLElement;
  const saved = SAVED.map((name) => [name, svg.getAttribute(name)] as const);
  const homeHeight = home.style.height;
  home.style.height = `${home.getBoundingClientRect().height}px`;
  const bodyOverflow = document.body.style.overflow;

  const overlay = getDialog();
  const viewport = document.createElement("div");
  viewport.className = "mermaid-viewport";
  overlay.replaceChildren(viewport);
  viewport.append(svg);
  document.body.style.overflow = "hidden";
  overlay.showModal();

  // Fit the whole diagram to the overlay.
  const { x, y, width, height } = svg.viewBox.baseVal;
  const natural = JSON.parse(svg.dataset.mermaidNatural ?? "null") ?? {
    x,
    y,
    width,
    height,
  };
  const { width: vw, height: vh } = viewport.getBoundingClientRect();
  const scale = Math.min(vw / natural.width, vh / natural.height);
  const w = vw / scale;
  const h = vh / scale;
  svg.style.width = "100%";
  svg.style.height = "100%";
  svg.style.maxWidth = "none";
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  svg.setAttribute(
    "viewBox",
    `${natural.x - (w - natural.width) / 2} ${natural.y - (h - natural.height) / 2} ${w} ${h}`,
  );
  const zoom = new PanZoom(svg, viewport);
  overlay.append(
    createToolbar({
      zoom,
      fullscreen: null,
      close: () => closeFullscreen(),
      mode: "always",
    }),
  );
  viewport.focus();

  const cleanup = () => {
    if (active?.cleanup !== cleanup) return;
    active = null;
    zoom.destroy();
    for (const [name, value] of saved) {
      if (value === null) svg.removeAttribute(name);
      else svg.setAttribute(name, value);
    }
    home.append(svg);
    home.style.height = homeHeight;
    overlay.replaceChildren();
    document.body.style.overflow = bodyOverflow;
    returnFocus.focus();
    onClose();
  };
  active = { d, cleanup };
  overlay.addEventListener("close", cleanup, { once: true });
}
