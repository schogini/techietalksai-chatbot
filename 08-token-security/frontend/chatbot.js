function decodeHTMLEntities(text) {
    const textarea = document.createElement("textarea");
    textarea.innerHTML = text;
    return textarea.value;
}

const Chatbot = {
    init(options) {
        this.backendUrl = options.backendUrl;
        this.session_id = null;
        this.createChatUI();
        this.getSession();
        this.setupEventListeners();
    },

    setupEventListeners() {
        const chatIcon = document.getElementById('chat-icon');
        const chatContainer = document.getElementById('chat-container');
        const closeBtn = document.getElementById('chat-close-btn');

        chatIcon.addEventListener('click', () => {
            chatContainer.classList.toggle('hidden');
        });

        closeBtn.addEventListener('click', () => {
            chatContainer.classList.add('hidden');
        });
    },

    createChatUI() {
        const container = document.getElementById('chat-container');

        const header = document.createElement('div');
        header.id = 'chat-header';
        
        const title = document.createElement('span');
        title.textContent = 'Chat with us!';
        
        const closeBtn = document.createElement('button');
        closeBtn.id = 'chat-close-btn';
        closeBtn.innerHTML = '&times;';

        header.appendChild(title);
        header.appendChild(closeBtn);
        container.appendChild(header);

        const messages = document.createElement('div');
        messages.id = 'chat-messages';
        container.appendChild(messages);

        const inputContainer = document.createElement('div');
        inputContainer.id = 'chat-input-container';

        const input = document.createElement('input');
        input.id = 'chat-input';
        input.type = 'text';
        input.placeholder = 'Type a message...';
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        const sendBtn = document.createElement('button');
        sendBtn.id = 'chat-send-btn';
        sendBtn.innerHTML = '&#10148;';
        sendBtn.onclick = () => this.sendMessage();

        inputContainer.appendChild(input);
        inputContainer.appendChild(sendBtn);
        container.appendChild(inputContainer);
    },

    async getSession() {
        try {
            const response = await fetch(`${this.backendUrl}/session`, {
                method: 'POST'
            });
            const data = await response.json();
            this.session_id = data.session_id;
            this.addMessage('<strong>Hello!</strong> How can I help you today?', 'bot-message');
        } catch (error) {
            console.error('Error getting session:', error);
            this.addMessage('Error connecting to the chatbot.', 'bot-message');
        }
    },

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (!message) return;

        this.addMessage(message, 'user-message');
        input.value = '';

        if (!this.session_id) {
            this.addMessage('Not connected to the server.', 'bot-message');
            return;
        }

        try {
            const response = await fetch(`${this.backendUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.session_id}`
                },
                body: JSON.stringify({ message: message })
            });

            if (response.status === 429) {
                this.addMessage("I'm getting a lot of requests right now. Please try again in a moment.", 'bot-message');
                return;
            } else if (!response.ok) {
                this.addMessage("I'm having trouble connecting. Please try again later.", 'bot-message');
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let botMessageElement = this.addMessage('', 'bot-message');

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n\n');

                botMessageElement.innerHTML = marked.parse(chunk.substring(6)); //data: 
                /*
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        // botMessageElement.textContent += line.substring(6);
                        botMessageElement.innerHTML = marked.parse(line.substring(6));
                    }
                }
                */
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage("I'm having trouble connecting. Please check your internet connection and try again.", 'bot-message');
        }
    },

    addMessage(text, className) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        // messageElement.textContent = text;
        // messageElement.innerHTML = text;
        // messageElement.innerHTML = decodeHTMLEntities(text);
        messageElement.innerHTML = marked.parse(text);
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return messageElement;
    }
};
