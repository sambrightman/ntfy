import logging
from unittest import TestCase
from mock import patch, MagicMock
from testfixtures import log_capture

from ntfy.backends.xmpp import notify, NtfySendMsgBot


class NtfySendMsgBotTestCase(TestCase):
    @patch('sleekxmpp.ClientXMPP.add_event_handler')
    def test_eventhandler(self, mock_add_event_handler):
        bot = NtfySendMsgBot('foo@bar', 'hunter2', 'bar@foo', 'title',
                             'message')
        mock_add_event_handler.assert_called_with('session_start',
                                                  bot.start)

    @patch('sleekxmpp.ClientXMPP.send_presence')
    @patch('sleekxmpp.ClientXMPP.get_roster')
    @patch('sleekxmpp.ClientXMPP.disconnect')
    @patch('sleekxmpp.ClientXMPP.send_message')
    def test_start(self, mock_send_message, *other_mocks):
        bot = NtfySendMsgBot('foo@bar', 'hunter2', 'bar@foo', 'title',
                             'message')
        bot.start(MagicMock)
        mock_send_message.assert_called_with(mbody='message', msubject='title',
                                             mto='bar@foo')

    @patch('sleekxmpp.ClientXMPP.send_presence')
    @patch('sleekxmpp.ClientXMPP.get_roster')
    @patch('sleekxmpp.ClientXMPP.disconnect')
    @patch('sleekxmpp.ClientXMPP.send_message')
    def test_start_mtype(self, mock_send_message, *other_mocks):
        bot = NtfySendMsgBot('foo@bar', 'hunter2', 'bar@foo', 'title',
                             'message', mtype='chat')
        bot.start(MagicMock)
        mock_send_message.assert_called_with(mbody='message', msubject='title',
                                             mto='bar@foo', mtype='chat')

    @patch('sleekxmpp.ClientXMPP.process')
    @patch('sleekxmpp.ClientXMPP.connect', return_value=False)
    @log_capture(level=logging.WARN)
    def test_failure(self, mock_connect, mock_process, log):
        notify('title', 'message', 'foo@bar', 'hunter2', 'bar@foo')
        mock_connect.assert_called_once()
        mock_process.assert_not_called()
        log.check(('ntfy.backends.xmpp', 'ERROR', 'Unable to connect'))
        self.assertIsNotNone(log.records[-1].exc_info)


class XMPPTestCase(TestCase):
    @patch('os.path.isdir')
    @patch('ntfy.backends.xmpp.NtfySendMsgBot')
    def test_capath(self, mock_bot_class, mock_isdir):
        notify('title', 'message', 'foo@bar', 'hunter2', 'bar@foo',
               path_to_certs='/custom/ca')
        self.assertEqual('/custom/ca', mock_bot_class().ca_certs)
