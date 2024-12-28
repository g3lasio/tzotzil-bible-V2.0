document.addEventListener("DOMContentLoaded", function () {
    function setupPasswordToggle(toggleId, passwordId) {
        const toggleButton = document.querySelector(toggleId);
        const passwordInput = document.querySelector(passwordId);

        if (toggleButton && passwordInput) {
            toggleButton.addEventListener("click", function (e) {
                // toggle the type attribute
                const type =
                    passwordInput.getAttribute("type") === "password"
                        ? "text"
                        : "password";
                passwordInput.setAttribute("type", type);

                // toggle the icon
                const icon = this.querySelector("i");
                icon.classList.toggle("bi-eye");
                icon.classList.toggle("bi-eye-slash");
            });
        }
    }

    // Setup toggle for both password fields
    setupPasswordToggle("#togglePassword", "#password");
    setupPasswordToggle("#toggleConfirmPassword", "#confirm_password");
});
