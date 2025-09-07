/**
 * Document Service
 * 
 * API service for document management operations.
 * Handles all communication with the document management backend endpoints.
 */

import axios from 'axios'
import { apiService } from './api.js'

class DocumentService {
  
  /**
   * Get axios config with authentication headers
   */
  getAuthConfig() {
    const token = localStorage.getItem('token')
    return {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    }
  }
  
  // =============================================================================
  // DOCUMENT OPERATIONS
  // =============================================================================
  
  /**
   * Get all documents with optional filtering and pagination
   */
  async getDocuments(params = {}) {
    try {
      const config = this.getAuthConfig()
      config.params = params
      const response = await axios.get(apiService.getUrl('/api/documents/'), config)
      return response.data
    } catch (error) {
      console.error('Error fetching documents:', error)
      throw error
    }
  }
  
  /**
   * Get a specific document by ID
   */
  async getDocument(documentId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/documents/${documentId}/`), this.getAuthConfig())
      return response.data
    } catch (error) {
      console.error('Error fetching document:', error)
      throw error
    }
  }
  
  /**
   * Upload a single document
   */
  async uploadDocument(formData, progressCallback = null) {
    try {
      const token = localStorage.getItem('token')
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      }
      
      // Add progress callback if provided
      if (progressCallback) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          progressCallback(percentCompleted)
        }
      }
      
      const response = await axios.post(apiService.getUrl('/api/documents/upload/'), formData, config)
      return response.data
    } catch (error) {
      console.error('Error uploading document:', error)
      throw error
    }
  }
  
  /**
   * Upload multiple documents at once
   */
  async bulkUpload(formData, progressCallback = null) {
    try {
      const token = localStorage.getItem('token')
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      }
      
      if (progressCallback) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          progressCallback(percentCompleted)
        }
      }
      
      const response = await axios.post(apiService.getUrl('/api/documents/bulk-upload/'), formData, config)
      return response.data
    } catch (error) {
      console.error('Error in bulk upload:', error)
      throw error
    }
  }
  
  /**
   * Update document metadata
   */
  async updateDocument(documentId, updateData) {
    try {
      const response = await axios.patch(apiService.getUrl(`/api/documents/${documentId}/`), updateData, this.getAuthConfig())
      return response.data
    } catch (error) {
      console.error('Error updating document:', error)
      throw error
    }
  }
  
  /**
   * Download a document (returns pre-signed URL)
   */
  async downloadDocument(documentId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/documents/${documentId}/download/`), this.getAuthConfig())
      return response.data
    } catch (error) {
      console.error('Error downloading document:', error)
      throw error
    }
  }
  
  /**
   * Share a document with specified permissions
   */
  async shareDocument(documentId, shareData) {
    try {
      const response = await axios.post(apiService.getUrl(`/api/documents/${documentId}/share/`), shareData)
      return response.data
    } catch (error) {
      console.error('Error sharing document:', error)
      throw error
    }
  }
  
  /**
   * Archive a document (soft delete)
   */
  async archiveDocument(documentId) {
    try {
      const response = await axios.delete(apiService.getUrl(`/api/documents/${documentId}/archive/`))
      return response.data
    } catch (error) {
      console.error('Error archiving document:', error)
      throw error
    }
  }
  
  /**
   * Permanently delete a document
   */
  async deleteDocument(documentId) {
    try {
      const response = await axios.delete(apiService.getUrl(`/api/documents/${documentId}/`), this.getAuthConfig())
      return response.data
    } catch (error) {
      console.error('Error deleting document:', error)
      throw error
    }
  }

  /**
   * Toggle document sharing with client
   */
  async toggleDocumentSharing(documentId, data) {
    try {
      const response = await axios.patch(
        apiService.getUrl(`/api/documents/${documentId}/toggle-sharing/`), 
        data,
        apiService.getConfig()
      )
      return response.data
    } catch (error) {
      console.error('Error toggling document sharing:', error)
      throw error
    }
  }
  
  /**
   * Get document version history
   */
  async getDocumentVersions(documentId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/documents/${documentId}/versions/`))
      return response.data
    } catch (error) {
      console.error('Error fetching document versions:', error)
      throw error
    }
  }
  
  /**
   * Get document audit trail
   */
  async getDocumentAuditTrail(documentId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/documents/${documentId}/audit-trail/`))
      return response.data
    } catch (error) {
      console.error('Error fetching audit trail:', error)
      throw error
    }
  }
  
  // =============================================================================
  // CATEGORY OPERATIONS
  // =============================================================================
  
  /**
   * Get all document categories
   */
  async getCategories() {
    try {
      const response = await axios.get(apiService.getUrl('/api/document-categories/'), this.getAuthConfig())
      return response.data
    } catch (error) {
      console.error('Error fetching categories:', error)
      throw error
    }
  }
  
  /**
   * Get a specific category
   */
  async getCategory(categoryId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/document-categories/${categoryId}/`))
      return response.data
    } catch (error) {
      console.error('Error fetching category:', error)
      throw error
    }
  }
  
  /**
   * Create a new document category
   */
  async createCategory(categoryData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/document-categories/'), categoryData)
      return response.data
    } catch (error) {
      console.error('Error creating category:', error)
      throw error
    }
  }
  
  /**
   * Update a document category
   */
  async updateCategory(categoryId, updateData) {
    try {
      const response = await axios.patch(apiService.getUrl(`/api/document-categories/${categoryId}/`), updateData)
      return response.data
    } catch (error) {
      console.error('Error updating category:', error)
      throw error
    }
  }
  
  /**
   * Delete a document category
   */
  async deleteCategory(categoryId) {
    try {
      const response = await axios.delete(apiService.getUrl(`/api/document-categories/${categoryId}/`))
      return response.data
    } catch (error) {
      console.error('Error deleting category:', error)
      throw error
    }
  }
  
  // =============================================================================
  // TEMPLATE OPERATIONS
  // =============================================================================
  
  /**
   * Get all document templates
   */
  async getTemplates() {
    try {
      const response = await axios.get(apiService.getUrl('/api/document-templates/'))
      return response.data
    } catch (error) {
      console.error('Error fetching templates:', error)
      throw error
    }
  }
  
  /**
   * Get a specific template
   */
  async getTemplate(templateId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/document-templates/${templateId}/`))
      return response.data
    } catch (error) {
      console.error('Error fetching template:', error)
      throw error
    }
  }
  
  /**
   * Create a new document template
   */
  async createTemplate(templateData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/document-templates/'), templateData)
      return response.data
    } catch (error) {
      console.error('Error creating template:', error)
      throw error
    }
  }
  
  /**
   * Update a document template
   */
  async updateTemplate(templateId, updateData) {
    try {
      const response = await axios.patch(apiService.getUrl(`/api/document-templates/${templateId}/`), updateData)
      return response.data
    } catch (error) {
      console.error('Error updating template:', error)
      throw error
    }
  }
  
  /**
   * Delete a document template
   */
  async deleteTemplate(templateId) {
    try {
      const response = await axios.delete(apiService.getUrl(`/api/document-templates/${templateId}/`))
      return response.data
    } catch (error) {
      console.error('Error deleting template:', error)
      throw error
    }
  }
  
  // =============================================================================
  // RETENTION POLICY OPERATIONS
  // =============================================================================
  
  /**
   * Get all retention policies
   */
  async getRetentionPolicies() {
    try {
      const response = await axios.get(apiService.getUrl('/api/document-retention-policies/'))
      return response.data
    } catch (error) {
      console.error('Error fetching retention policies:', error)
      throw error
    }
  }
  
  /**
   * Get a specific retention policy
   */
  async getRetentionPolicy(policyId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/document-retention-policies/${policyId}/`))
      return response.data
    } catch (error) {
      console.error('Error fetching retention policy:', error)
      throw error
    }
  }
  
  /**
   * Create a new retention policy
   */
  async createRetentionPolicy(policyData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/document-retention-policies/'), policyData)
      return response.data
    } catch (error) {
      console.error('Error creating retention policy:', error)
      throw error
    }
  }
  
  /**
   * Update a retention policy
   */
  async updateRetentionPolicy(policyId, updateData) {
    try {
      const response = await axios.patch(apiService.getUrl(`/api/document-retention-policies/${policyId}/`), updateData)
      return response.data
    } catch (error) {
      console.error('Error updating retention policy:', error)
      throw error
    }
  }
  
  /**
   * Delete a retention policy
   */
  async deleteRetentionPolicy(policyId) {
    try {
      const response = await axios.delete(apiService.getUrl(`/api/document-retention-policies/${policyId}/`))
      return response.data
    } catch (error) {
      console.error('Error deleting retention policy:', error)
      throw error
    }
  }
  
  // =============================================================================
  // SEARCH AND ANALYTICS
  // =============================================================================
  
  /**
   * Search documents with advanced filters
   */
  async searchDocuments(searchParams) {
    try {
      const response = await axios.get(apiService.getUrl('/api/documents/search/'), { 
        params: searchParams 
      })
      return response.data
    } catch (error) {
      console.error('Error searching documents:', error)
      throw error
    }
  }
  
  /**
   * Get document statistics and analytics
   */
  async getStatistics() {
    try {
      const response = await axios.get(apiService.getUrl('/api/documents/stats/'))
      return response.data
    } catch (error) {
      console.error('Error fetching statistics:', error)
      throw error
    }
  }
  
  /**
   * Get document analytics
   */
  async getAnalytics(params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/documents/analytics/'), { params })
      return response.data
    } catch (error) {
      console.error('Error fetching analytics:', error)
      throw error
    }
  }
  
  // =============================================================================
  // BULK OPERATIONS
  // =============================================================================
  
  /**
   * Perform bulk action on multiple documents
   */
  async bulkAction(actionData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/documents/bulk-action/'), actionData)
      return response.data
    } catch (error) {
      console.error('Error in bulk action:', error)
      throw error
    }
  }
  
  // =============================================================================
  // CLIENT-SPECIFIC OPERATIONS
  // =============================================================================
  
  /**
   * Get documents for a specific client
   */
  async getClientDocuments(clientId, params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/documents/'), { 
        params: { client_id: clientId, ...params } 
      })
      return response.data
    } catch (error) {
      console.error('Error fetching client documents:', error)
      throw error
    }
  }
  
  /**
   * Get documents by category
   */
  async getDocumentsByCategory(categoryId, params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/documents/'), { 
        params: { category_id: categoryId, ...params } 
      })
      return response.data
    } catch (error) {
      console.error('Error fetching documents by category:', error)
      throw error
    }
  }
  
  // =============================================================================
  // UTILITY METHODS
  // =============================================================================
  
  /**
   * Check if file type is allowed
   */
  isFileTypeAllowed(file) {
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/plain',
      'text/csv',
      'image/jpeg',
      'image/png',
      'image/tiff'
    ]
    
    return allowedTypes.includes(file.type)
  }
  
  /**
   * Validate file size
   */
  validateFileSize(file, maxSizeMB = 50) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024
    return file.size <= maxSizeBytes
  }
  
  /**
   * Get file extension from filename
   */
  getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase()
  }
  
  /**
   * Format file size for display
   */
  formatFileSize(bytes) {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  
  /**
   * Get file icon class based on content type
   */
  getFileIcon(contentType) {
    const iconMap = {
      'application/pdf': 'bi-file-pdf-fill text-danger',
      'application/msword': 'bi-file-word-fill text-primary',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'bi-file-word-fill text-primary',
      'application/vnd.ms-excel': 'bi-file-excel-fill text-success',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'bi-file-excel-fill text-success',
      'text/plain': 'bi-file-text-fill text-secondary',
      'text/csv': 'bi-file-spreadsheet-fill text-info',
      'image/jpeg': 'bi-file-image-fill text-warning',
      'image/png': 'bi-file-image-fill text-warning',
      'image/tiff': 'bi-file-image-fill text-warning'
    }
    
    return iconMap[contentType] || 'bi-file-fill text-muted'
  }
  
  /**
   * Get compliance type display name
   */
  getComplianceTypeDisplay(complianceType) {
    const displayMap = {
      'finra_3110': 'FINRA Rule 3110 - Books & Records',
      'finra_4511': 'FINRA Rule 4511 - Customer Account Info',
      'sec_17a4': 'SEC Rule 17a-4 - Record Retention',
      'ria_204': 'RIA Rule 204-2 - Investment Adviser Records',
      'privacy_reg_sp': 'Regulation S-P - Privacy',
      'none': 'No Specific Requirement'
    }
    
    return displayMap[complianceType] || complianceType
  }
  
  /**
   * Get status badge class
   */
  getStatusBadgeClass(status) {
    const classMap = {
      'processing': 'badge bg-warning',
      'active': 'badge bg-success',
      'archived': 'badge bg-secondary',
      'quarantined': 'badge bg-danger',
      'deleted': 'badge bg-dark'
    }
    
    return classMap[status] || 'badge bg-secondary'
  }
  
  /**
   * Generate unique upload ID for tracking
   */
  generateUploadId() {
    return 'upload_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }
}

export const documentService = new DocumentService()