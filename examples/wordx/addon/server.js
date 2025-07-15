#!/usr/bin/env node
/**
 * Simple HTTPS server for WordX Office Add-in
 * Uses port 7778 to avoid conflicts
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration
const PORT = process.env.WORDX_ADDON_PORT || 7778;
const HOST = '0.0.0.0';

// Certificate paths for Office Add-in development
const certPath = path.join(os.homedir(), '.office-addin-dev-certs', 'localhost.crt');
const keyPath = path.join(os.homedir(), '.office-addin-dev-certs', 'localhost.key');

// Check if certificates exist
if (!fs.existsSync(certPath) || !fs.existsSync(keyPath)) {
    console.error('❌ HTTPS certificates not found!');
    console.error('Run: pnpm run generate-cert');
    process.exit(1);
}

// Read certificates
const options = {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath)
};

// Static file server
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

// Create HTTPS server
const server = https.createServer(options, (req, res) => {
    console.log(`${req.method} ${req.url}`);

    // Parse URL
    let filePath = '.' + req.url;
    if (filePath === './') {
        filePath = './taskpane.html';
    }

    // Get file extension
    const extname = String(path.extname(filePath)).toLowerCase();
    const contentType = mimeTypes[extname] || 'application/octet-stream';

    // Read and serve file
    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                res.writeHead(404);
                res.end('File not found');
            } else {
                res.writeHead(500);
                res.end('Server error: ' + error.code);
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

// Start server
server.listen(PORT, HOST, () => {
    console.log('🚀 WordX Add-in Server');
    console.log(`📡 Listening on https://localhost:${PORT}`);
    console.log('📂 Serving files from:', process.cwd());
    console.log('');
    console.log('✅ Ready for Office Add-in connections');
});

// Handle shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down server...');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});