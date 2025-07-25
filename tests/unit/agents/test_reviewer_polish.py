"""
Unit tests for reviewer agent's polish functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from vibex.core.agent import Agent
from vibex.core.brain import Brain
from vibex.core.config import AgentConfig
from vibex.storage.project import ProjectStorage


class TestReviewerPolish:
    """Test reviewer agent's ability to polish documents."""
    
    @pytest.fixture
    def reviewer_config(self):
        """Create reviewer agent configuration."""
        return AgentConfig(
            name="reviewer",
            role="specialist",
            prompt_file="agents/reviewer.md",
            description="Reviewer agent",
            brain_config={
                "provider": "deepseek",
                "model": "deepseek/deepseek-chat"
            },
            tools=["read_file", "write_file", "list_files"]
        )
    
    @pytest.fixture
    def mock_taskspace_with_draft(self, tmp_path):
        """Create mock project_storage with a draft document."""
        project_dir = tmp_path / "test_taskspace"
        project_dir.mkdir()
        artifacts_dir = project_dir / "artifacts"
        artifacts_dir.mkdir()
        
        # Create draft with issues to polish
        draft_content = """# PostgreSQL vs MySQL Comparison

## Introduction

PostgreSQL and MySQL are both popular database systems. PostgreSQL is known for its robustness. MySQL is known for its speed.

## Performance

PostgreSQL has good performance. It handles complex queries well. PostgreSQL also has good performance for write operations.

MySQL has excellent performance. It is very fast for read operations. MySQL has excellent performance especially for simple queries.

## Features

PostgreSQL has many advanced features. These include:
- JSON support
- Full text search
- Advanced indexing

MySQL also has many features. These include:
- JSON support  
- Full text search
- Good replication

## Conclusion

Both databases are good choices. PostgreSQL is better for complex applications. MySQL is better for simple applications. Both databases have their strengths."""
        
        (artifacts_dir / "draft_report.md").write_text(draft_content)
        
        project_storage = ProjectStorage(
            task_id="test_task",
            project_path=project_dir
        )
        return project_storage
    
    @pytest.mark.asyncio
    async def test_reviewer_identifies_draft_for_polishing(self, reviewer_config, mock_taskspace_with_draft):
        """Test that reviewer correctly identifies draft documents."""
        with patch('vibex.core.agent.Brain') as MockBrain:
            mock_brain = Mock(spec=Brain)
            MockBrain.return_value = mock_brain
            
            reviewer = Agent(
                config=reviewer_config,
                task_config=Mock(project_storage=mock_taskspace_with_draft)
            )
            
            # Track tool calls
            tool_calls = []
            
            async def track_tools(tool_name, **kwargs):
                tool_calls.append((tool_name, kwargs))
                if tool_name == "list_files":
                    return Mock(success=True, result=["draft_report.md", "notes.txt"])
                elif tool_name == "read_file":
                    if kwargs.get('filename') == "draft_report.md":
                        content = (mock_taskspace_with_draft.artifacts_path / "draft_report.md").read_text()
                        return Mock(success=True, result=content)
                return Mock(success=True)
            
            reviewer.tool_manager = Mock()
            reviewer.tool_manager.execute = AsyncMock(side_effect=track_tools)
            
            mock_brain.generate_response = AsyncMock(return_value=Mock(
                content="I'll polish the draft document.",
                tool_calls=[
                    {"function": {"name": "list_files", "arguments": "{}"}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "draft_report.md"}'}}
                ]
            ))
            
            await reviewer.execute_task([{
                "role": "user",
                "content": "Review and polish the draft document."
            }])
            
            # Verify reviewer found and read the draft
            assert any(call[0] == "read_file" and call[1].get('filename') == "draft_report.md" 
                      for call in tool_calls)
    
    @pytest.mark.asyncio
    async def test_reviewer_creates_polished_version(self, reviewer_config, mock_taskspace_with_draft):
        """Test that reviewer creates a polished version of the document."""
        with patch('vibex.core.agent.Brain') as MockBrain:
            mock_brain = Mock(spec=Brain)
            MockBrain.return_value = mock_brain
            
            reviewer = Agent(
                config=reviewer_config,
                task_config=Mock(project_storage=mock_taskspace_with_draft)
            )
            
            # Expected polished content (with improvements)
            polished_content = """# PostgreSQL vs MySQL: A Comprehensive Comparison for Enterprise Applications

## Executive Summary

PostgreSQL and MySQL represent two of the most widely adopted open-source relational database management systems in the industry. While both offer robust solutions for data management, they excel in different scenarios. PostgreSQL distinguishes itself through advanced features and extensibility, making it ideal for complex, data-intensive applications. MySQL, conversely, prioritizes speed and simplicity, positioning itself as the go-to choice for web applications requiring rapid read operations.

## Performance Analysis

### PostgreSQL Performance Characteristics

PostgreSQL demonstrates exceptional performance in handling complex queries and concurrent write operations. Its sophisticated query planner and Multi-Version Concurrency Control (MVCC) architecture enable efficient processing of intricate data relationships without compromising data integrity.

### MySQL Performance Profile  

MySQL achieves outstanding performance in read-heavy workloads, particularly for straightforward queries. Its streamlined architecture and optimized storage engines deliver exceptional speed for web applications and content management systems.

## Feature Comparison

Both database systems offer comprehensive feature sets, though with different emphases:

**PostgreSQL** provides:
- Advanced JSON/JSONB support with indexing capabilities
- Sophisticated full-text search functionality
- Extensive indexing options including partial and expression indexes
- Superior support for complex data types

**MySQL** delivers:
- Efficient JSON support for modern applications
- Integrated full-text search capabilities
- Robust replication mechanisms for high availability
- Simplified administration and maintenance

## Strategic Recommendations

The choice between PostgreSQL and MySQL should align with your specific use case. PostgreSQL excels in scenarios requiring complex data relationships, advanced analytics, and strict ACID compliance. MySQL remains the optimal choice for high-traffic web applications prioritizing read performance and operational simplicity.

Both databases continue to evolve, with active communities ensuring long-term viability for enterprise deployments."""
            
            written_content = None
            
            async def capture_write(tool_name, **kwargs):
                nonlocal written_content
                if tool_name == "write_file":
                    written_content = kwargs.get('content')
                    return Mock(success=True, result="File written")
                elif tool_name == "read_file":
                    content = (mock_taskspace_with_draft.artifacts_path / "draft_report.md").read_text()
                    return Mock(success=True, result=content)
                return Mock(success=True)
            
            reviewer.tool_manager = Mock()
            reviewer.tool_manager.execute = AsyncMock(side_effect=capture_write)
            
            # Mock brain to generate polished content
            mock_brain.generate_response = AsyncMock(return_value=Mock(
                content="I've polished the document.",
                tool_calls=[
                    {"function": {"name": "read_file", "arguments": '{"filename": "draft_report.md"}'}},
                    {"function": {"name": "write_file", "arguments": f'{{"filename": "polished_report.md", "content": "{polished_content.replace(chr(10), "\\n")}"}}' }}
                ]
            ))
            
            await reviewer.execute_task([{
                "role": "user",
                "content": "Polish the draft document."
            }])
            
            # Verify polished version was created
            assert written_content is not None
            assert "PostgreSQL vs MySQL: A Comprehensive Comparison" in written_content
            assert "Executive Summary" in written_content
            assert len(written_content) > len((mock_taskspace_with_draft.artifacts_path / "draft_report.md").read_text())
    
    @pytest.mark.asyncio  
    async def test_reviewer_identifies_polish_improvements(self, reviewer_config, mock_taskspace_with_draft):
        """Test that reviewer identifies specific issues to polish."""
        with patch('vibex.core.agent.Brain') as MockBrain:
            mock_brain = Mock(spec=Brain)
            MockBrain.return_value = mock_brain
            
            reviewer = Agent(
                config=reviewer_config,
                task_config=Mock(project_storage=mock_taskspace_with_draft)
            )
            
            reviewer.tool_manager = Mock()
            reviewer.tool_manager.execute = AsyncMock(return_value=Mock(success=True))
            
            # Mock brain to identify issues
            review_analysis = """I've identified several areas for improvement:

1. **Redundancy**: The word "performance" is repeated too frequently
2. **Weak transitions**: Sections jump abruptly without connecting paragraphs  
3. **Inconsistent tone**: Mix of technical and casual language
4. **Vague statements**: "good choices", "better for" lack specificity
5. **Missing depth**: No concrete examples or metrics provided"""
            
            mock_brain.generate_response = AsyncMock(return_value=Mock(
                content=review_analysis,
                tool_calls=[]
            ))
            
            result = await reviewer.execute_task([{
                "role": "user",
                "content": "Analyze what needs polishing in the draft."
            }])
            
            # Verify reviewer identified key issues
            assert "Redundancy" in result.content
            assert "transitions" in result.content
            assert "tone" in result.content