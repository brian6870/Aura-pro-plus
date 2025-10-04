// Main JavaScript functionality with modern features
document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initAnimations();
    fixZIndexStacking();
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Confetti animation
function triggerConfetti() {
    const duration = 3 * 1000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);
        
        // Green confetti for environmental theme
        confetti(Object.assign({}, defaults, {
            particleCount,
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
            colors: ['#10b981', '#34d399', '#059669', '#a7f3d0']
        }));
        
        confetti(Object.assign({}, defaults, {
            particleCount,
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
            colors: ['#10b981', '#34d399', '#059669', '#a7f3d0']
        }));
    }, 250);
}

// Enhanced confetti for achievements
function triggerAchievementConfetti() {
    const duration = 5 * 1000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 100 * (timeLeft / duration);
        
        // Multiple color schemes for variety
        const colorSchemes = [
            ['#10b981', '#34d399', '#059669', '#a7f3d0'], // Green theme
            ['#f59e0b', '#fbbf24', '#d97706', '#fcd34d'], // Orange theme
            ['#3b82f6', '#60a5fa', '#1d4ed8', '#93c5fd'], // Blue theme
            ['#8b5cf6', '#a78bfa', '#7c3aed', '#c4b5fd']  // Purple theme
        ];
        
        const colors = colorSchemes[Math.floor(Math.random() * colorSchemes.length)];
        
        confetti(Object.assign({}, defaults, {
            particleCount,
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
            colors: colors
        }));
        
        confetti(Object.assign({}, defaults, {
            particleCount,
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
            colors: colors
        }));
        
        // Add some from the top
        confetti(Object.assign({}, defaults, {
            particleCount: particleCount / 2,
            origin: { x: Math.random(), y: Math.random() - 0.2 },
            colors: colors
        }));
    }, 250);
}

// Initialize enhanced animations
function initAnimations() {
    // Add staggered animations to all cards
    const animatedElements = document.querySelectorAll('.glass-card, .glow-card, .leaderboard-item, .chart-container');
    animatedElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
        element.classList.add('fade-in-up');
    });
    
    // Add loading pulse to elements that might update
    const updateElements = document.querySelectorAll('.stat-number, .chart-fill');
    updateElements.forEach(element => {
        element.classList.add('loading-pulse');
    });
}

// Fix z-index stacking issues
function fixZIndexStacking() {
    // Ensure streak fire is always on top
    const streakFire = document.querySelector('.streak-fire');
    if (streakFire) {
        streakFire.style.zIndex = '50';
    }
    
    // Ensure user dropdown works properly
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    dropdowns.forEach(dropdown => {
        dropdown.style.zIndex = '1100';
    });
    
    // Ensure fire elements have proper z-index
    const fireElements = document.querySelectorAll('.fire, .fire-container');
    fireElements.forEach(fire => {
        fire.style.zIndex = '60';
    });
}

// Utility functions
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add confetti to analysis success
if (window.location.pathname.includes('/analysis/analyze')) {
    setTimeout(() => {
        triggerConfetti();
    }, 1000);
}

// Run on page load and after any animations
document.addEventListener('DOMContentLoaded', function() {
    fixZIndexStacking();
    
    // Re-check after a short delay to catch any dynamic elements
    setTimeout(fixZIndexStacking, 100);
});

// Also fix when navigating (for SPA-like behavior)
window.addEventListener('load', fixZIndexStacking);
// Podium-specific confetti
function triggerPodiumConfetti() {
    const duration = 4 * 1000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 25, spread: 70, ticks: 60, zIndex: 100 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 30 * (timeLeft / duration);
        
        // Gold, Silver, Bronze colors for podium
        const podiumColors = ['#ffd700', '#c0c0c0', '#cd7f32', '#ffffff', '#ffa500'];
        
        // Confetti from top for podium celebration
        confetti(Object.assign({}, defaults, {
            particleCount,
            origin: { x: randomInRange(0.2, 0.8), y: Math.random() - 0.2 },
            colors: podiumColors,
            gravity: randomInRange(0.4, 0.6),
            scalar: randomInRange(0.8, 1.2)
        }));
        
        // Additional burst from sides
        confetti(Object.assign({}, defaults, {
            particleCount: particleCount / 2,
            origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
            colors: podiumColors
        }));
        
        confetti(Object.assign({}, defaults, {
            particleCount: particleCount / 2,
            origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
            colors: podiumColors
        }));
    }, 150);
}

// Enhanced podium interactions
function initPodiumInteractions() {
    const podiumItems = document.querySelectorAll('.podium-item[data-user]');
    
    podiumItems.forEach(item => {
        // Click celebration
        item.addEventListener('click', function() {
            const username = this.getAttribute('data-user');
            const points = this.getAttribute('data-points');
            
            // Add click animation
            this.style.transform = 'translateY(-15px) scale(1.1)';
            setTimeout(() => {
                this.style.transform = 'translateY(-10px) scale(1.05)';
            }, 300);
            
            // Trigger celebration
            triggerPodiumConfetti();
            
            // Show celebration message
            showCelebrationMessage(`${username} - ${points} points! 🎉`);
        });
        
        // Hover effects
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.08)';
            this.style.zIndex = '10';
        });
        
        item.addEventListener('mouseleave', function() {
            if (!this.classList.contains('clicked')) {
                this.style.transform = 'translateY(-10px) scale(1.05)';
            }
            this.style.zIndex = '2';
        });
        
        item.style.cursor = 'pointer';
        item.title = 'Click to celebrate this achiever! 🎉';
    });
}

// Celebration message
function showCelebrationMessage(message) {
    // Remove existing celebration messages
    const existingMessages = document.querySelectorAll('.celebration-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const celebrationMsg = document.createElement('div');
    celebrationMsg.className = 'celebration-message alert-modern position-fixed';
    celebrationMsg.style.cssText = `
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        background: linear-gradient(135deg, #10b981, #3b82f6);
        border: 2px solid rgba(255,255,255,0.3);
        color: white;
        font-weight: 600;
        padding: 1rem 2rem;
        border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: slideDown 0.5s ease-out;
    `;
    celebrationMsg.innerHTML = `<i class="fas fa-trophy me-2"></i>${message}`;
    
    document.body.appendChild(celebrationMsg);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        celebrationMsg.style.animation = 'slideUp 0.5s ease-in';
        setTimeout(() => celebrationMsg.remove(), 500);
    }, 3000);
}

// Add slide animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
        to {
            opacity: 0;
            transform: translateX(-50%) translateY(-50px);
        }
    }
`;
document.head.appendChild(style);

// Initialize podium interactions
document.addEventListener('DOMContentLoaded', function() {
    initPodiumInteractions();
    
    // Auto-trigger podium confetti on page load
    setTimeout(() => {
        const podiumItems = document.querySelectorAll('.podium-item[data-user]');
        if (podiumItems.length > 0) {
            triggerPodiumConfetti();
        }
    }, 2000);
});
