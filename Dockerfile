# Dockerfile for VibeX - Production Multi-Stage Build

# --- 1. Web Frontend Build Stage ---
FROM node:20-slim AS web-builder

# Set working directory
WORKDIR /app/web

# Copy package files first for better caching
COPY web/package.json web/pnpm-lock.yaml ./


# Install pnpm and dependencies
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile --prefer-offline

# Copy the rest of the web directory
COPY web/ .

# Build the Next.js application
RUN pnpm run build

# --- 2. Python Backend Stage ---
FROM python:3.11-slim AS python-base

# Set working directory
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary files for installation first
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY benchmark/ ./benchmark/

# Upgrade pip and install the package
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# --- 3. Final Production Stage ---
FROM python:3.11-slim

LABEL author="VibeX Team"
LABEL description="Production image for VibeX backend and web frontend"

WORKDIR /app

# Install runtime dependencies including tini for proper process management and Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    curl \
    git \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm \
    && rm -rf /var/lib/apt/lists/*

# Install uv via pip (more reliable in Docker)
RUN pip install uv

# Copy Python dependencies from the python-base stage
COPY --from=python-base /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=python-base /usr/local/bin/ /usr/local/bin/

# Copy the built web application from the web-builder stage
COPY --from=web-builder /app/web/.next ./web/.next
COPY --from=web-builder /app/web/node_modules ./web/node_modules
COPY --from=web-builder /app/web/public ./web/public
COPY --from=web-builder /app/web/package.json ./web/package.json
COPY --from=web-builder /app/web/next.config.ts ./web/next.config.ts

# Copy application source code
COPY . .

# No startup script needed - running directly

# Expose the ports the applications run on
# Railway typically uses 8080 for the main service
EXPOSE 8080 7770

# Use tini to start the application
# This ensures that process signals are handled correctly.
ENTRYPOINT ["/usr/bin/tini", "--"]

# Create startup script inline
RUN echo '#!/bin/bash\n\
echo "Starting VibeX services..."\n\
cd /app && BACKEND_PORT=7770 uv run prod &\n\
BACKEND_PID=$!\n\
cd /app/web && PORT=${PORT:-8080} pnpm run start &\n\
FRONTEND_PID=$!\n\
wait $BACKEND_PID $FRONTEND_PID' > /start.sh && chmod +x /start.sh

# Expose both ports
EXPOSE 7770 8080

# Run both services
CMD ["/start.sh"] 