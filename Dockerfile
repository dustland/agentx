# Dockerfile for VibeX - Production Multi-Stage Build

# --- 1. Web Frontend Build Stage ---
FROM node:20-slim AS web-builder

# Set working directory
WORKDIR /app/web

# Copy web-specific files
COPY web/package.json web/pnpm-lock.yaml ./
COPY web/tsconfig.json web/next.config.ts ./

# Install dependencies
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy the rest of the web source code
COPY web/. .

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
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# --- 3. Final Production Stage ---
FROM python:3.11-slim

LABEL author="VibeX Team"
LABEL description="Production image for VibeX backend and web frontend"

WORKDIR /app

# Install tini for proper process management
RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from the python-base stage
COPY --from=python-base /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=python-base /usr/local/bin/ /usr/local/bin/

# Copy the built web application from the web-builder stage
COPY --from=web-builder /app/web/.next ./web/.next
COPY --from=web-builder /app/web/node_modules ./web/node_modules
COPY --from=web-builder /app/web/public ./web/public
COPY --from=web-builder /app/web/package.json ./web/package.json
COPY --from=web-builder /app/web/next.config.mjs ./web/next.config.mjs

# Copy application source code
COPY . .

# Expose the port the application runs on
EXPOSE 7770

# Use tini to start the application
# This ensures that process signals are handled correctly.
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start both the backend and frontend services
CMD ["sh", "-c", "cd web && npx concurrently --names 'API,WEB' -c 'bgBlue.bold,bgMagenta.bold' 'cd .. && python -m vibex.run --host 0.0.0.0 --port 7770' 'pnpm run start'"] 