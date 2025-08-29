import { defineStore } from 'pinia';
import { communicationService } from '@/services/communicationService.js';
import { useAuthStore } from './auth.js';

export const useCommunicationStore = defineStore('communication', {
  state: () => ({
    // Communications data
    communications: [],
    currentCommunication: null,
    
    // Pagination
    totalCount: 0,
    currentPage: 1,
    pageSize: 20,
    hasNext: false,
    hasPrevious: false,
    
    // Filtering and search
    filters: {
      search: '',
      type: '',
      direction: '',
      sentiment: '',
      client_id: null,
      lead_id: null,
      is_read: null,
      priority_min: null,
      priority_max: null,
      date_from: null,
      date_to: null,
      email_account_id: null,
      ordering: '-created_at'
    },
    
    // Analytics data
    analytics: {
      period_days: 30,
      total_communications: 0,
      unread_count: 0,
      read_percentage: 0,
      by_type: [],
      by_direction: [],
      sentiment_stats: [],
      ai_averages: {},
      high_priority_count: 0,
      daily_counts: []
    },
    
    // Loading states
    loading: {
      communications: false,
      analytics: false,
      bulkOperation: false,
      creating: false,
      updating: false,
      deleting: false
    },
    
    // Error handling
    error: null,
    
    // Selection for bulk operations
    selectedCommunications: [],
    
    // Real-time updates
    lastSyncTime: null,
    autoRefreshInterval: null,
    pollingEnabled: false
  }),
  
  persist: {
    paths: ['filters', 'pageSize', 'selectedCommunications']
  },
  
  getters: {
    // Communication getters
    unreadCommunications: (state) => state.communications.filter(comm => !comm.is_read),
    unreadCount: (state) => state.communications.filter(comm => !comm.is_read).length,
    
    // Filter getters
    hasActiveFilters: (state) => {
      return Object.entries(state.filters).some(([key, value]) => {
        if (key === 'ordering') return false; // Ordering is not considered a filter
        return value !== '' && value !== null && value !== undefined;
      });
    },
    
    activeFilterCount: (state) => {
      return Object.entries(state.filters).filter(([key, value]) => {
        if (key === 'ordering') return false;
        return value !== '' && value !== null && value !== undefined;
      }).length;
    },
    
    // Selection getters
    hasSelectedCommunications: (state) => state.selectedCommunications.length > 0,
    selectedCount: (state) => state.selectedCommunications.length,
    allSelected: (state) => {
      if (state.communications.length === 0) return false;
      return state.communications.every(comm => 
        state.selectedCommunications.includes(comm.id)
      );
    },
    
    // Analytics getters
    highPriorityPercentage: (state) => {
      const total = state.analytics.total_communications;
      if (total === 0) return 0;
      return Math.round((state.analytics.high_priority_count / total) * 100);
    },
    
    // Communication type getters
    communicationsByType: (state) => {
      return state.communications.reduce((acc, comm) => {
        acc[comm.communication_type] = (acc[comm.communication_type] || 0) + 1;
        return acc;
      }, {});
    },
    
    // Sentiment getters
    communicationsBySentiment: (state) => {
      return state.communications.reduce((acc, comm) => {
        if (comm.ai_sentiment_label) {
          acc[comm.ai_sentiment_label] = (acc[comm.ai_sentiment_label] || 0) + 1;
        }
        return acc;
      }, {});
    },
    
    // Loading getters
    isLoading: (state) => Object.values(state.loading).some(loading => loading),
    
    // Pagination getters
    totalPages: (state) => Math.ceil(state.totalCount / state.pageSize),
    
    // Communication status
    communicationById: (state) => (id) => {
      return state.communications.find(comm => comm.id === id);
    }
  },
  
  actions: {
    // =============================================================================
    // COMMUNICATION CRUD OPERATIONS
    // =============================================================================
    
    async fetchCommunications(resetPagination = false) {
      this.loading.communications = true;
      this.error = null;
      
      try {
        if (resetPagination) {
          this.currentPage = 1;
        }
        
        const params = {
          ...this.filters,
          page: this.currentPage,
          page_size: this.pageSize
        };
        
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key];
          }
        });
        
        const response = await communicationService.getCommunications(params);
        
        this.communications = response.results || [];
        this.totalCount = response.count || 0;
        this.hasNext = !!response.next;
        this.hasPrevious = !!response.previous;
        this.lastSyncTime = new Date().toISOString();
        
        return response;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.communications = false;
      }
    },
    
    async fetchCommunication(id) {
      this.loading.communications = true;
      this.error = null;
      
      try {
        const communication = await communicationService.getCommunication(id);
        this.currentCommunication = communication;
        
        // Update in list if exists
        const index = this.communications.findIndex(c => c.id === id);
        if (index !== -1) {
          this.communications[index] = communication;
        }
        
        return communication;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.communications = false;
      }
    },
    
    async createCommunication(data) {
      this.loading.creating = true;
      this.error = null;
      
      try {
        const communication = await communicationService.createCommunication(data);
        
        // Add to beginning of list
        this.communications.unshift(communication);
        this.totalCount++;
        
        return communication;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.creating = false;
      }
    },
    
    async updateCommunication(id, data) {
      this.loading.updating = true;
      this.error = null;
      
      try {
        const communication = await communicationService.updateCommunication(id, data);
        
        // Update in list
        const index = this.communications.findIndex(c => c.id === id);
        if (index !== -1) {
          this.communications[index] = communication;
        }
        
        // Update current if it's the same
        if (this.currentCommunication && this.currentCommunication.id === id) {
          this.currentCommunication = communication;
        }
        
        return communication;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.updating = false;
      }
    },
    
    async deleteCommunication(id) {
      this.loading.deleting = true;
      this.error = null;
      
      try {
        await communicationService.deleteCommunication(id);
        
        // Remove from list
        this.communications = this.communications.filter(c => c.id !== id);
        this.totalCount--;
        
        // Clear current if it's the same
        if (this.currentCommunication && this.currentCommunication.id === id) {
          this.currentCommunication = null;
        }
        
        // Remove from selection
        this.selectedCommunications = this.selectedCommunications.filter(selectedId => selectedId !== id);
        
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.deleting = false;
      }
    },
    
    // =============================================================================
    // BULK OPERATIONS
    // =============================================================================
    
    async bulkMarkRead(ids = null) {
      const targetIds = ids || this.selectedCommunications;
      if (targetIds.length === 0) return;
      
      this.loading.bulkOperation = true;
      this.error = null;
      
      try {
        const result = await communicationService.bulkMarkRead(targetIds);
        
        // Update local state
        this.communications.forEach(comm => {
          if (targetIds.includes(comm.id)) {
            comm.is_read = true;
            comm.read_at = new Date().toISOString();
          }
        });
        
        // Clear selection if using selected communications
        if (!ids) {
          this.selectedCommunications = [];
        }
        
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.bulkOperation = false;
      }
    },
    
    async bulkMarkUnread(ids = null) {
      const targetIds = ids || this.selectedCommunications;
      if (targetIds.length === 0) return;
      
      this.loading.bulkOperation = true;
      this.error = null;
      
      try {
        const result = await communicationService.bulkMarkUnread(targetIds);
        
        // Update local state
        this.communications.forEach(comm => {
          if (targetIds.includes(comm.id)) {
            comm.is_read = false;
            comm.read_at = null;
          }
        });
        
        // Clear selection if using selected communications
        if (!ids) {
          this.selectedCommunications = [];
        }
        
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.bulkOperation = false;
      }
    },
    
    async bulkDelete(ids = null) {
      const targetIds = ids || this.selectedCommunications;
      if (targetIds.length === 0) return;
      
      this.loading.bulkOperation = true;
      this.error = null;
      
      try {
        const result = await communicationService.bulkDelete(targetIds);
        
        // Remove from local state
        this.communications = this.communications.filter(comm => !targetIds.includes(comm.id));
        this.totalCount -= targetIds.length;
        
        // Clear selection
        this.selectedCommunications = [];
        
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.bulkOperation = false;
      }
    },
    
    // =============================================================================
    // SEARCH AND FILTERING
    // =============================================================================
    
    async searchCommunications(query) {
      this.filters.search = query;
      return this.fetchCommunications(true);
    },
    
    setFilter(key, value) {
      this.filters[key] = value;
    },
    
    updateFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters };
    },
    
    clearFilters() {
      this.filters = {
        search: '',
        type: '',
        direction: '',
        sentiment: '',
        client_id: null,
        lead_id: null,
        is_read: null,
        priority_min: null,
        priority_max: null,
        date_from: null,
        date_to: null,
        email_account_id: null,
        ordering: '-created_at'
      };
    },
    
    async applyFilters() {
      return this.fetchCommunications(true);
    },
    
    // =============================================================================
    // ANALYTICS
    // =============================================================================
    
    async fetchAnalytics(params = {}) {
      this.loading.analytics = true;
      this.error = null;
      
      try {
        const analytics = await communicationService.getAnalytics(params);
        this.analytics = analytics;
        return analytics;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.analytics = false;
      }
    },
    
    // =============================================================================
    // SELECTION MANAGEMENT
    // =============================================================================
    
    selectCommunication(id) {
      if (!this.selectedCommunications.includes(id)) {
        this.selectedCommunications.push(id);
      }
    },
    
    deselectCommunication(id) {
      this.selectedCommunications = this.selectedCommunications.filter(selectedId => selectedId !== id);
    },
    
    toggleCommunicationSelection(id) {
      if (this.selectedCommunications.includes(id)) {
        this.deselectCommunication(id);
      } else {
        this.selectCommunication(id);
      }
    },
    
    selectAllCommunications() {
      this.selectedCommunications = this.communications.map(comm => comm.id);
    },
    
    deselectAllCommunications() {
      this.selectedCommunications = [];
    },
    
    toggleSelectAll() {
      if (this.allSelected) {
        this.deselectAllCommunications();
      } else {
        this.selectAllCommunications();
      }
    },
    
    // =============================================================================
    // PAGINATION
    // =============================================================================
    
    async nextPage() {
      if (this.hasNext) {
        this.currentPage++;
        return this.fetchCommunications();
      }
    },
    
    async previousPage() {
      if (this.hasPrevious) {
        this.currentPage--;
        return this.fetchCommunications();
      }
    },
    
    async goToPage(page) {
      this.currentPage = page;
      return this.fetchCommunications();
    },
    
    setPageSize(size) {
      this.pageSize = size;
      this.currentPage = 1;
    },
    
    // =============================================================================
    // REAL-TIME UPDATES
    // =============================================================================
    
    startPolling(intervalMs = 30000) { // Default 30 seconds
      if (this.autoRefreshInterval) {
        this.stopPolling();
      }
      
      this.pollingEnabled = true;
      this.autoRefreshInterval = setInterval(() => {
        if (this.pollingEnabled && !this.loading.communications) {
          this.fetchCommunications();
        }
      }, intervalMs);
    },
    
    stopPolling() {
      if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval);
        this.autoRefreshInterval = null;
      }
      this.pollingEnabled = false;
    },
    
    async refreshCommunications() {
      return this.fetchCommunications();
    },
    
    // =============================================================================
    // UTILITY METHODS
    // =============================================================================
    
    async markAsRead(id) {
      const communication = this.communicationById(id);
      if (communication && !communication.is_read) {
        return this.bulkMarkRead([id]);
      }
    },
    
    async markAsUnread(id) {
      const communication = this.communicationById(id);
      if (communication && communication.is_read) {
        return this.bulkMarkUnread([id]);
      }
    },
    
    getUnreadCountByType(type) {
      return this.communications.filter(comm => 
        comm.communication_type === type && !comm.is_read
      ).length;
    },
    
    getUnreadCountBySentiment(sentiment) {
      return this.communications.filter(comm => 
        comm.ai_sentiment_label === sentiment && !comm.is_read
      ).length;
    },
    
    clearError() {
      this.error = null;
    },
    
    reset() {
      this.communications = [];
      this.currentCommunication = null;
      this.totalCount = 0;
      this.currentPage = 1;
      this.hasNext = false;
      this.hasPrevious = false;
      this.selectedCommunications = [];
      this.error = null;
      this.clearFilters();
      this.stopPolling();
    }
  }
});