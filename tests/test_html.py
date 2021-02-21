import pytest

@pytest.fixture
def content(app):
    app.builder.build_all()
    return (app.outdir / 'index.html').read_text()


@pytest.mark.sphinx('html', testroot="basic")
def test_html_raw(content):
    assert '<script src="https://unpkg.com/mermaid/dist/mermaid.min.js"></script>' in content
    assert "<script>mermaid.initialize({startOnLoad:true});</script>" in content
    assert """<div class="mermaid">
            sequenceDiagram
   participant Alice
   participant Bob
   Alice-&gt;John: Hello John, how are you?
        </div>""" in content


@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_version': '8.3'})
def test_conf_mermaid_version(app, content):
    assert app.config.mermaid_version == "8.3"
    assert '<script src="https://unpkg.com/mermaid@8.3/dist/mermaid.min.js"></script>' in content


@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_version': None})
def test_conf_mermaid_no_version(app, content):
    # requires local mermaid
    assert 'mermaid.min.js' not in content


@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_init_js': "<script>custom script;</script>"})
def test_mermaid_init_js(content):
    assert "<script>mermaid.initialize({startOnLoad:true});</script>" not in content
    assert '<script>custom script;</script><div class="mermaid">' in content
