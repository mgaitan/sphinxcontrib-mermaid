import re
import sys
from json import dumps
from pathlib import Path

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
    assert "mermaid.run(" in index
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
    assert "mermaid.run(" in index
    assert "if (false) {\n        const mermaids_to_add_zoom" in index
    zoom_page = (app.outdir / "zoom.html").read_text().replace("<script >", "<script>")
    assert "svg.call(zoom);" in zoom_page
    assert 'd3.selectAll(".mermaid[data-zoom-id=' in zoom_page
    assert '] svg")' not in zoom_page
    assert 'return this.querySelector("svg");' in zoom_page
    assert "if (true) {\n        const mermaids_to_add_zoom" in zoom_page

    # the first diagram has no id
    assert '<pre id="participants" class="mermaid">\n        sequenceDiagram' in zoom_page

@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_d3_zoom": True})
def test_html_zoom_option_global(index):
    assert "mermaid.run(" in index
    assert "if (true) {\n        const mermaids_to_add_zoom" in index
    assert 'd3.selectAll(".mermaid").select(function() {' in index
    assert 'return this.querySelector("svg");' in index
    assert 'd3.selectAll(".mermaid svg")' not in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_d3_zoom": False})
def test_html_no_zoom(index):
    assert "mermaid.run(" in index
    assert "if (false) {\n        const mermaids_to_add_zoom" in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_version": "10.3.0", "mermaid_include_elk": False})
def test_conf_mermaid_version(app, index):
    assert "mermaid.run(" in index
    assert app.config.mermaid_version == "10.3.0"
    assert (
        'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.3.0/dist/mermaid.esm.min.mjs"'
        in index
    )


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_use_local": "test", "mermaid_include_elk": False})
def test_conf_mermaid_local(app, index):
    assert "mermaid.run(" in index
    assert "mermaid.min.js" not in index
    assert 'import mermaid from "./_static/test"' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_use_local": "test", "mermaid_include_elk": True, "mermaid_elk_use_local": "test"})
def test_conf_mermaid_elk_local(app, index):
    assert "mermaid.run(" in index
    assert "mermaid.min.js" not in index
    assert "mermaid-layout-elk.esm.min.mjs" not in index
    assert 'import elkLayouts from "./_static/test"' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_use_local": "test", "mermaid_include_zenuml": True, "mermaid_zenuml_use_local": "test"})
def test_conf_mermaid_zenuml_local(app, index):
    assert "mermaid.run()" in index
    assert "mermaid.min.js" not in index
    assert "mermaid-zenuml.esm.min.mjs" not in index
    assert 'import("./_static/test")' in index


@pytest.mark.sphinx(
    "html",
    testroot="basic",
    confoverrides={"d3_version": "1.2.3", "mermaid_d3_zoom": True, "mermaid_include_elk": False},
)
def test_conf_d3_version(app, index):
    assert "mermaid.run(" in index
    assert app.config.d3_version == "1.2.3"
    assert '<script src="https://cdn.jsdelivr.net/npm/d3@1.2.3/dist/d3.min.js"></script>' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"d3_use_local": "test", "mermaid_d3_zoom": True})
def test_conf_d3_local(app, index):
    assert "cdn.jsdelivr.net/npm/d3" not in index
    assert re.search(
        r'<script src="[^"]*_static/test(?:\?[^"]*)?"></script>',
        index,
    )


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_init_config": {"startOnLoad": True}})
def test_mermaid_init_js(index):
    assert "mermaid.run(" in index
    assert (
        '{"startOnLoad": false}'
        not in index
    )
    assert (
        '{"startOnLoad": true}'
        in index
    )


@pytest.mark.sphinx("html", testroot="config")
def test_mermaid_config(index):
    assert "config:\n  theme: base\n  themeVariables:\n    primaryColor: '#BB2528'" in index
    assert "config:\n  theme: forest" in index
    assert index.count("primaryColor: '#BB2528'") == 1
    assert "cdn.jsdelivr.net/npm/d3" not in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_include_elk": True, "mermaid_elk_version": "latest"})
def test_mermaid_with_elk(app, index):
    assert "mermaid.run(" in index
    assert (
        'import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk/dist/mermaid-layout-elk.esm.min.mjs"'
        in index
    )


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_include_zenuml": True, "mermaid_zenuml_version": "latest"})
def test_mermaid_with_zenuml(app, index):
    assert "mermaid.run()" in index
    assert (
        'import("https://cdn.jsdelivr.net/npm/@mermaid-js/mermaid-zenuml/dist/mermaid-zenuml.esm.min.mjs")'
        in index
    )
    assert '.replace(/^\\s*---\\s*\\n[^]*?\\n---\\s*/, "")' in index


