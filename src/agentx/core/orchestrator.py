from __future__ import annotations
import re
import asyncio
from pathlib import Path
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from agentx.core.task import Task
    from agentx.builtin_tools.plan import PlanTool

from agentx.core.agent import Agent
from agentx.core.brain import Brain
from .config import BrainConfig
from agentx.utils.logger import get_logger

logger = get_logger(__name__)


class BaseOrchestrator(ABC):
    """
    Base Orchestrator class implementing AgentX orchestration principles for multi-agent coordination.
    
    Key principles:
    - Strategic task decomposition (3-6 high-value tasks)
    - Direct path to professional deliverables
    - Quality-focused workflow with clear completion criteria
    - Elimination of redundant steps and intermediate files
    """
    
    def __init__(self, task: "Task"):
        self.task = task
        self.plan_tool = task.plan_tool  # Get the tool from the task
        self.workspace = Path(self.task.workspace_dir)
        
        # Detect input language once and store for consistent usage
        self.input_language = self._detect_language(self.task.initial_prompt)
        self.language_instruction = self._get_language_instruction(self.input_language)
        
        # Create organized workspace structure following AgentX principles
        self._setup_workspace_structure()
        
        logger.info(f"BaseOrchestrator initialized for task: {self.task.initial_prompt[:100]}... (Language: {self.input_language})")

    def _setup_workspace_structure(self):
        """Create only essential workspace structure - other directories created on-demand"""
        essential_directories = [
            "artifacts",         # Plans and coordination files (always needed)
        ]
        
        for directory in essential_directories:
            (self.workspace / directory).mkdir(parents=True, exist_ok=True)
        
        # Other directories (research, final_reports, assets, deploy, etc.) 
        # will be created on-demand when agents actually need them

    def _detect_language(self, text: str) -> str:
        """
        Detect the primary language of the input text.
        Returns language code for consistent responses.
        """
        # Simple heuristic-based language detection
        # Chinese characters (simplified/traditional)
        chinese_chars = len([c for c in text if "\u4e00" <= c <= "\u9fff"])
        
        # Japanese characters (hiragana, katakana, kanji)
        japanese_chars = len([c for c in text if "\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff"])
        
        # Korean characters
        korean_chars = len([c for c in text if "\uac00" <= c <= "\ud7af"])
        
        # Arabic characters
        arabic_chars = len([c for c in text if "\u0600" <= c <= "\u06ff"])
        
        # Spanish indicators
        spanish_words = ["análisis", "estratégico", "mercado", "empresa", "negocio"]
        spanish_score = sum(1 for word in spanish_words if word.lower() in text.lower())
        
        # French indicators
        french_words = ["analyse", "stratégique", "marché", "entreprise", "développement"]
        french_score = sum(1 for word in french_words if word.lower() in text.lower())
        
        # German indicators
        german_words = ["analyse", "strategisch", "markt", "unternehmen", "entwicklung"]
        german_score = sum(1 for word in german_words if word.lower() in text.lower())
        
        total_chars = len(text)
        if total_chars == 0:
            return "en"
        
        # Calculate percentages
        chinese_ratio = chinese_chars / total_chars
        japanese_ratio = japanese_chars / total_chars
        korean_ratio = korean_chars / total_chars
        arabic_ratio = arabic_chars / total_chars
        
        # Determine language based on character composition and keywords
        if chinese_ratio > 0.1:
            return "zh"
        elif japanese_ratio > 0.1:
            return "ja"
        elif korean_ratio > 0.1:
            return "ko"
        elif arabic_ratio > 0.1:
            return "ar"
        elif spanish_score >= 2:
            return "es"
        elif french_score >= 2:
            return "fr"
        elif german_score >= 2:
            return "de"
        else:
            return "en"  # Default to English
    
    def _get_language_instruction(self, language_code: str) -> str:
        """
        Get language-specific instruction for consistent output language.
        """
        language_instructions = {
            "zh": "IMPORTANT: Respond in Chinese (中文). All analysis, plans, and content must be in Chinese.",
            "ja": "IMPORTANT: Respond in Japanese (日本語). All analysis, plans, and content must be in Japanese.",
            "ko": "IMPORTANT: Respond in Korean (한국어). All analysis, plans, and content must be in Korean.",
            "ar": "IMPORTANT: Respond in Arabic (العربية). All analysis, plans, and content must be in Arabic.",
            "es": "IMPORTANT: Respond in Spanish (Español). All analysis, plans, and content must be in Spanish.",
            "fr": "IMPORTANT: Respond in French (Français). All analysis, plans, and content must be in French.",
            "de": "IMPORTANT: Respond in German (Deutsch). All analysis, plans, and content must be in German.",
            "en": "IMPORTANT: Respond in English. All analysis, plans, and content must be in English."
        }
        
        return language_instructions.get(language_code, language_instructions["en"])


    async def _create_plan(self, planner_agent_name: str):
        """
        Creates a strategic plan using the PlanTool.
        """
        if planner_agent_name not in self.task.agents:
            raise ValueError(f"Planner agent '{planner_agent_name}' not found in the team.")
        
        planner = self.task.agents[planner_agent_name]
        
        # The prompt now instructs the agent to call the 'create_plan' tool
        # with a structured (but flexible) JSON format.
        prompt = f"""Create a strategic execution plan for: {self.task.initial_prompt}

{self.language_instruction}

Your goal is to produce a JSON structure for the `create_plan` tool. The structure should contain a list of 'phases', each with a 'name' and a list of 'tasks'. Each task should have a 'description'.

AGENTX ORCHESTRATION PRINCIPLES:
- Maximum 3-6 high-value phases that directly contribute to final deliverables.
- Each task should be a concrete action building toward the phase goal.
- Focus on quality over quantity - fewer, better tasks.

Example of a good `plan_data` format:
{{
    "phases": [
        {{
            "name": "Phase 1: Research and Analysis",
            "tasks": [
                {{"description": "Conduct market research on target audience."}},
                {{"description": "Analyze competitor strategies."}}
            ]
        }},
        {{
            "name": "Phase 2: Content Creation",
            "tasks": [
                {{"description": "Write blog post about findings."}},
                {{"description": "Create social media content."}}
            ]
        }}
    ]
}}

Now, create the plan.
"""
        
        plan_result = await self.task.executor.run_agent(
            agent=planner,
            prompt=prompt
        )
        
        # We no longer check for a file, as the tool handles persistence.
        # We rely on the agent having correctly called the tool.
        logger.info(f"Planner agent executed. Agent output: {plan_result}")
        print(f"Planner agent run completed.")

    async def get_next_step(self) -> str | None:
        """Reads the plan from the PlanTool and returns the next incomplete step."""
        result = await self.plan_tool.get_plan_status(query="next incomplete task")
        
        if result.is_success() and result.content:
            # The tool should return the description of the next task.
            return result.content
        return None

    async def _update_plan(self, step: str, result: str):
        """Marks a step as complete in the PlanTool."""
        update_result = await self.plan_tool.update_task_status(
            task_query=step,
            new_status="completed",
            notes=result
        )
        
        if update_result.is_success():
            logger.info(f"Step completed and plan updated via PlanTool: {step[:50]}...")
        else:
            logger.warning(f"Could not update step '{step}' via PlanTool. Reason: {update_result.content}")
            print(f"Warning: Could not update step '{step}' via PlanTool.")

    def _create_step_prompt(self, step: str, agent: Agent) -> str:
        """
        Create comprehensive contextual prompt following AgentX principles.
        
        Provides detailed context, clear objectives, and professional standards.
        """
        context = f"""# Task Execution Context

{self.language_instruction}

## OVERALL PROJECT OBJECTIVE
{self.task.initial_prompt}

## CURRENT TASK FOCUS
{step}

## AGENTX ORCHESTRATION EXECUTION PRINCIPLES
- **Quality First**: Deliver professional, executive-ready outputs
- **Direct Value**: Every action must contribute directly to final deliverables
- **No Redundancy**: Avoid creating unnecessary intermediate files or steps
- **Strategic Focus**: Think like a consultant delivering to C-level executives
- **Efficiency**: Use the most direct path to achieve objectives

## WORKSPACE ORGANIZATION
- `research/`: Data gathering, market analysis, competitive intelligence
- `final_reports/`: Complete professional documents ready for business use
- `deploy/`: Production-ready deliverables for immediate distribution
- `assets/`: Supporting materials, charts, visualizations

## EXECUTION REQUIREMENTS
1. **Professional Standards**: All outputs must be suitable for executive consumption
2. **Data-Driven**: Include specific statistics, quantitative analysis, and credible sources
3. **Actionable Insights**: Provide strategic recommendations with implementation guidance
4. **Complete Deliverables**: Create finished products, not drafts or templates
5. **Quality Assurance**: Ensure accuracy, clarity, and professional presentation

## CURRENT TASK OBJECTIVE
Complete this specific task with professional excellence: **{step}**

Focus on delivering high-quality results that directly advance the overall project objective. Save all work using appropriate tools and organize outputs in the designated workspace structure.
"""
        return context

    @abstractmethod
    async def _get_worker_for_step(self, step: str) -> Agent:
        """Abstract method to determine which specialist agent should handle the current step."""
        pass

    async def _append_to_plan(self, planner_agent_name: str):
        """
        Append new tasks to existing plan when user provides additional requirements.
        Preserves all completed work and adds new todo items.
        """
        if planner_agent_name not in self.task.agents:
            raise ValueError(f"Planner agent '{planner_agent_name}' not found in the team.")
        
        planner = self.task.agents[planner_agent_name]
        
        # Read existing plan to understand completed work
        existing_plan = ""
        if self.plan_tool.get_plan_status(query="existing plan").is_success() and self.plan_tool.get_plan_status(query="existing plan").content:
            existing_plan = self.plan_tool.get_plan_status(query="existing plan").content
        
        prompt = f"""You have an existing strategic plan with completed work:

{existing_plan}

The user now has NEW REQUIREMENTS: {self.task.initial_prompt}

{self.language_instruction}

TASK: Append additional strategic tasks to the existing plan to fulfill the new requirements.

IMPORTANT GUIDELINES:
- DO NOT remove or modify existing completed items (marked with [x])
- DO NOT duplicate any existing work
- Build upon the completed foundation 
- Add only NEW tasks needed for the additional requirements
- Use the same format: - [ ] for new unchecked tasks
- Focus on high-value additions that leverage existing work

PLAN FORMAT:
- Keep all existing content exactly as is
- At the end, add a new section: "## Additional Requirements"
- List new tasks with - [ ] format
- Ensure logical dependencies and execution order

Append the new tasks to the existing plan and save the complete updated plan."""
        
        plan_result = await self.task.executor.run_agent(
            agent=planner,
            prompt=prompt
        )
        
        if not self.plan_tool.get_plan_status(query="existing plan").is_success():
            raise ValueError(f"Planner agent '{planner_agent_name}' did not update the plan. The agent output was: {plan_result}")
        
        logger.info(f"Strategic plan updated with new requirements")
        print(f"Plan updated with new requirements")

    async def run(self, planner_agent_name: str):
        """
        Runs the main orchestration loop following AgentX principles.
        
        Coordinates specialist agents to execute strategic plan with professional standards.
        """
        logger.info(f"Starting orchestration workflow with planner: {planner_agent_name}")
        
        # --- Main execution loop ---
        try:
            # Check if we need a new plan or should append to existing
            plan_status_result = await self.plan_tool.get_plan_status(query="existing plan")
            if not plan_status_result.is_success():
                # No plan exists - create new one
                await self._create_plan(planner_agent_name)
            elif self.task.initial_prompt and not self.task.can_resume_with_prompt(self.task.initial_prompt):
                # New requirements have been added - append to existing plan
                await self._append_to_plan(planner_agent_name)
            
            # --- Iterate through plan steps ---
            while (step := await self.get_next_step()):
                logger.info(f"🚀 Starting next step: {step}")
                
                # 1. Get best worker for the step
                worker_agent = await self._get_worker_for_step(step)
                
                # 2. Create contextual prompt
                step_prompt = self._create_step_prompt(step, worker_agent)
                
                # 3. Execute step
                result = await self.task.executor.run_agent(
                    agent=worker_agent,
                    prompt=step_prompt
                )
                
                # 4. Update plan with result
                await self._update_plan(step, str(result))
                
                # Give user a chance to review/pause
                await asyncio.sleep(1)

            # --- Task completion ---
            self.task.complete_task()
            
        except Exception as e:
            logger.error(f"Orchestrator failed: {e}")
            raise


