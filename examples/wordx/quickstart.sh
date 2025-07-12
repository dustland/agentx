#!/bin/bash
# WordX Quick Start Script
# This script sets up WordX with uv for package management

set -e  # Exit on error

echo "🚀 WordX Quick Start"
echo "=================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add uv to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
uv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
uv pip install -e .
uv pip install -e .[dev]

# Set up environment file
if [ ! -f backend/.env ]; then
    echo "⚙️  Creating environment file..."
    cp backend/environment.template backend/.env
    echo "📝 Please edit backend/.env with your API keys"
fi

# Install Node.js dependencies
echo "📦 Installing Office.js add-in dependencies..."
cd addon

if command -v pnpm &> /dev/null; then
    pnpm install
else
    npm install
fi

# Generate HTTPS certificates for the add-in
echo "🔐 Generating HTTPS certificates..."
if command -v pnpm &> /dev/null; then
    pnpm run generate-cert || echo "Note: Certificate generation failed, will use HTTP"
else
    npm run generate-cert || echo "Note: Certificate generation failed, will use HTTP"
fi

cd ..

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Start the servers with: python wordx_setup.py --start-dev"
echo "3. Load the add-in in Word using addon/manifest.xml"
echo ""
echo "Happy document processing with WordX! 🎉"
