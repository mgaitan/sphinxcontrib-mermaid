"""
    sphinx-mermaid
    ~~~~~~~~~~~~~~~

    Allow mermaid diagrams to be included in Sphinx-generated
    documents inline.

    :copyright: Copyright 2016-2023 by Martín Gaitán and others
    :license: BSD, see LICENSE for details.
"""
from __future__ import annotations

import codecs
import errno
import os
import posixpath
import re
from hashlib import sha1
from subprocess import PIPE, Popen
from tempfile import _get_default_tempdir
import uuid

import sphinx
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util import logging
from sphinx.util.i18n import search_image_for_language
from sphinx.util.osutil import ensuredir

from .autoclassdiag import class_diagram
from .exceptions import MermaidError

logger = logging.getLogger(__name__)

mapname_re = re.compile(r'<map id="(.*?)"')


class mermaid(nodes.General, nodes.Inline, nodes.Element):
    pass


def figure_wrapper(directive, node, caption):
    figure_node = nodes.figure("", node)
    if "align" in node:
        figure_node["align"] = node.attributes.pop("align")

    parsed = nodes.Element()
    directive.state.nested_parse(
        ViewList([caption], source=""), directive.content_offset, parsed
    )
    caption_node = nodes.caption(parsed[0].rawsource, "", *parsed[0].children)
    caption_node.source = parsed[0].source
    caption_node.line = parsed[0].line
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
    option_spec = {
        "alt": directives.unchanged,
        "align": align_spec,
        "caption": directives.unchanged,
        "zoom": directives.unchanged,
    }

    def get_mm_code(self):
        if self.arguments:
            # try to load mermaid code from an external file
            document = self.state.document
            if self.content:
                return [
                    document.reporter.warning(
                        "Mermaid directive cannot have both content and "
                        "a filename argument",
                        line=self.lineno,
                    )
                ]
            env = self.state.document.settings.env
            argument = search_image_for_language(self.arguments[0], env)
            rel_filename, filename = env.relfn2path(argument)
            env.note_dependency(rel_filename)
            try:
                with codecs.open(filename, "r", "utf-8") as fp:
                    mmcode = fp.read()
            except OSError:
                return [
                    document.reporter.warning(
                        "External Mermaid file %r not found or reading "
                        "it failed" % filename,
                        line=self.lineno,
                    )
                ]
        else:
            # inline mermaid code
            mmcode = "\n".join(self.content)
        return mmcode

    def run(self):
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

        # Wrap the mermaid code into a code node.
        node = mermaid()
        node["code"] = mmcode
        node["options"] = {}
        if "alt" in self.options:
            node["alt"] = self.options["alt"]
        if "align" in self.options:
            node["align"] = self.options["align"]
        if "inline" in self.options:
            node["inline"] = True
        if "zoom" in self.options:
            node["zoom"] = True
            node["zoom_id"] = f"id-{uuid.uuid4()}"

        caption = self.options.get("caption")
        if caption:
            node = figure_wrapper(self, node, caption)

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


def render_mm(self, code, options, _fmt, prefix="mermaid"):
    """Render mermaid code into a PNG or PDF output file."""

    if _fmt == "raw":
        _fmt = "png"

    mermaid_cmd = self.builder.config.mermaid_cmd
    mermaid_cmd_shell = self.builder.config.mermaid_cmd_shell in {True, "True", "true"}
    hashkey = (
        code + str(options) + str(self.builder.config.mermaid_sequence_config)
    ).encode("utf-8")

    basename = f"{prefix}-{sha1(hashkey).hexdigest()}"
    fname = f"{basename}.{_fmt}"
    relfn = posixpath.join(self.builder.imgpath, fname)
    outdir = os.path.join(self.builder.outdir, self.builder.imagedir)
    outfn = os.path.join(outdir, fname)
    tmpfn = os.path.join(_get_default_tempdir(), basename)

    if os.path.isfile(outfn):
        return relfn, outfn

    ensuredir(os.path.dirname(outfn))

    with open(tmpfn, "w") as t:
        t.write(code)

    mm_args = [mermaid_cmd, "-i", tmpfn, "-o", outfn]
    mm_args.extend(self.builder.config.mermaid_params)
    if self.builder.config.mermaid_sequence_config:
        mm_args.extend("--configFile", self.builder.config.mermaid_sequence_config)

    try:
        p = Popen(
            mm_args, shell=mermaid_cmd_shell, stdout=PIPE, stdin=PIPE, stderr=PIPE
        )
    except FileNotFoundError:
        logger.warning(
            "command %r cannot be run (needed for mermaid "
            "output), check the mermaid_cmd setting" % mermaid_cmd
        )
        return None, None

    stdout, stderr = p.communicate(str.encode(code))
    if self.builder.config.mermaid_verbose:
        logger.info(stdout)

    if p.returncode != 0:
        raise MermaidError(
            "Mermaid exited with error:\n[stderr]\n%s\n"
            "[stdout]\n%s" % (stderr, stdout)
        )
    if not os.path.isfile(outfn):
        raise MermaidError(
            "Mermaid did not produce an output file:\n[stderr]\n%s\n"
            "[stdout]\n%s" % (stderr, stdout)
        )
    return relfn, outfn


