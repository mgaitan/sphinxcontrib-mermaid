from recommonmark.parser import CommonMarkParser
from recommonmark.transform import AutoStructify

extensions = ['recommonmark', 'sphinxcontrib.mermaid']
exclude_patterns = ['_build']

source_parsers = {
    '.md': CommonMarkParser
}

def setup(app):
    app.add_transform(AutoStructify)