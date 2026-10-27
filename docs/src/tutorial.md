# Add your first diagram

This tutorial builds a small Sphinx site with one diagram, adds a caption, and
previews it in a browser. You need Python 3.10 or newer.

## Create the project

Install Sphinx and the extension in a fresh virtual environment:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install sphinx sphinxcontrib-mermaid
mkdir docs
```

On Windows, activate the environment with `.venv\Scripts\activate`.

Create `docs/conf.py`:

```python
project = "Publishing guide"
extensions = ["sphinxcontrib.mermaid"]
```

Create `docs/index.rst`:

```rst
Publishing guide
================

.. mermaid::

   flowchart LR
       Draft --> Review --> Published
```

## Build and preview

```sh
python -m sphinx -b html docs docs/_build/html
python -m http.server --directory docs/_build/html
```

Open <http://localhost:8000>. The diagram renders in place of its source. Hover
over it to see the toolbar; the fullscreen button opens the diagram over the
whole window, where you can drag to pan and use the zoom buttons.

The built pages load JavaScript modules, which browsers block on `file://`
URLs. Always preview through a local web server.

## Add a caption

Give the diagram a caption and a name you can link to:

```rst
.. mermaid::
   :caption: How a page gets published
   :name: publishing-flow

   flowchart LR
       Draft --> Review --> Published
```

Rebuild and reload. The caption appears under the diagram, and
`` :ref:`publishing-flow`  `` links to it from any page.

## Next steps

- [Add diagrams to an existing project](usage.md), including Markdown pages.
- [Control how big diagrams appear](sizing.md).
- Browse the [diagram gallery](examples.md) for every diagram type.
