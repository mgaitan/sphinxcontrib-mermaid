# -*- coding: utf-8 -*-
"""
    sphinx-mermaid
    ~~~~~~~~~~~~~~~

    Allow mermaid diagramas to be included in Sphinx-generated
    documents inline.

    :copyright: Copyright 2016 by Martín Gaitán and others, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re
import codecs
import posixpath
import json
from os import path
from subprocess import Popen, PIPE
from hashlib import sha1
from tempfile import _get_default_tempdir, NamedTemporaryFile

from six import text_type
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList

import sphinx
from sphinx.errors import SphinxError
from sphinx.locale import _
from sphinx.util.i18n import search_image_for_language
from sphinx.util.osutil import ensuredir, ENOENT
from sphinx.util.compat import Directive


mapname_re = re.compile(r'<map id="(.*?)"')


class MermaidError(SphinxError):
    category = 'Mermaid error'


class mermaid(nodes.General, nodes.Inline, nodes.Element):
    pass


def figure_wrapper(directive, node, caption):
    figure_node = nodes.figure('', node)
    if 'align' in node:
        figure_node['align'] = node.attributes.pop('align')

    parsed = nodes.Element()
    directive.state.nested_parse(ViewList([caption], source=''),
                                 directive.content_offset, parsed)
    caption_node = nodes.caption(parsed[0].rawsource, '',
                                 *parsed[0].children)
    caption_node.source = parsed[0].source
    caption_node.line = parsed[0].line
    figure_node += caption_node
    return figure_node


def align_spec(argument):
    return directives.choice(argument, ('left', 'center', 'right'))


class Mermaid(Directive):
    """
    Directive to insert arbitrary Mermaid markup.
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'alt': directives.unchanged,
        'align': align_spec,
        'caption': directives.unchanged,
    }

    def run(self):
        if self.arguments:
            document = self.state.document
            if self.content:
                return [document.reporter.warning(
                    'Mermaid directive cannot have both content and '
                    'a filename argument', line=self.lineno)]
            env = self.state.document.settings.env
            argument = search_image_for_language(self.arguments[0], env)
            rel_filename, filename = env.relfn2path(argument)
            env.note_dependency(rel_filename)
            try:
                with codecs.open(filename, 'r', 'utf-8') as fp:
                    mmcode = fp.read()
            except (IOError, OSError):
                return [document.reporter.warning(
                    'External Mermaid file %r not found or reading '
                    'it failed' % filename, line=self.lineno)]
        else:
            mmcode = '\n'.join(self.content)
            if not mmcode.strip():
                return [self.state_machine.reporter.warning(
                    'Ignoring "mermaid" directive without content.',
                    line=self.lineno)]
        node = mermaid()
        node['code'] = mmcode
        node['options'] = {}
        if 'alt' in self.options:
            node['alt'] = self.options['alt']
        if 'align' in self.options:
            node['align'] = self.options['align']
        if 'inline' in self.options:
            node['inline'] = True

        caption = self.options.get('caption')
        if caption:
            node = figure_wrapper(self, node, caption)

        return [node]


