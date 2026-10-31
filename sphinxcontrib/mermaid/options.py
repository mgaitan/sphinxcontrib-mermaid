"""Parse Mermaid frontmatter and per-diagram sizing options."""

from __future__ import annotations

import re

import yaml
from docutils.parsers.rst import directives

SPHINX_KEYS = ("fit", "zoom", "fullscreen", "width", "height")

_FRONTMATTER = re.compile(r"^---[ \t]*\n(?:(.*?)\n)?---[ \t]*(?:\n|$)", re.DOTALL)
_TRUE = {"", "true", "yes", "on", "1"}
_FALSE = {"false", "no", "off", "0"}


def _mapping(value, what):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{what} must be a mapping")  # noqa: TRY004 - user input, reported as a warning
    return value


def split_frontmatter(source: str) -> tuple[dict, str]:
    """Split a leading ``---`` YAML block from Mermaid source."""
    stripped = source.lstrip("\n")
    if not stripped.startswith("---"):
        return {}, source
    match = _FRONTMATTER.match(stripped)
    if not match:
        raise ValueError("unterminated Mermaid frontmatter")
    try:
        meta = yaml.safe_load(match.group(1) or "")
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Mermaid frontmatter: {exc}") from exc
    return _mapping(meta, "Mermaid frontmatter"), stripped[match.end() :]


def parse_config(value: str | dict) -> dict:
    """Parse a Mermaid config given as YAML/JSON text or a mapping."""
    if isinstance(value, str):
        try:
            value = yaml.safe_load(value)
        except yaml.YAMLError as exc:
            raise ValueError(f"invalid config: {exc}") from exc
    return _mapping(value, "config")


def _bool(value, key) -> bool:
    if value is None or isinstance(value, bool):
        return value is not False
    text = str(value).strip().lower()
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    raise ValueError(f"{key} must be a boolean, not {value!r}")


def parse_zoom(value: str | bool | None) -> bool:
    return _bool(value, "zoom")


def _length(validator, key, value) -> str:
    try:
        result = validator(str(value))
    except ValueError as exc:
        raise ValueError(f"invalid {key}: {exc}") from exc
    return f"{result}px" if re.fullmatch(r"[\d.]+", result) else result.replace(" ", "")


def validate_sphinx_options(raw: dict) -> dict:
    """Normalize the sphinx-side keys of ``raw``, ignoring all others."""
    result = {}
    for key in SPHINX_KEYS:
        if key not in raw:
            continue
        value = raw[key]
        if key == "fit":
            if value not in ("auto", "contain"):
                raise ValueError(f"fit must be 'auto' or 'contain', not {value!r}")
            result[key] = value
        elif key in ("zoom", "fullscreen"):
            result[key] = _bool(value, key)
        elif key == "width":
            result[key] = _length(directives.length_or_percentage_or_unitless, key, value)
        else:
            result[key] = _length(directives.length_or_unitless, key, value)
    return result


def build_source(mermaid_meta: dict, body: str) -> str:
    """Prefix ``body`` with Mermaid frontmatter when there is any."""
    if not mermaid_meta:
        return body
    return "---\n" + yaml.safe_dump(mermaid_meta, sort_keys=False, allow_unicode=True) + "---\n" + body


def deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        result[key] = deep_merge(result[key], value) if isinstance(result.get(key), dict) and isinstance(value, dict) else value
    return result
