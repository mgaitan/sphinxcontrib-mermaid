import pytest

from sphinxcontrib.mermaid.options import build_source, deep_merge, parse_config, parse_zoom, split_frontmatter, validate_sphinx_options


def test_split_frontmatter_nested_yaml():
    meta, body = split_frontmatter("---\ntitle: T\nconfig:\n  flowchart:\n    htmlLabels: false\nheight: 400\n---\nflowchart LR\n A-->B\n")
    assert meta == {"title": "T", "config": {"flowchart": {"htmlLabels": False}}, "height": 400}
    assert body == "flowchart LR\n A-->B\n"


def test_split_frontmatter_absent():
    assert split_frontmatter("graph TD\n A-->B") == ({}, "graph TD\n A-->B")


def test_split_frontmatter_leading_blank_lines():
    assert split_frontmatter("\n\n---\ntitle: T\n---\ngraph TD") == ({"title": "T"}, "graph TD")


@pytest.mark.parametrize("bad", ["---\ntitle: x\n", "---\n- a\n---\ngraph TD"])
def test_split_frontmatter_invalid(bad):
    with pytest.raises(ValueError):
        split_frontmatter(bad)


def test_parse_config_accepts_json_and_yaml():
    assert parse_config('{"layout": "elk"}') == {"layout": "elk"}
    assert parse_config("layout: elk\ntheme: forest") == {"layout": "elk", "theme": "forest"}
    assert parse_config({"a": 1}) == {"a": 1}
    with pytest.raises(ValueError):
        parse_config("[1, 2]")


@pytest.mark.parametrize("value,expected", [(None, True), ("", True), (True, True), ("false", False), (False, False), ("on", True), ("No", False)])
def test_parse_zoom(value, expected):
    assert parse_zoom(value) is expected


def test_parse_zoom_invalid():
    with pytest.raises(ValueError):
        parse_zoom("maybe")


def test_validate_sphinx_options():
    assert validate_sphinx_options({"fit": "contain", "width": "600", "height": "20em", "zoom": "false", "fullscreen": False, "title": "x"}) == {
        "fit": "contain",
        "width": "600px",
        "height": "20em",
        "zoom": False,
        "fullscreen": False,
    }
    assert validate_sphinx_options({"width": 50.5, "height": 300}) == {"width": "50.5px", "height": "300px"}
    assert validate_sphinx_options({"width": "80%"}) == {"width": "80%"}
    with pytest.raises(ValueError, match="fit"):
        validate_sphinx_options({"fit": "cover"})
    with pytest.raises(ValueError, match="height"):
        validate_sphinx_options({"height": "50%"})


def test_build_source_roundtrip():
    src = build_source({"title": "T", "config": {"layout": "elk"}}, "flowchart LR\n A-->B\n")
    assert split_frontmatter(src) == ({"title": "T", "config": {"layout": "elk"}}, "flowchart LR\n A-->B\n")
    assert build_source({}, "graph TD") == "graph TD"


def test_deep_merge():
    base = {"a": {"b": 1, "c": 2}}
    assert deep_merge(base, {"a": {"c": 3}, "d": 4}) == {"a": {"b": 1, "c": 3}, "d": 4}
    assert base == {"a": {"b": 1, "c": 2}}


def test_split_frontmatter_closing_must_start_a_line():
    assert split_frontmatter("---\ntitle: a ---\n---\ngraph TD") == ({"title": "a ---"}, "graph TD")
