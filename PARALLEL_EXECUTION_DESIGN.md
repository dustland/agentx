# Parallel Task Execution Design

## Current Problem

The AgentX framework currently executes tasks sequentially using `get_next_actionable_task()`, which returns only one task at a time. This creates bottlenecks, especially during research phases where multiple independent research tasks could run simultaneously.

## Proposed Solution

### 1. Multi-Task Detection
- Extend `Plan` class with `get_all_actionable_tasks()` method
- Return all tasks that have dependencies satisfied and can run in parallel
- Consider agent availability and resource constraints

### 2. Concurrent Execution Engine
- Modify `XAgent.step()` to handle multiple tasks simultaneously
- Use `asyncio.gather()` or `asyncio.create_task()` for true concurrency
- Implement task batching based on available agents and system resources

### 3. Agent Resource Management
- Track which agents are currently busy
- Allow multiple instances of the same agent type (e.g., multiple researchers)
- Implement agent pooling for high-concurrency scenarios

### 4. Execution Strategies

#### Strategy A: Parallel by Agent Type
```python
# Example: 3 research tasks can run in parallel with different agents
parallel_tasks = [
    {"task": "research_flask", "agent": "researcher_1"},
    {"task": "research_fastapi", "agent": "researcher_2"}, 
    {"task": "research_django", "agent": "researcher_3"}
]
```

#### Strategy B: Same Agent, Multiple Instances
```python
# Example: Same researcher handling multiple topics simultaneously
parallel_tasks = [
    {"task": "research_microservices", "agent": "researcher"},
    {"task": "research_containers", "agent": "researcher"},
    {"task": "research_kubernetes", "agent": "researcher"}
]
```

#### Strategy C: Mixed Parallel Execution
```python
# Example: Different types of tasks running simultaneously
parallel_tasks = [
    {"task": "research_topic_1", "agent": "researcher"},
    {"task": "write_introduction", "agent": "writer"},
    {"task": "create_outline", "agent": "writer"}
]
```

### 5. Implementation Plan

1. **Phase 1: Basic Parallel Detection**
   - Add `get_all_actionable_tasks()` to Plan class
   - Modify XAgent to detect parallel opportunities

2. **Phase 2: Concurrent Execution**
   - Implement parallel task execution in XAgent
   - Add progress tracking for multiple concurrent tasks

3. **Phase 3: Advanced Features**
   - Agent pooling and resource management
   - Dynamic batching based on system load
   - Intelligent dependency resolution

### 6. Expected Benefits

- **Research Phase**: 3-5x faster execution for independent research tasks
- **Writing Phase**: Parallel section writing when dependencies allow
- **Overall Workflow**: Reduced total execution time from ~5 minutes to ~2 minutes
- **Resource Utilization**: Better use of available CPU and API concurrency limits

### 7. Configuration Options

```yaml
# In team.yaml
execution:
  parallel_enabled: true
  max_concurrent_tasks: 5
  agent_pooling:
    researcher: 3  # Allow 3 concurrent researcher instances
    writer: 2      # Allow 2 concurrent writer instances
  batch_strategy: "mixed"  # or "by_agent_type", "same_agent"
```

### 8. Compatibility

- Maintain backward compatibility with existing sequential execution
- Add parallel execution as an opt-in feature
- Graceful degradation when resources are limited