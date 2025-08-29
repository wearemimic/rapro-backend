<template>
  <div 
    class="document-center"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
    :class="{ 'drag-over': isDragging }"
  >
    <!-- Drag & Drop Overlay -->
    <div v-if="isDragging" class="drag-overlay">
      <div class="drag-content">
        <i class="bi bi-cloud-upload display-1 text-primary mb-3"></i>
        <h4>Drop files to upload</h4>
        <p class="text-muted">Release to start uploading</p>
      </div>
    </div>

    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1">Document Center</h2>
        <p class="text-muted mb-0">Manage client documents with FINRA compliance</p>
      </div>
      <div class="d-flex gap-2">
        <button 
          class="btn btn-outline-secondary"
          @click="showStatistics = !showStatistics"
          :class="{ active: showStatistics }"
        >
          <i class="bi bi-graph-up me-1"></i>
          Analytics
        </button>
        <button 
          class="btn btn-primary"
          @click="showUploadModal = true"
          type="button"
          title="Open advanced upload with categories and metadata"
        >
          <i class="bi bi-cloud-upload me-1"></i>
          Upload Documents
        </button>
      </div>
    </div>

    <!-- Quick Upload Drop Zone -->
    <div 
      v-if="!showUploadModal"
      class="quick-upload-zone mb-4"
      @drop.prevent="handleQuickDrop"
      @dragover.prevent="isDragOverQuick = true"
      @dragleave.prevent="isDragOverQuick = false"
      :class="{ 'drag-active': isDragOverQuick }"
      @click="showUploadModal = true"
    >
      <i class="bi bi-cloud-upload display-6 mb-2"></i>
      <p class="mb-1 fw-semibold">Drop files here to upload</p>
      <p class="text-muted small mb-0">or click to open upload dialog</p>
      <p class="text-muted small">Supported: PDF, Word, Excel, Images (max 50MB)</p>
    </div>

    <!-- Statistics Cards (Collapsible) -->
    <div v-if="showStatistics" class="row mb-4">
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Total Documents</h6>
                <h4 class="mb-0">{{ documentStore.statistics.totalDocuments }}</h4>
              </div>
              <i class="bi bi-files display-6 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Storage Used</h6>
                <h4 class="mb-0">{{ documentStore.statistics.totalSizeMB }}MB</h4>
              </div>
              <i class="bi bi-hdd display-6 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Recent Uploads</h6>
                <h4 class="mb-0">{{ documentStore.statistics.recentUploads30d }}</h4>
                <small class="opacity-75">Last 30 days</small>
              </div>
              <i class="bi bi-cloud-arrow-up display-6 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card bg-warning text-dark">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Categories</h6>
                <h4 class="mb-0">{{ documentStore.categories.length }}</h4>
              </div>
              <i class="bi bi-folder display-6 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search Bar -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <!-- Search Input -->
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search documents..."
                v-model="searchQuery"
                @input="handleSearch"
              >
              <button 
                v-if="searchQuery"
                class="btn btn-outline-secondary"
                type="button"
                @click="clearSearch"
              >
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>
          
          <!-- Category Filter -->
          <div class="col-md-2">
            <select 
              class="form-select"
              v-model="documentStore.filters.category"
              @change="handleFilterChange"
            >
              <option value="">All Categories</option>
              <option 
                v-for="category in documentStore.categories" 
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
          </div>
          
          <!-- Status Filter -->
          <div class="col-md-2">
            <select 
              class="form-select"
              v-model="documentStore.filters.status"
              @change="handleFilterChange"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="archived">Archived</option>
              <option value="processing">Processing</option>
            </select>
          </div>
          
          <!-- File Type Filter -->
          <div class="col-md-2">
            <select 
              class="form-select"
              v-model="documentStore.filters.fileType"
              @change="handleFilterChange"
            >
              <option value="">All Types</option>
              <option value="application/pdf">PDF</option>
              <option value="application/msword">Word</option>
              <option value="application/vnd.ms-excel">Excel</option>
              <option value="image/jpeg">Images</option>
            </select>
          </div>
          
          <!-- View Toggle -->
          <div class="col-md-2">
            <div class="btn-group w-100" role="group">
              <input 
                type="radio" 
                class="btn-check" 
                id="listView" 
                v-model="viewMode"
                value="list"
                autocomplete="off"
              >
              <label class="btn btn-outline-secondary" for="listView">
                <i class="bi bi-list-ul"></i>
              </label>
              
              <input 
                type="radio" 
                class="btn-check" 
                id="gridView" 
                v-model="viewMode"
                value="grid"
                autocomplete="off"
              >
              <label class="btn btn-outline-secondary" for="gridView">
                <i class="bi bi-grid-3x3"></i>
              </label>
            </div>
          </div>
        </div>
        
        <!-- Active Filters Display -->
        <div v-if="hasActiveFilters" class="mt-3">
          <small class="text-muted">Active filters:</small>
          <div class="d-flex flex-wrap gap-2 mt-1">
            <span 
              v-if="searchQuery"
              class="badge bg-primary"
            >
              Search: "{{ searchQuery }}"
              <button 
                type="button" 
                class="btn-close btn-close-white ms-1" 
                @click="clearSearch"
                style="font-size: 0.6em;"
              ></button>
            </span>
            
            <span 
              v-if="documentStore.filters.category"
              class="badge bg-info"
            >
              Category: {{ getCategoryName(documentStore.filters.category) }}
              <button 
                type="button" 
                class="btn-close btn-close-white ms-1" 
                @click="clearCategoryFilter"
                style="font-size: 0.6em;"
              ></button>
            </span>
            
            <span 
              v-if="documentStore.filters.status"
              class="badge bg-success"
            >
              Status: {{ documentStore.filters.status }}
              <button 
                type="button" 
                class="btn-close btn-close-white ms-1" 
                @click="clearStatusFilter"
                style="font-size: 0.6em;"
              ></button>
            </span>
            
            <button 
              class="btn btn-sm btn-outline-secondary"
              @click="clearAllFilters"
            >
              Clear All
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Actions Bar (shown when documents are selected) -->
    <div v-if="documentStore.hasSelection" class="alert alert-info mb-3">
      <div class="d-flex justify-content-between align-items-center">
        <span>
          <i class="bi bi-check-square me-2"></i>
          {{ documentStore.selectedDocumentsCount }} document(s) selected
        </span>
        <div class="btn-group">
          <button 
            class="btn btn-sm btn-outline-warning"
            @click="bulkArchive"
            :disabled="documentStore.loading"
          >
            <i class="bi bi-archive me-1"></i>
            Archive
          </button>
          <button 
            class="btn btn-sm btn-outline-danger"
            @click="bulkDelete"
            :disabled="documentStore.loading"
          >
            <i class="bi bi-trash me-1"></i>
            Delete
          </button>
          <button 
            class="btn btn-sm btn-outline-secondary"
            @click="documentStore.clearSelection()"
          >
            <i class="bi bi-x me-1"></i>
            Clear Selection
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="documentStore.loading && !documentStore.documents.length" class="text-center py-5">
      <div class="spinner-border text-primary mb-3" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted">Loading documents...</p>
    </div>

    <!-- Error State -->
    <div v-if="documentStore.error" class="alert alert-danger mb-4">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ documentStore.error }}
      <button 
        class="btn btn-sm btn-outline-danger ms-2"
        @click="documentStore.clearError()"
      >
        Dismiss
      </button>
    </div>

    <!-- Document List/Grid View -->
    <DocumentList 
      v-if="!documentStore.loading || documentStore.documents.length"
      :viewMode="viewMode"
      :documents="documentStore.filteredDocuments"
      @document-select="handleDocumentSelect"
      @document-view="handleDocumentView"
      @document-download="handleDocumentDownload"
      @document-share="handleDocumentShare"
      @document-edit="handleDocumentEdit"
      @document-archive="handleDocumentArchive"
      @document-delete="handleDocumentDelete"
    />

    <!-- Empty State -->
    <div v-if="!documentStore.loading && documentStore.filteredDocuments.length === 0" class="text-center py-5">
      <i class="bi bi-files display-1 text-muted mb-3"></i>
      <h5 class="text-muted mb-3">
        {{ hasActiveFilters ? 'No documents match your filters' : 'No documents uploaded yet' }}
      </h5>
      <p class="text-muted mb-4">
        {{ hasActiveFilters ? 'Try adjusting your search criteria.' : 'Upload your first document to get started.' }}
      </p>
      <button 
        v-if="!hasActiveFilters"
        class="btn btn-primary"
        @click="showUploadModal = true"
      >
        <i class="bi bi-cloud-upload me-2"></i>
        Upload Documents
      </button>
      <button 
        v-else
        class="btn btn-outline-secondary"
        @click="clearAllFilters"
      >
        <i class="bi bi-funnel me-2"></i>
        Clear Filters
      </button>
    </div>

    <!-- Pagination -->
    <nav v-if="documentStore.pagination.totalPages > 1" class="mt-4">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: documentStore.pagination.page <= 1 }">
          <button class="page-link" @click="documentStore.previousPage()">
            <i class="bi bi-chevron-left"></i>
          </button>
        </li>
        
        <li 
          v-for="page in visiblePages" 
          :key="page"
          class="page-item"
          :class="{ active: documentStore.pagination.page === page }"
        >
          <button class="page-link" @click="documentStore.setPage(page)">
            {{ page }}
          </button>
        </li>
        
        <li class="page-item" :class="{ disabled: documentStore.pagination.page >= documentStore.pagination.totalPages }">
          <button class="page-link" @click="documentStore.nextPage()">
            <i class="bi bi-chevron-right"></i>
          </button>
        </li>
      </ul>
    </nav>

    <!-- Upload Modal -->
    <Teleport to="body">
      <div v-if="showUploadModal" class="upload-modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-xl modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i class="bi bi-cloud-upload me-2"></i>
                  Upload Documents
                </h5>
                <button type="button" class="btn-close" @click="closeUploadModal"></button>
              </div>
              <div class="modal-body">
                <DocumentUpload 
                  @close="closeUploadModal"
                  @uploaded="handleDocumentUploaded"
                />
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" @click="closeUploadModal">
                  <i class="bi bi-x-circle me-1"></i>
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="closeUploadModal"></div>
      </div>
    </Teleport>

    <!-- Document Viewer Modal -->
    <DocumentViewer 
      v-if="viewingDocument"
      :document="viewingDocument"
      @close="viewingDocument = null"
      @updated="handleDocumentUpdated"
      @deleted="handleDocumentDeleted"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useDocumentStore } from '@/stores/documentStore.js'
