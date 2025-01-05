document.addEventListener("DOMContentLoaded", function () {
    // Configuración de la validación de formularios
    initializePasswordToggles();
    initializeFormValidation();
    initializePasswordStrength();
    checkStoredToken();
});

function checkStoredToken() {
    const token = localStorage.getItem('auth_token');
    const tokenExpiry = localStorage.getItem('token_expiry');
    
    if (token && tokenExpiry && new Date().getTime() < parseInt(tokenExpiry)) {
        document.cookie = `token=${token};path=/;max-age=${60*60*24*30}`;
    } else {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token_expiry');
    }
}

function storeToken(token) {
    const expiryTime = new Date().getTime() + (30 * 24 * 60 * 60 * 1000); // 30 días
    localStorage.setItem('auth_token', token);
    localStorage.setItem('token_expiry', expiryTime.toString());
}

function initializePasswordToggles() {
    const toggleConfigs = [
        { toggleId: "#togglePassword", passwordId: "#password" },
        { toggleId: "#toggleConfirmPassword", passwordId: "#confirm_password" }
    ];

    toggleConfigs.forEach(config => {
        setupPasswordToggle(config.toggleId, config.passwordId);
    });
}

function setupPasswordToggle(toggleId, passwordId) {
    try {
        const toggleButton = document.querySelector(toggleId);
        const passwordInput = document.querySelector(passwordId);

        if (!toggleButton || !passwordInput) {
            console.warn(`Elementos no encontrados para ${toggleId} o ${passwordId}`);
            return;
        }

        // Añadir atributos de accesibilidad
        toggleButton.setAttribute('role', 'button');
        toggleButton.setAttribute('aria-label', 'Mostrar/Ocultar contraseña');
        toggleButton.setAttribute('tabindex', '0');

        // Estado visual
        const statusSpan = document.createElement('span');
        statusSpan.className = 'password-status';
        statusSpan.setAttribute('aria-live', 'polite');
        toggleButton.parentNode.insertBefore(statusSpan, toggleButton.nextSibling);

        // Manejadores de eventos
        const togglePassword = () => {
            try {
                const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
                passwordInput.setAttribute("type", type);

                const icon = toggleButton.querySelector("i");
                if (icon) {
                    icon.classList.toggle("bi-eye");
                    icon.classList.toggle("bi-eye-slash");
                }

                statusSpan.textContent = type === "text" ? "Contraseña visible" : "Contraseña oculta";
                statusSpan.classList.toggle('visible', type === "text");
            } catch (error) {
                console.error("Error al cambiar visibilidad:", error);
            }
        };

        toggleButton.addEventListener("click", togglePassword);
        toggleButton.addEventListener("keypress", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                togglePassword();
            }
        });
    } catch (error) {
        console.error(`Error configurando toggle de contraseña: ${error}`);
    }
}

function initializeFormValidation() {
    const loginForm = document.querySelector('.login-form');
    const signupForm = document.querySelector('.signup-form');
    const forgotForm = document.querySelector('.forgot-password-form');

    if (loginForm) setupLoginValidation(loginForm);
    if (signupForm) setupSignupValidation(signupForm);
    if (forgotForm) setupForgotPasswordValidation(forgotForm);
}

function setupLoginValidation(form) {
    const emailInput = form.querySelector('input[type="text"]');
    const passwordInput = form.querySelector('input[type="password"]');

    if (emailInput && passwordInput) {
        emailInput.addEventListener('input', validateLoginEmail);
        form.addEventListener('submit', (e) => validateLoginForm(e, form));
    }
}

function setupSignupValidation(form) {
    const inputs = {
        username: form.querySelector('input[name="username"]'),
        email: form.querySelector('input[name="email"]'),
        password: form.querySelector('input[name="password"]'),
        confirmPassword: form.querySelector('input[name="confirm_password"]')
    };

    if (inputs.username) inputs.username.addEventListener('input', validateUsername);
    if (inputs.email) inputs.email.addEventListener('input', validateEmail);
    if (inputs.password) inputs.password.addEventListener('input', validatePassword);
    if (inputs.confirmPassword) {
        inputs.confirmPassword.addEventListener('input', () => {
            validateConfirmPassword(inputs.password, inputs.confirmPassword);
        });
    }

    form.addEventListener('submit', (e) => validateSignupForm(e, form));
}

