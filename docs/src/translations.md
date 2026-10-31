# Translate diagrams

Captions go into gettext catalogs and are translated like other figure
captions. Inline diagram source is not extracted.

To translate the labels inside a diagram, keep the source in an external `.mmd`
file and add localized copies that follow Sphinx's
[`figure_language_filename`](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-figure_language_filename)
pattern. With the default pattern, `diagram.mmd` and `diagram.de.mmd` can sit
side by side, and `.. mermaid:: diagram.mmd` picks the German file when
`language = "de"`.
