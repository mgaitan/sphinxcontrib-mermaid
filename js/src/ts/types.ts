import type { Mermaid } from "mermaid";

export type { Mermaid };

export interface SiteConfig {
  mermaid: string;
  layouts: string[];
  diagrams: string[];
  extensions: string[];
  iconPacks: Record<string, string>;
  config: Record<string, unknown>;
  lightTheme: string;
  darkTheme: string;
  toolbar: "always" | "hover";
  maxHeight: string;
  minFontScale: number;
}

export interface DiagramOptions {
  fit: "auto" | "contain";
  zoom: boolean | "auto";
  fullscreen: boolean;
  width: string | null;
  height: string | null;
  /** The diagram's own Mermaid fontSize, if its config sets one. */
  fontSize?: number | null;
}

export interface Diagram {
  el: HTMLElement;
  source: string;
  options: DiagramOptions;
  svg: SVGSVGElement | null;
  size: SizeResult | null;
}

export interface SizeResult {
  /** Rendered pixels per diagram unit. */
  scale: number;
  /** The diagram does not fit at a readable size and needs a scrolling viewport. */
  overflow: boolean;
  /** The viewport's height in pixels when it is capped, else null. */
  height: number | null;
}

declare global {
  interface Window {
    mermaid: Mermaid;
    sphinxcontribMermaid: { render(root?: ParentNode): Promise<void> };
  }
}
