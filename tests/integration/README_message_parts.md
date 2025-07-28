# Message Parts Integration Tests

This directory contains integration tests for the message parts feature in VibeX.

## Overview

The message parts system allows agents to send structured messages with different types of content:
- Text content
- Tool calls and results
- Images and files
- Reasoning/thinking steps
- Error information
- Step boundaries

## Test Files

### `test_message_parts_simple.py`
Simple integration tests that verify the SSE streaming protocol without requiring a full XAgent setup:
- Tests streaming message construction
- Verifies SSE event format and ordering
- Tests error handling
- Validates field naming conventions (camelCase)

### `test_message_parts.py`
Full integration tests with mocked components:
- Tests complete agent execution with message parts
- Verifies XAgent streaming integration
- Tests message builder functionality
- Tests multimodal content handling

## Running the Tests

```bash
# Run all message parts tests
python tests/run_message_parts_tests.py

# Run only simple tests
pytest tests/integration/test_message_parts_simple.py -v

# Run with coverage
pytest tests/integration/test_message_parts*.py --cov=vibex.core.message --cov=vibex.core.message_builder
```

## What the Tests Verify

1. **Message Structure**
   - Parts are generated in correct order
   - Each part has proper type and fields
   - Content is accumulated correctly

2. **SSE Streaming**
   - `message_start` event initiates streaming
   - `part_delta` events stream text progressively
   - `part_complete` events finalize each part
   - `message_complete` event contains full message

3. **Field Naming**
   - All parts use camelCase fields (e.g., `toolCallId`, `isError`)
   - Compatible with frontend TypeScript interfaces

4. **Error Handling**
   - Tool errors are captured with `isError: true`
   - Error parts provide additional context
   - Message flow continues after errors

## Example Test Output

When you run the tests, you should see verification of:
```
✓ message_start event sent
✓ part_delta events stream text
✓ part_complete events for each part type
✓ message_complete with full structured message
✓ Proper camelCase field names
✓ Error handling and recovery
```

## Adding New Tests

To test new part types or scenarios:

1. Add test method to appropriate test class
2. Use `SSECapture` to record events
3. Verify event sequence and data structure
4. Ensure camelCase naming for all fields