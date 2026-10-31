extensions = ["sphinxcontrib.mermaid", "myst_parser"]
exclude_patterns = ["_build"]
source_suffix = {".md": "markdown"}
myst_fence_as_directive = ["mermaid"]


def _shift(app, docname, source):
    # Lines added by a source-read transform make the file's line numbers disagree with MyST's.
    source[0] = "\n\n\n\n\n" + source[0]


def setup(app):
    app.connect("source-read", _shift)
