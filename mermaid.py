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
from os import path
from subprocess import Popen, PIPE
from hashlib import sha1

from six import text_type
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList

import sphinx
from sphinx.errors import SphinxError
from sphinx.locale import _
from sphinx.util.i18n import search_image_for_language
from sphinx.util.osutil import ensuredir, ENOENT, EPIPE, EINVAL
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
    Directive to insert arbitrary mm markup.
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'alt': directives.unchanged,
        'align': align_spec,
        'inline': directives.flag,
        'caption': directives.unchanged,
        'mermaid_mm': directives.unchanged,
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
        if 'mermaid_mm' in self.options:
            node['options']['mermaid_mm'] = self.options['mermaid_mm']
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


class MermaidSimple(Directive):
    """
    Directive to insert arbitrary mermaid markup.
    """
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'alt': directives.unchanged,
        'align': align_spec,
        'inline': directives.flag,
        'caption': directives.unchanged,
        'mermaid_mm': directives.unchanged,
    }

    def run(self):
        node = mermaid()
        node['code'] = '%s %s {\n%s\n}\n' % \
                       (self.name, self.arguments[0], '\n'.join(self.content))
        node['options'] = {}
        if 'mermaid_mm' in self.options:
            node['options']['mermaid_mm'] = self.options['mermaid_mm']
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
    mermaid_mm = options.get('mermaid_mm', self.builder.config.mermaid_mm)
    hashkey = (code + str(options) + str(mermaid_mm) +
               str(self.builder.config.mermaid_mm_args)).encode('utf-8')

    fname = '%s-%s.%s' % (prefix, sha1(hashkey).hexdigest(), format)
    relfn = posixpath.join(self.builder.imgpath, fname)
    outfn = path.join(self.builder.outdir, self.builder.imagedir, fname)

    if path.isfile(outfn):
        return relfn, outfn

    if (hasattr(self.builder, '_mermaid_warned_mm') and
       self.builder._mermaid_warned_mm.get(mermaid_mm)):
        return None, None

    ensuredir(path.dirname(outfn))

    # mermaid expects UTF-8 by default
    if isinstance(code, text_type):
        code = code.encode('utf-8')

    mm_args = [mermaid_mm]
    mm_args.extend(self.builder.config.mermaid_mm_args)
    mm_args.extend(['-T' + format, '-o' + outfn])
    if format == 'png':
        mm_args.extend(['-Tcmapx', '-o%s.map' % outfn])
    try:
        p = Popen(mm_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    except OSError as err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('mm command %r cannot be run (needed for mermaid '
                          'output), check the mermaid_mm setting' % mermaid_mm)
        if not hasattr(self.builder, '_mermaid_warned_mm'):
            self.builder._mermaid_warned_mm = {}
        self.builder._mermaid_warned_mm[mermaid_mm] = True
        return None, None
    try:
        # Mermaid may close standard input when an error occurs,
        # resulting in a broken pipe on communicate()
        stdout, stderr = p.communicate(code)
    except (OSError, IOError) as err:
        if err.errno not in (EPIPE, EINVAL):
            raise
        # in this case, read the standard output and standard error streams
        # directly, to get the error message(s)
        stdout, stderr = p.stdout.read(), p.stderr.read()
        p.wait()
    if p.returncode != 0:
        raise MermaidError('mm exited with error:\n[stderr]\n%s\n'
                            '[stdout]\n%s' % (stderr, stdout))
    if not path.isfile(outfn):
        raise MermaidError('mm did not produce an output file:\n[stderr]\n%s\n'
                            '[stdout]\n%s' % (stderr, stdout))
    return relfn, outfn


def warn_for_deprecated_option(self, node):
    if hasattr(self.builder, '_mermaid_warned_inline'):
        return

    if 'inline' in node:
        self.builder.warn(':inline: option for mermaid is deprecated since version 1.4.0.')
        self.builder._mermaid_warned_inline = True


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
            with open(outfn + '.map', 'rb') as mapfile:
                imgmap = mapfile.readlines()
            if len(imgmap) == 2:
                # nothing in image map (the lines are <map> and </map>)
                self.body.append('<img src="%s" alt="%s" %s/>\n' %
                                 (fname, alt, imgcss))
            else:
                # has a map: get the name of the map and connect the parts
                mapname = mapname_re.match(imgmap[0].decode('utf-8')).group(1)
                self.body.append('<img src="%s" alt="%s" usemap="#%s" %s/>\n' %
                                 (fname, alt, mapname, imgcss))
                self.body.extend([item.decode('utf-8') for item in imgmap])
            if 'align' in node:
                self.body.append('</div>\n')

    raise nodes.SkipNode


def html_visit_mermaid(self, node):
    warn_for_deprecated_option(self, node)
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
    warn_for_deprecated_option(self, node)
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
    warn_for_deprecated_option(self, node)
    render_mm_texinfo(self, node, node['code'], node['options'])


def text_visit_mermaid(self, node):
    warn_for_deprecated_option(self, node)
    if 'alt' in node.attributes:
        self.add_text(_('[graph: %s]') % node['alt'])
    else:
        self.add_text(_('[graph]'))
    raise nodes.SkipNode


def man_visit_mermaid(self, node):
    warn_for_deprecated_option(self, node)
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
    app.add_directive('graph', MermaidSimple)
    app.add_directive('digraph', MermaidSimple)
    app.add_config_value('mermaid_mm', 'mm', 'html')
    app.add_config_value('mermaid_mm_args', [], 'html')
    app.add_config_value('mermaid_output_format', 'png', 'html')
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
