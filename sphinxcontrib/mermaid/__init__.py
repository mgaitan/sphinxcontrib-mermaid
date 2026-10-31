"""
sphinx-mermaid
~~~~~~~~~~~~~~~

Allow mermaid diagrams to be included in Sphinx-generated
documents inline.

:copyright: Copyright 2016-2025 by Martín Gaitán and others
:license: BSD, see LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx.application import Sphinx

from .config import register
from .directives import (
    Mermaid as Mermaid,
    MermaidClassDiagram as MermaidClassDiagram,
    align_spec as align_spec,
    figure_wrapper as figure_wrapper,
    mermaid as mermaid,
)
from .exceptions import MermaidError as MermaidError
from .html import add_assets, add_static_path, write_site_config
from .render import (
    html_visit_mermaid as html_visit_mermaid,
    latex_visit_mermaid as latex_visit_mermaid,
    man_visit_mermaid as man_visit_mermaid,
    render_mm as render_mm,
    render_mm_html as render_mm_html,
    render_mm_latex as render_mm_latex,
    render_mm_texinfo as render_mm_texinfo,
    texinfo_visit_mermaid as texinfo_visit_mermaid,
    text_visit_mermaid as text_visit_mermaid,
)

if TYPE_CHECKING:
    from sphinx.util.typing import ExtensionMetadata

__version__ = "2.1.1"


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_node(
        mermaid,
        html=(html_visit_mermaid, None),
        latex=(latex_visit_mermaid, None),
        texinfo=(texinfo_visit_mermaid, None),
        text=(text_visit_mermaid, None),
        man=(man_visit_mermaid, None),
    )
    app.add_directive("mermaid", Mermaid)
    app.add_directive("autoclasstree", MermaidClassDiagram)

    register(app)
    app.connect("builder-inited", add_static_path)
    app.connect("html-page-context", add_assets)
    app.connect("html-collect-pages", write_site_config)

    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}
