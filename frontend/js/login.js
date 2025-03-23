// Function to handle donor login
async function handleDonorLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('donor-email').value;
    const password = document.getElementById('donor-password').value;
    
    try {
        const response = await fetch('/api/donor/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        // Check if we have a successful response with tokens
        if (response.ok) {
            // Store the tokens and user data
            localStorage.setItem('access', data.access || data.token);
            localStorage.setItem('refresh', data.refresh || data.refresh_token);
            localStorage.setItem('userType', 'donor');
            localStorage.setItem('userEmail', data.email);
            localStorage.setItem('userId', data.user_id);

            // Redirect immediately without showing any messages
            window.location.href = '/donsubmit/';
            return;
        }
        
        // Only show error if login actually failed
        displayError(data.detail || data.message || 'Invalid email or password. Please try again.');
    } catch (error) {
        console.error('Login error:', error);
        displayError('An error occurred. Please try again.');
    }
}

// Function to handle organization login
async function handleOrganizationLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('org-email').value;
    const password = document.getElementById('org-password').value;
    
    try {
        const response = await fetch('/api/organization/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        console.log('Organization login response:', data); // Debug log
        
        if (response.ok) {
            // Verify token data
            if (!data.access || !data.refresh) {
                console.error('Missing tokens in response:', data);
                displayError('Authentication error. Please try again.');
                return;
            }

            // Login successful
            localStorage.setItem('userType', 'organization');
            localStorage.setItem('userEmail', data.email);
            localStorage.setItem('userId', data.user_id);
            localStorage.setItem('access', data.access);
            localStorage.setItem('refresh', data.refresh);

            // Verify storage
            console.log('Stored tokens:', {
                access: localStorage.getItem('access'),
                refresh: localStorage.getItem('refresh')
            });

            window.location.href = '/org/';
        } else {
            // Show error message with more detail
            console.error('Login failed:', data);
            displayError(data.detail || data.message || 'Invalid email or password. Please try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
        displayError('An error occurred. Please try again.');
    }
}

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to display error message
function displayError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.style.marginTop = '10px';
    errorDiv.textContent = message;
    
    // Remove any existing error messages
    const existingError = document.querySelector('.alert-danger');
    if (existingError) {
        existingError.remove();
    }
    
    // Add the new error message
    const form = document.querySelector('form');
    form.insertBefore(errorDiv, form.firstChild);
    
    // Remove error message after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Add event listeners when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    const donorForm = document.getElementById('donor-login-form');
    const orgForm = document.getElementById('org-login-form');
    
    if (donorForm) {
        donorForm.addEventListener('submit', handleDonorLogin);
    }
    
    if (orgForm) {
        orgForm.addEventListener('submit', handleOrganizationLogin);
    }

    // Password visibility toggle functionality
    function setupPasswordToggle(passwordInputId, toggleButtonId) {
        const passwordInput = document.getElementById(passwordInputId);
        const toggleButton = document.getElementById(toggleButtonId);
        
        if (passwordInput && toggleButton) {
            toggleButton.addEventListener('click', function() {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                
                // Toggle the eye icon
                const icon = toggleButton.querySelector('i');
                if (icon) {
                    icon.classList.toggle('icon-eye');
                    icon.classList.toggle('icon-eye-blocked');
                }
            });
        }
    }

    // Setup password toggles
    setupPasswordToggle('donor-password', 'donor-password-toggle');
    setupPasswordToggle('org-password', 'org-password-toggle');
}); 