def render_mm(self, code, options, format, prefix='mermaid'):
    """Render mermaid code into a PNG or PDF output file."""
    mermaid_cmd = self.builder.config.mermaid_cmd
    verbose = self.builder.config.mermaid_verbose
    hashkey = (code + str(options) +
               str(self.builder.config.mermaid_sequence_config)).encode('utf-8')

    basename = '%s-%s' % (prefix, sha1(hashkey).hexdigest())
    fname = '%s.%s' % (basename, format)
    relfn = posixpath.join(self.builder.imgpath, fname)
    outdir = path.join(self.builder.outdir, self.builder.imagedir)
    outfn = path.join(outdir, fname)
    tmpfn = path.join(_get_default_tempdir(), basename)

    if path.isfile(outfn):
        return relfn, outfn

    ensuredir(path.dirname(outfn))

    # mermaid expects UTF-8 by default
    if isinstance(code, text_type):
        code = code.encode('utf-8')

    with open(tmpfn, 'w') as t:
        t.write(code)

    mm_args = [mermaid_cmd, tmpfn, '-o', outdir]
    if verbose:
        mm_args.extend(['-v'])
    if self.builder.config.mermaid_phantom_path:
        mm_args.extend(['--phantomPath', self.builder.config.mermaid_phantom_path])
    if self.builder.config.mermaid_sequence_config:
        with NamedTemporaryFile(delete=False) as seq:
            json.dump(self.builder.config.mermaid_sequence_config, seq)
        mm_args.extend(['--sequenceConfig', seq.name])
    if format == 'png':
        mm_args.extend(['-p'])
    else:
        mm_args.extend(['-s'])
        self.builder.warn('Mermaid SVG support is experimental')
    try:
        p = Popen(mm_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    except OSError as err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('command %r cannot be run (needed for mermaid '
                          'output), check the mermaid_cmd setting' % mermaid_cmd)
        return None, None

    stdout, stderr = p.communicate(code)
    if verbose:
        self.builder.info(stdout)

    if p.returncode != 0:
        raise MermaidError('Mermaid exited with error:\n[stderr]\n%s\n'
                            '[stdout]\n%s' % (stderr, stdout))
    if not path.isfile(outfn):
        raise MermaidError('Mermaid did not produce an output file:\n[stderr]\n%s\n'
                            '[stdout]\n%s' % (stderr, stdout))
    return relfn, outfn


def render_mm_html(self, node, code, options, prefix='mermaid',
                    imgcls=None, alt=None):
    format = self.builder.config.mermaid_output_format
    try:
        if format not in ('png', 'svg'):
            raise MermaidError("mermaid_output_format must be one of 'png', "
                                "'svg', but is %r" % format)
        fname, outfn = render_mm(self, code, options, format, prefix)
    except MermaidError as exc:
        self.builder.warn('mermaid code %r: ' % code + str(exc))
        raise nodes.SkipNode

    if fname is None:
        self.body.append(self.encode(code))
    else:
        if alt is None:
            alt = node.get('alt', self.encode(code).strip())
        imgcss = imgcls and 'class="%s"' % imgcls or ''
        if format == 'svg':
            svgtag = '''<object data="%s" type="image/svg+xml">
            <p class="warning">%s</p></object>\n''' % (fname, alt)
            self.body.append(svgtag)
        else:
            if 'align' in node:
                self.body.append('<div align="%s" class="align-%s">' %
                                 (node['align'], node['align']))
            # nothing in image map (the lines are <map> and </map>)
            self.body.append('<img src="%s" alt="%s" %s/>\n' %
                             (fname, alt, imgcss))
            if 'align' in node:
                self.body.append('</div>\n')

    raise nodes.SkipNode


def html_visit_mermaid(self, node):
    render_mm_html(self, node, node['code'], node['options'])


def render_mm_latex(self, node, code, options, prefix='mermaid'):
    try:
        fname, outfn = render_mm(self, code, options, 'pdf', prefix)
    except MermaidError as exc:
        self.builder.warn('mm code %r: ' % code + str(exc))
        raise nodes.SkipNode

    is_inline = self.is_inline(node)
    if is_inline:
        para_separator = ''
    else:
        para_separator = '\n'

    if fname is not None:
        post = None
        if not is_inline and 'align' in node:
            if node['align'] == 'left':
                self.body.append('{')
                post = '\\hspace*{\\fill}}'
            elif node['align'] == 'right':
                self.body.append('{\\hspace*{\\fill}')
                post = '}'
        self.body.append('%s\\includegraphics{%s}%s' %
                         (para_separator, fname, para_separator))
        if post:
            self.body.append(post)

    raise nodes.SkipNode


def latex_visit_mermaid(self, node):
    render_mm_latex(self, node, node['code'], node['options'])


def render_mm_texinfo(self, node, code, options, prefix='mermaid'):
    try:
        fname, outfn = render_mm(self, code, options, 'png', prefix)
    except MermaidError as exc:
        self.builder.warn('mm code %r: ' % code + str(exc))
        raise nodes.SkipNode
    if fname is not None:
        self.body.append('@image{%s,,,[mermaid],png}\n' % fname[:-4])
    raise nodes.SkipNode


def texinfo_visit_mermaid(self, node):
    render_mm_texinfo(self, node, node['code'], node['options'])


def text_visit_mermaid(self, node):
    if 'alt' in node.attributes:
        self.add_text(_('[graph: %s]') % node['alt'])
    else:
        self.add_text(_('[graph]'))
    raise nodes.SkipNode


def man_visit_mermaid(self, node):
    if 'alt' in node.attributes:
        self.body.append(_('[graph: %s]') % node['alt'])
    else:
        self.body.append(_('[graph]'))
    raise nodes.SkipNode


def setup(app):
    app.add_node(mermaid,
                 html=(html_visit_mermaid, None),
                 latex=(latex_visit_mermaid, None),
                 texinfo=(texinfo_visit_mermaid, None),
                 text=(text_visit_mermaid, None),
                 man=(man_visit_mermaid, None))
    app.add_directive('mermaid', Mermaid)
    app.add_config_value('mermaid_cmd', 'mermaid', 'html')
    app.add_config_value('mermaid_output_format', 'png', 'html')
    app.add_config_value('mermaid_verbose', False, 'html')
    app.add_config_value('mermaid_phantom_path', None, 'html')
    app.add_config_value('mermaid_sequence_config', None, 'html')
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
