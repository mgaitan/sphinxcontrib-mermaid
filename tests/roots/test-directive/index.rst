Directive
=========

.. mermaid::
   :name: plain

   flowchart LR
     A --> B

.. mermaid::
   :name: sized
   :width: 600
   :height: 300px
   :fit: contain
   :zoom: false
   :config: {"theme": "forest"}
   :title: Hello

   flowchart LR
     A --> B

.. mermaid::
   :name: fm
   :height: 500px

   ---
   height: 250px
   zoom: true
   config:
     layout: elk
   ---
   flowchart LR
     A --> B

.. mermaid:: sized.mmd
   :name: external

.. mermaid::
   :name: captioned
   :caption: A caption
   :align: center

   flowchart LR
     A --> B

.. mermaid::
   :name: invalid
   :fit: cover

   flowchart LR
     A --> B

.. mermaid::
   :name: fmclass

   ---
   class: fromfm
   ---
   flowchart LR
     A --> B
