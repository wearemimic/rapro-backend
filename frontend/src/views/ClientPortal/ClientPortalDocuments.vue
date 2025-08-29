<template>
  <div class="client-portal-documents">
    <div class="page-header mb-4">
      <h5 class="mb-0">My Documents</h5>
      <small class="text-muted">Access and manage your financial documents</small>
    </div>

    <!-- Upload Section -->
    <div class="card mb-4">
      <div class="card-body">
        <h6 class="card-title">
          <i class="bi bi-cloud-upload me-2"></i>
          Upload New Document
        </h6>
        
        <!-- Upload Button -->
        <div class="mb-3">
          <input
            ref="fileInput"
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.csv,.jpg,.jpeg,.png,.tiff"
            style="display: none"
            @change="handleFileSelection"
          />
          <button 
            class="btn btn-primary me-2"
            @click="triggerFileInput"
            :disabled="uploadingFiles"
          >
            <div v-if="uploadingFiles" class="d-flex align-items-center">
              <div class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Uploading...</span>
              </div>
              Uploading...
            </div>
            <div v-else class="d-flex align-items-center">
              <i class="bi bi-plus-circle me-2"></i>
              Select Files
            </div>
          </button>
          <small class="text-muted">
            Supported formats: PDF, Word, Excel, Images (up to 50MB each)
          </small>
        </div>

        <!-- Drag and Drop Zone -->
        <div 
          v-if="!uploadingFiles"
          class="upload-drop-zone"
          @drop.prevent="handleDrop"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          :class="{ 'drag-active': isDragging }"
          @click="triggerFileInput"
        >
          <div class="text-center py-4">
            <i class="bi bi-cloud-upload display-4 text-muted mb-2"></i>
            <p class="mb-0">Drag and drop files here or click to browse</p>
            <small class="text-muted">Multiple files supported</small>
          </div>
        </div>
        
        <!-- Upload Progress -->
        <div v-if="uploadingFiles" class="upload-progress">
          <div class="d-flex align-items-center justify-content-center py-4">
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
              <span class="visually-hidden">Uploading...</span>
            </div>
            <span>Processing your files...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Documents List -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">
          <i class="bi bi-folder me-2"></i>
          Your Documents ({{ documents.length }})
        </h6>
        
        <!-- Category Filter -->
        <div v-if="documents.length > 0" class="btn-group btn-group-sm">
          <button 
            type="button" 
            class="btn"
            :class="selectedCategory === 'all' ? 'btn-primary' : 'btn-outline-primary'"
            @click="selectedCategory = 'all'"
          >
            All
          </button>
          <button 
            v-for="category in documentCategories" 
            :key="category.id"
            type="button" 
            class="btn"
            :class="selectedCategory === category.id ? 'btn-primary' : 'btn-outline-primary'"
            @click="selectedCategory = category.id"
          >
            {{ category.name }}
          </button>
        </div>
      </div>
      
      <div class="card-body">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading documents...</span>
          </div>
          <p class="text-muted mt-2">Loading your documents...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredDocuments.length === 0" class="text-center py-5">
          <i class="bi bi-folder-x display-1 text-muted mb-3"></i>
          <h6 class="text-muted">No documents found</h6>
          <p class="text-muted mb-3">
            {{ selectedCategory === 'all' 
                ? 'Upload your first document using the area above' 
                : 'No documents in this category' }}
          </p>
          <button 
            v-if="selectedCategory === 'all'"
            class="btn btn-primary"
            @click="triggerFileInput"
          >
            Upload Document
          </button>
        </div>

        <!-- Documents Grid -->
        <div v-else class="row">
          <div 
            v-for="doc in filteredDocuments" 
            :key="doc.id"
            class="col-md-6 col-lg-4 mb-3"
          >
            <div class="document-card card h-100">
              <div class="card-body p-3">
                <div class="d-flex align-items-start mb-2">
                  <div class="document-icon me-3">
                    <i :class="getFileIcon(doc.content_type)"></i>
                  </div>
                  <div class="flex-grow-1">
                    <h6 class="card-title mb-1 text-truncate" :title="doc.title || doc.original_filename">
                      {{ doc.title || doc.original_filename }}
                    </h6>
                    <div class="text-muted small mb-2">
                      <div>
                        <i class="bi bi-calendar me-1"></i>
                        {{ formatDate(doc.uploaded_at) }}
                      </div>
                      <div>
                        <i class="bi bi-hdd me-1"></i>
                        {{ formatFileSize(doc.file_size) }}
                      </div>
                      <div v-if="doc.category_name">
                        <i class="bi bi-tag me-1"></i>
                        {{ doc.category_name }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <p v-if="doc.description" class="card-text small text-muted mb-2 text-truncate">
                  {{ doc.description }}
                </p>
                
                <div class="document-actions">
                  <div class="btn-group w-100">
                    <button 
                      class="btn btn-outline-primary btn-sm"
                      @click="viewDocument(doc)"
                      title="View Document"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button 
                      class="btn btn-outline-success btn-sm"
                      @click="downloadDocument(doc)"
                      title="Download"
                    >
                      <i class="bi bi-download"></i>
                    </button>
                    <button 
                      class="btn btn-outline-secondary btn-sm"
                      @click="shareDocument(doc)"
                      title="Share"
                    >
                      <i class="bi bi-share"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Document Viewer Modal -->
    <Teleport to="body">
      <div v-if="viewingDocument" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-xl modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i :class="getFileIcon(viewingDocument.content_type) + ' me-2'"></i>
                  {{ viewingDocument.title || viewingDocument.original_filename }}
                </h5>
                <button type="button" class="btn-close" @click="viewingDocument = null"></button>
              </div>
              <div class="modal-body text-center py-5">
                <i :class="getFileIcon(viewingDocument.content_type) + ' display-1 mb-3'"></i>
                <h6>{{ viewingDocument.original_filename }}</h6>
                <p class="text-muted">{{ formatFileSize(viewingDocument.file_size) }}</p>
                <div class="mt-4">
                  <button 
                    class="btn btn-primary me-2" 
                    @click="downloadDocument(viewingDocument)"
                  >
                    <i class="bi bi-download me-2"></i>
                    Download Document
                  </button>
                  <button 
                    class="btn btn-outline-secondary" 
                    @click="shareDocument(viewingDocument)"
                  >
                    <i class="bi bi-share me-2"></i>
                    Share
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="viewingDocument = null"></div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDocumentStore } from '@/stores/documentStore.js'

