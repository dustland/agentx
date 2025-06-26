# AutoWriter - Deep Research Writing System

AutoWriter is a comprehensive multi-agent system based on Google's proven research architecture, designed to generate professional, publication-quality research reports through systematic decomposition and specialized agent orchestration.

## 🎯 Key Features

- **Google-Inspired Architecture**: 5-agent system following proven research methodologies
- **Systematic Research Decomposition**: Breaks complex topics into 5-8 focused sub-queries
- **Two-Stage Content Creation**: DeepSeek-Reasoner for analysis + DeepSeek-Chat for formatting
- **Publication-Quality Output**: Professional reports with comprehensive analysis and insights
- **Source Credibility Assessment**: Multi-tier evaluation of research sources
- **Deep Analytical Reasoning**: Cross-reference analysis and novel insight generation

## 🚀 Quick Start

### Prerequisites

Set up your API key:

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

### Generate a Research Report

```bash
cd examples/auto_writer

# Generate a comprehensive research report
python main.py --topic "Economic Impact of AI Coding Assistants"

# Interactive mode with step-by-step execution
python main.py --topic "Future of Autonomous Vehicles" --interactive

# Custom configuration
python main.py --topic "Climate Tech Innovation" --config path/to/custom/team.yaml
```

## 🤖 Google-Inspired Agent Architecture

### 1. Research Planner Agent

- **Model**: DeepSeek-Chat
- **Role**: Task decomposition and research strategy
- **Output**: 5-8 focused sub-queries with source targeting strategy

### 2. Search Specialist Agent

- **Model**: DeepSeek-Chat
- **Role**: Targeted information gathering with credibility assessment
- **Output**: High-quality sources with credibility scoring

### 3. Content Extractor Agent

- **Model**: DeepSeek-Chat
- **Role**: Deep content analysis and structured data extraction
- **Output**: Organized findings with quality assessment

### 4. Content Reasoner Agent

- **Model**: DeepSeek-Reasoner
- **Role**: Cross-reference analysis and insight generation
- **Output**: Comprehensive analytical reasoning document

### 5. Document Formatter Agent

- **Model**: DeepSeek-Chat
- **Role**: Transform reasoning into polished professional documents
- **Output**: Publication-ready markdown/HTML reports

## 📊 Two-Stage Content Creation

### Stage 1: Deep Reasoning (DeepSeek-Reasoner)

- **Research Synthesizer**: Cross-reference analysis of all findings
- **Content Reasoner**: Deep analytical reasoning and insight generation
- **Output**: Comprehensive reasoning document with novel insights

### Stage 2: Document Formatting (DeepSeek-Chat)

- **Document Formatter**: Transform reasoning into professional presentation
- **Output**: Polished markdown/HTML with proper structure and formatting

## 🔬 Research Methodology

### Phase 1: Planning and Decomposition

1. Analyze research topic scope and dimensions
2. Decompose into 5-8 specific sub-queries
3. Define source targeting strategy
4. Establish success criteria

### Phase 2: Systematic Information Gathering

1. Execute targeted searches for each sub-query
2. Assess source credibility using established criteria
3. Extract relevant data and insights
4. Document search methodology

### Phase 3: Deep Analysis and Synthesis

1. Cross-reference findings across all sub-queries
2. Identify patterns, relationships, and contradictions
3. Generate novel insights through analytical reasoning
4. Develop evidence-based conclusions

### Phase 4: Professional Document Creation

1. Structure reasoning into logical document flow
2. Apply professional formatting and presentation
3. Ensure accessibility and readability
4. Create publication-quality output

## 📋 Report Structure

Generated reports include:

1. **Executive Summary** - Key findings and implications
2. **Methodology** - Research approach and data sources
3. **Key Findings** - Organized by major themes
4. **Analysis and Insights** - Deep analytical reasoning
5. **Strategic Implications** - Opportunities and challenges
6. **Recommendations** - Immediate, medium, and long-term actions
7. **Conclusion** - Synthesis and final thoughts
8. **Appendices** - Source details and methodology

## 🛠️ Configuration

### Team Configuration

The system uses `config/team.yaml` which defines:

- **Agent Models**: DeepSeek-Reasoner for reasoning, DeepSeek-Chat for other tasks
- **Temperature Settings**: Optimized for each agent's role
- **Tool Access**: Web search, content extraction, file operations
- **Routing Logic**: Intelligent orchestration between agents
- **Execution Limits**: Max rounds and timeout settings

