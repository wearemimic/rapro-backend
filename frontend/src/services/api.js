import { API_CONFIG } from '@/config';

// API URL configuration
const API_BASE_URL = API_CONFIG.BASE_URL;

/**
 * Returns the full API URL for a given endpoint
 * @param {string} endpoint - The API endpoint (should start with '/')
 * @returns {string} The full API URL
 */
export function getApiUrl(endpoint) {
  // Ensure endpoint starts with '/'
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${normalizedEndpoint}`;
}

/**
 * Common API service functions
 */
export const apiService = {
  /**
   * Get the base API URL
   * @returns {string} The base API URL
   */
  getBaseUrl() {
    return API_BASE_URL;
  },
  
  /**
   * Get the full URL for an API endpoint
   * @param {string} endpoint - The API endpoint
   * @returns {string} The full API URL
   */
  getUrl(endpoint) {
    return getApiUrl(endpoint);
  },
  
  /**
   * Get axios config with authentication headers
   * @returns {Object} The axios config object with Authorization header
   */
  getConfig() {
    // Check localStorage first, then cookies as fallback (for PDF generation)
    const token = localStorage.getItem('token') || this.getTokenFromCookie();
    return {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    };
  },
  
  /**
   * Get token from cookie (fallback for when localStorage isn't available, e.g., PDF generation)
   * @returns {string|null} The token from cookie or null
   */
  getTokenFromCookie() {
    const name = 'token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for(let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
    return null;
  }
};

export default apiService; 