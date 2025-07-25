#!/usr/bin/env python3
import uvicorn
from vibex.server.api import app

if __name__ == "__main__":
    print("Starting VibeX server on port 7770...")
    uvicorn.run(app, host="0.0.0.0", port=7770, log_level="info")