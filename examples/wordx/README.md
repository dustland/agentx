# WordX - AI Assistant for Microsoft Word

**WordX** is a professional Microsoft Word add-in that brings the power of VibeX multi-agent teams directly into your document workflow. Transform your documents with AI-powered review, editing, formatting, and compliance checking.

## Features

- **🤖 Multi-Agent Processing**: Specialized AI agents for different document aspects
- **📄 Document Review**: Comprehensive structure and clarity analysis
- **✍️ Content Editing**: Professional writing enhancement and optimization
- **🎨 Smart Formatting**: Automated layout and presentation improvements
- **✅ Compliance Checking**: Industry standards and regulatory compliance
- **💬 Interactive Chat**: Real-time collaboration with AI agents
- **🔄 Real-Time Updates**: Live progress tracking and feedback

## Architecture

WordX consists of three main components:

1. **VibeX Backend**: FastAPI service with multi-agent teams
2. **Office.js Add-in**: Microsoft Word integration interface
3. **Agent Team**: Specialized AI agents for document processing

### Agent Team

- **Document Reviewer**: Analyzes structure, clarity, and organization
- **Content Editor**: Improves writing quality and engagement
- **Formatter**: Optimizes layout and visual presentation
- **Compliance Auditor**: Ensures standards and regulatory compliance

## Quick Start

### Fastest Setup

```bash
# Run the quickstart script
./quickstart.sh

# Then start the servers
python wordx_setup.py --start-dev
```

### Prerequisites

- Python 3.9+
- Node.js 16+
- Microsoft Word (Desktop or Online)
- uv (Python package manager) - Install from https://github.com/astral-sh/uv
- VibeX framework
- API keys for AI models (DeepSeek, OpenAI, etc.)

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/dustland/vibex.git
cd vibex/examples/wordx

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Unix/macOS
# or: .venv\Scripts\activate  # On Windows

# Install project with dependencies
uv pip install -e .

# Set up environment variables
cd backend
cp environment.template .env
# Edit .env with your API keys

# Start the backend service
python main.py
# Or use the script: python ../wordx_setup.py --start-dev
```

The backend will be available at `http://localhost:7779`

#### Custom Ports

To use custom ports, set these environment variables before starting:

```bash
export WORDX_BACKEND_PORT=7779  # Custom backend port
export WORDX_ADDON_PORT=7778     # Custom add-in port

# Then start the servers
python wordx_setup.py --start-dev
```

### 2. Office.js Add-in Setup

```bash
# Install Office.js development tools
cd addon
pnpm install  # or npm install

# Start the development server
pnpm start  # or npm start
```

The add-in will be available at `https://localhost:7778` (or `http://localhost:7778` if certificates are not configured)

### 3. Word Add-in Installation

1. Open Microsoft Word
2. Go to **Insert** → **My Add-ins** → **Upload My Add-in**
3. Select the `manifest.xml` file from the `addon` directory
4. Click **WordX** in the ribbon to open the task pane

## Usage

### Basic Document Processing

1. **Open a document** in Microsoft Word
2. **Click WordX** in the ribbon to open the task pane
3. **Describe your task** (e.g., "Review for clarity and professionalism")
4. **Select document type** (Business Report, Academic Paper, etc.)
5. **Click "Start Processing"** to begin AI review
6. **Monitor progress** with real-time updates
7. **Chat with agents** for refinements and adjustments

### Command Line Usage

```bash
# First activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or: .venv\Scripts\activate  # On Windows

# Run interactive demo
python main.py

# Run with demo document
python main.py --demo

# Start backend service only
python main.py --backend-only

# Use the setup script for easy installation
python wordx_setup.py --install-deps  # Install all dependencies
python wordx_setup.py --check-env     # Check environment
python wordx_setup.py --start-dev     # Start development servers
```

### API Usage

```python
from vibex import start_task
from pathlib import Path

# Load configuration
config_path = Path("backend/config/team.yaml")

# Create processing task
prompt = """
Document Processing Task:

Task Description: Review this document for clarity and professionalism

Document Content:
[Your document content here]

Please provide comprehensive improvements using the WordX workflow.
"""

# Start processing
x = await start_task(prompt, str(config_path))

# Process with agent team
while not x.is_complete:
    response = await x.step()
    print(f"Agent response: {response}")
```

