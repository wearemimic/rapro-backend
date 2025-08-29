import axios from 'axios';
import { apiService } from './api.js';

/**
 * Email Service for handling email account management and email operations
 */
class EmailService {
  constructor() {
    this.emailAccountsUrl = '/api/email-accounts';
    this.emailUrl = '/email';
  }

  // =============================================================================
  // EMAIL ACCOUNT MANAGEMENT
  // =============================================================================

  /**
   * Get all email accounts for the current user
   * @returns {Promise<Object>} Email accounts list
   */
  async getEmailAccounts() {
    try {
      const response = await axios.get(apiService.getUrl(this.emailAccountsUrl));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch email accounts');
    }
  }

  /**
   * Get a specific email account by ID
   * @param {number} id - Email account ID
   * @returns {Promise<Object>} Email account details
   */
  async getEmailAccount(id) {
    try {
      const response = await axios.get(apiService.getUrl(`${this.emailAccountsUrl}/${id}/`));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch email account');
    }
  }

  /**
   * Create a new email account
   * @param {Object} data - Email account data
   * @returns {Promise<Object>} Created email account
   */
  async createEmailAccount(data) {
    try {
      const response = await axios.post(apiService.getUrl(this.emailAccountsUrl), data);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to create email account');
    }
  }

  /**
   * Update an email account
   * @param {number} id - Email account ID
   * @param {Object} data - Updated email account data
   * @returns {Promise<Object>} Updated email account
   */
  async updateEmailAccount(id, data) {
    try {
      const response = await axios.put(apiService.getUrl(`${this.emailAccountsUrl}/${id}/`), data);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to update email account');
    }
  }

  /**
   * Delete an email account
   * @param {number} id - Email account ID
   * @returns {Promise<void>}
   */
  async deleteEmailAccount(id) {
    try {
      await axios.delete(apiService.getUrl(`${this.emailAccountsUrl}/${id}/`));
    } catch (error) {
      throw this.handleError(error, 'Failed to delete email account');
    }
  }

  // =============================================================================
  // EMAIL AUTHENTICATION & SETUP
  // =============================================================================

  /**
   * Get Gmail authentication URL
   * @returns {Promise<Object>} Auth URL data
   */
  async getGmailAuthUrl() {
    try {
      const response = await axios.get(apiService.getUrl(`${this.emailUrl}/gmail/auth-url/`));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to get Gmail auth URL');
    }
  }

  /**
   * Get Outlook authentication URL
   * @returns {Promise<Object>} Auth URL data
   */
  async getOutlookAuthUrl() {
    try {
      const response = await axios.get(apiService.getUrl(`${this.emailUrl}/outlook/auth-url/`));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to get Outlook auth URL');
    }
  }

  /**
   * Get OAuth settings status
   * @returns {Promise<Object>} OAuth status
   */
  async getOAuthStatus() {
    try {
      const response = await axios.get(apiService.getUrl('/oauth/status/'));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to get OAuth status');
    }
  }

  // =============================================================================
  // EMAIL OPERATIONS
  // =============================================================================

  /**
   * Send an email
   * @param {Object} emailData - Email data (to, subject, content, etc.)
   * @returns {Promise<Object>} Send result
   */
  async sendEmail(emailData) {
    try {
      const response = await axios.post(apiService.getUrl(`${this.emailUrl}/send/`), emailData);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to send email');
    }
  }

  /**
   * Sync all emails for all accounts
   * @returns {Promise<Object>} Sync result
   */
  async syncAllEmails() {
    try {
      const response = await axios.post(apiService.getUrl(`${this.emailUrl}/sync-all/`));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to sync emails');
    }
  }

  // =============================================================================
  // AI EMAIL OPERATIONS
  // =============================================================================

  /**
   * Analyze a communication with AI
   * @param {number} communicationId - Communication ID
   * @returns {Promise<Object>} AI analysis result
   */
  async analyzeWithAI(communicationId) {
    try {
      const response = await axios.post(apiService.getUrl(`/ai/analyze/${communicationId}/`));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to analyze communication with AI');
    }
  }

  /**
   * Bulk analyze communications with AI
   * @param {Array<number>} communicationIds - Array of communication IDs
   * @returns {Promise<Object>} Bulk analysis result
   */
  async bulkAnalyzeWithAI(communicationIds) {
    try {
      const response = await axios.post(apiService.getUrl('/ai/bulk-analyze/'), {
        communication_ids: communicationIds
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to bulk analyze communications');
    }
  }

  /**
   * Get AI analysis statistics
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} AI stats
   */
  async getAIStats(params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/ai/stats/'), { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch AI statistics');
    }
  }

  /**
   * Get high priority communications from AI analysis
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} High priority communications
   */
  async getHighPriorityCommunications(params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/ai/high-priority/'), { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch high priority communications');
    }
  }

  /**
   * Trigger automatic AI analysis
   * @returns {Promise<Object>} Auto analysis result
   */
  async triggerAutoAnalysis() {
    try {
      const response = await axios.post(apiService.getUrl('/ai/auto-analyze/'));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to trigger auto analysis');
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  /**
   * Get active email accounts only
   * @returns {Promise<Object>} Active email accounts
   */
  async getActiveEmailAccounts() {
    try {
      const accounts = await this.getEmailAccounts();
      return {
        ...accounts,
        results: accounts.results?.filter(account => account.is_active) || []
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch active email accounts');
    }
  }

  /**
   * Check if any email accounts are configured
   * @returns {Promise<boolean>} True if accounts exist
   */
  async hasEmailAccounts() {
    try {
      const accounts = await this.getEmailAccounts();
      return (accounts.count || 0) > 0;
    } catch (error) {
      // If error fetching, assume no accounts
      return false;
    }
  }

  /**
   * Get email account by provider
   * @param {string} provider - Provider name (gmail, outlook)
   * @returns {Promise<Object|null>} Email account or null
   */
  async getEmailAccountByProvider(provider) {
    try {
      const accounts = await this.getEmailAccounts();
      const account = accounts.results?.find(acc => acc.provider === provider);
      return account || null;
    } catch (error) {
      throw this.handleError(error, 'Failed to find email account by provider');
    }
  }

  /**
   * Handle API errors consistently
   * @param {Error} error - The error object
   * @param {string} defaultMessage - Default error message
   * @returns {Error} Formatted error
   */
  handleError(error, defaultMessage) {
    const message = error.response?.data?.error || 
                   error.response?.data?.message || 
                   error.message || 
                   defaultMessage;
    
    const errorObj = new Error(message);
    errorObj.status = error.response?.status;
    errorObj.data = error.response?.data;
    
    return errorObj;
  }
}

// Export singleton instance
export const emailService = new EmailService();
export default emailService;