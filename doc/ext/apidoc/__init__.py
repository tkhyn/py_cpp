import os

from .version import get_version
from .builder import build_apidoc


def setup(app):
    if os.environ.get('__BUILD_APIDOC__', False):
        app.connect("builder-inited", build_apidoc)
    return {'version': get_version()}
