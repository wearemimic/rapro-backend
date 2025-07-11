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
  }
};

export default apiService; 