function setupForgotPasswordValidation(form) {
    const emailInput = form.querySelector('input[type="email"]');
    if (emailInput) {
        emailInput.addEventListener('input', validateEmail);
        form.addEventListener('submit', (e) => validateForgotPasswordForm(e, form));
    }
}

function validateLoginEmail(e) {
    const input = e.target;
    const value = input.value.trim();
    const isEmail = value.includes('@');
    const isValid = isEmail ? validateEmailFormat(value) : value.length >= 3;

    updateValidationUI(input, isValid);
}

function validateUsername(e) {
    const input = e.target;
    const isValid = input.value.trim().length >= 3;
    updateValidationUI(input, isValid);
}

function validateEmail(e) {
    const input = e.target;
    const isValid = validateEmailFormat(input.value);
    updateValidationUI(input, isValid);
}

function validatePassword(e) {
    const input = e.target;
    const value = input.value;
    const strength = calculatePasswordStrength(value);
    updatePasswordStrengthUI(input, strength);
}

function validateConfirmPassword(passwordInput, confirmInput) {
    const isValid = passwordInput.value === confirmInput.value;
    updateValidationUI(confirmInput, isValid);
}

function validateEmailFormat(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email.toLowerCase());
}

function calculatePasswordStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.match(/[A-Z]/)) score++;
    if (password.match(/[a-z]/)) score++;
    if (password.match(/[0-9]/)) score++;
    if (password.match(/[^A-Za-z0-9]/)) score++;
    return score;
}

function updateValidationUI(input, isValid) {
    input.classList.toggle('is-valid', isValid);
    input.classList.toggle('is-invalid', !isValid);
}

function updatePasswordStrengthUI(input, strength) {
    const container = input.parentElement;
    let strengthIndicator = container.querySelector('.password-strength');

    if (!strengthIndicator) {
        strengthIndicator = document.createElement('div');
        strengthIndicator.className = 'password-strength';
        container.appendChild(strengthIndicator);
    }

    const strengthClasses = ['muy-débil', 'débil', 'media', 'fuerte', 'muy-fuerte'];
    strengthIndicator.className = `password-strength ${strengthClasses[strength-1] || ''}`;
    strengthIndicator.textContent = `Fortaleza: ${strengthClasses[strength-1] || 'muy-débil'}`;
}

function validateLoginForm(e, form) {
    const emailInput = form.querySelector('input[type="text"]');
    const passwordInput = form.querySelector('input[type="password"]');

    if (!emailInput.value.trim() || !passwordInput.value) {
        e.preventDefault();
        showFormError(form, "Por favor completa todos los campos");
    }
}

function validateSignupForm(e, form) {
    const inputs = {
        username: form.querySelector('input[name="username"]'),
        email: form.querySelector('input[name="email"]'),
        password: form.querySelector('input[name="password"]'),
        confirmPassword: form.querySelector('input[name="confirm_password"]')
    };

    if (!inputs.username.value.trim() || !inputs.email.value.trim() || 
        !inputs.password.value || !inputs.confirmPassword.value) {
        e.preventDefault();
        showFormError(form, "Por favor completa todos los campos");
        return;
    }

    if (!validateEmailFormat(inputs.email.value)) {
        e.preventDefault();
        showFormError(form, "Por favor ingresa un email válido");
        return;
    }

    if (inputs.password.value !== inputs.confirmPassword.value) {
        e.preventDefault();
        showFormError(form, "Las contraseñas no coinciden");
        return;
    }

    if (calculatePasswordStrength(inputs.password.value) < 3) {
        e.preventDefault();
        showFormError(form, "La contraseña debe ser más fuerte");
    }
}

function validateForgotPasswordForm(e, form) {
    const emailInput = form.querySelector('input[type="email"]');

    if (!emailInput.value.trim() || !validateEmailFormat(emailInput.value)) {
        e.preventDefault();
        showFormError(form, "Por favor ingresa un email válido");
    }
}

function showFormError(form, message) {
    let errorDiv = form.querySelector('.form-error');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'form-error alert alert-danger mt-3';
        form.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Inicializar medidor de fortaleza de contraseña
function initializePasswordStrength() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', validatePassword);
    });
}