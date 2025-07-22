#!/usr/bin/env python3
"""
Console SSE streaming viewer for AgentX.
This script connects to the SSE endpoint and displays streaming chunks in real-time.
"""
import asyncio
import aiohttp
import json
import sys
import argparse
from datetime import datetime
from typing import Optional

# ANSI color codes for pretty console output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

async def stream_task_events(task_id: str, user_id: str, base_url: str = "http://localhost:7770"):
    """Connect to SSE endpoint and stream events to console."""
    url = f"{base_url}/tasks/{task_id}/stream?user_id={user_id}"
    
    print(f"{Colors.CYAN}🔌 Connecting to SSE stream...{Colors.END}")
    print(f"{Colors.DIM}URL: {url}{Colors.END}")
    print(f"{Colors.DIM}{'='*60}{Colors.END}")
    
    accumulated_text = ""
    current_message_id = None
    chunk_count = 0
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"{Colors.RED}❌ Failed to connect: HTTP {response.status}{Colors.END}")
                    return
                
                print(f"{Colors.GREEN}✅ Connected to SSE stream!{Colors.END}\n")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    # Parse SSE format
                    if line.startswith('event:'):
                        event_type = line[6:].strip()
                        # print(f"{Colors.DIM}[Event: {event_type}]{Colors.END}")
                    
                    elif line.startswith('data:'):
                        try:
                            data = json.loads(line[5:])
                            
                            # Handle different event types
                            if data.get('type') == 'stream_chunk':
                                chunk_data = data.get('data', {})
                                chunk = chunk_data.get('chunk', '')
                                message_id = chunk_data.get('message_id')
                                is_final = chunk_data.get('is_final', False)
                                
                                # New message started
                                if message_id != current_message_id:
                                    if current_message_id:
                                        print(f"\n{Colors.DIM}[Message {current_message_id} complete - {chunk_count} chunks]{Colors.END}\n")
                                    current_message_id = message_id
                                    chunk_count = 0
                                    accumulated_text = ""
                                    print(f"{Colors.BLUE}{Colors.BOLD}📝 New streaming message (ID: {message_id}):{Colors.END}")
                                    print(f"{Colors.YELLOW}", end='', flush=True)
                                
                                # Display chunk
                                if chunk:
                                    print(chunk, end='', flush=True)
                                    accumulated_text += chunk
                                    chunk_count += 1
                                
                                # Final chunk
                                if is_final:
                                    print(f"{Colors.END}")
                                    print(f"{Colors.GREEN}✓ Streaming complete!{Colors.END}")
                                    print(f"{Colors.DIM}Total: {len(accumulated_text)} chars in {chunk_count} chunks{Colors.END}")
                            
                            elif data.get('type') == 'message':
                                # Complete message event
                                msg_data = data.get('data', {})
                                print(f"\n{Colors.MAGENTA}💬 Complete Message:{Colors.END}")
                                print(f"{Colors.DIM}ID: {msg_data.get('id')}{Colors.END}")
                                print(f"{Colors.DIM}Role: {msg_data.get('role')}{Colors.END}")
                                print(f"Content: {msg_data.get('content', '')[:100]}...")
                            
                            elif data.get('type') == 'agent_message':
                                # Agent message event
                                msg_data = data.get('data', {})
                                agent_id = msg_data.get('agent_id', 'unknown')
                                message = msg_data.get('message', '')
                                print(f"\n{Colors.CYAN}🤖 {agent_id}:{Colors.END} {message[:100]}...")
                            
                            elif data.get('type') == 'task_update':
                                # Task status update
                                update_data = data.get('data', {})
                                status = update_data.get('status', 'unknown')
                                print(f"\n{Colors.BLUE}📊 Task Status: {status}{Colors.END}")
                            
                            elif data.get('type') == 'tool_call_start':
                                # Tool call started
                                tool_data = data.get('data', {})
                                tool_name = tool_data.get('tool_name', 'unknown')
                                print(f"\n{Colors.YELLOW}🔧 Tool Call: {tool_name}{Colors.END}")
                            
                            elif data.get('type') == 'tool_call_result':
                                # Tool call result
                                tool_data = data.get('data', {})
                                tool_name = tool_data.get('tool_name', 'unknown')
                                is_error = tool_data.get('is_error', False)
                                if is_error:
                                    print(f"{Colors.RED}❌ {tool_name} failed{Colors.END}")
                                else:
                                    print(f"{Colors.GREEN}✓ {tool_name} completed{Colors.END}")
                            
                        except json.JSONDecodeError:
                            # Not JSON, might be a keep-alive or error
                            if line[5:].strip():
                                print(f"{Colors.DIM}[Raw data: {line[5:]}]{Colors.END}")
                    
                    elif line == '':
                        # Empty line separates events
                        pass
                    
                    elif line.startswith(':'):
                        # Comment line (keep-alive)
                        # print(f"{Colors.DIM}[Keep-alive]{Colors.END}")
                        pass
                        
        except aiohttp.ClientError as e:
            print(f"{Colors.RED}❌ Connection error: {e}{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚡ Stream interrupted by user{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.END}")

async def send_test_message(task_id: str, user_id: str, message: str, base_url: str = "http://localhost:7770"):
    """Send a message to trigger streaming."""
    url = f"{base_url}/tasks/{task_id}/chat"
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": user_id
    }
    
    payload = {
        "content": message
    }
    
    print(f"{Colors.CYAN}📤 Sending message: {message}{Colors.END}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"{Colors.GREEN}✅ Message sent successfully!{Colors.END}")
                    print(f"{Colors.DIM}Response: {json.dumps(result, indent=2)}{Colors.END}")
                else:
                    print(f"{Colors.RED}❌ Failed to send message: HTTP {response.status}{Colors.END}")
                    print(await response.text())
        except Exception as e:
            print(f"{Colors.RED}❌ Error sending message: {e}{Colors.END}")

async def main():
    parser = argparse.ArgumentParser(description='Console SSE streaming viewer for AgentX')
    parser.add_argument('task_id', help='Task ID to stream')
    parser.add_argument('--user-id', default='test-user', help='User ID (default: test-user)')
    parser.add_argument('--url', default='http://localhost:7770', help='AgentX API URL')
    parser.add_argument('--send', help='Send a message before streaming')
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}{Colors.CYAN}🚀 AgentX Console SSE Viewer{Colors.END}")
    print(f"Task ID: {args.task_id}")
    print(f"User ID: {args.user_id}")
    print()
    
    # Send a message first if requested
    if args.send:
        await send_test_message(args.task_id, args.user_id, args.send, args.url)
        print()
        # Give server a moment to start processing
        await asyncio.sleep(1)
    
    # Start streaming
    await stream_task_events(args.task_id, args.user_id, args.url)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.END}")