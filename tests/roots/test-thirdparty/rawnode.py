from docutils.parsers.rst import Directive

from sphinxcontrib.mermaid import mermaid


class RawNode(Directive):
    def run(self):
        node = mermaid()
        node["code"] = "graph TD\n  a --> b"
        return [node]


def setup(app):
    app.add_directive("rawnode", RawNode)
