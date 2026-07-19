import pytest


@pytest.mark.sphinx("gettext", testroot="i18n")
def test_mermaid_caption_is_extracted(app):
    app.builder.build_all()

    catalog = (app.outdir / "index.pot").read_text()

    assert 'msgid "A translatable diagram"' in catalog
    assert "flowchart LR" not in catalog
