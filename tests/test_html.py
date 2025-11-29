import re

import pytest


@pytest.fixture
def build_all(app):
    app.builder.build_all()


@pytest.fixture
def index(app, build_all):
    # normalize script tag for compat to Sphinx<4
    return (app.outdir / "index.html").read_text().replace("<script >", "<script>")


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_include_elk": True})
def test_html_raw(index):
    assert "mermaid.run()" in index
    assert (
        'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.12.1/dist/mermaid.esm.min.mjs"'
        in index
    )
    assert (
        'import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.2.0/dist/mermaid-layout-elk.esm.min.mjs"'
        in index
    )
    assert (
        'mermaid.registerLayoutLoaders(elkLayouts);'
        in index
    )
    assert (
        '{"startOnLoad": false}'
        in index
    )
    assert (
        '<pre id="participants" class="mermaid">\n        sequenceDiagram\n   participant Alice\n   participant Bob\n   Alice-&gt;John: Hello John, how are you?\n    </pre>'
        in index
    )


@pytest.mark.sphinx("html", testroot="basic")
def test_html_zoom_option(index, app):
    assert "mermaid.run()" in index
    assert 'if ("False" === "True") {\n        const mermaids_to_add_zoom' in index
    zoom_page = (app.outdir / "zoom.html").read_text().replace("<script >", "<script>")
    assert "svg.call(zoom);" in zoom_page

    # the first diagram has no id
    assert '<pre id="participants" class="mermaid">\n        sequenceDiagram' in zoom_page

@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_d3_zoom": True})
def test_html_zoom_option_global(index):
    assert "mermaid.run()" in index
    assert 'if ("True" === "True") {\n        const mermaids_to_add_zoom' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_d3_zoom": False})
def test_html_no_zoom(index):
    assert "mermaid.run()" in index
    assert 'if ("False" === "True") {\n        const mermaids_to_add_zoom' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_version": "10.3.0", "mermaid_include_elk": False})
def test_conf_mermaid_version(app, index):
    assert "mermaid.run()" in index
    assert app.config.mermaid_version == "10.3.0"
    assert (
        'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.3.0/dist/mermaid.esm.min.mjs"'
        in index
    )


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_use_local": "test", "mermaid_include_elk": False})
def test_conf_mermaid_local(app, index):
    assert "mermaid.run()" in index
    assert "mermaid.min.js" not in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_use_local": "test", "mermaid_elk_use_local": "test"})
def test_conf_mermaid_elk_local(app, index):
    assert "mermaid.run()" in index
    assert "mermaid.min.js" not in index
    assert "mermaid-layout-elk.esm.min.mjs" not in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"d3_version": "1.2.3", "mermaid_include_elk": False})
def test_conf_d3_version(app, index):
    assert "mermaid.run()" in index
    assert app.config.d3_version == "1.2.3"
    assert '<script src="https://cdn.jsdelivr.net/npm/d3@1.2.3/dist/d3.min.js"></script>' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"d3_use_local": "test"})
def test_conf_d3_local(app, index):
    assert "cdn.jsdelivr.net/npm/d3" not in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_init_config": {"startOnLoad": True}})
def test_mermaid_init_js(index):
    assert "mermaid.run()" in index
    assert (
        '{"startOnLoad": false}'
        not in index
    )
    assert (
        '{"startOnLoad": true}'
        in index
    )

@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_include_elk": True, "mermaid_elk_version": "latest"})
def test_mermaid_with_elk(app, index):
    assert "mermaid.run()" in index
    assert (
        'import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk/dist/mermaid-layout-elk.esm.min.mjs"'
        in index
    )


@pytest.mark.sphinx("html", testroot="markdown", confoverrides={"mermaid_include_elk": True})
def test_html_raw_from_markdown(index):
    assert "mermaid.run()" in index
    assert "mermaid.run()" in index
    assert (
        'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.12.1/dist/mermaid.esm.min.mjs"'
        in index
    )
    assert (
        'import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.2.0/dist/mermaid-layout-elk.esm.min.mjs"'
        in index
    )
    assert (
        'mermaid.registerLayoutLoaders(elkLayouts);'
        in index
    )
    assert (
        '{"startOnLoad": false}'
        in index
    )
    assert (
        '<pre align="center" id="participants" class="mermaid align-center">\n            sequenceDiagram\n      participant Alice\n      participant Bob\n      Alice-&gt;John: Hello John, how are you?\n    </pre>'
        in index
    )


@pytest.mark.sphinx("html", testroot="fullscreen")
def test_fullscreen_enabled(index):
    """Test that fullscreen JavaScript is added when enabled."""
    assert "mermaid.run()" in index
    assert ".mermaid-fullscreen-btn:hover" in index
    assert ".mermaid-fullscreen-modal" in index
    assert "mermaid-fullscreen-close" in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_fullscreen": False})
def test_fullscreen_disabled(index):
    """Test that fullscreen is not added when disabled."""
    assert "mermaid.run()" in index
    assert ".mermaid-fullscreen-btn:hover" not in index


@pytest.mark.sphinx("html", testroot="fullscreen", confoverrides={"mermaid_d3_zoom": True})
def test_fullscreen_with_zoom(index):
    """Test that fullscreen works with D3 zoom."""
    assert "mermaid.run()" in index
    assert ".mermaid-fullscreen-btn" in index
    assert "d3.zoom" in index


@pytest.mark.sphinx("html", testroot="fullscreen", confoverrides={"mermaid_fullscreen_button": "[+]"})
def test_custom_fullscreen_button(index):
    """Test custom fullscreen button icon."""
    assert "mermaid.run()" in index
    assert "[+]" in index