### Model Selection Strategy

```yaml
# Reasoning agents use DeepSeek-Reasoner
research_synthesizer:
  model: "deepseek-reasoner"

content_reasoner:
  model: "deepseek-reasoner"

# Other agents use DeepSeek-Chat
research_planner:
  model: "deepseek-chat"

document_formatter:
  model: "deepseek-chat"
```

## 📁 Project Structure

```
auto_writer/
├── main.py                   # Main entry point
├── README.md                 # This documentation
├── config/                   # Core configuration
│   ├── team.yaml            # Agent team configuration
│   └── prompts/             # Agent prompt templates
├── tests/                    # Test files and utilities
│   ├── test_*.py            # Individual test files
│   ├── debug_tools.py       # Debug utilities
│   └── *.yaml               # Test configurations
├── data/                     # Sample data files
└── workspace/               # Generated output files
```

## 📁 Output Files

Generated artifacts are saved to `workspace/`:

```
workspace/
├── research_plan.md          # Initial decomposition and strategy
├── search_results/           # Source findings by sub-query
│   ├── query_1_results.md
│   ├── query_2_results.md
│   └── ...
├── extractions/              # Detailed content analysis
│   ├── query_1_extraction.md
│   ├── query_2_extraction.md
│   └── ...
├── reasoning_document.md     # Deep analytical synthesis
├── final_report.md          # Professional formatted report
└── final_report.html        # HTML version (if requested)
```

## 🧪 Testing and Development

### Tests Directory

The `tests/` directory contains comprehensive test files and debugging utilities:

- **Individual Agent Tests**: Test specific agent functionality
- **Integration Tests**: Test complete research workflows
- **Debug Tools**: Utilities for troubleshooting and development
- **Test Configurations**: Specific configurations for testing scenarios

To run tests:

```bash
# Run individual agent tests
python tests/test_consultant.py
python tests/test_research_flow.py

# Debug available tools
python tests/debug_tools.py
```

## 🔍 Quality Assurance

AutoWriter implements systematic quality controls:

- **Source Credibility**: Three-tier assessment (High/Medium/Low)
- **Information Verification**: Cross-reference validation
- **Analytical Rigor**: Evidence-based reasoning and conclusions
- **Professional Standards**: Publication-quality formatting and presentation
- **Comprehensive Coverage**: Systematic sub-query decomposition

## 🎛️ Advanced Features

### Source Credibility Assessment

**High Credibility**:

- Peer-reviewed academic sources
- Government and institutional reports
- Established industry research organizations

**Medium Credibility**:

- Reputable news with fact-checking
- Professional association reports
- Well-sourced thought leadership

**Low Credibility**:

- Unverified or heavily biased sources
- Outdated information
- Unclear authorship or methodology

### Analytical Frameworks

The Content Reasoner applies established frameworks:

- **SWOT Analysis**: Strengths, Weaknesses, Opportunities, Threats
- **Systems Thinking**: Interconnections and feedback loops
- **Stakeholder Analysis**: Multiple perspectives and interests
- **Scenario Planning**: Future possibilities and implications

## 🏆 Success Criteria

A successful report generation includes:

- ✅ **Systematic Decomposition**: 5-8 focused sub-queries
- ✅ **High-Quality Sources**: Majority from credible, recent sources
- ✅ **Deep Analysis**: Novel insights beyond simple aggregation
- ✅ **Professional Presentation**: Publication-ready formatting
- ✅ **Comprehensive Coverage**: All key dimensions addressed
- ✅ **Evidence-Based Conclusions**: Well-supported recommendations

## 🔧 Troubleshooting

### Common Issues

**Search Quality**: If search results are poor, the Research Planner will refine sub-queries automatically

**Source Access**: Some sources may require subscription access - the system will find alternative sources

**Reasoning Depth**: DeepSeek-Reasoner requires sufficient context - ensure comprehensive extraction phase

**Format Issues**: Document Formatter can generate both markdown and HTML formats as needed

## 📚 Example Usage

```bash
# Basic research report
python main.py --topic "Impact of Remote Work on Corporate Culture"

# Interactive mode for step-by-step control
python main.py --topic "Quantum Computing Applications" --interactive

# Custom topic with specific focus
python main.py --topic "Sustainable Energy Storage Solutions for Grid-Scale Applications"
```

The system will systematically decompose your topic, gather high-quality sources, perform deep analysis, and generate a comprehensive professional report.
