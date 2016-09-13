from unittest import TestCase
from mock import patch
from testfixtures import log_capture

from ntfy.backends.insta import (notify,
                                 WrongMessageCountException,
                                 ApiException)


class TestInsta(TestCase):
    @patch('instapush.App.notify', return_value={'status': 200})
    def test_one_message(self, mock_notify):
        notify('title', 'message', 'event', 'appid', 'secret', 'a')
        mock_notify.assert_called_once_with(
            event_name='event',
            trackers={
                'a': 'message',
            },
        )

    @patch('instapush.App.notify', return_value={'status': 200})
    def test_two_messages(self, mock_notify):
        notify('title', 'message1:message2', 'event', 'appid', 'secret', 'ab')
        mock_notify.assert_called_once_with(
            event_name='event',
            trackers={
                'a': 'message1',
                'b': 'message2',
            },
        )

    @patch('instapush.App.notify', return_value={'status': 200})
    def test_escape_colon(self, mock_notify):
        notify('title', 'message\: detail', 'event', 'appid', 'secret', 'a')
        mock_notify.assert_called_once_with(
            event_name='event',
            trackers={
                'a': 'message: detail',
            },
        )

    @patch('instapush.App.notify', return_value={'status': 200})
    @log_capture()
    def test_wrong_message_count(self, mock_notify, log):
        self.assertRaises(
            WrongMessageCountException,
            notify,
            'title',
            'message1:message2',
            'event',
            'appid',
            'secret',
            'a'
        )
        mock_notify.assert_not_called()
        self.assertIsInstance(log.records, list)
        self.assertNotEqual([], log.records)

    @patch('instapush.App.notify', return_value={'status': 200})
    @log_capture()
    def test_wrong_tracker_count(self, mock_notify, log):
        self.assertRaises(
            WrongMessageCountException,
            notify,
            'title',
            'message',
            'event',
            'appid',
            'secret',
            'ab'
        )
        mock_notify.assert_not_called()
        self.assertIsInstance(log.records, list)
        self.assertNotEqual([], log.records)

    @patch('instapush.App.notify',
           return_value={'status': 401, 'msg': 'error'})
    @log_capture()
    def test_api_error(self, mock_notify, log):
        self.assertRaises(
            ApiException,
            notify,
            'title',
            'message',
            'event',
            'appid',
            'secret',
            'a'
        )
        mock_notify.assert_called_once_with(
            event_name='event',
            trackers={
                'a': 'message',
            },
        )
        log.check(
            ('ntfy.backends.insta', 'ERROR', '401: error')
        )
