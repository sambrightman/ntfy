from time import time
from re import escape
from unittest import TestCase, main
from mock import patch, MagicMock, Mock
from mock import patch, MagicMock
from testfixtures import OutputCapture, StringComparison, compare

from ntfy.cli import run_cmd, auto_done
from ntfy.cli import main as ntfy_main


def process_mock(returncode=0, stdout=None, stderr=None):
    process_mock = Mock()
    attrs = {'communicate.return_value': (stdout, stderr), 'returncode': returncode}
    process_mock.configure_mock(**attrs)
    return process_mock


class TestRunCmd(TestCase):
    @patch('ntfy.cli.Popen')
    def test_default(self, mock_Popen):
        mock_Popen.return_value = process_mock()
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = False
        self.assertEqual(('"true" succeeded in 0:00 minutes', 0), run_cmd(args))

    @patch('ntfy.cli.Popen')
    def test_emoji(self, mock_Popen):
        mock_Popen.return_value = process_mock()
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.no_emoji = False
        args.unfocused_only = False
        self.assertEqual((':white_check_mark: "true" succeeded in 0:00 minutes', 0),
                         run_cmd(args))

    def tests_usage(self):
        args = MagicMock()
        args.pid = False
        args.formatter = False
        args.command = []
        self.assertRaises(SystemExit, run_cmd, args)

    @patch('ntfy.cli.Popen')
    def test_longerthan(self, mock_Popen):
        mock_Popen.return_value = process_mock()
        args = MagicMock()
        args.longer_than = 1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = False
        self.assertEqual((None, None), run_cmd(args))

    @patch('ntfy.cli.is_focused')
    @patch('ntfy.cli.Popen')
    def test_focused(self, mock_Popen, mock_is_focused):
        mock_Popen.return_value = process_mock()
        mock_is_focused.return_value = True
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = True
        self.assertEqual((None, None), run_cmd(args))

    @patch('ntfy.cli.Popen')
    def test_failure(self, mock_Popen):
        mock_Popen.return_value = process_mock(42)
        args = MagicMock()
        args.longer_than = -1
        args.command = ['false']
        args.pid = None
        args.unfocused_only = False
        self.assertEqual(('"false" failed (code 42) in 0:00 minutes', 42), run_cmd(args))

    @patch('ntfy.cli.Popen')
    def test_stdout(self, mock_Popen):
        mock_Popen.return_value = process_mock(stdout='output')
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = False
        # not actually used
        args.stdout = True
        args.stderr = False
        self.assertEqual(('"true" succeeded in 0:00 minutes:\noutput', 0), run_cmd(args))

    @patch('ntfy.cli.Popen')
    def test_stderr(self, mock_Popen):
        mock_Popen.return_value = process_mock(stderr='error')
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = False
        # not actually used
        args.stdout = False
        args.stderr = True
        self.assertEqual(('"true" succeeded in 0:00 minutes:\nerror', 0), run_cmd(args))

    @patch('ntfy.cli.Popen')
    def test_stdout_and_stderr(self, mock_Popen):
        mock_Popen.return_value = process_mock(stdout='output', stderr='error')
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = False
        # not actually used
        args.stdout = True
        args.stderr = True
        self.assertEqual(('"true" succeeded in 0:00 minutes:\noutputerror', 0), run_cmd(args))

    @patch('ntfy.cli.Popen')
    def test_failure_stdout_and_stderr(self, mock_Popen):
        mock_Popen.return_value = process_mock(1, stdout='output', stderr='error')
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = False
        # not actually used
        args.stdout = True
        args.stderr = True
        self.assertEqual(('"true" failed (code 1) in 0:00 minutes:\noutputerror', 1), run_cmd(args))

    def test_formatter(self):
        args = MagicMock()
        args.pid = None
        args.command = None
        args.formatter = ("true", 0, 65)
        args.longer_than = -1
        args.unfocused_only = False
        self.assertEqual(('"true" succeeded in 1:05 minutes', 0), run_cmd(args))

    def test_formatter_failure(self):
        args = MagicMock()
        args.pid = None
        args.command = None
        args.formatter = ("false", 1, 10)
        args.longer_than = -1
        args.unfocused_only = False
        self.assertEqual(('"false" failed (code 1) in 0:10 minutes', 1), run_cmd(args))


class TestMain(TestCase):
    @patch('ntfy.backends.default.notify')
    def test_args(self, mock_notify):
        self.assertEquals(0, ntfy_main(['-o', 'foo', 'bar',
                                        '-b', 'default',
                                        '-t', 'TITLE',
                                        'send', 'test']))
        mock_notify.assert_called_once_with(message='test',
                                            title='TITLE',
                                            foo='bar',
                                            retcode=0)


class ShellIntegrationTestCase(TestCase):
    def test_shellintegration_printout(self):
        args = MagicMock()
        args.longer_than = 1
        with OutputCapture() as output:
            auto_done(args)
        compare(StringComparison('\n'.join([
            escape("export AUTO_NTFY_DONE_LONGER_THAN=-L1"),
            escape("export AUTO_NTFY_DONE_UNFOCUSED_ONLY=-b"),
            "source '.*/auto-ntfy-done.sh'",
            escape("# To use ntfy's shell integration, run this and add it to your shell's rc file:"),  # noqa: E501
            escape('# eval "$(ntfy shell-integration)"'),
        ]).strip()), output.captured.strip())

    def test_shellintegration_printout_bash(self):
        args = MagicMock()
        args.longer_than = 1
        args.shell = "bash"
        with OutputCapture() as output:
            auto_done(args)
        compare(StringComparison('\n'.join([
            escape("export AUTO_NTFY_DONE_LONGER_THAN=-L1"),
            escape("export AUTO_NTFY_DONE_UNFOCUSED_ONLY=-b"),
            "source '.*/bash-preexec.sh'",
            "source '.*/auto-ntfy-done.sh'",
            escape("# To use ntfy's shell integration, run this and add it to your shell's rc file:"),  # noqa: E501
            escape('# eval "$(ntfy shell-integration)"'),
        ]).strip()), output.captured.strip())

    def test_shellintegration_printout_focused(self):
        args = MagicMock()
        args.longer_than = 1
        args.unfocused_only = False
        with OutputCapture() as output:
            auto_done(args)
        compare(StringComparison('\n'.join([
            escape("export AUTO_NTFY_DONE_LONGER_THAN=-L1"),
            "source '.*/auto-ntfy-done.sh'",
            escape("# To use ntfy's shell integration, run this and add it to your shell's rc file:"),  # noqa: E501
            escape('# eval "$(ntfy shell-integration)"'),
        ]).strip()), output.captured.strip())


class TestWatchPID(TestCase):
    @patch('psutil.Process')
    def test_watch_pid(self, mock_process):
        mock_process.return_value.pid = 1
        mock_process.return_value.create_time.return_value = time()
        mock_process.return_value.cmdline.return_value = ['cmd']
        args = MagicMock()
        args.pid = 1
        args.unfocused_only = False
        self.assertEqual('PID[1]: "cmd" finished in 0:00 minutes',
                         run_cmd(args)[0])

    def test_watch_bad_pid(self):
        args = MagicMock()
        args.pid = 100000
        self.assertRaises(SystemExit, run_cmd, args)


if __name__ == '__main__':
    main()
