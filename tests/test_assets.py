import json
from pathlib import Path

import sphinxcontrib.mermaid

ASSETS = Path(sphinxcontrib.mermaid.__file__).parent / "_static" / "sphinxcontrib-mermaid"


def test_vendored_assets_present():
    for rel in [
        "sphinxcontrib-mermaid.js",
        "sphinxcontrib-mermaid.css",
        "mermaid/mermaid.esm.min.mjs",
        "mermaid-zenuml/mermaid-zenuml.esm.min.mjs",
        "mermaid-layout-tidy-tree/mermaid-layout-tidy-tree.esm.min.mjs",
        "licenses/mermaid-LICENSE",
    ]:
        assert (ASSETS / rel).is_file(), rel
    assert any((ASSETS / "mermaid/chunks/mermaid.esm.min").glob("*.mjs"))
    assert not list(ASSETS.rglob("*.map"))
    assert json.loads((ASSETS / "versions.json").read_text()) == {"mermaid": "12.2.0", "zenuml": "1.0.1", "tidyTree": "1.0.1"}
