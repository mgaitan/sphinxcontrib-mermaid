from pathlib import Path

import pytest
import sphinx
from packaging.version import Version


pytest_plugins = 'sphinx.testing.fixtures'


@pytest.fixture(scope='session')
def rootdir():
    if Version(sphinx.__version__) < Version('7.0.0'):
        from sphinx.testing.path import path
        return path(__file__).parent.abspath() / 'roots'
    return Path(__file__).parent.absolute() / 'roots'
