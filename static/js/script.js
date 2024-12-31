document.addEventListener('DOMContentLoaded', function () {
    initializeParticleBackground();
    initializeFuturisticEffects();
});

// Particle background effect
function initializeParticleBackground() {
    const canvas = document.getElementById('particle-background');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    class Particle {
        constructor() {
            this.reset();
        }
        
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2;
            this.speedX = (Math.random() - 0.5) * 0.5;
            this.speedY = (Math.random() - 0.5) * 0.5;
            this.opacity = Math.random() * 0.5;
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            if (this.x < 0 || this.x > canvas.width || 
                this.y < 0 || this.y > canvas.height) {
                this.reset();
            }
        }
        
        draw() {
            ctx.fillStyle = `rgba(0, 243, 255, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    
    function initParticles() {
        particles = [];
        const particleCount = Math.floor((canvas.width * canvas.height) / 10000);
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        requestAnimationFrame(animate);
    }
    
    window.addEventListener('resize', () => {
        resizeCanvas();
        initParticles();
    });
    
    resizeCanvas();
    initParticles();
    animate();
}

// Futuristic UI effects
function initializeFuturisticEffects() {
    const interactiveElements = document.querySelectorAll('button, .nav-link, .verse-row');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseover', () => {
            element.style.transform = 'scale(1.02)';
            element.style.boxShadow = '0 0 20px rgba(0, 243, 255, 0.4)';
        });
        
        element.addEventListener('mouseout', () => {
            element.style.transform = '';
            element.style.boxShadow = '';
        });
    });
}

// Toast notification helper
window.createToast = function(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const content = document.createElement('div');
    content.className = 'd-flex';
    
    const body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    
    content.appendChild(body);
    content.appendChild(closeButton);
    toast.appendChild(content);
    
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.appendChild(toast);
    document.body.appendChild(container);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => container.remove());
};

// Helper functions (retained from original code)
function addGlowEffect(element) {
    element.style.boxShadow = '0 0 20px rgba(0, 243, 255, 0.4)';
    element.style.transform = 'scale(1.02)';
}

function removeGlowEffect(element) {
    element.style.boxShadow = '';
    element.style.transform = '';
}
function downloadPDF(pdfUrl, filename) {
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = filename;
    link.target = '_blank';
    
    // Detectar dispositivo móvil
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    if (isMobile) {
        // En móviles, abrir en nueva pestaña
        window.open(pdfUrl, '_blank');
    } else {
        // En desktop, descarga directa
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}
