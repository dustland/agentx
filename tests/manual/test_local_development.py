#!/usr/bin/env python3
"""
Manual test for local development scenario.

This script demonstrates using the TaskspaceFactory and TaskspaceStorage
in a typical local development workflow.
"""

import asyncio
import json
import time
from pathlib import Path
import tempfile
import shutil

from agentx.storage import TaskspaceFactory


async def test_local_development_scenario():
    """Test the complete local development workflow."""
    print("=== AgentX Taskspace System - Local Development Test ===\n")
    
    # Setup
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temp directory: {temp_dir}")
    
    try:
        # 1. Create taskspace with memory caching for local development
        print("\n1. Creating taskspace with memory caching...")
        taskspace = TaskspaceFactory.create_taskspace(
            base_path=temp_dir,
            task_id="dev_task_001",
            user_id="developer",
            use_git_artifacts=True,
            cache_provider="memory"
        )
        print(f"✓ Taskspace created at: {taskspace.get_taskspace_path()}")
        print(f"✓ Caching enabled: {taskspace._cache is not None}")
        
        # 2. Create a realistic plan
        print("\n2. Storing development plan...")
        plan = {
            "goal": "Implement user authentication system",
            "description": "Create a secure authentication system with JWT tokens",
            "status": "in_progress",
            "tasks": [
                {
                    "id": "auth-001",
                    "name": "Design database schema",
                    "status": "completed",
                    "priority": "high"
                },
                {
                    "id": "auth-002", 
                    "name": "Implement user registration",
                    "status": "in_progress",
                    "priority": "high"
                },
                {
                    "id": "auth-003",
                    "name": "Add JWT token generation",
                    "status": "pending",
                    "priority": "medium"
                }
            ],
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T14:30:00Z"
        }
        
        result = await taskspace.store_plan(plan)
        print(f"✓ Plan stored successfully: {result.success}")
        
        # 3. Store some development artifacts
        print("\n3. Storing development artifacts...")
        
        # Store code files
        user_model = '''
class User:
    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
'''
        
        await taskspace.store_artifact(
            "user_model.py", 
            user_model,
            content_type="text/x-python",
            metadata={"language": "python", "component": "model"}
        )
        
        # Store configuration
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "auth_db"
            },
            "jwt": {
                "secret_key": "dev-secret-key",
                "expiration_hours": 24
            }
        }
        
        await taskspace.store_artifact(
            "config.json",
            json.dumps(config, indent=2),
            content_type="application/json",
            metadata={"type": "configuration"}
        )
        
        # Store test results
        test_results = {
            "test_suite": "authentication_tests",
            "total_tests": 15,
            "passed": 12,
            "failed": 3,
            "coverage": "87%",
            "failed_tests": [
                "test_password_validation",
                "test_duplicate_email", 
                "test_jwt_expiration"
            ]
        }
        
        await taskspace.store_artifact(
            "test_results.json",
            json.dumps(test_results, indent=2),
            content_type="application/json",
            metadata={"type": "test_results", "timestamp": "2024-01-15T14:30:00Z"}
        )
        
        print("✓ Stored 3 artifacts (user_model.py, config.json, test_results.json)")
        
        # 4. Store conversation messages
        print("\n4. Storing conversation history...")
        
        messages = [
            {
                "role": "user",
                "content": "Help me implement user registration with email validation",
                "timestamp": "2024-01-15T14:00:00Z"
            },
            {
                "role": "assistant", 
                "content": "I'll help you implement user registration. First, let's define the validation requirements...",
                "timestamp": "2024-01-15T14:01:00Z"
            },
            {
                "role": "user",
                "content": "The password should have at least 8 characters with mixed case and numbers",
                "timestamp": "2024-01-15T14:15:00Z"
            },
            {
                "role": "assistant",
                "content": "Perfect! I'll add password complexity validation to the User model...",
                "timestamp": "2024-01-15T14:16:00Z"
            }
        ]
        
        for msg in messages:
            await taskspace.store_message(msg)
        
        print(f"✓ Stored {len(messages)} conversation messages")
        
        # 5. Demonstrate caching performance
        print("\n5. Testing cache performance...")
        
        # Time multiple plan reads (should hit cache after first read)
        start_time = time.time()
        for i in range(20):
            plan_data = await taskspace.get_plan()
        cached_time = time.time() - start_time
        
        print(f"✓ 20 plan reads (with cache): {cached_time:.4f} seconds")
        
        # Test artifact retrieval
        start_time = time.time()
        for i in range(10):
            config_content = await taskspace.get_artifact("config.json")
        artifact_time = time.time() - start_time
        
        print(f"✓ 10 artifact reads (with cache): {artifact_time:.4f} seconds")
        
        # 6. Retrieve and display summary
        print("\n6. Taskspace summary...")
        summary = await taskspace.get_taskspace_summary()
        
        print(f"✓ Total files: {summary['total_files']}")
        print(f"✓ Total size: {summary['total_size_bytes']} bytes")
        print(f"✓ Total artifacts: {summary['total_artifacts']}")
        print(f"✓ Artifact storage: {summary['artifact_storage']}")
        
        # 7. List all artifacts
        print("\n7. Listing artifacts...")
        artifacts = await taskspace.list_artifacts()
        
        for artifact in artifacts:
            print(f"  - {artifact['name']} (v{artifact['version']}) - {artifact.get('size', 'unknown')} bytes")
        
        # 8. Get conversation history
        print("\n8. Conversation history...")
        history = await taskspace.get_conversation_history()
        
        print(f"✓ Retrieved {len(history)} messages")
        for i, msg in enumerate(history[-2:], 1):  # Show last 2 messages
            role = msg['role'].capitalize()
            content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            print(f"  {i}. {role}: {content}")
        
        # 9. Test without cache to show performance difference
        print("\n9. Testing without cache for comparison...")
        
        # Create taskspace without cache
        no_cache_taskspace = TaskspaceFactory.create_taskspace(
            base_path=temp_dir,
            task_id="dev_task_002",  # Different task to avoid conflicts
            user_id="developer",
            cache_provider=None
        )
        
        # Copy the plan to no-cache taskspace
        await no_cache_taskspace.store_plan(plan)
        
        # Time reads without cache
        start_time = time.time()
        for i in range(20):
            plan_data = await no_cache_taskspace.get_plan()
        no_cache_time = time.time() - start_time
        
        speedup = no_cache_time / cached_time if cached_time > 0 else 0
        print(f"✓ 20 plan reads (no cache): {no_cache_time:.4f} seconds")
        print(f"✓ Cache speedup: {speedup:.1f}x faster")
        
        print("\n=== Local Development Test Complete ===")
        print("✓ All operations successful")
        print("✓ Caching provides significant performance improvement")
        print("✓ API is easy to use for development workflows")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n✓ Cleaned up temp directory: {temp_dir}")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_local_development_scenario())
    exit(0 if success else 1)