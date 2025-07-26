# Memory Synthesis Engine

*Module: [`vibex.memory.synthesis_engine`](https://github.com/dustland/vibex/blob/main/src/vibex/memory/synthesis_engine.py)*

Memory Synthesis Engine

The intelligent core of the Memory System that analyzes events and creates
structured memories (Constraints, Hot Issues, Document Chunks) as specified
in the architecture document.

## MemorySynthesisEngine <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/synthesis_engine.py#L30" class="source-link" title="View source code">source</a>

The logical core of the Memory System that analyzes events and creates memories.

Implements the event-driven analysis logic specified in the architecture:
- Analyzes user messages for constraints/preferences
- Detects tool failures and creates hot issues
- Resolves hot issues when tools succeed
- Chunks document content for semantic search

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/synthesis_engine.py#L41" class="source-link" title="View source code">source</a>

```python
def __init__(self, memory_backend: MemoryBackend, brain: Optional['Brain'] = None)
```
### on_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/synthesis_engine.py#L62" class="source-link" title="View source code">source</a>

```python
async def on_event(self, event: Event) -> None
```

Main event handler - routes events to appropriate analysis methods.

This implements the event handling logic from the architecture document.

### get_relevant_context <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/synthesis_engine.py#L386" class="source-link" title="View source code">source</a>

```python
async def get_relevant_context(self, last_user_message: str, agent_name: str = None) -> str
```

Get relevant context for injection into agent prompts.

This implements the context retrieval logic from the architecture document.
