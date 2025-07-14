"""
Document Tools - Comprehensive document processing, refinement, and summarization.

This tool provides various document operations including polishing, merging,
summarization, and other document transformations using configurable AI models.
"""

from ..utils.logger import get_logger
from ..core.tool import Tool, tool, ToolResult
from ..core.brain import Brain
from ..core.config import BrainConfig
from typing import Optional, Any, List, Dict, Union
import time
from pathlib import Path
import datetime

logger = get_logger(__name__)


class DocumentTool(Tool):
    """
    Document processing tool for advanced document operations.
    
    Capabilities include:
    - Document polishing with configurable AI models
    - Section merging
    - Multi-file summarization
    - Format conversion
    - Document analysis
    """
    
    def __init__(
        self, 
        taskspace_storage: Optional[Any] = None, 
        polish_model: Optional[str] = None,
        summary_model: Optional[str] = None
    ) -> None:
        super().__init__("document")
        self.taskspace = taskspace_storage
        # Default models for different operations
        self.polish_model = polish_model or "deepseek/deepseek-reasoner"
        self.summary_model = summary_model or "deepseek/deepseek-chat"
        
    @tool(  # type: ignore[misc]
        description="Polish a draft document using advanced AI reasoning for professional refinement",
        return_description="ToolResult indicating success and location of polished document"
    )
    async def polish_document(
        self,
        draft_path: str,
        output_path: Optional[str] = None,
        polish_instructions: Optional[str] = None,
        model_override: Optional[str] = None
    ) -> "ToolResult":
        """
        Polish a draft document to create a cohesive, professional final version.
        
        Args:
            draft_path: Path to the draft document to polish
            output_path: Optional path for the polished document (defaults to polished_[original_name])
            polish_instructions: Optional specific instructions for polishing
            model_override: Optional model to use instead of default polish_model
            
        Returns:
            ToolResult with success status and output file location
        """
        start_time = time.time()
        polish_model = model_override or self.polish_model
        
        try:
            # Read the draft document
            logger.info(f"Reading draft document: {draft_path}")
            
            if self.taskspace:
                # Try taskspace first
                try:
                    draft_content = await self.taskspace.get_artifact(draft_path)
                    if draft_content is None:
                        raise FileNotFoundError(f"File not found in taskspace: {draft_path}")
                except:
                    # Fall back to file system
                    draft_path_obj = Path(draft_path)
                    if not draft_path_obj.exists():
                        return ToolResult.error_result(
                            error=f"Draft file not found: {draft_path}",
                            execution_time=time.time() - start_time
                        )
                    draft_content = draft_path_obj.read_text()
            else:
                # Direct file system access
                draft_path_obj = Path(draft_path)
                if not draft_path_obj.exists():
                    return ToolResult.error_result(
                        error=f"Draft file not found: {draft_path}",
                        execution_time=time.time() - start_time
                    )
                draft_content = draft_path_obj.read_text()
            
            # Check draft size and implement chunking for large documents
            draft_size = len(draft_content)
            logger.info(f"Draft document size: {draft_size} characters")
            
            # If document is too large, process in chunks to avoid timeouts
            max_chunk_size = 50000  # ~12k tokens, safe for most models
            should_chunk = draft_size > max_chunk_size
            
            if should_chunk:
                logger.info(f"Document size ({draft_size}) exceeds chunk limit ({max_chunk_size}), will process in chunks")
            
            # Create reasoning brain for polishing
            logger.info(f"Initializing {polish_model} for document polishing")
            
            # Parse model string to get provider and model
            if "/" in polish_model:
                provider, model = polish_model.split("/", 1)
            else:
                provider = "deepseek"
                model = polish_model
            
            # Configure brain based on model type
            supports_functions = "reasoner" not in model.lower()
            
            reasoning_brain = Brain(BrainConfig(
                provider=provider,
                model=polish_model,
                supports_function_calls=supports_functions,
                temperature=0.3,  # Lower temperature for consistent polishing
                max_tokens=8000,  # Max tokens supported by DeepSeek
                timeout=300  # 5 minutes timeout for large documents with reasoner
            ))
            
            # Build polishing prompt
            base_instructions = """You are a professional editor tasked with polishing this draft document.

Your goals:
1. **Remove Redundancies**: Eliminate repeated information and redundant phrases
2. **Smooth Transitions**: Add connecting sentences between sections for better flow
3. **Unify Tone**: Ensure consistent professional tone throughout
4. **Enhance Clarity**: Improve sentence structure and word choice
5. **Maintain Accuracy**: Keep all factual content, data, and key information intact
6. **Improve Structure**: Reorganize content if needed for better logical flow

Important constraints:
- Preserve all technical details and specific data
- Maintain the document's core message and intent
- Keep approximately the same length (can be slightly longer for clarity)
- Ensure the final document reads as if written by a single author

Output the polished document directly without any meta-commentary."""
            
            if polish_instructions:
                prompt = f"{base_instructions}\n\nAdditional instructions: {polish_instructions}\n\nDRAFT DOCUMENT:\n\n{draft_content}"
            else:
                prompt = f"{base_instructions}\n\nDRAFT DOCUMENT:\n\n{draft_content}"
            
            # Use AI model for polishing
            logger.info(f"Starting document polish with {polish_model}...")
            
            if should_chunk:
                # Process large documents in chunks to avoid timeouts
                polished_content = await self._polish_in_chunks(
                    draft_content, base_instructions, polish_instructions, 
                    reasoning_brain, supports_functions, max_chunk_size
                )
            else:
                # Process smaller documents normally
                if supports_functions:
                    # For models with function calling, use generate_response
                    response = await reasoning_brain.generate_response(
                        messages=[{"role": "user", "content": prompt}]
                    )
                    polished_content = response.content
                else:
                    # For pure reasoning models, use think
                    polished_content = await reasoning_brain.think(prompt)
            
            if not polished_content or len(polished_content.strip()) < 100:
                raise ValueError("Polishing produced insufficient content")
            
            # Determine output path
            if not output_path:
                if draft_path.endswith('.md'):
                    output_path = draft_path.replace('.md', '_polished.md')
                else:
                    output_path = f"polished_{Path(draft_path).name}"
            
            # Save polished document
            logger.info(f"Saving polished document to: {output_path}")
            
            if self.taskspace:
                save_result = await self.taskspace.store_artifact(
                    name=output_path,
                    content=polished_content,
                    content_type="text/markdown",
                    metadata={
                        "tool": "polish_document",
                        "original_file": draft_path,
                        "polish_model": polish_model
                    },
                    commit_message=f"Polished document: {draft_path}"
                )
                
                if not save_result.success:
                    raise Exception(f"Failed to save polished document: {save_result.error}")
            else:
                # Direct file system save
                Path(output_path).write_text(polished_content)
            
            # Calculate improvements
            execution_time = time.time() - start_time
            original_lines = draft_content.count('\n')
            polished_lines = polished_content.count('\n')
            
            logger.info(f"Polish complete in {execution_time:.2f}s")
            
            return ToolResult.success_result(
                result={
                    "output_path": output_path,
                    "original_size": draft_size,
                    "polished_size": len(polished_content),
                    "size_change": len(polished_content) - draft_size,
                    "line_count_change": polished_lines - original_lines
                },
                execution_time=execution_time,
                metadata={
                    "model": polish_model,
                    "draft_path": draft_path,
                    "output_path": output_path,
                    "message": f"Successfully polished document and saved to {output_path}"
                }
            )
            
        except Exception as e:
            logger.error(f"Document polishing failed: {e}")
            return ToolResult.error_result(
                error=str(e),
                execution_time=time.time() - start_time,
                metadata={"draft_path": draft_path}
            )

    @tool(
        description="Merge multiple document sections into a cohesive document",
        return_description="ToolResult with merged document location"
    )
    async def merge_sections(
        self,
        section_pattern: str = "section_*.md",
        output_path: str = "merged_document.md",
        add_transitions: bool = True
    ) -> "ToolResult":
        """
        Merge multiple section files into a single document.
        
        Args:
            section_pattern: Glob pattern to find section files
            output_path: Path for the merged document
            add_transitions: Whether to add transition sentences between sections
            
        Returns:
            ToolResult with merged document information
        """
        start_time = time.time()
        
        try:
            # Find section files
            if self.taskspace:
                files = await self.taskspace.list_artifacts()
                # files is a list of dicts with 'name' key
                section_files = sorted([f['name'] for f in files if Path(f['name']).match(section_pattern)])
            else:
                from glob import glob
                section_files = sorted(glob(section_pattern))
            
            if not section_files:
                return ToolResult.error_result(
                    error=f"No files found matching pattern: {section_pattern}",
                    execution_time=time.time() - start_time
                )
            
            logger.info(f"Found {len(section_files)} section files to merge")
            
            # Read and merge sections
            merged_content = []
            for i, section_file in enumerate(section_files):
                if self.taskspace:
                    content = await self.taskspace.get_artifact(section_file)
                else:
                    content = Path(section_file).read_text()
                
                merged_content.append(content.strip())
                
                # Add transition if requested and not last section
                if add_transitions and i < len(section_files) - 1:
                    merged_content.append("\n\n---\n\n")  # Simple transition marker
            
            final_content = "\n\n".join(merged_content)
            
            # Save merged document
            if self.taskspace:
                await self.taskspace.store_artifact(
                    name=output_path,
                    content=final_content,
                    content_type="text/markdown",
                    metadata={
                        "tool": "merge_sections",
                        "source_files": section_files,
                        "section_count": len(section_files)
                    },
                    commit_message=f"Merged {len(section_files)} sections into {output_path}"
                )
            else:
                Path(output_path).write_text(final_content)
            
            return ToolResult.success_result(
                result={
                    "output_path": output_path,
                    "sections_merged": len(section_files),
                    "total_size": len(final_content),
                    "section_files": section_files
                },
                execution_time=time.time() - start_time,
                metadata={
                    "message": f"Successfully merged {len(section_files)} sections into {output_path}"
                }
            )
            
        except Exception as e:
            logger.error(f"Section merge failed: {e}")
            return ToolResult.error_result(
                error=str(e),
                execution_time=time.time() - start_time
            )

    @tool(
        description="Summarize multiple documents into a comprehensive report",
        return_description="ToolResult with summary creation status"
    )
    async def summarize_documents(
        self,
        input_files: List[str],
        output_filename: str,
        summary_prompt: str,
        max_content_per_file: int = 10000,
        model_override: Optional[str] = None
    ) -> "ToolResult":
        """
        Create a comprehensive summary from multiple research files.
        
        Args:
            input_files: List of filenames to read and summarize
            output_filename: Name for the output summary file
            summary_prompt: Instructions for how to structure the summary
            max_content_per_file: Maximum characters to read from each file
            model_override: Optional model to use instead of default summary_model
            
        Returns:
            ToolResult with summary creation status
        """
        start_time = time.time()
        summary_model = model_override or self.summary_model
        
        try:
            if not self.taskspace:
                return ToolResult.error_result(
                    error="No taskspace available for file operations",
                    execution_time=time.time() - start_time
                )

            # Read all input files
            file_contents = []
            total_chars = 0
            
            for filename in input_files:
                try:
                    content = await self.taskspace.get_artifact(filename)
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
                return ToolResult.error_result(
                    error="No files could be read successfully",
                    execution_time=time.time() - start_time
                )

            # Create the summary using AI
            logger.info(f"Creating summary with {summary_model}")
            
            # Parse model string
            if "/" in summary_model:
                provider, model = summary_model.split("/", 1)
            else:
                provider = "deepseek"
                model = summary_model
            
            brain = Brain(BrainConfig(
                provider=provider,
                model=summary_model,
                supports_function_calls=True,
                temperature=0.3,
                max_tokens=8000,
                timeout=120  # 2 minutes timeout for summaries
            ))
            
            # Build the summary prompt
            prompt = f"""You are creating a comprehensive research summary from multiple source files.

SUMMARY INSTRUCTIONS:
{summary_prompt}

SOURCE FILES ({len(file_contents)} files, {total_chars} total characters):

"""
            
            for fc in file_contents:
                prompt += f"\n=== {fc['filename']} ({fc['size']} chars) ===\n{fc['content']}\n"
            
            prompt += "\n\nCreate a well-structured, comprehensive summary based on the above content and instructions."
            
            # Generate summary
            response = await brain.generate_response(
                messages=[{"role": "user", "content": prompt}]
            )
            
            summary_content = response.content
            
            # Add metadata header
            header = f"""# Research Summary

**Generated**: {datetime.datetime.now().isoformat()}
**Source Files**: {len(file_contents)}
**Total Content**: {total_chars} characters
**Summary Model**: {summary_model}

---

"""
            
            final_content = header + (summary_content or "")

            # Save the summary
            result = await self.taskspace.store_artifact(
                name=output_filename,
                content=final_content,
                content_type="text/markdown",
                metadata={
                    "tool": "summarize_documents",
                    "source_files": input_files,
                    "total_source_chars": total_chars,
                    "summary_model": summary_model,
                    "files_processed": len(file_contents)
                },
                commit_message=f"Created research summary from {len(file_contents)} files"
            )

            if result.success:
                logger.info(f"Summary created successfully: {output_filename}")
                return ToolResult.success_result(
                    result={
                        "output_file": output_filename,
                        "files_processed": len(file_contents),
                        "total_chars_processed": total_chars,
                        "summary_length": len(final_content)
                    },
                    execution_time=time.time() - start_time,
                    metadata={
                        "message": f"Created summary from {len(file_contents)} files"
                    }
                )
            else:
                raise Exception(f"Failed to save summary: {result.error}")

        except Exception as e:
            logger.error(f"Summary creation failed: {e}")
            return ToolResult.error_result(
                error=str(e),
                execution_time=time.time() - start_time
            )

    async def _polish_in_chunks(
        self,
        content: str,
        base_instructions: str,
        polish_instructions: Optional[str],
        brain: "Brain",
        supports_functions: bool,
        max_chunk_size: int
    ) -> str:
        """Polish large documents in chunks to avoid timeouts."""
        logger.info("Processing large document in chunks to avoid timeouts")
        
        # Split content into sections based on headers and paragraphs
        chunks = self._smart_chunk_content(content, max_chunk_size)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        polished_chunks = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Polishing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            
            # Create chunk-specific prompt
            chunk_instructions = f"{base_instructions}\n\nThis is part {i+1} of {len(chunks)} of a larger document. Polish this section while maintaining consistency with the overall document style."
            
            if polish_instructions:
                chunk_prompt = f"{chunk_instructions}\n\nAdditional instructions: {polish_instructions}\n\nCONTENT SECTION:\n\n{chunk}"
            else:
                chunk_prompt = f"{chunk_instructions}\n\nCONTENT SECTION:\n\n{chunk}"
            
            try:
                if supports_functions:
                    response = await brain.generate_response(
                        messages=[{"role": "user", "content": chunk_prompt}]
                    )
                    polished_chunk = response.content
                else:
                    polished_chunk = await brain.think(chunk_prompt)
                
                polished_chunks.append(polished_chunk)
                
            except Exception as e:
                logger.warning(f"Failed to polish chunk {i+1}: {e}, keeping original")
                polished_chunks.append(chunk)
        
        # Combine polished chunks
        result = "\n\n".join(polished_chunks)
        logger.info(f"Combined {len(polished_chunks)} polished chunks into final document")
        
        return result

    def _smart_chunk_content(self, content: str, max_size: int) -> list[str]:
        """Split content into chunks at section boundaries only."""
        if len(content) <= max_size:
            return [content]
        
        import re
        
        chunks = []
        
        # Split by ALL markdown headers (H1-H6)
        # This ensures we chunk at any logical section boundary
        header_pattern = r'^(#{1,6})\s+(.+)$'
        
        sections = []
        current_section = []
        current_header = None
        
        lines = content.split('\n')
        
        for line in lines:
            header_match = re.match(header_pattern, line, re.MULTILINE)
            
            if header_match:
                # Save previous section if exists
                if current_section:
                    section_content = '\n'.join(current_section)
                    sections.append({
                        'header': current_header,
                        'content': section_content,
                        'size': len(section_content)
                    })
                
                # Start new section
                current_header = line
                current_section = [line]
            else:
                current_section.append(line)
        
        # Don't forget the last section
        if current_section:
            section_content = '\n'.join(current_section)
            sections.append({
                'header': current_header,
                'content': section_content,
                'size': len(section_content)
            })
        
        # If no sections found, treat the whole document as one section
        if not sections:
            logger.warning("No section headers found in document, treating as single chunk")
            return [content]
        
        # Group sections into chunks that respect size limits
        current_chunk_sections = []
        current_chunk_size = 0
        
        for section in sections:
            section_size = section['size']
            
            # If this single section is too large, it must be its own chunk
            # We do NOT split sections further
            if section_size > max_size:
                logger.warning(f"Section '{section['header']}' ({section_size} chars) exceeds max size ({max_size}), keeping as single chunk")
                
                # First, save any accumulated sections
                if current_chunk_sections:
                    chunk_content = '\n\n'.join([s['content'] for s in current_chunk_sections])
                    chunks.append(chunk_content)
                    current_chunk_sections = []
                    current_chunk_size = 0
                
                # Add this large section as its own chunk
                chunks.append(section['content'])
                
            # If adding this section would exceed limit, start new chunk
            elif current_chunk_size + section_size + 2 > max_size:
                if current_chunk_sections:
                    chunk_content = '\n\n'.join([s['content'] for s in current_chunk_sections])
                    chunks.append(chunk_content)
                
                current_chunk_sections = [section]
                current_chunk_size = section_size
                
            # Otherwise, add section to current chunk
            else:
                current_chunk_sections.append(section)
                current_chunk_size += section_size + 2
        
        # Don't forget the last chunk
        if current_chunk_sections:
            chunk_content = '\n\n'.join([s['content'] for s in current_chunk_sections])
            chunks.append(chunk_content)
        
        logger.info(f"Split document into {len(chunks)} chunks at section boundaries only")
        return chunks


# Export
__all__ = ["DocumentTool"]