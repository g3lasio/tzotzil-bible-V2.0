// nevin.js - Sistema de chat teológico con estilo Transformers
class NevinChat {
    constructor() {
        this.state = {
            currentEmotion: "neutral",
            chatHistory: [],
            userContext: {},
            isProcessing: false,
            userId: document.querySelector('meta[name="user-id"]')?.content || null,
            transformationActive: false
        };

        // Inicializar cuando el DOM esté listo
        document.addEventListener("DOMContentLoaded", () => this.init());
    }

    init() {
        this.setupEventListeners();
        this.showWelcomeMessage();
        this.displayRandomSuggestions();
        this.initTransformationEffects();
    }

    initTransformationEffects() {
        const chatContainer = document.getElementById("chat-container");
        if (chatContainer) {
            chatContainer.classList.add("transform-effect");
            this.addTransformObserver();
        }
    }

    addTransformObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) {
                            node.classList.add("transform-effect");
                        }
                    });
                }
            });
        });

        const config = { childList: true, subtree: true };
        observer.observe(document.getElementById("chat-container"), config);
    }

    setupEventListeners() {
        const userInput = document.getElementById("user-input");
        const sendButton = document.getElementById("send-button");

        if (userInput) {
            userInput.addEventListener("keypress", (e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (sendButton) {
            sendButton.addEventListener("click", () => this.sendMessage());
        }

        // Otros botones
        document.getElementById("new-chat-button")?.addEventListener("click", () => this.startNewChat());
        document.getElementById("home-button")?.addEventListener("click", () => this.goHome());
        document.getElementById("chat-history-icon")?.addEventListener("click", () => this.showChatHistory());
    }

    async showWelcomeMessage() {
        const username = localStorage.getItem("username");
        let welcomeText = "";

        if (username && username !== "null") {
            const hour = new Date().getHours();
            let timeGreeting = hour < 12 ? "buenos días" : hour < 18 ? "buenas tardes" : "buenas noches";
            welcomeText = `¡${timeGreeting}, ${username}! Me alegra verte de nuevo. ¿En qué puedo ayudarte hoy?`;
        } else {
            welcomeText = `Hola, soy Nevin, tu asistente bíblico personal. Para brindarte una experiencia más personalizada, ¿podrías decirme tu nombre?`;
        }

        await this.showTransformationMessage(welcomeText);

        if (!username || username === "null") {
            this.showNameInput();
        }
    }

    showNameInput() {
        const chatHistory = document.getElementById("chat-history");
        if (!chatHistory) return;

        const inputContainer = document.createElement("div");
        inputContainer.classList.add("name-input-container", "transform-effect");

        const nameInput = document.createElement("input");
        nameInput.type = "text";
        nameInput.placeholder = "Escribe tu nombre aquí...";
        nameInput.classList.add("name-input");

        const submitButton = document.createElement("button");
        submitButton.textContent = "Continuar";
        submitButton.classList.add("name-submit", "transform-button");

        const handleNameSubmit = async () => {
            const name = nameInput.value.trim();
            if (name) {
                localStorage.setItem("username", name);
                inputContainer.remove();
                await this.showTransformationMessage(
                    `¡Gracias, ${name}! Es un placer conocerte. Estoy aquí para ayudarte a explorar y comprender mejor las verdades bíblicas. ¿Qué te gustaría aprender hoy?`
                );
                this.displayRandomSuggestions();
            }
        };

        submitButton.onclick = handleNameSubmit;
        nameInput.onkeypress = (e) => {
            if (e.key === "Enter") handleNameSubmit();
        };

        inputContainer.appendChild(nameInput);
        inputContainer.appendChild(submitButton);
        chatHistory.appendChild(inputContainer);

        inputContainer.scrollIntoView({ behavior: "smooth" });
    }

    formatReferences(text) {
        if (!text) return '';

        try {
            let formattedText = text;

            // Referencias bíblicas (entre __)
            formattedText = formattedText.replace(/__([^_]+?)__\s*-\s*([^_]+?)(?=\s*(?:__|$|\*|\())/g, (match, reference, content) => {
                console.log('Referencia bíblica:', { reference, content });
                return `<div class="verse-box" onclick="window.handleVerseClick('${reference.trim()}')">
                    <div class="verse-content">${content.trim()}</div>
                    <div class="verse-reference">${reference.trim()}</div>
                </div>`;
            });

            // Referencias de EGW (entre *)
            formattedText = formattedText.replace(/\*([^*]+?)\*\s*-\s*([^*]+?)(?=\s*(?:\*|$|__|$|\())/g, (match, source, content) => {
                console.log('Referencia EGW:', { source, content });
                return `<div class="egw-box">
                    <div class="egw-content">${content.trim()}</div>
                    <div class="egw-reference">${source.trim()}</div>
                </div>`;
            });

            // Referencias teológicas (entre paréntesis)
            formattedText = formattedText.replace(/\(([^)]+?)\)\s*-\s*([^)]+?)(?=\s*(?:\(|$|__|$|\*))/g, (match, source, content) => {
                console.log('Referencia teológica:', { source, content });
                return `<div class="theological-ref">
                    <strong>${source.trim()}</strong>
                    <div class="theological-content">${content.trim()}</div>
                </div>`;
            });

            // Mantener saltos de línea
            formattedText = formattedText.replace(/\n/g, '<br>');

            console.log('Texto formateado:', formattedText);
            return formattedText;

        } catch (error) {
            console.error('Error formateando referencias:', error);
            return text;
        }
    }

    async showTransformationMessage(text, isUser = false) {
        const chatHistory = document.getElementById("chat-history");
        if (!chatHistory) return;

        // Ocultar sugerencias cuando comienza la interacción
        if (!isUser) {
            const suggestionsContainer = document.getElementById("suggestions-container");
            if (suggestionsContainer) {
                suggestionsContainer.style.display = "none";
            }
        }

        const container = document.createElement("div");
        container.classList.add("transform-effect");

        if (isUser) {
            container.classList.add("user-message");
            container.textContent = text;
            chatHistory.appendChild(container);
            container.scrollIntoView({ behavior: "smooth" });
        } else {
            container.classList.add("nevin-response-container");

            const icon = document.createElement("img");
            icon.src = "/static/images/nevin-icon.svg";
            icon.alt = "Icono de Nevin";
            icon.classList.add("nevin-icon-response");
            container.appendChild(icon);

            const messageElement = document.createElement("div");
            messageElement.classList.add("nevin-message");
            container.appendChild(messageElement);
            chatHistory.appendChild(container);

            // Efecto de escritura progresiva
            const formattedText = this.formatReferences(text);
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = formattedText;
            const textContent = tempDiv.textContent;

            let buffer = '';
            const words = textContent.split(' ');
            let lastScroll = chatHistory.scrollTop;
            let userScrolled = false;

            // Detectar si el usuario hace scroll
            const scrollHandler = () => {
                if (chatHistory.scrollTop !== lastScroll) {
                    userScrolled = true;
                }
            };

            chatHistory.addEventListener('scroll', scrollHandler, { passive: true });

            const writeSpeed = 30;
            for (const word of words) {
                buffer += word + ' ';
                await new Promise(resolve => setTimeout(resolve, writeSpeed));
                const partialFormatted = this.formatReferences(buffer);
                messageElement.innerHTML = partialFormatted;

                if (!userScrolled) {
                    const isNearBottom = chatHistory.scrollHeight - chatHistory.scrollTop - chatHistory.clientHeight < 100;
                    if (isNearBottom) {
                        container.scrollIntoView({ block: "end", behavior: "smooth" });
                    }
                }
                lastScroll = chatHistory.scrollTop;
            }

            // Limpiar el event listener
            chatHistory.removeEventListener('scroll', scrollHandler);

            // Asegurar que el formato final sea correcto
            messageElement.innerHTML = formattedText;
        }
    }

    displayRandomSuggestions() {
        const suggestions = [
            "¿Qué dice la Biblia sobre la salvación?",
            "¿Cómo puedo fortalecer mi fe?",
            "¿Qué enseña la Biblia sobre el sábado?",
            "¿Qué dice Elena G. White sobre la oración?",
            "¿Cómo puedo entender mejor la profecía bíblica?"
        ];

        const container = document.getElementById("suggestions-container");
        if (!container) return;

        container.innerHTML = "";
        container.style.display = "flex";

        suggestions
            .sort(() => Math.random() - 0.5)
            .slice(0, 3)
            .forEach(suggestion => {
                const button = document.createElement("button");
                button.classList.add("suggestion-button", "transform-button");
                button.textContent = suggestion;
                button.onclick = () => this.handleSuggestionClick(suggestion);
                container.appendChild(button);
            });
    }

    handleSuggestionClick(suggestion) {
        const inputField = document.getElementById("user-input");
        if (inputField) {
            inputField.value = suggestion;
            this.sendMessage();
        }
    }

    async sendMessage() {
        const inputField = document.getElementById("user-input");
        const sendButton = document.getElementById("send-button");
        const message = inputField?.value.trim();
        const chatHistory = document.getElementById("chat-history");

        if (!message || this.state.isProcessing) {
            console.log("Mensaje vacío o el sistema está ocupado.");
            return;
        }

        if (!chatHistory) {
            console.error("Elemento chat-history no encontrado");
            return;
        }

        try {
            this.state.isProcessing = true;
            inputField.disabled = true;
            if (sendButton) sendButton.disabled = true;

            // Mostrar mensaje del usuario
            await this.showTransformationMessage(message, true);
            inputField.value = "";

            // Mostrar indicador de "pensando"
            const thinkingContainer = document.createElement("div");
            thinkingContainer.classList.add("nevin-thinking");
            thinkingContainer.innerHTML = `
                <div class="nevin-response-container">
                    <img src="/static/images/nevin-icon.svg" alt="Icono de Nevin" class="nevin-icon-response">
                    <div class="thinking-indicator">
                        <span class="thinking-text">Pensando</span>
                        <span class="dot">.</span>
                        <span class="dot">.</span>
                        <span class="dot">.</span>
                    </div>
                </div>
            `;
            document.getElementById("chat-history").appendChild(thinkingContainer);
            thinkingContainer.scrollIntoView({ behavior: "smooth" });

            console.log("Enviando datos al backend:");
            console.log({
                question: message,
                user_id: this.state.userId
            });

            // Llamada al backend
            const response = await fetch("/nevin/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: message,
                    user_id: window.userId || this.state.userId
                })
            });

            console.log("Respuesta del servidor:", response);

            // Remover indicador de "pensando"
            thinkingContainer.remove();

            if (!response.ok) {
                throw new Error("Error en la respuesta del servidor");
            }

            const data = await response.json();
            console.log("Datos recibidos del servidor:", data);
            await this.showTransformationMessage(data.response);

        } catch (error) {
            console.error("Error enviando mensaje:", error);
            await this.showTransformationMessage(
                "Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo."
            );
        } finally {
            this.state.isProcessing = false;
            if (inputField) {
                inputField.disabled = false;
                inputField.focus();
            }
            if (sendButton) sendButton.disabled = false;
        }
    }

    startNewChat() {
        const chatHistory = document.getElementById("chat-history");
        if (chatHistory) {
            chatHistory.innerHTML = "";
            this.showWelcomeMessage();
            this.displayRandomSuggestions();
        }
    }

    goHome() {
        window.location.href = '/home';
    }

    showChatHistory() {
        console.log("Mostrar historial de chat");
    }
}

// Inicializar Nevin y exportar funciones globales
const nevinChat = new NevinChat();

// Exponer funciones globalmente
window.sendMessage = () => nevinChat.sendMessage();
window.startNewChat = () => nevinChat.startNewChat();
window.goHome = () => nevinChat.goHome();
window.showChatHistory = () => nevinChat.showChatHistory();

window.handleVerseClick = (reference) => {
    // Extrae el libro y versículo
    const parts = reference.split(' ');
    const chapter = parts[parts.length - 1].split(':')[0];
    const verse = parts[parts.length - 1].split(':')[1];
    let book = parts.slice(0, -1).join(' ');
    
    // Construye la URL
    const url = `/chapter/${encodeURIComponent(book)}/${chapter}#verse-${verse}`;
    
    // Abre en una nueva pestaña
    window.open(url, '_blank');
};