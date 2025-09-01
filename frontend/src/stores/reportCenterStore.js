import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

export const useReportCenterStore = defineStore('reportCenter', {
  state: () => ({
    // Templates
    templates: [],
    templateLoading: false,
    templateError: null,
    
    // Reports
    reports: [],
    reportLoading: false,
    reportError: null,
    
    // Generation status
    generationTasks: {},
    pollingIntervals: {},
    
    // Current selections
    selectedTemplate: null,
    selectedReport: null,
    
    // UI state
    showTemplateGallery: false,
    showReportBuilder: false,
    showPreviewModal: false,
    
    // Analytics
    templateAnalytics: [],
    reportGenerations: [],
    
    // Bulk Export
    bulkExportJobs: [],
    bulkExportLoading: false,
    
    // Pagination
    templatesPagination: {
      page: 1,
      pageSize: 12,
      total: 0,
      hasNext: false,
      hasPrevious: false
    },
    reportsPagination: {
      page: 1,
      pageSize: 10,
      total: 0,
      hasNext: false,
      hasPrevious: false
    }
  }),
  
  persist: {
    paths: ['selectedTemplate', 'selectedReport']
  },
  
  getters: {
    isAuthenticated: () => {
      const authStore = useAuthStore();
      return authStore.isAuthenticated;
    },
    
    publicTemplates: (state) => {
      return state.templates.filter(template => template.is_public);
    },
    
    myTemplates: (state) => {
      const authStore = useAuthStore();
      return state.templates.filter(template => template.created_by === authStore.user?.id);
    },
    
    recentReports: (state) => {
      return state.reports
        .filter(report => report.status === 'completed')
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);
    },
    
    pendingReports: (state) => {
      return state.reports.filter(report => report.status === 'generating');
    },
    
    failedReports: (state) => {
      return state.reports.filter(report => report.status === 'failed');
    },
    
    templatesByType: (state) => {
      const grouped = {};
      state.templates.forEach(template => {
        const type = template.template_type || 'other';
        if (!grouped[type]) grouped[type] = [];
        grouped[type].push(template);
      });
      return grouped;
    }
  },
  
  actions: {
    // Template Actions
    async fetchTemplates(params = {}) {
      this.templateLoading = true;
      this.templateError = null;
      
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.get('http://localhost:8000/api/report-center/templates/', {
          headers,
          params: {
            page: this.templatesPagination.page,
            page_size: this.templatesPagination.pageSize,
            ...params
          }
        });
        
        this.templates = response.data.results || response.data;
        
        // Update pagination if response includes pagination data
        if (response.data.count !== undefined) {
          this.templatesPagination.total = response.data.count;
          this.templatesPagination.hasNext = !!response.data.next;
          this.templatesPagination.hasPrevious = !!response.data.previous;
        }
        
        return response.data;
      } catch (error) {
        this.templateError = error.response?.data?.message || 'Failed to fetch templates';
        console.error('Failed to fetch templates:', error);
        throw error;
      } finally {
        this.templateLoading = false;
      }
    },
    
    async createTemplate(templateData) {
      this.templateLoading = true;
      
      try {
        const response = await axios.post('/api/report-center/templates/', templateData);
        this.templates.unshift(response.data);
        return response.data;
      } catch (error) {
        this.templateError = error.response?.data?.message || 'Failed to create template';
        console.error('Failed to create template:', error);
        throw error;
      } finally {
        this.templateLoading = false;
      }
    },
    
    async updateTemplate(templateId, templateData) {
      this.templateLoading = true;
      
      try {
        const response = await axios.put(`/api/report-center/templates/${templateId}/`, templateData);
        const index = this.templates.findIndex(t => t.id === templateId);
        if (index !== -1) {
          this.templates[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.templateError = error.response?.data?.message || 'Failed to update template';
        console.error('Failed to update template:', error);
        throw error;
      } finally {
        this.templateLoading = false;
      }
    },
    
    async deleteTemplate(templateId) {
      try {
        await axios.delete(`/api/report-center/templates/${templateId}/`);
        this.templates = this.templates.filter(t => t.id !== templateId);
      } catch (error) {
        this.templateError = error.response?.data?.message || 'Failed to delete template';
        console.error('Failed to delete template:', error);
        throw error;
      }
    },
    
    async duplicateTemplate(templateId) {
      try {
        const response = await axios.post(`/api/report-center/templates/${templateId}/duplicate/`);
        this.templates.unshift(response.data);
        return response.data;
      } catch (error) {
        this.templateError = error.response?.data?.message || 'Failed to duplicate template';
        console.error('Failed to duplicate template:', error);
        throw error;
      }
    },
    
    // Report Actions
    async fetchReports(params = {}) {
      this.reportLoading = true;
      this.reportError = null;
      
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.get('http://localhost:8000/api/report-center/reports/', {
          headers,
          params: {
            page: this.reportsPagination.page,
            page_size: this.reportsPagination.pageSize,
            ...params
          }
        });
        
        this.reports = response.data.results || response.data;
        
        // Update pagination if response includes pagination data
        if (response.data.count !== undefined) {
          this.reportsPagination.total = response.data.count;
          this.reportsPagination.hasNext = !!response.data.next;
          this.reportsPagination.hasPrevious = !!response.data.previous;
        }
        
        return response.data;
      } catch (error) {
        this.reportError = error.response?.data?.message || 'Failed to fetch reports';
        console.error('Failed to fetch reports:', error);
        throw error;
      } finally {
        this.reportLoading = false;
      }
    },
    
    async createReport(reportData) {
      this.reportLoading = true;
      
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.post('http://localhost:8000/api/report-center/reports/', reportData, { headers });
        this.reports.unshift(response.data);
        return response.data;
      } catch (error) {
        this.reportError = error.response?.data?.message || 'Failed to create report';
        console.error('Failed to create report:', error);
        throw error;
      } finally {
        this.reportLoading = false;
      }
    },
    
    async updateReport(reportId, reportData) {
      try {
        const response = await axios.put(`/api/report-center/reports/${reportId}/`, reportData);
        const index = this.reports.findIndex(r => r.id === reportId);
        if (index !== -1) {
          this.reports[index] = response.data;
        }
        return response.data;
      } catch (error) {
        this.reportError = error.response?.data?.message || 'Failed to update report';
        console.error('Failed to update report:', error);
        throw error;
      }
    },
    
    async deleteReport(reportId) {
      try {
        await axios.delete(`/api/report-center/reports/${reportId}/`);
        this.reports = this.reports.filter(r => r.id !== reportId);
      } catch (error) {
        this.reportError = error.response?.data?.message || 'Failed to delete report';
        console.error('Failed to delete report:', error);
        throw error;
      }
    },
    
    async generateReport(reportId, format = 'pdf') {
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        
        // Find the report in our local store to get the necessary data
        const report = this.reports.find(r => r.id === reportId);
        if (!report) {
          throw new Error('Report not found in local store');
        }
        
        const response = await axios.post(`http://localhost:8000/api/report-center/reports/${reportId}/generate/`, {
          format,
          client_id: report.client_id,
          scenario_ids: report.scenario_ids || [],
          template_id: report.template_id,
          name: report.name
        }, { headers });
        
        // Track generation task
        this.generationTasks[reportId] = {
          task_id: response.data.task_id,
          format: response.data.format,
          started_at: new Date().toISOString(),
          status: 'generating'
        };
        
        // Update report status
        const reportIndex = this.reports.findIndex(r => r.id === reportId);
        if (reportIndex !== -1) {
          this.reports[reportIndex].status = 'generating';
          this.reports[reportIndex].generation_started_at = new Date().toISOString();
        }
        
        // Start polling for completion
        this.startStatusPolling(reportId);
        
        return response.data;
      } catch (error) {
        this.reportError = error.response?.data?.message || 'Failed to generate report';
        console.error('Failed to generate report:', error);
        throw error;
      }
    },
    
    async checkReportStatus(reportId) {
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.get(`http://localhost:8000/api/report-center/reports/${reportId}/status/`, { headers });
        
        // Update local report data
        const reportIndex = this.reports.findIndex(r => r.id === reportId);
        if (reportIndex !== -1) {
          Object.assign(this.reports[reportIndex], response.data);
        }
        
        // Update generation task status
        if (this.generationTasks[reportId]) {
          this.generationTasks[reportId].status = response.data.status;
          
          // Clean up completed/failed tasks
          if (['completed', 'failed'].includes(response.data.status)) {
            setTimeout(() => {
              delete this.generationTasks[reportId];
            }, 5000); // Clean up after 5 seconds
          }
        }
        
        return response.data;
      } catch (error) {
        console.error('Failed to check report status:', error);
        throw error;
      }
    },
    
    async batchGenerateReports(reportIds, format = 'pdf') {
      try {
        const response = await axios.post('/api/report-center/reports/batch_generate/', {
          report_ids: reportIds,
          format
        });
        
        // Track all generation tasks
        reportIds.forEach(reportId => {
          this.generationTasks[reportId] = {
            task_id: response.data.task_id,
            format: response.data.format,
            started_at: new Date().toISOString(),
            status: 'generating'
          };
        });
        
        return response.data;
      } catch (error) {
        this.reportError = error.response?.data?.message || 'Failed to generate reports';
        console.error('Failed to generate reports:', error);
        throw error;
      }
    },
    
    // Analytics Actions
    async fetchTemplateAnalytics() {
      try {
        const response = await axios.get('/api/report-center/analytics/');
        this.templateAnalytics = response.data.results || response.data;
        return response.data;
      } catch (error) {
        console.error('Failed to fetch template analytics:', error);
        throw error;
      }
    },
    
    async fetchReportGenerations(reportId = null) {
      try {
        const params = reportId ? { report: reportId } : {};
        const response = await axios.get('/api/report-center/generations/', { params });
        this.reportGenerations = response.data.results || response.data;
        return response.data;
      } catch (error) {
        console.error('Failed to fetch report generations:', error);
        throw error;
      }
    },
    
    // Status Polling
    startStatusPolling(reportId) {
      // Clear any existing polling for this report
      if (this.pollingIntervals && this.pollingIntervals[reportId]) {
        clearInterval(this.pollingIntervals[reportId]);
      }
      
      // Initialize polling intervals object if needed
      if (!this.pollingIntervals) {
        this.pollingIntervals = {};
      }
      
      // Poll every 2 seconds
      this.pollingIntervals[reportId] = setInterval(async () => {
        try {
          const status = await this.checkReportStatus(reportId);
          console.log(`Polling report ${reportId} status:`, status.status);
          
          // Stop polling if completed or failed
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(this.pollingIntervals[reportId]);
            delete this.pollingIntervals[reportId];
          }
        } catch (error) {
          console.error(`Error polling report ${reportId} status:`, error);
          // Stop polling on persistent errors
          clearInterval(this.pollingIntervals[reportId]);
          delete this.pollingIntervals[reportId];
        }
      }, 2000);
      
      // Safety timeout - stop polling after 2 minutes
      setTimeout(() => {
        if (this.pollingIntervals && this.pollingIntervals[reportId]) {
          clearInterval(this.pollingIntervals[reportId]);
          delete this.pollingIntervals[reportId];
        }
      }, 120000);
    },
    
    stopStatusPolling(reportId) {
      if (this.pollingIntervals && this.pollingIntervals[reportId]) {
        clearInterval(this.pollingIntervals[reportId]);
        delete this.pollingIntervals[reportId];
      }
    },

    // Download report file
    async downloadReport(reportId, format = 'pdf') {
      try {
        console.log(`Downloading report ${reportId} in ${format} format`);
        
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        
        const response = await axios.get(`http://localhost:8000/api/report-center/reports/${reportId}/download/?format=${format}`, {
          headers,
          responseType: 'blob' // Important for file downloads
        });

        // Get the filename from the Content-Disposition header
        const contentDisposition = response.headers['content-disposition'];
        let filename = `report_${reportId}.${format}`;
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="([^"]*)"/);
          if (match) {
            filename = match[1];
          }
        }

        // Create blob and download
        const blob = new Blob([response.data]);
        const url = window.URL.createObjectURL(blob);

        // Create temporary link and click it
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();

        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);

        console.log('Download completed successfully');
        return { success: true };
      } catch (error) {
        console.error('Download failed:', error);
        throw error;
      }
    },
    
    // UI State Actions
    selectTemplate(template) {
      this.selectedTemplate = template;
    },
    
    selectReport(report) {
      this.selectedReport = report;
    },
    
    showTemplateGalleryModal() {
      this.showTemplateGallery = true;
    },
    
    hideTemplateGalleryModal() {
      this.showTemplateGallery = false;
    },
    
    showReportBuilderModal() {
      this.showReportBuilder = true;
    },
    
    hideReportBuilderModal() {
      this.showReportBuilder = false;
    },
    
    showPreviewModalAction() {
      this.showPreviewModal = true;
    },
    
    hidePreviewModalAction() {
      this.showPreviewModal = false;
    },
    
    // Pagination Actions
    setTemplatesPage(page) {
      this.templatesPagination.page = page;
      this.fetchTemplates();
    },
    
    setReportsPage(page) {
      this.reportsPagination.page = page;
      this.fetchReports();
    },
    
    // Utility Actions
    clearErrors() {
      this.templateError = null;
      this.reportError = null;
    },
    
    refreshData() {
      return Promise.all([
        this.fetchTemplates(),
        this.fetchReports()
      ]);
    },
    
    // Bulk Export Actions
    async initiateBulkExport(exportConfig) {
      this.bulkExportLoading = true;
      
      try {
        const response = await axios.post('/api/report-center/bulk-export/initiate/', exportConfig);
        await this.fetchBulkExportJobs(); // Refresh jobs list
        return response.data;
      } catch (error) {
        console.error('Failed to initiate bulk export:', error);
        throw error;
      } finally {
        this.bulkExportLoading = false;
      }
    },
    
    async fetchBulkExportJobs(params = {}) {
      this.bulkExportLoading = true;
      
      try {
        const response = await axios.get('/api/report-center/bulk-export/jobs/', { params });
        this.bulkExportJobs = response.data.jobs || [];
        return response.data;
      } catch (error) {
        console.error('Failed to fetch bulk export jobs:', error);
        throw error;
      } finally {
        this.bulkExportLoading = false;
      }
    },
    
    async getBulkExportStatus(jobId) {
      try {
        const response = await axios.get(`/api/report-center/bulk-export/${jobId}/status/`);
        
        // Update job in local state
        const jobIndex = this.bulkExportJobs.findIndex(job => job.id === jobId);
        if (jobIndex !== -1) {
          this.bulkExportJobs[jobIndex] = { ...this.bulkExportJobs[jobIndex], ...response.data };
        }
        
        return response.data;
      } catch (error) {
        console.error('Failed to get bulk export status:', error);
        throw error;
      }
    },
    
    async cancelBulkExport(jobId) {
      try {
        const response = await axios.post(`/api/report-center/bulk-export/${jobId}/cancel/`);
        await this.fetchBulkExportJobs(); // Refresh jobs list
        return response.data;
      } catch (error) {
        console.error('Failed to cancel bulk export:', error);
        throw error;
      }
    },
    
    async downloadBulkExport(jobId) {
      try {
        const response = await axios.get(`/api/report-center/bulk-export/${jobId}/download/`);
        return response.data;
      } catch (error) {
        console.error('Failed to download bulk export:', error);
        throw error;
      }
    },
    
    async deleteBulkExport(jobId) {
      try {
        await axios.delete(`/api/report-center/bulk-export/${jobId}/`);
        this.bulkExportJobs = this.bulkExportJobs.filter(job => job.id !== jobId);
      } catch (error) {
        console.error('Failed to delete bulk export:', error);
        throw error;
      }
    },
    
    // =========================================================================
    // AI-POWERED CONTENT GENERATION ACTIONS
    // =========================================================================
    
    async generateExecutiveSummary(payload) {
      try {
        const response = await axios.post('/api/report-center/ai/executive-summary/', payload);
        return response.data;
      } catch (error) {
        console.error('Failed to generate executive summary:', error);
        throw error;
      }
    },
    
    async generateSlideRecommendations(payload) {
      try {
        const response = await axios.post('/api/report-center/ai/slide-recommendations/', payload);
        return response.data;
      } catch (error) {
        console.error('Failed to generate slide recommendations:', error);
        throw error;
      }
    },
    
    async generateSectionContent(payload) {
      try {
        const response = await axios.post('/api/report-center/ai/content-suggestions/', payload);
        return response.data;
      } catch (error) {
        console.error('Failed to generate section content:', error);
        throw error;
      }
    },
    
    async generateClientInsights(payload) {
      try {
        const response = await axios.post('/api/report-center/ai/client-insights/', payload);
        return response.data;
      } catch (error) {
        console.error('Failed to generate client insights:', error);
        throw error;
      }
    },
    
    async getAIUsageAnalytics(params = {}) {
      try {
        const response = await axios.get('/api/report-center/ai/usage-analytics/', { params });
        return response.data;
      } catch (error) {
        console.error('Failed to get AI usage analytics:', error);
        throw error;
      }
    }
  }
});