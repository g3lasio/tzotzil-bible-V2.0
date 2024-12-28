document.getElementById("send-button").addEventListener("click", function () {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() !== "") {
        // Aquí se podría implementar la lógica para interactuar con el asistente (llamada a una API o respuestas predefinidas).
        alert(`Usuario pregunta: ${userInput}`);
    }
});

function sendSuggestion(text) {
    document.getElementById("user-input").value = text;
}
