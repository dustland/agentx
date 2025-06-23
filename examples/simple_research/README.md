# Simple Research Example

This example demonstrates the **correct methodology** for conducting comprehensive web research using AgentX's `web_search` and `extract_content` tools.

## Purpose

Demonstrates the critical importance of **agent prompts** in guiding research methodology:

- 🎯 **Simple task prompt**: "Research quantum computing for drug discovery"
- 🧠 **Detailed agent prompt**: Contains all the methodology, examples, and quality standards
- 📊 **Result**: Comprehensive research despite minimal task instructions

## The Problem

Many users make this mistake:

```python
# This produces shallow, brief content
extract_content(urls, "summarize AI in healthcare")
```

Result: Brief bullet points with no depth, like:

- AI helps with diagnostics
- Machine learning improves treatment
- Challenges include privacy

## The Solution

Use detailed, structured extraction prompts:

```python
# This produces comprehensive, valuable content
extract_content(urls, "Extract comprehensive information about AI in healthcare including: 1) Specific diagnostic tools and their accuracy rates, 2) Real-world implementation examples with hospital names and outcomes, 3) Technical details about algorithms used, 4) Cost-benefit analysis and ROI data, 5) Regulatory approval status and FDA guidelines...")
```

Result: Detailed analysis with specific data, company names, case studies, expert opinions, and actionable insights.

## What This Example Demonstrates

1. **Strategic Search Planning**: Breaking topics into focused, searchable questions
2. **Effective Search Queries**: Using specific terms rather than generic ones
3. **Detailed Extraction Prompts**: Asking for comprehensive information with specific categories
4. **Quality Documentation**: Saving findings with full context and analysis

## Usage

```bash
cd examples/simple_research
python main.py
```

## Expected Output

The researcher will demonstrate:

- Planning a research strategy for quantum computing in drug discovery
- Executing focused web searches
- Using detailed extraction prompts to get comprehensive content
- Documenting findings with full context and analysis

Check the workspace folder for the detailed research files created.

## Key Learning

**Agent prompts are where the intelligence lives.** A simple 6-word task prompt becomes comprehensive research because the agent prompt contains:

- Detailed methodology and step-by-step instructions
- Examples of good vs bad extraction prompts
- Quality standards and expectations
- Specific techniques for getting valuable content

The task prompt can be simple - the agent prompt does the heavy lifting.

## The Demonstration

**Task Prompt**: "Research quantum computing for drug discovery" (6 words!)

**What the Agent Will Do** (guided by its prompt):

1. Plan research strategy and break down the topic
2. Execute focused web searches with specific terms
3. Use detailed extraction prompts to get comprehensive content
4. Document findings with full context and analysis
5. Demonstrate good vs bad extraction techniques

**Expected Output**:

- Comprehensive research files with detailed analysis
- Specific company names, partnerships, and case studies
- Technical details and expert opinions
- Real financial data and market projections
- Complete source citations and context

All from a 6-word task prompt - because the agent prompt contains the methodology!
