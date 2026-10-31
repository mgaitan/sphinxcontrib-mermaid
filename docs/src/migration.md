# Upgrade from 2.x

3.0 replaces the inline, templated JavaScript with a bundled runtime. Removed
settings raise an error that names the replacement, so a build will not
silently ignore them.

| Removed setting                                                                | Replacement                                                          |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| `mermaid_init_config`                                                          | `mermaid_config`                                                     |
| `mermaid_d3_zoom`                                                              | `mermaid_zoom`                                                       |
| `d3_version`, `d3_use_local`                                                   | none; d3 is no longer used                                           |
| `mermaid_include_elk`, `mermaid_elk_version`, `mermaid_elk_use_local`          | none; ELK is built into Mermaid 12                                   |
| `mermaid_include_zenuml`, `mermaid_zenuml_version`, `mermaid_zenuml_use_local` | none; ZenUML is bundled. Use `mermaid_extensions` for a custom build |
| `mermaid_fullscreen_button`, `mermaid_fullscreen_button_opacity`               | `mermaid_toolbar` and the `--mermaid-*` CSS variables                |
| `mermaid_js_priority`                                                          | none                                                                 |
| `mermaid_include_mindmap`                                                      | none; mindmap is built into Mermaid                                  |
| `mermaid_use_local`                                                            | `mermaid_base_url`, pointing at a directory instead of one file      |

Other changes:

- **Mermaid is bundled.** Pages no longer load Mermaid from jsdelivr. Set
  `mermaid_base_url = "https://cdn.jsdelivr.net/npm"` to keep doing so.
  `mermaid_version` only applies with a remote `mermaid_base_url` and must be
  12.0.0 or later.
- **`mermaid_config` goes to `mermaid.initialize`.** In 2.x it was copied into
  each diagram's frontmatter, and `mermaid_init_config` went to `initialize`.
  Merge both into `mermaid_config`; Mermaid applies it to every diagram. A
  diagram's own `config` still overrides it.
- **Your theme wins.** `mermaid_light_theme` and `mermaid_dark_theme` apply only
  when no `theme` is set in `mermaid_config` or the diagram's `config`.
- **Sizing changed.** Diagrams no longer get a fixed 500px height. See
  [sizing](sizing.md). `mermaid_width` and `mermaid_height` now default to no
  fixed size.
- **`config` accepts YAML.** The `:config:` option takes YAML or JSON, and
  nested frontmatter works in MyST fences.
- **Markup changed.** Diagrams render into `<div class="mermaid-diagram">`
  instead of `<pre class="mermaid">`. Custom CSS targeting `pre.mermaid > svg`
  or `.mermaid-container` needs updating.
- **Hot reload.** `window.mermaid` is the Mermaid module, and
  `window.sphinxcontribMermaid.render()` re-renders diagrams added to the page
  (it replaces `window.runMermaid`).
- **Building from source needs Node.js.** Wheels on PyPI include the built
  assets; installing from a git checkout or sdist needs Node.js 22+ and pnpm.
