# Project Registry

*Module: [`vibex.server.project_registry`](https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py)*

User-Task Index Management

Manages the mapping between users and their tasks.
This keeps the framework layer pure and user-agnostic.

## ProjectRegistry <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L30" class="source-link" title="View source code">source</a>

Abstract base class for user-project indexing

### add_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L33" class="source-link" title="View source code">source</a>

```python
async def add_project(self, user_id: str, project_id: str, config_path: Optional[str] = None) -> None
```

Add a task to a user's index

### remove_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L37" class="source-link" title="View source code">source</a>

```python
async def remove_project(self, user_id: str, project_id: str) -> None
```

Remove a task from a user's index

### get_user_projects <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L41" class="source-link" title="View source code">source</a>

```python
async def get_user_projects(self, user_id: str) -> List[str]
```

Get all task IDs for a user

### user_owns_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L45" class="source-link" title="View source code">source</a>

```python
async def user_owns_project(self, user_id: str, project_id: str) -> bool
```

Check if a user owns a specific task

### get_project_owner <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L49" class="source-link" title="View source code">source</a>

```python
async def get_project_owner(self, project_id: str) -> Optional[str]
```

Get the owner of a task

### get_project_info <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L53" class="source-link" title="View source code">source</a>

```python
async def get_project_info(self, project_id: str) -> Optional[dict]
```

Get task information including config_path

## FileProjectRegistry <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L58" class="source-link" title="View source code">source</a>

File-based implementation of user-project index

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L61" class="source-link" title="View source code">source</a>

```python
def __init__(self, base_path: Path = Path('./.vibex/users'))
```
### add_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L126" class="source-link" title="View source code">source</a>

```python
async def add_project(self, user_id: str, project_id: str, config_path: Optional[str] = None) -> None
```

Add a task to a user's index

### remove_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L137" class="source-link" title="View source code">source</a>

```python
async def remove_project(self, user_id: str, project_id: str) -> None
```

Remove a task from a user's index

### get_user_projects <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L148" class="source-link" title="View source code">source</a>

```python
async def get_user_projects(self, user_id: str) -> List[str]
```

Get all task IDs for a user

### user_owns_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L153" class="source-link" title="View source code">source</a>

```python
async def user_owns_project(self, user_id: str, project_id: str) -> bool
```

Check if a user owns a specific task

### get_project_owner <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L158" class="source-link" title="View source code">source</a>

```python
async def get_project_owner(self, project_id: str) -> Optional[str]
```

Get the owner of a task from reverse index

### get_project_info <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L175" class="source-link" title="View source code">source</a>

```python
async def get_project_info(self, project_id: str) -> Optional[dict]
```

Get task information including config_path

## RedisProjectRegistry <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L192" class="source-link" title="View source code">source</a>

Redis-based implementation of user-project index

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L195" class="source-link" title="View source code">source</a>

```python
def __init__(self, redis_url: str = 'redis://localhost:6379')
```
### add_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L207" class="source-link" title="View source code">source</a>

```python
async def add_project(self, user_id: str, project_id: str, config_path: Optional[str] = None) -> None
```

Add a task to a user's index

### remove_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L226" class="source-link" title="View source code">source</a>

```python
async def remove_project(self, user_id: str, project_id: str) -> None
```

Remove a task from a user's index

### get_user_projects <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L240" class="source-link" title="View source code">source</a>

```python
async def get_user_projects(self, user_id: str) -> List[str]
```

Get all task IDs for a user

### user_owns_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L246" class="source-link" title="View source code">source</a>

```python
async def user_owns_project(self, user_id: str, project_id: str) -> bool
```

Check if a user owns a specific task

### get_project_owner <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L251" class="source-link" title="View source code">source</a>

```python
async def get_project_owner(self, project_id: str) -> Optional[str]
```

Get the owner of a task

### get_project_info <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L257" class="source-link" title="View source code">source</a>

```python
async def get_project_info(self, project_id: str) -> Optional[dict]
```

Get task information including config_path

### close <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L274" class="source-link" title="View source code">source</a>

```python
async def close(self)
```

Close Redis connection

## Functions

## get_project_registry <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/project_registry.py#L280" class="source-link" title="View source code">source</a>

```python
def get_project_registry() -> ProjectRegistry
```

Factory function to get the appropriate registry implementation
