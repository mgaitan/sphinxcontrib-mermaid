import pytest
import re


@pytest.fixture
def build_all(app):
    app.builder.build_all()


@pytest.fixture
def index(app, build_all):
    # normalize script tag for compat to Sphinx<4
    return (app.outdir / "index.html").read_text().replace("<script >", "<script>")


@pytest.mark.sphinx("html", testroot="basic")
def test_html_raw(index):
    assert (
        '<script src="https://unpkg.com/mermaid@10.2.0/dist/mermaid.min.js"></script>'
        in index
    )
    assert "<script>mermaid.initialize({startOnLoad:true});</script>" in index
    assert (
        """<div class="mermaid">
            sequenceDiagram
   participant Alice
   participant Bob
   Alice-&gt;John: Hello John, how are you?
        </div>"""
        in index
    )


@pytest.mark.sphinx("html", testroot="basic")
def test_html_zoom_option(index, app):
    assert "svg.call(zoom);" not in index
    zoom_page = (app.outdir / "zoom.html").read_text().replace("<script >", "<script>")
    assert "svg.call(zoom);" in zoom_page

    # the first diagram has no id
    assert '<div class="mermaid">\n            sequenceDiagram' in zoom_page

    # the second has id and its loaded in the zooming code.
    div_id = re.findall(
        r'<div id="(id\-[a-fA-F0-9-]+)" class="mermaid">\n\s+flowchart TD', zoom_page
    )
    assert f'var svgs = d3.selectAll(".mermaid#{div_id[0]} svg")' in zoom_page


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_d3_zoom": True})
def test_html_zoom_option_global(index):
    assert "svg.call(zoom);" in index
    

@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_version": "8.3"})
def test_conf_mermaid_version(app, index):
    assert app.config.mermaid_version == "8.3"
    assert (
        '<script src="https://unpkg.com/mermaid@8.3/dist/mermaid.min.js"></script>'
        in index
    )


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_version": None})
def test_conf_mermaid_no_version(app, index):
    # requires local mermaid
    assert "mermaid.min.js" not in index


@pytest.mark.sphinx(
    "html", testroot="basic", confoverrides={"mermaid_init_js": "custom script;"}
)
def test_mermaid_init_js(index):
    assert "<script>mermaid.initialize({startOnLoad:true});</script>" not in index
    assert "<script>custom script;</script>" in index


@pytest.mark.sphinx("html", testroot="markdown")
def test_html_raw_from_markdown(index):
    assert (
        '<script src="https://unpkg.com/mermaid@10.2.0/dist/mermaid.min.js"></script>'
        in index
    )
    assert "<script>mermaid.initialize({startOnLoad:true});</script>" in index
    assert (
        """
<div class="mermaid">
                sequenceDiagram
      participant Alice
      participant Bob
      Alice-&gt;John: Hello John, how are you?
        </div>"""
        in index
    )
