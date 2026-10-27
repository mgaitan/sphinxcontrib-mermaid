# Configure zoom, pan, and fullscreen

Every diagram has a small toolbar in its top-right corner. It is shown at
reduced opacity and becomes fully visible on hover or keyboard focus.

## Fullscreen

The fullscreen button opens the diagram over the whole window, fitted to the
screen, with zoom always available. Press Escape, click the close button, or
click outside the diagram to close it. Turn the button off for one diagram with
`:fullscreen: false`, or for every diagram with `mermaid_fullscreen = False`.

## Zoom and pan

Zoom is on automatically for diagrams too large to show at a readable size. To
enable it for one diagram, add `:zoom:`. To enable it everywhere, set
`mermaid_zoom = True`. `:zoom: false` turns it off for one diagram, even an
oversized one; that diagram scrolls with native scrollbars instead.

When zoom is on:

- drag to pan,
- hold Ctrl (⌘ on macOS) and scroll, or pinch on a trackpad or touch screen, to
  zoom around the pointer,
- use the zoom buttons,
- focus the diagram with Tab and press `+`, `-`, `0` (reset), or the arrow keys.

Scrolling without a modifier always scrolls the page. Links and `click`
callbacks in a diagram still work; a drag does not trigger them.

## Hide the toolbar until hover

```python
mermaid_toolbar = "hover"
```

The toolbar then appears only on hover, on keyboard focus, or after a tap on
touch screens.
