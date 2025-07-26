# Message Types

*Module: [`vibex.core.message`](https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py)*

## Artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L18" class="source-link" title="View source code">source</a>

Artifact reference with versioning and metadata.

## MessagePart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L32" class="source-link" title="View source code">source</a>

A union of all possible content types that can be part of a message.
This allows for rich, multi-modal messages (e.g., text with images).

## TextPart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L40" class="source-link" title="View source code">source</a>

Text content part with language and confidence support.

## ToolCallPart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L47" class="source-link" title="View source code">source</a>

Tool call request part - conversation representation.

## ToolResultPart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L55" class="source-link" title="View source code">source</a>

Tool execution result part.

## ArtifactPart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L63" class="source-link" title="View source code">source</a>

Artifact reference part.

## ImagePart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L68" class="source-link" title="View source code">source</a>

Image content part with metadata.

## AudioPart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L76" class="source-link" title="View source code">source</a>

Audio content part with metadata.

## MemoryReference <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L85" class="source-link" title="View source code">source</a>

Memory reference with relevance scoring.

## MemoryPart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L92" class="source-link" title="View source code">source</a>

Memory operation part.

## GuardrailCheck <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L99" class="source-link" title="View source code">source</a>

Individual guardrail check result.

## GuardrailPart <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L108" class="source-link" title="View source code">source</a>

Guardrail check results part.

## Message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L116" class="source-link" title="View source code">source</a>

Standard chat message format compatible with LLM APIs and Vercel AI SDK.

This follows the industry standard format with role/content/parts structure.

### user_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L129" class="source-link" title="View source code">source</a>

```python
def user_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> 'Message'
```

Create a user message.

### assistant_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L138" class="source-link" title="View source code">source</a>

```python
def assistant_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> 'Message'
```

Create an assistant message.

### system_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L147" class="source-link" title="View source code">source</a>

```python
def system_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> 'Message'
```

Create a system message.

## UserMessage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L155" class="source-link" title="View source code">source</a>

User message - alias for Message with role='user'.

## TaskStep <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L159" class="source-link" title="View source code">source</a>

Represents a single execution step taken by an agent within a task.

A TaskStep contains the actions performed by an agent, including tool calls,
their results, and any other content generated during task execution.

### to_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L172" class="source-link" title="View source code">source</a>

```python
def to_message(self) -> Message
```

Convert TaskStep to a Message for unified chat history.

## MessageQueue <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L186" class="source-link" title="View source code">source</a>

Queue for managing message flow in tasks.

### add <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L191" class="source-link" title="View source code">source</a>

```python
def add(self, message: Message) -> None
```

Add a message to the queue.

### get_all <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L197" class="source-link" title="View source code">source</a>

```python
def get_all(self) -> List[Message]
```

Get all messages in the queue.

### clear <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L201" class="source-link" title="View source code">source</a>

```python
def clear(self) -> None
```

Clear all messages from the queue.

## ConversationHistory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L205" class="source-link" title="View source code">source</a>

Project conversation history with messages and metadata.

### add_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L213" class="source-link" title="View source code">source</a>

```python
def add_message(self, message: Message) -> None
```

Add a message to the history.

### add_step <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L218" class="source-link" title="View source code">source</a>

```python
def add_step(self, step: TaskStep) -> None
```

Add a task step to the history.

## StreamChunk <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L225" class="source-link" title="View source code">source</a>

Token-by-token message streaming from LLM.

This is Channel 1 of the dual-channel system - provides low-latency
UI updates for "typing" effect. This is message streaming, not events.

## StreamError <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L240" class="source-link" title="View source code">source</a>

Error in message streaming.

## StreamComplete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/message.py#L251" class="source-link" title="View source code">source</a>

Message streaming completion marker.
