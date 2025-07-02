from __future__ import annotations
import re
import asyncio
from pathlib import Path
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from agentx.core.task import Task

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
        self.workspace = Path(self.task.workspace_dir)
        self.plan_path = self.workspace / "artifacts" / "plan.md"
        
        # Detect input language once and store for consistent usage
        self.input_language = self._detect_language(self.task.initial_prompt)
        self.language_instruction = self._get_language_instruction(self.input_language)
        
        # Create organized workspace structure following AgentX principles
        self._setup_workspace_structure()
        
        logger.info(f"BaseOrchestrator initialized for task: {self.task.initial_prompt[:100]}... (Language: {self.input_language})")

    def _setup_workspace_structure(self):
        """Create professional workspace structure for organized output"""
        directories = [
            "artifacts",         # Plans and coordination files
            "research",          # Research findings and data
            "research/data_tables",  # Structured data files
            "research/case_studies", # Company examples
            "research/expert_quotes", # Industry expert insights
            "drafts",           # Work-in-progress content
            "final_reports",    # Completed deliverables
            "assets",           # Images, charts, supporting files
            "deploy"            # Final production-ready files
        ]
        
        for directory in directories:
            (self.workspace / directory).mkdir(parents=True, exist_ok=True)

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
        Creates strategic plan following AgentX orchestration principles:
        - 3-6 high-value tasks maximum
        - Direct path to final deliverables
        - No redundant intermediate steps
        - Clear completion criteria for each task
        """
        if planner_agent_name not in self.task.agents:
            raise ValueError(f"Planner agent '{planner_agent_name}' not found in the team.")
        
        planner = self.task.agents[planner_agent_name]
        
        prompt = f"""Create a strategic execution plan for: {self.task.initial_prompt}

{self.language_instruction}

AGENTX ORCHESTRATION PRINCIPLES:
- Maximum 3-6 high-value tasks that directly contribute to final deliverables
- Each task should build toward the ultimate goal without redundant steps
- No intermediate files or unnecessary complexity
- Direct path to professional, executive-ready outputs
- Clear, measurable completion criteria for each task

PLAN REQUIREMENTS:
- Use markdown checklist format with - [ ] for each task
- Each task should be substantial and directly valuable
- Focus on quality over quantity - fewer, better tasks
- Ensure logical dependencies and execution order
- Include specific deliverable requirements for each task

WORKSPACE ORGANIZATION:
- research/ for data gathering and analysis
- final_reports/ for completed content
- deploy/ for production-ready deliverables
- assets/ for supporting materials

Create a strategic plan that eliminates waste and focuses on high-impact deliverables. Save as '{self.plan_path.name}' in the current directory."""
        
        plan_result = await self.task.executor.run_agent(
            agent=planner,
            prompt=prompt
        )
        
        if not self.plan_path.exists():
            raise FileNotFoundError(f"Planner agent '{planner_agent_name}' did not create the plan file at {self.plan_path}. The agent output was: {plan_result}")
        
        logger.info(f"Strategic plan created at {self.plan_path}")
        print(f"Plan created at {self.plan_path}")

    def get_next_step(self) -> str | None:
        """Reads the plan and returns the next incomplete step."""
        if not self.plan_path.exists():
            return None
        with open(self.plan_path, "r") as f:
            plan_content = f.read()
        
        incomplete_tasks = re.findall(r"-\s*\[\s*\]\s*(.*)", plan_content)
        if not incomplete_tasks:
            return None
        
        return incomplete_tasks[0].strip()

    def _update_plan(self, step: str, result: str):
        """Marks a step as complete and appends the result."""
        with open(self.plan_path, "r") as f:
            content = f.read()
        
        # More flexible regex that handles variations in whitespace and formatting
        step_escaped = re.escape(step.strip())
        pattern = re.compile(r"^(\s*-\s*\[\s*\]\s*.*?" + step_escaped + r".*?)$", re.MULTILINE | re.IGNORECASE)
        
        match = pattern.search(content)
        if match:
            # Replace the unchecked box with a checked one
            old_line = match.group(1)
            new_line = re.sub(r"\[\s*\]", "[x]", old_line)
            new_content = content.replace(old_line, new_line, 1)
            
            # Append the result at the end, but avoid duplicating results
            if f"**Result for '{step}':**" not in new_content:
                new_content += f"\n\n**Result for '{step}':**\n{result}\n---\n"
            
            with open(self.plan_path, "w") as f:
                f.write(new_content)
                
            logger.info(f"Step completed and plan updated: {step[:50]}...")
        else:
            logger.warning(f"Could not find step '{step}' to mark as complete in the plan.")
            # Debug: show what we're looking for vs what's in the file
            print(f"Warning: Could not find step '{step}' to mark as complete in the plan.")
            print(f"Looking for step: '{step}'")
            incomplete_tasks = re.findall(r"-\s*\[\s*\]\s*(.*)", content)
            print(f"Available incomplete steps: {incomplete_tasks[:3]}...")  # Show first 3

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

    async def run(self, planner_agent_name: str):
        """
        Runs the main orchestration loop following AgentX principles.
        
        Coordinates specialist agents to execute strategic plan with professional standards.
        """
        logger.info(f"Starting orchestration workflow with planner: {planner_agent_name}")
        
        if not self.plan_path.exists():
            await self._create_plan(planner_agent_name)

        step_count = 0
        while (step := self.get_next_step()):
            step_count += 1
            logger.info(f"Orchestrating step {step_count}: {step[:100]}...")
            print(f"Executing step: {step}")
            
            worker_agent = await self._get_worker_for_step(step)
            
            # Create comprehensive contextual prompt following AgentX principles
            step_prompt = self._create_step_prompt(step, worker_agent)

            result = await self.task.executor.run_agent(
                agent=worker_agent,
                prompt=step_prompt
            )
            
            self._update_plan(step, str(result))
            logger.info(f"Step {step_count} completed successfully")
            print(f"Step '{step}' completed.")
            await asyncio.sleep(1)

        logger.info("All strategic tasks completed. Orchestration finished.")
        print("All steps completed. Task finished.")
        self.task.complete_task()


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
