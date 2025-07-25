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

def create_project():
    """Create a project and return its ID."""
    print("--- 1. Creating Project ---")
    payload = {"goal": PROJECT_GOAL, "config_path": CONFIG_PATH}
    response = requests.post(f"{BASE_URL}/projects", headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        project_data = response.json()
        project_id = project_data.get("project_id")
        print(f"Project created successfully. ID: {project_id}")
        return project_id
    else:
        print(f"Error creating project: {response.status_code} - {response.text}")
        return None

def get_project_details(project_id):
    """Get and print details of a project."""
    print(f"--- 2. Getting Project Details (ID: {project_id}) ---")
    response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
    
    if response.status_code == 200:
        print("Project details retrieved:")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"Error getting project details: {response.status_code} - {response.text}")
        return False

def list_projects():
    """List all projects for the user."""
    print("--- 3. Listing All Projects ---")
    response = requests.get(f"{BASE_URL}/projects", headers=HEADERS)
    
    if response.status_code == 200:
        projects = response.json().get("projects", [])
        print(f"Found {len(projects)} projects.")
        for project in projects:
            print(f"  - ID: {project.get('project_id')}, Status: {project.get('status')}")
        return True
    else:
        print(f"Error listing projects: {response.status_code} - {response.text}")
        return False

def delete_project(project_id):
    """Delete a project."""
    print(f"--- 4. Deleting Project (ID: {project_id}) ---")
    response = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
    
    if response.status_code == 200:
        print("Project deleted successfully.")
        return True
    else:
        print(f"Error deleting project: {response.status_code} - {response.text}")
        return False

def run_tests():
    """Run the sequence of API tests."""
    project_id = create_project()
    
    if project_id:
        time.sleep(1)  # Give server a moment
        get_project_details(project_id)
        list_projects()
        delete_project(project_id)

if __name__ == "__main__":
    run_tests()