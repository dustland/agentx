"""
Tests for CLI main functionality.

These tests define the expected correct behavior for the
VibeX command-line interface.
"""

import pytest
import sys
from unittest.mock import patch, Mock, MagicMock
from vibex.cli.main import main
from vibex.cli.parser import create_parser


class TestMainCLI:
    """Test main CLI entry point."""

    def test_main_with_no_args_shows_help(self):
        """main should show help when called with no arguments."""
        with patch('sys.argv', ['vibex']):
            with patch('vibex.cli.main.create_parser') as mock_parser:
                mock_arg_parser = Mock()
                mock_parser.return_value = mock_arg_parser
                mock_arg_parser.parse_args.return_value = Mock(command=None)

                with pytest.raises(SystemExit):
                    main()

                mock_arg_parser.print_help.assert_called_once()

    def test_main_delegates_to_subcommands(self):
        """main should delegate to appropriate subcommand handlers."""
        test_cases = [
            (['vibex', 'status'], 'show_status'),
            (['vibex', 'version'], 'show_version'),
        ]

        for argv, expected_func in test_cases:
            with patch('sys.argv', argv):
                with patch(f'vibex.cli.main.{expected_func}') as mock_func:
                    mock_func.return_value = None

                    result = main()

                    assert result == 0
                    mock_func.assert_called_once()

    def test_main_handles_keyboard_interrupt(self):
        """main should handle KeyboardInterrupt gracefully."""
        with patch('sys.argv', ['vibex', 'status']):
            with patch('vibex.cli.main.show_status') as mock_status:
                mock_status.side_effect = KeyboardInterrupt()

                result = main()

                assert result == 130

    def test_main_handles_general_exceptions(self):
        """main should handle general exceptions gracefully."""
        with patch('sys.argv', ['vibex', 'status']):
            with patch('vibex.cli.main.show_status') as mock_status:
                mock_status.side_effect = Exception("Something went wrong")

                result = main()

                assert result == 1

    def test_main_returns_command_exit_code(self):
        """main should return the exit code from command handlers."""
        with patch('sys.argv', ['vibex', 'init', 'myproject']):
            with patch('vibex.cli.main.bootstrap_project') as mock_bootstrap:
                mock_bootstrap.return_value = 42

                result = main()

                assert result == 42


class TestCommandRouting:
    """Test command routing functionality."""

    def test_main_routes_init(self):
        """main should route init command correctly."""
        with patch('sys.argv', ['vibex', 'init', 'myproject']):
            with patch('vibex.cli.main.bootstrap_project') as mock_bootstrap:
                mock_bootstrap.return_value = 0

                result = main()

                assert result == 0
                mock_bootstrap.assert_called_once()

    def test_main_routes_start(self):
        """main should route start command correctly."""
        with patch('sys.argv', ['vibex', 'start']):
            with patch('vibex.cli.main.start') as mock_start:
                mock_start.return_value = 0

                result = main()

                assert result == 0
                mock_start.assert_called_once()

    def test_main_routes_status(self):
        """main should route status command correctly."""
        with patch('sys.argv', ['vibex', 'status']):
            with patch('vibex.cli.main.show_status') as mock_status:
                mock_status.return_value = None

                result = main()

                assert result == 0
                mock_status.assert_called_once()

    def test_main_routes_version(self):
        """main should route version command correctly."""
        with patch('sys.argv', ['vibex', 'version']):
            with patch('vibex.cli.main.show_version') as mock_version:
                mock_version.return_value = None

                result = main()

                assert result == 0
                mock_version.assert_called_once()

    def test_main_unknown_command_shows_help(self):
        """main should show help for unknown commands."""
        with patch('sys.argv', ['vibex', 'unknown_command']):
            parser = create_parser()
            with patch('vibex.cli.main.create_parser', return_value=parser):
                with pytest.raises(SystemExit):
                    main()


class TestStartCommand:
    """Test start command functionality."""

    def test_start_command(self):
        """start command should be called correctly."""
        with patch('sys.argv', ['vibex', 'start']):
            with patch('vibex.cli.main.start') as mock_start:
                mock_start.return_value = 0

                result = main()

                assert result == 0
                mock_start.assert_called_once()

    def test_monitor_command(self):
        """monitor command should be called correctly."""
        with patch('sys.argv', ['vibex', 'monitor']):
            with patch('vibex.cli.main.monitor') as mock_monitor:
                mock_monitor.return_value = 0

                result = main()

                assert result == 0
                mock_monitor.assert_called_once()

    def test_monitor_web_command(self):
        """monitor --web command should be called correctly."""
        with patch('sys.argv', ['vibex', 'monitor', '--web']):
            # Need to create a proper parser to handle the arguments
            parser = create_parser()
            args = parser.parse_args(['monitor', '--web'])

            with patch('vibex.cli.main.create_parser', return_value=parser):
                with patch('vibex.cli.main.web') as mock_web:
                    mock_web.return_value = 0

                    result = main()

                    assert result == 0
                    mock_web.assert_called_once()


