# Match your Sphinx theme

The extension follows light and dark mode in these themes without
configuration:

| Theme               | Dark mode signal           |
| ------------------- | -------------------------- |
| Furo                | `body[data-theme]`         |
| pydata-sphinx-theme | `html[data-theme]`         |
| sphinx-fuma         | `html.dark` / `html.light` |
| sphinxawesome-theme | `html.dark`                |

For other themes it checks `.dark` and `[data-theme]` on `<html>` and
`<body>`, then the page background color, then the operating system preference.
When the mode changes, diagrams re-render with `mermaid_dark_theme` (default
`"dark"`) or `mermaid_light_theme` (default `"default"`).

## Use one Mermaid theme everywhere

Set a theme in `mermaid_config` or in a diagram's `config`. An explicit theme is
never replaced on mode changes:

```python
mermaid_config = {"theme": "neutral"}
```

## Customize colors

The toolbar and fullscreen view use these CSS custom properties, which default
to the theme's background, text, and border colors:

| Property               | Used for                       |
| ---------------------- | ------------------------------ |
| `--mermaid-bg`         | base background                |
| `--mermaid-fg`         | toolbar icons and overlay text |
| `--mermaid-border`     | toolbar border                 |
| `--mermaid-toolbar-bg` | toolbar background             |
| `--mermaid-overlay-bg` | fullscreen background          |

Override them from a stylesheet listed in `html_css_files`:

```css
.mermaid-diagram,
.mermaid-fullscreen {
  --mermaid-overlay-bg: #111;
}
```

For the diagram's own colors, use Mermaid's
[theme variables](https://mermaid.js.org/config/theming.html) through
`mermaid_config` or the diagram's `config`.
