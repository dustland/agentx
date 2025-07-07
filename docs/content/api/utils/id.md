# ID Utilities

*Module: [`agentx.utils.id`](https://github.com/dustland/agentx/blob/main/src/agentx/utils/id.py)*

ID generation utilities for AgentX.

## generate_short_id <a href="https://github.com/dustland/agentx/blob/main/src/agentx/utils/id.py#L8" class="source-link" title="View source code">source</a>

```python
def generate_short_id(length: int = 8) -> str
```

Generate a short, URL-friendly, cryptographically secure random ID.

**Args:**
    length (int): The desired length of the ID. Defaults to 8.

**Returns:**
    str: A new short ID.
