import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
extensions = ["sphinxcontrib.mermaid", "rawnode"]
exclude_patterns = ["_build"]
