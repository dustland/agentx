#!/bin/bash
source .venv/bin/activate
echo "Starting VibeX server on port 7770..."
python -m uvicorn vibex.server.api:app --host 0.0.0.0 --port 7770 --reload