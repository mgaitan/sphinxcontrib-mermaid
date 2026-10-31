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
