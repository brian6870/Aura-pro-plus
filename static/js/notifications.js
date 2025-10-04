// Notification Management System for Aura
// Handles automatic dismissal and enhanced notification features

class NotificationManager {
    constructor() {
        this.notificationTimeout = 3000; // 3 seconds
        this.init();
    }

    init() {
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupNotifications());
        } else {
            this.setupNotifications();
        }

        // Also handle dynamically added notifications
        this.setupMutationObserver();
    }

    setupNotifications() {
        // Process existing notifications
        this.processExistingNotifications();
        
        // Enhance Bootstrap alerts with auto-dismiss
        this.enhanceBootstrapAlerts();
        
        // Setup custom notification system
        this.setupCustomNotifications();
    }

    setupMutationObserver() {
        // Watch for new notifications added to the DOM
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList && (
                            node.classList.contains('alert') || 
                            node.classList.contains('notification') ||
                            node.classList.contains('alert-modern')
                        )) {
                            this.autoDismissNotification(node);
                        }
                        
                        // Check children for notifications
                        const newNotifications = node.querySelectorAll ? 
                            node.querySelectorAll('.alert, .notification, .alert-modern') : [];
                        newNotifications.forEach(notification => {
                            this.autoDismissNotification(notification);
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    processExistingNotifications() {
        // Get all existing notifications
        const notifications = document.querySelectorAll(`
            .alert:not(.alert-permanent),
            .notification:not(.permanent),
            .alert-modern:not(.permanent),
            [data-auto-dismiss="true"]
        `);

        notifications.forEach(notification => {
            this.autoDismissNotification(notification);
        });
    }

    enhanceBootstrapAlerts() {
        // Add close buttons to Bootstrap alerts if they don't have them
        const alerts = document.querySelectorAll('.alert:not(:has(.btn-close))');
        alerts.forEach(alert => {
            if (!alert.classList.contains('alert-permanent')) {
                this.addCloseButton(alert);
            }
        });
    }

    addCloseButton(notification) {
        // Only add close button if it doesn't already have one
        if (!notification.querySelector('.btn-close')) {
            const closeButton = document.createElement('button');
            closeButton.type = 'button';
            closeButton.className = 'btn-close btn-close-white';
            closeButton.setAttribute('data-bs-dismiss', 'alert');
            closeButton.setAttribute('aria-label', 'Close');
            
            // Position the close button properly
            if (notification.classList.contains('alert-modern')) {
                closeButton.style.position = 'absolute';
                closeButton.style.top = '1rem';
                closeButton.style.right = '1rem';
                notification.style.position = 'relative';
                notification.style.paddingRight = '3rem';
            }
            
            notification.appendChild(closeButton);
        }
    }

    autoDismissNotification(notification) {
        // Skip if notification is marked as permanent
        if (notification.classList.contains('alert-permanent') || 
            notification.classList.contains('permanent') ||
            notification.hasAttribute('data-no-auto-dismiss')) {
            return;
        }

        // Add fade-out animation class
        notification.style.transition = 'all 0.5s ease-in-out';

        // Set timeout to dismiss
        const dismissTimer = setTimeout(() => {
            this.dismissNotification(notification);
        }, this.notificationTimeout);

        // Store timer reference for manual control
        notification.setAttribute('data-dismiss-timer', dismissTimer);

        // Pause dismissal on hover
        notification.addEventListener('mouseenter', () => {
            clearTimeout(dismissTimer);
            notification.setAttribute('data-timer-paused', 'true');
        });

        // Resume dismissal when mouse leaves
        notification.addEventListener('mouseleave', () => {
            if (notification.getAttribute('data-timer-paused') === 'true') {
                const newTimer = setTimeout(() => {
                    this.dismissNotification(notification);
                }, this.notificationTimeout);
                notification.setAttribute('data-dismiss-timer', newTimer);
                notification.removeAttribute('data-timer-paused');
            }
        });

        // Also dismiss on click
        notification.addEventListener('click', (e) => {
            if (!e.target.classList.contains('btn-close')) {
                this.dismissNotification(notification);
            }
        });
    }

    dismissNotification(notification) {
        // Clear any existing timer
        const existingTimer = notification.getAttribute('data-dismiss-timer');
        if (existingTimer) {
            clearTimeout(parseInt(existingTimer));
        }

        // Add fade-out animation
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        notification.style.maxHeight = '0';
        notification.style.margin = '0';
        notification.style.padding = '0';
        notification.style.overflow = 'hidden';

        // Remove from DOM after animation
        setTimeout(() => {
            if (notification.parentNode) {
                // Use Bootstrap dismiss if available
                if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                    const bsAlert = new bootstrap.Alert(notification);
                    bsAlert.close();
                } else {
                    notification.remove();
                }
            }
        }, 500);
    }

    // Method to show custom notifications
    showCustomNotification(message, type = 'info', duration = null) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-modern fade-in-up`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1060;
            min-width: 300px;
            max-width: 500px;
            backdrop-filter: blur(20px);
        `;

        const icon = this.getNotificationIcon(type);
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${icon} me-3 fs-5"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close btn-close-white ms-3" data-bs-dismiss="alert"></button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto dismiss after specified duration or default
        const dismissTime = duration || this.notificationTimeout;
        setTimeout(() => {
            this.dismissNotification(notification);
        }, dismissTime);

        return notification;
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-triangle text-danger',
            'warning': 'fas fa-exclamation-circle text-warning',
            'info': 'fas fa-info-circle text-info',
            'primary': 'fas fa-bell text-primary'
        };
        return icons[type] || icons['info'];
    }

    // Method to manually dismiss all notifications
    dismissAllNotifications() {
        const notifications = document.querySelectorAll(`
            .alert,
            .notification,
            .alert-modern
        `);

        notifications.forEach(notification => {
            this.dismissNotification(notification);
        });
    }

    // Method to extend notification display time
    extendNotification(notification, additionalTime = 2000) {
        const existingTimer = notification.getAttribute('data-dismiss-timer');
        if (existingTimer) {
            clearTimeout(parseInt(existingTimer));
            
            const newTimer = setTimeout(() => {
                this.dismissNotification(notification);
            }, additionalTime);
            
            notification.setAttribute('data-dismiss-timer', newTimer);
        }
    }
}

