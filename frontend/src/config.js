/**
 * Application configuration
 */

// Set this to true to use the local network IP instead of localhost
const USE_NETWORK_IP = false;

// API URL configuration
// You can override this with environment variables in .env file
export const API_CONFIG = {
  // Base URL for API requests
  BASE_URL: USE_NETWORK_IP 
    ? 'http://192.168.1.83:8000' 
    : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'),
};

export default {
  API_CONFIG
}; 