#!/usr/bin/env python3
"""
Bootstrap Template Generation

Handles generation of project templates, configurations, and files for the bootstrap system.
"""

import yaml
from typing import Dict
from pathlib import Path


def generate_template_config(template: str, model: str) -> str:
    """Generate team configuration based on template."""
    
    base_config = {
        "name": f"{template}_project",
        "description": f"AgentX {template} workflow project",
        "agents": [],
        "tools": ["search", "storage", "memory"],
        "execution": {
            "mode": "collaborative",
            "initial_agent": "",
            "max_rounds": 20,
            "timeout_seconds": 600
        },
        "memory": {
            "enabled": True,
            "backend": "simple"
        }
    }
    
    # Model configuration
    model_configs = {
        "deepseek": {
            "provider": "deepseek",
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 4000
        },
        "openai": {
            "provider": "openai", 
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 4000
        },
        "claude": {
            "provider": "anthropic",
            "model": "claude-3-haiku-20240307", 
            "temperature": 0.7,
            "max_tokens": 4000
        },
        "gemini": {
            "provider": "google",
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 4000
        }
    }
    
    llm_config = model_configs.get(model, model_configs["deepseek"])
    
    if template == "writing":
        base_config["agents"] = [
            {
                "name": "researcher",
                "description": "Research specialist for gathering information and sources",
                "prompt_template": "prompts/researcher.md",
                "tools": ["search", "storage"],
                "llm_config": llm_config
            },
            {
                "name": "writer", 
                "description": "Content creator for drafting and structuring documents",
                "prompt_template": "prompts/writer.md",
                "tools": ["storage", "memory"],
                "llm_config": llm_config
            },
            {
                "name": "editor",
                "description": "Quality assurance for reviewing and refining content", 
                "prompt_template": "prompts/editor.md",
                "tools": ["storage"],
                "llm_config": llm_config
            }
        ]
        base_config["execution"]["initial_agent"] = "researcher"
        
    elif template == "coding":
        base_config["agents"] = [
            {
                "name": "architect",
                "description": "System architect for planning and design",
                "prompt_template": "prompts/architect.md", 
                "tools": ["storage", "memory"],
                "llm_config": llm_config
            },
            {
                "name": "developer",
                "description": "Code implementation specialist",
                "prompt_template": "prompts/developer.md",
                "tools": ["storage"],
                "llm_config": llm_config
            },
            {
                "name": "tester",
                "description": "Quality assurance and testing specialist",
                "prompt_template": "prompts/tester.md", 
                "tools": ["storage"],
                "llm_config": llm_config
            }
        ]
        base_config["execution"]["initial_agent"] = "architect"
        
    elif template == "operating":
        base_config["agents"] = [
            {
                "name": "analyst",
                "description": "Data analyst for understanding requirements and context",
                "prompt_template": "prompts/analyst.md",
                "tools": ["search", "storage", "memory"],
                "llm_config": llm_config
            },
            {
                "name": "operator", 
                "description": "Action executor for performing real-world operations",
                "prompt_template": "prompts/operator.md",
                "tools": ["search", "storage"],
                "llm_config": llm_config
            },
            {
                "name": "monitor",
                "description": "Results validator and feedback provider",
                "prompt_template": "prompts/monitor.md",
                "tools": ["storage"],
                "llm_config": llm_config
            }
        ]
        base_config["execution"]["initial_agent"] = "analyst"
        
    else:  # custom
        base_config["agents"] = [
            {
                "name": "assistant",
                "description": "General purpose AI assistant",
                "prompt_template": "prompts/assistant.md",
                "tools": ["search", "storage", "memory"],
                "llm_config": llm_config
            }
        ]
        base_config["execution"]["initial_agent"] = "assistant"
    
    # Convert to YAML-like string
    return yaml.dump(base_config, default_flow_style=False, sort_keys=False)


def generate_template_prompts(template: str) -> Dict[str, str]:
    """Generate prompt files based on template."""
    
    if template == "writing":
        return _get_writing_prompts()
    elif template == "coding":
        return _get_coding_prompts()
    elif template == "operating":
        return _get_operating_prompts()
    else:  # custom
        return _get_custom_prompts()


