/**
 * Logout Handler
 * Provides consistent logout functionality across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Logout handler loaded");
    
    // Find all logout buttons
    const logoutButtons = [
        document.getElementById('logout-button'),  // Index page
        document.getElementById('logoutBtn'),      // Dashboard pages
        document.getElementById('logoutLink')      // Admin pages
    ];
    
    // Add click event to all logout buttons found
    logoutButtons.forEach(button => {
        if (button) {
            console.log("Found logout button:", button.id);
            button.addEventListener('click', function(e) {
                e.preventDefault();
                console.log("Logout clicked - clearing all storage");
                
                // Clear all localStorage
                localStorage.clear();
                
                // Also clear sessionStorage just to be safe
                sessionStorage.clear();
                
                // Also expire/remove any cookies (optional)
                document.cookie.split(";").forEach(function(c) {
                    document.cookie = c.replace(/^ +/, "").replace(/=.*/, 
                    "=;expires=" + new Date().toUTCString() + ";path=/");
                });
                
                console.log("Storage cleared, redirecting to homepage");
                
                // Redirect to homepage
                window.location.href = '/index.html';
            });
        }
    });
}); 