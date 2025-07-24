"""
Test tool executor logging truncation functionality.

This test ensures that tool results with large content are properly truncated
in logs to prevent overwhelming console output.
"""
import pytest
from vibex.tool.executor import _truncate_content_for_logging, safe_json_dumps_for_logging


class TestLoggingTruncation:
    """Test tool result truncation for logging."""

    def test_content_field_truncation(self):
        """Test that content fields are truncated."""
        obj = {
            "content": "X" * 1000,
            "other_field": "short"
        }

        truncated = _truncate_content_for_logging(obj, max_length=100)

        assert len(truncated["content"]) <= 125  # 100 + ellipsis
        assert "truncated" in truncated["content"]
        assert truncated["other_field"] == "short"  # Short fields unchanged

    def test_title_field_truncation(self):
        """Test that title fields (like from web tools) are truncated."""
        obj = {
            "title": '{"nested": "' + "X" * 1000 + '"}',
            "url": "https://example.com"
        }

        truncated = _truncate_content_for_logging(obj, max_length=100)

        assert len(truncated["title"]) <= 125  # 100 + ellipsis
        assert "truncated" in truncated["title"]
        assert truncated["url"] == "https://example.com"  # Short fields unchanged

    def test_nested_object_truncation(self):
        """Test that nested objects are properly truncated."""
        obj = {
            "success": True,
            "result": [
                {
                    "url": "https://example.com",
                    "title": "Y" * 500,
                    "content": "Z" * 1000,
                    "metadata": {"length": 1000}
                }
            ]
        }

        truncated = _truncate_content_for_logging(obj, max_length=100)

        # Check nested truncation
        result_item = truncated["result"][0]
        assert len(result_item["title"]) <= 125
        assert len(result_item["content"]) <= 125
        assert "truncated" in result_item["title"]
        assert "truncated" in result_item["content"]
        assert result_item["url"] == "https://example.com"  # Short fields unchanged
        assert result_item["metadata"]["length"] == 1000  # Non-string fields unchanged

    def test_safe_json_dumps_for_logging(self):
        """Test complete logging function with large content."""
        obj = {
            "success": True,
            "result": [
                {
                    "title": "Large title: " + "X" * 2000,
                    "content": "Large content: " + "Y" * 3000
                }
            ]
        }

        log_output = safe_json_dumps_for_logging(obj, max_content_length=200)

        # Output should be manageable size
        assert len(log_output) < 1000
        assert "truncated" in log_output

        # Should still be valid JSON
        import json
        parsed = json.loads(log_output)
        assert parsed["success"] is True
        assert len(parsed["result"]) == 1

    def test_no_truncation_for_short_strings(self):
        """Test that short strings are not truncated."""
        obj = {
            "title": "Short title",
            "content": "Short content",
            "url": "https://example.com"
        }

        truncated = _truncate_content_for_logging(obj, max_length=100)

        assert truncated["title"] == "Short title"
        assert truncated["content"] == "Short content"
        assert truncated["url"] == "https://example.com"
        assert "truncated" not in str(truncated)
