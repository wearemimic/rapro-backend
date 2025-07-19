// Auth0 configuration
export const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN || 'your-auth0-domain.auth0.com',
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID || 'your-auth0-client-id',
  audience: import.meta.env.VITE_AUTH0_AUDIENCE || 'https://api.retirementadvisorpro.com',
  redirectUri: import.meta.env.VITE_AUTH0_CALLBACK_URL || 'http://localhost:3000/auth/callback',
  logoutRedirectUri: import.meta.env.VITE_AUTH0_LOGOUT_URL || 'http://localhost:3000',
};

// Debug logging
console.log('🔧 Auth0 Config:', {
  domain: auth0Config.domain,
  clientId: auth0Config.clientId,
  audience: auth0Config.audience,
  redirectUri: auth0Config.redirectUri,
  env_domain: import.meta.env.VITE_AUTH0_DOMAIN,
  env_client_id: import.meta.env.VITE_AUTH0_CLIENT_ID,
}); 