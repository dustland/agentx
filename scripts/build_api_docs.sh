#!/bin/bash

# Build AgentX API Documentation using pydoc-markdown
# This script generates MDX files compatible with Nextra

set -e

echo "🔧 Building AgentX API Documentation..."

# Clean existing docs (remove both old agentx folder and any generated files)
rm -rf docs/content/api/agentx
rm -rf docs/content/api/core
rm -rf docs/content/api/builtin_tools
rm -rf docs/content/api/cli
rm -rf docs/content/api/config
rm -rf docs/content/api/event
rm -rf docs/content/api/memory
rm -rf docs/content/api/search
rm -rf docs/content/api/storage
rm -rf docs/content/api/tool
rm -rf docs/content/api/utils

# Generate new docs
pydoc-markdown

# Convert .md files to .mdx for Nextra compatibility
find docs/content/api -name "*.md" -exec sh -c 'mv "$1" "${1%.md}.mdx"' _ {} \;

# Flatten the structure by moving contents from agentx folder up one level
if [ -d "docs/content/api/agentx" ]; then
    cd docs/content/api
    mv agentx/* .
    rmdir agentx
    cd - > /dev/null
fi

# Create proper Nextra _meta.js file
cat > docs/content/api/_meta.js << 'EOF'
export default {
  "core": "Core",
  "builtin_tools": "Builtin Tools",
  "cli": "CLI",
  "config": "Configuration",
  "event": "Events",
  "memory": "Memory",
  "search": "Search",
  "storage": "Storage",
  "tool": "Tools",
  "utils": "Utils"
}
EOF

echo "✅ API Documentation built successfully!"
echo "📖 Documentation available at: docs/content/api/" 