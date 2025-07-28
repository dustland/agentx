# Message Parts Architecture Analysis

## Current State

Our framework has several layers that need to support message parts:

1. **Brain (LLM Gateway)**
   - Streams: `text-delta`, `tool-call`, `finish`, `error`
   - Does NOT maintain message structure with parts

2. **Agent (Tool Executor)**
   - Processes Brain's stream
   - Executes tools
   - Returns chunks but loses part structure

3. **XAgent (Orchestrator)**
   - Collects parts during streaming
   - Creates Message with parts at the end
   - Does NOT stream parts to frontend in real-time

4. **Frontend**
   - Receives fragmented events
   - Tries to reconstruct message structure
   - Missing proper part-based updates

## Vercel AI SDK Approach

```typescript
// Message with parts
{
  id: "msg_123",
  role: "assistant",
  content: "Here's the weather...", // Full text for backward compat
  parts: [
    { type: "text", text: "Let me check the weather for you.\n" },
    { type: "tool-call", toolCallId: "call_456", toolName: "getWeather", args: {...} },
    { type: "tool-result", toolCallId: "call_456", result: {...} },
    { type: "text", text: "The weather in Tokyo is 72°F and sunny." }
  ]
}
```

## Required Changes

### 1. Enhanced Streaming Protocol

```python
# New streaming events
- message_start: { messageId, role }
- part_start: { messageId, partIndex, type }
- part_delta: { messageId, partIndex, delta }
- part_complete: { messageId, partIndex, part }
- message_complete: { message }
```

### 2. Message Builder Pattern

```python
class StreamingMessageBuilder:
    """Builds a Message with parts during streaming."""
    
    def __init__(self, message_id: str, role: str):
        self.message_id = message_id
        self.role = role
        self.parts: List[MessagePart] = []
        self.current_text = ""
        self.current_part_index = -1
    
    def add_text_delta(self, text: str):
        """Add text to current text part."""
        self.current_text += text
    
    def finalize_text_part(self):
        """Convert accumulated text to TextPart."""
        if self.current_text:
            self.parts.append(TextPart(text=self.current_text))
            self.current_text = ""
            self.current_part_index += 1
    
    def add_tool_call(self, tool_call: ToolCallPart):
        """Add a tool call part."""
        self.finalize_text_part()  # Finish any pending text
        self.parts.append(tool_call)
        self.current_part_index += 1
    
    def add_tool_result(self, tool_result: ToolResultPart):
        """Add a tool result part."""
        self.parts.append(tool_result)
        self.current_part_index += 1
    
    def build(self) -> Message:
        """Build the final message."""
        self.finalize_text_part()  # Finish any pending text
        
        # Combine all text for content field (backward compat)
        content = ""
        for part in self.parts:
            if isinstance(part, TextPart):
                content += part.text
            elif isinstance(part, ToolResultPart):
                content += f"\n\nTool result: {part.result}\n"
        
        return Message(
            id=self.message_id,
            role=self.role,
            content=content.strip(),
            parts=self.parts
        )
```

### 3. Frontend State Management

```typescript
interface StreamingMessage {
  id: string;
  role: string;
  parts: MessagePart[];
  status: 'streaming' | 'complete';
  currentPartIndex?: number;
}

// Handle streaming events
case "part_start":
  // Initialize new part
  message.parts[data.partIndex] = { type: data.type, ...data.initialData };
  break;

case "part_delta":
  // Update existing part
  const part = message.parts[data.partIndex];
  if (part.type === 'text') {
    part.text += data.delta;
  } else if (part.type === 'tool-call' && data.argsDelta) {
    part.args = JSON.parse(part.argsText + data.argsDelta);
  }
  break;

case "part_complete":
  // Finalize part
  message.parts[data.partIndex] = data.part;
  break;
```

## Implementation Plan

1. **Phase 1: Message Builder**
   - Create StreamingMessageBuilder class
   - Use in XAgent._stream_full_response
   - Emit proper part events

2. **Phase 2: Streaming Protocol**
   - Add new SSE event types
   - Send part_start/delta/complete events
   - Maintain message structure

3. **Phase 3: Frontend Integration**
   - Update useXAgent to handle part events
   - Maintain streaming message state
   - Render parts progressively

4. **Phase 4: Testing**
   - Test text + tool call sequences
   - Test multi-step tool calls
   - Test error handling

## Benefits

1. **Natural Visualization**: Parts render as they stream
2. **Structured Data**: Maintain proper message structure
3. **Tool Transparency**: Show tool calls inline with text
4. **Progressive Rendering**: Update UI smoothly
5. **Backward Compatible**: Still works with content field