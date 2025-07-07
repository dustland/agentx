#!/bin/bash

# Build AgentX API Documentation using pydoc-markdown
# This script generates MDX files compatible with Nextra

set -e

echo "🔧 Building AgentX API Documentation..."

# Clean existing docs
rm -rf docs/content/api/agentx

# Generate new docs
pydoc-markdown

# Convert .md files to .mdx for Nextra compatibility
find docs/content/api -name "*.md" -exec sh -c 'mv "$1" "${1%.md}.mdx"' _ {} \;

echo "✅ API Documentation built successfully!"
echo "📖 Documentation available at: docs/content/api/" 