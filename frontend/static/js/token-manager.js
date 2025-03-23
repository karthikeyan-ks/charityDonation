/**
 * Token Management Utility
 * Handles storage, retrieval, validation and refresh of authentication tokens
 */

// Token storage keys
const TOKEN_STORAGE = {
  ACCESS: 'access',
  REFRESH: 'refresh',
  USER_ID: 'userId',
  USER_EMAIL: 'userEmail',
  USER_TYPE: 'userType',
  USER_NAME: 'userName',
  EXPIRY: 'tokenExpiry'
};

// Store tokens with expiration time
function storeTokens(accessToken, refreshToken, expiryInMinutes = 60) {
  localStorage.setItem(TOKEN_STORAGE.ACCESS, accessToken);
  if (refreshToken) localStorage.setItem(TOKEN_STORAGE.REFRESH, refreshToken);
  
  // Set expiration time
  const expiryTime = new Date();
  expiryTime.setMinutes(expiryTime.getMinutes() + expiryInMinutes);
  localStorage.setItem(TOKEN_STORAGE.EXPIRY, expiryTime.getTime());
  
  console.log("Tokens stored successfully, expires at:", expiryTime);
}

// Store user information
function storeUserInfo(userId, email, userType, name) {
  // Clear any existing auth data first
  clearAuthData();
  
  if (userId) localStorage.setItem(TOKEN_STORAGE.USER_ID, userId);
  if (email) localStorage.setItem(TOKEN_STORAGE.USER_EMAIL, email);
  if (userType) localStorage.setItem(TOKEN_STORAGE.USER_TYPE, userType);
  if (name) localStorage.setItem(TOKEN_STORAGE.USER_NAME, name);
  
  console.log("User info stored for:", email, "with userType:", userType);
}

// Get the stored access token
function getAccessToken() {
  return localStorage.getItem(TOKEN_STORAGE.ACCESS);
}

// Check if the user is authenticated
function isAuthenticated() {
  const token = getAccessToken();
  const expiry = localStorage.getItem(TOKEN_STORAGE.EXPIRY);
  
  if (!token) return false;
  
  // Check if token is expired
  if (expiry && new Date().getTime() > parseInt(expiry)) {
    console.log("Token expired, attempting refresh");
    return false;
  }
  
  return true;
}

// Get user information
function getUserInfo() {
  return {
    id: localStorage.getItem(TOKEN_STORAGE.USER_ID),
    email: localStorage.getItem(TOKEN_STORAGE.USER_EMAIL),
    userType: localStorage.getItem(TOKEN_STORAGE.USER_TYPE),
    name: localStorage.getItem(TOKEN_STORAGE.USER_NAME)
  };
}

// Get CSRF token from cookies for secure requests
function getCsrfToken() {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, 'csrftoken='.length) === 'csrftoken=') {
        cookieValue = decodeURIComponent(cookie.substring('csrftoken='.length));
        break;
      }
    }
  }
  return cookieValue;
}

// Refresh the access token
async function refreshToken() {
  const refreshToken = localStorage.getItem(TOKEN_STORAGE.REFRESH);
  if (!refreshToken) {
    console.error("No refresh token available");
    clearAuthData();
    return false;
  }
  
  try {
    const response = await fetch('/api/token/refresh/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (response.ok) {
      const data = await response.json();
      storeTokens(data.access, null, 60); // Only update access token
      return true;
    } else {
      throw new Error('Token refresh failed');
    }
  } catch (error) {
    console.error('Error refreshing token:', error);
    clearAuthData();
    return false;
  }
}

// Make an authenticated API request with automatic token refresh
async function authenticatedFetch(url, options = {}) {
  // Add authorization header if not already present
  const headers = options.headers || {};
  
  if (!headers.Authorization && isAuthenticated()) {
    headers.Authorization = `Bearer ${getAccessToken()}`;
  }
  
  // Make the request
  let response = await fetch(url, { ...options, headers });
  
  // If unauthorized, try to refresh the token
  if (response.status === 401) {
    const refreshSuccessful = await refreshToken();
    
    if (refreshSuccessful) {
      // Retry the request with new token
      headers.Authorization = `Bearer ${getAccessToken()}`;
      response = await fetch(url, { ...options, headers });
    } else {
      // Redirect to login page if refresh failed
      redirectToLogin();
    }
  }
  
  return response;
}

// Clear all authentication data
function clearAuthData() {
  Object.values(TOKEN_STORAGE).forEach(key => localStorage.removeItem(key));
  console.log("Authentication data cleared");
}

// Redirect to the appropriate login page
function redirectToLogin() {
  const userType = localStorage.getItem(TOKEN_STORAGE.USER_TYPE);
  clearAuthData();
  
  if (userType === 'admin') {
    window.location.href = '/admin-login-page.html';
  } else if (userType === 'organization') {
    window.location.href = '/org.html';
  } else {
    window.location.href = '/donor.html';
  }
}

// Export the functions
window.TokenManager = {
  storeTokens,
  storeUserInfo,
  getAccessToken,
  isAuthenticated,
  getUserInfo,
  getCsrfToken,
  refreshToken,
  authenticatedFetch,
  clearAuthData,
  redirectToLogin
}; 