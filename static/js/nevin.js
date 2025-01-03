// nevin.js - Sistema de chat teológico con estilo Transformers
class NevinChat {
    constructor() {
        this.state = {
            currentEmotion: "neutral",
            chatHistory: [],
            userContext: {},
            isProcessing: false,
            userId:
                document.querySelector('meta[name="user-id"]')?.content || null,
            transformationActive: false,
        };

        // Inicializar cuando el DOM esté listo
        document.addEventListener("DOMContentLoaded", () => this.init());
    }

    init() {
        this.setupEventListeners();
        // Only show welcome message if chat history is empty
        if (!document.querySelector(".nevin-message")) {
            this.showWelcomeMessage();
        }
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
        document
            .getElementById("new-chat-button")
            ?.addEventListener("click", () => this.startNewChat());
        document
            .getElementById("home-button")
            ?.addEventListener("click", () => this.goHome());
        document
            .getElementById("chat-history-icon")
            ?.addEventListener("click", () => this.showChatHistory());
    }

    async showWelcomeMessage() {
        const username = localStorage.getItem("username");
        const hour = new Date().getHours();
        let welcomeText = "";

        if (username && username !== "null") {
            const greetings = [
                "¡Me alegra verte de nuevo",
                "¡Qué gusto tenerte de vuelta",
                "¡Bienvenido nuevamente",
                "¡Es un placer verte otra vez",
            ];
            const randomGreeting =
                greetings[Math.floor(Math.random() * greetings.length)];
            welcomeText = `${randomGreeting}, ${username}! ¿En qué puedo ayudarte hoy?`;
        } else {
            welcomeText = `¡Hola! Soy Nevin, tu asistente bíblico personal. Para brindarte una experiencia más personalizada, ¿podrías decirme tu nombre?`;
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
        inputContainer.classList.add(
            "name-input-container",
            "transform-effect",
        );

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
                    `¡Gracias, ${name}! Es un placer conocerte. Estoy aquí para ayudarte a explorar y comprender mejor las verdades bíblicas. ¿Qué te gustaría aprender hoy?`,
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
        // El texto ya viene formateado desde el backend
        return text || "";
    }

    async showTransformationMessage(text, isUser = false) {
        const chatHistory = document.getElementById("chat-history");
        if (!chatHistory) return;

        // Ocultar sugerencias cuando comienza la interacción
        if (!isUser) {
            const suggestionsContainer = document.getElementById(
                "suggestions-container",
            );
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
            const tempDiv = document.createElement("div");
            tempDiv.innerHTML = formattedText;
            const textContent = tempDiv.textContent;

            let buffer = "";
            const words = textContent.split(" ");
            let lastScroll = chatHistory.scrollTop;
            let userScrolled = false;

            // Detectar si el usuario hace scroll
            const scrollHandler = () => {
                if (chatHistory.scrollTop !== lastScroll) {
                    userScrolled = true;
                }
            };

            chatHistory.addEventListener("scroll", scrollHandler, {
                passive: true,
            });

            const writeSpeed = Math.max(10, Math.min(30, 30 - Math.floor(textContent.length / 100)));
            for (const word of words) {
                buffer += word + " ";
                await new Promise((resolve) => setTimeout(resolve, writeSpeed));
                const partialFormatted = this.formatReferences(buffer);
                messageElement.innerHTML = partialFormatted;

                if (!userScrolled) {
                    const isNearBottom =
                        chatHistory.scrollHeight -
                            chatHistory.scrollTop -
                            chatHistory.clientHeight <
                        100;
                    if (isNearBottom) {
                        container.scrollIntoView({
                            block: "end",
                            behavior: "smooth",
                        });
                    }
                }
                lastScroll = chatHistory.scrollTop;
            }

            // Limpiar el event listener
            chatHistory.removeEventListener("scroll", scrollHandler);

            // Asegurar que el formato final sea correcto
            messageElement.innerHTML = formattedText;
            
            try {
                // Agregar enlace de descarga si el mensaje contiene un pdf_url
                if (!isUser && this.currentResponse?.pdf_url && formattedText.includes('[PDF_LINK]')) {
                    formattedText = formattedText.replace('[PDF_LINK]', '');
                    const downloadLink = document.createElement('a');
                    downloadLink.href = this.currentResponse.pdf_url;
                    downloadLink.className = 'seminar-download-link';
                    downloadLink.innerHTML = '📄 Descargar Seminario PDF';
                    downloadLink.target = '_blank';
                    
                    // Asegurar que el enlace sea visible y tenga estilo
                    downloadLink.style.display = 'block';
                    downloadLink.style.marginTop = '15px';
                    messageElement.appendChild(document.createElement('br'));
                    messageElement.appendChild(document.createElement('br'));
                    messageElement.appendChild(downloadLink);
                }
            } catch (error) {
                console.error('Error al procesar PDF:', error);
            }
        }
    }

    displayRandomSuggestions(clearPrevious = false) {
        if (clearPrevious) {
            const chatHistory = document.getElementById("chat-history");
            if (chatHistory) {
                chatHistory.innerHTML = "";
            }
        }
        const suggestions = [
            "¿Qué relación tiene el Arca de Noé con el santuario celestial?",
            "¿Por qué el número siete tiene tanta relevancia en la Biblia?",
            "¿Cómo se explica la Trinidad a través del bautismo de Jesús?",
            "¿Por qué se considera el sábado como el sello de Dios en el tiempo del fin?",
            '¿Qué significa realmente "el juicio investigador" en el contexto celestial?',
            "¿Cómo conecta el libro de Daniel con las profecías del Apocalipsis?",
            '¿Por qué los ángeles son descritos como "seres ministradores" en Hebreos?',
            "¿Qué simboliza el candelabro de siete brazos en el santuario del Antiguo Testamento?",
            "¿Cómo los escritos de Elena G. de White complementan las doctrinas adventistas?",
            '¿Cuál es el significado del "libro de la vida" mencionado en Apocalipsis?',
            "¿Qué conexión existe entre el maná en el desierto y la Santa Cena?",
            '¿Por qué el sacrificio de Cristo es llamado "una ofrenda perfecta"?',
            "¿Qué profecías se cumplieron con exactitud en la caída de Jerusalén?",
            "¿Cómo influyen las tres etapas del juicio celestial en la salvación?",
            "¿Qué rol juega Babilonia simbólica en el tiempo del fin?",
            "¿Qué relación existe entre el diluvio universal y el bautismo cristiano?",
            '¿Cómo se define la "luz menor" y la "luz mayor" según Elena G. de White?',
            "¿Qué implicaciones tiene la ley dominical para los creyentes?",
            "¿Por qué el día de la expiación es tan significativo en las Escrituras?",
            "¿Cómo describe la Biblia la condición de los muertos antes de la resurrección?",
            "¿Qué nos enseña el tabernáculo terrenal sobre la obra de Cristo en el cielo?",
            '¿Por qué Jesús es llamado "el Cordero de Dios que quita el pecado del mundo"?',
            "¿Qué representa el cuarto mandamiento en el contexto de los últimos días?",
            "¿Cómo se explica el misterio de la iniquidad según Pablo?",
            "¿Qué relación tiene la visión de Ezequiel sobre los huesos secos con la resurrección?",
            "¿Cómo encaja la purificación del santuario con la profecía de las 2300 tardes y mañanas?",
            '¿Qué significa que Jesús sea nuestro "sumo sacerdote" según Hebreos?',
            "¿Por qué la fe y las obras no pueden separarse en la vida cristiana?",
            "¿Qué simboliza el río de agua de vida en Apocalipsis?",
            "¿Cómo se manifiesta la justicia de Cristo en la vida de los creyentes?",
            "¿Qué eventos marcarán la segunda venida de Jesús según Mateo 24?",
            "¿Qué lecciones espirituales nos enseña el éxodo de Israel de Egipto?",
            '¿Por qué se llama a Satanás "el acusador de los hermanos"?',
            '¿Qué significa la expresión "temed a Dios y dadle gloria" del mensaje de los tres ángeles?',
            "¿Cómo el santuario celestial aclara la obra mediadora de Cristo?",
            "¿Qué rol tienen los 144,000 en el tiempo del fin?",
            "¿Por qué es importante el don de profecía en la iglesia remanente?",
            "¿Qué simboliza el sello de Dios y la marca de la bestia?",
            "¿Qué conexión existe entre las plagas de Egipto y las plagas finales?",
            "¿Cómo armonizan la justicia y la misericordia de Dios en el juicio final?",
            "¿Qué representa el árbol de la vida en Génesis y Apocalipsis?",
            '¿Por qué los diez mandamientos son llamados "eternos"?',
            "¿Qué nos enseña el sacrificio de Isaac sobre la fe y la obediencia?",
            "¿Cómo se interpreta el sueño de Nabucodonosor en Daniel 2?",
            "¿Qué papel tiene el Espíritu Santo en la experiencia del nuevo nacimiento?",
            '¿Qué significa vivir "a la luz del regreso de Cristo"?',
            "¿Cómo explica la Biblia el origen del mal?",
            "¿Qué representa la mujer vestida de sol en Apocalipsis 12?",
            "¿Cómo el santuario es una clave para entender el plan de salvación?",
            "¿Qué lección espiritual nos enseña el lavamiento de pies?",
            "¿Cómo armoniza la inmortalidad condicional con las enseñanzas bíblicas?",
            "¿Qué eventos conectan la cruz con la resurrección de Jesús?",
            "¿Cómo la parábola de las diez vírgenes aplica al tiempo del fin?",
            "¿Qué simbolizan las trompetas en Apocalipsis?",
            "¿Por qué la fe de Abraham es llamada justicia?",
            "¿Qué mensaje tiene la carta a Laodicea para los cristianos de hoy?",
            "¿Qué profecías aún faltan por cumplirse antes del regreso de Cristo?",
            '¿Cómo interpretar el "tiempo del fin" según las Escrituras?',
            "¿Qué lecciones se extraen de las pruebas de Job?",
            "¿Por qué se enfatiza tanto el sábado en los escritos adventistas?",
            "¿Qué conexión tiene el pacto eterno con la cruz de Cristo?",
            "¿Cómo la Biblia describe la nueva tierra?",
            "¿Qué relación tienen los símbolos en Daniel y Apocalipsis?",
            '¿Por qué se llama a Cristo "el segundo Adán"?',
            "¿Cómo se interpreta la parábola del trigo y la cizaña?",
            "¿Qué representa el dragón en Apocalipsis?",
            "¿Cómo el santuario celestial explica el juicio pre-advenimiento?",
            '¿Qué significa ser parte del "remanente fiel"?',
            "¿Qué enseñanzas nos deja la cena pascual sobre el sacrificio de Jesús?",
            "¿Cómo el Apocalipsis revela el carácter de Dios?",
            "¿Qué simbolizan las siete iglesias de Asia?",
            "¿Qué rol tiene la ley moral en el tiempo del fin?",
            "¿Cómo los salmos describen el carácter de Dios?",
            '¿Qué significa "justificación por la fe" según Pablo?',
            "¿Cómo las profecías mesiánicas del Antiguo Testamento se cumplieron en Jesús?",
            "¿Qué representa el altar del incienso en el santuario?",
            '¿Por qué la Biblia llama a Jesús "el Alfa y la Omega"?',
            '¿Qué significa que "los muertos en Cristo resucitarán primero"?',
            "¿Qué lecciones podemos aprender de la vida de Daniel en Babilonia?",
            '¿Por qué la iglesia es llamada "el cuerpo de Cristo"?',
            "¿Qué simbolizan las bestias en las profecías de Daniel?",
            "¿Cómo interpretar los tiempos proféticos en la Biblia?",
            "¿Qué relación tienen las siete trompetas con los eventos finales?",
            '¿Por qué Jesús dijo "Yo soy la vid verdadera"?',
            "¿Qué representa la gran ramera en Apocalipsis?",
            "¿Cómo el arca del pacto refleja el carácter de Dios?",
            "¿Qué lecciones espirituales nos deja la parábola del hijo pródigo?",
            '¿Qué significa "pecado imperdonable" según Jesús?',
            "¿Cómo explica la Biblia la naturaleza de Cristo?",
            "¿Qué simbolizan las coronas en el Apocalipsis?",
            "¿Por qué es importante el pacto de gracia en la salvación?",
            "¿Qué nos enseña la historia de Moisés sobre la intercesión?",
            "¿Qué representa la cena de bodas del Cordero?",
            "¿Cómo la justicia de Cristo se manifiesta en el juicio final?",
            "¿Qué rol tiene la esperanza en la vida cristiana?",
            "¿Cómo el libro de los Salmos describe la relación del creyente con Dios?",
            "¿Qué representa la caída de Babilonia en Apocalipsis?",
            '¿Por qué Jesús dijo "No he venido a abolir la ley"?',
            "¿Qué simboliza el Espíritu Santo en la forma de una paloma?",
            "¿Qué relación tienen las bienaventuranzas con la vida cristiana?",
            "¿Cómo la Biblia describe el carácter del anticristo?",
            "¿Qué lecciones podemos aprender de la vida de José en Egipto?",
            '¿Qué significa "Dios es amor" según las Escrituras?',
            "¿Qué relación tiene la cruz con la segunda venida?",
            "¿Por qué el sábado será un tema de conflicto en el tiempo del fin?",
        ];

        const container = document.getElementById("suggestions-container");
        if (!container) return;

        container.innerHTML = "";
        container.style.display = "flex";

        suggestions
            .sort(() => Math.random() - 0.5)
            .slice(0, 3)
            .forEach((suggestion) => {
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
        const suggestionsContainer = document.getElementById(
            "suggestions-container",
        );

        if (!message || this.state.isProcessing) {
            console.log("Mensaje vacío o el sistema está ocupado.");
            return;
        }

        // Hide suggestions and clear chat
        if (suggestionsContainer) {
            suggestionsContainer.style.display = "none";
        }
        // No limpiar el historial para mantener la conversación fluida
        if (!chatHistory) {
            console.error("Elemento chat-history no encontrado");
            return;
        }

        // Validar longitud del mensaje
        if (message.length > 500) {
            alert("El mensaje es demasiado largo. Por favor, acórtalo.");
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
            
            const steps = [
                { id: 'thinking', text: 'Procesando consulta', time: 1000 },
                { id: 'doctrinal', text: 'Aplicando validación doctrinal', time: 1500 },
                { id: 'biblical', text: 'Aplicando interpretación bíblica', time: 1500 },
                { id: 'apologetic', text: 'Verificando modo apologético', time: 1000 }
            ];

            thinkingContainer.innerHTML = `
                <div class="nevin-response-container">
                    <img src="/static/images/nevin-icon.svg" alt="Icono de Nevin" class="nevin-icon-response">
                    <div class="thinking-steps">
                        ${steps.map(step => `
                            <div class="thinking-step" id="${step.id}">
                                <span class="step-text">${step.text}</span>
                                <span class="step-dots">
                                    <span class="dot">.</span>
                                    <span class="dot">.</span>
                                    <span class="dot">.</span>
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            document
                .getElementById("chat-history")
                .appendChild(thinkingContainer);
            thinkingContainer.scrollIntoView({ behavior: "smooth" });

            console.log("Enviando datos al backend:");
            console.log({
                question: message,
                user_id: this.state.userId,
            });

            // Llamada al backend
            const response = await fetch("/nevin/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    question: message,
                    user_id: window.userId || this.state.userId,
                }),
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
                "Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.",
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
            this.displayRandomSuggestions(true);
        }
    }

    goHome() {
        window.location.href = "/home";
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
    const parts = reference.split(" ");
    const chapter = parts[parts.length - 1].split(":")[0];
    const verse = parts[parts.length - 1].split(":")[1];
    let book = parts.slice(0, -1).join(" ");

    // Construye la URL
    const url = `/chapter/${encodeURIComponent(book)}/${chapter}#verse-${verse}`;

    // Abre en una nueva pestaña
    window.open(url, "_blank");
};