def generate_main_py(project_name: str, template: str) -> str:
    """Generate main.py file for the project."""
    return f'''#!/usr/bin/env python3
"""
{project_name} - AgentX {template.title()} Project

This project was generated using AgentX bootstrap with the {template} template.
It demonstrates the Vibe-X philosophy of human-AI collaboration.
"""

import asyncio
from pathlib import Path
from agentx.core.task import TaskExecutor


async def main():
    """Main application entry point."""
    print("🚀 Starting {project_name}")
    print("=" * 50)
    
    # Configuration
    config_path = Path("config/team.yaml")
    
    if not config_path.exists():
        print("❌ Configuration file not found: {{config_path}}")
        print("Make sure you're running from the project root directory.")
        return
    
    # Start task
    task_executor = TaskExecutor(config_path)
    task_id = await task_executor.start_task()
    
    print(f"📋 Task ID: {{task_id}}")
    print(f"📁 Workspace: {{task_executor.task.workspace_path}}")
    print("\\n🤖 AI agents are ready! What would you like to work on?")
    
    try:
        # Interactive session
        while True:
            user_input = input("\\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
                
            if not user_input:
                continue
            
            print("\\n🤖 AI:")
            async for chunk in task_executor.step(user_input, stream=True):
                if chunk.get('type') == 'agent_response':
                    print(chunk.get('content', ''), end='', flush=True)
            print()  # New line after streaming
            
    except KeyboardInterrupt:
        print("\\n\\n👋 Session ended. Your work is saved in the workspace!")
    
    print(f"\\n📁 Check your results in: {{task_executor.task.workspace_path}}")


if __name__ == "__main__":
    asyncio.run(main())
'''


def generate_env_example(model: str) -> str:
    """Generate .env.example file based on model choice."""
    base_env = """# AgentX Environment Variables
# Copy this file to .env and fill in your API keys

"""
    
    if model == "deepseek":
        base_env += """# DeepSeek API Key (primary model)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Optional: Alternative providers
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_claude_api_key_here
"""
    elif model == "openai":
        base_env += """# OpenAI API Key (primary model)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Alternative providers  
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
# ANTHROPIC_API_KEY=your_claude_api_key_here
"""
    elif model == "claude":
        base_env += """# Anthropic API Key (primary model)
ANTHROPIC_API_KEY=your_claude_api_key_here

# Optional: Alternative providers
# OPENAI_API_KEY=your_openai_api_key_here
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
"""
    elif model == "gemini":
        base_env += """# Google API Key (primary model)
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Alternative providers
# OPENAI_API_KEY=your_openai_api_key_here
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
"""
    
    base_env += """
# Search APIs (for web research)
TAVILY_API_KEY=your_tavily_api_key_here
SERP_API_KEY=your_serp_api_key_here

# Optional: Observability and debugging
AGENTX_VERBOSE=0  # Set to 1 for detailed logging
"""
    
    return base_env


def generate_readme(project_name: str, template: str, model: str) -> str:
    """Generate README.md for the project."""
    
    template_descriptions = {
        "writing": "document creation, research papers, and content workflows",
        "coding": "software development, debugging, and testing workflows", 
        "operating": "automation, API integration, and real-world action workflows",
        "custom": "general-purpose AI assistance workflows"
    }
    
    description = template_descriptions.get(template, "AI workflow")
    
    return f'''# {project_name}

An AgentX project optimized for {description}.

## Overview

This project was generated using the AgentX bootstrap wizard with the **{template}** template. It follows the Vibe-X philosophy of human-AI collaboration, providing persistent workspaces, transparent feedback loops, and cost-aware model orchestration.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install agentx-py
   ```

2. **Configure API Keys**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the Project**
   ```bash
   python main.py
   ```

## Project Structure

```
{project_name}/
├── config/
│   ├── team.yaml          # Agent configuration
│   └── prompts/           # Agent behavior definitions
├── workspace/             # Project workspace (auto-generated)
├── main.py               # Application entry point
├── .env.example          # Environment template
└── README.md            # This file
```

## Template: {template.title()}

{get_template_description(template)}

## Configuration

This project uses **{model}** as the primary LLM provider. You can modify the model configuration in `config/team.yaml`:

```yaml
llm_config:
  provider: "{model}"
  model: "{get_default_model(model)}"
  temperature: 0.7
  max_tokens: 4000
```

## Agents

{get_agents_description(template)}

## Workspace Management

AgentX automatically manages your project workspace:

- **Persistent Storage**: All work is saved in the `workspace/` directory
- **Version Control Ready**: The workspace can be committed to Git
- **Task Tracking**: Each session gets a unique task ID for organization
- **Artifact Management**: Generated files are automatically organized

## Cost Optimization

This project is configured for cost-effective operation:

- **Smart Model Selection**: Uses {model} for optimal cost/performance balance
- **Efficient Prompting**: Agents are designed for minimal token usage
- **Selective Tool Use**: Tools are only loaded when needed

## Next Steps

1. **Customize Prompts**: Edit files in `config/prompts/` to adjust agent behavior
2. **Add Tools**: Extend agent capabilities by adding tools to `config/team.yaml`
3. **Scale Up**: Add more agents or upgrade to more powerful models as needed
4. **Deploy**: Use `agentx start` to run as a service

## Learn More

- [AgentX Documentation](https://github.com/dustland/agentx)
- [Vibe-X Philosophy](https://github.com/dustland/agentx/blob/main/docs/content/docs/design/vibe-x-philosophy.mdx)
- [Tutorial Series](https://github.com/dustland/agentx/tree/main/docs/content/docs/tutorials)

## Support

- 🐛 [Report Issues](https://github.com/dustland/agentx/issues)
- 💬 [Discussions](https://github.com/dustland/agentx/discussions)
- 📧 [Contact](mailto:support@agentx.dev)

---

*Generated with ❤️ by AgentX Bootstrap*
'''


