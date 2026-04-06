document.addEventListener('DOMContentLoaded', function() {
    const trigger = document.getElementById('ai-assistant-trigger');
    const container = document.getElementById('ai-assistant-container');
    const closeBtn = document.getElementById('close-assistant');
    const minimizeBtn = document.getElementById('minimize-assistant');
    const input = document.getElementById('ai-assistant-input');
    const sendBtn = document.getElementById('send-ai-message');
    const chat = document.getElementById('ai-assistant-chat');
    
    // Track conversation history
    let chatHistory = [];

    // Toggle Assistant
    trigger.addEventListener('click', () => {
        container.classList.toggle('ai-assistant-minimized');
        if (!container.classList.contains('ai-assistant-minimized')) {
            input.focus();
        }
    });

    closeBtn.addEventListener('click', () => {
        container.classList.add('ai-assistant-minimized');
    });

    minimizeBtn.addEventListener('click', () => {
        container.classList.add('ai-assistant-minimized');
    });

    // Handle Quick Action Clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('quick-action-btn')) {
            const query = e.target.getAttribute('data-query');
            if (query) {
                input.value = query;
                sendMessage();
            }
        }
    });

    // Send Message
    function sendMessage() {
        const query = input.value.trim();
        if (!query) return;

        // Add user message
        addMessage(query, 'user-message');
        input.value = '';
        
        // Add typing indicator
        const typingId = 'typing-' + Date.now();
        addTypingIndicator(typingId);

        // API Call
        fetch('/api/assistant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                query: query,
                history: chatHistory
            })
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator(typingId);
            
            // Push to history
            chatHistory.push({ role: 'user', content: query });
            chatHistory.push({ role: 'assistant', content: data.response });
            
            // Keep history limited to last 10 messages
            if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);
            
            addMessage(data.response, 'assistant-message', data.products);
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator(typingId);
            addMessage("Sorry, I encountered an error. Please try again later.", 'assistant-message');
        });
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function addMessage(text, className, products = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message ' + className;
        
        // Basic Markdown Support (Bold and links)
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\n/g, '<br>');
        
        msgDiv.innerHTML = formattedText;
        
        chat.appendChild(msgDiv);

        if (products && products.length > 0) {
            products.forEach(product => {
                const pLink = document.createElement('a');
                pLink.href = product.url;
                pLink.className = 'product-suggestion';
                pLink.innerHTML = `
                    <img src="${product.image || 'https://via.placeholder.com/40'}" alt="${product.name}">
                    <div class="suggestion-info">
                        <span class="suggestion-name">${product.name}</span>
                        <span class="suggestion-price">${product.price}</span>
                    </div>
                `;
                chat.appendChild(pLink);
            });
        }

        chat.scrollTop = chat.scrollHeight;
    }

    function addTypingIndicator(id) {
        const indicator = document.createElement('div');
        indicator.id = id;
        indicator.className = 'chat-message assistant-message';
        indicator.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        chat.appendChild(indicator);
        chat.scrollTop = chat.scrollHeight;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
