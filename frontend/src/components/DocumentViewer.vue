<template>
  <div class="document-viewer">
    <!-- Modal for Document Viewing -->
    <div 
      class="modal fade" 
      id="documentViewerModal" 
      tabindex="-1" 
      ref="modal"
    >
      <div class="modal-dialog modal-xl modal-fullscreen-lg-down">
        <div class="modal-content">
          <!-- Modal Header -->
          <div class="modal-header">
            <div class="modal-title-section">
              <h5 class="modal-title d-flex align-items-center">
                <i :class="getFileIcon(document?.content_type)" class="me-2"></i>
                {{ document?.name || 'Document Viewer' }}
              </h5>
              <div v-if="document" class="document-meta text-muted">
                <small>
                  {{ formatFileSize(document.file_size) }} • 
                  {{ formatDate(document.created_at) }} •
                  <span :class="getStatusBadgeClass(document.status)">
                    {{ getStatusDisplay(document.status) }}
                  </span>
                </small>
              </div>
            </div>
            
            <div class="modal-actions">
              <div class="btn-group me-3">
                <button 
                  class="btn btn-outline-secondary btn-sm"
                  @click="downloadDocument"
                  :disabled="!document"
                >
                  <i class="bi bi-download me-1"></i>Download
                </button>
                
                <button 
                  class="btn btn-outline-secondary btn-sm"
                  @click="shareDocument"
                  :disabled="!document"
                >
                  <i class="bi bi-share me-1"></i>Share
                </button>
                
                <div class="dropdown">
                  <button 
                    class="btn btn-outline-secondary btn-sm dropdown-toggle"
                    type="button"
                    data-bs-toggle="dropdown"
                    :disabled="!document"
                  >
                    <i class="bi bi-three-dots"></i>
                  </button>
                  <ul class="dropdown-menu dropdown-menu-end">
                    <li>
                      <button class="dropdown-item" @click="editDocument">
                        <i class="bi bi-pencil me-2"></i>Edit Details
                      </button>
                    </li>
                    <li>
                      <button class="dropdown-item" @click="viewVersions">
                        <i class="bi bi-clock-history me-2"></i>Version History
                      </button>
                    </li>
                    <li>
                      <button class="dropdown-item" @click="viewAuditTrail">
                        <i class="bi bi-list-check me-2"></i>Audit Trail
                      </button>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                      <button class="dropdown-item text-warning" @click="archiveDocument">
                        <i class="bi bi-archive me-2"></i>Archive
                      </button>
                    </li>
                    <li>
                      <button class="dropdown-item text-danger" @click="deleteDocument">
                        <i class="bi bi-trash me-2"></i>Delete
                      </button>
                    </li>
                  </ul>
                </div>
              </div>
              
              <button 
                type="button" 
                class="btn-close" 
                @click="closeViewer"
              ></button>
            </div>
          </div>
          
          <!-- Modal Body -->
          <div class="modal-body p-0">
            <div class="viewer-container">
              <!-- Loading State -->
              <div v-if="loading" class="viewer-loading">
                <div class="text-center py-5">
                  <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                  <p class="text-muted">Loading document preview...</p>
                </div>
              </div>
              
              <!-- Error State -->
              <div v-else-if="error" class="viewer-error">
                <div class="text-center py-5">
                  <div class="mb-3">
                    <i class="bi bi-exclamation-triangle-fill text-warning" style="font-size: 3rem;"></i>
                  </div>
                  <h5 class="text-muted">Preview Not Available</h5>
                  <p class="text-muted mb-3">{{ error }}</p>
                  <button class="btn btn-primary" @click="downloadDocument">
                    <i class="bi bi-download me-2"></i>Download to View
                  </button>
                </div>
              </div>
              
              <!-- PDF Viewer -->
              <div v-else-if="document?.content_type === 'application/pdf'" class="pdf-viewer">
                <iframe 
                  :src="previewUrl" 
                  class="pdf-frame"
                  title="PDF Preview"
                ></iframe>
              </div>
              
              <!-- Image Viewer -->
              <div v-else-if="isImageFile" class="image-viewer">
                <div class="image-container">
                  <img 
                    :src="previewUrl" 
                    :alt="document?.name"
                    class="preview-image"
                    @load="onImageLoad"
                    @error="onImageError"
                  />
                </div>
                
                <!-- Image Controls -->
                <div class="image-controls">
                  <div class="btn-group">
                    <button class="btn btn-outline-secondary btn-sm" @click="zoomOut">
                      <i class="bi bi-zoom-out"></i>
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" @click="resetZoom">
                      {{ Math.round(imageZoom * 100) }}%
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" @click="zoomIn">
                      <i class="bi bi-zoom-in"></i>
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- Text File Viewer -->
              <div v-else-if="isTextFile" class="text-viewer">
                <div class="text-content">
                  <pre>{{ textContent }}</pre>
                </div>
              </div>
              
              <!-- Office Documents -->
              <div v-else-if="isOfficeFile" class="office-viewer">
                <div class="text-center py-5">
                  <div class="mb-3">
                    <i :class="getFileIcon(document?.content_type)" style="font-size: 4rem;"></i>
                  </div>
                  <h5>{{ document?.name }}</h5>
                  <p class="text-muted mb-4">
                    This document type requires downloading to view its full content.
                  </p>
                  <button class="btn btn-primary me-2" @click="downloadDocument">
                    <i class="bi bi-download me-2"></i>Download Document
                  </button>
                  <button class="btn btn-outline-secondary" @click="openInNewTab">
                    <i class="bi bi-box-arrow-up-right me-2"></i>Open in New Tab
                  </button>
                </div>
              </div>
              
              <!-- Default/Unknown File Type -->
              <div v-else class="default-viewer">
                <div class="text-center py-5">
                  <div class="mb-3">
                    <i class="bi bi-file-earmark text-muted" style="font-size: 4rem;"></i>
                  </div>
                  <h5>{{ document?.name }}</h5>
                  <p class="text-muted mb-4">Preview not available for this file type.</p>
                  <button class="btn btn-primary" @click="downloadDocument">
                    <i class="bi bi-download me-2"></i>Download to View
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Document Details Sidebar -->
          <div v-if="showDetails" class="document-details">
            <div class="details-header">
              <h6 class="mb-0">Document Details</h6>
              <button class="btn btn-sm btn-outline-secondary" @click="showDetails = false">
                <i class="bi bi-x"></i>
              </button>
            </div>
            
            <div class="details-content">
              <div class="detail-group">
                <label class="detail-label">Name</label>
                <div class="detail-value">{{ document?.name }}</div>
              </div>
              
              <div class="detail-group">
                <label class="detail-label">File Type</label>
                <div class="detail-value">{{ document?.content_type }}</div>
              </div>
              
              <div class="detail-group">
                <label class="detail-label">File Size</label>
                <div class="detail-value">{{ formatFileSize(document?.file_size) }}</div>
              </div>
              
              <div class="detail-group">
                <label class="detail-label">Category</label>
                <div class="detail-value">
                  <span v-if="document?.category" class="badge bg-secondary">
                    {{ document.category.name }}
                  </span>
                  <span v-else class="text-muted">No category</span>
                </div>
              </div>
              
              <div class="detail-group">
                <label class="detail-label">Client</label>
                <div class="detail-value">
                  <div v-if="document?.client">
                    <div class="fw-medium">{{ document.client.first_name }} {{ document.client.last_name }}</div>
                    <small class="text-muted">{{ document.client.email }}</small>
                  </div>
                  <span v-else class="text-muted">All clients</span>
                </div>
              </div>
              
              <div class="detail-group">
                <label class="detail-label">Status</label>
                <div class="detail-value">
                  <span :class="getStatusBadgeClass(document?.status)">
                    {{ getStatusDisplay(document?.status) }}
                  </span>
                </div>
              </div>
              
              <div class="detail-group">
                <label class="detail-label">Created</label>
                <div class="detail-value">
                  <div>{{ formatDate(document?.created_at) }}</div>
                  <small class="text-muted">{{ formatTime(document?.created_at) }}</small>
                </div>
              </div>
              
              <div class="detail-group">
                <label class="detail-label">Last Modified</label>
                <div class="detail-value">
                  <div>{{ formatDate(document?.updated_at) }}</div>
                  <small class="text-muted">{{ formatTime(document?.updated_at) }}</small>
                </div>
              </div>
              
              <div v-if="document?.compliance_type" class="detail-group">
                <label class="detail-label">Compliance</label>
                <div class="detail-value">
                  <span class="badge bg-info">
                    {{ getComplianceDisplay(document.compliance_type) }}
                  </span>
                </div>
              </div>
              
              <div v-if="document?.tags && document.tags.length" class="detail-group">
                <label class="detail-label">Tags</label>
                <div class="detail-value">
                  <span 
                    v-for="tag in document.tags" 
                    :key="tag" 
                    class="badge bg-light text-dark me-1"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { documentService } from '../services/documentService.js'

