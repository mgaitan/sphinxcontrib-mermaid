"""Static output through mermaid-cli for LaTeX, texinfo, PNG and SVG."""

from __future__ import annotations

import errno
import json
import os
import posixpath
import re
import shlex
from hashlib import sha1
from pathlib import Path
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory

from docutils import nodes
from sphinx.locale import _
from sphinx.util import logging
from sphinx.util.osutil import ensuredir

from .exceptions import MermaidError
from .html import render_raw
from .options import deep_merge

logger = logging.getLogger(__name__)

mapname_re = re.compile(r'<map id="(.*?)"')


def _mmdc_config(config) -> dict:
    """``mermaid_config`` merged over ``mermaid_sequence_config``, for mmdc's ``--configFile``."""
    if not config.mermaid_config:
        return {}
    base = {}
    if config.mermaid_sequence_config:
        base = json.loads(Path(config.mermaid_sequence_config).read_text(encoding="utf-8"))
    return deep_merge(base, config.mermaid_config)


def _size_style(node) -> str:
    options = node.get("options", {})
    style = "; ".join(f"{key}: {options[key]}" for key in ("width", "height") if options.get(key))
    return f' style="{style}"' if style else ""


def render_mm(self, code, options, _fmt, prefix="mermaid"):
    """Render mermaid code into a PNG or PDF output file."""

    if _fmt == "raw":
        _fmt = "png"

    mermaid_cmd = self.builder.config.mermaid_cmd
    mermaid_cmd_shell = self.builder.config.mermaid_cmd_shell in {True, "True", "true"}
    mm_config = _mmdc_config(self.builder.config)
    hashkey = (code + str(options) + str(self.builder.config.mermaid_sequence_config) + json.dumps(mm_config, sort_keys=True)).encode("utf-8")

    basename = f"{prefix}-{sha1(hashkey).hexdigest()}"
    fname = f"{basename}.{_fmt}"
    relfn = posixpath.join(self.builder.imgpath, fname)
    outdir = os.path.join(self.builder.outdir, self.builder.imagedir)
    outfn = os.path.join(outdir, fname)
    with TemporaryDirectory() as tempDir:
        tmpfn = os.path.join(tempDir, basename)

        if os.path.isfile(outfn):
            return relfn, outfn

        ensuredir(os.path.dirname(outfn))

        with open(tmpfn, "w", encoding="utf-8") as t:
            t.write(code)

        if isinstance(mermaid_cmd, str):
            mm_args = shlex.split(mermaid_cmd)
        else:
            mm_args = list(mermaid_cmd)

        mm_args.extend(self.builder.config.mermaid_params)
        mm_args += ["-i", tmpfn, "-o", outfn]
        if self.builder.config.mermaid_config:
            config_file = os.path.join(tempDir, "mermaid-config.json")
            Path(config_file).write_text(json.dumps(mm_config), encoding="utf-8")
            mm_args.extend(["--configFile", config_file])
        elif self.builder.config.mermaid_sequence_config:
            mm_args.extend(["--configFile", self.builder.config.mermaid_sequence_config])

        try:
            p = Popen(mm_args, shell=mermaid_cmd_shell, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
        except FileNotFoundError:
            logger.warning(f"command {mermaid_cmd!r} cannot be run (needed for mermaid output), check the mermaid_cmd setting")
            return None, None

        stdout, stderr = p.communicate(code)
        if self.builder.config.mermaid_verbose:
            logger.info(stdout)

        if p.returncode != 0:
            raise MermaidError(f"Mermaid exited with error:\n[stderr]\n{stderr}\n[stdout]\n{stdout}")
        if not os.path.isfile(outfn):
            raise MermaidError(f"Mermaid did not produce an output file:\n[stderr]\n{stderr}\n[stdout]\n{stdout}")
        return relfn, outfn


def render_mm_html(self, node, code, options, prefix="mermaid", imgcls=None, alt=None):
    _fmt = self.builder.config.mermaid_output_format
    if _fmt == "raw":
        return render_raw(self, node, code)

    try:
        if _fmt not in ("png", "svg"):
            raise MermaidError(f"mermaid_output_format must be one of 'raw', 'png', 'svg', but is {_fmt!r}")

        fname, _outfn = render_mm(self, code, options, _fmt, prefix)
    except MermaidError as exc:
        logger.warning(f"mermaid code {code!r}: " + str(exc))
        raise nodes.SkipNode

    if fname is None:
        self.body.append(self.encode(code))
    else:
        if alt is None:
            alt = self.attval(node["alt"]) if "alt" in node else self.encode(code).strip()
        imgcss = imgcls and f'class="{imgcls}"' or ""
        if _fmt == "svg":
            svgtag = f"""<object data="{fname}" type="image/svg+xml"{_size_style(node)}>
            <p class="warning">{alt}</p></object>
"""
            self.body.append(svgtag)
        else:
            if "align" in node:
                self.body.append(f'<pre align="{node["align"]}" class="align-{node["align"]}">')

            self.body.append(f'<img src="{fname}" alt="{alt}" {imgcss}{_size_style(node)}/>\n')
            if "align" in node:
                self.body.append("</pre>\n")

    raise nodes.SkipNode


def html_visit_mermaid(self, node):
    render_mm_html(self, node, node["code"], node.get("options", {}), imgcls="mermaid")


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
            if err.errno != errno.ENOENT:  # No such file or directory
                raise
            logger.warning(f"command {self.builder.config.mermaid_pdfcrop!r} cannot be run (needed to crop pdf), check the mermaid_cmd setting")
            return None, None

        stdout, stderr = p.communicate()
        if self.builder.config.mermaid_verbose:
            logger.info(stdout)

        if p.returncode != 0:
            raise MermaidError(f"PdfCrop exited with error:\n[stderr]\n{stderr}\n[stdout]\n{stdout}")
        if not os.path.isfile(outfn):
            raise MermaidError(f"PdfCrop did not produce an output file:\n[stderr]\n{stderr}\n[stdout]\n{stdout}")

        fname = "{filename[0]}-crop{filename[1]}".format(filename=os.path.splitext(fname))

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
        self.body.append(f"{para_separator}\\sphinxincludegraphics{{{fname}}}{para_separator}")
        if post:
            self.body.append(post)

    raise nodes.SkipNode


def latex_visit_mermaid(self, node):
    render_mm_latex(self, node, node["code"], node.get("options", {}))


def render_mm_texinfo(self, node, code, options, prefix="mermaid"):
    try:
        fname, _outfn = render_mm(self, code, options, "png", prefix)
    except MermaidError as exc:
        logger.warning(f"mm code {code!r}: " + str(exc))
        raise nodes.SkipNode
    if fname is not None:
        self.body.append(f"@image{{{fname[:-4]},,,[mermaid],png}}\n")
    raise nodes.SkipNode


def texinfo_visit_mermaid(self, node):
    render_mm_texinfo(self, node, node["code"], node.get("options", {}))


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
