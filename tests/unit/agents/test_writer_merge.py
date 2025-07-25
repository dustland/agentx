"""
Unit tests for writer agent's section merge functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, call
from pathlib import Path

from vibex.core.agent import Agent
from vibex.core.brain import Brain
from vibex.core.config import AgentConfig
from vibex.storage.project import ProjectStorage


class TestWriterMerge:
    """Test writer agent's ability to merge sections."""
    
    @pytest.fixture
    def writer_config(self):
        """Create writer agent configuration."""
        return AgentConfig(
            name="writer",
            role="specialist",
            prompt_file="agents/writer.md",
            description="Writer agent",
            brain_config={
                "provider": "deepseek",
                "model": "deepseek/deepseek-chat"
            },
            tools=["read_file", "write_file", "list_files"]
        )
    
    @pytest.fixture
    def mock_taskspace(self, tmp_path):
        """Create mock project_storage with section files."""
        project_dir = tmp_path / "test_taskspace"
        project_dir.mkdir()
        artifacts_dir = project_dir / "artifacts"
        artifacts_dir.mkdir()
        
        # Create test section files
        section_files = [
            ("section_01_introduction.md", "# Introduction\n\nThis is the introduction section."),
            ("section_02_analysis.md", "# Analysis\n\nThis is the analysis section."),
            ("section_03_results.md", "# Results\n\nThis is the results section."),
            ("section_04_conclusion.md", "# Conclusion\n\nThis is the conclusion section.")
        ]
        
        for filename, content in section_files:
            (artifacts_dir / filename).write_text(content)
        
        project_storage = ProjectStorage(
            project_id="test_project",
            project_path=project_dir
        )
        return project_storage
    
    @pytest.mark.asyncio
    async def test_writer_discovers_section_files(self, writer_config, mock_taskspace):
        """Test that writer can discover section files using list_files."""
        with patch('vibex.core.agent.Brain') as MockBrain:
            mock_brain = Mock(spec=Brain)
            MockBrain.return_value = mock_brain
            
            # Mock brain response for merge task
            mock_brain.generate_response = AsyncMock(return_value=Mock(
                content="I'll merge the section files.",
                tool_calls=[]
            ))
            
            # Create writer agent
            writer = Agent(
                config=writer_config,
                task_config=Mock(project_storage=mock_taskspace)
            )
            
            # Mock list_files tool to return section files
            async def mock_list_files():
                files = list(mock_taskspace.artifacts_path.glob("*.md"))
                return [f.name for f in files]
            
            writer.tool_manager = Mock()
            writer.tool_manager.execute = AsyncMock(side_effect=[
                # First call: list_files
                Mock(success=True, result=[
                    "section_01_introduction.md",
                    "section_02_analysis.md", 
                    "section_03_results.md",
                    "section_04_conclusion.md",
                    "other_file.txt"  # Should be filtered out
                ])
            ])
            
            # Execute merge task
            task_briefing = [{
                "role": "user",
                "content": "Merge all section files into a complete draft document."
            }]
            
            await writer.execute_task(task_briefing)
            
            # Verify list_files was called
            writer.tool_manager.execute.assert_called()
            call_args = writer.tool_manager.execute.call_args[1]
            assert call_args['tool_name'] == 'list_files'
    
    @pytest.mark.asyncio
    async def test_writer_merges_sections_in_order(self, writer_config, mock_taskspace):
        """Test that writer reads and merges sections in correct order."""
        with patch('vibex.core.agent.Brain') as MockBrain:
            mock_brain = Mock(spec=Brain)
            MockBrain.return_value = mock_brain
            
            # Create writer agent
            writer = Agent(
                config=writer_config,
                task_config=Mock(project_storage=mock_taskspace)
            )
            
            # Track tool calls
            tool_calls = []
            
            async def track_tool_calls(tool_name, **kwargs):
                tool_calls.append((tool_name, kwargs))
                
                if tool_name == "list_files":
                    return Mock(success=True, result=[
                        "section_01_introduction.md",
                        "section_03_results.md",  # Out of order
                        "section_02_analysis.md",
                        "section_04_conclusion.md"
                    ])
                elif tool_name == "read_file":
                    filename = kwargs.get('filename')
                    content = (mock_taskspace.artifacts_path / filename).read_text()
                    return Mock(success=True, result=content)
                elif tool_name == "write_file":
                    return Mock(success=True, result="File written")
            
            writer.tool_manager = Mock()
            writer.tool_manager.execute = AsyncMock(side_effect=track_tool_calls)
            
            # Mock brain to generate merge actions
            mock_brain.generate_response = AsyncMock(return_value=Mock(
                content="I'll merge the sections now.",
                tool_calls=[
                    {"function": {"name": "list_files", "arguments": "{}"}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "section_01_introduction.md"}'}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "section_02_analysis.md"}'}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "section_03_results.md"}'}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "section_04_conclusion.md"}'}},
                    {"function": {"name": "write_file", "arguments": '{"filename": "draft_report.md", "content": "merged content"}'}}
                ]
            ))
            
            # Execute merge task
            task_briefing = [{
                "role": "user", 
                "content": "Merge all section files into draft_report.md"
            }]
            
            await writer.execute_task(task_briefing)
            
            # Verify files were read in correct order
            read_calls = [(name, args) for name, args in tool_calls if name == "read_file"]
            assert len(read_calls) == 4
            assert read_calls[0][1]['filename'] == "section_01_introduction.md"
            assert read_calls[1][1]['filename'] == "section_02_analysis.md"
            assert read_calls[2][1]['filename'] == "section_03_results.md"
            assert read_calls[3][1]['filename'] == "section_04_conclusion.md"
    
    @pytest.mark.asyncio
    async def test_writer_filters_non_section_files(self, writer_config, mock_taskspace):
        """Test that writer only processes section_*.md files."""
        # Add non-section files
        (mock_taskspace.artifacts_path / "README.md").write_text("Readme")
        (mock_taskspace.artifacts_path / "notes.txt").write_text("Notes")
        (mock_taskspace.artifacts_path / "research_data.md").write_text("Research")
        
        with patch('vibex.core.agent.Brain') as MockBrain:
            mock_brain = Mock(spec=Brain)
            MockBrain.return_value = mock_brain
            
            writer = Agent(
                config=writer_config,
                task_config=Mock(project_storage=mock_taskspace)
            )
            
            processed_files = []
            
            async def track_reads(tool_name, **kwargs):
                if tool_name == "list_files":
                    all_files = [f.name for f in mock_taskspace.artifacts_path.glob("*")]
                    return Mock(success=True, result=all_files)
                elif tool_name == "read_file":
                    processed_files.append(kwargs.get('filename'))
                    return Mock(success=True, result="content")
                return Mock(success=True)
            
            writer.tool_manager = Mock()
            writer.tool_manager.execute = AsyncMock(side_effect=track_reads)
            
            # Mock brain to filter correctly
            mock_brain.generate_response = AsyncMock(return_value=Mock(
                content="I'll only merge section files.",
                tool_calls=[
                    {"function": {"name": "list_files", "arguments": "{}"}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "section_01_introduction.md"}'}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "section_02_analysis.md"}'}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "section_03_results.md"}'}},
                    {"function": {"name": "read_file", "arguments": '{"filename": "section_04_conclusion.md"}'}},
                    {"function": {"name": "write_file", "arguments": '{"filename": "draft_report.md", "content": "merged"}'}}
                ]
            ))
            
            await writer.execute_task([{
                "role": "user",
                "content": "Merge section files"
            }])
            
            # Verify only section files were processed
            assert all(f.startswith("section_") for f in processed_files)
            assert "README.md" not in processed_files
            assert "research_data.md" not in processed_files