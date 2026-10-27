# sphinxcontrib-mermaid

[![build status](https://github.com/mgaitan/sphinxcontrib-mermaid/actions/workflows/build.yaml/badge.svg)](https://github.com/mgaitan/sphinxcontrib-mermaid/actions/workflows/build.yaml)
[![version](https://img.shields.io/pypi/v/sphinxcontrib-mermaid)](https://pypi.org/project/sphinxcontrib-mermaid/)
[![downloads](https://img.shields.io/pypi/dm/sphinxcontrib-mermaid)](https://libraries.io/pypi/sphinxcontrib-mermaid/)

Embed [Mermaid](https://mermaid.js.org/) diagrams in Sphinx documents. HTML
pages render diagrams in the browser with a bundled copy of Mermaid, sized to
keep text readable, with pan, zoom, and a fullscreen view. LaTeX, texinfo, and
static image output use [mermaid-cli](https://github.com/mermaid-js/mermaid-cli).

## Install

```sh
pip install sphinxcontrib-mermaid
```

```python
# conf.py
extensions = ["sphinxcontrib.mermaid"]
```

## Use

```rst
.. mermaid::
   :caption: Publishing flow

   flowchart LR
       Draft --> Review --> Published
```

In Markdown with [MyST](https://myst-parser.readthedocs.io/), use a
```` ```{mermaid} ```` fence, or set `myst_fence_as_directive = ["mermaid"]` to render
plain ```` ```mermaid ```` fences. Diagrams can also come from `.mmd` files:
`.. mermaid:: diagrams/release.mmd`.

Size and interaction options work as directive options or in the diagram's
frontmatter:

```text
---
title: Release
height: 400px
config:
  layout: elk
---
flowchart TD
    Tag --> Build --> Publish
```

## Documentation

- [Tutorial](docs/src/tutorial.md)
- [Configuration reference](docs/src/configuration.md)
- [Upgrading from 2.x](docs/src/migration.md)
- [Diagram gallery](docs/src/examples.md)
