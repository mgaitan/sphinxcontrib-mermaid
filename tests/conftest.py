from pathlib import Path

import pytest

pytest_plugins = 'sphinx.testing.fixtures'


@pytest.fixture(scope='session')
def rootdir():
    return Path(__file__).parent.absolute() / 'roots'