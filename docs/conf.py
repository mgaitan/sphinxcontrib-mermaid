from sphinxcontrib.mermaid import __version__

project = "sphinxcontrib-mermaid"
copyright = "2017-2026, Martín Gaitán"
author = "Martín Gaitán"
version = release = __version__

extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinx.ext.imgconverter",
]
root_doc = "index"
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
exclude_patterns = ["_build", "html", "superpowers", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "sphinxcontrib-mermaid"

myst_enable_extensions = ["colon_fence"]
myst_fence_as_directive = ["mermaid"]
myst_heading_anchors = 3

mermaid_params = ["-ppuppeteer-config.json"]

latex_documents = [
    (root_doc, "sphinxcontrib-mermaid.tex", "sphinxcontrib-mermaid documentation", author, "manual"),
]
