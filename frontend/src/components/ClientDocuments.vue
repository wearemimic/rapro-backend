<template>
  <div class="client-documents">
    <!-- Header with Upload Button -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h5 class="mb-0">Client Documents</h5>
        <small class="text-muted">{{ documents.length }} document(s) for this client</small>
      </div>
      <div>
        <input
          ref="fileInput"
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.csv,.jpg,.jpeg,.png,.tiff"
          style="display: none"
          @change="handleFileSelection"
        />
        <button 
          class="btn btn-primary btn-sm"
          @click="openUploadModal"
        >
          <div v-if="uploadingFiles" class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status">
              <span class="visually-hidden">Uploading...</span>
            </div>
            Uploading...
          </div>
          <div v-else class="d-flex align-items-center">
            <i class="bi bi-cloud-upload me-1"></i>
            Upload Document
          </div>
        </button>
      </div>
    </div>

    <!-- Quick Upload Drop Zone -->
    <div 
      v-if="!uploadingFiles"
      class="client-upload-zone mb-3"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      :class="{ 'drag-active': isDragging }"
      @click="openUploadModal"
    >
      <i class="bi bi-cloud-upload me-2"></i>
      <span>Drop files here or click to upload (with category selection)</span>
    </div>
    
    <!-- Upload Progress -->
    <div v-if="uploadingFiles" class="upload-progress-zone mb-3">
      <div class="d-flex align-items-center justify-content-center">
        <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
          <span class="visually-hidden">Uploading...</span>
        </div>
        <span>Uploading files...</span>
      </div>
    </div>

    <!-- Document Categories Filter -->
    <div class="mb-3" v-if="documents.length > 0">
      <div class="btn-group btn-group-sm" role="group">
        <button 
          type="button" 
          class="btn"
          :class="selectedCategory === 'all' ? 'btn-primary' : 'btn-outline-primary'"
          @click="selectedCategory = 'all'"
        >
          All ({{ documents.length }})
        </button>
        <button 
          v-for="category in documentCategories" 
          :key="category.id"
          type="button" 
          class="btn"
          :class="selectedCategory === category.id ? 'btn-primary' : 'btn-outline-primary'"
          @click="selectedCategory = category.id"
        >
          {{ category.name }} ({{ getCategoryCount(category.id) }})
        </button>
      </div>
    </div>

    <!-- Documents List -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading documents...</span>
      </div>
    </div>

    <div v-else-if="filteredDocuments.length === 0" class="text-center py-4">
      <i class="bi bi-folder-x display-4 text-muted"></i>
      <p class="text-muted mt-2">No documents found for this client</p>
    </div>

    <div v-else class="document-list">
      <div 
        v-for="doc in filteredDocuments" 
        :key="doc.id"
        class="document-item card mb-2"
      >
        <div class="card-body p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div class="d-flex align-items-start">
              <div class="document-icon me-3">
                <i :class="getFileIcon(doc.content_type)"></i>
              </div>
              <div>
                <h6 class="mb-1">{{ doc.title || doc.original_filename }}</h6>
                <div class="text-muted small">
                  <span class="me-3">
                    <i class="bi bi-calendar me-1"></i>
                    {{ formatDate(doc.uploaded_at) }}
                  </span>
                  <span class="me-3">
                    <i class="bi bi-hdd me-1"></i>
                    {{ formatFileSize(doc.file_size) }}
                  </span>
                  <span v-if="doc.category_name">
                    <i class="bi bi-folder me-1"></i>
                    {{ doc.category_name }}
                  </span>
                </div>
                <p class="mb-0 mt-1 text-muted small" v-if="doc.description">
                  {{ doc.description }}
                </p>
              </div>
            </div>
            <div class="btn-group btn-group-sm">
              <button 
                class="btn btn-outline-primary"
                @click="viewDocument(doc)"
                title="View"
              >
                <i class="bi bi-eye"></i>
              </button>
              <button 
                class="btn btn-outline-success"
                @click="downloadDocument(doc)"
                title="Download"
              >
                <i class="bi bi-download"></i>
              </button>
              <button 
                class="btn"
                :class="doc.is_client_visible ? 'btn-info' : 'btn-outline-secondary'"
                @click="toggleDocumentSharing(doc)"
                :title="doc.is_client_visible ? 'Shared with client - click to make private' : 'Private - click to share with client'"
              >
                <i :class="doc.is_client_visible ? 'bi bi-share-fill' : 'bi bi-share'"></i>
              </button>
              <button 
                class="btn btn-outline-danger"
                @click="deleteDocument(doc)"
                title="Delete"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <Teleport to="body">
      <div v-if="showUploadModal" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i class="bi bi-cloud-upload me-2"></i>
                  Upload Document for {{ clientName }}
                </h5>
                <button type="button" class="btn-close" @click="closeUploadModal"></button>
              </div>
              <div class="modal-body">
                <ClientDocumentUpload 
                  :clientId="clientId"
                  :clientName="clientName"
                  :initialFiles="pendingFiles"
                  @close="closeUploadModal"
                  @uploaded="handleDocumentUploaded"
                />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="closeUploadModal"></div>
      </div>
    </Teleport>

    <!-- Document Viewer Modal -->
    <Teleport to="body">
      <div v-if="viewingDocument" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-xl modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i class="bi bi-file-text me-2"></i>
                  {{ viewingDocument.title || viewingDocument.original_filename }}
                </h5>
                <button type="button" class="btn-close" @click="viewingDocument = null"></button>
              </div>
              <div class="modal-body">
                <!-- Document preview would go here -->
                <div class="text-center py-5">
                  <i :class="getFileIcon(viewingDocument.content_type) + ' display-1 mb-3'"></i>
                  <p>{{ viewingDocument.original_filename }}</p>
                  <p class="text-muted">{{ formatFileSize(viewingDocument.file_size) }}</p>
                  <button class="btn btn-primary" @click="downloadDocument(viewingDocument)">
                    <i class="bi bi-download me-2"></i>
                    Download Document
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
import ClientDocumentUpload from '@/components/ClientDocumentUpload.vue'

