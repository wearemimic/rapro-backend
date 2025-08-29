import { defineStore } from 'pinia';
import { emailService } from '@/services/emailService.js';
import { communicationService } from '@/services/communicationService.js';
import { useCommunicationStore } from './communicationStore.js';

export const useEmailStore = defineStore('email', {
  state: () => ({
    // Email accounts data
    emailAccounts: [],
    currentEmailAccount: null,
    
    // Sync status
    syncStatus: {
      accounts: [],
      total_accounts: 0,
      active_accounts: 0,
      last_updated: null
    },
    
    // Sync operations
    currentSyncTasks: [],
    syncHistory: [],
    
    // OAuth settings
    oAuthStatus: {
      gmail_configured: false,
      outlook_configured: false,
      last_checked: null
    },
    
    // AI analysis
    aiStats: {
      total_analyzed: 0,
      pending_analysis: 0,
      avg_sentiment_score: 0,
      high_priority_count: 0,
      last_updated: null
    },
    
    // Loading states
    loading: {
      emailAccounts: false,
      syncStatus: false,
      syncing: false,
      oAuth: false,
      aiAnalysis: false,
      sending: false
    },
    
    // Error handling
    error: null,
    syncError: null,
    
    // Email composition
    draftEmail: {
      to: [],
      cc: [],
      bcc: [],
      subject: '',
      content: '',
      html_content: '',
      client_id: null,
      lead_id: null,
      email_account_id: null
    },
    
    // Real-time sync monitoring
    syncPollingInterval: null,
    syncPollingEnabled: false
  }),
  
  persist: {
    paths: ['draftEmail', 'syncHistory']
  },
  
  getters: {
    // Email account getters
    hasEmailAccounts: (state) => state.emailAccounts.length > 0,
    activeEmailAccounts: (state) => state.emailAccounts.filter(account => account.is_active),
    gmailAccounts: (state) => state.emailAccounts.filter(account => account.provider === 'gmail'),
    outlookAccounts: (state) => state.emailAccounts.filter(account => account.provider === 'outlook'),
    
    // Sync status getters
    accountsNeedingSync: (state) => {
      const now = new Date();
      const thirtyMinutesAgo = new Date(now.getTime() - 30 * 60 * 1000);
      
      return state.syncStatus.accounts.filter(account => 
        !account.last_sync_at || new Date(account.last_sync_at) < thirtyMinutesAgo
      );
    },
    
    isSyncInProgress: (state) => state.currentSyncTasks.length > 0,
    
    lastSyncTime: (state) => {
      if (state.syncStatus.accounts.length === 0) return null;
      
      const lastSyncTimes = state.syncStatus.accounts
        .filter(acc => acc.last_sync_at)
        .map(acc => new Date(acc.last_sync_at))
        .sort((a, b) => b - a);
      
      return lastSyncTimes.length > 0 ? lastSyncTimes[0] : null;
    },
    
    // OAuth getters
    isOAuthConfigured: (state) => state.oAuthStatus.gmail_configured || state.oAuthStatus.outlook_configured,
    
    // Loading getters
    isLoading: (state) => Object.values(state.loading).some(loading => loading),
    
    // Email account by ID
    emailAccountById: (state) => (id) => {
      return state.emailAccounts.find(account => account.id === id);
    },
    
    // Draft email validation
    isDraftValid: (state) => {
      return state.draftEmail.to.length > 0 && 
             state.draftEmail.subject.trim() !== '' && 
             state.draftEmail.content.trim() !== '';
    }
  },
  
  actions: {
    // =============================================================================
    // EMAIL ACCOUNT MANAGEMENT
    // =============================================================================
    
    async fetchEmailAccounts() {
      this.loading.emailAccounts = true;
      this.error = null;
      
      try {
        const response = await emailService.getEmailAccounts();
        this.emailAccounts = response.results || response || [];
        return response;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.emailAccounts = false;
      }
    },
    
    async fetchEmailAccount(id) {
      this.loading.emailAccounts = true;
      this.error = null;
      
      try {
        const account = await emailService.getEmailAccount(id);
        this.currentEmailAccount = account;
        
        // Update in list if exists
        const index = this.emailAccounts.findIndex(acc => acc.id === id);
        if (index !== -1) {
          this.emailAccounts[index] = account;
        }
        
        return account;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.emailAccounts = false;
      }
    },
    
    async createEmailAccount(data) {
      this.loading.emailAccounts = true;
      this.error = null;
      
      try {
        const account = await emailService.createEmailAccount(data);
        this.emailAccounts.push(account);
        return account;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.emailAccounts = false;
      }
    },
    
    async updateEmailAccount(id, data) {
      this.loading.emailAccounts = true;
      this.error = null;
      
      try {
        const account = await emailService.updateEmailAccount(id, data);
        
        // Update in list
        const index = this.emailAccounts.findIndex(acc => acc.id === id);
        if (index !== -1) {
          this.emailAccounts[index] = account;
        }
        
        // Update current if it's the same
        if (this.currentEmailAccount && this.currentEmailAccount.id === id) {
          this.currentEmailAccount = account;
        }
        
        return account;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.emailAccounts = false;
      }
    },
    
    async deleteEmailAccount(id) {
      this.loading.emailAccounts = true;
      this.error = null;
      
      try {
        await emailService.deleteEmailAccount(id);
        
        // Remove from list
        this.emailAccounts = this.emailAccounts.filter(acc => acc.id !== id);
        
        // Clear current if it's the same
        if (this.currentEmailAccount && this.currentEmailAccount.id === id) {
          this.currentEmailAccount = null;
        }
        
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.emailAccounts = false;
      }
    },
    
    // =============================================================================
    // EMAIL SYNC OPERATIONS
    // =============================================================================
    
    async syncEmails() {
      this.loading.syncing = true;
      this.syncError = null;
      
      try {
        const result = await communicationService.syncEmails();
        
        // Track sync tasks
        if (result.task_ids) {
          this.currentSyncTasks = result.task_ids.map(taskId => ({
            id: taskId,
            started_at: new Date().toISOString(),
            status: 'pending'
          }));
        }
        
        // Add to sync history
        this.syncHistory.unshift({
          timestamp: new Date().toISOString(),
          type: 'manual',
          account_count: result.account_count,
          task_ids: result.task_ids,
          status: 'started'
        });
        
        // Start monitoring sync status
        this.startSyncPolling();
        
        return result;
      } catch (error) {
        this.syncError = error.message;
        throw error;
      } finally {
        this.loading.syncing = false;
      }
    },
    
    async syncAllEmails() {
      this.loading.syncing = true;
      this.syncError = null;
      
      try {
        const result = await emailService.syncAllEmails();
        
        // Add to sync history
        this.syncHistory.unshift({
          timestamp: new Date().toISOString(),
          type: 'full_sync',
          status: 'completed',
          ...result
        });
        
        return result;
      } catch (error) {
        this.syncError = error.message;
        throw error;
      } finally {
        this.loading.syncing = false;
      }
    },
    
    async fetchSyncStatus() {
      this.loading.syncStatus = true;
      this.error = null;
      
      try {
        const status = await communicationService.getSyncStatus();
        this.syncStatus = {
          ...status,
          last_updated: new Date().toISOString()
        };
        return status;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.syncStatus = false;
      }
    },
    
    // =============================================================================
    // OAUTH MANAGEMENT
    // =============================================================================
    
    async getGmailAuthUrl() {
      this.loading.oAuth = true;
      this.error = null;
      
      try {
        const result = await emailService.getGmailAuthUrl();
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.oAuth = false;
      }
    },
    
    async getOutlookAuthUrl() {
      this.loading.oAuth = true;
      this.error = null;
      
      try {
        const result = await emailService.getOutlookAuthUrl();
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.oAuth = false;
      }
    },
    
    async fetchOAuthStatus() {
      this.loading.oAuth = true;
      this.error = null;
      
      try {
        const status = await emailService.getOAuthStatus();
        this.oAuthStatus = {
          ...status,
          last_checked: new Date().toISOString()
        };
        return status;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.oAuth = false;
      }
    },
    
    // =============================================================================
    // EMAIL COMPOSITION AND SENDING
    // =============================================================================
    
    resetDraftEmail() {
      this.draftEmail = {
        to: [],
        cc: [],
        bcc: [],
        subject: '',
        content: '',
        html_content: '',
        client_id: null,
        lead_id: null,
        email_account_id: null
      };
    },
    
    updateDraftEmail(updates) {
      this.draftEmail = { ...this.draftEmail, ...updates };
    },
    
    addRecipient(email, type = 'to') {
      if (!this.draftEmail[type].includes(email)) {
        this.draftEmail[type].push(email);
      }
    },
    
    removeRecipient(email, type = 'to') {
      this.draftEmail[type] = this.draftEmail[type].filter(recipient => recipient !== email);
    },
    
    async sendEmail(emailData = null) {
      this.loading.sending = true;
      this.error = null;
      
      try {
        const dataToSend = emailData || this.draftEmail;
        const result = await emailService.sendEmail(dataToSend);
        
        // Reset draft if sending the current draft
        if (!emailData) {
          this.resetDraftEmail();
        }
        
        // Refresh communications to show sent email
        const communicationStore = useCommunicationStore();
        communicationStore.refreshCommunications();
        
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.sending = false;
      }
    },
    
    // =============================================================================
    // AI OPERATIONS
    // =============================================================================
    
    async analyzeWithAI(communicationId) {
      this.loading.aiAnalysis = true;
      this.error = null;
      
      try {
        const result = await emailService.analyzeWithAI(communicationId);
        
        // Update AI stats after analysis
        this.fetchAIStats();
        
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.aiAnalysis = false;
      }
    },
    
    async bulkAnalyzeWithAI(communicationIds) {
      this.loading.aiAnalysis = true;
      this.error = null;
      
      try {
        const result = await emailService.bulkAnalyzeWithAI(communicationIds);
        
        // Update AI stats after analysis
        this.fetchAIStats();
        
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.aiAnalysis = false;
      }
    },
    
    async fetchAIStats(params = {}) {
      this.loading.aiAnalysis = true;
      this.error = null;
      
      try {
        const stats = await emailService.getAIStats(params);
        this.aiStats = {
          ...stats,
          last_updated: new Date().toISOString()
        };
        return stats;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.aiAnalysis = false;
      }
    },
    
    async getHighPriorityCommunications(params = {}) {
      this.error = null;
      
      try {
        const result = await emailService.getHighPriorityCommunications(params);
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },
    
    async triggerAutoAnalysis() {
      this.loading.aiAnalysis = true;
      this.error = null;
      
      try {
        const result = await emailService.triggerAutoAnalysis();
        
        // Update AI stats after triggering analysis
        this.fetchAIStats();
        
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.aiAnalysis = false;
      }
    },
    
    // =============================================================================
    // SYNC MONITORING
    // =============================================================================
    
    startSyncPolling(intervalMs = 5000) { // 5 seconds for sync monitoring
      if (this.syncPollingInterval) {
        this.stopSyncPolling();
      }
      
      this.syncPollingEnabled = true;
      this.syncPollingInterval = setInterval(async () => {
        if (this.syncPollingEnabled && this.currentSyncTasks.length > 0) {
          try {
            await this.fetchSyncStatus();
            
            // Check if all sync tasks are complete (simple check)
            if (this.currentSyncTasks.length > 0 && !this.loading.syncing) {
              // After 30 seconds, consider sync tasks complete
              const oldestTask = this.currentSyncTasks[0];
              const taskAge = new Date() - new Date(oldestTask.started_at);
              if (taskAge > 30000) { // 30 seconds
                this.currentSyncTasks = [];
                this.stopSyncPolling();
              }
            }
          } catch (error) {
            console.error('Sync polling error:', error);
          }
        } else if (!this.isSyncInProgress) {
          this.stopSyncPolling();
        }
      }, intervalMs);
    },
    
    stopSyncPolling() {
      if (this.syncPollingInterval) {
        clearInterval(this.syncPollingInterval);
        this.syncPollingInterval = null;
      }
      this.syncPollingEnabled = false;
    },
    
    // =============================================================================
    // UTILITY METHODS
    // =============================================================================
    
    async setupEmailAccount(provider) {
      try {
        let authResult;
        
        if (provider === 'gmail') {
          authResult = await this.getGmailAuthUrl();
        } else if (provider === 'outlook') {
          authResult = await this.getOutlookAuthUrl();
        } else {
          throw new Error('Unsupported provider');
        }
        
        // Open OAuth window
        if (authResult.auth_url) {
          window.open(authResult.auth_url, 'oauth', 'width=600,height=600');
        }
        
        return authResult;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },
    
    async refreshAllData() {
      await Promise.all([
        this.fetchEmailAccounts(),
        this.fetchSyncStatus(),
        this.fetchOAuthStatus(),
        this.fetchAIStats()
      ]);
    },
    
    clearError() {
      this.error = null;
      this.syncError = null;
    },
    
    clearSyncHistory() {
      this.syncHistory = [];
    },
    
    reset() {
      this.emailAccounts = [];
      this.currentEmailAccount = null;
      this.syncStatus = {
        accounts: [],
        total_accounts: 0,
        active_accounts: 0,
        last_updated: null
      };
      this.currentSyncTasks = [];
      this.syncHistory = [];
      this.error = null;
      this.syncError = null;
      this.resetDraftEmail();
      this.stopSyncPolling();
    }
  }
});