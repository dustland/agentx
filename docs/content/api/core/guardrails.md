# Guardrails

*Module: [`vibex.core.guardrails`](https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py)*

Guardrails Engine - Comprehensive Safety and Compliance System

This module implements multi-layered safety mechanisms including input validation,
output filtering, rate limiting, content safety, and policy compliance checks.

## GuardrailContext <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L27" class="source-link" title="View source code">source</a>

Context information for guardrail checks.

## RateLimitState <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L37" class="source-link" title="View source code">source</a>

Rate limiting state tracking.

## GuardrailRule <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L44" class="source-link" title="View source code">source</a>

Abstract base class for guardrail rules.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L47" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str, severity: str = 'medium', action: str = 'warn')
```
### check <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L53" class="source-link" title="View source code">source</a>

```python
async def check(self, content: str, context: GuardrailContext) -> GuardrailCheck
```

Check content against this rule.

## InputValidationRule <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L58" class="source-link" title="View source code">source</a>

Input validation rule for sanitizing user inputs.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L61" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str, patterns: List[str])
```
### check <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L65" class="source-link" title="View source code">source</a>

```python
async def check(self, content: str, context: GuardrailContext) -> GuardrailCheck
```

Check input against validation patterns.

## ContentFilterRule <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L88" class="source-link" title="View source code">source</a>

Content filtering rule for blocking inappropriate content.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L91" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str, keywords: List[str])
```
### check <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L95" class="source-link" title="View source code">source</a>

```python
async def check(self, content: str, context: GuardrailContext) -> GuardrailCheck
```

Check content for inappropriate keywords.

## RateLimitRule <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L119" class="source-link" title="View source code">source</a>

Rate limiting rule for preventing abuse.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L122" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str, max_requests: int, window_seconds: int)
```
### check <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L128" class="source-link" title="View source code">source</a>

```python
async def check(self, content: str, context: GuardrailContext) -> GuardrailCheck
```

Check rate limits for the agent.

## ContentSafetyRule <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L168" class="source-link" title="View source code">source</a>

Content safety rule using pattern matching and heuristics.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L171" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str, safety_patterns: List[str])
```
### check <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L175" class="source-link" title="View source code">source</a>

```python
async def check(self, content: str, context: GuardrailContext) -> GuardrailCheck
```

Check content for safety violations.

## ComplianceRule <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L198" class="source-link" title="View source code">source</a>

Compliance rule for organizational and regulatory requirements.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L201" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str, compliance_checks: List[Dict[str, Any]])
```
### check <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L205" class="source-link" title="View source code">source</a>

```python
async def check(self, content: str, context: GuardrailContext) -> GuardrailCheck
```

Check content for compliance violations.

## GuardrailEngine <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L244" class="source-link" title="View source code">source</a>

Comprehensive guardrails engine for safety and compliance.

Implements multi-layered safety mechanisms including input validation,
output filtering, rate limiting, content safety, and policy compliance.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L252" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### add_policy <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L286" class="source-link" title="View source code">source</a>

```python
def add_policy(self, policy: GuardrailPolicy)
```

Add a guardrail policy to the engine.

### check_content <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L348" class="source-link" title="View source code">source</a>

```python
async def check_content(self, content: str, context: GuardrailContext, policy_names: Optional[List[str]] = None) -> GuardrailPart
```

Check content against guardrail policies.

**Args:**
    content: Content to check
    context: Context information
    policy_names: Specific policies to check (None for all applicable)

**Returns:**
    GuardrailPart with check results

### should_block_content <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L452" class="source-link" title="View source code">source</a>

```python
def should_block_content(self, guardrail_part: GuardrailPart) -> bool
```

Determine if content should be blocked based on guardrail results.

### get_policy_names <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L459" class="source-link" title="View source code">source</a>

```python
def get_policy_names(self) -> List[str]
```

Get list of available policy names.

### get_policy_stats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L463" class="source-link" title="View source code">source</a>

```python
def get_policy_stats(self) -> Dict[str, Any]
```

Get statistics about guardrail policies and checks.

## Functions

## get_guardrail_engine <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L476" class="source-link" title="View source code">source</a>

```python
def get_guardrail_engine() -> GuardrailEngine
```

Get the global guardrail engine instance.

## check_content_safety <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/guardrails.py#L484" class="source-link" title="View source code">source</a>

```python
async def check_content_safety(content: str, agent_name: str, policy_names: Optional[List[str]] = None, project_id: Optional[str] = None, step_id: Optional[str] = None) -> GuardrailPart
```

Convenience function to check content safety.

**Args:**
    content: Content to check
    agent_name: Name of the agent
    policy_names: Specific policies to check
    project_id: Optional task ID
    step_id: Optional step ID

**Returns:**
    GuardrailPart with check results
