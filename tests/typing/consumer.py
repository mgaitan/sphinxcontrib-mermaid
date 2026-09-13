from collections.abc import Callable, Iterator
from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata
from sphinx.writers.html5 import HTML5Translator
from typing_extensions import assert_type

from sphinxcontrib.mermaid import (
    Mermaid,
    MermaidClassDiagram,
    MermaidError,
    class_diagram,
    html_visit_mermaid,
    mermaid,
    setup,
)
from sphinxcontrib.mermaid.autoclassdiag import get_classes


class CustomMermaid(mermaid):
    pass


node = mermaid("", nodes.Text("diagram"), ids=["diagram"])
assert_type(node, mermaid)
assert_type(node.deepcopy(), mermaid)
element: nodes.Element = node
node["code"] = "graph TD; A-->B"
node["options"] = {}
custom: nodes.Element = CustomMermaid()
visitor: Callable[[HTML5Translator, mermaid], None] = html_visit_mermaid
setup_extension: Callable[[Sphinx], ExtensionMetadata] = setup
error: Exception = MermaidError("invalid diagram")
diagram: str = class_diagram("example.Child", full=True, strict=True, namespace="example")
classes: Iterator[type[Any]] = get_classes("example", strict=True)


def use_directives(directive: Mermaid, class_directive: MermaidClassDiagram) -> None:
    assert_type(directive.get_mm_code(), str | list[nodes.Node])
    assert_type(directive.run(), list[nodes.Node])
    assert_type(class_directive.get_mm_code(), str)
    code: str | list[nodes.Node] = directive.get_mm_code()
    result: list[nodes.Node] = directive.run()
    class_code: str = class_directive.get_mm_code()
    # Pass results to typed functions so these assignments remain checked.
    print(code, result, class_code)
