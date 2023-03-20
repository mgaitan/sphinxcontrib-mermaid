import pytest

@pytest.fixture
def build_all(app):
    app.builder.build_all()


@pytest.fixture
def index(app, build_all):
    # normalize script tag for compat to Sphinx<4
    return (app.outdir / 'index.html').read_text().replace("<script >", "<script>")

# Test CDN load
@pytest.mark.sphinx('html', testroot="basic")
def test_html_raw(index):
    assert """const mermaidConfig = {
    "arrowMarkerAbsolute": false,
    "fontFamily": "'trebuchet ms', verdana, arial, sans-serif;",
    "logLevel": "fatal",
    "securityLevel": "strict",
    "startOnLoad": true,
    "theme": "default"
}""" in index
    assert """<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.esm.min.mjs"; mermaid.initialize(mermaidConfig)</script>""" in index
    assert """<div class="mermaid">
            sequenceDiagram
   participant Alice
   participant Bob
   Alice-&gt;John: Hello John, how are you?
        </div>""" in index

# Test specific version
@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_version': '8.3'})
def test_conf_mermaid_version(app, index):
    assert app.config.mermaid_version == "8.3"
    assert """const mermaidConfig = {
    "arrowMarkerAbsolute": false,
    "fontFamily": "'trebuchet ms', verdana, arial, sans-serif;",
    "logLevel": "fatal",
    "securityLevel": "strict",
    "startOnLoad": true,
    "theme": "default"
}""" in index
    assert """<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@8.3/dist/mermaid.esm.min.mjs"; mermaid.initialize(mermaidConfig)</script>""" in index

# Test loading local Mermaid
@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_version': None})
def test_conf_mermaid_no_version(app, index):
    # requires local mermaid
    assert 'mermaid.min.js' not in index

# Test custom init script
@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_init_js': "custom script;"})
def test_mermaid_init_js(index):
    assert "<script>mermaid.initialize({startOnLoad:true});</script>" not in index
    assert '<script>custom script;</script>' in index

# Test theme override
@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_theme': "forest"})
def test_mermaid_theme(index):
    assert """const mermaidConfig = {
    "arrowMarkerAbsolute": false,
    "fontFamily": "'trebuchet ms', verdana, arial, sans-serif;",
    "logLevel": "fatal",
    "securityLevel": "strict",
    "startOnLoad": true,
    "theme": "forest"
}""" in index
    assert """<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.esm.min.mjs"; mermaid.initialize(mermaidConfig)</script>""" in index

# Test font family override
@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_fontfamily': "comic sans"})
def test_mermaid_theme(index):
    assert """const mermaidConfig = {
    "arrowMarkerAbsolute": false,
    "fontFamily": "comic sans",
    "logLevel": "fatal",
    "securityLevel": "strict",
    "startOnLoad": true,
    "theme": "default"
}""" in index
    assert """<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.esm.min.mjs"; mermaid.initialize(mermaidConfig)</script>""" in index

# Test log level override
@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_loglevel': "info"})
def test_mermaid_loglevel(index):
    assert """const mermaidConfig = {
    "arrowMarkerAbsolute": false,
    "fontFamily": "'trebuchet ms', verdana, arial, sans-serif;",
    "logLevel": "info",
    "securityLevel": "strict",
    "startOnLoad": true,
    "theme": "default"
}""" in index
    assert """<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.esm.min.mjs"; mermaid.initialize(mermaidConfig)</script>""" in index

# Test security level override
@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_securitylevel': "loose"})
def test_mermaid_securitylevel(index):
    assert """const mermaidConfig = {
    "arrowMarkerAbsolute": false,
    "fontFamily": "'trebuchet ms', verdana, arial, sans-serif;",
    "logLevel": "fatal",
    "securityLevel": "loose",
    "startOnLoad": true,
    "theme": "default"
}""" in index
    assert """<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.esm.min.mjs"; mermaid.initialize(mermaidConfig)</script>""" in index

# Test arrow marker absolute override
@pytest.mark.sphinx('html', testroot="basic", confoverrides={'mermaid_arrowmarkerabsolute': True})
def test_mermaid_arrowmarkerabsolute(index):
    assert """const mermaidConfig = {
    "arrowMarkerAbsolute": true,
    "fontFamily": "'trebuchet ms', verdana, arial, sans-serif;",
    "logLevel": "fatal",
    "securityLevel": "strict",
    "startOnLoad": true,
    "theme": "default"
}""" in index
    assert """<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.esm.min.mjs"; mermaid.initialize(mermaidConfig)</script>""" in index

# Test Markdown rendering
@pytest.mark.sphinx('html', testroot="markdown")
def test_html_raw_from_markdown(index):
    assert """<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.esm.min.mjs"; mermaid.initialize(mermaidConfig)</script>""" in index
    assert """const mermaidConfig = {
    "arrowMarkerAbsolute": false,
    "fontFamily": "'trebuchet ms', verdana, arial, sans-serif;",
    "logLevel": "fatal",
    "securityLevel": "strict",
    "startOnLoad": true,
    "theme": "default"
}""" in index
    assert """
<div class="mermaid">
                sequenceDiagram
      participant Alice
      participant Bob
      Alice-&gt;John: Hello John, how are you?
        </div>""" in index