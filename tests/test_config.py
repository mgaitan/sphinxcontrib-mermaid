import pytest
from sphinx.errors import ConfigError


@pytest.mark.parametrize(
    "name,hint",
    [
        ("mermaid_d3_zoom", "mermaid_zoom"),
        ("mermaid_init_config", "mermaid_config"),
        ("mermaid_include_elk", "ELK"),
        ("d3_version", "d3"),
        ("mermaid_fullscreen_button", "mermaid_toolbar"),
        ("mermaid_use_local", "mermaid_base_url"),
    ],
)
def test_removed_setting_errors(make_app, rootdir, name, hint):
    with pytest.raises(ConfigError, match=f"{name} was removed in sphinxcontrib-mermaid 3.0: .*{hint}"):
        make_app("html", srcdir=rootdir / "test-basic", confoverrides={name: True})


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_version": "11.4.0"})
def test_version_without_remote_warns(app):
    assert "mermaid_version is ignored unless mermaid_base_url is a remote URL; using Mermaid 12.2.0" in app._warning.getvalue()


def test_cdn_old_version_errors(make_app, rootdir):
    with pytest.raises(ConfigError, match="12.0.0"):
        make_app(
            "html", srcdir=rootdir / "test-basic", confoverrides={"mermaid_base_url": "https://cdn.jsdelivr.net/npm", "mermaid_version": "11.4.0"}
        )


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_base_url": "https://cdn.jsdelivr.net/npm", "mermaid_version": "latest"})
def test_cdn_latest_allowed(app):
    assert "mermaid_version" not in app._warning.getvalue()


@pytest.mark.parametrize("overrides", [{"mermaid_toolbar": "sometimes"}, {"mermaid_fit": "cover"}])
def test_invalid_choice_errors(make_app, rootdir, overrides):
    with pytest.raises(ConfigError, match=next(iter(overrides))):
        make_app("html", srcdir=rootdir / "test-basic", confoverrides=overrides)


@pytest.mark.sphinx("html", testroot="basic")
def test_defaults(app):
    c = app.config
    assert (c.mermaid_base_url, c.mermaid_config, c.mermaid_extensions, c.mermaid_zoom, c.mermaid_fullscreen) == ("", {}, [], False, True)
    assert (c.mermaid_toolbar, c.mermaid_fit, c.mermaid_width, c.mermaid_height) == ("always", "auto", None, None)
    assert (c.mermaid_max_height, c.mermaid_min_font_scale, c.mermaid_version) == ("70vh", 0.7, None)


@pytest.mark.sphinx("html", testroot="basic", confoverrides={"mermaid_height": "300", "mermaid_width": 80})
def test_size_defaults_normalized(app):
    assert (app.config.mermaid_height, app.config.mermaid_width) == ("300px", "80px")


@pytest.mark.parametrize(
    "overrides",
    [{"mermaid_height": "50%"}, {"mermaid_width": "wide"}, {"mermaid_base_url": "https://cdn.jsdelivr.net/npm", "mermaid_version": "12.x"}],
)
def test_invalid_values_error(make_app, rootdir, overrides):
    with pytest.raises(ConfigError):
        make_app("html", srcdir=rootdir / "test-basic", confoverrides=overrides)
