import axios from 'axios';
import { apiService } from './api.js';

/**
 * Communication Service for handling all communication-related API calls
 */
class CommunicationService {
  constructor() {
    this.baseUrl = '/api/communications';
  }

  /**
   * Get all communications with filtering and search
   * @param {Object} params - Query parameters for filtering
   * @returns {Promise<Object>} Response with communications list
   */
  async getCommunications(params = {}) {
    try {
      const response = await axios.get(apiService.getUrl(this.baseUrl), {
        params: {
          ...params,
          // Add default ordering
          ordering: params.ordering || '-created_at'
        }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch communications');
    }
  }

  /**
   * Get a specific communication by ID
   * @param {number} id - Communication ID
   * @returns {Promise<Object>} Communication details
   */
  async getCommunication(id) {
    try {
      const response = await axios.get(apiService.getUrl(`${this.baseUrl}/${id}/`));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch communication');
    }
  }

  /**
   * Create a new communication
   * @param {Object} data - Communication data
   * @returns {Promise<Object>} Created communication
   */
  async createCommunication(data) {
    try {
      const response = await axios.post(apiService.getUrl(this.baseUrl), data);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to create communication');
    }
  }

  /**
   * Update a communication
   * @param {number} id - Communication ID
   * @param {Object} data - Updated communication data
   * @returns {Promise<Object>} Updated communication
   */
  async updateCommunication(id, data) {
    try {
      const response = await axios.put(apiService.getUrl(`${this.baseUrl}/${id}/`), data);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to update communication');
    }
  }

  /**
   * Delete a communication
   * @param {number} id - Communication ID
   * @returns {Promise<void>}
   */
  async deleteCommunication(id) {
    try {
      await axios.delete(apiService.getUrl(`${this.baseUrl}/${id}/`));
    } catch (error) {
      throw this.handleError(error, 'Failed to delete communication');
    }
  }

  /**
   * Mark multiple communications as read
   * @param {Array<number>} ids - Array of communication IDs
   * @returns {Promise<Object>} Bulk operation result
   */
  async bulkMarkRead(ids) {
    try {
      const response = await axios.post(apiService.getUrl(`${this.baseUrl}/bulk_mark_read/`), {
        ids
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to mark communications as read');
    }
  }

  /**
   * Mark multiple communications as unread
   * @param {Array<number>} ids - Array of communication IDs
   * @returns {Promise<Object>} Bulk operation result
   */
  async bulkMarkUnread(ids) {
    try {
      const response = await axios.post(apiService.getUrl(`${this.baseUrl}/bulk_mark_unread/`), {
        ids
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to mark communications as unread');
    }
  }

  /**
   * Delete multiple communications
   * @param {Array<number>} ids - Array of communication IDs
   * @returns {Promise<Object>} Bulk operation result
   */
  async bulkDelete(ids) {
    try {
      const response = await axios.delete(apiService.getUrl(`${this.baseUrl}/bulk_delete/`), {
        data: { ids }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to delete communications');
    }
  }

  /**
   * Trigger email sync for all email accounts
   * @returns {Promise<Object>} Sync operation result
   */
  async syncEmails() {
    try {
      const response = await axios.post(apiService.getUrl(`${this.baseUrl}/sync_emails/`));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to trigger email sync');
    }
  }

  /**
   * Get email sync status for all accounts
   * @returns {Promise<Object>} Sync status data
   */
  async getSyncStatus() {
    try {
      const response = await axios.get(apiService.getUrl(`${this.baseUrl}/sync_status/`));
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to get sync status');
    }
  }

  /**
   * Get communication analytics
   * @param {Object} params - Analytics parameters (days, etc.)
   * @returns {Promise<Object>} Analytics data
   */
  async getAnalytics(params = {}) {
    try {
      const response = await axios.get(apiService.getUrl(`${this.baseUrl}/analytics/`), {
        params: {
          days: 30, // Default to 30 days
          ...params
        }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to fetch analytics');
    }
  }

  /**
   * Search communications
   * @param {string} query - Search query
   * @param {Object} filters - Additional filters
   * @returns {Promise<Object>} Search results
   */
  async searchCommunications(query, filters = {}) {
    return this.getCommunications({
      search: query,
      ...filters
    });
  }

  /**
   * Get communications by client ID
   * @param {number} clientId - Client ID
   * @param {Object} additionalParams - Additional query parameters
   * @returns {Promise<Object>} Client communications
   */
  async getCommunicationsByClient(clientId, additionalParams = {}) {
    return this.getCommunications({
      client_id: clientId,
      ...additionalParams
    });
  }

  /**
   * Get communications by lead ID
   * @param {number} leadId - Lead ID
   * @param {Object} additionalParams - Additional query parameters
   * @returns {Promise<Object>} Lead communications
   */
  async getCommunicationsByLead(leadId, additionalParams = {}) {
    return this.getCommunications({
      lead_id: leadId,
      ...additionalParams
    });
  }

  /**
   * Get unread communications
   * @param {Object} additionalParams - Additional query parameters
   * @returns {Promise<Object>} Unread communications
   */
  async getUnreadCommunications(additionalParams = {}) {
    return this.getCommunications({
      is_read: false,
      ...additionalParams
    });
  }

  /**
   * Get communications by sentiment
   * @param {string} sentiment - Sentiment label (positive, negative, neutral, mixed)
   * @param {Object} additionalParams - Additional query parameters
   * @returns {Promise<Object>} Communications by sentiment
   */
  async getCommunicationsBySentiment(sentiment, additionalParams = {}) {
    return this.getCommunications({
      sentiment,
      ...additionalParams
    });
  }

  /**
   * Get high priority communications
   * @param {number} minPriority - Minimum priority score (default 0.7)
   * @param {Object} additionalParams - Additional query parameters
   * @returns {Promise<Object>} High priority communications
   */
  async getHighPriorityCommunications(minPriority = 0.7, additionalParams = {}) {
    return this.getCommunications({
      priority_min: minPriority,
      ...additionalParams
    });
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
export const communicationService = new CommunicationService();
export default communicationService;