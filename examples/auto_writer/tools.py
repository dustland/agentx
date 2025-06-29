import os
from agentx.builtin_tools.web_tools import WebTool
from agentx.core.tool import tool
from agentx.core.llm import get_llm

# Initialize the tools we'll need internally
web_tool = WebTool()
llm = get_llm()

@tool(
    description="Performs a comprehensive, multi-step research task on a given topic and saves all findings and artifacts.",
    return_description="A summary of the research task and a list of all artifacts created."
)
async def perform_comprehensive_research(topic: str, workspace: str) -> str:
    """
    Orchestrates a full research workflow: planning, searching, extracting, and synthesizing.

    Args:
        topic: The research topic.
        workspace: The path to the task's workspace directory.
    """
    print(f"🔬 Starting comprehensive research for topic: '{topic}'")
    artifacts_dir = os.path.join(workspace, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    # 1. Use an LLM to generate a research plan
    print("  - Generating research plan...")
    plan_prompt = f"Create a research plan with 3-4 distinct sub-queries for the topic: '{topic}'. Return only a numbered list of the queries."
    plan_response = await llm.generate(plan_prompt)
    plan = plan_response.text.strip().split('\n')
    
    plan_content = "# Research Plan\n\n" + "\n".join([f"- [ ] {q.strip()}" for q in plan])
    plan_path = os.path.join(artifacts_dir, "research_plan.md")
    with open(plan_path, 'w') as f:
        f.write(plan_content)
    print(f"  - Research plan saved to {plan_path}")

    # 2. Execute the research loop
    extracted_content_paths = []
    for i, query in enumerate(plan):
        print(f"  - Researching sub-query {i+1}/{len(plan)}: '{query}'")
        
        # a. Search
        search_results = await web_tool.web_search(query=query.strip(), max_results=3)
        search_artifact_path = os.path.join(artifacts_dir, f"search_results_{i+1}.md")
        with open(search_artifact_path, 'w') as f:
            f.write(str(search_results))
        print(f"    - Saved search results to {search_artifact_path}")

        # b. Extract
        if search_results.success and search_results.result:
            urls = [res['url'] for res in search_results.result[:2]] # Extract from top 2 results
            extract_prompt = f"Extract the key findings, statistics, and conclusions from the following content regarding the query: '{query}'"
            extracted_data = await web_tool.extract_content(urls=urls, prompt=extract_prompt)
            
            if extracted_data.success and extracted_data.result:
                extract_artifact_path = os.path.join(artifacts_dir, f"extracted_content_{i+1}.md")
                with open(extract_artifact_path, 'w') as f:
                    f.write(str(extracted_data.result))
                extracted_content_paths.append(extract_artifact_path)
                print(f"    - Saved extracted content to {extract_artifact_path}")
        
        # c. Update plan
        plan_content = plan_content.replace(f"[ ] {query}", f"[x] {query}")
        with open(plan_path, 'w') as f:
            f.write(plan_content)

    # 3. Synthesize the findings
    print("  - Synthesizing all findings...")
    all_extracted_text = ""
    for path in extracted_content_paths:
        with open(path, 'r') as f:
            all_extracted_text += f"\n\n---\n\n" + f.read()

    synthesis_prompt = f"""
    You are a research analyst. The following is a collection of extracted content from multiple sources about '{topic}'.
    Synthesize all of this information into a single, cohesive, and well-structured research brief.
    Ensure the brief is comprehensive and covers all the key findings.

    Extracted Content:
    {all_extracted_text}
    """
    synthesis_response = await llm.generate(synthesis_prompt)
    synthesis = synthesis_response.text

    # 4. Save the final brief
    brief_path = os.path.join(workspace, "research_brief.md")
    with open(brief_path, 'w') as f:
        f.write(synthesis)
    print(f"  - Final research brief saved to {brief_path}")

    return f"Comprehensive research complete. All artifacts and the final research brief have been saved in the workspace." 