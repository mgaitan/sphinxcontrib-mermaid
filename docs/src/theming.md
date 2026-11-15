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

## Diagram colors

With the default Mermaid themes, diagrams also take their colors from these
four Sphinx themes, in both modes:

| Role                               | Furo                           | pydata-sphinx-theme      | sphinx-fuma                   | sphinxawesome-theme  |
| ---------------------------------- | ------------------------------ | ------------------------ | ----------------------------- | -------------------- |
| Background, subgraphs, edge labels | `--color-background-primary`   | `--pst-color-background` | `--color-fd-background`       | `--background`       |
| Text                               | `--color-foreground-primary`   | `--pst-color-text-base`  | `--color-fd-foreground`       | `--foreground`       |
| Lines and arrows                   | `--color-foreground-secondary` | `--pst-color-text-muted` | `--color-fd-muted-foreground` | `--muted-foreground` |
| Node and actor fill                | `--color-background-secondary` | `--pst-color-surface`    | `--color-fd-muted`            | `--muted`            |
| Subgraph border                    | `--color-background-border`    | `--pst-color-border`     | `--color-fd-border`           | `--border`           |
| Node and actor border              | `--color-brand-primary`        | `--pst-color-primary`    | `--color-fd-primary`          | `--primary`          |

In dark mode, pie, mindmap, timeline, treemap, radar, and kanban diagrams use a
set of mid-tone category colors, because Mermaid's own dark palette is nearly
black. Sankey links and ZenUML diagrams are also adjusted to stay readable on a
dark page.

Theme variables in `mermaid_config` take precedence over these colors. A
diagram that sets its own `theme` or `themeVariables`, or a site that sets
`theme` in `mermaid_config`, keeps Mermaid's colors. So does a site that sets
`mermaid_light_theme` or `mermaid_dark_theme` to a theme other than `"default"`
or `"dark"`.

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
