"""
sphinx-mermaid
~~~~~~~~~~~~~~~

Allow mermaid diagrams to be included in Sphinx-generated
documents inline.

:copyright: Copyright 2016-2025 by Martín Gaitán and others
:license: BSD, see LICENSE for details.
"""

from __future__ import annotations

from .config import register
from .directives import Mermaid, MermaidClassDiagram, align_spec, figure_wrapper, mermaid
from .exceptions import MermaidError
from .html import add_assets, add_static_path, write_site_config
from .render import (
    html_visit_mermaid,
    latex_visit_mermaid,
    man_visit_mermaid,
    render_mm,
    render_mm_html,
    render_mm_latex,
    render_mm_texinfo,
    texinfo_visit_mermaid,
    text_visit_mermaid,
)

__version__ = "2.1.1"


def setup(app):
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
