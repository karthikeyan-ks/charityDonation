/**
 * Authentication and User Session Management
 * 
 * This utility script verifies user authentication status and handles session management
 * for the charity donation platform
 */

// Check if user is logged in on pages that require authentication
function checkUserAuthentication() {
    const token = localStorage.getItem('access');
    const userType = localStorage.getItem('userType');
    
    console.log("Auth-check.js - checking authentication:");
    console.log("- token exists:", token ? "yes" : "no");
    console.log("- userType:", userType);
    
    // Get current page path
    const currentPath = window.location.pathname;
    console.log("- current path:", currentPath);
    
    // Define secured paths that require authentication
    const donorSecuredPaths = ['/donor-dashboard.html', '/donsubmit.html'];
    const adminSecuredPaths = ['/admin-dashboard.html', '/admin-donors.html', '/admin-organizations.html'];
    const orgSecuredPaths = ['/organization-dashboard.html', '/orgsubmit.html'];
    
    // Check if current path needs authentication
    const requiresAuth = [
        ...donorSecuredPaths, 
        ...adminSecuredPaths, 
        ...orgSecuredPaths
    ].some(path => currentPath.includes(path));
    
    if (requiresAuth && !token) {
        // No token - redirect to login
        console.log("Authentication required but no token found");
        if (currentPath.includes('admin')) {
            window.location.href = '/admin-login-page.html';
        } else if (currentPath.includes('org')) {
            window.location.href = '/org.html';
        } else {
            window.location.href = '/donor.html';
        }
        return false;
    }
    
    // Strict access control - check if user is on the correct path for their type
    if (token && userType) {
        // Donors can only access donor paths
        if (userType === 'donor') {
            if (orgSecuredPaths.some(path => currentPath.includes(path)) || 
                adminSecuredPaths.some(path => currentPath.includes(path))) {
                console.log("Donor attempting to access restricted path:", currentPath);
                alert("You do not have permission to access this page.");
                window.location.href = '/donor-dashboard.html';
                return false;
            }
        }
        // Organizations can only access organization paths
        else if (userType === 'organization') {
            if (donorSecuredPaths.some(path => currentPath.includes(path)) || 
                adminSecuredPaths.some(path => currentPath.includes(path))) {
                console.log("Organization attempting to access restricted path:", currentPath);
                alert("You do not have permission to access this page.");
                window.location.href = '/orgsubmit.html';
                return false;
            }
        }
        // Admins can only access admin paths
        else if (userType === 'admin') {
            if (donorSecuredPaths.some(path => currentPath.includes(path)) || 
                orgSecuredPaths.some(path => currentPath.includes(path))) {
                console.log("Admin attempting to access restricted path:", currentPath);
                alert("You do not have permission to access this page.");
                window.location.href = '/admin-dashboard.html';
                return false;
            }
        }
    }
    
    return true;
}

// Display user info in the header of authenticated pages
function displayUserInfo() {
    const userNameElement = document.getElementById('userName');
    if (!userNameElement) return;
    
    const userEmail = localStorage.getItem('userEmail');
    const userName = localStorage.getItem('userName') || userEmail || 'User';
    
    userNameElement.textContent = userName;
}

// Check if user is authenticated with a specific role
function isAuthenticated(requiredRole = null) {
    const token = localStorage.getItem('access');
    const userType = localStorage.getItem('userType');
    
    console.log(`isAuthenticated check for role '${requiredRole}':`);
    console.log(`- token exists: ${token ? 'yes' : 'no'}`);
    console.log(`- userType: ${userType}`);
    console.log(`- matches required role: ${userType === requiredRole}`);
    
    if (!token || !userType) return false;
    
    // If role is specified, check if user has that role
    if (requiredRole && userType !== requiredRole) {
        return false;
    }
    
    return true;
}

// Handle logout functionality
function setupLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (!logoutBtn) return;
    
    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        localStorage.clear();
        window.location.href = '/index.html';
    });
}

// Run on page load
document.addEventListener('DOMContentLoaded', function() {
    if (checkUserAuthentication()) {
        displayUserInfo();
        setupLogout();
    }
}); 