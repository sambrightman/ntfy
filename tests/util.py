from contextlib import contextmanager, nested
from mock import MagicMock
import sys


@contextmanager
def fake_module(fake_module, name=None):
    if name is None:
        name = fake_module.__name__
    real_module = sys.modules.get(name)
    sys.modules[name] = fake_module
    yield
    if real_module is not None:
        sys.modules[name] = real_module
    else:
        del sys.modules[name]


@contextmanager
def mock_modules(*names):
    managers = (fake_module(MagicMock(), name) for name in names)
    with nested(*managers):
        yield
