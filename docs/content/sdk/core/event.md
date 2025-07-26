# Event System

*Module: [`vibex.core.event`](https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py)*

## StreamChunk <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L15" class="source-link" title="View source code">source</a>

Channel 1: Low-latency token stream for UI updates.

## TaskStartEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L25" class="source-link" title="View source code">source</a>

Task execution started.

## TaskCompleteEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L34" class="source-link" title="View source code">source</a>

Task execution completed.

## TaskPausedEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L45" class="source-link" title="View source code">source</a>

Task execution paused.

## TaskResumedEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L53" class="source-link" title="View source code">source</a>

Task execution resumed.

## AgentStartEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L62" class="source-link" title="View source code">source</a>

Agent turn started.

## AgentCompleteEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L71" class="source-link" title="View source code">source</a>

Agent turn completed.

## AgentHandoffEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L81" class="source-link" title="View source code">source</a>

Agent handoff occurred.

## ParallelExecutionStartEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L92" class="source-link" title="View source code">source</a>

Parallel execution started.

## ParallelExecutionSyncEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L100" class="source-link" title="View source code">source</a>

Parallel execution sync point reached.

## ConsensusProposalEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L108" class="source-link" title="View source code">source</a>

Consensus proposal made.

## ConsensusVoteEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L117" class="source-link" title="View source code">source</a>

Consensus vote cast.

## ConsensusReachedEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L126" class="source-link" title="View source code">source</a>

Consensus reached.

## ToolCallEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L135" class="source-link" title="View source code">source</a>

Tool call initiated.

## ToolResultEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L143" class="source-link" title="View source code">source</a>

Tool call completed.

## MemoryStoreEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L152" class="source-link" title="View source code">source</a>

Memory stored.

## MemoryRetrieveEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L161" class="source-link" title="View source code">source</a>

Memory retrieved.

## MemoryConsolidateEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L170" class="source-link" title="View source code">source</a>

Memory consolidated.

## HITLRequestEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L179" class="source-link" title="View source code">source</a>

Human-in-the-loop request made.

## HITLResponseEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L189" class="source-link" title="View source code">source</a>

Human-in-the-loop response received.

## GuardrailViolationEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L199" class="source-link" title="View source code">source</a>

Guardrail policy violation.

## GuardrailPolicyUpdateEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L211" class="source-link" title="View source code">source</a>

Guardrail policy updated.

## ArtifactCreatedEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L220" class="source-link" title="View source code">source</a>

Artifact created.

## ArtifactModifiedEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L227" class="source-link" title="View source code">source</a>

Artifact modified.

## ArtifactVersionedEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L236" class="source-link" title="View source code">source</a>

Artifact versioned.

## ErrorEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L246" class="source-link" title="View source code">source</a>

Error occurred.

## RecoveryEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L258" class="source-link" title="View source code">source</a>

Error recovery attempted.

## BreakpointHitEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L268" class="source-link" title="View source code">source</a>

Breakpoint hit during execution.

## UserInterventionEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L277" class="source-link" title="View source code">source</a>

User intervention occurred.

## HealthCheckEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L287" class="source-link" title="View source code">source</a>

System health check result.

## PerformanceMetricEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/event.py#L295" class="source-link" title="View source code">source</a>

Performance metric recorded.
