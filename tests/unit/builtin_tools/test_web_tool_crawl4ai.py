"""
Tests for WebTool with Crawl4AI implementation.

These tests verify the web content extraction functionality using Crawl4AI,
including handling of multiple URLs and browser context management.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from vibex.builtin_tools.web import WebTool, WebContent
from vibex.core.tool import ToolResult


class TestWebToolCrawl4AI:
    """Test web tool with Crawl4AI implementation."""

    def setup_method(self):
        """Setup test environment."""
        self.web_tool = WebTool()

    @pytest.mark.asyncio
    async def test_extract_urls_single_success(self):
        """Test successful extraction of a single URL."""
        test_url = "https://example.com"
        test_markdown = "# Example Title\nThis is example content."
        test_title = "Example Title"

        # Mock the crawl result
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = test_markdown
        mock_result.url = test_url
        mock_result.metadata = {"title": test_title}
        
        # Mock crawler's arun method
        mock_crawler = AsyncMock()
        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)

        with patch('vibex.builtin_tools.web.AsyncWebCrawler', return_value=mock_crawler):
            result = await self.web_tool.extract_urls(test_url)
            
            assert result.success is True
            assert result.metadata["total_urls"] == 1
            assert result.metadata["successful_extractions"] == 1
            assert result.metadata["failed_extractions"] == 0
            
            # Verify the result contains expected data
            assert result.result["url"] == test_url
            assert result.result["extraction_successful"] is True
            assert result.result["content_length"] > 0

    @pytest.mark.asyncio
    async def test_extract_urls_multiple_with_browser_context_fix(self):
        """Test that each URL gets its own browser instance to avoid context issues."""
        test_urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ]
        
        # Track browser instance creations
        browser_instances = []
        
        def create_mock_crawler(*args, **kwargs):
            """Create a new mock crawler instance."""
            mock_crawler = AsyncMock()
            
            # Create different results for each URL
            def mock_arun(url, config):
                mock_result = Mock()
                mock_result.success = True
                mock_result.markdown = f"# Content from {url}"
                mock_result.url = url
                mock_result.metadata = {"title": f"Title from {url}"}
                return mock_result
            
            mock_crawler.arun = AsyncMock(side_effect=mock_arun)
            mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
            mock_crawler.__aexit__ = AsyncMock(return_value=None)
            
            browser_instances.append(mock_crawler)
            return mock_crawler

        with patch('vibex.builtin_tools.web.AsyncWebCrawler', side_effect=create_mock_crawler):
            result = await self.web_tool.extract_urls(test_urls)
            
            # Verify separate browser instances were created
            assert len(browser_instances) == 3, "Should create one browser instance per URL"
            
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
    async def test_extract_urls_handles_browser_context_error(self):
        """Test handling of browser context closure errors."""
        test_urls = ["https://example1.com", "https://example2.com"]
        
        # Simulate browser context error on second URL
        call_count = 0
        
        def create_mock_crawler(*args, **kwargs):
            nonlocal call_count
            mock_crawler = AsyncMock()
            
            if call_count == 0:
                # First URL succeeds
                mock_result = Mock()
                mock_result.success = True
                mock_result.markdown = "# Success"
                mock_result.url = test_urls[0]
                mock_result.metadata = {"title": "Success"}
                mock_crawler.arun = AsyncMock(return_value=mock_result)
            else:
                # Second URL fails with browser context error
                mock_crawler.arun = AsyncMock(
                    side_effect=Exception("Target page, context or browser has been closed")
                )
            
            mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
            mock_crawler.__aexit__ = AsyncMock(return_value=None)
            
            call_count += 1
            return mock_crawler

        with patch('vibex.builtin_tools.web.AsyncWebCrawler', side_effect=create_mock_crawler):
            result = await self.web_tool.extract_urls(test_urls)
            
            # Should still return partial success
            assert result.success is True
            assert result.metadata["total_urls"] == 2
            assert result.metadata["successful_extractions"] == 1
            assert result.metadata["failed_extractions"] == 1
            
            # Check individual results
            assert result.result[0]["extraction_successful"] is True
            assert result.result[1]["extraction_successful"] is False
            assert "browser has been closed" in result.result[1]["error"]

    @pytest.mark.asyncio
    async def test_extract_urls_with_extraction_types(self):
        """Test different extraction types."""
        test_url = "https://example.com"
        
        # Test markdown extraction (default)
        mock_crawler = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "# Markdown content"
        mock_result.content = "# Markdown content"  # Add content attribute
        mock_result.url = test_url
        mock_result.metadata = {"title": "Test"}
        mock_result.extracted_content = None  # CSS extraction result
        mock_result.cleaned_html = None
        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)

        with patch('vibex.builtin_tools.web.AsyncWebCrawler', return_value=mock_crawler):
            # Test with css selector
            result = await self.web_tool.extract_urls(
                test_url, 
                extraction_type="css",
                css_selector=".content"
            )
            assert result.success is True
            
            # Verify extraction strategy was set
            call_args = mock_crawler.arun.call_args
            assert call_args is not None
            run_config = call_args[1]['config']
            assert hasattr(run_config, 'extraction_strategy')

    @pytest.mark.asyncio
    async def test_extract_urls_taskspace_integration(self):
        """Test project_storage storage integration."""
        test_url = "https://example.com"
        test_content = "# Test Content\nThis is test content."
        
        # Mock project_storage
        mock_taskspace = AsyncMock()
        mock_taskspace.store_artifact = AsyncMock(return_value=Mock(success=True))
        
        self.web_tool.project_storage = mock_taskspace
        
        # Mock crawler
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = test_content
        mock_result.content = test_content
        mock_result.url = test_url
        mock_result.metadata = {"title": "Test Page"}
        
        mock_crawler = AsyncMock()
        mock_crawler.arun = AsyncMock(return_value=mock_result)
        mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler.__aexit__ = AsyncMock(return_value=None)

        with patch('vibex.builtin_tools.web.AsyncWebCrawler', return_value=mock_crawler):
            result = await self.web_tool.extract_urls(test_url)
            
            assert result.success is True
            # Verify project_storage was called
            mock_taskspace.store_artifact.assert_called_once()
            
            # Check the stored content includes metadata
            stored_content = mock_taskspace.store_artifact.call_args[1]['content']
            assert "Test Page" in stored_content
            assert test_url in stored_content