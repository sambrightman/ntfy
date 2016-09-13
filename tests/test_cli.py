from time import time
from re import escape
from psutil import NoSuchProcess
from unittest import TestCase, main
from mock import patch, MagicMock, Mock
from testfixtures import OutputCapture, StringComparison, compare

from ntfy.cli import run_cmd, auto_done
from ntfy.cli import main as ntfy_main


def process_mock(returncode=0, stdout=None, stderr=None):
    process_mock = Mock()
    attrs = {'communicate.return_value': (stdout, stderr),
             'returncode': returncode}
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
        ret = run_cmd(args)
        self.assertEqual(('"true" succeeded in 0:00 minutes', 0), ret)

    @patch('ntfy.cli.Popen')
    def test_emoji(self, mock_Popen):
        mock_Popen.return_value = process_mock()
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.no_emoji = False
        args.unfocused_only = False
        ret = run_cmd(args)
        expected = (':white_check_mark: "true" succeeded in 0:00 minutes', 0)
        self.assertEqual(expected, ret)

    def tests_usage(self):
        args = MagicMock()
        args.pid = False
        args.formatter = False
        args.command = []
        self.assertRaises(SystemExit, run_cmd, args)

    @patch('ntfy.cli.Popen')
    def test_longer_than(self, mock_Popen):
        mock_Popen.return_value = process_mock()
        args = MagicMock()
        args.longer_than = 1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = False
        ret = run_cmd(args)
        self.assertEqual((None, None), ret)

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
        ret = run_cmd(args)
        self.assertEqual((None, None), ret)

    @patch('ntfy.cli.Popen')
    def test_failure(self, mock_Popen):
        mock_Popen.return_value = process_mock(42)
        args = MagicMock()
        args.longer_than = -1
        args.command = ['false']
        args.pid = None
        args.unfocused_only = False
        ret = run_cmd(args)
        self.assertEqual(('"false" failed (code 42) in 0:00 minutes', 42), ret)

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
        ret = run_cmd(args)
        self.assertEqual(('"true" succeeded in 0:00 minutes:\noutput', 0), ret)

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
        ret = run_cmd(args)
        self.assertEqual(('"true" succeeded in 0:00 minutes:\nerror', 0), ret)

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
        ret = run_cmd(args)
        self.assertEqual(('"true" succeeded in 0:00 minutes:\noutputerror', 0),
                         ret)

    @patch('ntfy.cli.Popen')
    def test_failure_stdout_and_stderr(self, mock_Popen):
        mock_Popen.return_value = process_mock(1,
                                               stdout='output',
                                               stderr='error')
        args = MagicMock()
        args.longer_than = -1
        args.command = ['true']
        args.pid = None
        args.unfocused_only = False
        # not actually used
        args.stdout = True
        args.stderr = True
        expected = ('"true" failed (code 1) in 0:00 minutes:\noutputerror', 1)
        ret = run_cmd(args)
        self.assertEqual(expected, ret)

    def test_formatter(self):
        args = MagicMock()
        args.pid = None
        args.command = None
        args.formatter = ("true", 0, 65)
        args.longer_than = -1
        args.unfocused_only = False
        ret = run_cmd(args)
        self.assertEqual(('"true" succeeded in 1:05 minutes', 0), ret)

    def test_formatter_failure(self):
        args = MagicMock()
        args.pid = None
        args.command = None
        args.formatter = ("false", 1, 10)
        args.longer_than = -1
        args.unfocused_only = False
        ret = run_cmd(args)
        self.assertEqual(('"false" failed (code 1) in 0:10 minutes', 1), ret)


class TestMain(TestCase):
    @patch('ntfy.backends.default.notify')
    def test_args(self, mock_notify):
        ret = ntfy_main(['-b', 'default',
                         '-o', 'foo', 'bar',
                         '-t', 'TITLE',
                         'send', 'test'])
        self.assertEqual(0, ret)
        mock_notify.assert_called_once_with(message='test',
                                            title='TITLE',
                                            foo='bar',
                                            retcode=0)

    @patch('ntfy.cli.load_config', return_value={'longer_than': 5})
    @patch('ntfy.backends.default.notify')
    def test_longer_than_config(self, mock_notify, mock_config):
        ret = ntfy_main(['-b', 'default',
                         '-t', 'TITLE',
                         'done', 'true'])
        self.assertEqual(0, ret)
        mock_notify.assert_not_called()

    @patch('argparse.ArgumentParser.print_usage')
    def test_func_required_usage(self, mock_usage):
        self.assertRaises(SystemExit, ntfy_main, [])
        mock_usage.assert_called_once()


class ShellIntegrationTestCase(TestCase):
    def test_printout(self):
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

    def test_printout_bash(self):
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

    def test_printout_focused(self):
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

    def test_printout_longer_than(self):
        args = MagicMock()
        args.longer_than = 0
        args.unfocused_only = False
        with OutputCapture() as output:
            auto_done(args)
        compare(StringComparison('\n'.join([
            "source '.*/auto-ntfy-done.sh'",
            escape("# To use ntfy's shell integration, run this and add it to your shell's rc file:"),  # noqa: E501
            escape('# eval "$(ntfy shell-integration)"'),
        ]).strip()), output.captured.strip())


class TestWatchPID(TestCase):
    @patch('psutil.Process')
    def test_watch_pid(self, mock_process):
        mock_process.return_value.pid = 1
        mock_process.return_value.create_time.return_value = time()
        mock_process.return_value.cmdline.return_value = ['foo', 'bar']
        mock_process.return_value.wait.return_value = 5
        args = MagicMock()
        args.pid = 1
        args.unfocused_only = False
        ret = run_cmd(args)
        self.assertEqual(('PID[1]: "foo bar" finished in 0:00 minutes', 5),
                         ret)

    @patch('psutil.Process')
    def test_watch_pid_race(self, mock_process):
        mock_process.return_value.pid = 1
        mock_process.return_value.create_time.return_value = time()
        mock_process.return_value.cmdline.return_value = ['foo', 'bar']
        mock_process.return_value.wait.side_effect = NoSuchProcess(1)
        args = MagicMock()
        args.pid = 1
        args.unfocused_only = False
        ret = run_cmd(args)
        self.assertEqual(('PID[1]: "foo bar" finished in 0:00 minutes', None),
                         ret)

    @patch('psutil.Process', side_effect=NoSuchProcess(100000))
    def test_watch_bad_pid(self, mock_process):
        args = MagicMock()
        args.pid = 100000
        args.unfocused_only = False
        self.assertRaises(SystemExit, run_cmd, args)


if __name__ == '__main__':
    main()
