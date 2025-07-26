# Xagent Service

*Module: [`vibex.server.xagent_service`](https://github.com/dustland/vibex/blob/main/src/vibex/server/xagent_service.py)*

XAgent Service Layer

Manages XAgent instances and provides the service interface for the REST API.
XAgent is the primary interface - each instance represents exactly one project.

## XAgentService <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/xagent_service.py#L23" class="source-link" title="View source code">source</a>

Service for managing XAgent instances.

XAgent is the primary interface to VibeX. Each XAgent instance represents
exactly one project and uses the project's ID as its identifier.

### create <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/xagent_service.py#L31" class="source-link" title="View source code">source</a>

```python
async def create(self, user_id: Optional[str] = None, goal: str = '', config_path: str = '', context: Optional[dict] = None) -> XAgent
```

Creates a new XAgent instance.

Returns the actual XAgent instance, not a DTO wrapper.
The XAgent manages its own project internally.

### get <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/xagent_service.py#L68" class="source-link" title="View source code">source</a>

```python
async def get(self, agent_id: str) -> XAgent
```

Get an XAgent instance by ID.

Returns the actual XAgent instance for direct interaction.
Uses lazy loading - if not in memory, tries to load from filesystem.

### list_for_user <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/xagent_service.py#L105" class="source-link" title="View source code">source</a>

```python
async def list_for_user(self, user_id: Optional[str] = None) -> list[XAgent]
```

Get all XAgent instances for a specific user.
**Note:** This is a simplified in-memory implementation.

### delete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/xagent_service.py#L114" class="source-link" title="View source code">source</a>

```python
async def delete(self, agent_id: str) -> bool
```

Delete an XAgent instance.

### exists <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/xagent_service.py#L124" class="source-link" title="View source code">source</a>

```python
def exists(self, agent_id: str) -> bool
```

Check if an XAgent instance exists.

## Functions

## get_xagent_service <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/xagent_service.py#L134" class="source-link" title="View source code">source</a>

```python
def get_xagent_service() -> XAgentService
```