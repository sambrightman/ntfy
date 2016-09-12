from sys import platform
from importlib import import_module
import logging


SUPPORTED_PLATFORMS = ['linux', 'win32', 'darwin']


class DefaultNotifierError(Exception):
    def __init__(self, exception, module):
        super(DefaultNotifierError, self).__init__(
            'caused by {}'.format(repr(exception))
        )
        self.exception = exception
        self.module = module


def notify(title, message, **kwargs):
    """
    This backend automatically selects the correct desktop notification backend
    for your operating system.
    """
    for os in SUPPORTED_PLATFORMS:
        if platform.startswith(os):
            module = import_module('ntfy.backends.{}'.format(os))
            try:
                module.notify(title=title, message=message, **kwargs)
            except Exception as e:
                raise DefaultNotifierError(e, module)
            return
    logging.getLogger(__name__).error(
        'Unsupported platform {}'.format(platform))