@pytest.mark.sphinx("html", testroot="markdown", confoverrides={"mermaid_include_elk": True})
def test_html_raw_from_markdown(index):
    assert "mermaid.run(" in index
    assert "mermaid.run(" in index
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
    assert "mermaid.run(" in index
    assert ".mermaid-container {\\n    position: relative;" in index
    assert ".mermaid-fullscreen-btn {\\n    position: absolute;" in index
    assert ".mermaid-fullscreen-btn:hover" in index
    assert ".mermaid-fullscreen-modal" in index
    assert "mermaid-fullscreen-close" in index
    assert "previousScrollOffset = [window.scrollX, window.scrollY];" in index
    assert "svg.style.display = 'block';" in index
    assert "svg.style.sdisplay" not in index
    assert index.count("document.addEventListener('keydown'") == 1


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_fullscreen": False})
def test_fullscreen_disabled(index):
    """Test that fullscreen is not added when disabled."""
    assert "mermaid.run(" in index
    assert ".mermaid-fullscreen-btn:hover" not in index


@pytest.mark.sphinx("html", testroot="fullscreen", confoverrides={"mermaid_d3_zoom": True})
def test_fullscreen_with_zoom(index):
    """Test that fullscreen works with D3 zoom."""
    assert "mermaid.run(" in index
    assert ".mermaid-fullscreen-btn" in index
    assert "d3.zoom" in index


@pytest.mark.sphinx("html", testroot="fullscreen", confoverrides={"mermaid_fullscreen_button": "[+]"})
def test_custom_fullscreen_button(index):
    """Test custom fullscreen button icon."""
    assert "mermaid.run(" in index
    assert "[+]" in index


@pytest.mark.sphinx("html", testroot="basic")
def test_lazy_rendering_code_present(index):
    """Test that lazy rendering code for hidden elements is present."""
    assert "IntersectionObserver" in index
    assert "data-mermaid-deferred" in index
    assert "mermaids_active.length !== mermaids_processed.length" in index
    # Zoom is applied through the idempotent helper so deferred diagrams can be
    # zoomed on reveal, and the fixed-count SVG gate that looped forever when a
    # zoomed diagram was hidden is gone.
    assert "addZoomToSvgs" in index
    assert "data-zoom-applied" in index
    assert "svgs.size() !== mermaids_to_add_zoom" not in index


@pytest.mark.sphinx("html", testroot="basic")
def test_mermaid_theme_defaults(index):
    """Default theme values are 'dark' and 'default'."""
    assert 'theme: darkTheme ? "dark" : "default"' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_dark_theme": "neutral", "mermaid_light_theme": "neutral"})
def test_mermaid_theme_both_custom(index):
    """Both theme values can be overridden."""
    assert 'theme: darkTheme ? "neutral" : "neutral"' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_dark_theme": "neutral"})
def test_mermaid_theme_dark_only(index):
    """Only dark theme overridden, light stays default."""
    assert 'theme: darkTheme ? "neutral" : "default"' in index


@pytest.mark.sphinx(
    "html",
    testroot="fullscreen",
    confoverrides={
        "mermaid_dark_theme": "dark'theme",
        "mermaid_fullscreen_button": "'` ${button}</script>",
        "mermaid_init_config": {"note": "` ${config}"},
        "mermaid_light_theme": 'light"theme',
    },
)
def test_javascript_config_values_are_escaped(index):
    button_text = "'` ${button}</script>"
    init_config = {"note": "` ${config}"}
    dark_theme = "dark'theme"
    light_theme = 'light"theme'
    escaped_button = dumps(button_text).replace("<", "\\u003c")

    assert f"fullscreenBtn.textContent = {escaped_button};" in index
    assert "\\u003c/script>" in index
    assert f"...{dumps(init_config)}" in index
    assert f"darkTheme ? {dumps(dark_theme)} : {dumps(light_theme)}" in index


@pytest.mark.sphinx(
    "html",
    testroot="invalid",
    confoverrides={
        # Call a fake mmdc script that always fails, to test error handling.
        # mmdc_fake is written in Python to make the test work on Windows.
        "mermaid_cmd": [
            sys.executable,
            str(Path(__file__).parent / "roots/test-invalid/mmdc_fake"),
        ],
        "mermaid_output_format": "svg",
    },
)
def test_render_error_message(app):
    """The stderr string from a failed mmdc run appears verbatim in the Sphinx warning."""
    app.builder.build_all()
    warnings = app._warning.getvalue()
    assert "Mermaid exited with error:\n[stderr]\nError: bad syntax\nsomething else" in warnings


@pytest.mark.sphinx(
    "html",
    testroot="basic",
    confoverrides={"mermaid_output_format": "svg"},
)
def test_static_output_skips_javascript(app, monkeypatch):
    monkeypatch.setattr(
        "sphinxcontrib.mermaid.render_mm",
        lambda *args, **kwargs: ("diagram.svg", app.outdir / "diagram.svg"),
    )

    app.builder.build_all()
    index = (app.outdir / "index.html").read_text()

    assert "cdn.jsdelivr.net/npm/mermaid" not in index
    assert "cdn.jsdelivr.net/npm/d3" not in index
    assert "mermaid.run(" not in index
