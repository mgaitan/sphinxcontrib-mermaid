import pytest

from sphinxcontrib.mermaid import mermaid
from sphinxcontrib.mermaid.autoclassdiag import class_diagram


@pytest.fixture(autouse=True)
def shapes(rootdir, monkeypatch):
    monkeypatch.syspath_prepend(str(rootdir / "test-autoclasstree"))


def test_multiple_inheritance_declares_each_edge_once():
    assert class_diagram("shapes.Squircle", full=True) == (
        "classDiagram\n  Round <|-- Squircle\n  Shape <|-- Round\n  Shape <|-- Square\n  Square <|-- Squircle"
    )


def test_named_class_without_bases_is_drawn():
    assert class_diagram("shapes.Lonely") == "classDiagram\n  class Lonely"


def test_strict_module_draws_classes_without_bases():
    assert class_diagram("shapes", strict=True, namespace="shapes") == (
        "classDiagram\n  class Lonely\n  class ShapeError\n  Round <|-- Squircle\n  Shape <|-- Round\n  Shape <|-- Square\n  Square <|-- Squircle"
    )


def test_module_without_strict_draws_only_inheritance():
    assert "class " not in class_diagram("shapes")


def _codes(app):
    app.build(force_all=True)
    doctree = app.env.get_and_resolve_doctree("index", app.builder)
    return {n["ids"][0]: n["code"] for n in doctree.findall(mermaid)}


@pytest.mark.sphinx("html", testroot="autoclasstree", freshenv=True)
def test_links_resolve_documented_classes(app):
    linked = _codes(app)["linked"]
    assert '  link Shape "api.html#shapes.Shape" _self' in linked
    assert '  link Round "api.html#shapes.Round" _self' in linked
    assert '  link Lonely "#shapes.Lonely" _self' in linked
    assert '  link Exception "https://docs.python.org/3/library/exceptions.html#Exception" _self' in linked
    assert "link Square " not in linked
    assert "link ShapeError " not in linked
    assert "api.html#shapes.Shape" in (app.outdir / "index.html").read_text(encoding="utf-8")


@pytest.mark.sphinx("html", testroot="autoclasstree", freshenv=True)
def test_links_are_opt_in(app):
    assert "link " not in _codes(app)["unlinked"]
