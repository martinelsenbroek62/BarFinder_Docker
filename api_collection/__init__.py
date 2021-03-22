# cython: language_level=3
"""EngineDialFrontend Flask App"""
from .app import init_app
from .version import VERSION

__version__ = VERSION
__all__ = ['app', 'celery']

app = init_app()  # pylint: disable=invalid-name
celery = app.celery  # pylint: disable=invalid-name
