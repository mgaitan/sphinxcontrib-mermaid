import hashlib
import html
import json
import re
import sys
from pathlib import Path

import pytest


@pytest.fixture
def build_all(app):
    app.builder.build_all()


@pytest.fixture
def index(app, build_all):
    return (app.outdir / "index.html").read_text()


def _config(app):
    return json.loads((app.outdir / "_static/sphinxcontrib-mermaid/config.json").read_text())


def _options(page):
    return [json.loads(html.unescape(v)) for v in re.findall(r'data-mermaid-options="([^"]+)"', page)]


@pytest.mark.sphinx("html", testroot="basic")
def test_markup_and_assets(app, index):
    assert '<div class="mermaid-diagram" id="participants"' in index
    assert '<pre class="mermaid">sequenceDiagram' in index
    assert "Alice-&gt;John" in index
    tag = re.search(r"<script[^>]*sphinxcontrib-mermaid\.js[^>]*>", index).group(0)
    assert 'type="module"' in tag
    assert re.search(r'src="_static/sphinxcontrib-mermaid/sphinxcontrib-mermaid\.js(\?v=[^"]+)?"', tag)
    assert "_static/sphinxcontrib-mermaid/sphinxcontrib-mermaid.css" in index
    assert _options(index)[0] == {"fit": "auto", "zoom": "auto", "fullscreen": True, "width": None, "height": None, "fontSize": None}
    assert (app.outdir / "_static/sphinxcontrib-mermaid/mermaid/mermaid.esm.min.mjs").is_file()


@pytest.mark.sphinx("html", testroot="basic")
def test_no_inline_scripts(app, build_all):
    for page in ["index.html", "zoom.html", "sub/nested.html"]:
        text = (app.outdir / page).read_text()
        inline = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", text, re.DOTALL)
        assert not [body for body in inline if "mermaid" in body.lower()], page


@pytest.mark.sphinx("html", testroot="basic")
def test_per_diagram_zoom_option(app, build_all):
    assert [o["zoom"] for o in _options((app.outdir / "zoom.html").read_text())] == ["auto", True]


@pytest.mark.sphinx("html", testroot="basic")
def test_nested_page_assets(app, build_all):
    assert "../_static/sphinxcontrib-mermaid/sphinxcontrib-mermaid.js" in (app.outdir / "sub/nested.html").read_text()


@pytest.mark.sphinx("html", testroot="basic")
def test_page_without_diagram_has_no_assets(app, build_all):
    assert "sphinxcontrib-mermaid.js" not in (app.outdir / "nodiagram.html").read_text()


@pytest.mark.sphinx("html", testroot="basic")
def test_site_config_bundled(app, build_all):
    cfg = _config(app)
    assert cfg == {
        "mermaid": "mermaid/mermaid.esm.min.mjs",
        "layouts": ["mermaid-layout-tidy-tree/mermaid-layout-tidy-tree.esm.min.mjs"],
        "diagrams": ["mermaid-zenuml/mermaid-zenuml.esm.min.mjs"],
        "extensions": [],
        "iconPacks": {},
        "config": {},
        "lightTheme": "default",
        "darkTheme": "dark",
        "toolbar": "always",
        "maxHeight": "70vh",
        "minFontScale": 0.7,
    }


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_base_url": "https://cdn.jsdelivr.net/npm", "mermaid_version": "12.1.0"})
def test_site_config_remote(app, build_all):
    cfg = _config(app)
    assert cfg["mermaid"] == "https://cdn.jsdelivr.net/npm/mermaid@12.1.0/dist/mermaid.esm.min.mjs"
    assert cfg["diagrams"] == ["https://cdn.jsdelivr.net/npm/@mermaid-js/mermaid-zenuml@1.0.1/dist/mermaid-zenuml.esm.min.mjs"]
    assert cfg["layouts"] == ["https://cdn.jsdelivr.net/npm/@mermaid-js/layout-tidy-tree@1.0.1/dist/mermaid-layout-tidy-tree.esm.min.mjs"]


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_base_url": "https://unpkg.com/"})
def test_site_config_other_cdn(app, build_all):
    cfg = _config(app)
    assert cfg["mermaid"] == "https://unpkg.com/mermaid@12.2.0/dist/mermaid.esm.min.mjs"
    assert cfg["diagrams"] == ["https://unpkg.com/@mermaid-js/mermaid-zenuml@1.0.1/dist/mermaid-zenuml.esm.min.mjs"]
    assert cfg["layouts"] == ["https://unpkg.com/@mermaid-js/layout-tidy-tree@1.0.1/dist/mermaid-layout-tidy-tree.esm.min.mjs"]


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_base_url": "https://cdn.jsdelivr.net/npm", "mermaid_version": "latest"})
def test_site_config_remote_latest(app, build_all):
    assert _config(app)["mermaid"] == "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs"


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_base_url": "vendor/node_modules"})
def test_site_config_local(app, build_all):
    cfg = _config(app)
    assert cfg["mermaid"] == "../vendor/node_modules/mermaid/dist/mermaid.esm.min.mjs"
    assert cfg["diagrams"] == ["../vendor/node_modules/@mermaid-js/mermaid-zenuml/dist/mermaid-zenuml.esm.min.mjs"]
    assert cfg["layouts"] == ["../vendor/node_modules/@mermaid-js/layout-tidy-tree/dist/mermaid-layout-tidy-tree.esm.min.mjs"]


