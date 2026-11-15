import sys
from pathlib import Path

from docutils import nodes

sys.path.insert(0, str(Path(__file__).parent))

extensions = ["sphinxcontrib.mermaid", "sphinx.ext.autodoc"]
exclude_patterns = ["_build"]


def fake_intersphinx(app, env, node, contnode):
    if node["reftarget"].startswith("builtins."):
        return nodes.reference("", "", contnode, refuri=f"https://docs.python.org/3/library/exceptions.html#{node['reftarget'][9:]}")
    return None


def setup(app):
    app.connect("missing-reference", fake_intersphinx)
