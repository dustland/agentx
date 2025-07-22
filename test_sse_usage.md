# SSE Console Viewer Usage

## Basic Usage

1. **Stream an existing task:**
   ```bash
   python test_sse_console.py O93I1laN --user-id your-user-id
   ```

2. **Send a message and stream the response:**
   ```bash
   python test_sse_console.py O93I1laN --user-id your-user-id --send "Tell me about San Francisco"
   ```

3. **Create a new task and stream it:**
   First create a task:
   ```bash
   curl -X POST http://localhost:7770/tasks \
     -H "Content-Type: application/json" \
     -H "X-User-ID: test-console" \
     -d '{
       "task_description": "Chat with me",
       "config_path": "examples/simple_chat/config/team.yaml"
     }'
   ```
   
   Then use the returned task_id:
   ```bash
   python test_sse_console.py <TASK_ID> --user-id test-console --send "Hello!"
   ```

## What You'll See

The console will display:
- 🔌 Connection status
- 📝 Streaming chunks in real-time (in yellow)
- ✓ Completion status with stats
- 💬 Complete messages
- 🤖 Agent messages
- 📊 Task status updates
- 🔧 Tool calls

## Example Output

```
🚀 AgentX Console SSE Viewer
Task ID: O93I1laN
User ID: test-user

📤 Sending message: Tell me about San Francisco
✅ Message sent successfully!

🔌 Connecting to SSE stream...
✅ Connected to SSE stream!

📝 New streaming message (ID: m0KMptSq):
San Francisco is a vibrant city known for its iconic Golden Gate Bridge, 
steep rolling hills, and eclectic mix of architecture...
✓ Streaming complete!
Total: 523 chars in 87 chunks
```

## Tips

- The script shows streaming chunks in yellow as they arrive
- Use Ctrl+C to stop streaming
- Add `--url` to connect to a different server
- The accumulated text and chunk count help verify streaming performance