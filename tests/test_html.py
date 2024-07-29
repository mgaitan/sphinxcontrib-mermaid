import re

import pytest


@pytest.fixture
def build_all(app):
    app.builder.build_all()


@pytest.fixture
def index(app, build_all):
    # normalize script tag for compat to Sphinx<4
    return (app.outdir / "index.html").read_text().replace("<script >", "<script>")


@pytest.mark.sphinx("html", testroot="basic")
def test_html_raw(index):
    assert "mermaid.run()" in index
    assert (
        '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"></script>'
        in index
    )
    assert '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs";import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.1.4/dist/mermaid-layout-elk.esm.min.mjs";mermaid.registerLayoutLoaders(elkLayouts);mermaid.initialize({startOnLoad:false});</script>' in index
    assert (
        '<pre id="participants" class="mermaid">\n        sequenceDiagram\n   participant Alice\n   participant Bob\n   Alice-&gt;John: Hello John, how are you?\n    </pre>'
        in index
    )


@pytest.mark.sphinx("html", testroot="basic")
def test_html_zoom_option(index, app):
    assert "mermaid.run()" in index
    assert "svg.call(zoom);" not in index
    zoom_page = (app.outdir / "zoom.html").read_text().replace("<script >", "<script>")
    assert "svg.call(zoom);" in zoom_page

    # the first diagram has no id
    assert '<pre id="participants" class="mermaid">\n        sequenceDiagram' in zoom_page

    # the second has id and its loaded in the zooming code.
    pre_id = re.findall(
        r'<pre data-zoom-id="(id\-[a-fA-F0-9-]+)" class="mermaid">\n\s+flowchart TD', zoom_page
    )
    assert f'var svgs = d3.selectAll(".mermaid[data-zoom-id={pre_id[0]}] svg")' in zoom_page


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_d3_zoom": True})
def test_html_zoom_option_global(index):
    assert "mermaid.run()" in index
    assert "svg.call(zoom);" in index
    

@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_d3_zoom": False})
def test_html_no_zoom(index):
    assert "mermaid.run()" in index
    assert "svg.call(zoom);" not in index
    

@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_version": "10.3.0", "mermaid_include_elk": ""})
def test_conf_mermaid_version(app, index):
    assert "mermaid.run()" in index
    assert app.config.mermaid_version == "10.3.0"
    assert (
        '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@10.3.0/dist/mermaid.esm.min.mjs"></script>'
        in index
    )


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_use_local": "test", "mermaid_include_elk": ""})
def test_conf_mermaid_local(app, index):
    assert "mermaid.run()" in index
    assert "mermaid.min.js" not in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_use_local": "test", "mermaid_elk_use_local": "test"})
def test_conf_mermaid_elk_local(app, index):
    assert "mermaid.run()" in index
    assert "mermaid.min.js" not in index
    assert "mermaid-layout-elk.esm.min.mjs" not in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"d3_version": "1.2.3", "mermaid_include_elk": ""})
def test_conf_d3_version(app, index):
    assert "mermaid.run()" in index
    assert app.config.d3_version == "1.2.3"
    assert (
        '<script src="https://cdn.jsdelivr.net/npm/d3@1.2.3/dist/d3.min.js"></script>'
        in index
    )


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"d3_use_local": "test"})
def test_conf_d3_local(app, index):
    assert "d3" not in index


@pytest.mark.sphinx(
    "html", testroot="basic", confoverrides={"mermaid_init_js": "custom script;"}
)
def test_mermaid_init_js(index):
    assert "mermaid.run()" in index
    assert '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"; mermaid.initialize({startOnLoad:false});</script>' not in index
    assert '<script type="module">custom script;</script>' in index


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_include_elk": "latest"})
def test_mermaid_with_elk(app, index):
    assert "mermaid.run()" in index
    assert (
        '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"></script>'
        in index
    )


@pytest.mark.sphinx("html", testroot="markdown")
def test_html_raw_from_markdown(index):
    assert "mermaid.run()" in index
    assert (
        '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"></script>'
        in index
    )
    assert '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs";import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.1.4/dist/mermaid-layout-elk.esm.min.mjs";mermaid.registerLayoutLoaders(elkLayouts);mermaid.initialize({startOnLoad:false});</script>' in index
    assert (
        '<pre align="center" id="participants" class="mermaid align-center">\n            sequenceDiagram\n      participant Alice\n      participant Bob\n      Alice-&gt;John: Hello John, how are you?\n    </pre>'
        in index
    )
