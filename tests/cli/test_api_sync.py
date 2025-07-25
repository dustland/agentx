#!/usr/bin/env python3
import requests
import json
import time

# Test sync project creation and execution
print("Testing synchronous project execution...")

headers = {
    "X-User-ID": "test-user-sync",
    "Content-Type": "application/json"
}
payload = {
    "goal": "Write a short poem about the seasons.",
    "config_path": "examples/simple_team/config/team.yaml",
    "sync": True  # Request synchronous execution
}

try:
    response = requests.post("http://localhost:7770/projects", 
                           headers=headers, 
                           json=payload)
    
    print(f"Sync project create: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Project completed synchronously:")
        print(json.dumps(result, indent=2))
        
        # Verify final status
        project_id = result.get("project_id")
        if project_id:
            time.sleep(1) # Allow a moment for state to settle
            status_res = requests.get(f"http://localhost:7770/projects/{project_id}", headers=headers)
            print("\nFinal project status:")
            print(json.dumps(status_res.json(), indent=2))
            
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Sync project test failed: {e}")