import DocumentList from '@/components/DocumentList.vue'
import DocumentUpload from '@/components/DocumentUpload.vue'
import DocumentViewer from '@/components/DocumentViewer.vue'

export default {
  name: 'DocumentCenter',
  components: {
    DocumentList,
    DocumentUpload,
    DocumentViewer
  },
  setup() {
    console.log('=== DocumentCenter setup() called ===')
    const documentStore = useDocumentStore()
    console.log('Document store initialized:', documentStore)
    
    // Local reactive state
    const showStatistics = ref(false)
    const showUploadModal = ref(false)
    const viewingDocument = ref(null)
    const viewMode = ref('list') // 'list' or 'grid'
    const searchQuery = ref('')
    const searchTimeout = ref(null)
    const isDragging = ref(false)
    const isDragOverQuick = ref(false)
    const dragCounter = ref(0)

    // Computed properties
    const hasActiveFilters = computed(() => {
      return searchQuery.value ||
             documentStore.filters.category ||
             documentStore.filters.status ||
             documentStore.filters.fileType ||
             documentStore.filters.complianceType ||
             documentStore.filters.containsPII !== null
    })

    const visiblePages = computed(() => {
      const current = documentStore.pagination.page
      const total = documentStore.pagination.totalPages
      const range = 5 // Show 5 page numbers at a time
      
      let start = Math.max(1, current - Math.floor(range / 2))
      let end = Math.min(total, start + range - 1)
      
      if (end - start + 1 < range) {
        start = Math.max(1, end - range + 1)
      }
      
      const pages = []
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    // Methods
    const getCategoryName = (categoryId) => {
      const category = documentStore.categories.find(c => c.id === categoryId)
      return category ? category.name : 'Unknown'
    }

    const handleSearch = () => {
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value)
      }
      
      searchTimeout.value = setTimeout(() => {
        if (searchQuery.value.trim()) {
          documentStore.searchDocuments(searchQuery.value.trim())
        } else {
          documentStore.fetchDocuments()
        }
      }, 300) // Debounce search
    }

    const clearSearch = () => {
      searchQuery.value = ''
      documentStore.updateFilters({ search: '' })
      documentStore.fetchDocuments()
    }

    const handleFilterChange = () => {
      documentStore.fetchDocuments()
    }

    const clearCategoryFilter = () => {
      documentStore.updateFilters({ category: null })
      documentStore.fetchDocuments()
    }

    const clearStatusFilter = () => {
      documentStore.updateFilters({ status: '' })
      documentStore.fetchDocuments()
    }

    const clearAllFilters = () => {
      searchQuery.value = ''
      documentStore.clearFilters()
      documentStore.fetchDocuments()
    }

    // Document event handlers
    const handleDocumentSelect = (documentId, selected) => {
      if (selected) {
        documentStore.selectDocument(documentId)
      } else {
        documentStore.deselectDocument(documentId)
      }
    }

    const handleDocumentView = (document) => {
      viewingDocument.value = document
    }

    const handleDocumentDownload = async (document) => {
      try {
        await documentStore.downloadDocument(document.id, document.original_filename)
      } catch (error) {
        console.error('Download failed:', error)
      }
    }

    const handleDocumentShare = (document) => {
      // Open share modal (to be implemented)
      console.log('Share document:', document)
    }

    const handleDocumentEdit = (document) => {
      viewingDocument.value = document
    }

    const handleDocumentArchive = async (document) => {
      if (confirm(`Are you sure you want to archive "${document.title || document.original_filename}"?`)) {
        try {
          await documentStore.archiveDocument(document.id)
        } catch (error) {
          console.error('Archive failed:', error)
        }
      }
    }

    const handleDocumentDelete = async (document) => {
      if (confirm(`Are you sure you want to permanently delete "${document.title || document.original_filename}"? This action cannot be undone.`)) {
        try {
          await documentStore.deleteDocument(document.id)
        } catch (error) {
          console.error('Delete failed:', error)
        }
      }
    }

    // Bulk operations
    const bulkArchive = async () => {
      if (confirm(`Are you sure you want to archive ${documentStore.selectedDocumentsCount} document(s)?`)) {
        try {
          await documentStore.bulkAction('archive', documentStore.selectedDocuments)
        } catch (error) {
          console.error('Bulk archive failed:', error)
        }
      }
    }

    const bulkDelete = async () => {
      if (confirm(`Are you sure you want to permanently delete ${documentStore.selectedDocumentsCount} document(s)? This action cannot be undone.`)) {
        try {
          await documentStore.bulkAction('delete', documentStore.selectedDocuments)
        } catch (error) {
          console.error('Bulk delete failed:', error)
        }
      }
    }

    // Modal event handlers
    const handleDocumentUploaded = (document) => {
      showUploadModal.value = false
      // Document is automatically added to store by the upload action
    }

    const handleDocumentUpdated = (document) => {
      // Document is automatically updated in store
    }

    const handleDocumentDeleted = (document) => {
      viewingDocument.value = null
      // Document is automatically removed from store
    }

    // Upload handlers
    const closeUploadModal = () => {
      showUploadModal.value = false
    }

    // Drag and Drop handlers
    const handleDragOver = (e) => {
      e.preventDefault()
      dragCounter.value++
      isDragging.value = true
    }

    const handleDragLeave = (e) => {
      e.preventDefault()
      dragCounter.value--
      if (dragCounter.value === 0) {
        isDragging.value = false
      }
    }

    const handleDrop = async (e) => {
      e.preventDefault()
      isDragging.value = false
      dragCounter.value = 0
      
      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        // Open upload modal with the dropped files
        showUploadModal.value = true
        // Wait for next tick to ensure modal is mounted
        await new Promise(resolve => setTimeout(resolve, 100))
        // Pass files to the upload component
        const event = new CustomEvent('files-dropped', { 
          detail: { files } 
        })
        window.dispatchEvent(event)
      }
    }
    
    const handleQuickDrop = async (e) => {
      e.preventDefault()
      isDragOverQuick.value = false
      
      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        // Open upload modal with the dropped files
        showUploadModal.value = true
        // Wait for next tick to ensure modal is mounted
        await new Promise(resolve => setTimeout(resolve, 100))
        // Pass files to the upload component
        const event = new CustomEvent('files-dropped', { 
          detail: { files } 
        })
        window.dispatchEvent(event)
      }
    }

    // Lifecycle
    onMounted(async () => {
      console.log('DocumentCenter mounted')
      console.log('documentStore available:', !!documentStore)
      
      try {
        // Load documents first, then stats and categories in background
        if (documentStore.fetchDocuments) {
          await documentStore.fetchDocuments()
        } else {
          console.error('documentStore.fetchDocuments not available')
        }
        
        // Load these in the background (don't block the UI if they fail)
        Promise.all([
          documentStore.fetchCategories ? documentStore.fetchCategories().catch(console.error) : Promise.resolve(),
          documentStore.fetchStatistics ? documentStore.fetchStatistics().catch(console.error) : Promise.resolve()
        ])
      } catch (error) {
        console.error('Failed to load documents:', error)
      }
    })

    // Watch for search query changes
    watch(() => documentStore.filters.search, (newValue) => {
      searchQuery.value = newValue || ''
    })

    return {
      documentStore,
      showStatistics,
      showUploadModal,
      viewingDocument,
      viewMode,
      searchQuery,
      isDragging,
      isDragOverQuick,
      hasActiveFilters,
      visiblePages,
      getCategoryName,
      handleSearch,
      clearSearch,
      handleFilterChange,
      clearCategoryFilter,
      clearStatusFilter,
      clearAllFilters,
      handleDocumentSelect,
      handleDocumentView,
      handleDocumentDownload,
      handleDocumentShare,
      handleDocumentEdit,
      handleDocumentArchive,
      handleDocumentDelete,
      bulkArchive,
      bulkDelete,
      handleDocumentUploaded,
      handleDocumentUpdated,
      handleDocumentDeleted,
      closeUploadModal,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      handleQuickDrop
    }
  }
}
</script>