def _render_mm_html_raw(
    self, node, code, options, prefix="mermaid", imgcls=None, alt=None
):
    if "align" in node and "zoom_id" in node:
        tag_template = """<div align="{align}" id="{zoom_id}" class="mermaid align-{align}">
            {code}
        </div>
        """
    elif "align" in node and "zoom_id" not in node:
        tag_template = """<div align="{align}" class="mermaid align-{align}">
            {code}
        </div>
        """
    elif "align" not in node and "zoom_id" in node:
        tag_template = """<div id="{zoom_id}" class="mermaid">
            {code}
        </div>
        """
    else:
        tag_template = """<div class="mermaid">
            {code}
        </div>"""

    self.body.append(
        tag_template.format(align=node.get("align"), zoom_id=node.get("zoom_id"), code=self.encode(code))
    )
    raise nodes.SkipNode


def render_mm_html(self, node, code, options, prefix="mermaid", imgcls=None, alt=None):

    _fmt = self.builder.config.mermaid_output_format
    if _fmt == "raw":
        return _render_mm_html_raw(
            self, node, code, options, prefix="mermaid", imgcls=None, alt=None
        )

    try:
        if _fmt not in ("png", "svg"):
            raise MermaidError(
                "mermaid_output_format must be one of 'raw', 'png', "
                "'svg', but is %r" % _fmt
            )

        fname, outfn = render_mm(self, code, options, _fmt, prefix)
    except MermaidError as exc:
        logger.warning(f"mermaid code {code!r}: " + str(exc))
        raise nodes.SkipNode

    if fname is None:
        self.body.append(self.encode(code))
    else:
        if alt is None:
            alt = node.get("alt", self.encode(code).strip())
        imgcss = imgcls and f'class="{imgcls}"' or ""
        if _fmt == "svg":
            svgtag = f"""<object data="{fname}" type="image/svg+xml">
            <p class="warning">{alt}</p></object>
"""
            self.body.append(svgtag)
        else:
            if "align" in node:
                self.body.append(
                    '<div align="%s" class="align-%s">' % (node["align"], node["align"])
                )

            self.body.append(f'<img src="{fname}" alt="{alt}" {imgcss}/>\n')
            if "align" in node:
                self.body.append("</div>\n")

    raise nodes.SkipNode


def html_visit_mermaid(self, node):
    render_mm_html(self, node, node["code"], node["options"])


