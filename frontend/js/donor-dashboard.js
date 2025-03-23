document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    if (!TokenManager.isAuthenticated()) {
        TokenManager.redirectToLogin();
        return;
    }

    // Function to format date
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    // Function to create donation item HTML
    function createDonationItem(donation) {
        const statusClass = `status-${donation.status.toLowerCase()}`;
        
        return `
            <div class="donation-item">
                <div class="donation-header">
                    <h3 class="donation-title">${donation.name}</h3>
                    <span class="donation-status ${statusClass}">${donation.status}</span>
                </div>
                <div class="donation-details">
                    <div class="detail-item">
                        <span class="detail-label">Category</span>
                        <span class="detail-value">${donation.category_name}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Condition</span>
                        <span class="detail-value">${donation.condition}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Quantity</span>
                        <span class="detail-value">${donation.quantity}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Submitted On</span>
                        <span class="detail-value">${formatDate(donation.created_at)}</span>
                    </div>
                </div>
                ${donation.image ? `<img src="${donation.image}" alt="${donation.name}" class="donation-image">` : ''}
                <div class="action-buttons">
                    ${donation.status === 'available' ? `
                        <button class="btn btn-danger" onclick="cancelDonation(${donation.id})">Cancel Donation</button>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Function to load donations
    async function loadDonations() {
        try {
            // Use TokenManager for authenticated request
            const response = await TokenManager.authenticatedFetch('/api/items/items/');
            
            if (!response.ok) {
                throw new Error(`Failed to load donations: ${response.status}`);
            }
            
            const donations = await response.json();
            const donationList = document.getElementById('donationList');
            
            if (donations.length === 0) {
                donationList.innerHTML = `
                    <div class="empty-state">
                        <i class="icon-gift"></i>
                        <p>You haven't submitted any donations yet.</p>
                        <a href="donsubmit.html" class="btn btn-primary">Submit Your First Donation</a>
                    </div>
                `;
                return;
            }
            
            donationList.innerHTML = donations.map(createDonationItem).join('');
        } catch (error) {
            console.error('Error loading donations:', error);
            const donationList = document.getElementById('donationList');
            donationList.innerHTML = `
                <div class="alert alert-info">
                    There was an issue loading your donations. You can still submit a new donation below.
                    <a href="donsubmit.html" class="btn btn-primary mt-3">Make a Donation</a>
                </div>
            `;
        }
    }

    // Function to cancel donation
    window.cancelDonation = async function(donationId) {
        if (!confirm('Are you sure you want to cancel this donation?')) {
            return;
        }

        try {
            // Use TokenManager for authenticated request
            const response = await TokenManager.authenticatedFetch(`/api/items/items/${donationId}/cancel/`, {
                method: 'POST'
            });

            if (response.ok) {
                loadDonations(); // Reload the donations list
            } else {
                const data = await response.json();
                alert(data.error || 'Failed to cancel donation');
            }
        } catch (error) {
            console.error('Error cancelling donation:', error);
            alert('Failed to cancel donation. Please try again.');
        }
    };

    // Note: Logout is now handled by logout-handler.js

    // Load donations when the page loads - with delay to ensure database connection
    setTimeout(loadDonations, 500);
}); 