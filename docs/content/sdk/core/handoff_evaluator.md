# Handoff Evaluator

*Module: [`vibex.core.handoff_evaluator`](https://github.com/dustland/vibex/blob/main/src/vibex/core/handoff_evaluator.py)*

Handoff evaluation system for XAgent orchestration.

This module provides intelligent handoff evaluation without requiring agents
to explicitly call handoff tools. XAgent evaluates conditions and makes
routing decisions centrally.

## HandoffContext <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/handoff_evaluator.py#L19" class="source-link" title="View source code">source</a>

Context for evaluating handoff conditions.

## HandoffEvaluator <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/handoff_evaluator.py#L28" class="source-link" title="View source code">source</a>

Evaluates handoff conditions and determines next agent.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/handoff_evaluator.py#L31" class="source-link" title="View source code">source</a>

```python
def __init__(self, handoffs: List[Handoff], agents: Dict[str, Agent])
```
### evaluate_handoffs <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/handoff_evaluator.py#L48" class="source-link" title="View source code">source</a>

```python
async def evaluate_handoffs(self, context: HandoffContext) -> Optional[str]
```

Evaluate if a handoff should occur based on current context.
Returns the target agent name if handoff should occur, None otherwise.

### get_fallback_agent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/handoff_evaluator.py#L139" class="source-link" title="View source code">source</a>

```python
def get_fallback_agent(self, current_agent: str) -> Optional[str]
```

Get a fallback agent if no conditions are met but work continues.
