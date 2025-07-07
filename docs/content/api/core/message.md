# Message Types

*Module: [`agentx.core.message`](https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py)*

## Artifact <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L20" class="source-link" title="View source code">source</a>

Artifact reference with versioning and metadata.

## TextPart <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L34" class="source-link" title="View source code">source</a>

Text content part with language and confidence support.

## ToolCallPart <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L41" class="source-link" title="View source code">source</a>

Tool call request part - conversation representation.

## ToolResultPart <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L49" class="source-link" title="View source code">source</a>

Tool execution result part.

## ArtifactPart <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L57" class="source-link" title="View source code">source</a>

Artifact reference part.

## ImagePart <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L62" class="source-link" title="View source code">source</a>

Image content part with metadata.

## AudioPart <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L70" class="source-link" title="View source code">source</a>

Audio content part with metadata.

## MemoryReference <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L79" class="source-link" title="View source code">source</a>

Memory reference with relevance scoring.

## MemoryPart <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L86" class="source-link" title="View source code">source</a>

Memory operation part.

## GuardrailCheck <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L93" class="source-link" title="View source code">source</a>

Individual guardrail check result.

## GuardrailPart <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L102" class="source-link" title="View source code">source</a>

Guardrail check results part.

## TaskStep <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L110" class="source-link" title="View source code">source</a>

A single step in a task's conversation history.

## Message <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L119" class="source-link" title="View source code">source</a>

Standard chat message format compatible with LLM APIs and Vercel AI SDK.

This follows the industry standard format with role/content/parts structure.

### user_message <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L132" class="source-link" title="View source code">source</a>

```python
def user_message(cls, content: str, parts: Optional[List[ConversationPart]] = None) -> 'Message'
```

Create a user message.

### assistant_message <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L141" class="source-link" title="View source code">source</a>

```python
def assistant_message(cls, content: str, parts: Optional[List[ConversationPart]] = None) -> 'Message'
```

Create an assistant message.

### system_message <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L150" class="source-link" title="View source code">source</a>

```python
def system_message(cls, content: str, parts: Optional[List[ConversationPart]] = None) -> 'Message'
```

Create a system message.

## UserMessage <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L158" class="source-link" title="View source code">source</a>

User message - alias for Message with role='user'.

## MessageQueue <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L162" class="source-link" title="View source code">source</a>

Queue for managing message flow in tasks.

### add <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L167" class="source-link" title="View source code">source</a>

```python
def add(self, message: Message) -> None
```

Add a message to the queue.

### get_all <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L173" class="source-link" title="View source code">source</a>

```python
def get_all(self) -> List[Message]
```

Get all messages in the queue.

### clear <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L177" class="source-link" title="View source code">source</a>

```python
def clear(self) -> None
```

Clear all messages from the queue.

## TaskHistory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L181" class="source-link" title="View source code">source</a>

Task execution history with messages and metadata.

### add_message <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L189" class="source-link" title="View source code">source</a>

```python
def add_message(self, message: Message) -> None
```

Add a message to the history.

### add_step <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L194" class="source-link" title="View source code">source</a>

```python
def add_step(self, step: TaskStep) -> None
```

Add a task step to the history.

## StreamChunk <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L201" class="source-link" title="View source code">source</a>

Token-by-token message streaming from LLM.

This is Channel 1 of the dual-channel system - provides low-latency
UI updates for "typing" effect. This is message streaming, not events.

## StreamError <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L216" class="source-link" title="View source code">source</a>

Error in message streaming.

## StreamComplete <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/message.py#L227" class="source-link" title="View source code">source</a>

Message streaming completion marker.
