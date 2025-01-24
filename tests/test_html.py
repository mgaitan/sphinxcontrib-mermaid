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

@pytest.mark.sphinx("html", testroot="file")
def test_html_raw__file_input__correctly_parsed(index):
    assert "mermaid.run()" in index
    assert (
            '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"></script>'
            in index
    )
    assert '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs";import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.1.4/dist/mermaid-layout-elk.esm.min.mjs";mermaid.registerLayoutLoaders(elkLayouts);mermaid.initialize({startOnLoad:false});</script>' in index
    assert '<pre id="participants" class="mermaid">' in index
    assert 'sequenceDiagram' in index
    assert 'participant Alice' in index
    assert 'participant Bob' in index
    assert 'Alice-&gt;John: Hello John, how are you?' in index

@pytest.mark.sphinx("html", testroot="file_content")
def test_html_raw__file_content_input__warning(index, warning):
    assert "mermaid.run()" not in index
    assert "Mermaid directive cannot have both content and " "a filename argument" in warning.getvalue()


@pytest.mark.sphinx("html", testroot="file_not_found")
def test_html_raw__file_not_available__warning(index, warning):
    assert "mermaid.run()" not in index
    assert "External Mermaid file" in warning.getvalue()
    assert "invalid_file_name.mmd' not found or reading it failed" in warning.getvalue()

@pytest.mark.sphinx("html", testroot="file_empty")
def test_html_raw__file_empty__warning(index, warning):
    assert "mermaid.run()" in index
    assert 'Ignoring "mermaid" directive without content' in warning.getvalue()


@pytest.mark.sphinx("html", testroot="basic_config")
def test_html_raw__inline_config__config_available(index):
    assert "mermaid.run()" in index
    assert (
            '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"></script>'
            in index
    )
    assert '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs";import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.1.4/dist/mermaid-layout-elk.esm.min.mjs";mermaid.registerLayoutLoaders(elkLayouts);mermaid.initialize({startOnLoad:false});</script>' in index
    assert (
            '---\nconfig:\n  theme: forest\n\n---\n'
            in index
    )


@pytest.mark.sphinx("html", testroot="basic_title")
def test_html_raw__title__title_available(index):
    assert "mermaid.run()" in index
    assert (
            '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"></script>'
            in index
    )
    assert '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs";import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.1.4/dist/mermaid-layout-elk.esm.min.mjs";mermaid.registerLayoutLoaders(elkLayouts);mermaid.initialize({startOnLoad:false});</script>' in index
    assert (
            '---\ntitle: test title\n---\n'
            in index
    )

@pytest.mark.sphinx("html", testroot="basic_caption")
def test_html_raw__caption__caption_available(index):
    assert "mermaid.run()" in index
    assert (
            '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"></script>'
            in index
    )
    assert '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs";import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.1.4/dist/mermaid-layout-elk.esm.min.mjs";mermaid.registerLayoutLoaders(elkLayouts);mermaid.initialize({startOnLoad:false});</script>' in index
    assert (
            '<figure class="align-default" id="participants">\n<pre  class="mermaid">\n        sequenceDiagram\n   participant Alice\n   participant Bob\n   Alice-&gt;John: Hello John, how are you?\n    </pre><figcaption>\n<p><span class="caption-text">A simple sequence diagram</span><a class="headerlink" href="#participants" title="Link to this image">'
            in index
    )

@pytest.mark.sphinx("html", testroot="basic_caption_align")
def test_html_raw__caption_align__caption_available(index):
    assert "mermaid.run()" in index
    assert (
            '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs"></script>'
            in index
    )
    assert '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.2.0/dist/mermaid.esm.min.mjs";import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.1.4/dist/mermaid-layout-elk.esm.min.mjs";mermaid.registerLayoutLoaders(elkLayouts);mermaid.initialize({startOnLoad:false});</script>' in index
    assert (
            '<figure class="align-center" id="participants">\n<pre  class="mermaid">\n        sequenceDiagram\n   participant Alice\n   participant Bob\n   Alice-&gt;John: Hello John, how are you?\n    </pre><figcaption>\n<p><span class="caption-text">A simple sequence diagram</span><a class="headerlink" href="#participants" title="Link to this image">'
            in index
    )