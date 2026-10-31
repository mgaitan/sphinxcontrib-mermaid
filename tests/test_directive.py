import pytest

from sphinxcontrib.mermaid import mermaid
from sphinxcontrib.mermaid.options import split_frontmatter


def _nodes(app):
    app.build(force_all=True)
    return list(app.env.get_doctree("index").findall(mermaid))


def _by_id(app):
    return {(n["ids"] or n.parent["ids"])[0]: n for n in _nodes(app)}


@pytest.mark.sphinx("html", testroot="directive")
def test_directive_options(app):
    nodes = _by_id(app)
    assert nodes["sized"]["options"] == {"width": "600px", "height": "300px", "fit": "contain", "zoom": False}
    assert split_frontmatter(nodes["sized"]["code"])[0] == {"title": "Hello", "config": {"theme": "forest"}}
    assert nodes["fm"]["options"] == {"height": "500px", "zoom": True}
    assert split_frontmatter(nodes["fm"]["code"]) == ({"config": {"layout": "elk"}}, "flowchart LR\n  A --> B")
    assert nodes["plain"]["options"] == {}
    assert not nodes["plain"]["code"].startswith("---")
    assert nodes["external"]["options"] == {"fit": "contain"}
    assert nodes["captioned"].parent.tagname == "figure"


@pytest.mark.sphinx("html", testroot="directive", freshenv=True)
def test_invalid_option_warns_not_crashes(app):
    nodes = _by_id(app)
    assert "fit must be 'auto' or 'contain'" in app._warning.getvalue()
    assert nodes["invalid"]["options"] == {}


@pytest.mark.sphinx("html", testroot="myst")
def test_myst_nested_frontmatter_recovered(app):
    first, second = _nodes(app)
    assert split_frontmatter(first["code"])[0] == {"title": "T", "config": {"flowchart": {"htmlLabels": False}}}
    assert first["options"] == {"height": "400px"}
    assert second["options"] == {"zoom": True}


@pytest.mark.sphinx("html", testroot="myst-edge", freshenv=True)
def test_myst_recovery_edge_cases(app):
    colon, quoted, included = _nodes(app)
    assert "myclass" in colon["classes"]
    assert split_frontmatter(colon["code"])[0] == {"config": {"layout": "elk"}}
    assert split_frontmatter(quoted["code"])[0] == {"config": {"theme": "forest"}}
    assert split_frontmatter(included["code"])[0] == {"config": {"flowchart": {"htmlLabels": False}}}
    assert "flattened" not in app._warning.getvalue()


@pytest.mark.sphinx("html", testroot="directive", freshenv=True)
def test_rst_frontmatter_class(app):
    assert "fromfm" in _by_id(app)["fmclass"]["classes"]


@pytest.mark.sphinx("html", testroot="myst-fallback", freshenv=True)
def test_myst_unrecoverable_frontmatter_warns(app):
    _nodes(app)
    assert "nested YAML in MyST directive options is flattened; use single-line JSON for config" in app._warning.getvalue()
