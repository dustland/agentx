# Fix for Message Parts Not Showing in Frontend

## Issue
When sending the initial goal message to XAgent, tool blocks are not displayed in the frontend even though tools are being executed. The logs show:
- `[STREAMING] Starting streaming response` followed immediately by `[STREAMING] Sent final chunk`
- Tool execution happens but no message parts are sent to frontend

## Root Cause
The initial goal message triggers plan generation which bypasses the streaming response mechanism. The flow is:
1. Message arrives with mode='agent' 
2. `_ensure_plan_initialized()` is called
3. Plan is generated without streaming
4. Empty response is returned
5. Task execution happens separately without message parts

## Solution

The XAgent needs to be modified to ensure initial messages get proper streaming responses. Here's the fix:

### Option 1: Modify Initial Message Handling (Quick Fix)
In `xagent.py`, modify the chat method to force a streaming response after plan initialization:

```python
# In the chat method, after plan initialization:
if not self.plan and self.initial_prompt:
    # Plan was just created, provide a streaming response about it
    response = await self._generate_plan_summary_response(message)
else:
    response = await self._handle_agent_message(message)
```

### Option 2: Stream Plan Generation (Better Solution)
Modify `_generate_plan` to use streaming:

```python
async def _generate_plan(self, prompt: str) -> Plan:
    """Generate a plan using streaming to show progress."""
    # Use streaming message builder
    from ..server.streaming import event_stream_manager
    
    message_id = generate_short_id()
    
    # Send message_start event
    await event_stream_manager.send_event(
        self.project_id,
        "message_start",
        {"message_id": message_id, "role": "assistant"}
    )
    
    # Stream plan generation...
```

### Option 3: Ensure Tool Calls Are Streamed (Current Implementation Issue)
The real issue might be that task execution (after plan creation) is not using the message parts streaming. When `step()` is called, it should stream the tool calls:

```python
# In _execute_single_task method
async def _execute_single_task(self, task: Task) -> str:
    # This should use _stream_full_response to ensure message parts are sent
    # Currently it might be using a different path
```

## Immediate Workaround
To see message parts working:
1. Send a follow-up message after the initial goal
2. This will trigger `_handle_agent_message` which properly uses `_stream_full_response`
3. Tool calls in the response will show as message parts

## Test Steps
1. Start XAgent with a goal
2. After plan creation, send a message like "Please proceed with the first task"
3. This should trigger proper streaming with message parts

## Long-term Fix
The XAgent architecture needs adjustment to ensure all LLM interactions (including during task execution) use the streaming message builder to send proper message parts to the frontend.