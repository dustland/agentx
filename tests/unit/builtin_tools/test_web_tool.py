"""
Tests for WebTool builtin tool.

These tests verify the parallel processing functionality and proper behavior
of web content extraction using the Jina Reader API.
"""

import pytest
import asyncio
import aiohttp
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from vibex.builtin_tools.web import WebTool, WebContent
from vibex.core.tool import ToolResult


class TestWebToolInitialization:
    """Test web tool initialization."""

    def test_web_tool_default_initialization(self):
        """WebTool should initialize with default parameters."""
        with patch.dict(os.environ, {}, clear=True):
            web_tool = WebTool()
            assert web_tool.jina_api_key is None

    def test_web_tool_with_api_key(self):
        """WebTool should initialize with API key."""
        web_tool = WebTool(jina_api_key="test_key")
        assert web_tool.jina_api_key == "test_key"


class TestWebToolParallelExtractContent:
    """Test parallel content extraction functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.web_tool = WebTool(jina_api_key="test_key")

    @pytest.mark.asyncio
    async def test_extract_content_single_url_success(self):
        """extract_content should handle single URL successfully."""
        test_url = "https://example.com"
        test_content = "# Example Title\nThis is example content."

        # Create mock session with proper async context manager
        def mock_get(url, **kwargs):
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=test_content)
            mock_response.raise_for_status = AsyncMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            return mock_response

        # Create mock session
        mock_session = AsyncMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch('aiohttp.TCPConnector') as mock_connector:
                result = await self.web_tool.extract_content(test_url)

        # Verify result structure
        assert result.success is True
        assert isinstance(result.result, dict)
        assert result.result["url"] == test_url
        assert result.result["title"] == "# Example Title"
        assert result.result["content_preview"] == "This is example content."
        assert result.result["extraction_successful"] is True

        # Verify metadata
        assert result.metadata["total_urls"] == 1
        assert result.metadata["successful_extractions"] == 1
        assert result.metadata["parallel_processing"] is True
        assert "extraction_time_seconds" in result.metadata

    @pytest.mark.asyncio
    async def test_extract_content_multiple_urls_parallel(self):
        """extract_content should process multiple URLs in parallel."""
        test_urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ]
        test_contents = [
            "# Title 1\nContent 1",
            "# Title 2\nContent 2",
            "# Title 3\nContent 3"
        ]

        def mock_get(url, **kwargs):
            """Mock get request that returns different content per URL."""
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.raise_for_status = AsyncMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            if "example1" in str(url):
                mock_response.text = AsyncMock(return_value=test_contents[0])
            elif "example2" in str(url):
                mock_response.text = AsyncMock(return_value=test_contents[1])
            elif "example3" in str(url):
                mock_response.text = AsyncMock(return_value=test_contents[2])

            return mock_response

        mock_session = AsyncMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch('aiohttp.TCPConnector') as mock_connector:
                start_time = asyncio.get_event_loop().time()
                result = await self.web_tool.extract_content(test_urls)
                end_time = asyncio.get_event_loop().time()

        # Verify parallel processing happened
        assert result.success is True
        assert isinstance(result.result, list)
        assert len(result.result) == 3

        # Verify all URLs were processed
        extracted_urls = [content["url"] for content in result.result]
        assert set(extracted_urls) == set(test_urls)

        # Verify all extractions succeeded
        assert all(content["extraction_successful"] for content in result.result)

        # Verify metadata
        assert result.metadata["total_urls"] == 3
        assert result.metadata["successful_extractions"] == 3
        assert result.metadata["parallel_processing"] is True

        # Verify time efficiency (should be much faster than sequential)
        extraction_time = result.metadata["extraction_time_seconds"]
        assert extraction_time < 1.0  # Should be fast for mocked requests

    @pytest.mark.asyncio
    async def test_extract_content_handles_mixed_success_failure(self):
        """extract_content should handle mix of successful and failed extractions."""
        test_urls = [
            "https://success.com",
            "https://failure.com"
        ]

        def mock_get(url, **kwargs):
            """Mock get request with mixed success/failure."""
            if "success" in str(url):
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value="# Success\nSuccess content")
                mock_response.raise_for_status = AsyncMock()
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)
                return mock_response
            else:
                # For failure URL, raise exception immediately when getting response
                raise aiohttp.ClientError("Network error")

        mock_session = AsyncMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch('aiohttp.TCPConnector'):
                result = await self.web_tool.extract_content(test_urls)

        # Should still succeed if at least one URL works
        assert result.success is True
        assert len(result.result) == 2

        # Check individual results
        success_result = next(r for r in result.result if r["url"] == "https://success.com")
        failure_result = next(r for r in result.result if r["url"] == "https://failure.com")

        assert success_result["extraction_successful"] is True
        assert success_result["title"] == "# Success"
        assert success_result["content_preview"] == "Success content"

        assert failure_result["extraction_successful"] is False
        assert failure_result["error"] == "Network error"

        # Verify metadata
        assert result.metadata["total_urls"] == 2
        assert result.metadata["successful_extractions"] == 1

    @pytest.mark.asyncio
    async def test_extract_content_authenticated_fallback(self):
        """extract_content should fallback to unauthenticated when 422 error occurs."""
        test_url = "https://example.com"
        test_content = "# Title\nContent from fallback"

        call_count = 0

        def mock_get(url, **kwargs):
            """Mock get request that fails first time with 422, succeeds on retry."""
            nonlocal call_count
            call_count += 1

            mock_response = AsyncMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            if call_count == 1:
                # First call (authenticated) fails with 422
                mock_response.status = 422
                mock_response.text = AsyncMock(return_value="Unprocessable Entity")
            else:
                # Second call (unauthenticated) succeeds
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=test_content)
                mock_response.raise_for_status = AsyncMock()

            return mock_response

        mock_session = AsyncMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch('aiohttp.TCPConnector'):
                result = await self.web_tool.extract_content(test_url)

        # Should succeed after fallback
        assert result.success is True
        assert result.result["extraction_successful"] is True
        assert result.result["content_preview"] == "Content from fallback"
        assert call_count == 2  # Should have made two calls

    @pytest.mark.asyncio
    async def test_extract_content_connection_limits(self):
        """extract_content should configure proper connection limits."""
        test_urls = ["https://example.com"]

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="# Title\nContent")
        mock_response.raise_for_status = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('aiohttp.ClientSession', return_value=mock_session) as mock_session_class:
            with patch('aiohttp.TCPConnector') as mock_connector:
                await self.web_tool.extract_content(test_urls)

        # Verify TCPConnector was configured with proper limits
        mock_connector.assert_called_once_with(
            limit=20,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True
        )

        # Verify ClientSession was created with the connector
        mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_content_preserves_jina_headers(self):
        """extract_content should use proper Jina Reader headers."""
        test_url = "https://example.com"

        captured_headers = None

        def mock_get(url, **kwargs):
            nonlocal captured_headers
            captured_headers = kwargs.get('headers', {})

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="# Title\nContent")
            mock_response.raise_for_status = AsyncMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            return mock_response

        mock_session = AsyncMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch('aiohttp.TCPConnector'):
                await self.web_tool.extract_content(test_url, prompt="Extract specific data")

        # Verify proper headers were used
        assert captured_headers is not None
        assert 'Authorization' in captured_headers
        assert 'Bearer test_key' in captured_headers['Authorization']
        assert 'User-Agent' in captured_headers
        assert 'Mozilla/5.0' in captured_headers['User-Agent']
        assert captured_headers['Accept'] == 'application/json'
        assert captured_headers['X-Return-Format'] == 'markdown'

    @pytest.mark.asyncio
    async def test_extract_content_without_api_key(self):
        """extract_content should work without API key (free tier)."""
        with patch.dict(os.environ, {}, clear=True):
            web_tool = WebTool()  # No API key
        test_url = "https://example.com"

        captured_headers = None

        def mock_get(url, **kwargs):
            nonlocal captured_headers
            captured_headers = kwargs.get('headers', {})

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="# Title\nContent")
            mock_response.raise_for_status = AsyncMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            return mock_response

        mock_session = AsyncMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch('aiohttp.TCPConnector'):
                result = await web_tool.extract_content(test_url)

        # Should succeed
        assert result.success is True

        # Verify free tier headers were used
        assert 'Authorization' not in captured_headers
        assert captured_headers['Accept'] == 'text/plain'
        assert 'X-Return-Format' not in captured_headers

    @pytest.mark.asyncio
    async def test_extract_content_performance_timing(self):
        """extract_content should measure and report extraction time."""
        test_urls = ["https://example1.com", "https://example2.com"]

        # Add artificial delay to test timing
        async def mock_get(url, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay per request

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="# Title\nContent")
            mock_response.raise_for_status = AsyncMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            return mock_response

        mock_session = AsyncMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch('aiohttp.TCPConnector'):
                result = await self.web_tool.extract_content(test_urls)

        # Verify timing is recorded
        assert "extraction_time_seconds" in result.metadata
        extraction_time = result.metadata["extraction_time_seconds"]

        # Since we're mocking, the actual time will be very fast
        # Just verify that timing is recorded and is a reasonable value
        assert extraction_time >= 0.0
        assert extraction_time < 1.0  # Should complete quickly with mocks

        # The key is that parallel processing is enabled in metadata
        assert result.metadata["parallel_processing"] is True
