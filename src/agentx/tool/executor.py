"""
Tool executor for secure and performant tool execution.

The executor is responsible for:
- Secure tool execution with validation
- Performance monitoring and resource limits
- Error handling and result formatting
- Security policies and audit logging
"""

import time
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from dataclasses import asdict, is_dataclass
from ..utils.logger import get_logger
from .registry import ToolRegistry, get_tool_registry
from ..core.tool import ToolResult

logger = get_logger(__name__)


def safe_json_serialize(obj):
    """
    Safely serialize objects to JSON, handling dataclasses, Pydantic models, and other complex types.
    """
    if is_dataclass(obj):
        return asdict(obj)
    elif hasattr(obj, 'model_dump'):  # Pydantic model
        return obj.model_dump()
    elif hasattr(obj, '__dict__'):  # Regular object with attributes
        return obj.__dict__
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: safe_json_serialize(value) for key, value in obj.items()}
    else:
        # For primitive types and other serializable objects
        return obj


def safe_json_dumps(obj, **kwargs):
    """
    Safely serialize objects to JSON with fallback handling.
    """
    try:
        return json.dumps(safe_json_serialize(obj), **kwargs)
    except (TypeError, ValueError) as e:
        # Fallback: convert to string representation
        return json.dumps(str(obj), **kwargs)


def truncate_for_logging(content: str, max_length: int = 500) -> str:
    """
    Truncate content for logging purposes while preserving readability.

    Args:
        content: Content to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated content with ellipsis if needed
    """
    if len(content) <= max_length:
        return content

    truncated = content[:max_length].strip()
    return f"{truncated}... [truncated {len(content) - max_length} chars]"


def safe_json_dumps_for_logging(obj, max_content_length: int = 500, **kwargs):
    """
    Safely serialize objects to JSON with content truncation for logging.

    Args:
        obj: Object to serialize
        max_content_length: Maximum length for content fields before truncation
        **kwargs: Additional JSON serialization arguments

    Returns:
        JSON string with truncated content for logging
    """
    try:
        # Create a copy for logging that truncates large content
        logging_obj = _truncate_content_for_logging(obj, max_content_length)
        return json.dumps(safe_json_serialize(logging_obj), **kwargs)
    except (TypeError, ValueError) as e:
        # Fallback: convert to string representation
        return json.dumps(str(obj), **kwargs)


