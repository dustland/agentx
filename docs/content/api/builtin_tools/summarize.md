# Summarize

*Module: [`agentx.builtin_tools.summarize`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/summarize.py)*

Summarization Tools - Combine multiple content files into structured summaries

## SummarizeTool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/summarize.py#L17" class="source-link" title="View source code">source</a>

Tool for creating structured summaries from multiple content files.
Designed for research workflows where multiple extracted files need to be
synthesized into a single comprehensive report.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/summarize.py#L24" class="source-link" title="View source code">source</a>

```python
def __init__(self, workspace_storage: Optional[Any] = None)
```
### create_research_summary <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/summarize.py#L30" class="source-link" title="View source code">source</a>

```python
async def create_research_summary(self, input_files: List[str], output_filename: str, summary_prompt: str, max_content_per_file: int = 10000) -> ToolResult
```

Create a comprehensive summary from multiple research files.

**Args:**
    input_files: List of filenames to read and summarize
    output_filename: Name for the output summary file
    summary_prompt: Instructions for how to structure the summary
    max_content_per_file: Maximum characters to read from each file

**Returns:**
    ToolResult with summary creation status
