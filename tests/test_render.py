import json
import re
import sys
from pathlib import Path

import pytest

RECORD = [sys.executable, str(Path(__file__).parent / "roots/test-render/mmdc_record")]


def _record(app):
    return json.loads((app.outdir / "_images/mmdc-record.json").read_text())


@pytest.mark.sphinx(
    "html",
    testroot="render",
    freshenv=True,
    confoverrides={"mermaid_cmd": RECORD, "mermaid_output_format": "png", "mermaid_config": {"theme": "forest"}},
)
def test_mmdc_receives_global_config(app):
    app.build(force_all=True)
    assert _record(app)["config"] == {"theme": "forest"}


@pytest.mark.sphinx("html", testroot="render", freshenv=True, confoverrides={"mermaid_cmd": RECORD, "mermaid_output_format": "png"})
def test_mmdc_without_config_has_no_config_file(app):
    app.build(force_all=True)
    assert "--configFile" not in _record(app)["args"]


@pytest.mark.sphinx("html", testroot="render", freshenv=True, confoverrides={"mermaid_cmd": RECORD, "mermaid_output_format": "png"})
def test_static_img_gets_size(app):
    app.build(force_all=True)
    index = (app.outdir / "index.html").read_text()
    assert re.search(r'<img src="[^"]+" alt="[^"]*" class="mermaid" style="width: 600px; height: 300px"', index)


@pytest.mark.sphinx("html", testroot="render", freshenv=True, confoverrides={"mermaid_cmd": RECORD, "mermaid_output_format": "png", "rst_prolog": ""})
def test_static_alt_escaped(app):
    (app.srcdir / "index.rst").write_text('Render\n------\n\n.. mermaid::\n   :alt: a "b" <c>\n\n   graph TD\n      a --> b\n')
    app.build(force_all=True)
    index = (app.outdir / "index.html").read_text()
    assert 'alt="a &quot;b&quot; &lt;c&gt;"' in index
