#!/usr/bin/env node

/**
 * VibeX Studio Setup Script
 * Ensures all dependencies are up to date and properly configured
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function exec(command, options = {}) {
  try {
    log(`Running: ${command}`, colors.blue);
    execSync(command, { stdio: 'inherit', ...options });
    return true;
  } catch (error) {
    log(`Error: ${error.message}`, colors.red);
    return false;
  }
}

async function main() {
  log('\nVibeX Studio Setup\n', colors.bright);

  // Check if pnpm is installed
  try {
    execSync('pnpm --version', { stdio: 'ignore' });
  } catch {
    log('pnpm is not installed. Installing...', colors.yellow);
    exec('npm install -g pnpm');
  }

  // Update pnpm itself
  log('\nUpdating pnpm...', colors.bright);
  exec('pnpm self-update || npm install -g pnpm@latest');

  // Update all dependencies to latest
  log('\nUpdating all dependencies to latest versions...', colors.bright);
  exec('pnpm update --latest');

  // Install dependencies
  log('\nInstalling dependencies...', colors.bright);
  exec('pnpm install');

  // Check if .env.local exists, if not create from example
  if (!fs.existsSync('.env.local') && fs.existsSync('.env.example')) {
    log('\nCreating .env.local from .env.example...', colors.yellow);
    fs.copyFileSync('.env.example', '.env.local');
    log('Please update .env.local with your configuration', colors.yellow);
  }

  // Install shadcn/ui components
  const components = [
    'button',
    'card',
    'tabs',
    'badge',
    'select',
    'textarea',
    'toast',
    'dialog',
    'dropdown-menu',
    'label',
    'skeleton',
    'separator',
    'scroll-area',
    'avatar',
    'progress',
    'alert',
    'input',
  ];

  log('\nInstalling shadcn/ui components...', colors.bright);
  for (const component of components) {
    log(`Installing ${component}...`, colors.blue);
    exec(`pnpm dlx shadcn@latest add ${component} --yes`);
  }

  // Run type checking
  log('\nRunning type check...', colors.bright);
  const typeCheckSuccess = exec('pnpm tsc --noEmit');

  // Final message
  log('\nSetup complete!', colors.green);
  
  if (!typeCheckSuccess) {
    log('\nWarning: There are TypeScript errors. Please fix them before proceeding.', colors.yellow);
  }

  log('\nNext steps:', colors.bright);
  log('  1. Update .env.local with your VibeX API URL', colors.reset);
  log('  2. Run "pnpm dev" to start the development server', colors.reset);
  log('  3. Open http://localhost:7777 in your browser', colors.reset);
  log('');
}

main().catch((error) => {
  log(`\nSetup failed: ${error.message}`, colors.red);
  process.exit(1);
});