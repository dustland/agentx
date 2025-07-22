#!/usr/bin/env node

/**
 * Test SSE streaming functionality
 * This script verifies that the backend SSE implementation works correctly
 * by connecting to the stream first, then sending messages.
 * 
 * Usage: node scripts/test-sse-streaming.js
 */

const { EventSource } = require('eventsource');

const API_BASE_URL = process.env.NEXT_PUBLIC_AGENTX_API_URL || 'http://localhost:7770';
const USER_ID = 'sse-stream-test';

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

async function testSSEStreaming() {
  log('\n=== Testing SSE Streaming ===\n', colors.bright + colors.blue);

  try {
    // Step 1: Create task
    log('1. Creating task...', colors.cyan);
    
    const createResponse = await fetch(`${API_BASE_URL}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': USER_ID
      },
      body: JSON.stringify({
        config_path: "examples/simple_chat/config/team.yaml",
        task_description: "Test SSE streaming"
      })
    });

    if (!createResponse.ok) {
      throw new Error(`Failed to create task: ${await createResponse.text()}`);
    }

    const task = await createResponse.json();
    log(`✓ Task created: ${task.task_id}`, colors.green);

    // Step 2: Connect to SSE FIRST
    log('\n2. Connecting to SSE stream...', colors.cyan);
    
    const eventSource = new EventSource(`${API_BASE_URL}/tasks/${task.task_id}/stream?user_id=${USER_ID}`);
    
    const receivedEvents = [];
    let connectionEstablished = false;

    eventSource.onopen = () => {
      connectionEstablished = true;
      log('✓ SSE connection established', colors.green);
    };

    // Note: We're not setting onmessage directly to avoid conflicts
    // All events will be handled by addEventListener

    eventSource.addEventListener('agent_message', (event) => {
      const data = JSON.parse(event.data);
      log(`\n🤖 Agent message event:`, colors.yellow);
      log(`   Agent: ${data.agent_id}`, colors.cyan);
      log(`   Message: ${data.message.substring(0, 100)}...`, colors.cyan);
      receivedEvents.push({ type: 'agent_message', data });
    });

    eventSource.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      log(`\n💬 Message event (complete):`, colors.yellow);
      log(`   ID: ${data.id}`, colors.cyan);
      log(`   Role: ${data.role}`, colors.cyan);
      log(`   Content: ${data.content.substring(0, 100)}...`, colors.cyan);
      receivedEvents.push({ type: 'message', data });
    });

    eventSource.addEventListener('stream_chunk', (event) => {
      const data = JSON.parse(event.data);
      log(`\n✨ Stream chunk event:`, colors.magenta);
      log(`   Message ID: ${data.message_id}`, colors.cyan);
      log(`   Chunk: "${data.chunk}"`, colors.cyan);
      log(`   Is Final: ${data.is_final}`, colors.cyan);
      receivedEvents.push({ type: 'stream_chunk', data });
    });

    eventSource.addEventListener('task_update', (event) => {
      const data = JSON.parse(event.data);
      log(`\n📋 Task update event:`, colors.yellow);
      log(`   Status: ${data.status}`, colors.cyan);
      receivedEvents.push({ type: 'task_update', data });
    });

    eventSource.addEventListener('tool_call', (event) => {
      const data = JSON.parse(event.data);
      log(`\n🔧 Tool call event:`, colors.yellow);
      log(`   Tool: ${data.tool_name}`, colors.cyan);
      log(`   Status: ${data.status}`, colors.cyan);
      receivedEvents.push({ type: 'tool_call', data });
    });

    eventSource.onerror = (error) => {
      log(`\n⚠️  SSE error:`, colors.red);
      console.error(error);
    };

    // Wait for connection to establish
    await new Promise(resolve => {
      const checkConnection = setInterval(() => {
        if (connectionEstablished) {
          clearInterval(checkConnection);
          resolve();
        }
      }, 100);
      
      // Timeout after 3 seconds
      setTimeout(() => {
        clearInterval(checkConnection);
        resolve();
      }, 3000);
    });

    // Step 3: Send message AFTER SSE is connected
    log('\n3. Sending chat message...', colors.cyan);
    
    const chatResponse = await fetch(`${API_BASE_URL}/tasks/${task.task_id}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': USER_ID
      },
      body: JSON.stringify({
        message: "Hello! Tell me a joke about programming."
      })
    });

    if (!chatResponse.ok) {
      throw new Error(`Failed to send message: ${await chatResponse.text()}`);
    }

    const chatResult = await chatResponse.json();
    log('✓ Message sent', colors.green);
    log(`  Response preview: ${chatResult.response.substring(0, 100)}...`, colors.cyan);

    // Step 4: Listen for SSE events
    log('\n4. Listening for SSE events...', colors.cyan);
    
    // Wait for events (5 seconds)
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Close connection
    eventSource.close();

    // Results
    log('\n=== Test Results ===', colors.bright + colors.blue);
    log(`Total events received: ${receivedEvents.length}`, colors.cyan);
    
    const eventTypes = {};
    receivedEvents.forEach(event => {
      eventTypes[event.type] = (eventTypes[event.type] || 0) + 1;
    });

    Object.entries(eventTypes).forEach(([type, count]) => {
      log(`  ${type}: ${count}`, colors.green);
    });

    if (receivedEvents.length > 0) {
      log('\n✅ SSE streaming is working!', colors.green);
      
      // Check for streaming chunks
      const streamChunks = receivedEvents.filter(e => e.type === 'stream_chunk');
      const completeMessages = receivedEvents.filter(e => e.type === 'message');
      
      if (streamChunks.length > 0) {
        log(`\n🎉 Streaming chunks detected: ${streamChunks.length} chunks`, colors.green);
        
        // Reconstruct streamed message
        const messageChunks = {};
        streamChunks.forEach(event => {
          const msgId = event.data.message_id;
          if (!messageChunks[msgId]) {
            messageChunks[msgId] = [];
          }
          messageChunks[msgId].push(event.data);
        });
        
        Object.entries(messageChunks).forEach(([msgId, chunks]) => {
          const fullText = chunks.map(c => c.chunk).join('');
          log(`\n  Streamed message ${msgId}:`, colors.cyan);
          log(`    Chunks: ${chunks.length}`, colors.cyan);
          log(`    Text: "${fullText.substring(0, 100)}..."`, colors.cyan);
        });
      }
      
      if (completeMessages.length > 0) {
        log(`\n📦 Complete messages received: ${completeMessages.length}`, colors.green);
        completeMessages.forEach(event => {
          log(`  Message ID: ${event.data.id}, Role: ${event.data.role}`, colors.cyan);
        });
      }
      
      // Show last few events
      log('\nLast 5 events:', colors.cyan);
      receivedEvents.slice(-5).forEach((event, i) => {
        log(`  ${i + 1}. ${event.type}`, colors.yellow);
        if (event.type === 'agent_message') {
          log(`     Agent: ${event.data.agent_id}`, colors.cyan);
          log(`     Message: ${event.data.message.substring(0, 60)}...`, colors.cyan);
        } else if (event.type === 'stream_chunk') {
          log(`     Chunk: "${event.data.chunk}"`, colors.cyan);
          log(`     Final: ${event.data.is_final}`, colors.cyan);
        } else if (event.type === 'message') {
          log(`     Role: ${event.data.role}`, colors.cyan);
          log(`     Content: ${event.data.content.substring(0, 60)}...`, colors.cyan);
        }
      });
    } else {
      log('\n❌ No SSE events received', colors.red);
    }

  } catch (error) {
    log(`\n❌ Test failed: ${error.message}`, colors.red);
    console.error(error);
  }
}

// Run test
testSSEStreaming().catch(console.error);