#!/usr/bin/env python3
"""
Comprehensive API test suite for VibeX server
Tests all main endpoints and provides a summary of what works and what doesn't
"""
import requests
import json
import time
import os

# --- Configuration ---
BASE_URL = os.environ.get("VIBEX_API_URL", "http://localhost:7770")
USER_ID = "test-user-full-suite"
HEADERS = {"X-User-ID": USER_ID, "Content-Type": "application/json"}
CONFIG_PATH = "examples/simple_team/config/team.yaml"

def run_test(name, func, *args, **kwargs):
    """Helper to run a test function and print results."""
    print(f"\n--- Starting Test: {name} ---")
    try:
        result = func(*args, **kwargs)
        if result is not None:
            print(f"Result for {name}:")
            # Limit printing large content
            if isinstance(result, dict) and "content" in result and len(result["content"] or "") > 200:
                result["content"] = result["content"][:200] + "..."
            print(json.dumps(result, indent=2))
        print(f"--- PASSED: {name} ---")
        return result
    except Exception as e:
        print(f"--- FAILED: {name} ---")
        print(f"Error: {e}")
        # Optionally, re-raise to stop all tests on failure
        # raise e
        return None

# --- API Test Functions ---

def test_health_check():
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    response.raise_for_status()
    return response.json()

def test_create_project():
    payload = {"goal": "Test project for full API suite", "config_path": CONFIG_PATH}
    response = requests.post(f"{BASE_URL}/projects", headers=HEADERS, json=payload, timeout=10)
    response.raise_for_status()
    project_data = response.json()
    if "project_id" not in project_data:
        raise ValueError("project_id not in response")
    return project_data

def test_list_projects():
    response = requests.get(f"{BASE_URL}/projects", headers=HEADERS, timeout=5)
    response.raise_for_status()
    return response.json()

def test_get_project(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=HEADERS, timeout=5)
    response.raise_for_status()
    return response.json()

def test_send_chat_message(project_id):
    payload = {"content": "Hello, X agent! Please proceed with the plan."}
    response = requests.post(f"{BASE_URL}/projects/{project_id}/chat", headers=HEADERS, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()

def test_get_messages(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}/messages", headers=HEADERS, timeout=5)
    response.raise_for_status()
    return response.json()

def test_get_artifacts(project_id):
    # This might be empty initially
    response = requests.get(f"{BASE_URL}/projects/{project_id}/artifacts", headers=HEADERS, timeout=5)
    response.raise_for_status()
    return response.json()

def test_get_plan(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}/plan", headers=HEADERS, timeout=5)
    response.raise_for_status()
    return response.json()
    
def test_get_logs(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}/logs?limit=50", headers=HEADERS, timeout=5)
    response.raise_for_status()
    return response.json()

def test_delete_project(project_id):
    response = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()

def main():
    """Main function to orchestrate tests."""
    print("===== Running Full API Test Suite =====")
    
    run_test("Health Check", test_health_check)
    
    project_info = run_test("Create Project", test_create_project)
    if not project_info:
        print("Halting tests: Project creation failed.")
        return
        
    project_id = project_info.get("project_id")
    
    # Wait a bit for async background tasks to start
    time.sleep(2)
    
    # Run tests that depend on a created project
    run_test("List Projects", test_list_projects)
    run_test("Get Project Details", test_get_project, project_id)
    run_test("Send Chat Message", test_send_chat_message, project_id)
    
    # Wait for the chat message to be processed
    print("\nWaiting for project to process the message...")
    time.sleep(5)
    
    run_test("Get Messages", test_get_messages, project_id)
    run_test("Get Artifacts", test_get_artifacts, project_id)
    run_test("Get Plan", test_get_plan, project_id)
    run_test("Get Logs", test_get_logs, project_id)
    
    # Clean up
    run_test("Delete Project", test_delete_project, project_id)
    
    print("\n===== Full API Test Suite Finished =====")

if __name__ == "__main__":
    main()