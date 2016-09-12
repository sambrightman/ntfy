from unittest import TestCase, main
from sys import version_info
from mock import patch, mock_open, MagicMock, ANY

from .util import mock_modules
from ntfy.cli import main as ntfy_main

py = version_info.major
builtin_module = '__builtin__' if py == 2 else 'builtins'


class TestIntegration(TestCase):
    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    @patch('ntfy.backends.pushover.requests.post')
    def test_pushover(self, mock_post, mock_yamlload):
        mock_yamlload.return_value = {
            'backends': ['pushover'],
            'pushover': {'user_key': MagicMock()},
        }
        ret = ntfy_main(['send', 'foobar'])
        self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    @patch('ntfy.backends.prowl.requests.post')
    def test_prowl(self, mock_post, mock_yamlload):
        mock_yamlload.return_value = {
            'backends': ['prowl'],
            'prowl': {'api_key': MagicMock()},
        }
        ret = ntfy_main(['send', 'foobar'])
        self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    @patch('ntfy.backends.pushbullet.requests.post')
    def test_pushbullet(self, mock_post, mock_yamlload):
        mock_yamlload.return_value = {
            'backends': ['pushbullet'],
            'pushbullet': {'access_token': MagicMock()},
        }
        ret = ntfy_main(['send', 'foobar'])
        self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    @patch('ntfy.backends.simplepush.requests.post')
    def test_simplepush(self, mock_post, mock_yamlload):
        mock_yamlload.return_value = {
            'backends': ['simplepush'],
            'simplepush': {'key': MagicMock()},
        }
        ret = ntfy_main(['send', 'foobar'])
        self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.backends.default.platform', 'linux')
    @patch('ntfy.config.yaml.load')
    def test_default(self, mock_yamlload):
        with mock_modules('dbus'):
            mock_yamlload.return_value = {'backends': ['default']}
            ret = ntfy_main(['send', 'foobar'])
            self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.backends.default.platform', 'foobar')
    @patch('ntfy.config.yaml.load')
    @log_capture()
    def test_default_unsupported_platform(self, mock_yamlload, log):
        mock_yamlload.return_value = {'backends': ['default']}
        ret = ntfy_main(['send', 'foobar'])
        self.assertEqual(0, ret)
        log.check(
            ('ntfy.backends.default', 'ERROR', 'Unsupported platform foobar')
        )

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    def test_linux(self, mock_yamlload):
        with mock_modules('dbus'):
            mock_yamlload.return_value = {'backends': ['linux']}
            ret = ntfy_main(['send', 'foobar'])
            self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    def test_darwin(self, mock_yamlload):
        with mock_modules('Foundation', 'objc', 'AppKit'):
            mock_yamlload.return_value = {'backends': ['darwin']}
            ret = ntfy_main(['send', 'foobar'])
            self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    def test_win32(self, mock_yamlload):
        with mock_modules('win32api', 'win32gui', 'win32con'):
            mock_yamlload.return_value = {'backends': ['win32'], }
            ret = ntfy_main(['send', 'foobar'])
            self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    @patch('ntfy.backends.xmpp.NtfySendMsgBot')
    def test_xmpp(self, mock_bot, mock_yamlload):
        mock_yamlload.return_value = {
            'backends': ['xmpp'],
            'xmpp': {
                'jid': 'foo@bar',
                'password': 'hunter2',
                'recipient': 'bar@foo'
            }
        }
        ret = ntfy_main(['send', 'foobar'])
        self.assertEqual(0, ret)

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    def test_instapush(self, mock_yamlload):
        def nt(event_name=None,trackers=None):
            return { 'status': 200 }

        modules['instapush'] = MagicMock()
        modules['instapush'].App.notify = nt

        mock_yamlload.return_value = {
            'backends': ['insta'],
            'insta': {
                'appid': 'appid',
                'secret': 'secret',
                'event_name': 'event',
                'trackers': ['a']
            }
        }
        ntfy_main(['send', 'ms'])

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    @patch('ntfy.backends.pushover.requests.post')
    def test_title_config(self, mock_post, mock_yamlload):
        mock_yamlload.return_value = {
            'title': 'title1',
            'backends': ['pushover'],
            'pushover': {'user_key': MagicMock()},
        }
        ret = ntfy_main(['send', 'message'])
        self.assertEqual(0, ret)
        mock_post.assert_called_once_with(
            ANY,
            data={
                'user': ANY,
                'message': 'message',
                'token': ANY,
                'title': 'title1',
            },
            headers=ANY,
        )

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    @patch('ntfy.backends.pushover.requests.post')
    def test_title_config_override_from_backend(self,
                                                mock_post,
                                                mock_yamlload):
        mock_yamlload.return_value = {
            'title': 'title1',
            'backends': ['pushover'],
            'pushover': {'title': 'title2',
                         'user_key': MagicMock()},
        }
        ret = ntfy_main(['send', 'message'])
        self.assertEqual(0, ret)
        mock_post.assert_called_once_with(
            ANY,
            data={
                'user': ANY,
                'message': 'message',
                'token': ANY,
                'title': 'title2',
            },
            headers=ANY,
        )

    @patch(builtin_module + '.open', mock_open())
    @patch('ntfy.config.yaml.load')
    @patch('ntfy.backends.pushover.requests.post')
    def test_title_config_override_from_command_line(self,
                                                     mock_post,
                                                     mock_yamlload):
        mock_yamlload.return_value = {
            'title': 'title1',
            'backends': ['pushover'],
            'pushover': {'title': 'title2',
                         'user_key': MagicMock()},
        }
        ret = ntfy_main(['-t', 'title3', 'send', 'message'])
        self.assertEqual(0, ret)
        mock_post.assert_called_once_with(
            ANY,
            data={
                'user': ANY,
                'message': 'message',
                'token': ANY,
                'title': 'title3',
            },
            headers=ANY,
        )

    @patch('ntfy.cli.load_config', return_value={})
    @patch('ntfy.backends.default.notify')
    @patch('argparse.ArgumentParser.parse_args')
    def test_message_none_skipped(self, mock_args, mock_notify, mock_loader):
        mock_args.return_value.log_level = 'WARNING'
        mock_args.return_value.func.return_value = (None, 0)
        ret = ntfy_main()
        self.assertEqual(0, ret)
        mock_args.return_value.func.assert_called_once()
        mock_notify.assert_not_called()


if __name__ == '__main__':
    main()
