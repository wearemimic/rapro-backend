// Auth0 configuration - Simple setup following Auth0 Vue.js docs
export const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN,
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID,
  redirectUri: window.location.origin + '/auth/callback'
}; 