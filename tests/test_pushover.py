from unittest import TestCase, main
from mock import patch
from testfixtures import log_capture

from ntfy.backends.pushover import notify, __name__ as N
from ntfy.config import USER_AGENT


class TestPushover(TestCase):
    @patch('requests.Response')
    @patch('requests.post')
    def test_basic(self, mock_post, mock_response):
        mock_post.return_value = mock_response
        notify('title', 'message', user_key='user_key')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title'},
            headers={'User-Agent': USER_AGENT})
        mock_response.raise_for_status.assert_called_once()

    @patch('requests.post')
    def test_url_title(self, mock_post):
        notify('title',
               'message',
               user_key='user_key',
               url_title='foo',
               url='bar')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'url_title': 'foo',
                  'url': 'bar'},
            headers={'User-Agent': USER_AGENT})

        mock_post.reset_mock()
        notify('title', 'message', user_key='user_key', url_title='foo')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title'},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_html(self, mock_post):
        notify('title', 'message', user_key='user_key', html=True)
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'html': 1},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_priority(self, mock_post):
        notify('title', 'message', user_key='user_key', priority=1)
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'priority': 1},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_invalid_priority(self, mock_post):
        self.assertRaises(ValueError,
                          notify,
                          'title',
                          'message',
                          user_key='user_key',
                          priority=3)

    @patch('requests.post')
    def test_hi_priority(self, mock_post):
        notify('title', 'message', user_key='user_key', priority=2)
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'priority': 2,
                  'retry': 30,
                  'expire': 86400},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_hi_priority_retry(self, mock_post):
        notify('title', 'message', user_key='user_key', priority=2, retry=60)
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'priority': 2,
                  'retry': 60,
                  'expire': 86400},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_hi_priority_expire(self, mock_post):
        notify('title', 'message', user_key='user_key', priority=2, expire=60)
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'priority': 2,
                  'retry': 30,
                  'expire': 60},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_hi_priority_callback(self, mock_post):
        notify('title',
               'message',
               user_key='user_key',
               priority=2,
               callback='http://example.com')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'priority': 2,
                  'retry': 30,
                  'expire': 86400,
                  'callback': 'http://example.com'},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_device(self, mock_post):
        notify('title', 'message', user_key='user_key', device='foobar')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'device': 'foobar'},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_sound(self, mock_post):
        notify('title', 'message', user_key='user_key', sound='foobar')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'sound': 'foobar'},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    def test_url(self, mock_post):
        notify('title', 'message', user_key='user_key', url='foobar')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title',
                  'url': 'foobar'},
            headers={'User-Agent': USER_AGENT})

    @patch('requests.post')
    @log_capture()
    def test_non_emergency_warning_retry(self, mock_post, log):
        notify('title', 'message', user_key='user_key', retry=60)
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title'},
            headers={'User-Agent': USER_AGENT})
        log.check(
            (N, 'WARNING', 'Non-emergency, ignoring retry set in config')
        )

    @patch('requests.post')
    @log_capture()
    def test_non_emergency_warning_expire(self, mock_post, log):
        notify('title', 'message', user_key='user_key', expire=60)
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title'},
            headers={'User-Agent': USER_AGENT})
        log.check(
            (N, 'WARNING', 'Non-emergency, ignoring expire set in config')
        )

    @patch('requests.post')
    @log_capture()
    def test_non_emergency_warning_callback(self, mock_post, log):
        notify('title',
               'message',
               user_key='user_key',
               callback='http://example.com')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title'},
            headers={'User-Agent': USER_AGENT})
        log.check(
            (N, 'WARNING', 'Non-emergency, ignoring callback set in config')
        )

    @patch('requests.post')
    @log_capture()
    def test_non_emergency_warnings(self, mock_post, log):
        notify('title',
               'message',
               user_key='user_key',
               retry=60,
               expire=60,
               callback='http://example.com')
        mock_post.assert_called_once_with(
            'https://api.pushover.net/1/messages.json',
            data={'user': 'user_key',
                  'message': 'message',
                  'token': 'aUnsraBiEZVsmrG89AZp47K3S2dX2a',
                  'title': 'title'},
            headers={'User-Agent': USER_AGENT})
        log.check(
            (N, 'WARNING', 'Non-emergency, ignoring retry set in config'),
            (N, 'WARNING', 'Non-emergency, ignoring expire set in config'),
            (N, 'WARNING', 'Non-emergency, ignoring callback set in config'),
        )


if __name__ == '__main__':
    main()
