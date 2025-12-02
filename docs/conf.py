#!/usr/bin/env python3
from pathlib import Path

extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinx.ext.imgconverter",
]

templates_path = ["_templates"]
source_suffix = [".md"]
master_doc = "index"
project = "sphinxcontrib-mermaid"
copyright = "2017-2025, Martín Gaitán"
author = "Martín Gaitán"

version = "2.0"
release = "2.0.0rc1"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False

html_theme = "furo"

html_static_path = ["_static"]
htmlhelp_basename = "sphinxcontrib-mermaiddoc"

latex_documents = [
    (master_doc, "sphinxcontrib-mermaid.tex", "sphinxcontrib-mermaid documentation", "Martín Gaitán", "manual"),
]

man_pages = [(master_doc, "sphinxcontrib-mermaid", "sphinxcontrib-mermaid documentation", [author], 1)]

texinfo_documents = [
    (
        master_doc,
        "sphinxcontrib-mermaid",
        "sphinxcontrib-mermaid documentation",
        author,
        "sphinxcontrib-mermaid",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Myst
myst_enable_extensions = ["amsmath", "colon_fence", "dollarmath", "html_image"]
myst_fence_as_directive = ["mermaid"]

mermaid_params = ["-ppuppeteer-config.json"]
mermaid_d3_zoom = True
mermaid_fullscreen = True
mermaid_include_elk = True
mermaid_include_mindmap = True

toctree_base = """{toctree}
---
caption: ""
maxdepth: 2
hidden: true
---"""
toctree_root = f"""```{toctree_base}
```
"""


def run_copyreadme(_):
    out = Path("index.md")
    readme = Path("../README.md")
    out.write_text(toctree_root + "\n" + readme.read_text())


_GITHUB_ADMONITIONS = {
    "> [!NOTE]": "note",
    "> [!TIP]": "tip",
    "> [!IMPORTANT]": "important",
    "> [!WARNING]": "warning",
    "> [!CAUTION]": "caution",
}


def run_convert_github_admonitions_to_rst(app, filename, lines):
    # loop through lines, replace github admonitions
    for i, orig_line in enumerate(lines):
        orig_line_splits = orig_line.split("\n")
        replacing = False
        for j, line in enumerate(orig_line_splits):
            # look for admonition key
            for admonition_key in _GITHUB_ADMONITIONS:
                if admonition_key in line:
                    line = line.replace(admonition_key, ":::{" + _GITHUB_ADMONITIONS[admonition_key] + "}\n")
                    # start replacing quotes in subsequent lines
                    replacing = True
                    break
            else:
                # replace indent to match directive
                if replacing and "> " in line:
                    line = line.replace("> ", "  ")
                elif replacing:
                    # missing "> ", so stop replacing and terminate directive
                    line = f"\n:::\n{line}"
                    replacing = False
            # swap line back in splits
            orig_line_splits[j] = line
        # swap line back in original
        lines[i] = "\n".join(orig_line_splits)


def setup(app):
    app.connect("builder-inited", run_copyreadme)
    app.connect("source-read", run_convert_github_admonitions_to_rst)
