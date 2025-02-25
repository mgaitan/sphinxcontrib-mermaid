import pytest
from sphinx.builders.text import TextBuilder
from sphinx.writers.text import TextTranslator


class MarkdownTestTranslator(TextTranslator):
    def visit_literal_block(self, node):
        self.add_text(f"```{node['language']}\n")
        self.new_state(0)

    def add(self, text):
        self.add_text(text)

    def depart_literal_block(self, node):
        self.end_state(wrap=False)
        self.add_text("\n```\n")


class MarkdownTestBuilder(TextBuilder):
    name = "markdown"
    format = "markdown"
    out_suffix = ".md"
    default_translator_class = MarkdownTestTranslator


@pytest.mark.sphinx("html", testroot="markdown")
def test_markdown_builder_mermaid(app):
    app.add_builder(MarkdownTestBuilder)
    app.builder = MarkdownTestBuilder(app, app.env)
    app.builder.build_all()

    output = (app.outdir / "index.md").read_text()
    assert "```mermaid" in output
    assert "sequenceDiagram" in output
    assert "Alice->John: Hello John, how are you?" in output
