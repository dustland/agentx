#!/bin/bash

# Build AgentX API Documentation using Sphinx + AutoAPI
# This script builds the HTML documentation and opens it in the browser

set -e

echo "🔧 Building AgentX API Documentation..."
make clean
make html

echo "✅ Documentation built successfully!"
echo "📖 Documentation available at: _build/html/index.html"

# Optionally open in browser (uncomment if desired)
# open _build/html/index.html  # macOS
# xdg-open _build/html/index.html  # Linux 