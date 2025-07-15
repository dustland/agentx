#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

const API_URL = process.env.NEXT_PUBLIC_AGENTX_API_URL || 'http://localhost:7770';
const HEALTH_CHECK_TIMEOUT = 3000; // 3 seconds
const HEALTH_CHECK_RETRIES = 5;
const RETRY_DELAY = 1000; // 1 second

console.log('🔍 Checking AgentX Backend Server...');

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
          // Verify this is actually AgentX API
          const isAgentX = healthData.service_type === 'agentx-task-orchestration' &&
                          healthData.service_name === 'AgentX API' &&
                          healthData.api_endpoints &&
                          healthData.api_endpoints.includes('/tasks');
          
          if (isAgentX) {
            console.log(`📍 Detected ${healthData.service_name} v${healthData.version} (${healthData.active_tasks} active tasks)`);
          }
          
          resolve(isAgentX);
        } catch (e) {
          // Failed to parse JSON or not AgentX format
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
      console.log('✅ AgentX server is ready!');
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
    console.log(`✅ AgentX server is already running at ${API_URL}`);
    console.log('💡 Using existing server instance.');
    return;
  }

  console.log('🚀 Starting AgentX Backend Server...');

  // Check if we're in the correct directory structure
  const agentxRoot = path.resolve(__dirname, '../../');
  const serverPath = path.join(agentxRoot, 'src/agentx/server');

  if (!fs.existsSync(serverPath)) {
    console.error('❌ AgentX server not found. Make sure you\'re running this from the studio directory.');
    process.exit(1);
  }

  // Start the AgentX server
  const serverProcess = spawn('python', ['-m', 'agentx.server.api'], {
    cwd: agentxRoot,
    stdio: 'inherit',
    env: {
      ...process.env,
      PYTHONPATH: path.join(agentxRoot, 'src'),
    }
  });

  serverProcess.on('close', (code) => {
    console.log(`\n🔴 AgentX server exited with code ${code}`);
    process.exit(code);
  });

  serverProcess.on('error', (error) => {
    console.error('❌ Failed to start AgentX server:', error.message);
    console.log('\n💡 Make sure you have:');
    console.log('   1. Python installed');
    console.log('   2. AgentX dependencies installed (pip install -e .)');
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
    console.log('\n🛑 Shutting down AgentX server...');
    serverProcess.kill('SIGINT');
  });

  process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down AgentX server...');
    serverProcess.kill('SIGTERM');
  });
}

// Run the main function
main().catch((error) => {
  console.error('❌ Unexpected error:', error);
  process.exit(1);
});