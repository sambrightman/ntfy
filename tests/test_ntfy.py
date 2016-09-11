import os
import sys
from unittest import TestCase
from mock import patch
from testfixtures import log_capture

from .util import fake_module
import ntfy


class DummyException(Exception):
    pass


class DummyModule:
    @staticmethod
    def notify(message, title, required, retcode=None):
        raise DummyException()


class DummyDefaultModule:
    @staticmethod
    def notify(message, title, wrapped_required, retcode=None):
        raise ntfy.backends.default.DefaultNotifierError(
            DummyException(),
            DummyDefaultModule)


class DummyExitModule:
    @staticmethod
    def notify(message, title, retcode=None):
        sys.exit(1)


class OverrideBackendTestCase(TestCase):
    @patch('requests.post')
    def test_runcmd(self, mock_post):
        ret = ntfy.notify('message', 'title', {
            'backends': ['foobar'],
            'foobar': {
                'backend': 'pushover',
                'user_key': 't0k3n',
            }
        })
        self.assertEqual(0, ret)


class ErrorTestCase(TestCase):
    @log_capture()
    def test_invalid_backend(self, log):
        ret = ntfy.notify('message', 'title', {'backends': ['foobar']})
        self.assertEqual(1, ret)
        log.check(
            ('ntfy', 'ERROR', "Invalid backend foobar")
        )

    @patch('ntfy.notifier_modules', return_value={'default': DummyModule})
    @log_capture()
    def test_backend_missing_arg(self, mock_nm, log):
        ret = ntfy.notify('message', 'title',
                          config={})
        self.assertEqual(1, ret)
        log.check(
            ('ntfy', 'ERROR', "Missing arguments: set(['required'])")
        )
        self.assertIsNone(log.records[-1].exc_info)

    @patch('ntfy.notifier_modules', return_value={'default': DummyModule})
    @log_capture()
    def test_backend_unknown_arg(self, mock_nm, log):
        ret = ntfy.notify('message',
                          'title',
                          config={'default': {'required': None,
                                              'unknown': None}})
        self.assertEqual(1, ret)
        log.check(
            ('ntfy', 'ERROR', "Got unknown arguments: set(['unknown'])")
        )
        self.assertIsNone(log.records[-1].exc_info)

    @patch('ntfy.notifier_modules', return_value={'default': DummyModule})
    @log_capture()
    def test_backend_error(self, mock_nm, log):
        with fake_module(DummyModule):
            ret = ntfy.notify('message', 'title',
                              config={'default': {'required': None}})
            self.assertEqual(1, ret)
            log.check(('ntfy', 'ERROR',
                       "Failed to send notification using default"))
            exc_info = log.records[-1].exc_info
            self.assertIsNotNone(exc_info)
            self.assertIsInstance(exc_info[0], DummyException.__class__)

    @patch('ntfy.notifier_modules',
           return_value={'default': DummyDefaultModule})
    @log_capture()
    def test_backend_wrapped_missing_arg(self, mock_nm, log):
        with fake_module(DummyDefaultModule):
            ret = ntfy.notify('message', 'title', config={})
            self.assertEqual(1, ret)
            log.check(('ntfy', 'ERROR',
                       "Missing arguments: set(['wrapped_required'])"))
            exc_info = log.records[-1].exc_info
            self.assertIsNone(exc_info)

    @patch('ntfy.notifier_modules',
           return_value={'default': DummyDefaultModule})
    @log_capture()
    def test_backend_wrapped_error(self, mock_nm, log):
        with fake_module(DummyDefaultModule):
            ret = ntfy.notify('message', 'title',
                              config={'default': {'wrapped_required': None}})
            self.assertEqual(1, ret)
            log.check(('ntfy', 'ERROR',
                       "Failed to send notification using default"))
            exc_info = log.records[-1].exc_info
            self.assertIsNotNone(exc_info)
            self.assertIsInstance(exc_info[0], DummyException.__class__)

    @patch('ntfy.notifier_modules',
           return_value={'default': DummyExitModule})
    def test_backend_exit(self, mock_nm):
        with fake_module(DummyExitModule):
            self.assertRaises(SystemExit, ntfy.notify, 'message', 'title')


class NotifierModulesTestCase(TestCase):
    def test_notifier_modules(self):
        nm = ntfy.notifier_modules(dict.fromkeys(['default']))
        self.assertEqual({'default': ntfy.backends.default}, nm)

    def test_notifier_modules_missing_module(self):
        nm = ntfy.notifier_modules(dict.fromkeys(['missing']))
        self.assertEqual({'missing': None}, nm)

    def test_notifier_modules_missing_and_present(self):
        nm = ntfy.notifier_modules(dict.fromkeys(['missing', 'default']))
        self.assertEqual(nm, {'missing': None,
                              'default': ntfy.backends.default})


class TitleTestCase(TestCase):
    @patch('ntfy.getcwd', return_value='cwd')
    @patch('ntfy.gethostname', return_value='host')
    @patch('ntfy.getuser', return_value='user')
    def test_default_title(self, mock_getuser, mock_gethostname, mock_getcwd):
        t = ntfy.default_title()
        self.assertEqual('user@host:cwd', t)

    @patch('ntfy.name', 'posix')
    @patch('ntfy.getcwd', return_value=os.path.expanduser('~'))
    @patch('ntfy.gethostname', return_value='host')
    @patch('ntfy.getuser', return_value='user')
    def test_default_title_home(self,
                                mock_getuser,
                                mock_gethostname,
                                mock_getcwd):
        t = ntfy.default_title()
        self.assertEqual('user@host:~/', t)

    @patch('ntfy.name', 'nt')
    @patch('ntfy.getcwd', return_value=os.path.expanduser('~'))
    @patch('ntfy.gethostname', return_value='host')
    @patch('ntfy.getuser', return_value='user')
    def test_default_title_home_windows(self,
                                        mock_getuser,
                                        mock_gethostname,
                                        mock_getcwd):
        t = ntfy.default_title()
        self.assertEqual('user@host:{}'.format(os.path.expanduser('~')), t)
