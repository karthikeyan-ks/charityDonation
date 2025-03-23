document.addEventListener('DOMContentLoaded', function() {
    // Get user info from localStorage
    const userEmail = localStorage.getItem('userEmail');
    const userId = localStorage.getItem('userId');
    
    // Function to get the current access token
    function getAccessToken() {
        return localStorage.getItem('access');
    }
    
    // Function to check if user is logged in
    function checkAuth() {
        const token = getAccessToken();
        if (!token) {
            localStorage.clear(); // Clear any partial data
            window.location.href = '/donor.html';
            return false;
        }
        return true;
    }
    
    // Initial auth check
    if (!checkAuth()) return;
    
    // Display user info
    const userEmailElement = document.getElementById('userEmail');
    if (userEmail && userEmailElement) {
        userEmailElement.textContent = userEmail;
    }

    // Handle condition selection
    const conditionOptions = document.querySelectorAll('.condition-option');
    const conditionInput = document.getElementById('itemCondition');
    
    if (conditionOptions && conditionInput) {
        conditionOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Remove selected class from all options
                conditionOptions.forEach(opt => opt.classList.remove('selected'));
                // Add selected class to clicked option
                this.classList.add('selected');
                // Update hidden input value
                conditionInput.value = this.dataset.value;
            });
        });
    }

    // Handle category selection
    const categorySelect = document.getElementById('itemCategory');
    const otherCategoryField = document.getElementById('otherCategoryField');
    
    if (categorySelect && otherCategoryField) {
        categorySelect.addEventListener('change', function() {
            otherCategoryField.style.display = this.value === 'other' ? 'block' : 'none';
        });
    }

    // Handle image preview
    const imageInput = document.getElementById('itemImage');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Function to handle token refresh
    async function refreshToken() {
        try {
            const refresh = localStorage.getItem('refresh');
            if (!refresh) {
                throw new Error('No refresh token available');
            }

            const response = await fetch('/api/token/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ refresh })
            });

            if (response.ok) {
                const data = await response.json();
                if (!data.access) {
                    throw new Error('No access token in refresh response');
                }
                localStorage.setItem('access', data.access);
                // Update refresh token if provided
                if (data.refresh) {
                    localStorage.setItem('refresh', data.refresh);
                }
                return data.access;
            } else {
                const errorData = await response.json();
                console.error('Token refresh failed:', errorData);
                // If refresh token is invalid, clear storage and redirect to login
                if (response.status === 401) {
                    localStorage.clear();
                    window.location.href = '/donor.html';
                }
                throw new Error(errorData.detail || 'Token refresh failed');
            }
        } catch (error) {
            console.error('Error refreshing token:', error);
            localStorage.clear(); // Clear storage on error
            window.location.href = '/donor.html'; // Redirect to login
            return null;
        }
    }

    // Add getCookie function since it's used by refreshToken
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

    // Function to make authenticated request
    async function makeAuthenticatedRequest(url, options = {}) {
        let token = getAccessToken();
        
        if (!token) {
            throw new Error('No access token available');
        }

        // Add authorization header
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };

        let response = await fetch(url, { ...options, headers });

        // If unauthorized, try refreshing token
        if (response.status === 401) {
            token = await refreshToken();
            
            if (!token) {
                throw new Error('Token refresh failed');
            }

            // Update authorization header with new token
            headers.Authorization = `Bearer ${token}`;
            response = await fetch(url, { ...options, headers });
        }

        return response;
    }

    // Handle form submission
    const donationForm = document.getElementById('itemDonationForm');
    const donationSuccess = document.getElementById('donationSuccess');
    
    if (donationForm && donationSuccess) {
        donationForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Check authentication before proceeding
            if (!checkAuth()) return;

            try {
                // Create FormData object
                const formData = new FormData();
                
                const category = categorySelect.value === 'other' ? 
                    document.getElementById('otherCategory').value : 
                    categorySelect.value;
                    
                formData.append('category', category);
                formData.append('name', document.getElementById('itemName').value);
                formData.append('description', document.getElementById('itemDescription').value);
                formData.append('condition', conditionInput.value);
                formData.append('quantity', document.getElementById('itemQuantity').value);
                formData.append('pickup_address', document.getElementById('pickupAddress').value);
                formData.append('donor', userId);
                
                if (imageInput.files[0]) {
                    formData.append('image', imageInput.files[0]);
                }

                // Make authenticated request
                const response = await makeAuthenticatedRequest('/api/items/items/', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    // Hide form and show success message
                    donationForm.style.display = 'none';
                    donationSuccess.style.display = 'block';
                    setTimeout(() => {
                        window.location.href = '/donor/dashboard/';
                    }, 2000);
                } else {
                    const data = await response.json();
                    if (response.status === 401) {
                        localStorage.clear();
                        alert('Your session has expired. Please log in again.');
                        window.location.href = '/donor.html';
                    } else {
                        alert(data.detail || 'An error occurred while submitting your donation.');
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                alert(error.message || 'An error occurred while submitting your donation. Please try again.');
            }
        });
    }
}); 