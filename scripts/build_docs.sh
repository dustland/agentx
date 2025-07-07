#!/bin/bash

# Simple script to build AgentX API documentation
# Uses our custom Python script for clean, comprehensive docs

echo "🔧 Building AgentX API Documentation..."
python scripts/generate_api_docs.py
echo "✅ Done! Documentation is ready at docs/content/api/" 