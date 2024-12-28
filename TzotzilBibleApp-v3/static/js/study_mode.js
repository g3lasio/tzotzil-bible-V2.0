document.getElementById("ask-button").addEventListener("click", function () {
    const userQuestion = document.getElementById("user-question").value;
    if (userQuestion.trim() !== "") {
        // Implementar la lógica para responder preguntas (podría conectarse a una API o un set de respuestas)
        alert(`Usuario pregunta: ${userQuestion}`);
    }
});