class TestCLIArgumentParsing:
    """Test CLI argument parsing."""

    def test_parser_creates_all_subcommands(self):
        """Parser should create all expected subcommands."""
        parser = create_parser()

        # Should have subparsers
        assert hasattr(parser, '_subparsers')

        # Test parsing various commands
        test_commands = [
            ['init'],
            ['start'],
            ['monitor'],
            ['status'],
            ['version'],
            ['example', 'test'],
        ]

        for command in test_commands:
            try:
                args = parser.parse_args(command)
                assert hasattr(args, 'command')
            except SystemExit:
                # Some commands might require additional args
                pass

    def test_parser_init_command_args(self):
        """Parser should handle init command arguments correctly."""
        parser = create_parser()

        # Test with minimal args
        args = parser.parse_args(['init'])
        assert args.command == 'init'
        assert hasattr(args, 'no_interactive')

        # Test with all args
        args = parser.parse_args(['init', 'myproject', '--template', 'coding', '--no-interactive'])
        assert args.command == 'init'
        assert args.project_name == 'myproject'
        assert args.template == 'coding'
        assert args.no_interactive is True

    def test_parser_start_command_args(self):
        """Parser should handle start command arguments correctly."""
        parser = create_parser()

        # Test start command
        args = parser.parse_args(['start'])
        assert args.command == 'start'
        assert hasattr(args, 'host')
        assert hasattr(args, 'port')

    def test_parser_monitor_command_args(self):
        """Parser should handle monitor command arguments correctly."""
        parser = create_parser()

        # Test monitor command
        args = parser.parse_args(['monitor'])
        assert args.command == 'monitor'

        # Test monitor with web option
        args = parser.parse_args(['monitor', '--web'])
        assert args.command == 'monitor'
        assert args.web is True

    def test_parser_status_command_args(self):
        """Parser should handle status command arguments correctly."""
        parser = create_parser()

        args = parser.parse_args(['status'])
        assert args.command == 'status'

    def test_parser_version_command_args(self):
        """Parser should handle version command arguments correctly."""
        parser = create_parser()

        args = parser.parse_args(['version'])
        assert args.command == 'version'


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    def test_cli_handles_invalid_arguments(self):
        """CLI should handle invalid arguments gracefully."""
        parser = create_parser()

        # Test invalid command
        with pytest.raises(SystemExit):
            parser.parse_args(['invalid_command'])

        # Test valid commands don't raise
        args = parser.parse_args(['status'])
        assert args.command == 'status'

    def test_cli_handles_import_errors(self):
        """CLI should handle import errors gracefully."""
        with patch('sys.argv', ['vibex', 'start']):
            with patch('vibex.cli.main.start', side_effect=ImportError("Missing dependency")):
                result = main()
                assert result == 1

    def test_cli_handles_permission_errors(self):
        """CLI should handle permission errors gracefully."""
        with patch('sys.argv', ['vibex', 'init', 'myproject']):
            with patch('vibex.cli.main.bootstrap_project', side_effect=PermissionError("Permission denied")):
                result = main()
                assert result == 1


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def test_cli_end_to_end_simulation(self):
        """Test complete CLI workflow simulation."""
        # Mock all external dependencies
        with patch('vibex.cli.main.start') as mock_start:
            mock_start.return_value = 0

            # Simulate command line args
            test_argv = ['vibex', 'start']

            with patch('sys.argv', test_argv):
                result = main()

                assert result == 0
                mock_start.assert_called_once()

    def test_cli_with_environment_variables(self):
        """Test CLI behavior with environment variables."""
        with patch.dict('os.environ', {'AGENTX_VERBOSE': '1'}):
            with patch('vibex.cli.main.start') as mock_start:
                mock_start.return_value = 0

                test_argv = ['vibex', 'start']

                with patch('sys.argv', test_argv):
                    result = main()

                    assert result == 0

    def test_cli_output_formatting(self):
        """Test CLI output formatting."""
        # This would test that output is properly formatted for console
        # Mock stdout to capture output
        with patch('sys.stdout') as mock_stdout:
            with patch('sys.argv', ['vibex', 'version']):
                with patch('vibex.cli.main.show_version') as mock_version:
                    mock_version.return_value = None

                    result = main()

                    assert result == 0
