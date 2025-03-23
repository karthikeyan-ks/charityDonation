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

    // Function to fetch categories
    async function fetchCategories() {
        try {
            const response = await fetch('/api/items/categories/');
            if (!response.ok) {
                throw new Error('Failed to fetch categories');
            }
            const categories = await response.json();
            
            // Get the category select element
            const categorySelect = document.getElementById('itemCategory');
            if (!categorySelect) return;

            // Clear existing options except the first one
            while (categorySelect.options.length > 1) {
                categorySelect.remove(1);
            }

            // Add categories from the backend
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });

            // Add the "Other" option at the end
            const otherOption = document.createElement('option');
            otherOption.value = 'other';
            otherOption.textContent = 'Other';
            categorySelect.appendChild(otherOption);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    }

    // Fetch categories when the page loads
    fetchCategories();

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
                // Create donation data object
                let donationData = {
                    name: document.getElementById('itemName').value.trim(),
                    description: document.getElementById('itemDescription').value.trim(),
                    condition: document.getElementById('itemCondition').value,
                    quantity: parseInt(document.getElementById('itemQuantity').value),
                    pickup_address: document.getElementById('pickupAddress').value.trim(),
                    status: 'available',
                    donor: parseInt(userId)
                };

                // Get the category value
                const categorySelect = document.getElementById('itemCategory');
                const categoryValue = categorySelect.value;
                
                // If "other" is selected, create a new category first
                if (categoryValue === 'other') {
                    const otherCategoryName = document.getElementById('otherCategory').value;
                    if (!otherCategoryName) {
                        alert('Please specify the category name');
                        return;
                    }
                    
                    // Create new category
                    const categoryResponse = await makeAuthenticatedRequest('/api/items/categories/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ name: otherCategoryName })
                    });
                    
                    if (!categoryResponse.ok) {
                        const errorData = await categoryResponse.json();
                        throw new Error(errorData.detail || 'Failed to create new category');
                    }
                    
                    const newCategory = await categoryResponse.json();
                    donationData.category = newCategory.id;
                } else {
                    donationData.category = parseInt(categoryValue);
                }

                // Validate required fields
                if (!donationData.name || !donationData.description || !donationData.condition || 
                    !donationData.quantity || !donationData.pickup_address) {
                    alert('Please fill in all required fields');
                    return;
                }

                // Validate quantity is a positive number
                if (isNaN(donationData.quantity) || donationData.quantity <= 0) {
                    alert('Please enter a valid quantity (must be a positive number)');
                    return;
                }

                // Log the data being sent
                console.log('Sending donation data:', donationData);

                // Submit the donation
                try {
                    const response = await makeAuthenticatedRequest('/api/items/items/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify(donationData)
                    });

                    if (response.ok) {
                        // Show success message
                        donationSuccess.style.display = 'block';
                        donationForm.style.display = 'none';
                        
                        // Redirect to donor dashboard after 3 seconds
                        setTimeout(() => {
                            window.location.href = '/donor-dashboard.html';
                        }, 3000);
                    } else {
                        const data = await response.json();
                        console.error('Server response:', data);
                        if (response.status === 401) {
                            localStorage.clear();
                            alert('Your session has expired. Please log in again.');
                            window.location.href = '/donor.html';
                        } else {
                            // Log the complete error response
                            console.error('Error details:', {
                                status: response.status,
                                statusText: response.statusText,
                                data: data
                            });
                            throw new Error(data.detail || data.message || 'Failed to submit donation');
                        }
                    }
                } catch (error) {
                    console.error('Error submitting donation:', error);
                    // Log the complete error object
                    console.error('Full error object:', {
                        message: error.message,
                        stack: error.stack,
                        name: error.name
                    });
                    alert(error.message || 'Failed to submit donation. Please try again.');
                }
            } catch (error) {
                console.error('Error submitting donation:', error);
                alert(error.message || 'Failed to submit donation. Please try again.');
            }
        });
    }
}); 