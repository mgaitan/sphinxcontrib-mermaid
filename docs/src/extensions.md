# Use icons, layouts, and external diagrams

## Built in

The bundled Mermaid includes every diagram type in its release and the ELK
layouts (`layout: elk`). The extension also bundles the official
[ZenUML](https://mermaid.js.org/syntax/zenuml.html) diagram and the
`tidy-tree` layout. Their code loads only when a page uses them.

## Icon packs

Register [Iconify](https://iconify.design/) JSON icon packs by name. Values are
URLs or paths under `html_static_path`; packs are fetched only when a diagram
uses one of their icons.

```python
mermaid_icon_packs = {
    "logos": "https://cdn.jsdelivr.net/npm/@iconify-json/logos@1/icons.json",
    "local": "icons/local.json",
}
```

Then reference icons as `logos:aws-lambda` in an architecture diagram.

## Other external diagrams and layouts

`mermaid_extensions` lists ES modules to load before rendering. Each module's
default export can be one value or a list. Objects with a `detector` are
registered with `registerExternalDiagrams`, and objects with a `loader` and a
`name` are registered with `registerLayoutLoaders`.

```python
mermaid_extensions = [
    "vendor/my-diagram.esm.min.mjs",
    "https://cdn.jsdelivr.net/npm/some-layout@1/dist/layout.esm.min.mjs",
]
```

Relative paths resolve from `html_static_path`.
