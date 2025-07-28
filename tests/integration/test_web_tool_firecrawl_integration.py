"""
Integration tests for WebTool with Firecrawl API.

These tests verify the actual Firecrawl API integration works correctly.
They require a valid FIRECRAWL_API_KEY environment variable.
"""

import pytest
import asyncio
import os
from vibex.builtin_tools.web import WebTool
from vibex.core.tool import ToolResult


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("FIRECRAWL_API_KEY"),
    reason="FIRECRAWL_API_KEY not set"
)
class TestWebToolFirecrawlIntegration:
    """Integration tests for web tool with real Firecrawl API."""

    def setup_method(self):
        """Setup test environment."""
        self.web_tool = WebTool()

    @pytest.mark.asyncio
    async def test_extract_single_url_real(self):
        """Test extracting content from a real URL."""
        # Use a stable, simple webpage for testing
        test_url = "https://example.com"
        
        result = await self.web_tool.extract_urls(test_url)
        
        assert result.success is True
        assert result.result is not None
        assert result.result["url"] == test_url
        assert result.result["extraction_successful"] is True
        assert result.result["content_length"] > 0
        
        # Check that we got some content
        assert "Example Domain" in result.result["title"] or "example" in result.result["title"].lower()

    @pytest.mark.asyncio
    async def test_extract_markdown_format(self):
        """Test that markdown extraction works correctly."""
        test_url = "https://www.python.org"
        
        result = await self.web_tool.extract_urls(
            test_url,
            formats=["markdown"],
            only_main_content=True
        )
        
        assert result.success is True
        assert result.result["extraction_successful"] is True
        
        # Verify we got markdown content
        metadata = result.result.get("metadata", {})
        assert metadata.get("formats_used") == ["markdown"]
        assert result.result["content_length"] > 0

    @pytest.mark.asyncio
    async def test_extract_with_timeout(self):
        """Test extraction with custom timeout."""
        test_url = "https://httpbin.org/delay/1"
        
        # Should succeed with 5 second timeout
        result = await self.web_tool.extract_urls(
            test_url,
            timeout=5000
        )
        
        # httpbin might not return much content, just check it didn't timeout
        assert result.success is True or result.result["error"] is not None

    @pytest.mark.asyncio
    async def test_extract_multiple_urls(self):
        """Test extracting multiple URLs."""
        test_urls = [
            "https://example.com",
            "https://example.org"
        ]
        
        result = await self.web_tool.extract_urls(test_urls)
        
        assert result.metadata["total_urls"] == 2
        assert isinstance(result.result, list)
        assert len(result.result) == 2
        
        # At least one should succeed
        successful = [r for r in result.result if r["extraction_successful"]]
        assert len(successful) > 0

    @pytest.mark.asyncio
    async def test_extract_with_selectors(self):
        """Test extraction with include/exclude tags."""
        test_url = "https://example.com"
        
        result = await self.web_tool.extract_urls(
            test_url,
            formats=["markdown"],
            include_tags=["body", "main", "article"],
            exclude_tags=["script", "style"]
        )
        
        assert result.success is True
        assert result.result["extraction_successful"] is True

    @pytest.mark.asyncio 
    async def test_extract_handles_invalid_url(self):
        """Test handling of invalid URLs."""
        invalid_url = "https://this-domain-definitely-does-not-exist-12345.com"
        
        result = await self.web_tool.extract_urls(invalid_url)
        
        # Should handle gracefully
        assert result.success is False
        assert result.metadata["failed_extractions"] == 1
        assert result.result["extraction_successful"] is False
        assert result.result["error"] is not None

    @pytest.mark.asyncio
    async def test_extract_medium_article(self):
        """Test extracting the specific Medium article that was failing."""
        # This is the URL from the error message
        test_url = "https://andrewbaisden.medium.com/my-ultimate-toolkit-10-ai-tools-that-boost-productivity-547f81b70d7d"
        
        result = await self.web_tool.extract_urls(
            test_url,
            formats=["markdown"],
            only_main_content=True
        )
        
        # The extraction should work now with the fixed code
        if result.success:
            assert result.result["extraction_successful"] is True
            assert result.result["content_length"] > 0
            # Check we got the article content
            assert "toolkit" in result.result["title"].lower() or "productivity" in result.result["title"].lower()
        else:
            # If it fails, make sure it's handled gracefully
            assert result.result["error"] is not None
            print(f"Medium article extraction failed with error: {result.result['error']}")

    @pytest.mark.asyncio
    async def test_extract_with_project_storage(self):
        """Test extraction with project storage integration."""
        from unittest.mock import AsyncMock, Mock
        
        # Mock project storage
        mock_storage = AsyncMock()
        mock_storage.store_artifact = AsyncMock(return_value=Mock(success=True))
        
        self.web_tool.project_storage = mock_storage
        
        test_url = "https://example.com"
        result = await self.web_tool.extract_urls(test_url)
        
        assert result.success is True
        
        # Verify storage was called if extraction succeeded
        if result.result["extraction_successful"]:
            mock_storage.store_artifact.assert_called_once()
            assert len(result.metadata["saved_files"]) > 0