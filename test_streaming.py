#!/usr/bin/env python3
"""
Test script to verify streaming functionality in AgentX framework.
This script tests streaming without the web UI to isolate the core functionality.
"""
import asyncio
import sys
from pathlib import Path
from agentx.core.xagent import XAgent
from agentx.config.team_loader import load_team_config
from agentx.utils.logger import get_logger

logger = get_logger(__name__)

class StreamingTester:
    """Helper class to capture and display streaming events."""
    
    def __init__(self):
        self.chunks = []
        self.complete_response = ""
        
    async def capture_streaming_response(self, x_agent: XAgent, message: str):
        """Test streaming by monitoring XAgent's internal streaming."""
        print(f"\n🧪 Testing streaming response for: '{message}'")
        print("=" * 50)
        
        # Clear previous data
        self.chunks = []
        self.complete_response = ""
        
        # Mock the streaming function to capture chunks
        original_send_stream_chunk = None
        
        try:
            # Try to import and mock the streaming function
            from agentx.server.streaming import send_stream_chunk
            original_send_stream_chunk = send_stream_chunk
            
            async def mock_send_stream_chunk(task_id, chunk, message_id, is_final=False, error=None):
                """Mock function to capture streaming chunks."""
                timestamp = asyncio.get_event_loop().time()
                
                if error:
                    print(f"❌ ERROR CHUNK: {error}")
                    self.chunks.append({
                        "type": "error", 
                        "content": error, 
                        "timestamp": timestamp,
                        "message_id": message_id,
                        "is_final": is_final
                    })
                else:
                    if chunk:  # Only print non-empty chunks
                        print(f"📤 CHUNK: '{chunk}' (len={len(chunk)}, msg_id={message_id})")
                        self.complete_response += chunk
                        self.chunks.append({
                            "type": "content", 
                            "content": chunk, 
                            "timestamp": timestamp,
                            "message_id": message_id,
                            "is_final": is_final
                        })
                    
                    if is_final:
                        print(f"🏁 FINAL CHUNK (msg_id={message_id})")
                        self.chunks.append({
                            "type": "final", 
                            "content": "", 
                            "timestamp": timestamp,
                            "message_id": message_id,
                            "is_final": True
                        })
            
            # Replace the function temporarily
            import agentx.server.streaming
            agentx.server.streaming.send_stream_chunk = mock_send_stream_chunk
            
        except ImportError:
            print("⚠️  Streaming module not available, testing core response only")
        
        # Call the chat method and measure time
        start_time = asyncio.get_event_loop().time()
        try:
            response = await x_agent.chat(message)
            end_time = asyncio.get_event_loop().time()
            
            print(f"\n✅ Chat completed in {end_time - start_time:.2f}s")
            print(f"📝 Full response: '{response.text}'")
            
            # Analyze streaming performance
            if self.chunks:
                print(f"\n📊 Streaming Analysis:")
                print(f"   • Total chunks received: {len([c for c in self.chunks if c['type'] == 'content'])}")
                print(f"   • Total characters streamed: {len(self.complete_response)}")
                print(f"   • Streamed response matches final: {self.complete_response.strip() == response.text.strip()}")
                
                # Calculate timing between chunks
                content_chunks = [c for c in self.chunks if c['type'] == 'content']
                if len(content_chunks) > 1:
                    intervals = []
                    for i in range(1, len(content_chunks)):
                        interval = content_chunks[i]['timestamp'] - content_chunks[i-1]['timestamp']
                        intervals.append(interval * 1000)  # Convert to ms
                    
                    avg_interval = sum(intervals) / len(intervals)
                    print(f"   • Average chunk interval: {avg_interval:.1f}ms")
                    print(f"   • Chunk intervals: {[f'{i:.1f}ms' for i in intervals[:5]]}{' ...' if len(intervals) > 5 else ''}")
            else:
                print("⚠️  No streaming chunks captured - streaming may not be working")
            
        except Exception as e:
            print(f"❌ Error during chat: {e}")
            logger.error(f"Chat failed: {e}", exc_info=True)
        
        # Restore original function
        if original_send_stream_chunk:
            agentx.server.streaming.send_stream_chunk = original_send_stream_chunk
        
        print("=" * 50)

async def main():
    """Main test function."""
    print("🚀 AgentX Streaming Test")
    print("This script tests streaming functionality in the core AgentX framework")
    print()
    
    # Load simple_chat configuration
    config_path = Path("examples/simple_chat/config/team.yaml")
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        print("Please run this script from the AgentX root directory")
        sys.exit(1)
    
    print(f"📁 Loading config from: {config_path}")
    try:
        team_config = load_team_config(str(config_path))
        print(f"✅ Config loaded successfully")
        print(f"   • Team name: {getattr(team_config, 'name', 'Unknown')}")
        print(f"   • Agents: {[agent.name for agent in team_config.agents]}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)
    
    # Initialize XAgent
    print(f"\n🤖 Initializing XAgent...")
    try:
        x = XAgent(team_config=team_config)
        print(f"✅ XAgent initialized successfully")
        print(f"   • Task ID: {x.task_id}")
        print(f"   • Brain config: {x.brain.config.provider if hasattr(x.brain, 'config') else 'Unknown'}")
        print(f"   • Specialist agents: {list(x.specialist_agents.keys())}")
    except Exception as e:
        print(f"❌ Failed to initialize XAgent: {e}")
        logger.error(f"XAgent initialization failed: {e}", exc_info=True)
        sys.exit(1)
    
    # Create streaming tester
    tester = StreamingTester()
    
    # Test messages of increasing complexity
    test_messages = [
        "Hello, how are you?",
        "Tell me a joke about programming",
        "Explain what React is in 3 sentences",
        "Count from 1 to 5 with explanations"
    ]
    
    for i, test_message in enumerate(test_messages, 1):
        print(f"\n🧪 Test {i}/{len(test_messages)}")
        await tester.capture_streaming_response(x, test_message)
        
        # Add delay between tests
        if i < len(test_messages):
            print("⏳ Waiting 2s before next test...")
            await asyncio.sleep(2)
    
    print(f"\n🎉 All tests completed!")
    print(f"Summary:")
    print(f"   • Tests run: {len(test_messages)}")
    print(f"   • XAgent task ID: {x.task_id}")
    print(f"   • Check task_data/{x.task_id}/ for generated files")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)