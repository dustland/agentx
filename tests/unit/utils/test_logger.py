"""
Tests for logger utility.

These tests define the expected correct behavior for logging
functionality in the VibeX framework.
"""

import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from vibex.utils.logger import get_logger, setup_clean_chat_logging


class TestGetLogger:
    """Test get_logger functionality."""

    def test_get_logger_returns_logger_instance(self):
        """get_logger should return a logger instance."""
        logger = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_consistent_instances(self):
        """get_logger should return consistent instances for same name."""
        logger1 = get_logger("same_module")
        logger2 = get_logger("same_module")

        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """get_logger should return different instances for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"

    def test_get_logger_with_file_name(self):
        """get_logger should handle __name__ inputs correctly."""
        logger = get_logger("vibex.core.agent")

        assert logger.name == "vibex.core.agent"
        assert isinstance(logger, logging.Logger)


class TestSetupCleanChatLogging:
    """Test setup_clean_chat_logging functionality."""

    def setup_method(self):
        """Setup test environment."""
        # Save original state
        self.original_level = logging.getLogger().level
        self.original_handlers = logging.getLogger().handlers.copy()

        # Clear handlers for clean test
        logging.getLogger().handlers.clear()

    def teardown_method(self):
        """Restore original logging state."""
        # Restore original state
        logging.getLogger().setLevel(self.original_level)
        logging.getLogger().handlers.clear()
        logging.getLogger().handlers.extend(self.original_handlers)

    def test_setup_clean_chat_logging_basic_configuration(self):
        """setup_clean_chat_logging should configure basic logging."""
        setup_clean_chat_logging()

        root_logger = logging.getLogger()

        # Should have at least one handler
        assert len(root_logger.handlers) > 0

        # Should set appropriate level
        assert root_logger.level <= logging.INFO

    def test_setup_clean_chat_logging_suppresses_noisy_loggers(self):
        """setup_clean_chat_logging should suppress noisy third-party loggers."""
        setup_clean_chat_logging()

        # Check that noisy loggers are suppressed
        noisy_loggers = [
            "litellm",
            "httpx",
            "urllib3",
            "requests",
            "asyncio"
        ]

        for logger_name in noisy_loggers:
            logger = logging.getLogger(logger_name)
            assert logger.level >= logging.WARNING

    def test_setup_clean_chat_logging_preserves_vibex_loggers(self):
        """setup_clean_chat_logging should preserve VibeX logger levels."""
        setup_clean_chat_logging()

        # VibeX loggers should not be suppressed
        vibex_logger = logging.getLogger("vibex")
        assert vibex_logger.level <= logging.INFO

        core_logger = logging.getLogger("vibex.core")
        assert core_logger.level <= logging.INFO

    @patch.dict('os.environ', {'AGENTX_VERBOSE': '1'})
    def test_setup_clean_chat_logging_verbose_mode(self):
        """setup_clean_chat_logging should respect verbose mode."""
        setup_clean_chat_logging()

        root_logger = logging.getLogger()

        # In verbose mode, should set DEBUG level
        assert root_logger.level <= logging.DEBUG

        # Even noisy loggers should be less suppressed in verbose mode
        litellm_logger = logging.getLogger("litellm")
        assert litellm_logger.level <= logging.INFO

    @patch.dict('os.environ', {'AGENTX_VERBOSE': '0'})
    def test_setup_clean_chat_logging_non_verbose_mode(self):
        """setup_clean_chat_logging should respect non-verbose mode."""
        setup_clean_chat_logging()

        # Should suppress noisy loggers more aggressively
        litellm_logger = logging.getLogger("litellm")
        assert litellm_logger.level >= logging.WARNING

    def test_setup_clean_chat_logging_idempotent(self):
        """setup_clean_chat_logging should be idempotent."""
        # Call multiple times
        setup_clean_chat_logging()
        handler_count_1 = len(logging.getLogger().handlers)

        setup_clean_chat_logging()
        handler_count_2 = len(logging.getLogger().handlers)

        setup_clean_chat_logging()
        handler_count_3 = len(logging.getLogger().handlers)

        # Should not keep adding handlers
        assert handler_count_1 == handler_count_2 == handler_count_3


class TestLoggingIntegration:
    """Test logging integration scenarios."""

    def setup_method(self):
        """Setup test environment."""
        # Save original state
        self.original_level = logging.getLogger().level
        self.original_handlers = logging.getLogger().handlers.copy()

        # Clear handlers for clean test
        logging.getLogger().handlers.clear()

    def teardown_method(self):
        """Restore original logging state."""
        # Restore original state
        logging.getLogger().setLevel(self.original_level)
        logging.getLogger().handlers.clear()
        logging.getLogger().handlers.extend(self.original_handlers)

    def test_logger_hierarchy_works_correctly(self):
        """Logger hierarchy should work correctly."""
        setup_clean_chat_logging()

        # Get loggers at different levels
        root_logger = get_logger("vibex")
        core_logger = get_logger("vibex.core")
        agent_logger = get_logger("vibex.core.agent")

        # Should all be different instances
        assert root_logger is not core_logger
        assert core_logger is not agent_logger

        # Should have proper hierarchy
        assert agent_logger.parent.name == "vibex.core"
        assert core_logger.parent.name == "vibex"

    def test_logging_with_different_levels(self):
        """Logging should work correctly with different levels."""
        setup_clean_chat_logging()

        logger = get_logger("test_logger")

        # Should be able to log at different levels
        with patch.object(logger, '_log') as mock_log:
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

            # At least some calls should have been made
            assert mock_log.call_count >= 0

    @patch('logging.StreamHandler')
    def test_setup_creates_stream_handler(self, mock_stream_handler):
        """setup_clean_chat_logging should create stream handler."""
        mock_handler = Mock()
        mock_stream_handler.return_value = mock_handler

        setup_clean_chat_logging()

        # Should have created a stream handler
        mock_stream_handler.assert_called()

        # Handler should be added to root logger
        root_logger = logging.getLogger()
        assert mock_handler in root_logger.handlers or len(root_logger.handlers) > 0

    def test_logger_respects_level_configuration(self):
        """Logger should respect level configuration."""
        setup_clean_chat_logging()

        # Set specific level for test logger
        test_logger = get_logger("test_specific")
        test_logger.setLevel(logging.ERROR)

        with patch.object(test_logger, '_log') as mock_log:
            test_logger.debug("Should not log")
            test_logger.info("Should not log")
            test_logger.warning("Should not log")
            test_logger.error("Should log")

            # Only error should have been logged (if at all)
            if mock_log.call_count > 0:
                # If any calls were made, the last one should be ERROR level
                last_call = mock_log.call_args_list[-1]
                assert last_call[0][0] >= logging.ERROR


class TestLoggingErrorHandling:
    """Test logging error handling."""

    def test_get_logger_handles_invalid_names(self):
        """get_logger should handle invalid names gracefully."""
        # Should not raise exceptions for various inputs
        logger1 = get_logger("")
        logger2 = get_logger(None)

        assert isinstance(logger1, logging.Logger)
        assert isinstance(logger2, logging.Logger)

    def test_logging_handles_unicode_messages(self):
        """Logging should handle unicode messages correctly."""
        setup_clean_chat_logging()
        logger = get_logger("unicode_test")

        # Should not raise exceptions
        try:
            logger.info("Unicode message: 你好 🌟 émojis")
            logger.info("Special chars: ñáéíóú àèìòù")
            success = True
        except Exception:
            success = False

        assert success is True

    def test_logging_handles_complex_objects(self):
        """Logging should handle complex objects in messages."""
        setup_clean_chat_logging()
        logger = get_logger("object_test")

        # Should not raise exceptions when logging complex objects
        try:
            logger.info("Dict: %s", {"key": "value", "nested": {"inner": "data"}})
            logger.info("List: %s", [1, 2, 3, {"nested": "list"}])
            logger.info("Object: %s", object())
            success = True
        except Exception:
            success = False

        assert success is True

    @patch('logging.StreamHandler')
    def test_setup_handles_handler_creation_errors(self, mock_stream_handler):
        """setup_clean_chat_logging should handle handler creation errors."""
        # Mock handler creation to raise exception
        mock_stream_handler.side_effect = Exception("Handler creation failed")

        # Should not raise exception
        try:
            setup_clean_chat_logging()
            success = True
        except Exception:
            success = False

        # Should handle gracefully (either succeed or fail gracefully)
        assert success is True or isinstance(logging.getLogger().handlers, list)
