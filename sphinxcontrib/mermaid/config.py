"""Configuration values for sphinxcontrib-mermaid."""

from __future__ import annotations

import json
from pathlib import Path

from packaging.version import InvalidVersion, Version
from sphinx.errors import ConfigError, ExtensionError
from sphinx.util import logging

from .options import validate_sphinx_options

logger = logging.getLogger(__name__)

ASSETS = Path(__file__).parent / "_static" / "sphinxcontrib-mermaid"

_REMOVED = object()
_ELK = "ELK is built into Mermaid 12"
_ZENUML = "ZenUML is bundled; use mermaid_extensions for custom builds"
_BUTTON = "use mermaid_toolbar and --mermaid-* CSS variables"
REMOVED = {
    "mermaid_init_config": "use mermaid_config",
    "mermaid_d3_zoom": "use mermaid_zoom",
    "d3_version": "d3 is no longer used",
    "d3_use_local": "d3 is no longer used",
    "mermaid_include_elk": _ELK,
    "mermaid_elk_version": _ELK,
    "mermaid_elk_use_local": _ELK,
    "mermaid_include_zenuml": _ZENUML,
    "mermaid_zenuml_version": _ZENUML,
    "mermaid_zenuml_use_local": _ZENUML,
    "mermaid_fullscreen_button": _BUTTON,
    "mermaid_fullscreen_button_opacity": _BUTTON,
    "mermaid_js_priority": "no longer needed",
    "mermaid_include_mindmap": "mindmap is built into Mermaid",
    "mermaid_use_local": "use mermaid_base_url",
}

_VALUES = {
    # Static output via mermaid-cli
    "mermaid_output_format": ("raw", "html"),
    "mermaid_cmd": ("mmdc", "html"),
    "mermaid_cmd_shell": (False, "html"),
    "mermaid_pdfcrop": ("", "html"),
    "mermaid_params": ([], "html"),
    "mermaid_verbose": (False, "html"),
    "mermaid_sequence_config": (None, "html"),
    # Mermaid itself
    "mermaid_config": ({}, "env"),
    "mermaid_version": (None, "html"),
    "mermaid_base_url": ("", "html"),
    "mermaid_extensions": ([], "html"),
    "mermaid_icon_packs": ({}, "html"),
    "mermaid_light_theme": ("default", "html"),
    "mermaid_dark_theme": ("dark", "html"),
    # Sizing and interaction
    "mermaid_zoom": (False, "html"),
    "mermaid_fullscreen": (True, "html"),
    "mermaid_toolbar": ("always", "html"),
    "mermaid_fit": ("auto", "html"),
    "mermaid_width": (None, "html"),
    "mermaid_height": (None, "html"),
    "mermaid_max_height": ("70vh", "html"),
    "mermaid_min_font_scale": (0.7, "html"),
}


def bundled_versions() -> dict[str, str]:
    try:
        return json.loads((ASSETS / "versions.json").read_text(encoding="utf-8"))
    except OSError as exc:
        raise ExtensionError("sphinxcontrib-mermaid assets are missing; run 'pnpm --dir js install && pnpm --dir js build'") from exc


def is_remote(value: str) -> bool:
    return value.startswith(("http://", "https://", "//"))


def _validate(app, config):
    for name, hint in REMOVED.items():
        if config[name] is not _REMOVED:
            raise ConfigError(f"{name} was removed in sphinxcontrib-mermaid 3.0: {hint}")
    if config.mermaid_toolbar not in ("always", "hover"):
        raise ConfigError(f"mermaid_toolbar must be 'always' or 'hover', not {config.mermaid_toolbar!r}")
    if config.mermaid_fit not in ("auto", "contain"):
        raise ConfigError(f"mermaid_fit must be 'auto' or 'contain', not {config.mermaid_fit!r}")
    for key in ("width", "height"):
        name = f"mermaid_{key}"
        if config[name] is not None:
            try:
                config[name] = validate_sphinx_options({key: config[name]})[key]
            except ValueError as exc:
                raise ConfigError(f"{name}: {exc}") from exc
    version = config.mermaid_version
    if version and not is_remote(config.mermaid_base_url):
        logger.warning(
            "mermaid_version is ignored unless mermaid_base_url is a remote URL; using Mermaid %s",
            bundled_versions()["mermaid"],
        )
    elif version and version != "latest":
        try:
            too_old = Version(version) < Version("12.0.0")
        except InvalidVersion as exc:
            raise ConfigError(f"mermaid_version must be a version number or 'latest', not {version!r}") from exc
        if too_old:
            raise ConfigError(f"mermaid_version must be 12.0.0 or later, not {version!r}")


def register(app) -> None:
    for name, (default, rebuild) in _VALUES.items():
        app.add_config_value(name, default, rebuild)
    for name in REMOVED:
        app.add_config_value(name, _REMOVED, "")
    app.connect("config-inited", _validate)
