#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

const API_URL = process.env.NEXT_PUBLIC_VIBEX_API_URL || 'http://localhost:7770';
const HEALTH_CHECK_TIMEOUT = 3000; // 3 seconds
const HEALTH_CHECK_RETRIES = 5;
const RETRY_DELAY = 1000; // 1 second

console.log('🔍 Checking VibeX Backend Server...');

// Parse API URL
const apiUrl = new URL(API_URL);

// Function to check if server is already running and is AgentX
async function checkHealth() {
  return new Promise((resolve) => {
    const options = {
      hostname: apiUrl.hostname,
      port: apiUrl.port || 80,
      path: '/health',
      method: 'GET',
      timeout: HEALTH_CHECK_TIMEOUT,
    };

    const req = http.request(options, (res) => {
      if (res.statusCode !== 200) {
        resolve(false);
        return;
      }

      let data = '';
      res.on('data', chunk => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const healthData = JSON.parse(data);
          // Verify this is actually VibeX API
          const isVibeX = healthData.service_type === 'vibex-task-orchestration' &&
                          healthData.service_name === 'VibeX API' &&
                          healthData.api_endpoints &&
                          healthData.api_endpoints.includes('/tasks');
          
          if (isVibeX) {
            console.log(`📍 Detected ${healthData.service_name} v${healthData.version} (${healthData.active_tasks} active tasks)`);
          }
          
          resolve(isVibeX);
        } catch (e) {
          // Failed to parse JSON or not VibeX format
          resolve(false);
        }
      });
    });

    req.on('error', () => {
      resolve(false);
    });

    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

// Function to wait for server to be ready
async function waitForServer(retries = HEALTH_CHECK_RETRIES) {
  for (let i = 0; i < retries; i++) {
    console.log(`⏳ Waiting for server to be ready... (${i + 1}/${retries})`);
    const isHealthy = await checkHealth();
    if (isHealthy) {
      console.log('✅ VibeX server is ready!');
      return true;
    }
    if (i < retries - 1) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
    }
  }
  return false;
}

// Main function
async function main() {
  // Check if server is already running
  const isRunning = await checkHealth();
  
  if (isRunning) {
    console.log(`✅ VibeX server is already running at ${API_URL}`);
    console.log('💡 Using existing server instance.');
    return;
  }

  console.log('🚀 Starting VibeX Backend Server...');

  // Check if we're in the correct directory structure
  const vibexRoot = path.resolve(__dirname, '../../');
  const serverPath = path.join(vibexRoot, 'src/vibex/server');

  if (!fs.existsSync(serverPath)) {
    console.error('❌ VibeX server not found. Make sure you\'re running this from the studio directory.');
    process.exit(1);
  }

  // Start the VibeX server
  const serverProcess = spawn('python', ['-m', 'vibex.server.api'], {
    cwd: vibexRoot,
    stdio: 'inherit',
    env: {
      ...process.env,
      PYTHONPATH: path.join(vibexRoot, 'src'),
    }
  });

  serverProcess.on('close', (code) => {
    console.log(`\n🔴 VibeX server exited with code ${code}`);
    process.exit(code);
  });

  serverProcess.on('error', (error) => {
    console.error('❌ Failed to start VibeX server:', error.message);
    console.log('\n💡 Make sure you have:');
    console.log('   1. Python installed');
    console.log('   2. VibeX dependencies installed (pip install -e .)');
    console.log('   3. Running from the correct directory');
    process.exit(1);
  });

  // Wait for server to be ready
  const isReady = await waitForServer();
  if (!isReady) {
    console.error('❌ Server failed to start within timeout period');
    serverProcess.kill('SIGTERM');
    process.exit(1);
  }

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down VibeX server...');
    serverProcess.kill('SIGINT');
  });

  process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down VibeX server...');
    serverProcess.kill('SIGTERM');
  });
}

// Run the main function
main().catch((error) => {
  console.error('❌ Unexpected error:', error);
  process.exit(1);
});