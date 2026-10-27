reStructuredText examples
=========================

A captioned, centered diagram with a reference name:

.. code-block:: rst

   .. mermaid::
      :caption: Request and response
      :name: request-flow
      :align: center
      :alt: A client requests a page from a server.

      sequenceDiagram
          Client->>Server: GET /
          Server-->>Client: 200 OK

.. mermaid::
   :caption: Request and response
   :name: request-flow
   :align: center
   :alt: A client requests a page from a server.

   sequenceDiagram
       Client->>Server: GET /
       Server-->>Client: 200 OK

Link to it with ``:ref:`request-flow```: :ref:`request-flow`.

A fixed-height diagram with zoom:

.. code-block:: rst

   .. mermaid:: examples/elk.mmd
      :height: 250px
      :zoom:

.. mermaid:: examples/elk.mmd
   :height: 250px
   :zoom:

A diagram with a per-diagram Mermaid config:

.. code-block:: rst

   .. mermaid::
      :config: {"theme": "forest"}

      flowchart LR
          Forest --> Theme

.. mermaid::
   :config: {"theme": "forest"}

   flowchart LR
       Forest --> Theme
