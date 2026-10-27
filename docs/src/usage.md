# Add diagrams to a project

Add the extension to `conf.py`:

```python
extensions = [..., "sphinxcontrib.mermaid"]
```

## reStructuredText

Write the diagram inline:

```rst
.. mermaid::

   sequenceDiagram
       Alice->>Bob: Hello
       Bob-->>Alice: Hi
```

Or point the directive at a file. Relative paths resolve from the document's
directory, and absolute paths from the source directory:

```rst
.. mermaid:: diagrams/release.mmd
```

## Markdown with MyST

With [MyST](https://myst-parser.readthedocs.io/) enabled, use a `{mermaid}`
directive fence:

````md
```{mermaid}
flowchart LR
    A --> B
```
````

To use plain ```` ```mermaid ```` fences, which also render on GitHub, add this to
`conf.py`:

```python
myst_fence_as_directive = ["mermaid"]
```

## Options

Options can be given as directive options or as top-level keys in the
diagram's frontmatter. Directive options win when both are present. Mermaid
ignores keys it does not know, so a `.mmd` file with sizing keys still renders
on GitHub and in the Mermaid Live Editor.

```rst
.. mermaid::
   :caption: Release flow
   :align: center
   :height: 300px

   ---
   title: Release
   config:
     layout: elk
   ---
   flowchart TD
       Tag --> Build --> Publish
```

See the [configuration reference](configuration.md#per-diagram-options) for the
full list.

Under MyST, the `---` block at the top of a fence is parsed as directive
options, and MyST flattens nested YAML. The extension re-reads the block from
the source file, so nested `config` mappings work. Where the source file is not
available (for example, notebooks), write `config` as single-line JSON:
`config: {"layout": "elk"}`.
