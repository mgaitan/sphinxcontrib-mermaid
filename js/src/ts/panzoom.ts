interface Box {
  x: number;
  y: number;
  w: number;
  h: number;
}

const DRAG_THRESHOLD = 4;
const MIN_SCALE = 0.1;
const MAX_SCALE = 10;
const KEY_PAN = 40;

/** Pan and zoom an SVG by rewriting its viewBox; the viewBox at construction is the fit state. */
export class PanZoom {
  private readonly fit: Box;
  private readonly fitAttr: string;
  private box: Box;
  private readonly pointers = new Map<number, { x: number; y: number }>();
  private dragged = 0;
  private suppressClick = false;
  private readonly abort = new AbortController();

  constructor(
    private readonly svg: SVGSVGElement,
    private readonly viewport: HTMLElement,
  ) {
    this.fitAttr = svg.getAttribute("viewBox") ?? "";
    const [x, y, w, h] = this.fitAttr.split(/[\s,]+/).map(Number);
    this.fit = { x, y, w, h };
    this.box = { ...this.fit };
    viewport.tabIndex = 0;
    const signal = this.abort.signal;
    viewport.addEventListener("wheel", (e) => this.onWheel(e), {
      passive: false,
      signal,
    });
    viewport.addEventListener("pointerdown", (e) => this.onDown(e), {
      signal,
    });
    viewport.addEventListener("pointermove", (e) => this.onMove(e), {
      signal,
    });
    for (const type of ["pointerup", "pointercancel"] as const) {
      viewport.addEventListener(type, (e) => this.onUp(e), { signal });
    }
    // A drag must not also follow a link or fire a Mermaid click callback.
    viewport.addEventListener(
      "click",
      (e) => {
        if (!this.suppressClick) return;
        this.suppressClick = false;
        e.preventDefault();
        e.stopPropagation();
      },
      { capture: true, signal },
    );
    viewport.addEventListener("keydown", (e) => this.onKey(e), { signal });
  }

  get scale(): number {
    return this.fit.w / this.box.w;
  }

  zoomBy(factor: number, cx?: number, cy?: number): void {
    const rect = this.svg.getBoundingClientRect();
    const scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, this.scale * factor));
    const w = this.fit.w / scale;
    const h = this.fit.h / scale;
    const fx = cx === undefined ? 0.5 : (cx - rect.left) / rect.width;
    const fy = cy === undefined ? 0.5 : (cy - rect.top) / rect.height;
    const ux = this.box.x + fx * this.box.w;
    const uy = this.box.y + fy * this.box.h;
    this.set({ x: ux - fx * w, y: uy - fy * h, w, h });
  }

  panBy(dx: number, dy: number): void {
    const rect = this.svg.getBoundingClientRect();
    const k = this.box.w / (rect.width || 1);
    this.set({ ...this.box, x: this.box.x - dx * k, y: this.box.y - dy * k });
  }

  reset(): void {
    this.box = { ...this.fit };
    this.svg.setAttribute("viewBox", this.fitAttr);
  }

  destroy(): void {
    this.abort.abort();
    this.viewport.removeAttribute("tabindex");
  }

  private set(box: Box): void {
    this.box = box;
    this.svg.setAttribute("viewBox", `${box.x} ${box.y} ${box.w} ${box.h}`);
  }

  private onWheel(e: WheelEvent): void {
    if (!(e.ctrlKey || e.metaKey)) return;
    e.preventDefault();
    this.zoomBy(Math.exp(-e.deltaY * 0.002), e.clientX, e.clientY);
  }

  private onDown(e: PointerEvent): void {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    this.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    this.dragged = 0;
    // A touch drag never fires a click, so a stale flag would swallow the next tap.
    this.suppressClick = false;
  }

  private onMove(e: PointerEvent): void {
    const last = this.pointers.get(e.pointerId);
    if (!last) return;
    if (this.pointers.size === 2) {
      const [a, b] = [...this.pointers.values()];
      const other = a === last ? b : a;
      const before = Math.hypot(last.x - other.x, last.y - other.y);
      const after = Math.hypot(e.clientX - other.x, e.clientY - other.y);
      if (before > 0)
        this.zoomBy(
          after / before,
          (e.clientX + other.x) / 2,
          (e.clientY + other.y) / 2,
        );
    } else {
      const dx = e.clientX - last.x;
      const dy = e.clientY - last.y;
      this.dragged += Math.hypot(dx, dy);
      if (this.dragged > DRAG_THRESHOLD) {
        if (!this.viewport.hasPointerCapture(e.pointerId))
          this.viewport.setPointerCapture(e.pointerId);
        this.viewport.dataset.mermaidDragging = "true";
        this.panBy(dx, dy);
      }
    }
    this.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  }

  private onUp(e: PointerEvent): void {
    if (!this.pointers.delete(e.pointerId)) return;
    if (this.dragged > DRAG_THRESHOLD) this.suppressClick = true;
    delete this.viewport.dataset.mermaidDragging;
  }

  private onKey(e: KeyboardEvent): void {
    const actions: Record<string, () => void> = {
      "+": () => this.zoomBy(1.25),
      "=": () => this.zoomBy(1.25),
      "-": () => this.zoomBy(0.8),
      "0": () => this.reset(),
      ArrowLeft: () => this.panBy(KEY_PAN, 0),
      ArrowRight: () => this.panBy(-KEY_PAN, 0),
      ArrowUp: () => this.panBy(0, KEY_PAN),
      ArrowDown: () => this.panBy(0, -KEY_PAN),
    };
    const action = actions[e.key];
    if (!action || e.ctrlKey || e.metaKey || e.altKey) return;
    e.preventDefault();
    action();
  }
}
