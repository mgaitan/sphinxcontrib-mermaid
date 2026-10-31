"""The ``mermaid`` and ``autoclasstree`` directives."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList
from sphinx.util import logging
from sphinx.util.i18n import search_image_for_language
from sphinx.util.nodes import set_source_info

from .autoclassdiag import class_diagram
from .options import SPHINX_KEYS, build_source, deep_merge, parse_config, split_frontmatter, validate_sphinx_options

logger = logging.getLogger(__name__)

_FENCE = re.compile(r"[ \t>]*(`{3,}|~{3,}|:{3,})")


def _fence_frontmatter(lines, i, content):
    """Return the dedented ``---`` block of the fence opening at ``lines[i]``, if its body matches ``content``."""
    if not 0 <= i < len(lines):
        return None
    match = _FENCE.match(lines[i])
    if not match:
        return None
    # Blockquote markers and list indentation before the fence prefix every line of it.
    prefix = lines[i][: match.start(1)]

    def unprefix(line):
        return line[len(prefix) :] if line.startswith(prefix) else line.lstrip(" \t>")

    body = [unprefix(line) for line in lines[i + 1 :]]
    if not body or body[0].strip() != "---":
        return None
    end = next((j for j in range(1, len(body)) if body[j].strip() == "---"), None)
    if end is None:
        return None
    first = next((line for line in content if line.strip()), None)
    after = next((line for line in body[end + 1 :] if line.strip()), None)
    if first is not None and (after is None or after.strip() != first.strip()):
        return None
    return textwrap.dedent("\n".join(body[1:end]))


class mermaid(nodes.General, nodes.Inline, nodes.Element):
    pass


def figure_wrapper(directive, node, caption):
    figure_node = nodes.figure("", node)
    if "align" in node:
        figure_node["align"] = node.attributes.pop("align")

    parsed = nodes.Element()
    directive.state.nested_parse(ViewList([caption], source=""), directive.content_offset, parsed)
    caption_node = nodes.caption(parsed[0].rawsource, "", *parsed[0].children)
    set_source_info(directive, caption_node)
    figure_node += caption_node
    return figure_node


def align_spec(argument):
    return directives.choice(argument, ("left", "center", "right"))


class Mermaid(Directive):
    """
    Directive to insert arbitrary Mermaid markup.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012 - Docutils defines directive options on the class.
        # Sphinx directives
        "name": directives.unchanged,
        "class": directives.class_option,
        "alt": directives.unchanged,
        "align": align_spec,
        "caption": directives.unchanged,
        # Sizing and interaction
        "width": directives.unchanged,
        "height": directives.unchanged,
        "fit": directives.unchanged,
        "zoom": directives.unchanged,
        "fullscreen": directives.unchanged,
        # Mermaid frontmatter
        "config": directives.unchanged,
        "title": directives.unchanged,
        "displayMode": directives.unchanged,
    }

    def get_mm_code(self):
        if self.arguments:
            # try to load mermaid code from an external file
            document = self.state.document
            if self.content:
                return [
                    document.reporter.warning(
                        "Mermaid directive cannot have both content and a filename argument",
                        line=self.lineno,
                    )
                ]
            env = self.state.document.settings.env
            argument = search_image_for_language(self.arguments[0], env)
            rel_filename, filename = env.relfn2path(argument)
            env.note_dependency(rel_filename)
            try:
                mmcode = Path(filename).read_text(encoding="utf-8")
            except OSError:
                return [
                    document.reporter.warning(
                        f"External Mermaid file {filename!r} not found or reading it failed",
                        line=self.lineno,
                    )
                ]
        else:
            # inline mermaid code
            mmcode = "\n".join(self.content)
        return mmcode

    def _warn(self, message):
        logger.warning(f"mermaid: {message}", location=(self.state.document.settings.env.docname, self.lineno))

    def _myst_raw_frontmatter(self):
        """Re-read a MyST fence's ``---`` block, which MyST flattens into options."""
        if type(self.state_machine).__name__ != "MockStateMachine":
            return None
        try:
            lines = Path(self.state.document["source"]).read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        # MyST's line number can be one off (e.g. inside {include}); confirm by matching the body.
        for i in (self.lineno - 1, self.lineno - 2, self.lineno):
            block = _fence_frontmatter(lines, i, self.content)
            if block is not None:
                try:
                    return split_frontmatter("---\n" + block + "\n---\n")[0]
                except ValueError:
                    return None
        if "config" in self.options:
            try:
                parse_config(self.options["config"])
            except ValueError:
                self._warn("nested YAML in MyST directive options is flattened; use single-line JSON for config")
        return None

    def _sphinx_options(self, raw):
        try:
            return validate_sphinx_options(raw)
        except ValueError as exc:
            self._warn(str(exc))
        # Validate key by key so one bad value does not drop the others.
        result = {}
        for key in SPHINX_KEYS:
            if key in raw:
                try:
                    result.update(validate_sphinx_options({key: raw[key]}))
                except ValueError:
                    pass
        return result

    def run(self, **kwargs):
        mmcode = self.get_mm_code()
        # mmcode is a list, so it's a system message, not content to be included in the
        # document.
        if not isinstance(mmcode, str):
            return mmcode

        # if mmcode is empty, ignore the directive.
        if not mmcode.strip():
            return [
                self.state_machine.reporter.warning(
                    'Ignoring "mermaid" directive without content.',
                    line=self.lineno,
                )
            ]

        try:
            frontmatter, body = split_frontmatter(mmcode)
        except ValueError as exc:
            self._warn(str(exc))
            frontmatter, body = {}, mmcode

        options = dict(self.options)
        recovered = self._myst_raw_frontmatter()
        if recovered is not None:
            # MyST consumed the fence's frontmatter as directive options
            options = {key: value for key, value in options.items() if key not in recovered}
            frontmatter = deep_merge(recovered, frontmatter)

        node = mermaid()
        node["options"] = self._sphinx_options(
            {**{k: v for k, v in frontmatter.items() if k in SPHINX_KEYS}, **{k: v for k, v in options.items() if k in SPHINX_KEYS}}
        )
        meta = {k: v for k, v in frontmatter.items() if k not in SPHINX_KEYS and k not in ("align", "alt", "caption", "name", "class")}
        if "config" in options:
            try:
                meta["config"] = deep_merge(parse_config(meta.get("config") or {}), parse_config(options["config"]))
            except ValueError as exc:
                self._warn(str(exc))
        for key in ("title", "displayMode"):
            if key in options:
                meta[key] = options[key]
        node["code"] = build_source(meta, body)

        # Sphinx directives
        for key in ("alt", "align", "caption", "name"):
            if key not in options and key in frontmatter:
                options[key] = str(frontmatter[key])
        if "alt" in options:
            node["alt"] = options["alt"]
        if "align" in options:
            try:
                node["align"] = align_spec(options["align"])
            except ValueError as exc:
                self._warn(f"invalid align: {exc}")
        classes = options.get("class")
        if classes is None and "class" in frontmatter:
            fm_class = frontmatter["class"]
            classes = directives.class_option(" ".join(fm_class) if isinstance(fm_class, list) else str(fm_class))
        node["classes"] += classes or []

        caption = options.get("caption")
        if caption is not None:
            node = figure_wrapper(self, node, caption)

        if "name" in options:
            self.options["name"] = options["name"]
        self.add_name(node)
        return [node]


class MermaidClassDiagram(Mermaid):
    has_content = False
    required_arguments = 1
    optional_arguments = 100
    option_spec = Mermaid.option_spec.copy()
    option_spec.update(
        {
            "full": directives.flag,
            "namespace": directives.unchanged,
            "strict": directives.flag,
        }
    )

    def get_mm_code(self):
        return class_diagram(
            *self.arguments,
            full="full" in self.options,
            strict="strict" in self.options,
            namespace=self.options.get("namespace"),
        )
