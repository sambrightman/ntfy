from contextlib import contextmanager
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
