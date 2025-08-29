/**
 * Document Management Store
 * 
 * Pinia store for managing document state, uploads, downloads, and all document operations.
 * Integrates with the backend document management API with full FINRA compliance support.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { documentService } from '@/services/documentService.js'

export const useDocumentStore = defineStore('document', () => {
  // =============================================================================
  // STATE
  // =============================================================================
  
  const documents = ref([])
  const categories = ref([])
  const templates = ref([])
  const retentionPolicies = ref([])
  const currentDocument = ref(null)
  const documentVersions = ref([])
  const auditLogs = ref([])
  
  // UI State
  const loading = ref(false)
  const uploading = ref(false)
  const uploadProgress = ref({})
  const error = ref(null)
  const selectedDocuments = ref([])
  
  // Filters and Search
  const filters = ref({
    search: '',
    category: null,
    client: null,
    status: 'active',
    dateRange: { start: null, end: null },
    fileType: null,
    complianceType: null,
    containsPII: null
  })
  
  // Pagination
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  })
  
  // Document Statistics
  const statistics = ref({
    totalDocuments: 0,
    totalSizeMB: 0,
    recentUploads30d: 0,
    statusBreakdown: {},
    categoryBreakdown: {},
    clientBreakdown: [],
    complianceSummary: {}
  })

  // =============================================================================
  // COMPUTED
  // =============================================================================
  
  const filteredDocuments = computed(() => {
    let filtered = documents.value
    
    // Search filter
    if (filters.value.search) {
      const searchTerm = filters.value.search.toLowerCase()
      filtered = filtered.filter(doc => 
        doc.title?.toLowerCase().includes(searchTerm) ||
        doc.original_filename?.toLowerCase().includes(searchTerm) ||
        doc.description?.toLowerCase().includes(searchTerm) ||
        doc.client_name?.toLowerCase().includes(searchTerm) ||
        (doc.tags && doc.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
      )
    }
    
    // Category filter
    if (filters.value.category) {
      filtered = filtered.filter(doc => doc.category === filters.value.category)
    }
    
    // Client filter
    if (filters.value.client) {
      filtered = filtered.filter(doc => doc.client === filters.value.client)
    }
    
    // Status filter
    if (filters.value.status && filters.value.status !== 'all') {
      filtered = filtered.filter(doc => doc.status === filters.value.status)
    }
    
    // File type filter
    if (filters.value.fileType) {
      filtered = filtered.filter(doc => doc.content_type === filters.value.fileType)
    }
    
    // Compliance type filter
    if (filters.value.complianceType) {
      filtered = filtered.filter(doc => doc.compliance_type === filters.value.complianceType)
    }
    
    // PII filter
    if (filters.value.containsPII !== null) {
      filtered = filtered.filter(doc => doc.contains_pii === filters.value.containsPII)
    }
    
    // Date range filter
    if (filters.value.dateRange.start && filters.value.dateRange.end) {
      const startDate = new Date(filters.value.dateRange.start)
      const endDate = new Date(filters.value.dateRange.end)
      filtered = filtered.filter(doc => {
        const docDate = new Date(doc.uploaded_at)
        return docDate >= startDate && docDate <= endDate
      })
    }
    
    return filtered
  })
  
  const selectedDocumentsCount = computed(() => selectedDocuments.value.length)
  
  const hasSelection = computed(() => selectedDocuments.value.length > 0)
  
  const categoriesMap = computed(() => {
    const map = new Map()
    categories.value.forEach(cat => map.set(cat.id, cat))
    return map
  })
  
  const documentsByCategory = computed(() => {
    const grouped = {}
    documents.value.forEach(doc => {
      const categoryName = doc.category_name || 'Uncategorized'
      if (!grouped[categoryName]) {
        grouped[categoryName] = []
      }
      grouped[categoryName].push(doc)
    })
    return grouped
  })
  
  const recentDocuments = computed(() => {
    return documents.value
      .slice()
      .sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at))
      .slice(0, 10)
  })

  // =============================================================================
  // ACTIONS - DOCUMENTS
  // =============================================================================
  
  async function fetchDocuments(params = {}) {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = {
        page: pagination.value.page,
        limit: pagination.value.limit,
        ...filters.value,
        ...params
      }
      
      // Clean up null/undefined values
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === null || queryParams[key] === undefined || queryParams[key] === '') {
          delete queryParams[key]
        }
      })
      
      const response = await documentService.getDocuments(queryParams)
      
      documents.value = response.results || response
      pagination.value = {
        page: response.page || 1,
        limit: response.limit || 20,
        total: response.count || documents.value.length,
        totalPages: Math.ceil((response.count || documents.value.length) / (response.limit || 20))
      }
      
      return response
    } catch (err) {
      console.error('Error fetching documents:', err)
      error.value = err.response?.data?.message || 'Failed to load documents'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function getDocument(documentId) {
    loading.value = true
    error.value = null
    
    try {
      const response = await documentService.getDocument(documentId)
      currentDocument.value = response
      return response
    } catch (err) {
      console.error('Error fetching document:', err)
      error.value = err.response?.data?.message || 'Failed to load document'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function uploadDocument(fileData, progressCallback = null) {
    uploading.value = true
    error.value = null
    
    try {
      const formData = new FormData()
      formData.append('file', fileData.file)
      
      // Add metadata
      if (fileData.title) formData.append('title', fileData.title)
      if (fileData.description) formData.append('description', fileData.description)
      if (fileData.category_id) formData.append('category_id', fileData.category_id)
      if (fileData.client_id) formData.append('client_id', fileData.client_id)
      if (fileData.tags) formData.append('tags', fileData.tags.join(','))
      if (fileData.compliance_type) formData.append('compliance_type', fileData.compliance_type)
      if (fileData.contains_pii !== undefined) formData.append('contains_pii', fileData.contains_pii)
      if (fileData.contains_phi !== undefined) formData.append('contains_phi', fileData.contains_phi)
      if (fileData.is_client_visible !== undefined) formData.append('is_client_visible', fileData.is_client_visible)
      
      const response = await documentService.uploadDocument(formData, progressCallback)
      
      // Add to documents list
      documents.value.unshift(response)
      
      // Update statistics
      await fetchStatistics()
      
      return response
    } catch (err) {
      console.error('Error uploading document:', err)
      error.value = err.response?.data?.message || 'Failed to upload document'
      throw err
    } finally {
      uploading.value = false
    }
  }
  
  async function bulkUpload(files, commonData = {}, progressCallback = null) {
    uploading.value = true
    error.value = null
    
    try {
      const formData = new FormData()
      
      // Add all files
      files.forEach(file => {
        formData.append('files', file)
      })
      
      // Add common metadata
      if (commonData.category_id) formData.append('category_id', commonData.category_id)
      if (commonData.client_id) formData.append('client_id', commonData.client_id)
      
      const response = await documentService.bulkUpload(formData, progressCallback)
      
      // Add successful uploads to documents list
      const successful = response.results.filter(r => r.success)
      successful.forEach(result => {
        if (result.document) {
          documents.value.unshift(result.document)
        }
      })
      
      // Update statistics
      await fetchStatistics()
      
      return response
    } catch (err) {
      console.error('Error in bulk upload:', err)
      error.value = err.response?.data?.message || 'Failed to upload documents'
      throw err
    } finally {
      uploading.value = false
    }
  }
  
  async function downloadDocument(documentId, filename = null) {
    try {
      const response = await documentService.downloadDocument(documentId)
      
      if (response.download_url) {
        // Create temporary link to trigger download
        const link = document.createElement('a')
        link.href = response.download_url
        link.download = filename || response.filename || 'download'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Update access count in local state
        const docIndex = documents.value.findIndex(d => d.id === documentId)
        if (docIndex !== -1) {
          documents.value[docIndex].access_count += 1
          documents.value[docIndex].last_accessed = new Date().toISOString()
        }
      }
      
      return response
    } catch (err) {
      console.error('Error downloading document:', err)
      error.value = err.response?.data?.message || 'Failed to download document'
      throw err
    }
  }
  
  async function shareDocument(documentId, shareData) {
    try {
      const response = await documentService.shareDocument(documentId, shareData)
      return response
    } catch (err) {
      console.error('Error sharing document:', err)
      error.value = err.response?.data?.message || 'Failed to share document'
      throw err
    }
  }
  
  async function updateDocument(documentId, updateData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await documentService.updateDocument(documentId, updateData)
      
      // Update in local state
      const index = documents.value.findIndex(d => d.id === documentId)
      if (index !== -1) {
        documents.value[index] = { ...documents.value[index], ...response }
      }
      
      if (currentDocument.value && currentDocument.value.id === documentId) {
        currentDocument.value = { ...currentDocument.value, ...response }
      }
      
      return response
    } catch (err) {
      console.error('Error updating document:', err)
      error.value = err.response?.data?.message || 'Failed to update document'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function archiveDocument(documentId) {
    try {
      await documentService.archiveDocument(documentId)
      
      // Update status in local state
      const index = documents.value.findIndex(d => d.id === documentId)
      if (index !== -1) {
        documents.value[index].status = 'archived'
        documents.value[index].archived_at = new Date().toISOString()
      }
      
      return true
    } catch (err) {
      console.error('Error archiving document:', err)
      error.value = err.response?.data?.message || 'Failed to archive document'
      throw err
    }
  }
  
  async function deleteDocument(documentId) {
    try {
      await documentService.deleteDocument(documentId)
      
      // Remove from local state
      const index = documents.value.findIndex(d => d.id === documentId)
      if (index !== -1) {
        documents.value.splice(index, 1)
      }
      
      // Clear current document if it was deleted
      if (currentDocument.value && currentDocument.value.id === documentId) {
        currentDocument.value = null
      }
      
      // Update statistics
      await fetchStatistics()
      
      return true
    } catch (err) {
      console.error('Error deleting document:', err)
      error.value = err.response?.data?.message || 'Failed to delete document'
      throw err
    }
  }

  async function toggleDocumentSharing(documentId, isClientVisible) {
    try {
      const response = await documentService.toggleDocumentSharing(documentId, { is_client_visible: isClientVisible })
      
      // Update local state
      const index = documents.value.findIndex(d => d.id === documentId)
      if (index !== -1) {
        documents.value[index].is_client_visible = response.is_client_visible
      }
      
      // Update current document if it's the one being updated
      if (currentDocument.value && currentDocument.value.id === documentId) {
        currentDocument.value.is_client_visible = response.is_client_visible
      }
      
      return response
    } catch (err) {
      console.error('Error toggling document sharing:', err)
      error.value = err.response?.data?.message || 'Failed to update document sharing'
      throw err
    }
  }
  
  // =============================================================================
  // ACTIONS - CATEGORIES
  // =============================================================================
  
  async function fetchCategories() {
    try {
      const response = await documentService.getCategories()
      categories.value = response.results || response
      return response
    } catch (err) {
      console.error('Error fetching categories:', err)
      throw err
    }
  }
  
  async function createCategory(categoryData) {
    try {
      const response = await documentService.createCategory(categoryData)
      categories.value.push(response)
      return response
    } catch (err) {
      console.error('Error creating category:', err)
      error.value = err.response?.data?.message || 'Failed to create category'
      throw err
    }
  }
  
  async function updateCategory(categoryId, updateData) {
    try {
      const response = await documentService.updateCategory(categoryId, updateData)
      
      const index = categories.value.findIndex(c => c.id === categoryId)
      if (index !== -1) {
        categories.value[index] = { ...categories.value[index], ...response }
      }
      
      return response
    } catch (err) {
      console.error('Error updating category:', err)
      error.value = err.response?.data?.message || 'Failed to update category'
      throw err
    }
  }
  
  async function deleteCategory(categoryId) {
    try {
      await documentService.deleteCategory(categoryId)
      
      const index = categories.value.findIndex(c => c.id === categoryId)
      if (index !== -1) {
        categories.value.splice(index, 1)
      }
      
      return true
    } catch (err) {
      console.error('Error deleting category:', err)
      error.value = err.response?.data?.message || 'Failed to delete category'
      throw err
    }
  }
  
  // =============================================================================
  // ACTIONS - STATISTICS & ANALYTICS
  // =============================================================================
  
  async function fetchStatistics() {
    try {
      const response = await documentService.getStatistics()
      statistics.value = response
      return response
    } catch (err) {
      console.error('Error fetching statistics:', err)
      throw err
    }
  }
  
  // =============================================================================
  // ACTIONS - SEARCH & FILTERING
  // =============================================================================
  
  async function searchDocuments(query, additionalFilters = {}) {
    loading.value = true
    error.value = null
    
    try {
      const searchParams = {
        q: query,
        ...filters.value,
        ...additionalFilters
      }
      
      const response = await documentService.searchDocuments(searchParams)
      documents.value = response.documents || response.results || response
      
      return response
    } catch (err) {
      console.error('Error searching documents:', err)
      error.value = err.response?.data?.message || 'Search failed'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  function updateFilters(newFilters) {
    filters.value = { ...filters.value, ...newFilters }
  }
  
  function clearFilters() {
    filters.value = {
      search: '',
      category: null,
      client: null,
      status: 'active',
      dateRange: { start: null, end: null },
      fileType: null,
      complianceType: null,
      containsPII: null
    }
  }
  
  // =============================================================================
  // ACTIONS - BULK OPERATIONS
  // =============================================================================
  
  async function bulkAction(action, documentIds, actionData = {}) {
    loading.value = true
    error.value = null
    
    try {
      const response = await documentService.bulkAction({
        action,
        document_ids: documentIds,
        ...actionData
      })
      
      // Update local state based on action
      if (action === 'archive') {
        documentIds.forEach(id => {
          const index = documents.value.findIndex(d => d.id === id)
          if (index !== -1) {
            documents.value[index].status = 'archived'
            documents.value[index].archived_at = new Date().toISOString()
          }
        })
      } else if (action === 'delete') {
        documentIds.forEach(id => {
          const index = documents.value.findIndex(d => d.id === id)
          if (index !== -1) {
            documents.value.splice(index, 1)
          }
        })
      }
      
      // Clear selection
      selectedDocuments.value = []
      
      // Update statistics
      await fetchStatistics()
      
      return response
    } catch (err) {
      console.error('Error in bulk action:', err)
      error.value = err.response?.data?.message || 'Bulk action failed'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // =============================================================================
  // ACTIONS - SELECTION
  // =============================================================================
  
  function selectDocument(documentId) {
    if (!selectedDocuments.value.includes(documentId)) {
      selectedDocuments.value.push(documentId)
    }
  }
  
  function deselectDocument(documentId) {
    const index = selectedDocuments.value.indexOf(documentId)
    if (index > -1) {
      selectedDocuments.value.splice(index, 1)
    }
  }
  
  function toggleDocumentSelection(documentId) {
    if (selectedDocuments.value.includes(documentId)) {
      deselectDocument(documentId)
    } else {
      selectDocument(documentId)
    }
  }
  
  function selectAllVisible() {
    selectedDocuments.value = filteredDocuments.value.map(doc => doc.id)
  }
  
  function clearSelection() {
    selectedDocuments.value = []
  }
  
  // =============================================================================
  // ACTIONS - PAGINATION
  // =============================================================================
  
  function setPage(page) {
    pagination.value.page = page
    fetchDocuments()
  }
  
  function nextPage() {
    if (pagination.value.page < pagination.value.totalPages) {
      setPage(pagination.value.page + 1)
    }
  }
  
  function previousPage() {
    if (pagination.value.page > 1) {
      setPage(pagination.value.page - 1)
    }
  }
  
  // =============================================================================
  // ACTIONS - UTILITIES
  // =============================================================================
  
  function formatFileSize(bytes) {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  
  function getFileIcon(contentType) {
    if (!contentType) return 'bi-file'
    
    const iconMap = {
      'application/pdf': 'bi-file-pdf',
      'application/msword': 'bi-file-word',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'bi-file-word',
      'application/vnd.ms-excel': 'bi-file-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'bi-file-excel',
      'text/plain': 'bi-file-text',
      'text/csv': 'bi-file-spreadsheet',
      'image/jpeg': 'bi-file-image',
      'image/png': 'bi-file-image',
      'image/tiff': 'bi-file-image'
    }
    
    return iconMap[contentType] || 'bi-file'
  }
  
  function clearError() {
    error.value = null
  }
  
  function reset() {
    documents.value = []
    categories.value = []
    templates.value = []
    retentionPolicies.value = []
    currentDocument.value = null
    documentVersions.value = []
    auditLogs.value = []
    selectedDocuments.value = []
    clearFilters()
    clearError()
    pagination.value = {
      page: 1,
      limit: 20,
      total: 0,
      totalPages: 0
    }
  }

  // =============================================================================
  // INITIALIZATION
  // =============================================================================
  
  async function getClientDocuments(clientId) {
    loading.value = true
    error.value = null
    
    try {
      const response = await documentService.getClientDocuments(clientId)
      return response
    } catch (err) {
      console.error('Error fetching client documents:', err)
      error.value = err.response?.data?.message || 'Failed to load client documents'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Auto-fetch categories on store initialization
  fetchCategories()
  
  return {
    // State
    documents,
    categories,
    templates,
    retentionPolicies,
    currentDocument,
    documentVersions,
    auditLogs,
    loading,
    uploading,
    uploadProgress,
    error,
    selectedDocuments,
    filters,
    pagination,
    statistics,
    
    // Computed
    filteredDocuments,
    selectedDocumentsCount,
    hasSelection,
    categoriesMap,
    documentsByCategory,
    recentDocuments,
    
    // Actions
    fetchDocuments,
    getClientDocuments,
    getDocument,
    uploadDocument,
    bulkUpload,
    downloadDocument,
    shareDocument,
    updateDocument,
    archiveDocument,
    deleteDocument,
    toggleDocumentSharing,
    
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    
    fetchStatistics,
    
    searchDocuments,
    updateFilters,
    clearFilters,
    
    bulkAction,
    
    selectDocument,
    deselectDocument,
    toggleDocumentSelection,
    selectAllVisible,
    clearSelection,
    
    setPage,
    nextPage,
    previousPage,
    
    formatFileSize,
    getFileIcon,
    clearError,
    reset
  }
})