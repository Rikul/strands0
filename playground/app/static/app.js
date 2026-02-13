document.addEventListener('DOMContentLoaded', () => {

    // DOM Elements
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    // user/session controls removed
    // system prompt + model settings panels removed

    // Defensive: if the markup is customized, avoid hard crashes.
    if (!chatMessages || !userInput || !sendButton) {
        console.error('Missing core chat UI elements.');
        return;
    }
    
    // API endpoints
    const API_BASE_URL = '';
    const GET_CONVERSATIONS_ENDPOINT = `${API_BASE_URL}/get_conversations`;
    const CS_AGENT_ENDPOINT = `${API_BASE_URL}/strandsplayground_agent`;
    // endpoints kept (backend supports them), but UI no longer exposes controls.
    const SYSTEM_PROMPT_ENDPOINT = `${API_BASE_URL}/system_prompt`;
    const MODEL_SETTINGS_ENDPOINT = `${API_BASE_URL}/model_settings`;
    
    // State
    let userId = 'user1';
    let isProcessing = false;
    
    // Initialize chat
    loadConversation();
    
    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });


    // User/session switching removed; fixed userId = 'user1'
    
    // Functions
    async function loadConversation() {
        try {
            chatMessages.innerHTML = '<div class="loading"></div>';
            
            const response = await fetch(`${GET_CONVERSATIONS_ENDPOINT}?userId=${encodeURIComponent(userId)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            displayConversation(data.messages);
        } catch (error) {
            console.error('Error loading conversation:', error);
            chatMessages.innerHTML = '';
            showError('Failed to load conversation. Please try again.');
        }
    }
    
    function displayConversation(messages) {
        chatMessages.innerHTML = '';
        
        if (!messages || messages.length === 0) {
            const welcomeMsg = document.createElement('div');
            welcomeMsg.className = 'message bot-message';
            welcomeMsg.textContent = "Welcome to Strands Playground, let's get started!";
            chatMessages.appendChild(welcomeMsg);
            
            // Add note about file access
            return;
        }
        
        messages.forEach(msg => {
            if (msg.role === 'user' || msg.role === 'assistant') {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`;
                
                const responseText = msg.content[0].text;
                messageDiv.textContent = responseText;
                
                chatMessages.appendChild(messageDiv);
            }
        });
        
        scrollToBottom();
    }
    
    async function sendMessage() {
        const message = userInput.value.trim();
        
        if (!message || isProcessing) return;
        
        // Add user message to chat
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'message user-message';
        userMessageDiv.textContent = message;
        chatMessages.appendChild(userMessageDiv);
        
        // Clear input and scroll to bottom
        userInput.value = '';
        scrollToBottom();
        
        // Show loading indicator in chat
        isProcessing = true;
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message';
        loadingDiv.innerHTML = '<div class="loading"></div>';
        chatMessages.appendChild(loadingDiv);
        
        // Show loading indicator in summary panel
        if (window.showSummaryLoading) {
            window.showSummaryLoading();
        }
        
        try {
            const startTime = Date.now();
            
            const response = await fetch(CS_AGENT_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: message,
                    userId: userId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove loading indicator
            chatMessages.removeChild(loadingDiv);
            
            // Add bot response
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot-message';
            
            const responseText = data.messages.content[0].text;
            botMessageDiv.textContent = responseText;
            
            chatMessages.appendChild(botMessageDiv);
            
            // Update summary panel if available
            if (data.summary && window.updateSummaryPanel) {
                console.log(data.summary);
                window.updateSummaryPanel(data.summary);
            }
            
            scrollToBottom();
        } catch (error) {
            console.error('Error sending message:', error);
            chatMessages.removeChild(loadingDiv);
            showError('Failed to send message. Please try again.');
        } finally {
            isProcessing = false;
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // System prompt + model settings panels removed
    
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        chatMessages.appendChild(errorDiv);
        
        setTimeout(() => {
            chatMessages.removeChild(errorDiv);
        }, 5000);
        
        scrollToBottom();
    }
    
    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        chatMessages.appendChild(successDiv);
        
        setTimeout(() => {
            chatMessages.removeChild(successDiv);
        }, 3000);
        
        scrollToBottom();
    }
});