def render_mm_latex(self, node, code, options, prefix="mermaid"):
    try:
        fname, outfn = render_mm(self, code, options, "pdf", prefix)
    except MermaidError as exc:
        logger.warning(f"mm code {code!r}: " + str(exc))
        raise nodes.SkipNode

    if self.builder.config.mermaid_pdfcrop != "":
        mm_args = [self.builder.config.mermaid_pdfcrop, outfn]
        try:
            p = Popen(mm_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        except OSError as err:
            if err.errno != errno.ENOENT:   # No such file or directory
                raise
            logger.warning(
                f"command {self.builder.config.mermaid_pdfcrop!r} cannot be run (needed to crop pdf), check the mermaid_cmd setting"
            )
            return None, None

        stdout, stderr = p.communicate()
        if self.builder.config.mermaid_verbose:
            logger.info(stdout)

        if p.returncode != 0:
            raise MermaidError(
                "PdfCrop exited with error:\n[stderr]\n%s\n"
                "[stdout]\n%s" % (stderr, stdout)
            )
        if not os.path.isfile(outfn):
            raise MermaidError(
                "PdfCrop did not produce an output file:\n[stderr]\n%s\n"
                "[stdout]\n%s" % (stderr, stdout)
            )

        fname = "{filename[0]}-crop{filename[1]}".format(
            filename=os.path.splitext(fname)
        )

    is_inline = self.is_inline(node)
    if is_inline:
        para_separator = ""
    else:
        para_separator = "\n"

    if fname is not None:
        post = None
        if not is_inline and "align" in node:
            if node["align"] == "left":
                self.body.append("{")
                post = "\\hspace*{\\fill}}"
            elif node["align"] == "right":
                self.body.append("{\\hspace*{\\fill}")
                post = "}"
        self.body.append(
            "%s\\sphinxincludegraphics{%s}%s" % (para_separator, fname, para_separator)
        )
        if post:
            self.body.append(post)

    raise nodes.SkipNode


def latex_visit_mermaid(self, node):
    render_mm_latex(self, node, node["code"], node["options"])


def render_mm_texinfo(self, node, code, options, prefix="mermaid"):
    try:
        fname, outfn = render_mm(self, code, options, "png", prefix)
    except MermaidError as exc:
        logger.warning(f"mm code {code!r}: " + str(exc))
        raise nodes.SkipNode
    if fname is not None:
        self.body.append("@image{%s,,,[mermaid],png}\n" % fname[:-4])
    raise nodes.SkipNode


def texinfo_visit_mermaid(self, node):
    render_mm_texinfo(self, node, node["code"], node["options"])


def text_visit_mermaid(self, node):
    if "alt" in node.attributes:
        self.add_text(_("[graph: %s]") % node["alt"])
    else:
        self.add_text(_("[graph]"))
    raise nodes.SkipNode


def man_visit_mermaid(self, node):
    if "alt" in node.attributes:
        self.body.append(_("[graph: %s]") % node["alt"])
    else:
        self.body.append(_("[graph]"))
    raise nodes.SkipNode


def install_js(
    app: Sphinx,
    pagename,
    templatename: str,
    context: dict,
    doctree: nodes.document | None,
) -> None:
    # Skip for pages without Mermaid diagrams
    if doctree and not doctree.next_node(mermaid):
        return

    # Add required JavaScript
    if not app.config.mermaid_version:
        _mermaid_js_url = None  # assume it is local
    elif app.config.mermaid_version == "latest":
        _mermaid_js_url = "https://unpkg.com/mermaid/dist/mermaid.min.js"
    else:
        _mermaid_js_url = f"https://unpkg.com/mermaid@{app.config.mermaid_version}/dist/mermaid.min.js"
    if _mermaid_js_url:
        app.add_js_file(_mermaid_js_url, priority=app.config.mermaid_js_priority)

    if app.config.mermaid_init_js:
        # If mermaid is local the init-call must be placed after `html_js_files` which has a priority of 800.
        priority = (
            app.config.mermaid_init_js_priority if _mermaid_js_url is not None else 801
        )
        app.add_js_file(None, body=app.config.mermaid_init_js, priority=priority)

    if app.config.mermaid_output_format == "raw":
        if app.config.mermaid_d3_zoom:
            _d3_js_url = "https://unpkg.com/d3/dist/d3.min.js"
            _d3_js_script = """
            window.addEventListener("load", function () {
              var svgs = d3.selectAll(".mermaid svg");
              svgs.each(function() {
                var svg = d3.select(this);
                svg.html("<g>" + svg.html() + "</g>");
                var inner = svg.select("g");
                var zoom = d3.zoom().on("zoom", function(event) {
                  inner.attr("transform", event.transform);
                });
                svg.call(zoom);
              });
            });
            """
            app.add_js_file(_d3_js_url, priority=app.config.mermaid_js_priority)
            app.add_js_file(None, body=_d3_js_script, priority=app.config.mermaid_js_priority)
        elif doctree:
            mermaid_nodes = doctree.findall(mermaid)
            _d3_selector = ""
            for mermaid_node in mermaid_nodes:
                if "zoom_id" in mermaid_node:
                    _zoom_id = mermaid_node["zoom_id"]
                    if _d3_selector == "":
                        _d3_selector += f".mermaid#{_zoom_id} svg"
                    else:
                        _d3_selector += f", .mermaid#{_zoom_id} svg"
            if _d3_selector != "":
                _d3_js_url = "https://unpkg.com/d3/dist/d3.min.js"
                _d3_js_script = f"""
                window.addEventListener("load", function () {{
                  var svgs = d3.selectAll("{_d3_selector}");
                  svgs.each(function() {{
                    var svg = d3.select(this);
                    svg.html("<g>" + svg.html() + "</g>");
                    var inner = svg.select("g");
                    var zoom = d3.zoom().on("zoom", function(event) {{
                      inner.attr("transform", event.transform);
                    }});
                    svg.call(zoom);
                  }});
                }});
                """
                app.add_js_file(_d3_js_url, priority=app.config.mermaid_js_priority)
                app.add_js_file(None, body=_d3_js_script, priority=app.config.mermaid_js_priority)


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

    app.add_config_value("mermaid_cmd", "mmdc", "html")
    app.add_config_value("mermaid_cmd_shell", "False", "html")
    app.add_config_value("mermaid_pdfcrop", "", "html")
    app.add_config_value("mermaid_output_format", "raw", "html")
    app.add_config_value("mermaid_params", list(), "html")
    app.add_config_value("mermaid_verbose", False, "html")
    app.add_config_value("mermaid_sequence_config", False, "html")
    
    # Starting in version 10, mermaid is an "ESM only" package
    # thus it requires a different initialization code not yet supported. 
    # So the current latest version supported is this
    # Discussion: https://github.com/mermaid-js/mermaid/discussions/4148
    app.add_config_value("mermaid_version", "10.2.0", "html")
    app.add_config_value("mermaid_js_priority", 500, "html")
    app.add_config_value("mermaid_init_js_priority", 500, "html")
    app.add_config_value(
        "mermaid_init_js", "mermaid.initialize({startOnLoad:true});", "html"
    )
    app.add_config_value("mermaid_d3_zoom", False, "html")
    app.connect("html-page-context", install_js)

    return {"version": sphinx.__display_version__, "parallel_read_safe": True}
