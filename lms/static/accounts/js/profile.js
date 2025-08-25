// accounts/static/accounts/js/profile.js

class ProfileManager {
    constructor() {
        this.initProfileForm();
        this.initPasswordValidation();
    }

    initProfileForm() {
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            this.setupProfileForm(profileForm);
        }
    }

    setupProfileForm(form) {
        form.addEventListener('submit', (e) => {
            if (!this.validateProfileForm(form)) {
                e.preventDefault();
            }
        });

        // Real-time validation
        this.setupRealTimeValidation(form);
    }

    validateProfileForm(form) {
        let isValid = true;
        
        // Email validation
        const email = form.querySelector('#email');
        if (email && !this.isValidEmail(email.value)) {
            this.showError(email, 'Please enter a valid email address');
            isValid = false;
        }

        // Password validation if changing password
        if (this.isChangingPassword(form)) {
            if (!this.validatePasswordChange(form)) {
                isValid = false;
            }
        }

        return isValid;
    }

    isChangingPassword(form) {
        const currentPassword = form.querySelector('#current_password');
        return currentPassword && currentPassword.value.trim() !== '';
    }

    validatePasswordChange(form) {
        let isValid = true;
        
        const currentPassword = form.querySelector('#current_password');
        const newPassword = form.querySelector('#new_password');
        const confirmPassword = form.querySelector('#confirm_password');

        if (newPassword.value !== confirmPassword.value) {
            this.showError(confirmPassword, 'Passwords do not match');
            isValid = false;
        }

        if (newPassword.value.length < 8) {
            this.showError(newPassword, 'Password must be at least 8 characters long');
            isValid = false;
        }

        return isValid;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showError(field, message) {
        field.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    setupRealTimeValidation(form) {
        const fields = form.querySelectorAll('input, textarea');
        fields.forEach(field => {
            field.addEventListener('input', () => {
                field.classList.remove('is-invalid');
                
                const errorMessage = field.parentNode.querySelector('.invalid-feedback');
                if (errorMessage) {
                    errorMessage.remove();
                }
            });
        });
    }

    initPasswordValidation() {
        const passwordForm = document.getElementById('password-form');
        if (passwordForm) {
            this.setupPasswordForm(passwordForm);
        }
    }

    setupPasswordForm(form) {
        // Similar setup as profile form
    }
}

// Initialize profile manager
document.addEventListener('DOMContentLoaded', function() {
    new ProfileManager();
});