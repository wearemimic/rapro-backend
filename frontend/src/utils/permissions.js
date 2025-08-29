// CRM Permissions System
// Simple permission checking utility for CRM features
import { useAuthStore } from '@/stores/auth';

/**
 * Check if user has access to CRM features
 * @param {Object} user - User object from auth store
 * @returns {boolean} - Whether user has CRM access
 */
export function hasCRMAccess(user) {
  // If no user provided, try to get from localStorage
  if (!user) {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        user = JSON.parse(storedUser);
      }
    } catch (error) {
      console.error('Error parsing user from localStorage:', error);
      return false;
    }
  }
  
  // Check if user exists after trying localStorage
  if (!user) {
    console.log('CRM Access: No user found');
    return false;
  }
  
  console.log('CRM Access Check for user:', user.email, 'Active:', user.is_active);
  
  // Check if user is active
  if (user.is_active === false) {
    console.log('CRM Access: User is not active');
    return false;
  }
  
  // Specific user access - grant CRM access to mannese@wearemimic.com
  if (user.email === 'mannese@wearemimic.com') {
    console.log('CRM Access: Granted for mannese@wearemimic.com');
    return true;
  }
  
  // Check subscription status (if exists)
  if (user.subscription_status === 'inactive' || user.subscription_status === 'cancelled') {
    console.log('CRM Access: Denied due to subscription status:', user.subscription_status);
    return false;
  }
  
  // For now, all other authenticated users also have CRM access
  // In the future, this could check subscription tiers or roles
  console.log('CRM Access: Granted for authenticated user');
  return true;
}

/**
 * Check if user can manage communications for a specific client
 * @param {Object} user - User object from auth store
 * @param {String|Number} clientId - Client ID
 * @returns {boolean} - Whether user can manage this client's communications
 */
export function canManageClientCommunications(user, clientId) {
  // Basic CRM access required
  if (!hasCRMAccess(user)) return false;
  
  // For now, users can manage communications for all their clients
  // In the future, this could check client ownership or team permissions
  return true;
}

/**
 * Check if user can use AI features in CRM
 * @param {Object} user - User object from auth store
 * @returns {boolean} - Whether user has AI features access
 */
export function hasAIFeaturesAccess(user) {
  // Basic CRM access required
  if (!hasCRMAccess(user)) return false;
  
  // For now, all CRM users have AI access
  // In the future, this could check premium subscription tiers
  return true;
}

/**
 * Check if user can send emails
 * @param {Object} user - User object from auth store
 * @returns {boolean} - Whether user can send emails
 */
export function canSendEmails(user) {
  return hasCRMAccess(user);
}

/**
 * Check if user can setup email accounts
 * @param {Object} user - User object from auth store
 * @returns {boolean} - Whether user can setup email accounts
 */
export function canSetupEmailAccounts(user) {
  return hasCRMAccess(user);
}

/**
 * Get permission error message for CRM features
 * @param {String} feature - Feature name
 * @returns {String} - Error message
 */
export function getCRMPermissionErrorMessage(feature = 'CRM') {
  return `You don't have permission to access ${feature} features. Please check your subscription status or contact support.`;
}

/**
 * Permission levels for different CRM features
 */
export const CRM_PERMISSIONS = {
  VIEW_COMMUNICATIONS: 'view_communications',
  MANAGE_COMMUNICATIONS: 'manage_communications',
  SEND_EMAILS: 'send_emails',
  SETUP_EMAIL_ACCOUNTS: 'setup_email_accounts',
  USE_AI_FEATURES: 'use_ai_features',
  VIEW_ANALYTICS: 'view_analytics',
  MANAGE_CLIENT_COMMUNICATIONS: 'manage_client_communications'
};

/**
 * Check if user has specific permission
 * @param {Object} user - User object from auth store
 * @param {String} permission - Permission constant from CRM_PERMISSIONS
 * @param {Object} context - Additional context (like clientId)
 * @returns {boolean} - Whether user has the permission
 */
export function hasPermission(user, permission, context = {}) {
  switch (permission) {
    case CRM_PERMISSIONS.VIEW_COMMUNICATIONS:
      return hasCRMAccess(user);
    
    case CRM_PERMISSIONS.MANAGE_COMMUNICATIONS:
      return hasCRMAccess(user);
    
    case CRM_PERMISSIONS.SEND_EMAILS:
      return canSendEmails(user);
    
    case CRM_PERMISSIONS.SETUP_EMAIL_ACCOUNTS:
      return canSetupEmailAccounts(user);
    
    case CRM_PERMISSIONS.USE_AI_FEATURES:
      return hasAIFeaturesAccess(user);
    
    case CRM_PERMISSIONS.VIEW_ANALYTICS:
      return hasCRMAccess(user);
    
    case CRM_PERMISSIONS.MANAGE_CLIENT_COMMUNICATIONS:
      return canManageClientCommunications(user, context.clientId);
    
    default:
      return false;
  }
}

/**
 * Vue composable for permissions in components
 */
export function usePermissions() {
  const authStore = useAuthStore();
  
  return {
    hasCRMAccess: () => hasCRMAccess(authStore.user),
    canManageClientCommunications: (clientId) => canManageClientCommunications(authStore.user, clientId),
    hasAIFeaturesAccess: () => hasAIFeaturesAccess(authStore.user),
    canSendEmails: () => canSendEmails(authStore.user),
    canSetupEmailAccounts: () => canSetupEmailAccounts(authStore.user),
    hasPermission: (permission, context) => hasPermission(authStore.user, permission, context),
    getCRMPermissionErrorMessage
  };
}