// Flash message handler for Flask messages
class FlashMessageHandler {
    constructor() {
        this.notificationManager = new NotificationManager();
        this.init();
    }

    init() {
        // Process Flask flash messages
        this.processFlashMessages();
    }

    processFlashMessages() {
        const flashMessages = document.querySelectorAll('.alert[role="alert"]');
        flashMessages.forEach(message => {
            // Add appropriate styling based on category
            const category = this.detectMessageCategory(message);
            if (category) {
                message.classList.add(`alert-${category}`);
            }
            
            // Ensure modern styling
            if (!message.classList.contains('alert-modern')) {
                message.classList.add('alert-modern');
            }

            // Auto-dismiss
            this.notificationManager.autoDismissNotification(message);
        });
    }

    detectMessageCategory(message) {
        // Detect category from existing classes
        const classes = message.className.split(' ');
        const categoryClass = classes.find(cls => cls.startsWith('alert-'));
        if (categoryClass) {
            return categoryClass.replace('alert-', '');
        }

        // Detect from content or context
        const text = message.textContent.toLowerCase();
        if (text.includes('success') || text.includes('thank you') || text.includes('welcome')) {
            return 'success';
        } else if (text.includes('error') || text.includes('invalid') || text.includes('failed')) {
            return 'danger';
        } else if (text.includes('warning') || text.includes('attention')) {
            return 'warning';
        } else {
            return 'info';
        }
    }
}

// Initialize everything when loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize notification manager
    window.notificationManager = new NotificationManager();
    
    // Initialize flash message handler
    window.flashHandler = new FlashMessageHandler();

    // Add global keyboard shortcut (ESC to close all notifications)
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            window.notificationManager.dismissAllNotifications();
        }
    });

    // Add click-outside to close for custom notifications
    document.addEventListener('click', function(e) {
        if (e.target.closest('.alert, .notification')) {
            return; // Don't close if clicking on notification
        }
        
        // Close all non-flash notifications when clicking outside
        const customNotifications = document.querySelectorAll(`
            .alert:not([role="alert"]),
            .notification
        `);
        
        customNotifications.forEach(notification => {
            window.notificationManager.dismissNotification(notification);
        });
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NotificationManager, FlashMessageHandler };
}