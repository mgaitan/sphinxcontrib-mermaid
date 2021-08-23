.. image:: https://travis-ci.com/mgaitan/sphinxcontrib-mermaid.svg?branch=master
    :target: https://travis-ci.com/mgaitan/sphinxcontrib-mermaid

This extension allows you to embed `Mermaid <https://mermaid-js.github.io/mermaid>`_ graphs in your
documents, including general flowcharts, sequence and gantt diagrams.

It adds a directive to embed mermaid markup. For example::

  .. mermaid::

     sequenceDiagram
        participant Alice
        participant Bob
        Alice->John: Hello John, how are you?
        loop Healthcheck
            John->John: Fight against hypochondria
        end
        Note right of John: Rational thoughts <br/>prevail...
        John-->Alice: Great!
        John->Bob: How about you?
        Bob-->John: Jolly good!


By default, the HTML builder will simply render this as a ``div`` tag with
``class="mermaid"``, injecting the external javascript, css and initialization code to
make mermaid works.

For other builders (or if ``mermaid_output_format`` config variable is set differently), the extension
will use `mermaid-cli <https://github.com/mermaidjs/mermaid.cli>`_ to render as
to a PNG or SVG image, and then used in the proper code.


.. mermaid::

   sequenceDiagram
      participant Alice
      participant Bob
      Alice->John: Hello John, how are you?
      loop Healthcheck
          John->John: Fight against hypochondria
      end
      Note right of John: Rational thoughts <br/>prevail...
      John-->Alice: Great!
      John->Bob: How about you?
      Bob-->John: Jolly good!


You can also embed external mermaid files, by giving the file name as an
argument to the directive and no additional content::

   .. mermaid:: path/to/mermaid-gantt-code.mmd

As for all file references in Sphinx, if the filename is not absolute, it is
taken as relative to the source directory.


In addition, you can use mermaid to automatically generate a diagram to show the class inheritance using the directive ``autoclasstree``. It accepts one or more fully qualified
names to a class or a module. In the case of a module, all the class found will be included.

Of course, these objects need to be importable to make its diagram.

If an optional attribute ``:full:`` is given, it will show the complete hierarchy of each class.

The option ``:namespace: <value>`` limits to the base classes that belongs to this namespace.
Meanwhile, the flag ``:strict:`` only process the classes that are strictly defined in the given
module (ignoring classes imported from other modules).


For example::

    .. autoclasstree:: sphinx.util.SphinxParallelError sphinx.util.ExtensionError
       :full:

.. autoclasstree:: sphinx.util.SphinxParallelError sphinx.util.ExtensionError
   :full:


Or directly the module::

    .. autoclasstree:: sphinx.util


.. autoclasstree:: sphinx.util

And alternative to `autoclasstree` directive is `mermaid-inheritance`. That directive mimics exactly the
official `inheritance_diagram <https://www.sphinx-doc.org/en/master/usage/extensions/inheritance.html>`_ 
extension but uses mermaid JS instead of graphviz to include the inheritance diagrams.

It adds this directive::

    .. mermaid-inheritance::

This directive has one or more arguments, each giving a module or class name. Class names can be unqualified; 
in that case they are taken to exist in the currently described module.

For each given class, and each class in each given module, the base classes are determined. Then, from all classes 
and their base classes, a graph is generated which is then rendered via the ``mermaid`` extension to a directed graph.

This directive supports an option called ``parts`` that, if given, must be an integer, advising the directive 
to keep that many dot-separated parts in the displayed names (from right to left). For example, ``parts=1``
will only display class names, without the names of the modules that contain them.

The directive also supports a ``private-bases`` flag option; if given, private base classes (those whose name 
starts with ``_``) will be included.

You can use ``caption`` option to give a caption to the diagram.

It also supports a ``top-classes`` option which requires one or more class names separated by comma. If specified 
inheritance traversal will stop at the specified class names. 

For example::

    .. mermaid-inheritance:: sphinx.ext.inheritance_diagram.InheritanceDiagram

.. mermaid-inheritance:: sphinx.ext.inheritance_diagram.InheritanceDiagram

