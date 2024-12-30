// Add sanitizeHTML function at the top
function sanitizeHTML(content) {
    if (typeof DOMPurify !== 'undefined') {
        return DOMPurify.sanitize(content, {
            ALLOWED_TAGS: ['div', 'p', 'ul', 'li', 'small', 'span'],
            ALLOWED_CLASSES: {
                'div': ['info-box', 'quote-box', 'verse-box', 'response-section', 'suggestions-box'],
                'ul': ['bullet-list'],
                'small': ['verse-ref', 'quote-ref']
            }
        });
    }
    // Fallback to basic HTML escaping if DOMPurify is not available
    return content.replace(/[&<>"']/g, function(match) {
        const escape = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return escape[match];
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const elements = {
        questionForm: document.getElementById('question-form'),
        chatContainer: document.getElementById('chat-container'),
        questionInput: document.getElementById('question-input'),
        connectionStatus: document.getElementById('connection-status'),
        typingIndicator: document.getElementById('typing-indicator'),
        errorAlert: document.getElementById('error-alert'),
        loadingOverlay: document.getElementById('loading-overlay'),
        suggestedQuestions: document.querySelectorAll('.suggested-question')
    };

    initializeEventHandlers(elements);
    initializeLanguageSwitcher();
    loadConversationHistory();
});

function appendMessage(container, content, type) {
    if (!container || !content) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    
    const sanitizedContent = sanitizeHTML(content);
    
    messageDiv.innerHTML = sanitizedContent;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

async function loadConversationHistory() {
    try {
        const response = await fetch('/api/conversation-history');
        const data = await response.json();
        
        if (data.success && data.history) {
            const chatContainer = document.getElementById('chat-container');
            const welcomeMessage = chatContainer.querySelector('.assistant-message');
            chatContainer.innerHTML = '';
            if (welcomeMessage) {
                chatContainer.appendChild(welcomeMessage);
            }
            
            data.history.reverse().forEach(conv => {
                appendMessage(chatContainer, conv.question, 'user');
                appendMessage(chatContainer, conv.response, 'assistant');
            });
        } else if (data.error) {
            console.error('Error loading history:', data.error);
        }
    } catch (error) {
        console.error('Error loading conversation history:', error);
    }
}

function initializeEventHandlers(elements) {
    if (elements.suggestedQuestions) {
        elements.suggestedQuestions.forEach(button => {
            button.addEventListener('click', () => {
                if (elements.questionInput && elements.questionForm) {
                    elements.questionInput.value = button.dataset.question || '';
                    elements.questionInput.focus();
                    
                    const suggestedQuestionsContainer = document.querySelector('.suggested-questions');
                    if (suggestedQuestionsContainer) {
                        suggestedQuestionsContainer.style.display = 'none';
                    }
                    
                    elements.questionForm.dispatchEvent(new Event('submit'));
                }
            });
        });
    }

    if (elements.questionForm) {
        elements.questionForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await handleFormSubmit(elements);
        });
    }
}

async function handleFormSubmit(elements) {
    const question = elements.questionInput.value.trim();
    if (!question) return;

    try {
        showLoadingState(elements, true);
        
        appendMessage(elements.chatContainer, question, 'user');
        elements.questionInput.value = '';

        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        let data;
        try {
            data = await response.json();
        } catch (parseError) {
            throw new Error('Error parsing server response');
        }

        showLoadingState(elements, false);

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Error processing request');
        }

        displayResponse(elements, data);

    } catch (error) {
        console.error('Error processing request:', error);
        handleError(elements, error);
    }
}

function showLoadingState(elements, show) {
    elements.typingIndicator.style.display = show ? 'flex' : 'none';
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
    elements.connectionStatus.style.display = show ? 'block' : 'none';
    elements.connectionStatus.textContent = 'Procesando tu pregunta...';
}

function displayResponse(elements, data) {
    if (!elements.chatContainer) return;

    if (data.error) {
        handleError(elements, new Error(data.error));
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message assistant-message';
    
    // Check if this is a name request
    if (data.response.includes("¿podrías decirme tu nombre?")) {
        const nameForm = document.createElement('div');
        nameForm.className = 'name-input-form mt-3';
        nameForm.innerHTML = `
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Escribe tu nombre aquí" id="name-input">
                <button class="btn btn-primary" type="button" onclick="submitName()">Enviar</button>
            </div>
        `;
        messageDiv.appendChild(nameForm);
    }
    
    const sanitizedContent = sanitizeHTML(data.response);
    messageDiv.innerHTML += sanitizedContent;
    elements.chatContainer.appendChild(messageDiv);
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function handleError(elements, error) {
    showLoadingState(elements, false);
    
    const errorMessage = error.message || 'Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta nuevamente.';
    
    appendMessage(elements.chatContainer, 
        `Error: ${errorMessage}`, 
        'assistant');
    
    if (elements.errorAlert) {
        elements.errorAlert.textContent = errorMessage;
        elements.errorAlert.style.display = 'block';
        elements.errorAlert.classList.add('error-alert');
        setTimeout(() => {
            elements.errorAlert.style.display = 'none';
            elements.errorAlert.classList.remove('error-alert');
        }, 5000);
    }
}

// Add new function to handle name submission
async function submitName() {
    const nameInput = document.getElementById('name-input');
    const name = nameInput.value.trim();
    if (!name) return;

    try {
        const response = await fetch('/api/update-name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });

        const data = await response.json();
        if (data.success) {
            location.reload();  // Reload to show personalized welcome
        } else {
            throw new Error(data.error || 'Error updating name');
        }
    } catch (error) {
        console.error('Error updating name:', error);
        handleError({ errorAlert: document.getElementById('error-alert') }, error);
    }
}

function initializeLanguageSwitcher() {
    const languageButtons = document.querySelectorAll('[data-language]');
    if (!languageButtons.length) return;

    languageButtons.forEach(button => {
        button.addEventListener('click', function() {
            const language = this.dataset.language;
            if (!language) return;
            switchLanguage(language);
        });
    });
}

function switchLanguage(language) {
    if (!language) return;

    fetch('/api/switch-language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelectorAll('[data-language]').forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.language === language) {
                    btn.classList.add('active');
                }
            });
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error switching language:', error);
        handleError(elements, new Error('Error al cambiar el idioma. Por favor, intenta nuevamente.'));
    });
}
