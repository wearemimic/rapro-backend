/**
 * Application configuration
 */

// API URL configuration
// These are set by environment variables at build time
export const API_CONFIG = {
  // Base URL for API requests (backend)
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  // API endpoint URL
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  // Frontend URL (for redirects, callbacks, etc)
  FRONTEND_URL: import.meta.env.VITE_FRONTEND_URL || 'http://localhost:3000',
};

// Auth0 configuration
export const AUTH0_CONFIG = {
  DOMAIN: import.meta.env.VITE_AUTH0_DOMAIN,
  CLIENT_ID: import.meta.env.VITE_AUTH0_CLIENT_ID,
  AUDIENCE: import.meta.env.VITE_AUTH0_AUDIENCE,
  REDIRECT_URI: `${API_CONFIG.FRONTEND_URL}/auth/callback`,
};

// Stripe configuration
export const STRIPE_CONFIG = {
  PUBLIC_KEY: import.meta.env.VITE_STRIPE_PUBLIC_KEY,
};

export default {
  API_CONFIG,
  AUTH0_CONFIG,
  STRIPE_CONFIG
}; 