const props = defineProps({
  client: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['document-count-updated'])

const documentStore = useDocumentStore()

// State
const documents = ref([])
const documentCategories = ref([])
const loading = ref(false)
const viewingDocument = ref(null)
const selectedCategory = ref('all')
const isDragging = ref(false)
const fileInput = ref(null)
const uploadingFiles = ref(false)

// Computed
const filteredDocuments = computed(() => {
  if (selectedCategory.value === 'all') {
    return documents.value
  }
  return documents.value.filter(doc => doc.category === selectedCategory.value)
})

// Methods
const loadClientDocuments = async () => {
  loading.value = true
  try {
    const response = await documentStore.getClientDocuments(props.client.id)
    documents.value = response.results || response || []
    emit('document-count-updated', documents.value.length)
  } catch (error) {
    console.error('Failed to load client documents:', error)
    documents.value = []
    emit('document-count-updated', 0)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const categories = await documentStore.fetchCategories()
    documentCategories.value = categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const triggerFileInput = () => {
  if (!uploadingFiles.value && fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelection = async (e) => {
  const files = Array.from(e.target.files)
  if (files.length > 0) {
    await uploadFiles(files)
  }
  e.target.value = ''
}

const handleDrop = async (e) => {
  e.preventDefault()
  isDragging.value = false
  
  const files = Array.from(e.dataTransfer.files)
  if (files.length > 0) {
    await uploadFiles(files)
  }
}

const uploadFiles = async (files) => {
  uploadingFiles.value = true
  
  try {
    for (const file of files) {
      if (!isValidFileType(file)) {
        alert(`File "${file.name}" has an unsupported file type.`)
        continue
      }
      
      if (!isValidFileSize(file)) {
        alert(`File "${file.name}" exceeds the 50MB size limit.`)
        continue
      }
      
      await documentStore.uploadDocument({
        file: file,
        client_id: props.client.id,
        title: file.name.split('.').slice(0, -1).join('.'),
        description: `Uploaded via client portal`
      })
    }
    
    await loadClientDocuments()
    
  } catch (error) {
    console.error('Upload failed:', error)
    alert('Upload failed. Please try again.')
  } finally {
    uploadingFiles.value = false
  }
}

const isValidFileType = (file) => {
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

const isValidFileSize = (file, maxSizeMB = 50) => {
  const maxSizeBytes = maxSizeMB * 1024 * 1024
  return file.size <= maxSizeBytes
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileIcon = (contentType) => {
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

const viewDocument = (doc) => {
  viewingDocument.value = doc
}

const downloadDocument = async (doc) => {
  try {
    await documentStore.downloadDocument(doc.id, doc.original_filename)
  } catch (error) {
    console.error('Download failed:', error)
    alert('Download failed. Please try again.')
  }
}

const shareDocument = (doc) => {
  // Placeholder for share functionality
  alert(`Share functionality for "${doc.title || doc.original_filename}" will be implemented soon.`)
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadClientDocuments(),
    loadCategories()
  ])
})

// Watch for client changes
watch(() => props.client?.id, async (newId) => {
  if (newId) {
    await loadClientDocuments()
  }
})
</script>

<style scoped>
.client-portal-documents {
  padding: 0;
}

.page-header {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1rem;
}

.upload-drop-zone {
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.upload-drop-zone:hover {
  border-color: #007bff;
  background: #e7f3ff;
}

.upload-drop-zone.drag-active {
  border-color: #007bff;
  background: #e3f2fd;
  transform: scale(1.01);
}

.upload-progress {
  border: 2px solid #007bff;
  border-radius: 8px;
  background: #e7f3ff;
}

.document-card {
  transition: all 0.2s ease;
  border: 1px solid #dee2e6;
}

.document-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.document-icon {
  font-size: 1.5rem;
  width: 30px;
  text-align: center;
}

.document-actions .btn-group .btn {
  flex: 1;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

.modal-overlay .modal {
  position: relative;
  z-index: 10001;
}

.modal-overlay .modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 10000;
}
</style>