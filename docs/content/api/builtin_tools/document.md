# Document

*Module: [`vibex.builtin_tools.document`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/document.py)*

Document Tools - Comprehensive document processing, refinement, and summarization.

This tool provides various document operations including polishing, merging,
summarization, and other document transformations using configurable AI models.

## DocumentTool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/document.py#L20" class="source-link" title="View source code">source</a>

Document processing tool for advanced document operations.

Capabilities include:
- Document polishing with configurable AI models
- Section merging
- Multi-file summarization
- Format conversion
- Document analysis

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/document.py#L32" class="source-link" title="View source code">source</a>

```python
def __init__(self, project_storage: Optional[Any] = None, polish_model: Optional[str] = None, summary_model: Optional[str] = None) -> None
```
### polish_document <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/document.py#L48" class="source-link" title="View source code">source</a>

```python
async def polish_document(self, draft_path: str, output_path: Optional[str] = None, polish_instructions: Optional[str] = None, model_override: Optional[str] = None) -> 'ToolResult'
```

Polish a draft document to create a cohesive, professional final version.

**Args:**
    draft_path: Path to the draft document to polish
    output_path: Optional path for the polished document (defaults to polished_[original_name])
    polish_instructions: Optional specific instructions for polishing
    model_override: Optional model to use instead of default polish_model

**Returns:**
    ToolResult with success status and output file location

### merge_sections <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/document.py#L245" class="source-link" title="View source code">source</a>

```python
async def merge_sections(self, section_pattern: str = 'section_*.md', output_path: str = 'merged_document.md', add_transitions: bool = True) -> 'ToolResult'
```

Merge multiple section files into a single document.

**Args:**
    section_pattern: Glob pattern to find section files
    output_path: Path for the merged document
    add_transitions: Whether to add transition sentences between sections

**Returns:**
    ToolResult with merged document information

### summarize_documents <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/document.py#L338" class="source-link" title="View source code">source</a>

```python
async def summarize_documents(self, input_files: List[str], output_filename: str, summary_prompt: str, max_content_per_file: int = 10000, model_override: Optional[str] = None) -> 'ToolResult'
```

Create a comprehensive summary from multiple research files.

**Args:**
    input_files: List of filenames to read and summarize
    output_filename: Name for the output summary file
    summary_prompt: Instructions for how to structure the summary
    max_content_per_file: Maximum characters to read from each file
    model_override: Optional model to use instead of default summary_model

**Returns:**
    ToolResult with summary creation status
