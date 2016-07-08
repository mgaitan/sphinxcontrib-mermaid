sphinxcontrib-mermaid
=====================

This extension allows you to embed `Mermaid <http://knsv.github.io/mermaid/>`_ graphs in your documents, including general flowcharts, sequence and gantt diagrams.

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

The code will be rendered to a PNG (default) or SVG image (experimental)
(see :confval:`mermaid_output_format`) using `mermaid-cli <http://knsv.github.io/mermaid/#mermaid-cli>`_.

You can also embed external mermaid files, by giving the file name as an
argument to the directive and no additional content::

   .. mermaid:: path/to/mermaid-gantt-code.mmd

As for all file references in Sphinx, if the filename is absolute, it is
taken as relative to the source directory.

Installation
------------

You can install it using pip

::

    pip install sphinxcontrib-mermaid

Then add ``sphinxcontrib.mermaid`` in ``extensions`` list of your projec't ``conf.py``::

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


``mermaid_cmd``

   The command name with which to invoke ``mermaid-cli`` program.  The default is ``'mermaid'``; you may need to set this to a full path if it's not in the executable
   search path.

``mermaid_phantom_path``

    The mermaid command requires PhantomJS (version ^1.9.0) to be installed and available in your $PATH, or you can specify it's location with in this config variable.

``mermaid_output_format``

   The output format for Mermaid when building HTML files.  This must be either
   ``'png'`` or ``'svg'``; the default is ``'png'``. Note ``'svg'`` support is very experimental in mermaid.


``mermaid_sequence_config``

    Allows overriding the sequence diagram configuration. It could be useful to increase the width between actors. It **should be a normal python dictionary**
    Check options in the `documentation <http://knsv.github.io/mermaid/#sequence-diagram-configuration>`_

``mermaid_verbose``

    Use the verbose mode when call mermaid-cli, and show its output in the building
    process.


Acknowledge
-----------

Much of the code is based on `sphinx.ext.graphviz <http://www.sphinx-doc.org/en/stable/ext/graphviz.html>`_. Thanks to its authors and other Sphinx contributors for such amazing tool.
