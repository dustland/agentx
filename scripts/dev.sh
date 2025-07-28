#!/bin/bash

# Kill any existing process on port 7770
echo "🔍 Checking for existing processes on port 7770..."
if lsof -ti:7770 >/dev/null 2>&1; then
    echo "⚡ Killing existing processes on port 7770..."
    lsof -ti:7770 | xargs kill -9
    sleep 1
    echo "✅ Processes killed successfully"
else
    echo "✅ No existing processes found on port 7770"
fi

# Start the development server
echo "🚀 Starting VibeX development server..."
uv run dev 