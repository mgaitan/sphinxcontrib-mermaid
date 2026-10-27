# Control diagram size

By default (`fit: auto`), a diagram renders at its natural size. If it is wider
than the page column, it shrinks to fit, but only while its text stays at about
70% of the page's body font size or larger. A diagram that would need to shrink
further stays at that size inside a scrollable view whose height is capped at
70% of the window. Pan and zoom turn on for that view automatically. Small
diagrams take only the space they need.

## Always shrink to fit

Use `fit: contain` to scale a diagram to the column width however small its
text becomes:

```rst
.. mermaid:: big.mmd
   :fit: contain
```

Set `mermaid_fit = "contain"` in `conf.py` to make that the default.

## Set an explicit size

`width` accepts a length or percentage and `height` accepts a length. Bare
numbers are pixels. With a height, the diagram scales down to fit the box, but
under `fit: auto` it stops at the readable text size and pans inside the box
instead. Add `fit: contain` to make it fit the box regardless.

```rst
.. mermaid:: big.mmd
   :width: 80%
   :height: 400px
```

The same keys work in frontmatter:

```text
---
height: 400px
---
flowchart LR
    ...
```

`mermaid_width` and `mermaid_height` set defaults for every diagram.

## Tune the heuristic

- `mermaid_min_font_scale` (default `0.7`) sets the smallest text size as a
  fraction of the body font.
- `mermaid_max_height` (default `"70vh"`) caps the height of the scrolling view.

The heuristic uses Mermaid's `fontSize` (from `mermaid_config` or
`themeVariables.fontSize`, default 16px) as the diagram's text size.