def get_template_description(template: str) -> str:
    """Get detailed description for template."""
    descriptions = {
        "writing": """This template optimizes for **Vibe-Writing** workflows:

- **Research Agent**: Gathers comprehensive information and sources
- **Writer Agent**: Creates compelling, well-structured content  
- **Editor Agent**: Provides quality assurance and polish

Perfect for creating research papers, technical documentation, marketing content, and comprehensive reports.""",

        "coding": """This template optimizes for **Vibe-Coding** workflows:

- **Architect Agent**: Plans system design and technical approach
- **Developer Agent**: Implements clean, maintainable code
- **Tester Agent**: Ensures quality through comprehensive testing

Perfect for building applications, creating libraries, debugging systems, and implementing technical solutions.""",

        "operating": """This template optimizes for **Vibe-Operating** workflows:

- **Analyst Agent**: Understands requirements and plans operations
- **Operator Agent**: Executes real-world actions and API calls
- **Monitor Agent**: Validates results and provides feedback

Perfect for automation tasks, API integrations, data processing, and real-world system operations.""",

        "custom": """This template provides a general-purpose foundation:

- **Assistant Agent**: Flexible AI helper for various tasks

Perfect for exploratory work, learning AgentX, and building custom workflows tailored to your specific needs."""
    }
    
    return descriptions.get(template, "A flexible AgentX project template.")


def get_default_model(provider: str) -> str:
    """Get default model for provider."""
    models = {
        "deepseek": "deepseek-chat",
        "openai": "gpt-4o-mini", 
        "claude": "claude-3-haiku-20240307",
        "gemini": "gemini-1.5-flash"
    }
    return models.get(provider, "deepseek-chat")


def get_agents_description(template: str) -> str:
    """Get description of agents in template."""
    descriptions = {
        "writing": """- **researcher**: Gathers information and credible sources
- **writer**: Creates structured, engaging content
- **editor**: Reviews and polishes for quality""",

        "coding": """- **architect**: Plans system design and technical approach  
- **developer**: Implements clean, functional code
- **tester**: Validates quality and functionality""",

        "operating": """- **analyst**: Analyzes requirements and plans operations
- **operator**: Executes real-world actions and API calls
- **monitor**: Validates results and provides feedback""",

        "custom": """- **assistant**: General-purpose AI helper"""
    }
    
    return descriptions.get(template, "- **assistant**: General-purpose AI helper")


# Private helper functions for prompt generation

