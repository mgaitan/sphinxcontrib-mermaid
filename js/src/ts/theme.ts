const media = matchMedia("(prefers-color-scheme: dark)");

function fromAttribute(el: HTMLElement): boolean | null {
  const value = el.dataset.theme;
  if (value === "dark") return true;
  if (value === "light") return false;
  if (value === "auto") return media.matches;
  return null;
}

function luminance(color: string): number | null {
  const match = color.match(
    /rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?/,
  );
  if (!match || match[4] === "0") return null;
  const [r, g, b] = match.slice(1, 4).map(Number);
  return (r * 299 + g * 587 + b * 114) / 1000;
}

/**
 * Detect dark mode: Furo (body[data-theme]), pydata (html[data-theme]),
 * sphinx-fuma and sphinxawesome (html.dark / html.light), then the page background,
 * then the OS preference.
 */
export function isDark(): boolean {
  const html = document.documentElement;
  const body = document.body;
  const attribute = fromAttribute(body) ?? fromAttribute(html);
  if (attribute !== null) return attribute;
  if (html.classList.contains("dark") || body.classList.contains("dark"))
    return true;
  if (html.classList.contains("light") || body.classList.contains("light"))
    return false;
  const background =
    luminance(getComputedStyle(body).backgroundColor) ??
    luminance(getComputedStyle(html).backgroundColor);
  if (background !== null) return background < 128;
  return media.matches;
}

/** Call ``cb`` with the new mode whenever the page flips between light and dark. */
export function watchTheme(cb: (dark: boolean) => void): void {
  let dark = isDark();
  const check = () => {
    const next = isDark();
    if (next === dark) return;
    dark = next;
    cb(dark);
  };
  const observer = new MutationObserver(check);
  for (const el of [document.documentElement, document.body]) {
    observer.observe(el, {
      attributes: true,
      attributeFilter: ["class", "data-theme", "style"],
    });
  }
  media.addEventListener("change", check);
}

type Role = "bg" | "fg" | "muted" | "surface" | "border" | "accent";

/** The custom properties that hold each theme's colors. */
const THEMES: Record<Role, string>[] = [
  // Furo
  {
    bg: "--color-background-primary",
    fg: "--color-foreground-primary",
    muted: "--color-foreground-secondary",
    surface: "--color-background-secondary",
    border: "--color-background-border",
    accent: "--color-brand-primary",
  },
  // pydata-sphinx-theme
  {
    bg: "--pst-color-background",
    fg: "--pst-color-text-base",
    muted: "--pst-color-text-muted",
    surface: "--pst-color-surface",
    border: "--pst-color-border",
    accent: "--pst-color-primary",
  },
  // sphinx-fuma
  {
    bg: "--color-fd-background",
    fg: "--color-fd-foreground",
    muted: "--color-fd-muted-foreground",
    surface: "--color-fd-muted",
    border: "--color-fd-border",
    accent: "--color-fd-primary",
  },
  // sphinxawesome-theme, as bare HSL components
  {
    bg: "--background",
    fg: "--foreground",
    muted: "--muted-foreground",
    surface: "--muted",
    border: "--border",
    accent: "--primary",
  },
];

/** The Mermaid theme variables set from each role. */
const VARIABLES: Record<Role, string[]> = {
  bg: ["background", "clusterBkg", "edgeLabelBackground"],
  fg: [
    "textColor",
    "primaryTextColor",
    "nodeTextColor",
    "titleColor",
    "actorTextColor",
    "signalColor",
    "signalTextColor",
    "labelTextColor",
    "loopTextColor",
  ],
  muted: ["lineColor"],
  surface: ["mainBkg", "actorBkg", "labelBoxBkgColor"],
  border: ["clusterBorder"],
  // The dark theme draws node borders as a gradient between the two stops.
  accent: [
    "nodeBorder",
    "actorBorder",
    "labelBoxBorderColor",
    "gradientStart",
    "gradientStop",
  ],
};

/**
 * Category colors for the dark theme, whose own scale is nearly black.
 * Used by pie, mindmap, timeline, treemap, radar, and kanban.
 */
const DARK_SCALE = [
  "#3b6ea5",
  "#c26a1b",
  "#b8403f",
  "#3f8f8a",
  "#4b8a3e",
  "#a68a1d",
  "#8a5a88",
  "#c0607a",
  "#7a5c48",
  "#5f6b7a",
  "#2f7f9f",
  "#8f4fb0",
];

let paint: CanvasRenderingContext2D | null = null;

/** Convert any CSS color to rgb()/rgba(), which Mermaid's color library can parse. */
function toRgb(value: string): string | null {
  paint ??= document
    .createElement("canvas")
    .getContext("2d", { willReadFrequently: true });
  if (!paint) return null;
  // An invalid color leaves fillStyle unchanged, so it differs between the two.
  paint.fillStyle = "#000";
  paint.fillStyle = value;
  const first = paint.fillStyle;
  paint.fillStyle = "#fff";
  paint.fillStyle = value;
  if (paint.fillStyle !== first) return null;
  paint.clearRect(0, 0, 1, 1);
  paint.fillRect(0, 0, 1, 1);
  const [r, g, b, a] = paint.getImageData(0, 0, 1, 1).data;
  return a === 255
    ? `rgb(${r}, ${g}, ${b})`
    : `rgba(${r}, ${g}, ${b}, ${(a / 255).toFixed(3)})`;
}

/** The page's colors, from the first supported theme whose variables are set. */
function pageColors(): Partial<Record<Role, string>> {
  const styles = getComputedStyle(document.body);
  for (const theme of THEMES) {
    const raw = (role: Role) => styles.getPropertyValue(theme[role]).trim();
    const bare = /^\d/.test(raw("bg"));
    if (!raw("bg") || (theme.bg === "--background" && !bare)) continue;
    const colors: Partial<Record<Role, string>> = {};
    for (const role of Object.keys(theme) as Role[]) {
      const value = raw(role);
      const rgb = value && toRgb(bare ? `hsl(${value})` : value);
      if (rgb) colors[role] = rgb;
    }
    return colors;
  }
  return {};
}

/**
 * Theme variables that fit Mermaid's default light and dark themes to the page:
 * the Sphinx theme's colors, and readable category colors in dark mode.
 */
export function themeVariables(theme: string): Record<string, string> {
  const variables: Record<string, string> = {};
  if (theme !== "default" && theme !== "dark") return variables;
  if (theme === "dark") {
    // Pie colors are derived from the scale, but not for directive variables.
    DARK_SCALE.forEach((color, i) => {
      variables[`cScale${i}`] = color;
      variables[`cScaleLabel${i}`] = "#ffffff";
      variables[`pie${i + 1}`] = color;
    });
  }
  for (const [role, color] of Object.entries(pageColors())) {
    for (const name of VARIABLES[role as Role]) variables[name] = color;
  }
  return variables;
}

/** sphinxawesome stores colors as bare HSL components, which cannot sit in a var() fallback chain. */
export function mapThemeColors(): void {
  const root = document.documentElement;
  const styles = getComputedStyle(root);
  if (!/^\d/.test(styles.getPropertyValue("--background").trim())) return;
  for (const [ours, theirs] of [
    ["bg", "background"],
    ["fg", "foreground"],
    ["border", "border"],
  ]) {
    root.style.setProperty(`--mermaid-theme-${ours}`, `hsl(var(--${theirs}))`);
  }
}
