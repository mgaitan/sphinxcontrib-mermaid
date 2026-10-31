Diagrams
========

.. toctree::
   :hidden:

   sub/nested
   hidden
   errors
   sizing
   explicit-theme

.. mermaid::
   :name: small

   flowchart LR
     Client --> API --> DB

.. mermaid::
   :name: wide

   flowchart LR
     Source --> Parse --> Resolve --> Transform --> Write --> Index --> HTML

.. mermaid:: giant.mmd
   :name: giant

.. mermaid::
   :name: zen

   zenuml
       title Order
       Client->Server: place()

.. mermaid::
   :name: tidy

   ---
   config:
     layout: tidy-tree
   ---
   mindmap
     root((Docs))
       Tutorials
       Guides
       Reference

.. mermaid::
   :name: linked
   :zoom:

   flowchart LR
     A[Example] --> B[Other]
     click A "https://example.com"