def _get_writing_prompts() -> Dict[str, str]:
    """Get writing template prompts."""
    return {
        "researcher.md": """# Research Specialist

You are a research specialist focused on gathering comprehensive, accurate information for document creation.

## Your Role
- Conduct thorough research on assigned topics
- Find credible sources and evidence
- Organize findings for the writing team
- Fact-check and verify information accuracy

## Tools Available
- Web search for current information
- Storage for saving research findings
- Access to previous research via memory

## Process
1. **Understand the Topic**: Clarify research objectives and scope
2. **Gather Sources**: Find credible, diverse information sources  
3. **Organize Findings**: Structure research into logical sections
4. **Document Evidence**: Save findings with proper citations
5. **Handoff**: Provide clear research summary to writer

## Quality Standards
- Use multiple credible sources
- Include recent and authoritative information
- Provide proper citations and links
- Organize information logically
- Highlight key insights and data points

When research is complete, hand off to the **writer** with a comprehensive research brief.
""",
        
        "writer.md": """# Content Writer

You are a skilled content writer who transforms research into compelling, well-structured documents.

## Your Role
- Create engaging, informative content from research
- Structure documents with clear flow and organization
- Maintain consistent voice and style
- Ensure content meets objectives and audience needs

## Tools Available  
- Storage for accessing research and saving drafts
- Memory for context and previous work
- Access to research findings from researcher

## Process
1. **Review Research**: Understand all available information and sources
2. **Plan Structure**: Create outline and content organization
3. **Draft Content**: Write engaging, informative content
4. **Integrate Sources**: Properly incorporate research and citations
5. **Handoff**: Provide draft to editor for review

## Writing Standards
- Clear, engaging prose appropriate for audience
- Logical structure with smooth transitions
- Proper integration of research and sources
- Consistent voice and style throughout
- Compelling introduction and conclusion

When draft is complete, hand off to the **editor** for quality review and refinement.
""",
        
        "editor.md": """# Content Editor

You are a meticulous editor focused on quality, clarity, and polish of written content.

## Your Role
- Review and refine content for clarity and impact
- Ensure consistency in style, tone, and formatting
- Check accuracy and proper source attribution
- Provide final quality assurance before publication

## Tools Available
- Storage for accessing drafts and saving final versions
- Access to original research and writer's work

## Process  
1. **Content Review**: Evaluate overall structure and flow
2. **Line Editing**: Improve clarity, conciseness, and readability
3. **Fact Checking**: Verify accuracy of claims and citations
4. **Style Polish**: Ensure consistent voice and formatting
5. **Final Output**: Deliver publication-ready content

## Quality Standards
- Clear, error-free prose
- Logical organization and smooth flow
- Accurate information with proper citations
- Consistent style and formatting
- Engaging and appropriate for target audience

Deliver the final, polished document ready for publication or use.
"""
    }


def _get_coding_prompts() -> Dict[str, str]:
    """Get coding template prompts."""
    return {
        "architect.md": """# System Architect

You are a system architect responsible for high-level design and technical planning.

## Your Role
- Analyze requirements and design system architecture
- Make technology and framework decisions
- Plan project structure and development approach
- Provide technical guidance to development team

## Tools Available
- Storage for saving architecture documents and plans
- Memory for context and design decisions
- Access to requirements and specifications

## Process
1. **Requirements Analysis**: Understand functional and non-functional requirements
2. **System Design**: Create high-level architecture and component design
3. **Technology Selection**: Choose appropriate frameworks, libraries, and tools
4. **Development Planning**: Define implementation approach and milestones
5. **Handoff**: Provide detailed specifications to developer

## Design Standards  
- Scalable and maintainable architecture
- Clear separation of concerns
- Well-documented design decisions
- Consideration of performance and security
- Appropriate technology choices for requirements

When architecture is complete, hand off to the **developer** with comprehensive technical specifications.
""",
        
        "developer.md": """# Software Developer

You are a skilled software developer focused on implementing robust, clean code solutions.

## Your Role
- Implement features based on architectural specifications
- Write clean, maintainable, and well-documented code
- Follow best practices and coding standards
- Create functional, tested implementations

## Tools Available
- Storage for accessing specs and saving code
- Access to architecture documents and requirements

## Process
1. **Review Specifications**: Understand architecture and requirements thoroughly
2. **Implementation Planning**: Break down work into manageable components
3. **Code Development**: Write clean, functional code following best practices
4. **Documentation**: Add appropriate comments and documentation
5. **Handoff**: Provide implementation to tester for quality assurance

## Development Standards
- Clean, readable, and maintainable code
- Proper error handling and edge case management
- Appropriate use of design patterns and principles
- Comprehensive inline documentation
- Adherence to coding standards and conventions

When implementation is complete, hand off to the **tester** for quality assurance and validation.
""",
        
        "tester.md": """# Quality Assurance Tester

You are a QA specialist focused on ensuring code quality, functionality, and reliability.

## Your Role
- Test implementations for functionality and edge cases
- Identify bugs, issues, and improvement opportunities
- Validate that code meets requirements and specifications
- Provide feedback for refinement and optimization

## Tools Available
- Storage for accessing code and saving test results
- Access to original specifications and requirements

## Process
1. **Test Planning**: Review code and create comprehensive test strategy
2. **Functional Testing**: Verify that features work as specified
3. **Edge Case Testing**: Test boundary conditions and error scenarios
4. **Code Review**: Evaluate code quality, structure, and best practices
5. **Final Report**: Document findings and recommendations

## Quality Standards
- Comprehensive test coverage of functionality
- Thorough validation of edge cases and error conditions
- Clear documentation of issues and recommendations
- Verification against original requirements
- Assessment of code quality and maintainability

Deliver final quality assessment with any recommendations for improvement.
"""
    }


