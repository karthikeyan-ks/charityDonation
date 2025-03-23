/**
 * Logout Handler
 * Provides consistent logout functionality across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Logout handler loaded");
    
    // Find all logout elements by their IDs
    const logoutElements = [
        document.getElementById('logout-button'),    // Index page
        document.getElementById('logoutBtn'),        // Dashboard pages
        document.getElementById('logoutLink'),       // Admin/org pages
        ...document.querySelectorAll('[data-action="logout"]') // Any element with data-action="logout"
    ].filter(el => el !== null); // Filter out null elements
    
    console.log(`Found ${logoutElements.length} logout elements`);
    
    // Add click event to all logout elements found
    logoutElements.forEach(element => {
        console.log(`Setting up logout handler for element: ${element.id || element.className || 'unnamed'}`);
        
        element.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Logout clicked - clearing storage and redirecting");
            
            // Clear all localStorage
            localStorage.clear();
            
            // Also clear sessionStorage just to be safe
            sessionStorage.clear();
            
            // Also expire/remove any cookies
            document.cookie.split(";").forEach(function(c) {
                document.cookie = c.replace(/^ +/, "").replace(/=.*/, 
                "=;expires=" + new Date().toUTCString() + ";path=/");
            });
            
            // Redirect to homepage
            window.location.href = '/index.html';
        });
    });
    
    // As a backup, also add a global function that can be called directly
    window.performLogout = function() {
        console.log("Performing logout via global function");
        localStorage.clear();
        sessionStorage.clear();
        document.cookie.split(";").forEach(function(c) {
            document.cookie = c.replace(/^ +/, "").replace(/=.*/, 
            "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        window.location.href = '/index.html';
    };
}); 