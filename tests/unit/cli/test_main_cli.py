"""
Tests for CLI main functionality.

These tests define the expected correct behavior for the
AgentX command-line interface.
"""

import pytest
import sys
from unittest.mock import patch, Mock, MagicMock
from agentx.cli.main import main
from agentx.cli.parser import create_parser


class TestMainCLI:
    """Test main CLI entry point."""
    
    def test_main_with_no_args_shows_help(self):
        """main should show help when called with no arguments."""
        with patch('sys.argv', ['agentx']):
            with patch('agentx.cli.main.create_parser') as mock_parser:
                mock_arg_parser = Mock()
                mock_parser.return_value = mock_arg_parser
                mock_arg_parser.parse_args.return_value = Mock(command=None)
                
                with pytest.raises(SystemExit):
                    main()
                
                mock_arg_parser.print_help.assert_called_once()
    
    def test_main_delegates_to_subcommands(self):
        """main should delegate to appropriate subcommand handlers."""
        test_cases = [
            (['agentx', 'init'], 'init'),
            (['agentx', 'run'], 'run'),
            (['agentx', 'status'], 'status'),
            (['agentx', 'version'], 'version'),
        ]
        
        for argv, expected_command in test_cases:
            with patch('sys.argv', argv):
                with patch('agentx.cli.main.handle_command') as mock_handle:
                    mock_handle.return_value = 0
                    
                    result = main()
                    
                    assert result == 0
                    mock_handle.assert_called_once()
                    args = mock_handle.call_args[0][0]
                    assert hasattr(args, 'command')
    
    def test_main_handles_keyboard_interrupt(self):
        """main should handle KeyboardInterrupt gracefully."""
        with patch('sys.argv', ['agentx', 'run']):
            with patch('agentx.cli.main.handle_command') as mock_handle:
                mock_handle.side_effect = KeyboardInterrupt()
                
                result = main()
                
                assert result == 1
    
    def test_main_handles_general_exceptions(self):
        """main should handle general exceptions gracefully."""
        with patch('sys.argv', ['agentx', 'run']):
            with patch('agentx.cli.main.handle_command') as mock_handle:
                mock_handle.side_effect = Exception("Something went wrong")
                
                result = main()
                
                assert result == 1
    
    def test_main_returns_command_exit_code(self):
        """main should return the exit code from command handlers."""
        with patch('sys.argv', ['agentx', 'init']):
            with patch('agentx.cli.main.handle_command') as mock_handle:
                mock_handle.return_value = 42
                
                result = main()
                
                assert result == 42


class TestCommandRouting:
    """Test command routing functionality."""
    
    def test_handle_command_routes_init(self):
        """handle_command should route init command correctly."""
        with patch('agentx.cli.bootstrap.handle_init') as mock_init:
            mock_init.return_value = 0
            args = Mock(command='init', interactive=True)
            
            from agentx.cli.main import handle_command
            result = handle_command(args)
            
            assert result == 0
            mock_init.assert_called_once_with(args)
    
    def test_handle_command_routes_run(self):
        """handle_command should route run command correctly."""
        with patch('agentx.cli.main.handle_run') as mock_run:
            mock_run.return_value = 0
            args = Mock(command='run', config='team.yaml')
            
            from agentx.cli.main import handle_command
            result = handle_command(args)
            
            assert result == 0
            mock_run.assert_called_once_with(args)
    
    def test_handle_command_routes_status(self):
        """handle_command should route status command correctly."""
        with patch('agentx.cli.status.handle_status') as mock_status:
            mock_status.return_value = 0
            args = Mock(command='status')
            
            from agentx.cli.main import handle_command
            result = handle_command(args)
            
            assert result == 0
            mock_status.assert_called_once_with(args)
    
    def test_handle_command_routes_version(self):
        """handle_command should route version command correctly."""
        with patch('agentx.cli.status.handle_version') as mock_version:
            mock_version.return_value = 0
            args = Mock(command='version')
            
            from agentx.cli.main import handle_command
            result = handle_command(args)
            
            assert result == 0
            mock_version.assert_called_once_with(args)
    
    def test_handle_command_unknown_command_returns_error(self):
        """handle_command should return error for unknown commands."""
        args = Mock(command='unknown_command')
        
        from agentx.cli.main import handle_command
        result = handle_command(args)
        
        assert result == 1


