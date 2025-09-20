const ChatbotWidget = {
    // FAQ Data
    faqData: {
        "how does renting work": {
            answer: "Renting with CultureWear is simple! 📝\n\n1. **Browse** our collection of authentic cultural attire\n2. **Select** your size and rental period\n3. **Pay** securely with XRPL tokens or traditional methods\n4. **Receive** your outfit with automated delivery tracking\n5. **Wear** and enjoy your event!\n6. **Return** using the prepaid label and earn StylePoints\n\nEach garment has a digital passport showing its history, cleaning records, and reviews from previous renters. You'll know exactly what you're getting!",
            followUp: ["What are StylePoints?", "How do payments work?", "What if the item doesn't fit?"]
        },
        "what are stylepoints": {
            answer: "StylePoints are our blockchain-based reward system! 💎\n\n**How they work:**\n• Earn points for every rental, review, and referral\n• Points are stored as FAssets on the Flare network\n• They have real USD value and can be traded\n\n**Ways to earn:**\n• 50 points per rental\n• 100 points for 5-star reviews\n• 200 points for on-time returns\n• 500 points welcome bonus for new users\n• Bonus points during cultural holidays\n\n**How to use them:**\n• Redeem for rental discounts\n• Trade with other users\n• Convert to other tokens\n\nYour StylePoints are truly yours - stored on blockchain!",
            followUp: ["How do I redeem StylePoints?", "How does blockchain work?", "What's the welcome bonus?"]
        },
        "how do payments work": {
            answer: "We use cutting-edge blockchain technology for global payments! 💳\n\n**Payment Methods:**\n• **XRPL Tokens**: Fast, low-fee payments using USDToken\n• **Traditional**: Credit/debit cards for those new to crypto\n• **StylePoints**: Use your earned rewards for discounts\n\n**Why XRPL?**\n• Minimal transaction fees (fractions of a cent)\n• Global reach - pay from anywhere in the world\n• Instant settlement and confirmation\n• Automatic refunds for delivery issues\n\n**Security:**\n• All transactions are blockchain-verified\n• Automatic smart contract execution\n• Real-time delivery and payment tracking\n\nNo need for expensive international transfer fees!",
            followUp: ["How do I connect my wallet?", "What if I don't have crypto?", "Is it secure?"]
        },
        "what about sustainability": {
            answer: "Sustainability is at the heart of everything we do! ♻️\n\n**Environmental Impact:**\n• Sharing reduces fashion waste by 70%\n• Each rental prevents ~15kg of CO₂ emissions\n• Professional cleaning extends garment lifespan\n• Digital tracking reduces overproduction\n\n**Cultural Preservation:**\n• Support authentic artisans and traditional makers\n• Preserve cultural knowledge and techniques\n• Make cultural fashion accessible without appropriation\n• Educational content about each garment's significance\n\n**Blockchain Transparency:**\n• Complete supply chain visibility\n• Verify ethical sourcing and fair wages\n• Track environmental certifications\n• Immutable sustainability records\n\nEvery rental helps build a more sustainable and culturally respectful fashion future! 🌍",
            followUp: ["How much CO₂ do I save?", "How do you verify authenticity?", "What cultures do you work with?"]
        },
        "how do i connect my wallet": {
            answer: "Connecting your Web3 wallet unlocks the full CultureWear experience! 🔗\n\n**Supported Wallets:**\n• **Xumm**: Best for XRPL payments and transactions\n• **MetaMask**: Popular wallet for Flare network and StylePoints\n• **Ledger**: Hardware wallet for maximum security\n\n**Connection Steps:**\n1. Click 'Connect Wallet' in your profile\n2. Select your preferred wallet\n3. Approve the connection in your wallet app\n4. Sign a verification message\n5. You're connected! 🎉\n\n**Benefits:**\n• Earn and manage StylePoints (FAssets)\n• Make global payments with minimal fees\n• Access NFT garment histories\n• Participate in exclusive blockchain features\n\n**New to Web3?** No problem! You can start with email signup and add a wallet anytime.",
            followUp: ["Which wallet should I choose?", "Is it safe?", "What if I'm new to crypto?"]
        },
        "what cultural attire do you have": {
            answer: "We celebrate cultures from around the world! 🌍\n\n**Asian Cultures:**\n• Japanese Kimonos, Yukata, and formal wear\n• Indian Sarees, Lehengas, and Sherwanis\n• Chinese Qipao and traditional dresses\n• Korean Hanbok for special occasions\n\n**European Traditions:**\n• German Dirndls and Lederhosen\n• Scottish Kilts and Highland dress\n• Eastern European folk costumes\n• Nordic traditional wear\n\n**African Heritage:**\n• West African Kente and Dashiki\n• East African traditional robes\n• Moroccan Caftans and Takchita\n• Ethiopian cultural dress\n\n**Latin American:**\n• Mexican Huipil and formal wear\n• Andean traditional clothing\n• Caribbean ceremonial dress\n\nEach piece comes with cultural context and proper wearing guidelines. We work directly with cultural communities to ensure authenticity and respectful representation! 🤝",
            followUp: ["How do you ensure authenticity?", "Can I request specific items?", "Do you have sizing guides?"]
        },
        "default": {
            answer: "I'm here to help with questions about CultureWear! 🤖\n\nI can assist you with:\n• How our rental system works\n• StylePoints and rewards\n• Payments and blockchain features\n• Sustainability and cultural impact\n• Wallet connections and Web3 features\n• Our cultural attire collection\n\nTry asking about any of these topics, or choose from the quick questions!",
            followUp: ["How does renting work?", "What are StylePoints?", "What cultural attire do you have?"]
        }
    },

    // State
    isOpen: false,
    isTyping: false,
    messageHistory: [],

    // Initialize the chatbot
    init() {
        this.createChatWidget();
        this.bindEvents();
    },

    // Create the chat widget HTML
    createChatWidget() {
        const chatHTML = `
            <!-- Floating Chat Button -->
            <div id="chat-float-btn" class="chat-float-btn">
                <span>💬</span>
                <div class="chat-tooltip">Need help? Ask me anything!</div>
            </div>

            <!-- Chat Modal -->
            <div id="chat-modal" class="chat-modal">
                <div class="chat-modal-content">
                    <div class="chat-header">
                        <h3>🤖 CultureWear Assistant</h3>
                        <p>I'm here to help with your questions!</p>
                        <button id="chat-close-btn" class="chat-close-btn">&times;</button>
                    </div>

                    <div class="chat-messages" id="chat-messages">
                        <div class="welcome-message" id="welcome-message">
                            <h4 style="margin-bottom: 1rem; color: #2c3e50;">How can I help you today?</h4>
                            <div class="quick-questions">
                                <div class="quick-question" onclick="ChatbotWidget.askQuestion('How does renting work?')">
                                    <div class="quick-question-icon">👗</div>
                                    <div class="quick-question-text">How does renting work?</div>
                                </div>
                                <div class="quick-question" onclick="ChatbotWidget.askQuestion('What are StylePoints?')">
                                    <div class="quick-question-icon">💎</div>
                                    <div class="quick-question-text">What are StylePoints?</div>
                                </div>
                                <div class="quick-question" onclick="ChatbotWidget.askQuestion('How do payments work?')">
                                    <div class="quick-question-icon">💳</div>
                                    <div class="quick-question-text">How do payments work?</div>
                                </div>
                                <div class="quick-question" onclick="ChatbotWidget.askQuestion('What about sustainability?')">
                                    <div class="quick-question-icon">♻️</div>
                                    <div class="quick-question-text">What about sustainability?</div>
                                </div>
                                <div class="quick-question" onclick="ChatbotWidget.askQuestion('How do I connect my wallet?')">
                                    <div class="quick-question-icon">🔗</div>
                                    <div class="quick-question-text">How do I connect my wallet?</div>
                                </div>
                                <div class="quick-question" onclick="ChatbotWidget.askQuestion('What cultural attire do you have?')">
                                    <div class="quick-question-icon">🌍</div>
                                    <div class="quick-question-text">What cultural attire do you have?</div>
                                </div>
                            </div>
                        </div>

                        <div class="typing-indicator" id="typing-indicator">
                            <div class="message-avatar bot-avatar">🤖</div>
                            <div>
                                <div class="typing-dots">
                                    <div class="typing-dot"></div>
                                    <div class="typing-dot"></div>
                                    <div class="typing-dot"></div>
                                </div>
                                <div style="font-size: 0.8rem; margin-top: 0.25rem;">Assistant is typing...</div>
                            </div>
                        </div>
                    </div>

                    <div class="chat-input-container">
                        <div class="chat-input-wrapper">
                            <textarea 
                                class="chat-input" 
                                id="chat-input" 
                                placeholder="Ask me anything about CultureWear..."
                                rows="1"
                            ></textarea>
                            <button class="send-btn" id="send-btn">
                                ➤
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add CSS
        const chatCSS = `
            <style>
                /* Floating Chat Button */
                .chat-float-btn {
                    position: fixed;
                    bottom: 30px;
                    right: 30px;
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 1.5rem;
                    cursor: pointer;
                    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
                    transition: all 0.3s ease;
                    z-index: 1000;
                    animation: chatPulse 2s infinite;
                }

                .chat-float-btn:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
                    animation: none;
                }

                .chat-tooltip {
                    position: absolute;
                    right: 70px;
                    top: 50%;
                    transform: translateY(-50%);
                    background: #333;
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 10px;
                    font-size: 0.9rem;
                    white-space: nowrap;
                    opacity: 0;
                    pointer-events: none;
                    transition: opacity 0.3s ease;
                }

                .chat-tooltip::after {
                    content: '';
                    position: absolute;
                    left: 100%;
                    top: 50%;
                    transform: translateY(-50%);
                    border: 6px solid transparent;
                    border-left-color: #333;
                }

                .chat-float-btn:hover .chat-tooltip {
                    opacity: 1;
                }

                @keyframes chatPulse {
                    0% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
                    50% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.7); }
                    100% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
                }

                /* Chat Modal */
                .chat-modal {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 2000;
                }

                .chat-modal-content {
                    position: absolute;
                    bottom: 100px;
                    right: 30px;
                    width: 400px;
                    height: 600px;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    animation: chatSlideUp 0.3s ease-out;
                }

                @keyframes chatSlideUp {
                    from {
                        opacity: 0;
                        transform: translateY(50px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                .chat-header {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    padding: 1.5rem;
                    position: relative;
                }

                .chat-header h3 {
                    margin: 0 0 0.25rem 0;
                    font-size: 1.3rem;
                }

                .chat-header p {
                    margin: 0;
                    opacity: 0.9;
                    font-size: 0.9rem;
                }

                .chat-close-btn {
                    position: absolute;
                    top: 1rem;
                    right: 1rem;
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    font-size: 1.5rem;
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.3s ease;
                }

                .chat-close-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }

                .chat-messages {
                    flex: 1;
                    padding: 1.5rem;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }

                .message {
                    display: flex;
                    gap: 0.75rem;
                    max-width: 85%;
                }

                .message.user {
                    align-self: flex-end;
                    flex-direction: row-reverse;
                }

                .message-avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    flex-shrink: 0;
                    font-size: 0.9rem;
                }

                .bot-avatar {
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                }

                .user-avatar {
                    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                    color: white;
                }

                .message-content {
                    background: #f8f9fa;
                    padding: 0.75rem 1rem;
                    border-radius: 15px;
                    border-bottom-left-radius: 4px;
                    font-size: 0.9rem;
                    line-height: 1.4;
                }

                .message.user .message-content {
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    border-bottom-left-radius: 15px;
                    border-bottom-right-radius: 4px;
                }

                .message-time {
                    font-size: 0.7rem;
                    opacity: 0.6;
                    margin-top: 0.25rem;
                }

                .quick-questions {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 0.75rem;
                }

                .quick-question {
                    background: rgba(102, 126, 234, 0.1);
                    border: 1px solid rgba(102, 126, 234, 0.2);
                    padding: 0.75rem;
                    border-radius: 10px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-align: center;
                }

                .quick-question:hover {
                    background: rgba(102, 126, 234, 0.2);
                    border-color: rgba(102, 126, 234, 0.4);
                    transform: translateY(-1px);
                }

                .quick-question-icon {
                    font-size: 1.2rem;
                    margin-bottom: 0.25rem;
                }

                .quick-question-text {
                    font-weight: 500;
                    color: #2c3e50;
                    font-size: 0.8rem;
                    line-height: 1.2;
                }

                .typing-indicator {
                    display: none;
                    align-items: center;
                    gap: 0.5rem;
                    font-style: italic;
                    opacity: 0.7;
                }

                .typing-dots {
                    display: flex;
                    gap: 0.25rem;
                }

                .typing-dot {
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                    background: #667eea;
                    animation: typingBounce 1.4s ease-in-out infinite;
                }

                .typing-dot:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .typing-dot:nth-child(3) {
                    animation-delay: 0.4s;
                }

                @keyframes typingBounce {
                    0%, 60%, 100% { transform: translateY(0); }
                    30% { transform: translateY(-8px); }
                }

                .chat-input-container {
                    padding: 1rem 1.5rem;
                    border-top: 1px solid #e9ecef;
                    background: white;
                }

                .chat-input-wrapper {
                    display: flex;
                    gap: 0.75rem;
                    align-items: flex-end;
                }

                .chat-input {
                    flex: 1;
                    padding: 0.75rem 1rem;
                    border: 2px solid #e9ecef;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    resize: none;
                    max-height: 80px;
                    min-height: 40px;
                    outline: none;
                    transition: border-color 0.3s ease;
                    font-family: inherit;
                }

                .chat-input:focus {
                    border-color: #667eea;
                }

                .send-btn {
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1rem;
                    transition: transform 0.3s ease;
                }

                .send-btn:hover {
                    transform: scale(1.1);
                }

                .send-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none;
                }

                .welcome-message.hidden {
                    display: none;
                }

                /* Mobile Responsive */
                @media (max-width: 768px) {
                    .chat-modal-content {
                        bottom: 20px;
                        right: 20px;
                        left: 20px;
                        width: auto;
                        height: 70vh;
                    }
                    
                    .chat-float-btn {
                        width: 50px;
                        height: 50px;
                        bottom: 20px;
                        right: 20px;
                    }
                    
                    .quick-questions {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        `;

        // Add CSS to head
        document.head.insertAdjacentHTML('beforeend', chatCSS);
        
        // Add HTML to body
        document.body.insertAdjacentHTML('beforeend', chatHTML);
    },

    // Bind events
    bindEvents() {
        const floatBtn = document.getElementById('chat-float-btn');
        const modal = document.getElementById('chat-modal');
        const closeBtn = document.getElementById('chat-close-btn');
        const sendBtn = document.getElementById('send-btn');
        const chatInput = document.getElementById('chat-input');

        floatBtn.addEventListener('click', () => this.openChat());
        closeBtn.addEventListener('click', () => this.closeChat());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeChat();
        });
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 80) + 'px';
            sendBtn.disabled = !chatInput.value.trim();
        });
    },

    // Open chat
    openChat() {
        const modal = document.getElementById('chat-modal');
        modal.style.display = 'block';
        this.isOpen = true;
        
        // Focus input
        setTimeout(() => {
            document.getElementById('chat-input').focus();
        }, 300);
    },

    // Close chat
    closeChat() {
        const modal = document.getElementById('chat-modal');
        modal.style.display = 'none';
        this.isOpen = false;
    },

    // Helper functions
    getCurrentTime() {
        return new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    },

    addMessage(content, isUser = false, showFollowUp = true) {
        const messagesContainer = document.getElementById('chat-messages');
        const welcomeMessage = document.getElementById('welcome-message');
        
        if (!welcomeMessage.classList.contains('hidden')) {
            welcomeMessage.classList.add('hidden');
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const formattedContent = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = `
            <div class="message-avatar ${isUser ? 'user-avatar' : 'bot-avatar'}">
                ${isUser ? 'U' : '🤖'}
            </div>
            <div class="message-content">
                <div>${formattedContent}</div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        
        if (!isUser && showFollowUp) {
            const question = content.toLowerCase();
            const faqKey = this.findBestMatch(question);
            const followUpQuestions = this.faqData[faqKey]?.followUp;
            
            if (followUpQuestions && followUpQuestions.length > 0) {
                setTimeout(() => {
                    const followUpDiv = document.createElement('div');
                    followUpDiv.className = 'message bot';
                    followUpDiv.innerHTML = `
                        <div class="message-avatar bot-avatar">🤖</div>
                        <div class="message-content">
                            <div><strong>You might also want to ask:</strong></div>
                            <div style="margin-top: 0.5rem;">
                                ${followUpQuestions.map(q => 
                                    `<div style="background: rgba(102, 126, 234, 0.1); padding: 0.4rem 0.6rem; margin: 0.2rem 0; border-radius: 8px; cursor: pointer; font-size: 0.8rem;" onclick="ChatbotWidget.askQuestion('${q}')">${q}</div>`
                                ).join('')}
                            </div>
                            <div class="message-time">${this.getCurrentTime()}</div>
                        </div>
                    `;
                    messagesContainer.appendChild(followUpDiv);
                    this.scrollToBottom();
                }, 500);
            }
        }
        
        this.scrollToBottom();
    },

    showTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.style.display = 'flex';
        this.isTyping = true;
        this.scrollToBottom();
    },

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.style.display = 'none';
        this.isTyping = false;
    },

    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    },

    findBestMatch(question) {
        const normalizedQuestion = question.toLowerCase().trim();
        
        for (let key in this.faqData) {
            if (key !== 'default') {
                const keywords = key.split(' ');
                const matches = keywords.filter(keyword => 
                    normalizedQuestion.includes(keyword)
                );
                
                if (matches.length >= Math.ceil(keywords.length * 0.6)) {
                    return key;
                }
            }
        }
        
        // Partial matching
        if (normalizedQuestion.includes('rent') || normalizedQuestion.includes('how') || normalizedQuestion.includes('work')) {
            return 'how does renting work';
        }
        if (normalizedQuestion.includes('points') || normalizedQuestion.includes('rewards') || normalizedQuestion.includes('style')) {
            return 'what are stylepoints';
        }
        if (normalizedQuestion.includes('pay') || normalizedQuestion.includes('payment') || normalizedQuestion.includes('money') || normalizedQuestion.includes('cost')) {
            return 'how do payments work';
        }
        if (normalizedQuestion.includes('sustain') || normalizedQuestion.includes('environment') || normalizedQuestion.includes('eco') || normalizedQuestion.includes('green')) {
            return 'what about sustainability';
        }
        if (normalizedQuestion.includes('wallet') || normalizedQuestion.includes('connect') || normalizedQuestion.includes('blockchain') || normalizedQuestion.includes('crypto')) {
            return 'how do i connect my wallet';
        }
        if (normalizedQuestion.includes('clothes') || normalizedQuestion.includes('attire') || normalizedQuestion.includes('culture') || normalizedQuestion.includes('collection')) {
            return 'what cultural attire do you have';
        }
        
        return 'default';
    },

    getBotResponse(question) {
        const faqKey = this.findBestMatch(question);
        return this.faqData[faqKey].answer;
    },

    askQuestion(question) {
        if (this.isTyping) return;
        
        this.addMessage(question, true);
        this.messageHistory.push({ type: 'user', content: question, time: this.getCurrentTime() });
        
        this.showTypingIndicator();
        
        setTimeout(() => {
            this.hideTypingIndicator();
            
            const response = this.getBotResponse(question);
            this.addMessage(response, false);
            this.messageHistory.push({ type: 'bot', content: response, time: this.getCurrentTime() });
        }, 1000 + Math.random() * 1000);
    },

    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message && !this.isTyping) {
            this.askQuestion(message);
            input.value = '';
            input.style.height = 'auto';
            document.getElementById('send-btn').disabled = true;
        }
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ChatbotWidget.init());
} else {
    ChatbotWidget.init();
}