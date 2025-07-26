# Chat History

*Module: [`vibex.storage.chat_history`](https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py)*

Chat History Storage

Handles persistence of chat conversations with support for streaming messages.
Key features:
- Persist complete messages only (not streaming chunks)
- Handle streaming completion with final message consolidation
- Efficient storage with message deduplication
- Support for both in-memory and file-based storage

## ChatHistoryStorage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L24" class="source-link" title="View source code">source</a>

Manages chat history persistence for tasks.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L27" class="source-link" title="View source code">source</a>

```python
def __init__(self, project_path: str)
```
### save_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L34" class="source-link" title="View source code">source</a>

```python
async def save_message(self, project_id: str, message: Message) -> None
```

Save a complete message to persistent storage.

### save_step <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L59" class="source-link" title="View source code">source</a>

```python
async def save_step(self, project_id: str, step: TaskStep) -> None
```

Save a task step as an assistant message to maintain unified chat history.

### handle_streaming_chunk <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L86" class="source-link" title="View source code">source</a>

```python
async def handle_streaming_chunk(self, project_id: str, chunk: StreamChunk) -> None
```

Handle streaming message chunks - accumulate but don't persist until complete.

### load_history <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L134" class="source-link" title="View source code">source</a>

```python
async def load_history(self, project_id: str) -> ConversationHistory
```

Load chat history from persistent storage.

### clear_history <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L181" class="source-link" title="View source code">source</a>

```python
async def clear_history(self, project_id: str) -> None
```

Clear chat history for a task by removing the entire history file.

### get_active_streaming_messages <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L199" class="source-link" title="View source code">source</a>

```python
def get_active_streaming_messages(self, project_id: str) -> List[Dict]
```

Get currently active streaming messages for a task.

## ChatHistoryManager <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L214" class="source-link" title="View source code">source</a>

Global manager for chat history storage across all tasks.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L217" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### get_storage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L220" class="source-link" title="View source code">source</a>

```python
def get_storage(self, project_path: str) -> ChatHistoryStorage
```

Get or create a chat history storage instance for a project.

### save_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L226" class="source-link" title="View source code">source</a>

```python
async def save_message(self, project_id: str, project_path: str, message: Message) -> None
```

Save a message using the appropriate storage instance.

### save_step <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L231" class="source-link" title="View source code">source</a>

```python
async def save_step(self, project_id: str, project_path: str, step: TaskStep) -> None
```

Save a task step using the appropriate storage instance.

### load_history <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/chat_history.py#L236" class="source-link" title="View source code">source</a>

```python
async def load_history(self, project_id: str, project_path: str) -> ConversationHistory
```

Load history using the appropriate storage instance.