const props = defineProps({
  clientId: {
    type: [Number, String],
    required: true
  },
  clientName: {
    type: String,
    default: 'Client'
  }
})

const emit = defineEmits(['document-count-updated'])

const documentStore = useDocumentStore()

// State
const documents = ref([])
const documentCategories = ref([])
const loading = ref(false)
const showUploadModal = ref(false)
const viewingDocument = ref(null)
const selectedCategory = ref('all')
const pendingFiles = ref([])
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

const getCategoryCount = (categoryId) => {
  return documents.value.filter(doc => doc.category === categoryId).length
}

// Methods
const loadClientDocuments = async () => {
  loading.value = true
  try {
    const response = await documentStore.getClientDocuments(props.clientId)
    documents.value = response.results || response || []
    // Emit document count to parent
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
  }
}

const deleteDocument = async (doc) => {
  if (confirm(`Are you sure you want to delete "${doc.title || doc.original_filename}"?`)) {
    try {
      await documentStore.deleteDocument(doc.id)
      await loadClientDocuments() // This will emit the updated count
    } catch (error) {
      console.error('Delete failed:', error)
    }
  }
}

const toggleDocumentSharing = async (doc) => {
  try {
    const newVisibility = !doc.is_client_visible
    await documentStore.toggleDocumentSharing(doc.id, newVisibility)
    
    // Update local state
    doc.is_client_visible = newVisibility
    
    // Show success message
    const message = newVisibility 
      ? `"${doc.title || doc.original_filename}" is now shared with client`
      : `"${doc.title || doc.original_filename}" is now private`
    
    // You could add toast notification here if available
    console.log(message)
    
  } catch (error) {
    console.error('Failed to toggle document sharing:', error)
    alert('Failed to update document sharing. Please try again.')
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
  // Clear the input so same file can be selected again
  e.target.value = ''
}

const uploadFiles = async (files) => {
  uploadingFiles.value = true
  
  try {
    for (const file of files) {
      // Validate file type and size
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
        client_id: props.clientId,
        title: file.name.split('.').slice(0, -1).join('.'),
        description: `Uploaded for ${props.clientName}`
      })
    }
    
    // Reload documents after upload
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

const handleDrop = async (e) => {
  e.preventDefault()
  isDragging.value = false
  
  const files = Array.from(e.dataTransfer.files)
  if (files.length > 0) {
    pendingFiles.value = files
    showUploadModal.value = true
  }
}

const openUploadModal = () => {
  pendingFiles.value = []
  showUploadModal.value = true
}

const closeUploadModal = () => {
  showUploadModal.value = false
}

const handleDocumentUploaded = async () => {
  showUploadModal.value = false
  await loadClientDocuments()
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadClientDocuments(),
    loadCategories()
  ])
})

// Watch for client changes
watch(() => props.clientId, async (newId) => {
  if (newId) {
    await loadClientDocuments()
  }
})
</script>

<style scoped>
.client-documents {
  min-height: 400px;
}

.client-upload-zone {
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.client-upload-zone:hover {
  border-color: #007bff;
  background: #e7f3ff;
}

.client-upload-zone.drag-active {
  border-color: #007bff;
  background: #e3f2fd;
  transform: scale(1.01);
}

.upload-progress-zone {
  border: 2px solid #007bff;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  background: #e7f3ff;
}

.document-item {
  transition: all 0.2s ease;
  border: 1px solid #dee2e6;
}

.document-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.document-icon {
  font-size: 2rem;
  width: 40px;
  text-align: center;
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