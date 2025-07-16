#!/usr/bin/env python3
"""
Test script for multi-worker FastAPI deployment.

This script tests:
1. API endpoints work correctly
2. State is shared across workers via caching
3. Task execution works in multi-worker mode
4. Artifacts and messages are handled correctly
"""

import asyncio
import httpx
import json
import os
import time
import uuid
from typing import Dict, Any, List

BASE_URL = "http://localhost:7770"
API_KEY = "test-api-key"  # Update this if you have auth configured

# Use memory cache for testing since Redis may not be available
os.environ["ENABLE_MEMORY_CACHE"] = "true"
os.environ["ENABLE_REDIS_CACHE"] = "false"


class MultiWorkerAPITest:
    """Test suite for multi-worker API deployment."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={"X-API-Key": API_KEY} if API_KEY else {},
            timeout=30.0
        )
        self.task_id = None
        self.results = {}
    
    async def cleanup(self):
        """Clean up resources."""
        await self.client.aclose()
    
    async def test_health_check(self):
        """Test basic health check endpoint."""
        print("\n1. Testing health check...")
        try:
            response = await self.client.get("/health")
            assert response.status_code == 200
            data = response.json()
            print(f"✓ Health check passed: {data}")
            self.results["health_check"] = "PASSED"
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.results["health_check"] = f"FAILED: {e}"
            return False
    
    async def test_create_task(self):
        """Test task creation."""
        print("\n2. Testing task creation...")
        try:
            task_data = {
                "config_path": "tests/manual/test_team.yaml",  # Test config
                "task_description": "Test multi-worker functionality: Verify that state is shared across workers"
            }
            
            response = await self.client.post("/tasks", json=task_data)
            if response.status_code != 200:
                print(f"   Response status: {response.status_code}")
                print(f"   Response body: {response.text}")
            assert response.status_code == 200
            
            data = response.json()
            self.task_id = data["task_id"]
            
            print(f"✓ Task created successfully: {self.task_id}")
            self.results["task_creation"] = "PASSED"
            return True
        except Exception as e:
            print(f"❌ Task creation failed: {e}")
            if hasattr(e, 'response'):
                print(f"   Response status: {e.response.status_code}")
                print(f"   Response body: {e.response.text}")
            self.results["task_creation"] = f"FAILED: {e}"
            return False
    
    async def test_get_task_status(self):
        """Test getting task status (tests cache hit)."""
        print("\n3. Testing task status retrieval...")
        if not self.task_id:
            print("❌ No task_id available")
            self.results["task_status"] = "SKIPPED: No task_id"
            return False
        
        try:
            # Test multiple times to verify caching
            response_times = []
            
            for i in range(5):
                start_time = time.time()
                response = await self.client.get(f"/tasks/{self.task_id}/status")
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                assert response.status_code == 200
                data = response.json()
                
                print(f"  Request {i+1}: {response_time:.3f}s - Status: {data.get('status', 'unknown')}")
            
            # First request might be slower, subsequent should be faster (cached)
            avg_initial = sum(response_times[:2]) / 2
            avg_cached = sum(response_times[2:]) / 3
            
            if avg_cached < avg_initial * 0.5:  # Cached should be at least 2x faster
                print(f"✓ Caching detected: Initial avg: {avg_initial:.3f}s, Cached avg: {avg_cached:.3f}s")
            else:
                print(f"⚠️  Caching may not be working: Initial avg: {avg_initial:.3f}s, Cached avg: {avg_cached:.3f}s")
            
            self.results["task_status"] = "PASSED"
            return True
        except Exception as e:
            print(f"❌ Task status retrieval failed: {e}")
            self.results["task_status"] = f"FAILED: {e}"
            return False
    
    async def test_execute_task(self):
        """Test task execution."""
        print("\n4. Testing task execution...")
        if not self.task_id:
            print("❌ No task_id available")
            self.results["task_execution"] = "SKIPPED: No task_id"
            return False
        
        try:
            # Start task execution
            execute_data = {
                "stream": False,  # Non-streaming for simplicity
                "model": "claude-3-5-sonnet-latest"
            }
            
            response = await self.client.post(
                f"/tasks/{self.task_id}/execute",
                json=execute_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Task execution completed: {result.get('status', 'unknown')}")
                self.results["task_execution"] = "PASSED"
                return True
            else:
                print(f"❌ Task execution returned status: {response.status_code}")
                print(f"   Response: {response.text}")
                self.results["task_execution"] = f"FAILED: Status {response.status_code}"
                return False
                
        except Exception as e:
            print(f"❌ Task execution failed: {e}")
            self.results["task_execution"] = f"FAILED: {e}"
            return False
    
    async def test_artifact_operations(self):
        """Test artifact storage and retrieval."""
        print("\n5. Testing artifact operations...")
        if not self.task_id:
            print("❌ No task_id available")
            self.results["artifacts"] = "SKIPPED: No task_id"
            return False
        
        try:
            # Store an artifact
            artifact_data = {
                "name": "test_result.json",
                "content": json.dumps({"test": "multi-worker", "timestamp": time.time()}),
                "content_type": "application/json"
            }
            
            response = await self.client.post(
                f"/tasks/{self.task_id}/artifacts",
                json=artifact_data
            )
            
            if response.status_code != 200:
                print(f"❌ Artifact creation failed: {response.status_code}")
                self.results["artifacts"] = f"FAILED: Create returned {response.status_code}"
                return False
            
            print("✓ Artifact created successfully")
            
            # List artifacts (should hit cache on subsequent requests)
            list_times = []
            for i in range(3):
                start_time = time.time()
                response = await self.client.get(f"/tasks/{self.task_id}/artifacts")
                list_time = time.time() - start_time
                list_times.append(list_time)
                
                assert response.status_code == 200
                artifacts = response.json()
                
                print(f"  List request {i+1}: {list_time:.3f}s - Found {len(artifacts)} artifacts")
            
            # Verify artifact is listed
            artifact_found = any(a["name"] == "test_result.json" for a in artifacts)
            if artifact_found:
                print("✓ Artifact found in listing")
            else:
                print("❌ Artifact not found in listing")
                self.results["artifacts"] = "FAILED: Artifact not in list"
                return False
            
            # Get specific artifact
            response = await self.client.get(f"/tasks/{self.task_id}/artifacts/test_result.json")
            if response.status_code == 200:
                content = response.json()
                print(f"✓ Artifact retrieved successfully: {content}")
                self.results["artifacts"] = "PASSED"
                return True
            else:
                print(f"❌ Artifact retrieval failed: {response.status_code}")
                self.results["artifacts"] = f"FAILED: Get returned {response.status_code}"
                return False
                
        except Exception as e:
            print(f"❌ Artifact operations failed: {e}")
            self.results["artifacts"] = f"FAILED: {e}"
            return False
    
    async def test_conversation_operations(self):
        """Test conversation/message operations."""
        print("\n6. Testing conversation operations...")
        if not self.task_id:
            print("❌ No task_id available")
            self.results["conversation"] = "SKIPPED: No task_id"
            return False
        
        try:
            # Add messages
            messages = [
                {"role": "user", "content": "Test message from worker 1"},
                {"role": "assistant", "content": "Response processed by worker 2"}
            ]
            
            for msg in messages:
                response = await self.client.post(
                    f"/tasks/{self.task_id}/messages",
                    json=msg
                )
                if response.status_code != 200:
                    print(f"❌ Message creation failed: {response.status_code}")
                    self.results["conversation"] = f"FAILED: Message create returned {response.status_code}"
                    return False
            
            print("✓ Messages created successfully")
            
            # Get conversation history
            response = await self.client.get(f"/tasks/{self.task_id}/messages")
            if response.status_code == 200:
                history = response.json()
                print(f"✓ Retrieved {len(history)} messages")
                
                # Verify our messages are there
                found_user = any(m.get("content") == "Test message from worker 1" for m in history)
                found_assistant = any(m.get("content") == "Response processed by worker 2" for m in history)
                
                if found_user and found_assistant:
                    print("✓ All messages found in history")
                    self.results["conversation"] = "PASSED"
                    return True
                else:
                    print("❌ Some messages missing from history")
                    self.results["conversation"] = "FAILED: Messages not found"
                    return False
            else:
                print(f"❌ Message retrieval failed: {response.status_code}")
                self.results["conversation"] = f"FAILED: Get returned {response.status_code}"
                return False
                
        except Exception as e:
            print(f"❌ Conversation operations failed: {e}")
            self.results["conversation"] = f"FAILED: {e}"
            return False
    
    async def test_cross_worker_consistency(self):
        """Test that state is consistent across multiple rapid requests."""
        print("\n7. Testing cross-worker consistency...")
        if not self.task_id:
            print("❌ No task_id available")
            self.results["consistency"] = "SKIPPED: No task_id"
            return False
        
        try:
            # Make rapid parallel requests that might hit different workers
            async def get_status():
                response = await self.client.get(f"/tasks/{self.task_id}/status")
                return response.json() if response.status_code == 200 else None
            
            # Fire 10 parallel requests
            results = await asyncio.gather(*[get_status() for _ in range(10)])
            
            # All results should be identical
            if all(results):
                first_result = results[0]
                all_identical = all(r == first_result for r in results[1:])
                
                if all_identical:
                    print("✓ All 10 parallel requests returned identical results")
                    print(f"  Consistent status: {first_result.get('status', 'unknown')}")
                    self.results["consistency"] = "PASSED"
                    return True
                else:
                    print("❌ Inconsistent results across parallel requests")
                    self.results["consistency"] = "FAILED: Inconsistent results"
                    return False
            else:
                print("❌ Some requests failed")
                self.results["consistency"] = "FAILED: Some requests failed"
                return False
                
        except Exception as e:
            print(f"❌ Consistency test failed: {e}")
            self.results["consistency"] = f"FAILED: {e}"
            return False
    
    async def run_all_tests(self):
        """Run all tests in sequence."""
        print("=== Multi-Worker API Test Suite ===")
        print(f"Testing against: {BASE_URL}")
        print("Note: Make sure the API is running with multiple workers (uv run prod)")
        
        tests = [
            self.test_health_check,
            self.test_create_task,
            self.test_get_task_status,
            self.test_artifact_operations,
            self.test_conversation_operations,
            self.test_cross_worker_consistency,
            self.test_execute_task,  # Run last as it might take time
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                print(f"❌ Test crashed: {e}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print("\n=== Test Summary ===")
        passed = sum(1 for r in self.results.values() if r == "PASSED")
        failed = sum(1 for r in self.results.values() if r.startswith("FAILED"))
        skipped = sum(1 for r in self.results.values() if r.startswith("SKIPPED"))
        
        for test_name, result in self.results.items():
            status_icon = "✓" if result == "PASSED" else "❌" if result.startswith("FAILED") else "⚠️"
            print(f"{status_icon} {test_name}: {result}")
        
        print(f"\nTotal: {len(self.results)} tests")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        
        return failed == 0


async def main():
    """Run the multi-worker API tests."""
    tester = MultiWorkerAPITest()
    
    try:
        success = await tester.run_all_tests()
        return success
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        return False
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)