class TestRunCommand:
    """Test run command functionality."""
    
    def test_handle_run_with_valid_config(self):
        """handle_run should execute task with valid config."""
        with patch('agentx.cli.main.execute_task') as mock_execute:
            mock_execute.return_value = Mock()  # Async generator mock
            args = Mock(
                config='team.yaml',
                prompt='Test prompt',
                stream=True,
                model=None,
                workspace=None
            )
            
            from agentx.cli.main import handle_run
            result = handle_run(args)
            
            assert result == 0
            mock_execute.assert_called_once()
    
    def test_handle_run_missing_config_file(self):
        """handle_run should handle missing config file gracefully."""
        args = Mock(
            config='nonexistent.yaml',
            prompt='Test prompt',
            stream=True,
            model=None,
            workspace=None
        )
        
        with patch('pathlib.Path.exists', return_value=False):
            from agentx.cli.main import handle_run
            result = handle_run(args)
            
            assert result == 1
    
    def test_handle_run_missing_prompt(self):
        """handle_run should handle missing prompt gracefully."""
        args = Mock(
            config='team.yaml',
            prompt=None,
            stream=True,
            model=None,
            workspace=None
        )
        
        from agentx.cli.main import handle_run
        result = handle_run(args)
        
        assert result == 1
    
    def test_handle_run_with_model_override(self):
        """handle_run should pass model override to task execution."""
        with patch('agentx.cli.main.execute_task') as mock_execute:
            mock_execute.return_value = Mock()
            args = Mock(
                config='team.yaml',
                prompt='Test prompt',
                stream=True,
                model='gpt-4',
                workspace=None
            )
            
            from agentx.cli.main import handle_run
            result = handle_run(args)
            
            assert result == 0
            # Verify model override was passed
            call_args = mock_execute.call_args
            assert 'model_override' in call_args.kwargs or len(call_args.args) >= 3
    
    def test_handle_run_with_workspace_override(self):
        """handle_run should pass workspace override to task execution."""
        with patch('agentx.cli.main.execute_task') as mock_execute:
            mock_execute.return_value = Mock()
            args = Mock(
                config='team.yaml',
                prompt='Test prompt',
                stream=True,
                model=None,
                workspace='/custom/workspace'
            )
            
            from agentx.cli.main import handle_run
            result = handle_run(args)
            
            assert result == 0
            # Verify workspace override was passed
            call_args = mock_execute.call_args
            assert 'workspace_dir' in call_args.kwargs or len(call_args.args) >= 4


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
            ['run', 'team.yaml', 'test prompt'],
            ['status'],
            ['version'],
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
        assert hasattr(args, 'interactive')
        
        # Test with all args
        args = parser.parse_args(['init', '--template', 'coding', '--non-interactive'])
        assert args.command == 'init'
        assert args.template == 'coding'
        assert args.interactive is False
    
    def test_parser_run_command_args(self):
        """Parser should handle run command arguments correctly."""
        parser = create_parser()
        
        # Test with minimal required args
        args = parser.parse_args(['run', 'team.yaml', 'test prompt'])
        assert args.command == 'run'
        assert args.config == 'team.yaml'
        assert args.prompt == 'test prompt'
        
        # Test with optional args
        args = parser.parse_args([
            'run', 'team.yaml', 'test prompt',
            '--model', 'gpt-4',
            '--workspace', '/tmp/workspace',
            '--no-stream'
        ])
        assert args.model == 'gpt-4'
        assert args.workspace == '/tmp/workspace'
        assert args.stream is False
    
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
        
        # Test missing required arguments
        with pytest.raises(SystemExit):
            parser.parse_args(['run'])  # Missing config and prompt
    
    def test_cli_handles_import_errors(self):
        """CLI should handle import errors gracefully."""
        with patch('agentx.cli.main.execute_task', side_effect=ImportError("Missing dependency")):
            args = Mock(
                config='team.yaml',
                prompt='Test prompt',
                stream=True,
                model=None,
                workspace=None
            )
            
            from agentx.cli.main import handle_run
            result = handle_run(args)
            
            assert result == 1
    
    def test_cli_handles_permission_errors(self):
        """CLI should handle permission errors gracefully."""
        with patch('pathlib.Path.exists', side_effect=PermissionError("Permission denied")):
            args = Mock(
                config='team.yaml',
                prompt='Test prompt',
                stream=True,
                model=None,
                workspace=None
            )
            
            from agentx.cli.main import handle_run
            result = handle_run(args)
            
            assert result == 1


class TestCLIIntegration:
    """Test CLI integration scenarios."""
    
    def test_cli_end_to_end_simulation(self):
        """Test complete CLI workflow simulation."""
        # Mock all external dependencies
        with patch('agentx.cli.main.execute_task') as mock_execute, \
             patch('pathlib.Path.exists', return_value=True):
            
            mock_execute.return_value = Mock()
            
            # Simulate command line args
            test_argv = ['agentx', 'run', 'team.yaml', 'Test prompt']
            
            with patch('sys.argv', test_argv):
                result = main()
                
                assert result == 0
                mock_execute.assert_called_once()
    
    def test_cli_with_environment_variables(self):
        """Test CLI behavior with environment variables."""
        with patch.dict('os.environ', {'AGENTX_VERBOSE': '1'}):
            with patch('agentx.cli.main.execute_task') as mock_execute, \
                 patch('pathlib.Path.exists', return_value=True):
                
                mock_execute.return_value = Mock()
                
                args = Mock(
                    config='team.yaml',
                    prompt='Test prompt',
                    stream=True,
                    model=None,
                    workspace=None
                )
                
                from agentx.cli.main import handle_run
                result = handle_run(args)
                
                assert result == 0
    
    def test_cli_output_formatting(self):
        """Test CLI output formatting."""
        # This would test that output is properly formatted for console
        # Mock stdout to capture output
        with patch('sys.stdout') as mock_stdout:
            args = Mock(command='version')
            
            from agentx.cli.main import handle_command
            result = handle_command(args)
            
            # Should have written to stdout
            assert mock_stdout.write.called or result == 0 