class Orchestrator(BaseOrchestrator):
    """
    Professional Multi-Agent Orchestrator implementing AgentX principles.
    
    Uses intelligent routing to coordinate specialist agents for high-quality deliverable production.
    Focuses on strategic task decomposition and professional workflow management.
    """
    
    def __init__(self, task: "Task"):
        super().__init__(task)
        self._agent_specializations = self._analyze_agent_capabilities()
        
    def _analyze_agent_capabilities(self) -> Dict[str, List[str]]:
        """
        Analyze available agents and their specializations for intelligent routing.
        
        Returns mapping of agent names to their key capabilities and focus areas.
        """
        specializations = {}
        
        for agent_name, agent in self.task.agents.items():
            name_lower = agent_name.lower()
            
            # Determine specializations based on agent name and role
            if 'research' in name_lower or 'analyst' in name_lower:
                specializations[agent_name] = [
                    'market research', 'data gathering', 'competitive analysis',
                    'industry trends', 'statistics', 'case studies', 'expert insights'
                ]
            elif 'write' in name_lower or 'content' in name_lower:
                specializations[agent_name] = [
                    'content creation', 'report writing', 'executive summaries',
                    'strategic analysis', 'recommendations', 'professional documentation'
                ]
            elif 'review' in name_lower or 'quality' in name_lower:
                specializations[agent_name] = [
                    'quality assurance', 'fact checking', 'editing',
                    'presentation optimization', 'final review'
                ]
            elif 'plan' in name_lower:
                specializations[agent_name] = [
                    'strategic planning', 'task decomposition', 'workflow design',
                    'project coordination', 'objective setting'
                ]
            elif 'technical' in name_lower or 'dev' in name_lower:
                specializations[agent_name] = [
                    'technical implementation', 'html creation', 'data visualization',
                    'interactive elements', 'web development'
                ]
            elif 'format' in name_lower or 'document' in name_lower:
                specializations[agent_name] = [
                    'document formatting', 'html generation', 'pdf creation', 'word documents',
                    'presentation slides', 'multi-format output', 'professional styling',
                    'responsive design', 'interactive visualizations', 'document conversion'
                ]
            else:
                # Default general capabilities
                specializations[agent_name] = [
                    'general assistance', 'task execution', 'content support'
                ]
                
        logger.info(f"Agent specializations mapped: {list(specializations.keys())}")
        return specializations

    async def _get_worker_for_step(self, step: str) -> "Agent":
        """
        Uses intelligent routing to determine the best specialist agent for each step.
        
        Combines keyword matching with LLM-based classification for optimal agent selection.
        """
        step_lower = step.lower()
        agent_names = list(self.task.agents.keys())
        
        # First, try keyword-based routing for common patterns
        best_agent = self._route_by_keywords(step_lower, agent_names)
        
        if best_agent:
            logger.info(f"Keyword-based routing: '{step[:50]}...' -> {best_agent.config.name}")
            print(f"Routing step to agent: '{best_agent.config.name}' (keyword match)")
            return best_agent
        
        # Fallback to LLM-based classification for complex cases
        return await self._route_by_llm(step, agent_names)
    
    def _route_by_keywords(self, step_lower: str, agent_names: List[str]) -> Optional[Agent]:
        """Route tasks based on keyword matching with agent specializations."""
        
        # Research and data gathering keywords
        research_keywords = [
            'research', 'market', 'data', 'statistics', 'competitive', 
            'analysis', 'industry', 'trends', 'case studies', 'sources',
            'gather', 'collect', 'investigate', 'analyze', 'study'
        ]
        
        # Content creation and writing keywords  
        writing_keywords = [
            'write', 'create', 'report', 'content', 'executive', 'summary',
            'recommendations', 'strategic', 'document', 'draft', 'compose'
        ]
        
        # Quality and review keywords
        review_keywords = [
            'review', 'quality', 'check', 'verify', 'validate', 'edit',
            'polish', 'optimize', 'final', 'ensure', 'confirm'
        ]
        
        # Technical implementation keywords
        technical_keywords = [
            'html', 'technical', 'visualization', 'charts', 'interactive',
            'website', 'design', 'implement', 'develop', 'code'
        ]
        
        # Document formatting keywords
        formatting_keywords = [
            'format', 'document', 'html', 'pdf', 'word', 'presentation',
            'slides', 'styling', 'layout', 'convert', 'transform', 'export'
        ]
        
        # Count keyword matches for each category
        research_score = sum(1 for keyword in research_keywords if keyword in step_lower)
        writing_score = sum(1 for keyword in writing_keywords if keyword in step_lower)
        review_score = sum(1 for keyword in review_keywords if keyword in step_lower)
        technical_score = sum(1 for keyword in technical_keywords if keyword in step_lower)
        formatting_score = sum(1 for keyword in formatting_keywords if keyword in step_lower)
        
        # Find the category with highest score
        scores = {
            'research': research_score,
            'writing': writing_score,
            'review': review_score,
            'technical': technical_score,
            'formatting': formatting_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return None  # No clear match, use LLM routing
            
        best_category = max(scores, key=scores.get)
        
        # Map categories to agent names
        for agent_name in agent_names:
            name_lower = agent_name.lower()
            
            if best_category == 'research' and any(keyword in name_lower for keyword in ['research', 'analyst']):
                return self.task.agents[agent_name]
            elif best_category == 'writing' and any(keyword in name_lower for keyword in ['write', 'content']):
                return self.task.agents[agent_name]
            elif best_category == 'review' and any(keyword in name_lower for keyword in ['review', 'quality']):
                return self.task.agents[agent_name]
            elif best_category == 'technical' and any(keyword in name_lower for keyword in ['technical', 'dev']):
                return self.task.agents[agent_name]
            elif best_category == 'formatting' and any(keyword in name_lower for keyword in ['format', 'document']):
                return self.task.agents[agent_name]
        
        return None

    async def _route_by_llm(self, step: str, agent_names: List[str]) -> Agent:
        """Use LLM-based classification for complex routing decisions."""
        
        # Create detailed prompt with agent specializations
        agent_descriptions = []
        for agent_name in agent_names:
            specializations = self._agent_specializations.get(agent_name, ['general tasks'])
            agent_descriptions.append(f"- {agent_name}: {', '.join(specializations)}")
        
        prompt = f"""Given this task step:
"{step}"

Which specialist agent is best suited to execute this task?

Available agents and their specializations:
{chr(10).join(agent_descriptions)}

Consider:
- The specific skills and expertise required
- The type of output or deliverable needed
- The complexity and scope of the task

Respond with only the exact agent name that best matches the task requirements."""

        # Use efficient model for classification
        routing_config = BrainConfig(
            provider="deepseek",
            model="deepseek/deepseek-chat",
            temperature=0.1,
            max_tokens=100,
            supports_function_calls=False,
            streaming=False
        )
        routing_brain = Brain(routing_config)

        response = await routing_brain.generate_response(
            messages=[{"role": "user", "content": prompt}]
        )

        chosen_agent_name = response.content.strip()

        # Find the best matching agent
        best_agent = None
        for name in agent_names:
            if name.lower() in chosen_agent_name.lower():
                best_agent = self.task.agents[name]
                break

        if best_agent:
            logger.info(f"LLM-based routing: '{step[:50]}...' -> {best_agent.config.name}")
            print(f"Routing step to agent: '{best_agent.config.name}' (LLM classification)")
            return best_agent
        else:
            logger.warning(f"Could not determine optimal agent for step, using fallback: {step[:50]}...")
            print(f"Warning: Could not reliably determine agent for step '{step}'. Defaulting to first agent.")
            return self.task.agents[agent_names[0]]


# End of file - no backward compatibility aliases 
