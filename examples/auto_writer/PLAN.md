# Auto Writer Execution Plan - STRICT

## Goal

Create a high-quality HTML report with REAL content, not fake summaries.

## Principles

1. **No fallbacks** - If a step fails, STOP
2. **Validate outputs** - Check file sizes, content quality
3. **Use actual data** - No mock content or brief summaries
4. **Clear failure reporting** - Know exactly what failed

## Step-by-Step Plan

### Step 1: Initialize Environment ✓

- Create taskspace directory
- Verify artifacts directory exists
- FAIL if taskspace can't be created

### Step 2: Initialize Tools ✓

- Create SearchTool with taskspace
- Create WebTool with taskspace
- FAIL if tools can't access taskspace

### Step 3: Search & Extract Content

- Search for 3-5 queries about web development 2025
- Extract content from top 3 results per query
- **Validation:**
  - Each saved file must exist
  - Each file must be > 5KB (not truncated)
  - Total must be > 30KB of content
- FAIL if extraction produces tiny/no files

### Step 4: Create Research Analysis

- Read all extracted files
- Combine into comprehensive research document
- **Validation:**
  - Research file must be > 10KB
  - Must reference all sources
  - Must contain actual extracted content
- FAIL if research is too brief

### Step 5: Generate HTML Report

- Use VibeX with clear instructions
- Reference the actual research files
- **Validation:**
  - HTML file must exist
  - HTML must be > 10KB
  - Must contain real content from research
- FAIL if no HTML or tiny file

## Expected Results

- 3-9 extracted content files (5-50KB each)
- 1 research analysis file (30KB+)
- 1 HTML report (50KB+)
- Total taskspace: 100KB+ of real content

## NO Fallbacks Policy

- NO "simple extraction" with 3KB limit
- NO brief summaries instead of content
- NO mock data generation
- NO continuing after failures

Each step depends on the previous one succeeding with quality output.
