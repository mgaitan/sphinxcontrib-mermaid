import errno
import json
import re
import sys
from pathlib import Path

import pytest

from sphinxcontrib.mermaid import render

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


@pytest.mark.sphinx("latex", testroot="render", freshenv=True, confoverrides={"mermaid_cmd": RECORD})
def test_missing_pdfcrop_skips_latex_node(app, tmp_path):
    app.config.mermaid_pdfcrop = str(tmp_path / "missing-pdfcrop")
    app.build(force_all=True)
    assert "needed to crop pdf" in app.warning.getvalue()
    assert len(list(app.outdir.glob("mermaid-*.pdf"))) == 1
    tex_files = list(app.outdir.glob("*.tex"))
    assert len(tex_files) == 1
    assert r"\sphinxincludegraphics{mermaid-" not in tex_files[0].read_text()


@pytest.mark.sphinx("latex", testroot="render", freshenv=True, confoverrides={"mermaid_cmd": RECORD})
def test_latex_render_without_pdfcrop(app):
    app.build(force_all=True)
    tex_files = list(app.outdir.glob("*.tex"))
    assert len(tex_files) == 1
    assert r"\sphinxincludegraphics{mermaid-" in tex_files[0].read_text()
    assert "cannot be run" not in app.warning.getvalue()


@pytest.mark.sphinx("latex", testroot="render", freshenv=True, confoverrides={"mermaid_cmd": RECORD})
def test_other_pdfcrop_oserror_propagates(app, monkeypatch):
    app.config.mermaid_pdfcrop = "pdfcrop"
    popen = render.Popen

    def run(args, **kwargs):
        if args[0] == "pdfcrop":
            raise PermissionError(errno.EACCES, "Permission denied")
        return popen(args, **kwargs)

    monkeypatch.setattr(render, "Popen", run)
    with pytest.raises(PermissionError):
        app.build(force_all=True)
