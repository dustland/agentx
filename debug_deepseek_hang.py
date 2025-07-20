#!/usr/bin/env python3
"""Debug script to test if DeepSeek API is hanging."""

import asyncio
import os
import logging
import litellm

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
litellm.set_verbose = True

async def test_direct_litellm_call():
    """Test a direct litellm call to DeepSeek."""
    print("Testing direct litellm call to DeepSeek...")
    
    try:
        # Simple non-streaming call
        response = await litellm.acompletion(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": "hi"}],
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            timeout=10,  # 10 second timeout
            stream=False
        )
        
        print(f"Success! Response: {response.choices[0].message.content}")
        return True
        
    except asyncio.TimeoutError:
        print("ERROR: Request timed out after 10 seconds!")
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False

async def test_with_brain_config():
    """Test using the Brain configuration."""
    from agentx.core.config import BrainConfig
    from agentx.core.brain import Brain
    
    print("\nTesting with Brain configuration...")
    
    try:
        # Create brain with short timeout
        config = BrainConfig(
            provider="deepseek",
            model="deepseek-chat",
            timeout=10  # 10 second timeout
        )
        
        brain = Brain(config=config)
        # Brain doesn't have an initialize method, it's initialized on first use
        
        response = await brain.generate_response(
            messages=[{"role": "user", "content": "hi"}],
            temperature=0.7
        )
        
        print(f"Success! Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("=== DeepSeek API Hang Debug ===\n")
    
    # Check API key
    has_key = bool(os.getenv("DEEPSEEK_API_KEY"))
    print(f"DEEPSEEK_API_KEY exists: {has_key}")
    
    if not has_key:
        print("ERROR: DEEPSEEK_API_KEY not set!")
        return
    
    print("\n" + "="*50 + "\n")
    
    # Test 1: Direct litellm call
    success1 = await test_direct_litellm_call()
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Brain configuration
    success2 = await test_with_brain_config()
    
    print("\n" + "="*50 + "\n")
    print(f"Results: Direct call: {'✓' if success1 else '✗'}, Brain call: {'✓' if success2 else '✗'}")

if __name__ == "__main__":
    asyncio.run(main())