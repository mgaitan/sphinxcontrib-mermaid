# Load Mermaid from a CDN

By default, Mermaid and its plugins are copied into the built site, so pages
work offline and make no third-party requests. `mermaid_base_url` loads
Mermaid, ZenUML, and the tidy-tree layout from somewhere else instead.

A remote URL is treated as an npm CDN, so any host that serves
`<package>@<version>/dist/...` works, such as jsdelivr, unpkg, or a private
mirror:

```python
mermaid_base_url = "https://cdn.jsdelivr.net/npm"
mermaid_version = "12.2.0"  # optional; defaults to the bundled version
```

`mermaid_version` accepts any release from 12.0.0 on, or `"latest"`. It is
ignored, with a warning, unless `mermaid_base_url` is a remote URL. The ZenUML
and tidy-tree plugins load at the versions the extension was built with.

## Use your own copy

A path under `html_static_path` is read as a `node_modules` directory, with each
package at `<path>/<package>/dist/...`:

```python
html_static_path = ["_static"]
mermaid_base_url = "vendor/node_modules"
```

This serves `_static/vendor/node_modules/mermaid/dist/mermaid.esm.min.mjs`,
`.../@mermaid-js/mermaid-zenuml/dist/mermaid-zenuml.esm.min.mjs`, and
`.../@mermaid-js/layout-tidy-tree/dist/mermaid-layout-tidy-tree.esm.min.mjs`.