def _truncate_content_for_logging(obj, max_length: int):
    """
    Recursively truncate content in objects for logging purposes.

    Args:
        obj: Object to process
        max_length: Maximum length for content fields

    Returns:
        Object with truncated content
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if isinstance(value, str):
                # Truncate ANY string field that's too long, not just specific field names
                # This handles cases like 'title' fields containing large JSON strings
                if len(value) > max_length:
                    result[key] = truncate_for_logging(value, max_length)
                else:
                    result[key] = value
            elif isinstance(value, (dict, list)):
                result[key] = _truncate_content_for_logging(value, max_length)
            else:
                result[key] = value
        return result
    elif isinstance(obj, list):
        return [_truncate_content_for_logging(item, max_length) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle objects with attributes (like WebContent)
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, str):
                # Truncate ANY string field that's too long, not just specific field names
                if len(value) > max_length:
                    result[key] = truncate_for_logging(value, max_length)
                else:
                    result[key] = value
            elif isinstance(value, (dict, list)):
                result[key] = _truncate_content_for_logging(value, max_length)
            else:
                result[key] = value
        return result
    else:
        # For primitive types and other objects, return as-is
        return obj


class SecurityPolicy:
    """Security policies for tool execution."""

    # Resource limits
    MAX_EXECUTION_TIME = 60.0  # seconds
    MAX_TOOLS_PER_BATCH = 10
    MAX_CONCURRENT_EXECUTIONS = 3

    # Note: Tool permissions are now controlled by agent configurations
    # Builtin tools are allowed by default since they're designed to be safe
    # Agent configs in presets/config.yaml control what tools are available to each agent

    # Blocked tools (never allowed)
    BLOCKED_TOOLS = [
        "system_command", "exec", "eval", "delete_all"
    ]


class ToolExecutor:
    """
    Secure tool executor with performance monitoring and security policies.

    This class handles the actual execution of tools with:
    - Security validation and permissions
    - Resource limits and monitoring
    - Error handling and logging
    - Audit trails
    """

    def __init__(self, registry: Optional[ToolRegistry] = None):
        """
        Initialize tool executor.

        Args:
            registry: Tool registry to use (defaults to global registry)
        """
        self.registry = registry or get_tool_registry()
        self.security_policy = SecurityPolicy()
        self.active_executions = 0
        self.execution_history: List[Dict[str, Any]] = []

        logger.info("🔧 ToolExecutor initialized with security policies")

    async def execute_tool(
        self,
        tool_name: str,
        agent_name: str = "default",
        **kwargs
    ) -> ToolResult:
        """
        Execute a single tool with security validation.

        Args:
            tool_name: Name of the tool to execute
            agent_name: Name of the agent requesting execution (for permissions)
            **kwargs: Tool arguments

        Returns:
            ToolResult with execution outcome
        """
        start_time = time.time()

        try:
            # Security validation
            validation_result = self._validate_execution(tool_name, agent_name, kwargs)
            if not validation_result.success:
                return validation_result

            # Resource limit check
            if self.active_executions >= self.security_policy.MAX_CONCURRENT_EXECUTIONS:
                return ToolResult(
                    success=False,
                    error="Maximum concurrent executions exceeded",
                    execution_time=time.time() - start_time
                )

            # Get tool function
            tool_function = self.registry.get_tool_function(tool_name)
            if not tool_function:
                return ToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' not found in registry",
                    execution_time=time.time() - start_time
                )

            # Execute with monitoring
            self.active_executions += 1
            try:
                result = await self._execute_with_timeout(
                    tool_function.function,
                    kwargs,
                    self.security_policy.MAX_EXECUTION_TIME
                )

                execution_time = time.time() - start_time

                # Log successful execution
                self._log_execution(tool_name, agent_name, kwargs, True, execution_time)

                return ToolResult(
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    metadata={
                        "tool_name": tool_name,
                        "agent_name": agent_name
                    }
                )

            finally:
                self.active_executions -= 1

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tool execution timed out after {self.security_policy.MAX_EXECUTION_TIME}s"
            self._log_execution(tool_name, agent_name, kwargs, False, execution_time, error_msg)

            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tool execution failed: {str(e)}"
            self._log_execution(tool_name, agent_name, kwargs, False, execution_time, error_msg)

            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

    async def execute_tools(
        self,
        tool_calls: List[Any],
        agent_name: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls and return formatted results for LLM.

        Args:
            tool_calls: List of tool call objects from LLM response
            agent_name: Name of the agent requesting execution

        Returns:
            List of tool result messages formatted for LLM conversation
        """
        # Validate batch size
        if len(tool_calls) > self.security_policy.MAX_TOOLS_PER_BATCH:
            error_msg = f"Too many tool calls: {len(tool_calls)} > {self.security_policy.MAX_TOOLS_PER_BATCH}"
            logger.error(error_msg)

            # Return error for all tool calls
            return [
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tc.function.name,
                    "content": safe_json_dumps({
                        "success": False,
                        "error": error_msg
                    })
                } for tc in tool_calls
            ]

        tool_messages = []

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id
            try:
                # Parse tool arguments
                tool_args = json.loads(tool_call.function.arguments)

                # Log tool call (framework logging - respects streaming mode)
                logger.info(f"🔧 TOOL CALL START | ID: {tool_call_id} | Tool: {tool_name} | Agent: {agent_name}")
                logger.info(f"📝 TOOL ARGS | {safe_json_dumps(tool_args, indent=2)}")

                # Execute the tool
                start_time = time.time()
                result = await self.execute_tool(tool_name, agent_name, **tool_args)
                execution_time = time.time() - start_time

                # Log tool call result (framework logging - respects streaming mode)
                if result.success:
                    logger.info(f"✅ TOOL CALL SUCCESS | ID: {tool_call_id} | Tool: {tool_name} | Time: {execution_time:.2f}s")
                    # Use truncated logging for large content like web extractions
                    logger.info(f"📤 TOOL RESULT | {safe_json_dumps_for_logging(result.result, max_content_length=500)}")
                else:
                    logger.info(f"❌ TOOL CALL FAILED | ID: {tool_call_id} | Tool: {tool_name} | Error: {result.error}")
                    logger.info(f"⏱️  TOOL TIME | {execution_time:.2f}s")

                # Format result for LLM using safe serialization (FULL CONTENT - no truncation)
                if result.success:
                    content = safe_json_dumps({
                        "success": True,
                        "result": result.result,
                        "execution_time": result.execution_time,
                        "metadata": result.metadata
                    }, ensure_ascii=False, indent=2)
                else:
                    content = safe_json_dumps({
                        "success": False,
                        "error": result.error,
                        "execution_time": result.execution_time
                    }, ensure_ascii=False, indent=2)

            except json.JSONDecodeError as e:
                logger.error(f"❌ TOOL CALL PARSE ERROR | ID: {tool_call_id} | Tool: {tool_name} | Error: Invalid JSON arguments")
                logger.error(f"🔍 RAW ARGS | {tool_call.function.arguments}")
                content = safe_json_dumps({
                    "success": False,
                    "error": f"Invalid tool arguments: {str(e)}"
                })

            except Exception as e:
                logger.error(f"❌ TOOL CALL EXCEPTION | ID: {tool_call_id} | Tool: {tool_name} | Error: {str(e)}")
                content = safe_json_dumps({
                    "success": False,
                    "error": f"Tool execution failed: {str(e)}"
                })

            # Add tool result message
            tool_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": content
            })

        # Log batch summary
        successful_calls = sum(1 for msg in tool_messages if '"success": true' in msg["content"])
        failed_calls = len(tool_messages) - successful_calls
        logger.info(f"📊 TOOL BATCH COMPLETE | Agent: {agent_name} | Total: {len(tool_messages)} | Success: {successful_calls} | Failed: {failed_calls}")

        return tool_messages

    def _validate_execution(
        self,
        tool_name: str,
        agent_name: str,
        kwargs: Dict[str, Any]
    ) -> ToolResult:
        """
        Validate tool execution request against security policies.

        Args:
            tool_name: Tool to execute
            agent_name: Agent requesting execution
            kwargs: Tool arguments

        Returns:
            ToolResult indicating validation success/failure
        """
        # Check if tool is blocked
        if tool_name in self.security_policy.BLOCKED_TOOLS:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' is blocked by security policy"
            )

        # Allow all builtin tools by default - agent configs control what's available
        # This removes the confusing dual-permission system
        return ToolResult(success=True)

    async def _execute_with_timeout(
        self,
        func,
        kwargs: Dict[str, Any],
        timeout: float
    ):
        """
        Execute function with timeout.

        Args:
            func: Function to execute
            kwargs: Function arguments
            timeout: Timeout in seconds

        Returns:
            Function result

        Raises:
            asyncio.TimeoutError: If execution exceeds timeout
        """
        if asyncio.iscoroutinefunction(func):
            # Async function
            return await asyncio.wait_for(func(**kwargs), timeout=timeout)
        else:
            # Sync function - run in thread pool
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(None, lambda: func(**kwargs)),
                timeout=timeout
            )

    def _log_execution(
        self,
        tool_name: str,
        agent_name: str,
        kwargs: Dict[str, Any],
        success: bool,
        execution_time: float,
        error: Optional[str] = None
    ):
        """
        Log tool execution for audit trail.

        Args:
            tool_name: Tool that was executed
            agent_name: Agent that requested execution
            kwargs: Tool arguments
            success: Whether execution succeeded
            execution_time: Time taken for execution
            error: Error message if failed
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "agent_name": agent_name,
            "arguments": kwargs,
            "success": success,
            "execution_time": execution_time,
            "error": error
        }

        self.execution_history.append(log_entry)

        # Keep only last 1000 entries to prevent memory bloat
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]

        # Log to file/external system if needed
        if success:
            logger.debug(f"✅ Tool '{tool_name}' executed successfully for '{agent_name}' in {execution_time:.2f}s")
        else:
            logger.debug(f"❌ Tool '{tool_name}' failed for '{agent_name}': {error}")

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for entry in self.execution_history if entry["success"])

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failure_rate": (total_executions - successful_executions) / max(total_executions, 1),
            "active_executions": self.active_executions,
            "recent_executions": self.execution_history[-10:] if self.execution_history else []
        }

    def clear_history(self):
        """Clear execution history."""
        self.execution_history.clear()
        logger.debug("Tool execution history cleared")
