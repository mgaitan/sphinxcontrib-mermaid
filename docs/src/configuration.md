# Configuration reference

## Mermaid

| Setting               | Default     | Description                                                                                                                              |
| --------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `mermaid_config`      | `{}`        | Mermaid configuration passed to `mermaid.initialize` (and to mermaid-cli as a config file). `startOnLoad` is always off.                 |
| `mermaid_light_theme` | `"default"` | Mermaid theme in light mode, used when no `theme` is configured.                                                                         |
| `mermaid_dark_theme`  | `"dark"`    | Mermaid theme in dark mode, used when no `theme` is configured.                                                                          |
| `mermaid_base_url`    | `""`        | npm CDN URL, or `node_modules`-style path under `html_static_path`, to load Mermaid and its plugins from. Empty uses the bundled copies. |
| `mermaid_version`     | `None`      | Mermaid version to load from a remote `mermaid_base_url` (12.0.0 or later, or `"latest"`). Defaults to the bundled version.              |
| `mermaid_icon_packs`  | `{}`        | Icon pack name → Iconify JSON URL or `html_static_path` path.                                                                            |
| `mermaid_extensions`  | `[]`        | ES module URLs or `html_static_path` paths whose default exports are registered as external diagrams or layout loaders.                  |

## Sizing and interaction

| Setting                  | Default    | Description                                                                                            |
| ------------------------ | ---------- | ------------------------------------------------------------------------------------------------------ |
| `mermaid_fit`            | `"auto"`   | `"auto"` keeps text readable and scrolls oversized diagrams; `"contain"` always shrinks to the column. |
| `mermaid_width`          | `None`     | Default diagram width (CSS length or percentage).                                                      |
| `mermaid_height`         | `None`     | Default diagram height (CSS length).                                                                   |
| `mermaid_max_height`     | `"70vh"`   | Height cap for the scrolling view of oversized diagrams.                                               |
| `mermaid_min_font_scale` | `0.7`      | Smallest diagram text size under `fit: auto`, as a fraction of the body font size.                     |
| `mermaid_zoom`           | `False`    | Enable pan and zoom on every diagram. Oversized diagrams get it regardless.                            |
| `mermaid_fullscreen`     | `True`     | Show the fullscreen button.                                                                            |
| `mermaid_toolbar`        | `"always"` | `"always"` shows the toolbar faintly at all times; `"hover"` shows it only on hover, focus, or tap.    |

## Static output

| Setting                   | Default  | Description                                                                                  |
| ------------------------- | -------- | -------------------------------------------------------------------------------------------- |
| `mermaid_output_format`   | `"raw"`  | HTML output: `"raw"` renders in the browser; `"png"` or `"svg"` use mermaid-cli.             |
| `mermaid_cmd`             | `"mmdc"` | mermaid-cli command. A string is split with `shlex.split`; a list is used as-is.             |
| `mermaid_cmd_shell`       | `False`  | Run the command through the shell (needed for some Windows setups).                          |
| `mermaid_params`          | `[]`     | Extra mermaid-cli arguments, for example `["--theme", "forest"]`.                            |
| `mermaid_sequence_config` | `None`   | Path to a JSON config file for mermaid-cli. Merged under `mermaid_config` when both are set. |
| `mermaid_pdfcrop`         | `""`     | `pdfcrop` executable used to trim LaTeX output.                                              |
| `mermaid_verbose`         | `False`  | Log mermaid-cli output.                                                                      |

## Per-diagram options

These work as directive options and as top-level frontmatter keys. Directive
options win over frontmatter, which wins over `conf.py` defaults.

| Option        | Values                                                               |
| ------------- | -------------------------------------------------------------------- |
| `name`        | Reference target and HTML `id`.                                      |
| `class`       | Extra CSS classes.                                                   |
| `alt`         | Accessible label (`aria-label`, image `alt`).                        |
| `align`       | `left`, `center`, or `right`.                                        |
| `caption`     | Figure caption.                                                      |
| `title`       | Mermaid diagram title.                                               |
| `config`      | Mermaid config mapping (YAML or JSON), merged over `mermaid_config`. |
| `displayMode` | Passed to Mermaid frontmatter.                                       |
| `width`       | Length or percentage; bare numbers are pixels.                       |
| `height`      | Length; bare numbers are pixels.                                     |
| `fit`         | `auto` or `contain`.                                                 |
| `zoom`        | Flag, or `true`/`false`.                                             |
| `fullscreen`  | `true` or `false`.                                                   |

## CSS custom properties

Set on `.mermaid-diagram` and `.mermaid-fullscreen`: `--mermaid-bg`,
`--mermaid-fg`, `--mermaid-border`, `--mermaid-toolbar-bg`,
`--mermaid-overlay-bg`. See [theming](theming.md).

## JavaScript API

- `window.mermaid`: the loaded Mermaid module.
- `window.sphinxcontribMermaid.render(root?)`: render diagrams under `root`
  (default: the document), including ones added after page load. Returns a
  promise.
