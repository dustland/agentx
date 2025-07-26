# Project Service

*Module: [`vibex.server.project_service`](https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py)*

Project Service Layer

Provides business logic orchestration for project management.
Handles user-project relationships while keeping the framework pure.

## ProjectService <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L23" class="source-link" title="View source code">source</a>

Service layer for project management.

This service handles:
- User-project relationship management
- Project access control
- High-level project operations

It does NOT handle:
- Storage paths (framework's responsibility)
- HTTP concerns (API layer's responsibility)

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L37" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### create_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L41" class="source-link" title="View source code">source</a>

```python
async def create_project(self, user_id: str, description: str, config_path: str = 'examples/simple_chat/config/team.yaml', context: Optional[Dict[str, Any]] = None) -> ProjectResponse
```

Create a new project for a user.

**Args:**
    user_id: The user creating the project
    description: The initial project goal
    config_path: Path to team configuration
    context: Additional context for the project

**Returns:**
    ProjectResponse object

### verify_project_ownership <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L86" class="source-link" title="View source code">source</a>

```python
async def verify_project_ownership(self, user_id: str, project_id: str) -> bool
```

Verify that a user owns a project without loading the full project.

This is a lightweight check that doesn't create any log entries
or initialize the project, making it safe to use for read-only
operations like fetching logs.

**Args:**
    user_id: The user to check
    project_id: The project to check

**Returns:**
    True if user owns the project

**Raises:**
    PermissionError: If user doesn't own the project
    ValueError: If project doesn't exist

### get_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L118" class="source-link" title="View source code">source</a>

```python
async def get_project(self, user_id: str, project_id: str) -> XAgent
```

Get the project's X agent, verifying user ownership.

**Args:**
    user_id: The user requesting the project
    project_id: The project to retrieve

**Returns:**
    The project's XAgent instance

**Raises:**
    PermissionError: If user doesn't own the project
    ValueError: If project doesn't exist

### list_user_projects <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L150" class="source-link" title="View source code">source</a>

```python
async def list_user_projects(self, user_id: str) -> List[Dict[str, Any]]
```

List all projects for a user.

**Args:**
    user_id: The user whose projects to list

**Returns:**
    List of project information dictionaries

### delete_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L189" class="source-link" title="View source code">source</a>

```python
async def delete_project(self, user_id: str, project_id: str) -> None
```

Delete a task, verifying user ownership.

**Args:**
    user_id: The user deleting the task
    project_id: The task to delete

**Raises:**
    PermissionError: If user doesn't own the project

### send_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L215" class="source-link" title="View source code">source</a>

```python
async def send_message(self, user_id: str, project_id: str, content: str, mode: str = 'agent') -> Dict[str, Any]
```

Send a message to the project's X agent.

**Args:**
    user_id: The user sending the message
    project_id: The project to send to
    content: The message content

**Returns:**
    Response information

**Raises:**
    PermissionError: If user doesn't own the project

### get_project_messages <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L271" class="source-link" title="View source code">source</a>

```python
async def get_project_messages(self, user_id: str, project_id: str) -> List[Dict[str, Any]]
```

Get messages for a project.

**Args:**
    user_id: The user requesting messages
    project_id: The project whose messages to retrieve

**Returns:**
    List of messages

**Raises:**
    PermissionError: If user doesn't own the project

### get_project_artifacts <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L313" class="source-link" title="View source code">source</a>

```python
async def get_project_artifacts(self, user_id: str, project_id: str) -> List[Dict[str, Any]]
```

Get artifacts for a project.

**Args:**
    user_id: The user requesting artifacts
    project_id: The project whose artifacts to retrieve

**Returns:**
    List of artifact information

**Raises:**
    PermissionError: If user doesn't own the project

### execute_project_step <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L349" class="source-link" title="View source code">source</a>

```python
async def execute_project_step(self, user_id: str, project_id: str) -> str
```

Execute a single step of a project.
This is a placeholder for more complex project execution logic.

**Args:**
    user_id (str): The ID of the user executing the project.
    project_id (str): The ID of the project.

**Returns:**
    str: A message indicating the result of the execution step.

### start_run <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L381" class="source-link" title="View source code">source</a>

```python
def start_run(self, project_id: str) -> bool
```

Try to start running a project.
Returns True if run started, False if already running.

### finish_run <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L391" class="source-link" title="View source code">source</a>

```python
def finish_run(self, project_id: str) -> None
```

Mark project run as finished.

## Functions

## get_project_service <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_service.py#L400" class="source-link" title="View source code">source</a>

```python
def get_project_service() -> ProjectService
```

Get the global project service instance
