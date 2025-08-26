/**
 * Token validation and refresh utilities
 */

/**
 * Decode JWT token and get expiration time
 * @param {string} token - JWT token
 * @returns {object|null} Decoded token payload or null if invalid
 */
export function decodeToken(token) {
  if (!token) return null;
  
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const payload = parts[1];
    const decoded = JSON.parse(atob(payload));
    return decoded;
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
}

/**
 * Check if token is expired or expires soon
 * @param {string} token - JWT token
 * @param {number} bufferMinutes - Minutes before expiration to consider as "expired"
 * @returns {boolean} True if token is expired or expires soon
 */
export function isTokenExpiringSoon(token, bufferMinutes = 5) {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;
  
  const now = Math.floor(Date.now() / 1000);
  const expirationBuffer = bufferMinutes * 60;
  
  return decoded.exp <= (now + expirationBuffer);
}

/**
 * Get token expiration time in minutes from now
 * @param {string} token - JWT token
 * @returns {number} Minutes until expiration, or -1 if expired/invalid
 */
export function getTokenExpirationInMinutes(token) {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return -1;
  
  const now = Math.floor(Date.now() / 1000);
  const secondsUntilExpiration = decoded.exp - now;
  
  return Math.floor(secondsUntilExpiration / 60);
}

/**
 * Check if token is valid (not expired and properly formatted)
 * @param {string} token - JWT token
 * @returns {boolean} True if token is valid
 */
export function isTokenValid(token) {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return false;
  
  const now = Math.floor(Date.now() / 1000);
  return decoded.exp > now;
}