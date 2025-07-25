#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:7770"
USER_ID = "test-user"

def create_project(goal: str, config: str = "examples/simple_chat/config/team.yaml"):
    """Create a new project."""
    headers = {"X-User-ID": USER_ID}
    payload = {"goal": goal, "config_path": config}
    response = requests.post(f"{BASE_URL}/projects", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_project_status(project_id: str):
    """Get the status of a project."""
    headers = {"X-User-ID": USER_ID}
    response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=headers)
    response.raise_for_status()
    return response.json()

def send_message(project_id: str, message: str):
    """Send a message to a project."""
    headers = {"X-User-ID": USER_ID}
    payload = {"content": message}
    response = requests.post(f"{BASE_URL}/projects/{project_id}/chat", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_messages(project_id: str):
    """Get messages for a project."""
    headers = {"X-User-ID": USER_ID}
    response = requests.get(f"{BASE_URL}/projects/{project_id}/messages", headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    """Main function to run the test."""
    print("Starting API test...")

    # 1. Create a project
    print("\n--- 1. Creating a project ---")
    project_data = create_project("Write a short story about a robot.")
    project_id = project_data.get("project_id")
    print(f"Project created with ID: {project_id}")
    print(f"Initial status: {project_data.get('status')}")

    # 2. Wait for the project to process
    print("\n--- 2. Waiting for project to process ---")
    for _ in range(10):
        status_data = get_project_status(project_id)
        print(f"Current status: {status_data.get('status')}")
        if status_data.get('status') == 'completed':
            break
        time.sleep(2)
    else:
        print("Project did not complete in time.")

    # 3. Send a message to the project
    print("\n--- 3. Sending a message ---")
    send_message(project_id, "Make the story funnier.")
    print("Message sent.")

    # 4. Get all messages
    print("\n--- 4. Getting all messages ---")
    messages = get_messages(project_id)
    print(f"Total messages: {len(messages.get('messages', []))}")
    for msg in messages.get('messages', []):
        print(f"- {msg['role']}: {msg['content'][:80]}...")

    print("\nAPI test finished.")

if __name__ == "__main__":
    main()