<style scoped>
.document-center {
  padding: 100px 20px 20px 20px; /* Top padding for fixed header */
}

.btn-group .btn-check:checked + .btn {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
  color: white;
}

.badge .btn-close {
  padding: 0;
  font-size: 0.6em;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.input-group .btn {
  border-left: none;
}

.pagination .page-link {
  color: var(--bs-primary);
}

.pagination .page-item.active .page-link {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
}

.alert-info {
  background-color: rgba(13, 110, 253, 0.1);
  border-color: rgba(13, 110, 253, 0.2);
}

/* Drag & Drop Styles */
.document-center {
  position: relative;
  transition: background-color 0.2s ease;
}

.document-center.drag-over {
  background-color: rgba(13, 110, 253, 0.05);
}

.drag-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(5px);
}

.drag-content {
  text-align: center;
  padding: 3rem;
  border: 2px dashed #007bff;
  border-radius: 12px;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 90%;
}

.drag-content i {
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

/* Upload Modal Styles */
.upload-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

.upload-modal-overlay .modal {
  position: relative;
  z-index: 10001;
}

.upload-modal-overlay .modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 10000;
}

/* Quick Upload Zone Styles */
.quick-upload-zone {
  border: 2px dashed #dee2e6;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.quick-upload-zone:hover {
  border-color: #007bff;
  background: #e7f3ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.quick-upload-zone.drag-active {
  border-color: #007bff;
  background: #e3f2fd;
  transform: scale(1.02);
  box-shadow: 0 8px 20px rgba(0, 123, 255, 0.2);
}

.quick-upload-zone i {
  color: #6c757d;
  transition: color 0.3s ease;
}

.quick-upload-zone:hover i,
.quick-upload-zone.drag-active i {
  color: #007bff;
}

@media (max-width: 768px) {
  .document-center {
    padding: 80px 15px 15px 15px; /* Smaller top padding on mobile */
  }
  
  .d-flex.gap-2 {
    flex-direction: column;
  }
  
  .btn-group.w-100 {
    width: 100% !important;
  }
}
</style>