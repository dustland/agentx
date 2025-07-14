/*
 * WordX - Office.js Integration
 * Copyright (c) AgentX. All rights reserved.
 * Licensed under the MIT License.
 */

// Global variables
let currentTaskId = null;
let statusCheckInterval = null;
let retryCount = 0;
let maxRetries = 3;
let retryDelay = 1000; // Start with 1 second

// Use configured backend URL or default
const API_BASE_URL = (window.WORDX_CONFIG && window.WORDX_CONFIG.BACKEND_URL)
    ? `${window.WORDX_CONFIG.BACKEND_URL}/api`
    : 'http://localhost:8765/api';

// Office.js initialization
Office.onReady((info) => {
    console.log('Office.onReady called with info:', info);
    
    if (info.host === Office.HostType.Word) {
        console.log('WordX add-in loaded successfully');
        console.log('API Base URL:', API_BASE_URL);

        try {
            // Initialize the interface
            initializeInterface();

            // Set up event handlers
            setupEventHandlers();
            
            // Test backend connection
            fetch(`${API_BASE_URL.replace('/api', '')}`)
                .then(res => res.json())
                .then(data => console.log('Backend connected:', data))
                .catch(err => console.error('Backend connection error:', err));
                
        } catch (error) {
            console.error('Error during initialization:', error);
            showError('Failed to initialize add-in: ' + error.message);
        }
    } else {
        console.error('Not running in Word. Host:', info.host);
    }
}).catch((error) => {
    console.error('Office.onReady error:', error);
    document.body.innerHTML = '<div style="padding:20px; color:red;">Error loading Office.js: ' + error.message + '</div>';
});

/**
 * Initialize the user interface
 */
function initializeInterface() {
    // Reset all sections to initial state
    showSection('mainControls');
    hideSection('statusSection');
    hideSection('chatSection');
    hideSection('resultsSection');
    hideSection('errorSection');

    // Clear any existing task
    currentTaskId = null;

    // Clear status check interval
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

/**
 * Set up event handlers
 */
function setupEventHandlers() {
    // Enter key handler for chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
}

/**
 * Show a specific section
 */
function showSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.remove('hidden');
    }
}

/**
 * Hide a specific section
 */
function hideSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('hidden');
    }
}

/**
 * Retry utility function with exponential backoff
 */