const props = defineProps({
  document: {
    type: Object,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'download', 'share', 'edit', 'delete', 'archive'])

const modal = ref(null)
const loading = ref(false)
const error = ref('')
const previewUrl = ref('')
const textContent = ref('')
const showDetails = ref(false)
const imageZoom = ref(1)

let modalInstance = null

const isImageFile = computed(() => {
  return props.document?.content_type?.startsWith('image/')
})

const isTextFile = computed(() => {
  const textTypes = ['text/plain', 'text/csv']
  return textTypes.includes(props.document?.content_type)
})

const isOfficeFile = computed(() => {
  const officeTypes = [
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]
  return officeTypes.includes(props.document?.content_type)
})

watch(() => props.visible, async (newVisible) => {
  if (newVisible && props.document) {
    await showModal()
  } else if (!newVisible) {
    hideModal()
  }
})

watch(() => props.document, async (newDocument) => {
  if (newDocument && props.visible) {
    await loadDocumentPreview()
  }
})

async function showModal() {
  if (!modalInstance) {
    modalInstance = new window.bootstrap.Modal(modal.value)
  }
  
  await loadDocumentPreview()
  modalInstance.show()
}

function hideModal() {
  if (modalInstance) {
    modalInstance.hide()
  }
}

function closeViewer() {
  hideModal()
  emit('close')
}

async function loadDocumentPreview() {
  if (!props.document) return
  
  loading.value = true
  error.value = ''
  previewUrl.value = ''
  textContent.value = ''
  
  try {
    if (props.document.content_type === 'application/pdf') {
      const response = await documentService.downloadDocument(props.document.id)
      previewUrl.value = response.download_url
    } else if (isImageFile.value) {
      const response = await documentService.downloadDocument(props.document.id)
      previewUrl.value = response.download_url
    } else if (isTextFile.value) {
      const response = await fetch(props.document.file_url || '#')
      if (response.ok) {
        textContent.value = await response.text()
      } else {
        error.value = 'Failed to load text content'
      }
    } else if (isOfficeFile.value) {
      const response = await documentService.downloadDocument(props.document.id)
      previewUrl.value = response.download_url
    }
  } catch (err) {
    error.value = 'Failed to load document preview'
    console.error('Preview error:', err)
  } finally {
    loading.value = false
  }
}

function onImageLoad() {
  loading.value = false
}

function onImageError() {
  error.value = 'Failed to load image'
  loading.value = false
}

function zoomIn() {
  imageZoom.value = Math.min(imageZoom.value * 1.2, 3)
}

function zoomOut() {
  imageZoom.value = Math.max(imageZoom.value / 1.2, 0.1)
}

function resetZoom() {
  imageZoom.value = 1
}

function downloadDocument() {
  emit('download', props.document)
}

function shareDocument() {
  emit('share', props.document)
}

function editDocument() {
  emit('edit', props.document)
}

function archiveDocument() {
  emit('archive', props.document)
}

function deleteDocument() {
  emit('delete', props.document)
}

function openInNewTab() {
  if (previewUrl.value) {
    window.open(previewUrl.value, '_blank')
  }
}

function viewVersions() {
  console.log('View versions for:', props.document)
}

function viewAuditTrail() {
  console.log('View audit trail for:', props.document)
}

function getFileIcon(contentType) {
  return documentService.getFileIcon(contentType)
}

function formatFileSize(bytes) {
  return documentService.formatFileSize(bytes)
}

function getStatusBadgeClass(status) {
  return documentService.getStatusBadgeClass(status)
}

function getStatusDisplay(status) {
  const statusMap = {
    'processing': 'Processing',
    'active': 'Active',
    'archived': 'Archived',
    'quarantined': 'Quarantined',
    'deleted': 'Deleted'
  }
  return statusMap[status] || status
}

function getComplianceDisplay(complianceType) {
  return documentService.getComplianceTypeDisplay(complianceType)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString()
}

function formatTime(dateString) {
  return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-title-section {
  flex: 1;
}

.modal-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.document-meta {
  font-size: 0.875rem;
}

.modal-actions {
  display: flex;
  align-items: center;
}

.viewer-container {
  height: 70vh;
  min-height: 500px;
  position: relative;
  overflow: hidden;
}

.viewer-loading,
.viewer-error {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pdf-viewer {
  height: 100%;
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.image-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
  background: #f8f9fa;
  position: relative;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transform: scale(var(--zoom, 1));
  transition: transform 0.2s ease;
}

.image-controls {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background: rgba(0,0,0,0.8);
  border-radius: 6px;
  padding: 0.5rem;
}

.text-viewer {
  height: 100%;
  overflow: auto;
  background: #f8f9fa;
}

.text-content {
  padding: 2rem;
}

.text-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.office-viewer,
.default-viewer {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
}

.document-details {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 350px;
  background: #fff;
  border-left: 1px solid #dee2e6;
  z-index: 1000;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
}

.details-content {
  padding: 1rem;
  overflow-y: auto;
  height: calc(100% - 70px);
}

.detail-group {
  margin-bottom: 1.5rem;
}

.detail-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
  display: block;
}

.detail-value {
  font-size: 0.9rem;
  line-height: 1.4;
}

@media (max-width: 992px) {
  .modal-dialog {
    margin: 0;
    max-width: none;
    height: 100vh;
  }
  
  .modal-content {
    height: 100vh;
    border-radius: 0;
  }
  
  .viewer-container {
    height: calc(100vh - 150px);
  }
  
  .document-details {
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: 1050;
  }
}

@media (max-width: 576px) {
  .modal-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .modal-actions {
    justify-content: flex-end;
  }
  
  .image-controls {
    bottom: 0.5rem;
    right: 0.5rem;
  }
}
</style>