.. note::

    ``.`` are replaced by ``_`` in class name because mermaidJS does not allow them.

To stop the diagram at ``SphinxDirective`` and only display the class name::

    .. mermaid-inheritance:: sphinx.ext.inheritance_diagram.InheritanceDiagram
        :top-classes: sphinx.util.docutils.SphinxDirective
        :parts: 1


.. mermaid-inheritance:: sphinx.ext.inheritance_diagram.InheritanceDiagram
   :top-classes: sphinx.util.docutils.SphinxDirective
   :parts: 1

Installation
------------

You can install it using pip

::

    pip install sphinxcontrib-mermaid

Then add ``sphinxcontrib.mermaid`` in ``extensions`` list of your project's ``conf.py``::

    extensions = [
        ...,
        'sphinxcontrib.mermaid',
        # Optional if you want the inheritance graphs
        'sphinxcontrib.mermaid-inheritance',
    ]


Directive options
------------------

``:alt:``: determines the image's alternate text for HTML output.  If not given, the alternate text defaults to the mermaid code.

``:align:``: determines the image's position. Valid options are ``'left'``, ``'center'``, ``'right'``

``:caption:``: can be used to give a caption to the diagram.


Config values
-------------

``mermaid_output_format``

   The output format for Mermaid when building HTML files.  This must be either ``'raw'``
   ``'png'`` or ``'svg'``; the default is ``'raw'``. ``mermaid-cli`` is required if it's not ``raw``

``mermaid_version``

  The version of mermaid that will be used to parse ``raw`` output in HTML files. This should match a version available on https://unpkg.com/browse/mermaid/. The default is ``"latest"``.

  If it's set to ``""``, the lib won't be automatically included from the CDN service and you'll need to add it as a local
  file in ``html_js_files``. For instance, if you download the lib to `_static/js/mermaid.js`, in ``conf.py``::


    html_js_files = [
       'js/mermaid.js',
    ]


``mermaid_init_js``

  Mermaid initilizaction code. Default to ``"mermaid.initialize({startOnLoad:true});"``.

.. versionchanged:: 0.7
    The init code doesn't include the `<script>` tag anymore. It's automatically added at build time.


``mermaid_cmd``

   The command name with which to invoke ``mermaid-cli`` program.  The default is ``'mmdc'``; you may need to set this to a full path if it's not in the executable search path.

``mermaid_cmd_shell``

   When set to true, the ``shell=True`` argument will be passed the process execution command.  This allows commands other than binary executables to be executed on Windows.  The default is false.

``mermaid_params``

   For individual parameters, a list of parameters can be added. Refer to `<https://github.com/mermaid-js/mermaid-cli#options>`_.
   Examples::

      mermaid_params = ['--theme', 'forest', '--width', '600', '--backgroundColor', 'transparent']

   This will render the mermaid diagram with theme forest, 600px width and transparent background.

``mermaid_sequence_config``

    Allows overriding the sequence diagram configuration. It could be useful to increase the width between actors. It **needs to be a json file**
    Check options in the `documentation <https://mermaid-js.github.io/mermaid/#/n00b-syntaxReference?id=configuration>`_

``mermaid_verbose``

    Use the verbose mode when call mermaid-cli, and show its output in the building
    process.

``mermaid_pdfcrop``

    If using latex output, it might be useful to crop the pdf just to the needed space. For this, ``pdfcrop`` can be used.
    State binary name to use this extra function.


Markdown support
----------------

You can include Mermaid diagrams in your Markdown documents in Sphinx.
You just need to setup the `markdown support in Sphinx <https://www.sphinx-doc.org/en/master/usage/markdown.html>`_ via
`myst-parser <https://myst-parser.readthedocs.io/>`_
. See a `minimal configuration from the tests <https://github.com/mgaitan/sphinxcontrib-mermaid/blob/master/tests/roots/test-markdown/conf.py>`_

Then in your `.md` documents include a code block as in reStructuredTexts::


 ```{mermaid}

     sequenceDiagram
       participant Alice
       participant Bob
       Alice->John: Hello John, how are you?
 ```


