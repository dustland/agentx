"""
Summarization Tools - Combine multiple content files into structured summaries
"""

import asyncio
import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from ..core.tool import Tool, tool, ToolResult
from ..core.brain import Brain
from ..core.config import BrainConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SummarizeTool(Tool):
    """
    Tool for creating structured summaries from multiple content files.
    Designed for research workflows where multiple extracted files need to be
    synthesized into a single comprehensive report.
    """

    def __init__(self, workspace_storage: Optional[Any] = None):
        super().__init__("summarize")
        self.workspace = workspace_storage
        self.brain: Optional[Brain] = None  # Will be initialized when needed

    @tool(description="Create a comprehensive summary report from multiple content files")
    async def create_research_summary(
        self,
        input_files: List[str],
        output_filename: str,
        summary_prompt: str,
        max_content_per_file: int = 10000
    ) -> ToolResult:
        """
        Create a comprehensive summary from multiple research files.
        
        Args:
            input_files: List of filenames to read and summarize
            output_filename: Name for the output summary file
            summary_prompt: Instructions for how to structure the summary
            max_content_per_file: Maximum characters to read from each file
            
        Returns:
            ToolResult with summary creation status
        """
        try:
            if not self.workspace:
                return ToolResult(
                    success=False,
                    error="No workspace available for file operations"
                )

            # Read all input files
            file_contents = []
            total_chars = 0
            
            for filename in input_files:
                try:
                    content = await self.workspace.get_artifact(filename)
                    if content:
                        # Truncate if needed
                        if len(content) > max_content_per_file:
                            content = content[:max_content_per_file] + f"\n\n[Content truncated at {max_content_per_file} characters]"
                        
                        file_contents.append({
                            "filename": filename,
                            "content": content,
                            "size": len(content)
                        })
                        total_chars += len(content)
                        logger.info(f"Read {filename}: {len(content)} characters")
                    else:
                        logger.warning(f"File not found: {filename}")
                except Exception as e:
                    logger.error(f"Failed to read {filename}: {e}")
                    continue

            if not file_contents:
                return ToolResult(
                    success=False,
                    error="No files could be read successfully"
                )

            # Create the summary content using AI
            summary_content = await self._create_ai_summary(
                file_contents, summary_prompt, total_chars
            )

            # Save the summary
            result = await self.workspace.store_artifact(
                name=output_filename,
                content=summary_content,
                content_type="text/markdown",
                metadata={
                    "tool": "summarize",
                    "source_files": input_files,
                    "total_source_chars": total_chars,
                    "summary_chars": len(summary_content)
                },
                commit_message=f"Created research summary from {len(file_contents)} files"
            )

            if result.success:
                return ToolResult(
                    success=True,
                    result=f"✅ Research summary created: {output_filename}",
                    metadata={
                        "output_file": output_filename,
                        "source_files_processed": len(file_contents),
                        "total_source_chars": total_chars,
                        "summary_chars": len(summary_content),
                        "compression_ratio": f"{len(summary_content)/total_chars:.2%}"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Failed to save summary: {result.error}"
                )

        except Exception as e:
            logger.error(f"Error creating research summary: {e}")
            return ToolResult(
                success=False,
                error=f"Summary creation failed: {str(e)}"
            )

    async def _create_ai_summary(
        self, 
        file_contents: List[Dict[str, Any]], 
        summary_prompt: str,
        total_chars: int
    ) -> str:
        """Create an AI-powered structured summary from the file contents."""
        
        try:
            # Initialize brain if needed
            if not self.brain:
                brain_config = BrainConfig(
                    provider="deepseek",
                    model="deepseek-chat", 
                    temperature=0.3,
                    max_tokens=4000
                )
                self.brain = Brain(brain_config)
            
            # Prepare content for AI analysis
            content_for_ai = self._prepare_content_for_ai(file_contents, summary_prompt)
            
            # Use AI to create comprehensive summary
            ai_prompt = f"""You are an expert research analyst tasked with creating a comprehensive summary from multiple source documents.

TASK: {summary_prompt}

SOURCE MATERIALS:
{content_for_ai}

Please create a well-structured, comprehensive research summary that:
1. Synthesizes information from all sources
2. Identifies key themes and patterns
3. Extracts important statistics and data points
4. Highlights expert insights and quotes
5. Provides actionable recommendations
6. Maintains academic rigor and accuracy

Format as professional markdown with clear sections and subsections. This summary will be used by a writer to create the final comprehensive report."""

            # Use the simple think interface for clean AI interaction
            response = await self.brain.think(ai_prompt, temperature=0.3)
            
            # Add metadata header
            summary = f"""# Research Summary Report

**Generated:** {datetime.datetime.now().isoformat()}
**Source Files:** {len(file_contents)}
**Total Content:** {total_chars:,} characters
**Summary Method:** AI-powered analysis

{response}

---

## Source Files Reference
"""
            
            # Add source file references
            for i, file_info in enumerate(file_contents, 1):
                filename = file_info["filename"]
                size = file_info["size"]
                summary += f"- **{i}. {filename}** ({size:,} characters)\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"AI summarization failed: {e}")
            # Fallback to basic summary
            return self._create_basic_summary(file_contents, summary_prompt, total_chars)

    def _prepare_content_for_ai(self, file_contents: List[Dict[str, Any]], summary_prompt: str) -> str:
        """Prepare content for AI analysis, managing context limits."""
        
        # Calculate available space for content (leave room for prompt overhead)
        max_total_chars = 80000  # Conservative limit for most models
        prompt_overhead = 2000
        available_chars = max_total_chars - prompt_overhead
        
        content_sections = []
        used_chars = 0
        
        for i, file_info in enumerate(file_contents, 1):
            filename = file_info["filename"]
            content = file_info["content"]
            
            # Calculate how much content we can include from this file
            remaining_chars = available_chars - used_chars
            if remaining_chars <= 0:
                break
                
            # Truncate content if needed, but try to keep meaningful chunks
            if len(content) > remaining_chars:
                # Try to break at paragraph boundaries
                truncated = content[:remaining_chars]
                last_paragraph = truncated.rfind('\n\n')
                if last_paragraph > remaining_chars * 0.7:  # At least 70% of content
                    truncated = truncated[:last_paragraph]
                content = truncated + "\n\n[CONTENT TRUNCATED]"
            
            section = f"""
## Source {i}: {filename}

{content}

---
"""
            content_sections.append(section)
            used_chars += len(section)
            
            if used_chars >= available_chars:
                break
        
        return '\n'.join(content_sections)

    def _create_basic_summary(
        self, 
        file_contents: List[Dict[str, Any]], 
        summary_prompt: str,
        total_chars: int
    ) -> str:
        """Create a basic structured summary when AI is not available."""
        
        summary = f"""# Research Summary Report

**Generated:** {datetime.datetime.now().isoformat()}
**Source Files:** {len(file_contents)}
**Total Content:** {total_chars:,} characters
**Summary Method:** Basic extraction

## Task Requirements
{summary_prompt}

## Source Materials Summary

"""
        
        for i, file_info in enumerate(file_contents, 1):
            filename = file_info["filename"]
            content = file_info["content"]
            size = file_info["size"]
            
            # Include first portion of each file
            preview = content[:1000] + "..." if len(content) > 1000 else content
            
            summary += f"""### {i}. {filename}
**Size:** {size:,} characters

**Content Preview:**
{preview}

---

"""
        
        summary += f"""
## Next Steps for Writer

The writer should analyze the {len(file_contents)} source files above to create a comprehensive report addressing: {summary_prompt}

All source files contain the full extracted content and should be thoroughly analyzed to create the final deliverable.

## Source Files Available
"""
        
        for i, file_info in enumerate(file_contents, 1):
            filename = file_info["filename"]
            size = file_info["size"]
            summary += f"- **{filename}** ({size:,} characters)\n"
        
        return summary


# Export
__all__ = ["SummarizeTool"]