async function retryWithBackoff(fn, maxRetries = 3, baseDelay = 1000) {
    let attempt = 0;
    
    while (attempt < maxRetries) {
        try {
            return await fn();
        } catch (error) {
            attempt++;
            
            if (attempt >= maxRetries) {
                throw error;
            }
            
            const delay = baseDelay * Math.pow(2, attempt - 1);
            console.log(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}

/**
 * Make API request with retry logic
 */
async function apiRequest(url, options = {}) {
    return retryWithBackoff(async () => {
        const response = await fetch(url, {
            timeout: 30000, // 30 second timeout
            ...options
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        return response.json();
    }, maxRetries, retryDelay);
}

/**
 * Get the current document content
 */
async function getDocumentContent() {
    return new Promise((resolve, reject) => {
        Word.run(async (context) => {
            try {
                // Get the document body
                const body = context.document.body;

                // Load the text content
                context.load(body, 'text');

                await context.sync();

                resolve(body.text);
            } catch (error) {
                console.error('Error getting document content:', error);
                reject(error);
            }
        });
    });
}

/**
 * Process the document with AgentX
 */
async function processDocument() {
    try {
        // Get task description and document type
        const taskDescription = document.getElementById('taskDescription').value;
        const documentType = document.getElementById('documentType').value;

        if (!taskDescription.trim()) {
            alert('Please describe what you want to do with your document.');
            return;
        }

        // Disable the process button
        const processButton = document.getElementById('processButton');
        processButton.disabled = true;
        processButton.textContent = 'Getting document content...';

        // Get the document content
        const documentContent = await getDocumentContent();

        if (!documentContent.trim()) {
            alert('Your document appears to be empty. Please add some content first.');
            processButton.disabled = false;
            processButton.textContent = 'Start Processing';
            return;
        }

        // Update button text
        processButton.textContent = 'Starting agent team...';

        // Start the processing with retry logic
        const result = await apiRequest(`${API_BASE_URL}/process-document`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: documentContent,
                task_description: taskDescription,
                document_type: documentType
            })
        });
        currentTaskId = result.task_id;

        // Show processing status
        showProcessingStatus();

        // Start monitoring progress
        startStatusMonitoring();

    } catch (error) {
        console.error('Error processing document:', error);
        showError('Failed to start document processing. Please check your connection and try again.');
    }
}

/**
 * Analyze document only (no changes)
 */
async function analyzeDocument() {
    try {
        const taskDescription = "Analyze this document and provide feedback on structure, clarity, and areas for improvement. Do not make any changes.";
        const documentType = document.getElementById('documentType').value;

        // Set the task description
        document.getElementById('taskDescription').value = taskDescription;

        // Process the document
        await processDocument();

    } catch (error) {
        console.error('Error analyzing document:', error);
        showError('Failed to analyze document. Please try again.');
    }
}

/**
 * Show processing status section
 */
function showProcessingStatus() {
    hideSection('mainControls');
    showSection('statusSection');

    // Reset progress
    updateProgress(0, 'Initializing agent team...');
    updateCurrentAgent('Document Reviewer');
}

/**
 * Start monitoring the processing status
 */
function startStatusMonitoring() {
    if (!currentTaskId) return;

    let statusRetryCount = 0;
    const maxStatusRetries = 5;

    statusCheckInterval = setInterval(async () => {
        try {
            const status = await retryWithBackoff(async () => {
                const response = await fetch(`${API_BASE_URL}/task-status/${currentTaskId}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return response.json();
            }, 2, 1000); // Shorter retry for status checks

            // Reset retry count on successful request
            statusRetryCount = 0;

            // Update progress
            updateProgress(status.progress * 100, getStatusMessage(status));

            if (status.current_agent) {
                updateCurrentAgent(status.current_agent);
            }

            // Check if completed
            if (status.status === 'completed') {
                clearInterval(statusCheckInterval);
                showProcessingComplete();
            } else if (status.status === 'failed' || status.status === 'error') {
                clearInterval(statusCheckInterval);
                showError(status.final_result || 'Processing failed');
            }

        } catch (error) {
            console.error('Error checking status:', error);
            statusRetryCount++;
            
            if (statusRetryCount >= maxStatusRetries) {
                clearInterval(statusCheckInterval);
                showError('Lost connection to processing service. Please check your internet connection and try again.');
            } else {
                // Show temporary connection issue warning
                updateProgress(null, `Connection issue (${statusRetryCount}/${maxStatusRetries})... retrying`);
            }
        }
    }, 3000); // Check every 3 seconds (slightly slower to reduce load)
}

/**
 * Update the progress bar and message
 */
function updateProgress(percent, message) {
    const progressFill = document.getElementById('progressFill');
    const statusMessage = document.getElementById('statusMessage');

    if (progressFill && percent !== null && percent !== undefined) {
        progressFill.style.width = `${Math.max(0, Math.min(100, percent))}%`;
    }

    if (statusMessage) {
        statusMessage.innerHTML = `<div class="spinner"></div>${message}`;
    }
}

/**
 * Update the current agent display
 */
function updateCurrentAgent(agentName) {
    const currentAgent = document.getElementById('currentAgent');
    if (currentAgent) {
        currentAgent.textContent = agentName;
    }
}

/**
 * Get status message based on progress
 */
function getStatusMessage(status) {
    if (status.progress < 0.25) {
        return 'Document reviewer analyzing structure...';
    } else if (status.progress < 0.5) {
        return 'Content editor improving clarity...';
    } else if (status.progress < 0.75) {
        return 'Formatter optimizing layout...';
    } else if (status.progress < 1.0) {
        return 'Compliance auditor checking standards...';
    } else {
        return 'Processing complete!';
    }
}

/**
 * Show processing complete
 */
function showProcessingComplete() {
    hideSection('statusSection');
    showSection('chatSection');
    showSection('resultsSection');

    // Add completion message to chat
    addChatMessage('agent', 'Document processing completed! Your document has been reviewed and improved. You can now chat with us to make further refinements.');
}

/**
 * Show error section
 */
function showError(message) {
    hideSection('statusSection');
    showSection('errorSection');

    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
    }
}

/**
 * Send a chat message to the agent team
 */
async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message || !currentTaskId) return;

    // Add user message to chat
    addChatMessage('user', message);

    // Clear input
    chatInput.value = '';

    // Add thinking indicator
    addChatMessage('agent', 'Agent team is thinking...');

    try {
        const result = await apiRequest(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_id: currentTaskId,
                message: message
            })
        });

        // Remove thinking indicator
        removeChatThinking();

        // Add agent response
        addChatMessage('agent', result.response);

    } catch (error) {
        console.error('Error sending chat message:', error);
        removeChatThinking();
        
        if (error.message.includes('HTTP 404')) {
            addChatMessage('agent', 'The processing session has expired. Please start a new document processing task.');
        } else if (error.message.includes('timeout') || error.message.includes('network')) {
            addChatMessage('agent', 'Network connection issue. Please check your internet connection and try again.');
        } else {
            addChatMessage('agent', 'Sorry, there was an error communicating with the agent team. Please try again.');
        }
    }
}

/**
 * Add a message to the chat container
 */
function addChatMessage(sender, message) {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;

    if (sender === 'agent') {
        messageDiv.innerHTML = `<strong>Agent Team:</strong> ${message}`;
    } else {
        messageDiv.innerHTML = `<strong>You:</strong> ${message}`;
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Remove thinking indicator from chat
 */
function removeChatThinking() {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;

    const messages = chatContainer.querySelectorAll('.chat-message');
    const lastMessage = messages[messages.length - 1];

    if (lastMessage && lastMessage.textContent.includes('thinking...')) {
        lastMessage.remove();
    }
}

/**
 * Reset the interface to initial state
 */
function resetInterface() {
    // Clear current task
    currentTaskId = null;

    // Clear status check interval
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }

    // Reset form
    document.getElementById('taskDescription').value = '';
    document.getElementById('documentType').value = 'general';

    // Reset button
    const processButton = document.getElementById('processButton');
    processButton.disabled = false;
    processButton.textContent = 'Start Processing';

    // Clear chat
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer) {
        chatContainer.innerHTML = '<div class="chat-message agent"><strong>Agent Team:</strong> Ready to help with your next document!</div>';
    }

    // Show initial interface
    initializeInterface();
}

/**
 * Handle Enter key in chat input
 */
function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

// Export functions for global access
window.processDocument = processDocument;
window.analyzeDocument = analyzeDocument;
window.sendChatMessage = sendChatMessage;
window.resetInterface = resetInterface;
window.handleChatKeyPress = handleChatKeyPress;
