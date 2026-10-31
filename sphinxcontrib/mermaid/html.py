"""Client-side HTML output: diagram markup, runtime assets and site config."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

from docutils import nodes

from .config import ASSETS, bundled_versions, is_remote
from .directives import mermaid
from .options import split_frontmatter

_PACKAGES = {
    "mermaid": ("mermaid", "mermaid", "mermaid"),
    "diagrams": ("@mermaid-js/mermaid-zenuml", "zenuml", "mermaid-zenuml"),
    "layouts": ("@mermaid-js/layout-tidy-tree", "tidyTree", "mermaid-layout-tidy-tree"),
}


def _client_side(app) -> bool:
    # EPUB readers can't load ES modules, and its builder rejects the .mjs files.
    return app.builder.format == "html" and not app.builder.name.startswith("epub") and app.config.mermaid_output_format == "raw"


def resolve_url(value: str) -> str:
    """Resolve a URL or ``html_static_path`` path relative to the runtime's directory."""
    if is_remote(value) or value.startswith("/"):
        return value
    return "../" + value


def _package_url(base: str, package: str, version: str | None, entry: str) -> str:
    """A package's ES module: bundled, under an npm CDN (``package@version``), or a local node_modules layout."""
    if not base:
        return f"{entry}/{entry}.esm.min.mjs"
    if not is_remote(base) or version == "latest":
        version = None
    return f"{resolve_url(base.rstrip('/'))}/{package}{'@' + version if version else ''}/dist/{entry}.esm.min.mjs"


def site_config(app) -> dict:
    config = app.config
    versions = bundled_versions()
    versions["mermaid"] = config.mermaid_version or versions["mermaid"]
    urls = {key: _package_url(config.mermaid_base_url, package, versions[version], entry) for key, (package, version, entry) in _PACKAGES.items()}
    return {
        "mermaid": urls["mermaid"],
        "layouts": [urls["layouts"]],
        "diagrams": [urls["diagrams"]],
        "extensions": [resolve_url(url) for url in config.mermaid_extensions],
        "iconPacks": {name: resolve_url(url) for name, url in config.mermaid_icon_packs.items()},
        "config": config.mermaid_config,
        "lightTheme": config.mermaid_light_theme,
        "darkTheme": config.mermaid_dark_theme,
        "toolbar": config.mermaid_toolbar,
        "maxHeight": config.mermaid_max_height,
        "minFontScale": config.mermaid_min_font_scale,
    }


def _font_size(code: str):
    """The diagram's own Mermaid ``fontSize``, which sets the readable-text floor."""
    try:
        config = split_frontmatter(code)[0].get("config") or {}
    except ValueError:
        return None
    if not isinstance(config, dict):
        return None
    theme = config.get("themeVariables")
    value = config.get("fontSize", theme.get("fontSize") if isinstance(theme, dict) else None)
    try:
        return float(str(value).removesuffix("px")) if value is not None else None
    except ValueError:
        return None


def diagram_options(node, config) -> dict:
    options = node.get("options", {})
    font_size = _font_size(node.get("code", ""))
    return {
        "fit": options.get("fit", config.mermaid_fit),
        "zoom": options.get("zoom", True if config.mermaid_zoom else "auto"),
        "fullscreen": options.get("fullscreen", config.mermaid_fullscreen),
        "width": options.get("width", config.mermaid_width),
        "height": options.get("height", config.mermaid_height),
        "fontSize": int(font_size) if font_size is not None and font_size.is_integer() else font_size,
    }


def render_raw(self, node, code):
    """Emit the ``mermaid-diagram`` placeholder the runtime renders into."""
    classes = ["mermaid-diagram", *([f"align-{node['align']}"] if "align" in node else []), *node.get("classes", [])]
    attrs = {"class": " ".join(classes)}
    if node.get("ids"):
        attrs["id"] = node["ids"][0]
    attrs["data-mermaid-options"] = json.dumps(diagram_options(node, self.builder.config))
    if "alt" in node:
        # "group", not "img": the toolbar buttons and diagram links stay reachable.
        attrs["role"] = "group"
        attrs["aria-label"] = node["alt"]
    attributes = " ".join(f'{key}="{html.escape(value, quote=True)}"' for key, value in attrs.items())
    self.body.append(f'<div {attributes}><pre class="mermaid">{self.encode(code)}</pre></div>\n')
    raise nodes.SkipNode


def add_static_path(app) -> None:
    if not _client_side(app):
        return
    bundled_versions()
    app.config.html_static_path = [*app.config.html_static_path, str(ASSETS.parent)]


def add_assets(app, pagename, templatename, context, doctree) -> None:
    if not _client_side(app) or doctree is None or not doctree.next_node(mermaid):
        return
    # The runtime appends this to its config.json request so a changed config is not served stale.
    app.add_js_file("sphinxcontrib-mermaid/sphinxcontrib-mermaid.js", type="module", **{"data-mermaid-config": _config_version(app)})
    app.add_css_file("sphinxcontrib-mermaid/sphinxcontrib-mermaid.css")


def _config_text(app) -> str:
    return json.dumps(site_config(app), indent=2)


def _config_version(app) -> str:
    return hashlib.sha1(_config_text(app).encode("utf-8")).hexdigest()[:12]


def write_site_config(app):
    if not _client_side(app):
        return []
    out = Path(app.outdir) / "_static" / "sphinxcontrib-mermaid"
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_bytes(_config_text(app).encode("utf-8"))
    return []
