document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const messagesContainer = document.getElementById('messages-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const modelInfo = document.getElementById('model-info');
    
    // Chat state
    let sessionId = null;
    let isWaitingForResponse = false;
    
    // Function to initialize the chat
    function initChat() {
        // Get the session ID and load chat history
        fetch('/api/chat/session')
            .then(response => response.json())
            .then(data => {
                sessionId = data.session_id;
                loadChatHistory();
                loadModelInfo();
            })
            .catch(error => {
                console.error('Error initializing chat:', error);
                addSystemMessage('Error initializing chat. Please try refreshing the page.');
            });
    }
    
    // Function to load model info
    function loadModelInfo() {
        fetch('/api/model-config')
            .then(response => response.json())
            .then(data => {
                if (data.default) {
                    const { provider, model_name } = data.default;
                    modelInfo.textContent = `Using: ${provider} / ${model_name}`;
                } else {
                    modelInfo.textContent = 'No model configured';
                    modelInfo.className = 'badge bg-warning';
                }
            })
            .catch(error => {
                console.error('Error loading model info:', error);
                modelInfo.textContent = 'Error loading model info';
                modelInfo.className = 'badge bg-danger';
            });
    }
    
    // Function to load chat history
    function loadChatHistory() {
        if (!sessionId) return;
        
        fetch(`/api/chat/history?session_id=${sessionId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.history.length > 0) {
                    // Clear the default welcome message
                    messagesContainer.innerHTML = '';
                    
                    // Add each message to the UI
                    data.history.forEach(message => {
                        addMessageToUI(message.role, message.content);
                    });
                    
                    // Scroll to the bottom
                    scrollToBottom();
                }
            })
            .catch(error => {
                console.error('Error loading chat history:', error);
            });
    }
    
    // Function to add a message to the UI
    function addMessageToUI(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process the content for markdown-like formatting
        let formattedContent = content;
        
        // Handle code blocks
        formattedContent = formattedContent.replace(/```([\s\S]*?)```/g, (match, code) => {
            return `<pre><code>${code.trim()}</code></pre>`;
        });
        
        // Handle inline code
        formattedContent = formattedContent.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Handle line breaks
        formattedContent = formattedContent.replace(/\n/g, '<br>');
        
        contentDiv.innerHTML = formattedContent;
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        scrollToBottom();
    }
    
    // Function to add a system message (errors, notifications)
    function addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'alert alert-warning mt-2';
        messageDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${content}`;
        messagesContainer.appendChild(messageDiv);
        
        scrollToBottom();
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message message-assistant typing-indicator-container';
        typingDiv.id = 'typing-indicator';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<span class="typing-indicator">.</span><span class="typing-indicator">.</span><span class="typing-indicator">.</span>';
        
        typingDiv.appendChild(contentDiv);
        messagesContainer.appendChild(typingDiv);
        
        scrollToBottom();
        
        // Animate the typing dots
        let dots = 0;
        const typingDots = document.querySelectorAll('.typing-indicator');
        
        return setInterval(() => {
            typingDots.forEach((dot, i) => {
                dot.style.opacity = (dots % 3 === i) ? '1' : '0.3';
            });
            dots = (dots + 1) % 3;
        }, 300);
    }
    
    // Function to remove typing indicator
    function removeTypingIndicator(interval) {
        clearInterval(interval);
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    // Function to send a chat message
    function sendMessage(message) {
        if (!message.trim() || isWaitingForResponse) return;
        
        // Add user message to UI
        addMessageToUI('user', message);
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        isWaitingForResponse = true;
        const typingInterval = showTypingIndicator();
        
        // Send message to server
        fetch('/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator(typingInterval);
            isWaitingForResponse = false;
            
            if (data.success) {
                // Add assistant's response to UI
                addMessageToUI('assistant', data.response);
                
                // Update session ID if needed
                if (data.session_id) {
                    sessionId = data.session_id;
                }
            } else {
                addSystemMessage(`Error: ${data.error || 'Unknown error occurred'}`);
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            removeTypingIndicator(typingInterval);
            isWaitingForResponse = false;
            addSystemMessage('Error sending message. Please try again.');
        });
    }
    
    // Function to scroll to the bottom of the messages container
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Event listeners
    sendButton.addEventListener('click', function() {
        sendMessage(messageInput.value);
    });
    
    messageInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage(messageInput.value);
        }
    });
    
    // Initialize chat
    initChat();
});
