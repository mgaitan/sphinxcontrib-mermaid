.. image:: https://github.com/mgaitan/sphinxcontrib-mermaid/actions/workflows/test.yml/badge.svg
    :target: https://github.com/mgaitan/sphinxcontrib-mermaid/actions/workflows/test.yml

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


Installation
------------

You can install it using pip

::

    pip install sphinxcontrib-mermaid

Then add ``sphinxcontrib.mermaid`` in ``extensions`` list of your project's ``conf.py``::

    extensions = [
        ...,
        'sphinxcontrib.mermaid'
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

   For individual parameters, a list of parameters can be added. Refer to `<https://github.com/mermaidjs/mermaid.cli#options>`_.
   Examples::

      mermaid_params = ['--theme', 'forest', '--width', '600', '--backgroundColor', 'transparent']

   This will render the mermaid diagram with theme forest, 600px width and transparent background.

``mermaid_sequence_config``

    Allows overriding the sequence diagram configuration. It could be useful to increase the width between actors. It **needs to be a json file**
    Check options in the `documentation <https://mermaid-js.github.io/mermaid/#/mermaidAPI?id=configuration>`_

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

Building PDFs on readthedocs.io
-----------------------------------

In order to have Mermaid diagrams build properly in PDFs generated on readthedocs.io, you will need a few extra configurations.  

1. In your ``.readthedocs.yaml`` file (which should be in the root of your repository) include a ``post-install`` command to install the Mermaid CLI: ::

    build:
      os: ubuntu-20.04
      tools:
        python: "3.8"
        nodejs: "16"
      jobs:
        post_install:
          - npm install -g @mermaid-js/mermaid-cli

 Note that if you previously did not have a ``.readthedocs.yaml`` file, you will also need to specify all targets you wish to build and other basic configuration options.  A minimal example of a complete file is: ::

    # .readthedocs.yaml
    # Read the Docs configuration file
    # See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

    # Required
    version: 2

    # Set the version of Python and other tools you might need
    build:
      os: ubuntu-20.04
      tools:
        python: "3.8"
        nodejs: "16"
      jobs:
        post_install:
          - npm install -g @mermaid-js/mermaid-cli

    # Build documentation in the docs/ directory with Sphinx
    sphinx:
       configuration: docs/conf.py

    # If using Sphinx, optionally build your docs in additional formats such as PDF
    formats:
      - epub
      - pdf

    python:
       install:
       - requirements: docs/requirements.txt

2. In your documentation directory add file ``puppeteer-config.json`` with contents: ::

    {
      "args": ["--no-sandbox"]
    }
   

3. In your documentation ``conf.py`` file, add: ::

    mermaid_params = ['-p' 'puppeteer-config.json']


