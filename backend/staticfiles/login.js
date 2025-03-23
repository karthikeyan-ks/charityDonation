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
        
        if (response.ok) {
            // Login successful
            localStorage.setItem('userType', 'donor');
            localStorage.setItem('userEmail', data.email);
            localStorage.setItem('userId', data.user_id);
            window.location.href = '/donorsubmit.html'; // Updated redirect URL
        } else {
            // Show error message
            displayError(data.message || 'Invalid email or password. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
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
        
        if (response.ok) {
            // Login successful
            localStorage.setItem('userType', 'organization');
            localStorage.setItem('userEmail', data.email);
            localStorage.setItem('userId', data.user_id);
            window.location.href = '/org/'; // Redirect to organization dashboard
        } else {
            // Show error message
            displayError(data.message || 'Invalid email or password. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
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
}); 