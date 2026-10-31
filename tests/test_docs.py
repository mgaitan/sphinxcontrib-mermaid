import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

DOCS = Path(__file__).parent.parent / "docs"


@pytest.mark.skipif(not importlib.util.find_spec("myst_parser") or not importlib.util.find_spec("furo"), reason="docs extras not installed")
def test_docs_build_without_warnings(tmp_path):
    subprocess.run([sys.executable, "-m", "sphinx", "-W", "--keep-going", "-q", "-b", "html", str(DOCS), str(tmp_path)], check=True)
    assert (tmp_path / "src/examples.html").is_file()
    assert (tmp_path / "src/configuration.html").is_file()
