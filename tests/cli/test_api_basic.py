#!/usr/bin/env python3
import requests
import json
import time

# --- Test Configuration ---
BASE_URL = "http://localhost:7770"
USER_ID = "test-user-basic"
HEADERS = {"X-User-ID": USER_ID, "Content-Type": "application/json"}
PROJECT_GOAL = "Create a basic plan for a new marketing campaign."
CONFIG_PATH = "examples/simple_team/config/team.yaml"

def create_xagent():
    """Create an XAgent and return its ID."""
    print("--- 1. Creating XAgent ---")
    payload = {"goal": PROJECT_GOAL, "config_path": CONFIG_PATH}
    response = requests.post(f"{BASE_URL}/xagents", headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        xagent_data = response.json()
        xagent_id = xagent_data.get("xagent_id")
        print(f"XAgent created successfully. ID: {xagent_id}")
        return xagent_id
    else:
        print(f"Error creating XAgent: {response.status_code} - {response.text}")
        return None

def get_xagent_details(xagent_id):
    """Get and print details of an XAgent."""
    print(f"--- 2. Getting XAgent Details (ID: {xagent_id}) ---")
    response = requests.get(f"{BASE_URL}/xagents/{xagent_id}", headers=HEADERS)
    
    if response.status_code == 200:
        print("XAgent details retrieved:")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"Error getting XAgent details: {response.status_code} - {response.text}")
        return False

def list_xagents():
    """List all XAgents for the user."""
    print("--- 3. Listing All XAgents ---")
    response = requests.get(f"{BASE_URL}/xagents", headers=HEADERS)
    
    if response.status_code == 200:
        xagents = response.json().get("xagents", [])
        print(f"Found {len(xagents)} XAgents.")
        for xagent in xagents:
            print(f"  - ID: {xagent.get('xagent_id')}, Status: {xagent.get('status')}")
        return True
    else:
        print(f"Error listing XAgents: {response.status_code} - {response.text}")
        return False

def delete_xagent(xagent_id):
    """Delete an XAgent."""
    print(f"--- 4. Deleting XAgent (ID: {xagent_id}) ---")
    response = requests.delete(f"{BASE_URL}/xagents/{xagent_id}", headers=HEADERS)
    
    if response.status_code == 200:
        print("XAgent deleted successfully.")
        return True
    else:
        print(f"Error deleting XAgent: {response.status_code} - {response.text}")
        return False

def run_tests():
    """Run the sequence of API tests."""
    xagent_id = create_xagent()
    
    if xagent_id:
        time.sleep(1)  # Give server a moment
        get_xagent_details(xagent_id)
        list_xagents()
        delete_xagent(xagent_id)

if __name__ == "__main__":
    run_tests()