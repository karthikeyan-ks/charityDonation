document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('org-login-form');
    const passwordToggle = document.getElementById('org-password-toggle');
    const passwordInput = document.getElementById('org-password');

    // Toggle password visibility
    if (passwordToggle) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.querySelector('i').classList.toggle('icon-eye');
            this.querySelector('i').classList.toggle('icon-eye-blocked');
        });
    }

    // Check if already logged in as organization
    if (localStorage.getItem('access') && localStorage.getItem('userType') === 'organization') {
        console.log('Already logged in as organization, redirecting to orgsubmit.html');
        window.location.href = '/orgsubmit.html';
        return;
    }

    // Handle form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
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
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Clear any existing auth data first
                    localStorage.clear();
                    
                    // Store the tokens and user info
                    localStorage.setItem('access', data.access);
                    localStorage.setItem('refresh', data.refresh);
                    localStorage.setItem('userEmail', email);
                    localStorage.setItem('userId', data.user_id);
                    
                    // IMPORTANT: Set user type to organization
                    localStorage.setItem('userType', 'organization');
                    
                    // Set username or use email as fallback
                    localStorage.setItem('userName', data.username || email.split('@')[0]);
                    
                    console.log('Login successful, userType set to:', localStorage.getItem('userType'));
                    console.log('All localStorage items after login:');
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        console.log(`- ${key}: ${localStorage.getItem(key)}`);
                    }
                    
                    // Show success message
                    showAlert('Login successful! Redirecting...', 'success');
                    
                    // Redirect to organization submission page after a short delay
                    setTimeout(() => {
                        window.location.href = '/orgsubmit.html';
                    }, 1000);
                } else {
                    const errorData = await response.json();
                    showAlert(errorData.detail || 'Login failed. Please check your credentials.', 'danger');
                }
            } catch (error) {
                console.error('Login error:', error);
                showAlert('An error occurred during login. Please try again.', 'danger');
            }
        });
    }
});

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

// Function to show alert messages
function showAlert(message, type) {
    // Remove any existing alerts
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    // Insert alert before the form
    const form = document.getElementById('org-login-form');
    form.parentNode.insertBefore(alertDiv, form);

    // Remove alert after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Toggle between login and signup forms
document.getElementById('showSignUp').addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signUpForm').style.display = 'block';
    document.querySelector('.stepper').style.display = 'block';
});

document.getElementById('showLogin').addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('signUpForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
});

document.getElementById('backToLogin').addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('signUpForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
});

// Stepper functionality
document.getElementById('goToStep2').addEventListener('click', function() {
    document.getElementById('step1').classList.remove('active');
    document.getElementById('step2').classList.add('active');
    document.querySelectorAll('.stepper-dot')[0].classList.remove('active');
    document.querySelectorAll('.stepper-dot')[1].classList.add('active');
});

document.getElementById('backToStep1').addEventListener('click', function() {
    document.getElementById('step2').classList.remove('active');
    document.getElementById('step1').classList.add('active');
    document.querySelectorAll('.stepper-dot')[1].classList.remove('active');
    document.querySelectorAll('.stepper-dot')[0].classList.add('active');
});

document.getElementById('goToStep3').addEventListener('click', function() {
    document.getElementById('step2').classList.remove('active');
    document.getElementById('step3').classList.add('active');
    document.querySelectorAll('.stepper-dot')[1].classList.remove('active');
    document.querySelectorAll('.stepper-dot')[2].classList.add('active');
});

document.getElementById('backToStep2').addEventListener('click', function() {
    document.getElementById('step3').classList.remove('active');
    document.getElementById('step2').classList.add('active');
    document.querySelectorAll('.stepper-dot')[2].classList.remove('active');
    document.querySelectorAll('.stepper-dot')[1].classList.add('active');
});

// Handle organization registration
document.getElementById('completeRegistration').addEventListener('click', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('orgName').value);
    formData.append('email', document.getElementById('signupEmail').value);
    formData.append('phone', document.getElementById('signupPhone').value);
    formData.append('password', document.getElementById('signupPassword').value);
    formData.append('license_number', document.getElementById('licenseNumber').value);
    formData.append('description', document.getElementById('orgDescription').value);
    
    const certFile = document.getElementById('certFile').files[0];
    if (certFile) {
        formData.append('registration_certificate', certFile);
    }
    
    try {
        const response = await fetch('/api/organization/register/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Store organization info in localStorage for the pending page
            localStorage.setItem('pendingOrgName', document.getElementById('orgName').value);
            localStorage.setItem('pendingOrgEmail', document.getElementById('signupEmail').value);
            localStorage.setItem('pendingOrgId', data.organization_id);
            
            showAlert('Registration submitted successfully! Redirecting to pending approval page...', 'success');
            setTimeout(() => {
                window.location.href = 'org-pending.html';
            }, 2000);
        } else {
            const errorData = await response.json();
            showAlert(errorData.detail || 'Registration failed. Please try again.', 'danger');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAlert('An error occurred during registration. Please try again.', 'danger');
    }
}); 