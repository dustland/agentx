# Project

*Module: [`vibex.core.project`](https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py)*

Project module - the top-level container for VibeX work.

A Project represents a complete body of work that may involve multiple tasks,
agents, and execution steps. Each project is managed by an XAgent that serves
as its conversational representative.

Key concepts:
- Project: The overall work container (e.g., "Build a web app")
- Task: Individual execution units within a project (e.g., "Create backend API")
- TaskStep: Specific actions within a task (e.g., "Write authentication endpoint")

Example:
    # Start a new project
    project = await start_project(
        goal="Build a documentation website",
        config_path="config/team.yaml"
    )

    # The project's X agent manages execution
    response = await project.x_agent.chat("Make it mobile-friendly")

## Project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L49" class="source-link" title="View source code">source</a>
### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L50" class="source-link" title="View source code">source</a>

```python
def __init__(self, project_id: str, config: ProjectConfig, history: ConversationHistory, message_queue: MessageQueue, agents: Dict[str, Agent], storage: ProjectStorage, initial_goal: str, x_agent: Optional['XAgent'] = None)
```
### get_agent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L75" class="source-link" title="View source code">source</a>

```python
def get_agent(self, name: str) -> Agent
```
### complete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L80" class="source-link" title="View source code">source</a>

```python
def complete(self)
```
### get_context <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L84" class="source-link" title="View source code">source</a>

```python
def get_context(self) -> Dict[str, Any]
```
### create_plan <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L104" class="source-link" title="View source code">source</a>

```python
async def create_plan(self, plan: Plan) -> None
```
### update_plan <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L109" class="source-link" title="View source code">source</a>

```python
async def update_plan(self, plan: Plan) -> None
```
### get_next_task <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L115" class="source-link" title="View source code">source</a>

```python
async def get_next_task(self) -> Optional[Task]
```
### get_parallel_tasks <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L120" class="source-link" title="View source code">source</a>

```python
async def get_parallel_tasks(self, max_tasks: int = 3) -> List[Task]
```

Get tasks that can be executed in parallel.

### update_project_status <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L126" class="source-link" title="View source code">source</a>

```python
async def update_project_status(self, project_id: str, status: TaskStatus) -> bool
```

Update the status of a task and persist the plan.

### assign_task_to_agent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L139" class="source-link" title="View source code">source</a>

```python
async def assign_task_to_agent(self, task_id: str, agent_name: str) -> bool
```

Assign a task to a specific agent.

### is_plan_complete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L158" class="source-link" title="View source code">source</a>

```python
def is_plan_complete(self) -> bool
```

Check if all tasks in the plan are completed.

### has_failed_tasks <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L164" class="source-link" title="View source code">source</a>

```python
def has_failed_tasks(self) -> bool
```
### load_project_state <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L181" class="source-link" title="View source code">source</a>

```python
async def load_project_state(self) -> bool
```
### load_plan <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L200" class="source-link" title="View source code">source</a>

```python
async def load_plan(self) -> Optional[Plan]
```
### get_summary <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L205" class="source-link" title="View source code">source</a>

```python
def get_summary(self) -> Dict[str, Any]
```
## Functions

## start_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L232" class="source-link" title="View source code">source</a>

```python
async def start_project(goal: str, config_path: Union[str, Path, TeamConfig], project_id: Optional[str] = None, workspace_dir: Optional[Path] = None) -> Project
```
## run_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L305" class="source-link" title="View source code">source</a>

```python
async def run_project(goal: str, config_path: Union[str, Path, TeamConfig], project_id: Optional[str] = None) -> AsyncGenerator[Message, None]
```
## resume_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L326" class="source-link" title="View source code">source</a>

```python
async def resume_project(project_id: str, config_path: Union[str, Path, TeamConfig]) -> Project
```
## main <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/project.py#L419" class="source-link" title="View source code">source</a>

```python
async def main()
```

Main function for testing.
