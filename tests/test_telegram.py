from unittest import TestCase
from mock import patch, ANY

from ntfy.backends.telegram import notify, CONFIG_DIR, CONFIG_FILE


def fake_path_exists(path):
    return {
        CONFIG_FILE: False,
        CONFIG_DIR: True,
    }.get(path)


class TestTelegram(TestCase):
    @patch('ntfy.backends.telegram.path.exists', return_value=True)
    @patch('ntfy.backends.telegram.send')
    def test_config_exists(self, mock_send, mock_path_exists):
        notify('title', 'message')
        mock_send.assert_called_once_with(
            conf=ANY,
            messages=['message'],
        )

    @patch('ntfy.backends.telegram.path.exists', return_value=False)
    @patch('ntfy.backends.telegram.makedirs')
    @patch('ntfy.backends.telegram.configure')
    @patch('ntfy.backends.telegram.send')
    def test_nothing_exists(self,
                            mock_send,
                            mock_configure,
                            mock_makedirs,
                            mock_path_exists):
        notify('title', 'message')
        mock_makedirs.assert_called_once()
        mock_configure.assert_called_once()
        mock_send.assert_called_once_with(
            conf=ANY,
            messages=['message'],
        )

    @patch('ntfy.backends.telegram.path.exists', side_effect=fake_path_exists)
    @patch('ntfy.backends.telegram.makedirs')
    @patch('ntfy.backends.telegram.configure')
    @patch('ntfy.backends.telegram.send')
    def test_directory_exists(self,
                              mock_send,
                              mock_configure,
                              mock_makedirs,
                              mock_path_exists):
        notify('title', 'message')
        mock_makedirs.assert_not_called()
        mock_configure.assert_called_once()
        mock_send.assert_called_once_with(
            conf=ANY,
            messages=['message'],
        )
