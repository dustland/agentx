#!/bin/bash

# Start script for Railway deployment
# Ensures backend is ready before starting frontend

echo "[STARTUP] Starting VibeX services..."
echo "[STARTUP] Environment: PORT=$PORT"
echo "[STARTUP] Working directory: $(pwd)"

# Start the backend API in the background
echo "[STARTUP] Starting backend API on port 7770..."
cd /app && python -m vibex.run --host 0.0.0.0 --port 7770 2>&1 | sed 's/^/[BACKEND] /' &
BACKEND_PID=$!

# Wait for backend to be ready
echo "[STARTUP] Waiting for backend to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:7770/health > /dev/null; then
        echo "[STARTUP] Backend is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "[STARTUP] Backend not ready yet... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "[ERROR] Backend failed to start!"
    exit 1
fi

# Start the web frontend  
# Railway typically sets PORT to 8080
FRONTEND_PORT=${PORT:-8080}
echo "[STARTUP] Starting web frontend on port $FRONTEND_PORT..."
cd /app/web && PORT=$FRONTEND_PORT pnpm run start &
FRONTEND_PID=$!

# Function to handle shutdown
cleanup() {
    echo "[SHUTDOWN] Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "[SHUTDOWN] Services stopped."
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID