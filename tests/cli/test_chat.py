#!/usr/bin/env python3
import requests
import json

project_id = "_Wxc6V_E"  # From the previous test

print(f"Testing chat with project {project_id}...")
headers = {
    "X-User-ID": "test-user",
    "Content-Type": "application/json"
}

payload = {
    "project_id": project_id,
    "content": "Hello, this is a test message"
}

try:
    response = requests.post("http://localhost:7770/chat", 
                           headers=headers, 
                           json=payload,
                           timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS! Chat response:")
        result = response.json()
        print(f"Message ID: {result.get('message_id')}")
        print(f"Response: {result.get('response', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")