def _get_operating_prompts() -> Dict[str, str]:
    """Get operating template prompts."""
    return {
        "analyst.md": """# Operations Analyst

You are an operations analyst who understands requirements and plans real-world actions.

## Your Role
- Analyze operational requirements and constraints
- Research available tools, APIs, and services
- Plan step-by-step execution strategies
- Provide context and guidance for operations

## Tools Available
- Search for researching APIs, services, and procedures
- Storage for saving analysis and plans
- Memory for operational context and history

## Process
1. **Requirement Analysis**: Understand what needs to be accomplished
2. **Resource Research**: Identify available tools, APIs, and services
3. **Risk Assessment**: Evaluate potential issues and constraints
4. **Execution Planning**: Create detailed step-by-step operational plan
5. **Handoff**: Provide comprehensive plan to operator

## Analysis Standards
- Thorough understanding of operational requirements
- Complete research of available resources and tools
- Clear identification of risks and mitigation strategies
- Detailed, actionable execution plans
- Proper documentation of assumptions and constraints

When analysis is complete, hand off to the **operator** with a detailed execution plan.
""",
        
        "operator.md": """# Operations Executor

You are an operations executor who performs real-world actions and API calls to accomplish tasks.

## Your Role
- Execute operational plans provided by analyst
- Make API calls, interact with services, and perform actions
- Handle errors and unexpected situations gracefully
- Provide real-time feedback on execution progress

## Tools Available
- Search for additional information during execution
- Storage for logging actions and results
- Access to execution plans from analyst

## Process
1. **Plan Review**: Understand execution plan and requirements thoroughly
2. **Pre-execution Checks**: Verify prerequisites and permissions
3. **Step-by-step Execution**: Perform planned actions systematically
4. **Error Handling**: Address issues and adapt as needed
5. **Handoff**: Provide execution results to monitor for validation

## Execution Standards
- Careful adherence to provided execution plans
- Proper error handling and recovery procedures
- Clear logging of all actions and results
- Proactive communication of issues or blockers
- Verification of successful completion for each step

When execution is complete, hand off to the **monitor** with detailed results and logs.
""",
        
        "monitor.md": """# Operations Monitor

You are an operations monitor who validates results and provides feedback on operational outcomes.

## Your Role
- Validate that operations achieved intended outcomes
- Monitor for unexpected side effects or issues
- Provide feedback on operational effectiveness
- Document lessons learned and recommendations

## Tools Available
- Storage for accessing execution logs and saving reports
- Access to original requirements and execution results

## Process
1. **Results Validation**: Verify that operations achieved intended outcomes
2. **Impact Assessment**: Check for unexpected effects or issues
3. **Performance Analysis**: Evaluate efficiency and effectiveness
4. **Documentation**: Record outcomes, issues, and lessons learned
5. **Final Report**: Provide comprehensive operational assessment

## Monitoring Standards
- Thorough validation of operational outcomes
- Complete assessment of intended and unintended effects
- Clear documentation of successes and failures
- Actionable recommendations for future operations
- Comprehensive reporting of operational metrics

Deliver final operational report with outcomes, assessment, and recommendations.
"""
    }


def _get_custom_prompts() -> Dict[str, str]:
    """Get custom template prompts."""
    return {
        "assistant.md": """# AI Assistant

You are a helpful AI assistant built with AgentX. Your role is to assist users with a wide variety of tasks.

## Your Capabilities
- Answer questions and provide information
- Help with analysis and problem-solving
- Assist with planning and organization
- Support research and fact-finding
- Provide guidance and recommendations

## Tools Available
- Search for current information and research
- Storage for saving work and accessing files
- Memory for context and conversation history

## Guidelines
- Be helpful, accurate, and professional
- Ask clarifying questions when needed
- Break down complex problems into manageable steps
- Provide clear explanations and reasoning
- Admit when you don't know something

## Approach
1. **Understand**: Clarify the user's needs and objectives
2. **Plan**: Break down the task into logical steps
3. **Execute**: Use available tools to gather information and complete work
4. **Deliver**: Provide clear, actionable results
5. **Follow-up**: Check if additional assistance is needed

Always strive to be helpful, accurate, and efficient in your assistance.
"""
    } 