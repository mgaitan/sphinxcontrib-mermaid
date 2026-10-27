Sizing
======

.. mermaid::
   :name: small
   :alt: Client to API to DB

   flowchart LR
     Client --> API --> DB

.. mermaid::
   :name: wide

   flowchart LR
     Source --> Parse --> Resolve --> Transform

.. mermaid:: giant.mmd
   :name: giant

.. mermaid:: giant.mmd
   :name: contained
   :fit: contain

.. mermaid:: giant.mmd
   :name: sized
   :width: 400
   :height: 200px

.. mermaid:: giant.mmd
   :name: nozoom
   :zoom: false

.. mermaid::
   :name: nofs
   :fullscreen: false

   flowchart LR
     No --> Fullscreen

.. mermaid::
   :name: gantt

   gantt
       dateFormat YYYY-MM-DD
       section Build
       Bundle   :a1, 2026-01-05, 3d
       Runtime  :a2, after a1, 10d
       Docs     :a3, after a2, 5d

.. mermaid:: bigfont.mmd
   :name: bigfont
