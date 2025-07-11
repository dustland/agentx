from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from .brain import Brain
from .config import AgentConfig, BrainConfig
from .tool import Tool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AgentState(BaseModel):
    """Current state of an agent during execution."""
    agent_name: str
    current_step_id: Optional[str] = None
    is_active: bool = False
    last_response: Optional[str] = None
    last_response_timestamp: Optional[datetime] = None
    tool_calls_made: int = 0
    tokens_used: int = 0
    errors_encountered: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Agent:
    """
    Represents an autonomous agent that manages its own conversation flow.

    Key Principles:
    - Each agent is autonomous and manages its own conversation flow
    - Agents communicate with other agents through public interfaces only
    - The brain is private to the agent - no external access
    - Tool execution is handled through the injected tool manager

    This combines:
    - AgentConfig (configuration data)
    - Brain (private LLM interaction)
    - Conversation management with integrated tool execution
    """

    def __init__(self, config: AgentConfig, tool_manager=None):
        """
        Initialize agent with configuration and optional tool manager.

        Args:
            config: Agent configuration
            tool_manager: Optional tool manager (injected by TaskExecutor)
        """
        # Core configuration
        self.config = config
        self.name = config.name
        self.description = config.description
        self.tools = config.tools or []
        self.memory_enabled = getattr(config, 'memory_enabled', True)  # Default to True if not specified
        self.max_iterations = getattr(config, 'max_iterations', 10)  # Default to 10 if not specified

        # State management
        self.state = AgentState(agent_name=self.name)

        # Initialize brain with agent's brain config or default
        self.brain: Brain = self._initialize_brain(config)

        # Tool management (injected by TaskExecutor for task isolation)
        self.tool_manager = tool_manager

        logger.info(f"🤖 Agent '{self.name}' initialized with {len(self.tools)} tools")

    def _initialize_brain(self, config: AgentConfig) -> Brain:
        """Initialize the brain with the agent's configuration."""
        # Use agent's brain_config if available, otherwise use default
        brain_config = config.brain_config or BrainConfig()
        return Brain.from_config(brain_config)

    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text using a simple approximation.
        More accurate than character count but not perfect.
        """
        # Simple approximation: ~4 characters per token for most text
        # This is conservative and works reasonably well for most content
        return len(text) // 4

    def _count_message_tokens(self, message: Dict[str, Any]) -> int:
        """Count tokens in a single message."""
        total_tokens = 0

        # Count content tokens
        if message.get("content"):
            total_tokens += self._estimate_token_count(message["content"])

        # Count tool call tokens (if any)
        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                if tool_call.get("function", {}).get("name"):
                    total_tokens += self._estimate_token_count(tool_call["function"]["name"])
                if tool_call.get("function", {}).get("arguments"):
                    total_tokens += self._estimate_token_count(tool_call["function"]["arguments"])

        # Add overhead for message formatting
        total_tokens += 10  # Rough estimate for role, timestamps, etc.

        return total_tokens

    def _truncate_conversation_history(self, messages: List[Dict[str, Any]], max_tokens: int) -> List[Dict[str, Any]]:
        """
        Truncate conversation history to stay within token limit.

        Strategy:
        1. Always keep the most recent user message
        2. Keep recent assistant responses and tool interactions
        3. Remove older messages when approaching limit
        """
        if not messages:
            return messages

        # Count tokens in messages from newest to oldest
        truncated_messages = []
        current_tokens = 0

        # Reserve tokens for system prompt and response (more reasonable)
        reserved_tokens = min(max_tokens // 4, 1000)  # Reserve 25% or 1000 tokens, whichever is smaller
        effective_max = max_tokens - reserved_tokens

        # Always keep the most recent user message first
        most_recent_user = None
        for message in reversed(messages):
            if message.get("role") == "user":
                most_recent_user = message
                break

        if most_recent_user:
            truncated_messages.append(most_recent_user)
            current_tokens += self._count_message_tokens(most_recent_user)

        # Process remaining messages in reverse order (newest first), skipping the most recent user message
        for message in reversed(messages):
            # Skip the most recent user message as we already added it
            if most_recent_user and message is most_recent_user:
                continue

            message_tokens = self._count_message_tokens(message)

            # Check if adding this message would exceed limit
            if current_tokens + message_tokens > effective_max:
                # Stop adding messages if we exceed the limit
                break
            else:
                # Add this message at the beginning (since we're processing in reverse)
                truncated_messages.insert(0, message)
                current_tokens += message_tokens

        original_count = len(messages)
        truncated_count = len(truncated_messages)

        if truncated_count < original_count:
            logger.warning(f"Truncated conversation history from {original_count} to {truncated_count} messages "
                          f"(~{current_tokens} tokens) to stay within {max_tokens} token limit")

        return truncated_messages

    def get_max_context_tokens(self) -> int:
        """Get the maximum context tokens for this agent."""
        # Check if agent has memory config with max_context_tokens
        if hasattr(self.config, 'memory_config') and self.config.memory_config:
            return getattr(self.config.memory_config, 'max_context_tokens', 32000)

        # Check if there's a team memory config available (passed during initialization)
        if hasattr(self, 'team_memory_config') and self.team_memory_config:
            return getattr(self.team_memory_config, 'max_context_tokens', 32000)

        # Default to 32000 tokens (safe for most models)
        return 32000

    def get_tools_json(self) -> List[Dict[str, Any]]:
        """Get the JSON schemas for the tools available to this agent."""
        if not self.tool_manager:
            return []

        # Always include all builtin tools for this agent
        builtin_tools = self.tool_manager.get_builtin_tools()

        # Add custom tools from agent config (if any)
        tools_to_include = builtin_tools.copy()
        if self.tools:
            for tool_name in self.tools:
                if tool_name not in tools_to_include:
                    # Only add if it's actually registered
                    all_available = self.tool_manager.list_tools()
                    if tool_name in all_available:
                        tools_to_include.append(tool_name)

        # Return schemas for all included tools
        return self.tool_manager.get_tool_schemas(tools_to_include)

    # ============================================================================
    # PUBLIC AGENT INTERFACE - Same as Brain interface for consistency
    # ============================================================================

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        max_tool_rounds: int = 10
    ) -> str:
        """
        Generate response with tool execution.

        This is a simpler, non-streaming version that returns the final response.

        Args:
            messages: Conversation messages in LLM format
            system_prompt: Optional system prompt override
            max_tool_rounds: Maximum tool execution rounds

        Returns:
            Final response string
        """
        self.state.is_active = True
        try:
            # Check if brain config has streaming setting
            if hasattr(self.brain.config, 'streaming') and not self.brain.config.streaming:
                return await self._generate_response_non_streaming(
                    messages, system_prompt, max_tool_rounds
                )

            # Use streaming mode (existing behavior)
            response_parts = []
            async for chunk in self._streaming_loop(messages, system_prompt, max_tool_rounds):
                if isinstance(chunk, dict) and chunk.get("type") == "content":
                    response_parts.append(chunk.get("content", ""))
                elif isinstance(chunk, str):
                    response_parts.append(chunk)
            return "".join(response_parts)
        finally:
            self.state.is_active = False

    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        max_tool_rounds: int = 10
    ) -> AsyncGenerator[str, None]:
        """
        Stream response with tool execution.

        This matches Brain's interface but includes tool execution loop.

        Args:
            messages: Conversation messages in LLM format
            system_prompt: Optional system prompt override
            max_tool_rounds: Maximum tool execution rounds

        Yields:
            Response chunks and tool execution status updates
        """
        self.state.is_active = True
        try:
            async for chunk in self._streaming_loop(messages, system_prompt, max_tool_rounds):
                yield chunk
        finally:
            self.state.is_active = False

    # ============================================================================
    # CONVERSATION MANAGEMENT - Handles tool execution
    # ============================================================================

    async def _conversation_loop(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str],
        max_tool_rounds: int = 10
    ) -> str:
        """
        Conversation loop with tool execution.

        Agent generates responses and executes tools as needed.
        """
        conversation = messages.copy()

        for round_num in range(max_tool_rounds):
            # Always show conversation state
            print(f"🧠 AGENT ROUND {round_num + 1} | Agent: {self.name} | Messages: {len(conversation)}")

            # Truncate conversation history if needed
            max_tokens = self.get_max_context_tokens()
            truncated_conversation = self._truncate_conversation_history(conversation, max_tokens)

            # Get response from brain
            llm_response = await self.brain.generate_response(
                messages=truncated_conversation,
                system_prompt=system_prompt,
                tools=self.get_tools_json()
            )

            # Always show LLM response
            if llm_response.content:
                print(f"💬 AGENT RESPONSE | Agent: {self.name} | Content: {llm_response.content[:200]}{'...' if len(llm_response.content) > 200 else ''}")

            # Check if brain wants to call tools
            if llm_response.tool_calls:
                logger.debug(f"Agent '{self.name}' requesting {len(llm_response.tool_calls)} tool calls in round {round_num + 1}")

                # Add assistant's message with tool calls
                conversation.append({
                    "role": "assistant",
                    "content": llm_response.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in llm_response.tool_calls
                    ]
                })

                # Execute tools - use injected ToolExecutor from TaskExecutor
                tool_messages = await self.tool_manager.execute_tools(llm_response.tool_calls, self.name)
                conversation.extend(tool_messages)

                # Continue to next round
                continue
            else:
                # No tool calls, return final response
                return llm_response.content or ""

        # Max rounds exceeded
        logger.warning(f"Agent '{self.name}' exceeded maximum tool execution rounds ({max_tool_rounds})")
        return llm_response.content or "I apologize, but I've reached the maximum number of tool execution attempts."

    async def _streaming_loop(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str],
        max_tool_rounds: int = 10
    ) -> AsyncGenerator[str, None]:
        """
        Clean streaming loop that consumes Brain's structured stream.

        The Brain handles all streaming + tool call complexity.
        Agent just processes the structured chunks and handles tool execution.
        """
        conversation = messages.copy()
        available_tools = self.get_tools_json()

        for round_num in range(max_tool_rounds):
            # Truncate conversation history if needed
            max_tokens = self.get_max_context_tokens()
            truncated_conversation = self._truncate_conversation_history(conversation, max_tokens)

            # Single streaming call - Brain handles tool call detection
            stream = self.brain.stream_response(
                messages=truncated_conversation,
                system_prompt=system_prompt,
                tools=available_tools
            )

            # Process structured stream from Brain
            content_parts = []
            tool_calls_detected = []

            async for chunk in stream:
                chunk_type = chunk.get('type')

                if chunk_type == 'text-delta':
                    # Stream text content to user immediately
                    content = chunk.get('content', '')
                    content_parts.append(content)
                    yield {"type": "content", "content": content}

                elif chunk_type == 'tool-call':
                    # Collect tool calls (no text parsing needed!)
                    tool_calls_detected.append(chunk.get('tool_call'))

                elif chunk_type == 'finish':
                    # Stream finished - process any tool calls
                    break

                elif chunk_type == 'error':
                    # Stream error
                    yield {"type": "error", "content": chunk.get('content', 'Error occurred')}
                    return

            # Handle tool calls if detected
            if tool_calls_detected:
                # Emit tool call chunk
                yield {
                    "type": "tool_calls_start",
                    "count": len(tool_calls_detected),
                    "content": f"\n🔧 Executing {len(tool_calls_detected)} tool(s)...\n"
                }

                # Add assistant message with tool calls
                full_content = ''.join(content_parts)
                conversation.append({
                    "role": "assistant",
                    "content": full_content,
                    "tool_calls": [
                        {
                            "id": tc.get('id'),
                            "type": tc.get('type', 'function'),
                            "function": tc.get('function', {})
                        } for tc in tool_calls_detected
                    ]
                })

                # Execute tools and emit tool-result chunks for client visualization
                # Convert to expected format for tool executor
                formatted_tool_calls = []
                for tc in tool_calls_detected:
                    # Create mock tool call object with required attributes
                    class MockToolCall:
                        def __init__(self, data):
                            self.id = data.get('id')
                            self.type = data.get('type', 'function')
                            self.function = type('obj', (object,), {
                                'name': data.get('function', {}).get('name'),
                                'arguments': data.get('function', {}).get('arguments')
                            })()

                    formatted_tool_calls.append(MockToolCall(tc))

                # Execute tools one by one and emit results for client visualization
                tool_messages = []
                for i, tool_call in enumerate(formatted_tool_calls):
                    # Emit tool call start
                    yield {
                        "type": "tool_call",
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                        "content": f"🔧 Calling {tool_call.function.name}..."
                    }

                    try:
                        # Execute single tool call
                        result = await self.tool_manager.execute_tools([tool_call], self.name)
                        tool_messages.extend(result)

                        # Emit tool result chunk
                        tool_result_content = result[0].get('content', '') if result else 'No result'
                        yield {
                            "type": "tool_result",
                            "name": tool_call.function.name,
                            "success": True,
                            "content": f"✅ {tool_call.function.name}: {tool_result_content[:100]}{'...' if len(tool_result_content) > 100 else ''}"
                        }

                    except Exception as e:
                        # Handle tool execution error
                        error_message = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": f"Error: {str(e)}"
                        }
                        tool_messages.append(error_message)
                        yield {
                            "type": "tool_result",
                            "name": tool_call.function.name,
                            "success": False,
                            "content": f"❌ {tool_call.function.name} failed: {str(e)}"
                        }

                conversation.extend(tool_messages)

                # Continue to next step
                continue
            else:
                # No tool calls - conversation complete
                return

        # Max rounds exceeded
        yield {"type": "warning", "content": "\n⚠️ Reached maximum tool execution limit."}

    async def _generate_response_non_streaming(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str],
        max_tool_rounds: int = 10
    ) -> str:
        """
        Non-streaming loop using Brain's generate_response method.
        """
        conversation = messages.copy()
        available_tools = self.get_tools_json()

        for round_num in range(max_tool_rounds):
            # Truncate conversation history if needed
            max_tokens = self.get_max_context_tokens()
            truncated_conversation = self._truncate_conversation_history(conversation, max_tokens)

            # Single non-streaming call
            response = await self.brain.generate_response(
                messages=truncated_conversation,
                system_prompt=system_prompt,
                tools=available_tools
            )

            # Check if there are tool calls in the response
            if response.tool_calls:
                # Add assistant message with tool calls
                conversation.append({
                    "role": "assistant",
                    "content": response.content or "",
                    "tool_calls": [
                        {
                            "id": tc.get('id'),
                            "type": tc.get('type', 'function'),
                            "function": tc.get('function', {})
                        } for tc in response.tool_calls
                    ]
                })

                # Execute tools
                formatted_tool_calls = []
                for tc in response.tool_calls:
                    class MockToolCall:
                        def __init__(self, data):
                            self.id = data.get('id')
                            self.type = data.get('type', 'function')
                            self.function = type('obj', (object,), {
                                'name': data.get('function', {}).get('name'),
                                'arguments': data.get('function', {}).get('arguments')
                            })()

                    formatted_tool_calls.append(MockToolCall(tc))

                # Execute tools and add results to conversation
                try:
                    tool_messages = await self.tool_manager.execute_tools(formatted_tool_calls, self.name)
                    conversation.extend(tool_messages)
                except Exception as e:
                    # Handle tool execution error
                    error_message = {
                        "role": "tool",
                        "content": f"Error executing tools: {str(e)}"
                    }
                    conversation.append(error_message)

                # Continue to next round
                continue
            else:
                # No tool calls - return the response content
                return response.content or ""

        # Max rounds exceeded
        return "Reached maximum tool execution limit."

    def build_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Build the system prompt for the agent, including dynamic context and tool definitions."""
        # Load base prompt from file or use system_message
        base_prompt = ""

        # Check for prompt_template first (this is what team loader sets)
        if hasattr(self.config, 'prompt_template') and self.config.prompt_template:
            try:
                # If prompt_template looks like a file path, read it
                if self.config.prompt_template.endswith('.md') or '/' in self.config.prompt_template:
                    with open(self.config.prompt_template, 'r') as f:
                        base_prompt = f.read()
                else:
                    # Otherwise use it as direct prompt content
                    base_prompt = self.config.prompt_template
            except Exception as e:
                logger.warning(f"Failed to load prompt template {self.config.prompt_template}: {e}")
                base_prompt = getattr(self.config, 'system_message', "You are a helpful AI assistant.")
        elif hasattr(self.config, 'prompt_file') and self.config.prompt_file:
            try:
                with open(self.config.prompt_file, 'r') as f:
                    base_prompt = f.read()
            except Exception as e:
                logger.warning(f"Failed to load prompt file {self.config.prompt_file}: {e}")
                base_prompt = getattr(self.config, 'system_message', "You are a helpful AI assistant.")
        elif hasattr(self.config, 'system_message') and self.config.system_message:
            base_prompt = self.config.system_message
        else:
            base_prompt = "You are a helpful AI assistant."

        if not context:
            return base_prompt

        # Add context information
        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        context_prompt = f"""
Here is some context for the current task:
- Current date and time: {current_datetime}
- Task ID: {context.get('task_id', 'N/A')}

IMPORTANT - File Storage Guidelines:
- All storage tools (write_file, read_file, etc.) work within your task workspace automatically
- Use RELATIVE paths only: "report.md", "data/results.json", "temp/script.sh"
- DO NOT use absolute paths or workspace prefixes like "workspace/task_id/file.md"
- Files save to artifacts/ by default, or specify "temp/" for temporary files
- Examples: write_file("report.md", content) → saves to artifacts/report.md
"""

        # Add tool information with explicit instructions
        tools_prompt = ""
        if self.tools:
            available_tools = [tool for tool in self.tools if tool in [t['function']['name'] for t in self.get_tools_json()]]
            if available_tools:
                tools_prompt = f"""

IMPORTANT: You have access to the following tools. Use them when needed to complete tasks:

Available Tools: {', '.join(available_tools)}

When you need to use a tool:
1. Think about which tool would help accomplish the task
2. Call the tool with the appropriate parameters
3. Wait for the result before continuing
4. Use the tool results to inform your response

Tool Usage Guidelines:
- Use tools proactively when they can help solve the user's request
- For file operations, use the file management tools
- For saving important content, use store_artifact
- For research or web searches, use the search tools
- Always check tool results and handle errors gracefully
"""

        return f"{base_prompt}{context_prompt}{tools_prompt}"

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities summary."""
        return {
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
            "memory_enabled": self.memory_enabled,
            "max_iterations": self.max_iterations,
            "state": self.state.dict()
        }

    def reset_state(self):
        """Reset agent state."""
        self.state = AgentState(agent_name=self.name)

    def add_tool(self, tool):
        """Add a tool to the agent's capabilities."""
        if isinstance(tool, str):
            if tool not in self.tools:
                self.tools.append(tool)
        elif isinstance(tool, Tool):
            # Register the tool and add its methods
            from .tool import register_tool
            register_tool(tool)
            methods = tool.get_callable_methods()
            for method_name in methods:
                if method_name not in self.tools:
                    self.tools.append(method_name)
        else:
            raise ValueError(f"Invalid tool type: {type(tool)}")

    def remove_tool(self, tool_name: str):
        """Remove a tool from the agent's capabilities."""
        if tool_name in self.tools:
            self.tools.remove(tool_name)

    def update_config(self, **kwargs):
        """Update agent configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def __str__(self) -> str:
        return f"Agent(name='{self.name}', tools={len(self.tools)}, active={self.state.is_active})"

    def __repr__(self) -> str:
        return self.__str__()


def create_assistant_agent(name: str, system_message: str = "") -> Agent:
    """Create a simple assistant agent with default configuration."""
    from .config import AgentConfig, BrainConfig

    config = AgentConfig(
        name=name,
        description="AI Assistant",
        prompt_template=system_message or "You are a helpful AI assistant.",
        brain_config=BrainConfig()
    )

    return Agent(config)
