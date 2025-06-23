"""
Orchestrator Component - Clean Agent Routing

Simple, intelligent orchestrator that handles agent coordination with proper
handoff support. Uses AI for smart routing decisions without hardcoded rules.
"""

import json
from typing import Dict, Any, List, Optional
from .config import BrainConfig
from .brain import Brain
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """
    Clean orchestrator for intelligent agent routing.
    
    Uses AI to make smart routing decisions based on:
    1. Team configuration handoffs (when available)
    2. Agent responses and work completion status
    3. Task context and progress
    """
    
    def __init__(self, task: 'Task' = None, max_rounds: int = 50, timeout: int = 3600):
        """Initialize orchestrator with task context."""
        self.task = task
        self.max_rounds = max_rounds
        self.timeout = timeout
        self.routing_brain = None
        
        if task and task.team_config:
            self._initialize_routing_brain()

    def _initialize_routing_brain(self):
        """Initialize the routing brain from team config."""
        try:
            # Get brain config from team orchestrator config
            orchestrator_config = getattr(self.task.team_config, 'orchestrator', None)
            if orchestrator_config and hasattr(orchestrator_config, 'brain_config'):
                brain_config = orchestrator_config.brain_config
            else:
                # Fallback: use default brain config
                brain_config = BrainConfig(
                    provider="deepseek",
                    model="deepseek-chat", 
                    temperature=0.0,
                    max_tokens=100
                )
            
            self.routing_brain = Brain.from_config(brain_config)
            if not self.routing_brain:
                raise RuntimeError("Brain.from_config() returned None")
                
            logger.info(f"Routing brain initialized for task '{self.task.task_id}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize routing brain: {e}")
            raise

    async def decide_next_step(self, context: Dict[str, Any], last_response: str = None) -> Dict[str, Any]:
        """
        Decide the next action: CONTINUE, HANDOFF, or COMPLETE.
        
        Uses intelligent AI-based routing that considers:
        - Current agent and their response
        - Available handoff options from team config
        - Work completion status
        - Task progress and context
        """
        # No task: complete immediately
        if not self.task:
            return {"action": "COMPLETE", "next_agent": context.get("current_agent", "assistant"), "reason": "No task configured"}
        
        # Single-agent teams: complete after response
        if len(self.task.agents) <= 1:
            return {"action": "COMPLETE", "next_agent": context.get("current_agent", "assistant"), "reason": "Single agent task complete"}
        
        # Multi-agent teams: use intelligent routing
        current_agent = context.get("current_agent")
        
        try:
            return await self._intelligent_routing(current_agent, last_response)
        except Exception as e:
            logger.error(f"Routing decision failed: {e}")
            return {"action": "CONTINUE", "next_agent": current_agent, "reason": f"Error fallback: {e}"}

    async def _intelligent_routing(self, current_agent: str, last_response: str = None) -> Dict[str, Any]:
        """
        Use AI to make intelligent routing decisions.
        """
        # Ensure routing brain is initialized
        if not self.routing_brain:
            self._initialize_routing_brain()
        
        # Get available handoff options
        handoff_options = self._get_handoff_options(current_agent)
        all_agents = list(self.task.agents.keys())
        
        # Build intelligent routing prompt
        prompt = f"""You are an intelligent task orchestrator. Analyze the current agent's response and decide the next action.

CONTEXT:
- Current agent: {current_agent}
- All agents: {all_agents}
- Available handoffs: {handoff_options}
- Agent response: "{last_response[:500] if last_response else 'No response'}"

TEAM WORKFLOW:
{self._get_team_workflow_info()}

ANALYSIS GUIDELINES:
1. **Work Completion**: Is the current agent's work actually complete?
   - Look for completion signals: "done", "finished", "complete", "ready for next"
   - Look for continuation signals: "working on", "still need to", "next I will"
   - Consider if files were created, tasks completed, goals achieved

2. **Handoff Readiness**: Should we move to the next agent?
   - Only handoff when current phase is truly complete
   - Consider the logical workflow progression
   - Ensure the next agent has what they need to start

3. **Task Progress**: What's the overall task status?
   - Are we still in early phases or near completion?
   - Is this the final deliverable or intermediate work?

DECISION RULES:
- CONTINUE: Current agent has more work to do
- HANDOFF: Current work complete, next agent should take over  
- COMPLETE: Entire task is finished
- NEVER handoff to the same agent

Return JSON: {{"action": "CONTINUE|HANDOFF|COMPLETE", "next_agent": "agent_name", "reason": "explanation"}}"""

        # Get AI decision
        brain_response = await self.routing_brain.generate_response(
            messages=[{"role": "user", "content": prompt}],
            json_mode=True
        )
        
        # Parse decision
        try:
            decision = json.loads(brain_response.content.strip())
            action = decision.get("action", "CONTINUE")
            next_agent = decision.get("next_agent", current_agent)
            reason = decision.get("reason", "AI routing decision")
            
            # Validate decision
            if action == "HANDOFF" and next_agent == current_agent:
                logger.warning("AI tried to handoff to same agent, forcing CONTINUE")
                action = "CONTINUE"
            
            if action == "HANDOFF" and next_agent not in all_agents:
                logger.warning(f"AI chose invalid agent {next_agent}, forcing CONTINUE")
                action = "CONTINUE"
                next_agent = current_agent
            
            return {"action": action, "next_agent": next_agent, "reason": reason}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse routing decision: {e}")
            return {"action": "CONTINUE", "next_agent": current_agent, "reason": "JSON parse error"}

    def _get_handoff_options(self, current_agent: str) -> List[str]:
        """Get available handoff targets for current agent."""
        if not self.task or not self.task.team_config:
            # Fallback: all other agents
            all_agents = list(self.task.agents.keys())
            return [agent for agent in all_agents if agent != current_agent]
        
        # Get handoffs from team configuration
        handoffs = getattr(self.task.team_config, 'handoffs', [])
        if not handoffs:
            # No handoffs configured, allow all agents
            all_agents = list(self.task.agents.keys())
            return [agent for agent in all_agents if agent != current_agent]
        
        # Find valid handoff targets
        targets = []
        for handoff in handoffs:
            if isinstance(handoff, dict):
                from_agent = handoff.get('from_agent')
                to_agent = handoff.get('to_agent')
                if from_agent == current_agent and to_agent:
                    targets.append(to_agent)
        
        return targets

    def _get_team_workflow_info(self) -> str:
        """Get team workflow information for routing context."""
        if not self.task or not self.task.team_config:
            return "No team workflow configured"
        
        info = []
        
        # Add agent descriptions
        for name, agent in self.task.agents.items():
            info.append(f"- {name}: {agent.config.description}")
        
        # Add handoff flow
        handoffs = getattr(self.task.team_config, 'handoffs', [])
        if handoffs:
            info.append("\nWorkflow:")
            for handoff in handoffs:
                if isinstance(handoff, dict):
                    from_agent = handoff.get('from_agent')
                    to_agent = handoff.get('to_agent')
                    condition = handoff.get('condition', '')
                    info.append(f"- {from_agent} → {to_agent}: {condition}")
        
        return "\n".join(info)