## Configuration

### Team Configuration

The agent team is configured in `backend/config/team.yaml`:

```yaml
name: "WordX Document Processing Team"
description: "Multi-agent team for professional document processing"

agents:
  document_reviewer:
    name: "Document Reviewer"
    description: "Analyzes document structure and clarity"
    model: "default"
    prompt_file: "prompts/document_reviewer.md"

  content_editor:
    name: "Content Editor"
    description: "Improves writing quality and engagement"
    model: "default"
    prompt_file: "prompts/content_editor.md"

  # ... other agents
```

### Environment Variables

```bash
# Required API keys
DEEPSEEK_API_KEY="your_deepseek_api_key"
OPENAI_API_KEY="your_openai_api_key"
CLAUDE_API_KEY="your_claude_api_key"

# Optional configuration
VIBEX_VERBOSE=1              # Enable verbose logging
WORDX_BACKEND_URL="http://localhost:7779"  # Backend URL
WORDX_TIMEOUT=300             # Processing timeout (seconds)
```

## Document Types

WordX supports specialized processing for different document types:

- **General Documents**: Business communications, reports
- **Academic Papers**: Research papers, theses, articles
- **Business Reports**: Executive summaries, proposals
- **Legal Documents**: Contracts, compliance documents
- **Marketing Materials**: Content marketing, presentations
- **Technical Documentation**: Manuals, specifications

## API Reference

### Backend Endpoints

- `GET /` - Health check
- `POST /api/process-document` - Start document processing
- `GET /api/task-status/{task_id}` - Get processing status
- `POST /api/chat` - Chat with agent team
- `DELETE /api/task/{task_id}` - Cancel processing task

### Request/Response Examples

```javascript
// Start processing
const response = await fetch("/api/process-document", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    content: "Your document content",
    task_description: "Review for clarity",
    document_type: "business",
  }),
});

// Get status
const status = await fetch(`/api/task-status/${taskId}`);
```

## Development

### Project Structure

```
wordx/
├── backend/                 # FastAPI backend service
│   ├── main.py             # Backend application
│   └── config/             # Agent configuration
│       ├── team.yaml       # Team configuration
│       └── prompts/        # Agent prompts
│           ├── document_reviewer.md
│           ├── content_editor.md
│           ├── formatter.md
│           └── compliance_auditor.md
├── addon/                  # Office.js add-in
│   ├── manifest.xml        # Add-in manifest
│   ├── taskpane.html       # Main UI
│   ├── src/
│   │   └── taskpane.js     # Office.js integration
│   └── package.json        # Node.js dependencies
├── pyproject.toml          # Python project configuration (uv)
├── .python-version         # Python version for uv
├── wordx_setup.py          # Setup and installation script
└── main.py                # Example application
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Testing

```bash
# Activate virtual environment first
source .venv/bin/activate  # On Unix/macOS
# or: .venv\Scripts\activate  # On Windows

# Test backend
python -m pytest

# Test Office.js add-in
cd addon
pnpm test  # or npm test

# Validate manifest
pnpm run validate  # or npm run validate
```

## Troubleshooting

### Common Issues

**Backend won't start:**

- Check that all dependencies are installed: `uv pip install -e .`
- Verify API keys are set correctly
- Check port 7779 is available

**Add-in won't load:**

- Ensure development server is running on port 7778
- Check that manifest.xml is valid
- Verify Office.js is supported in your Word version

**Processing fails:**

- Check backend logs for errors
- Verify API keys are working
- Ensure document content is not empty

### Debug Mode

Enable verbose logging:

```bash
export VIBEX_VERBOSE=1
python main.py --backend-only
```

### Support

- **Documentation**: [VibeX Documentation](https://docs.vibex.ai)
- **Issues**: [GitHub Issues](https://github.com/dustland/vibex/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dustland/vibex/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Acknowledgments

- Built with [VibeX](https://github.com/dustland/vibex) multi-agent framework
- Powered by [Office.js](https://docs.microsoft.com/en-us/office/dev/add-ins/) for Word integration
- Uses [FastAPI](https://fastapi.tiangolo.com/) for backend services

---

**WordX** - Transform your documents with AI-powered multi-agent teams. Professional document processing made simple.