@pytest.mark.sphinx(
    "html",
    testroot="basic",
    confoverrides={
        "mermaid_extensions": ["ext/x.mjs", "https://e.example/y.mjs"],
        "mermaid_icon_packs": {"local": "icons.json", "logos": "https://x/icons.json"},
    },
)
def test_url_resolution(app, build_all):
    cfg = _config(app)
    assert cfg["extensions"] == ["../ext/x.mjs", "https://e.example/y.mjs"]
    assert cfg["iconPacks"] == {"local": "../icons.json", "logos": "https://x/icons.json"}


@pytest.mark.sphinx(
    "html",
    testroot="basic",
    confoverrides={"mermaid_config": {"note": "</script><x>"}, "mermaid_zoom": True, "mermaid_fit": "contain", "mermaid_height": "300px"},
)
def test_values_escaped_and_defaults(app, index):
    assert "</script><x>" not in index
    assert _config(app)["config"] == {"note": "</script><x>"}
    assert _options(index)[0] == {"fit": "contain", "zoom": True, "fullscreen": True, "width": None, "height": "300px", "fontSize": None}


@pytest.mark.sphinx("html", testroot="markdown")
def test_html_from_markdown(index):
    assert '<div class="mermaid-diagram align-center" id="participants"' in index


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
        "sphinxcontrib.mermaid.render.render_mm",
        lambda *args, **kwargs: ("diagram.svg", app.outdir / "diagram.svg"),
    )

    app.builder.build_all()
    index = (app.outdir / "index.html").read_text()

    assert "sphinxcontrib-mermaid.js" not in index
    assert "sphinxcontrib-mermaid.css" not in index


@pytest.mark.sphinx(
    "html",
    testroot="basic",
    confoverrides={"mermaid_output_format": "png"},
)
def test_static_png_has_mermaid_class(app, monkeypatch):
    monkeypatch.setattr(
        "sphinxcontrib.mermaid.render.render_mm",
        lambda *args, **kwargs: ("diagram.png", app.outdir / "diagram.png"),
    )

    app.builder.build_all()
    index = (app.outdir / "index.html").read_text()

    assert re.search(r'<img src="diagram\.png"[^>]* class="mermaid"', index)


@pytest.mark.sphinx("html", testroot="thirdparty")
def test_node_without_options_renders(app, index):
    assert _options(index) == [{"fit": "auto", "zoom": "auto", "fullscreen": True, "width": None, "height": None, "fontSize": None}]


@pytest.mark.sphinx("epub", testroot="basic", freshenv=True)
def test_epub_gets_no_runtime_assets(app):
    app.build(force_all=True)
    assert "unknown mimetype" not in app._warning.getvalue()
    assert not (app.outdir / "_static/sphinxcontrib-mermaid").exists()


@pytest.mark.sphinx("html", testroot="basic")
def test_alt_uses_group_role_and_font_size_option(app, build_all):
    page = (app.outdir / "a11y.html").read_text()
    assert 'role="group" aria-label="A &quot;quoted&quot; &lt;label&gt;"' in page
    assert _options(page)[0]["fontSize"] == 32


@pytest.mark.sphinx("html", testroot="basic")
def test_runtime_tag_has_config_version(app, index):
    tag = re.search(r"<script[^>]*sphinxcontrib-mermaid\.js[^>]*>", index).group(0)
    match = re.search(r'data-mermaid-config="([0-9a-f]{12})"', tag)
    assert match
    assert hashlib.sha1((app.outdir / "_static/sphinxcontrib-mermaid/config.json").read_bytes()).hexdigest()[:12] == match.group(1)
