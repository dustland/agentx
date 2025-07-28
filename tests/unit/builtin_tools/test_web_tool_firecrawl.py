"""
Tests for WebTool with Firecrawl implementation.

These tests verify the web content extraction functionality using Firecrawl,
including handling of multiple URLs and error scenarios.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from vibex.builtin_tools.web import WebTool, WebContent
from vibex.core.tool import ToolResult


class TestWebToolFirecrawl:
    """Test web tool with Firecrawl implementation."""

    def setup_method(self):
        """Setup test environment."""
        # Patch environment variable for API key
        self.patcher = patch.dict('os.environ', {'FIRECRAWL_API_KEY': 'test-api-key'})
        self.patcher.start()
        
        # Mock FirecrawlApp at module level
        self.firecrawl_patcher = patch('vibex.builtin_tools.web.FirecrawlApp')
        self.mock_firecrawl_class = self.firecrawl_patcher.start()
        
        # Create mock instance
        self.mock_firecrawl = Mock()
        self.mock_firecrawl_class.return_value = self.mock_firecrawl
        
        self.web_tool = WebTool()

    def teardown_method(self):
        """Cleanup test environment."""
        self.patcher.stop()
        self.firecrawl_patcher.stop()

    @pytest.mark.asyncio
    async def test_extract_urls_single_success(self):
        """Test successful extraction of a single URL."""
        test_url = "https://example.com"
        test_markdown = "# Example Title\nThis is example content."
        test_title = "Example Title"

        # Mock the scrape result
        self.mock_firecrawl.scrape_url.return_value = {
            'success': True,
            'markdown': test_markdown,
            'metadata': {
                'title': test_title
            }
        }

        result = await self.web_tool.extract_urls(test_url)
        
        assert result.success is True
        assert result.metadata["total_urls"] == 1
        assert result.metadata["successful_extractions"] == 1
        assert result.metadata["failed_extractions"] == 0
        
        # Verify the result contains expected data
        assert result.result["url"] == test_url
        assert result.result["extraction_successful"] is True
        assert result.result["content_length"] > 0
        assert result.result["title"] == test_title

    @pytest.mark.asyncio
    async def test_extract_urls_multiple(self):
        """Test extraction of multiple URLs."""
        test_urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ]
        
        # Mock different results for each URL
        def mock_scrape_side_effect(url, params=None):
            return {
                'success': True,
                'markdown': f"# Content from {url}",
                'metadata': {
                    'title': f"Title from {url}"
                }
            }
        
        self.mock_firecrawl.scrape_url.side_effect = mock_scrape_side_effect

        result = await self.web_tool.extract_urls(test_urls)
        
        # Verify all extractions succeeded
        assert result.success is True
        assert result.metadata["total_urls"] == 3
        assert result.metadata["successful_extractions"] == 3
        assert result.metadata["failed_extractions"] == 0
        
        # Verify each URL was processed
        for i, url_result in enumerate(result.result):
            assert url_result["url"] == test_urls[i]
            assert url_result["extraction_successful"] is True

    @pytest.mark.asyncio
    async def test_extract_urls_with_retry(self):
        """Test retry logic on failures."""
        test_url = "https://example.com"
        
        # First two calls fail, third succeeds
        self.mock_firecrawl.scrape_url.side_effect = [
            Exception("Connection error"),
            Exception("Timeout error"),
            {
                'success': True,
                'markdown': "# Success after retry",
                'metadata': {'title': "Success"}
            }
        ]

        result = await self.web_tool.extract_urls(test_url)
        
        # Should succeed after retries
        assert result.success is True
        assert result.result["extraction_successful"] is True
        
        # Verify scrape_url was called 3 times
        assert self.mock_firecrawl.scrape_url.call_count == 3

    @pytest.mark.asyncio
    async def test_extract_urls_failure_after_retries(self):
        """Test handling when all retries fail."""
        test_url = "https://example.com"
        
        # All attempts fail
        self.mock_firecrawl.scrape_url.side_effect = Exception("Persistent error")

        result = await self.web_tool.extract_urls(test_url)
        
        # Should return partial success (false for this single URL)
        assert result.success is False
        assert result.metadata["successful_extractions"] == 0
        assert result.metadata["failed_extractions"] == 1
        assert result.result["extraction_successful"] is False
        assert "Persistent error" in result.result["error"]

    @pytest.mark.asyncio
    async def test_extract_urls_custom_options(self):
        """Test extraction with custom options."""
        test_url = "https://example.com"
        
        self.mock_firecrawl.scrape_url.return_value = {
            'success': True,
            'html': '<div>HTML content</div>',
            'metadata': {'title': "Test Page"}
        }

        result = await self.web_tool.extract_urls(
            test_url,
            formats=["html"],
            only_main_content=False,
            include_tags=["article", "main"],
            exclude_tags=["nav", "footer"],
            wait_for_selector=".content-loaded",
            timeout=60000
        )
        
        assert result.success is True
        
        # Verify the options were passed to scrape_url
        call_args = self.mock_firecrawl.scrape_url.call_args
        params = call_args[1]['params']
        assert params['formats'] == ["html"]
        assert params['onlyMainContent'] is False
        assert params['includeTags'] == ["article", "main"]
        assert params['excludeTags'] == ["nav", "footer"]
        assert params['waitFor'] == ".content-loaded"
        assert params['timeout'] == 60000

    @pytest.mark.asyncio
    async def test_extract_urls_no_api_key(self):
        """Test behavior when API key is missing or invalid."""
        # Test with real Firecrawl behavior - it will try to scrape but get 401
        # Mock scrape to raise the expected error
        self.mock_firecrawl.scrape_url.side_effect = Exception(
            "Unexpected error during scrape URL: Status code 401. Unauthorized: Token missing"
        )
        
        result = await self.web_tool.extract_urls("https://example.com")
        
        assert result.success is False
        assert result.metadata["failed_extractions"] == 1
        # Check that the error is captured in the result
        assert "401" in result.result["error"] or "Unauthorized" in result.result["error"]

    @pytest.mark.asyncio
    async def test_extract_urls_project_storage_integration(self):
        """Test project storage integration."""
        test_url = "https://example.com"
        test_content = "# Test Content\nThis is test content."
        
        # Mock project storage
        mock_storage = AsyncMock()
        mock_storage.store_artifact = AsyncMock(return_value=Mock(success=True))
        
        self.web_tool.project_storage = mock_storage
        
        # Mock scrape result
        self.mock_firecrawl.scrape_url.return_value = {
            'success': True,
            'markdown': test_content,
            'metadata': {'title': "Test Page"}
        }

        result = await self.web_tool.extract_urls(test_url)
        
        assert result.success is True
        # Verify project storage was called
        mock_storage.store_artifact.assert_called_once()
        
        # Check the stored content includes metadata
        stored_content = mock_storage.store_artifact.call_args[1]['content']
        assert "Test Page" in stored_content
        assert test_url in stored_content

    @pytest.mark.asyncio
    async def test_extract_urls_mixed_success(self):
        """Test handling mixed success/failure results."""
        test_urls = ["https://success.com", "https://fail.com"]
        
        # First succeeds, second fails
        self.mock_firecrawl.scrape_url.side_effect = [
            {
                'success': True,
                'markdown': "# Success",
                'metadata': {'title': "Success"}
            },
            Exception("Failed to extract")
        ]

        result = await self.web_tool.extract_urls(test_urls)
        
        # Should still return success=True (partial success)
        assert result.success is True
        assert result.metadata["successful_extractions"] == 1
        assert result.metadata["failed_extractions"] == 1
        
        # Check individual results
        assert result.result[0]["extraction_successful"] is True
        assert result.result[1]["extraction_successful"] is False