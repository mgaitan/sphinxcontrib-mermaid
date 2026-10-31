# Troubleshooting

## Diagrams do not render when I open the HTML file directly

Browsers block JavaScript modules on `file://` URLs. Serve the build directory:

```sh
python -m http.server --directory docs/_build/html
```

## A diagram shows an error message

The message comes from Mermaid's parser. Paste the source into the
[Mermaid Live Editor](https://mermaid.live/) to check it. Other diagrams on the
page still render.

## `config` in a MyST fence is ignored or warns about flattened YAML

MyST parses the `---` block at the top of a fence as directive options and
flattens nested YAML. The extension re-reads the block from the source file.
When that is not possible (for example, in notebooks), write `config` as
single-line JSON: `config: {"layout": "elk"}`.

## A removed setting stops the build

See [upgrading from 2.x](migration.md) for each replacement.

## `sphinxcontrib-mermaid assets are missing`

The package was installed from source without building its JavaScript. Install
a wheel from PyPI, or run `pnpm --dir js install && pnpm --dir js build` in the
checkout.

## Links in a diagram do nothing

Mermaid's default `securityLevel` is `strict`, which disables `click`
directives. Set `mermaid_config = {"securityLevel": "loose"}` if you trust the
diagram sources.

## Sandboxed diagrams have no zoom or fullscreen

With `mermaid_config = {"securityLevel": "sandbox"}`, Mermaid renders each
diagram inside an iframe. The extension shows that iframe as-is, without
sizing, pan, zoom, or the toolbar.
