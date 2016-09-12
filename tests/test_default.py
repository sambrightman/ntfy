from unittest import TestCase
from mock import patch, MagicMock
from testfixtures import log_capture

from ntfy.backends.default import (notify,
                                   SUPPORTED_PLATFORMS,
                                   DefaultNotifierError)
from .util import mock_modules


class TestDefault(TestCase):
    @patch('ntfy.backends.default.platform')
    @log_capture('ntfy.backends.default')
    def test_supported_platforms(self, mock_platform, log):
        with mock_modules('dbus',
                          'win32api', 'win32gui', 'win32con',
                          'Foundation', 'objc'):
            for platform in SUPPORTED_PLATFORMS:
                sw = MagicMock(side_effect=lambda os: platform.startswith(os))
                mock_platform.startswith = sw
                notify('title', 'message')
                log.check()

    @patch('ntfy.backends.default.platform', 'foobar')
    @patch('ntfy.backends.default.import_module')
    @log_capture()
    def test_unsupported_platform(self, mock_import_module, log):
        notify('title', 'message')
        mock_import_module.assert_not_called()
        log.check(
            ('ntfy.backends.default', 'ERROR', 'Unsupported platform foobar')
        )

    @patch('ntfy.backends.default.import_module')
    def test_defaultnotifiererror(self, mock_import_module):
        mock_fail = MagicMock(side_effect=Exception())
        mock_import_module.return_value.notify = mock_fail
        self.assertRaises(DefaultNotifierError, notify, 'title', 'message')
