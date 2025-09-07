<template>
  <div class="client-document-upload">
    <!-- Upload Area -->
    <div
      class="upload-area"
      :class="{ 
        'upload-dragging': isDragging, 
        'upload-disabled': uploading,
        'upload-error': hasError 
      }"
      @drop.prevent.stop="handleDrop"
      @dragover.prevent.stop="handleDragOver"
      @dragenter.prevent.stop="handleDragEnter"
      @dragleave.prevent.stop="handleDragLeave"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.csv,.jpg,.jpeg,.png,.tiff"
        style="display: none"
        @change="handleFileInput"
      />
      
      <div class="upload-content">
        <div v-if="!uploading" class="upload-icon">
          <i class="bi bi-cloud-upload" style="font-size: 3rem; color: #007bff;"></i>
        </div>
        
        <div v-if="uploading" class="upload-progress">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Uploading...</span>
          </div>
        </div>
        
        <div class="upload-text">
          <h5 v-if="!uploading" class="mb-2">
            {{ isDragging ? 'Drop files here' : 'Upload Documents for ' + clientName }}
          </h5>
          <h5 v-else class="mb-2">Uploading {{ uploadProgress }}%...</h5>
          
          <p v-if="!uploading" class="text-muted mb-3">
            <i class="bi bi-hand-index me-1"></i>
            Drag and drop files here or click to browse
          </p>
          
          <div v-if="uploading && uploadProgress > 0" class="progress mb-3">
            <div 
              class="progress-bar" 
              role="progressbar" 
              :style="{ width: uploadProgress + '%' }"
              :aria-valuenow="uploadProgress"
              aria-valuemin="0"
              aria-valuemax="100"
            >
              {{ uploadProgress }}%
            </div>
          </div>
          
          <small class="text-muted">
            Supported formats: PDF, Word, Excel, Images, Text files
            <br>
            Maximum file size: 50MB per file
          </small>
        </div>
      </div>
    </div>
    
    <!-- Error Messages -->
    <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ errorMessage }}
    </div>
    
    <!-- Success Messages -->
    <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>
      {{ successMessage }}
    </div>
    
    <!-- File Queue -->
    <div v-if="fileQueue.length > 0" class="file-queue mt-4">
      <h6 class="mb-3">
        <i class="bi bi-files me-2"></i>
        Files to Upload ({{ fileQueue.length }})
      </h6>
      
      <div class="file-list">
        <div 
          v-for="(fileItem, index) in fileQueue" 
          :key="index"
          class="file-item"
          :class="{ 'file-error': fileItem.error, 'file-success': fileItem.uploaded }"
        >
          <div class="file-info">
            <div class="file-icon">
              <i :class="getFileIcon(fileItem.file.type)"></i>
            </div>
            <div class="file-details">
              <div class="file-name">{{ fileItem.file.name }}</div>
              <div class="file-size">{{ formatFileSize(fileItem.file.size) }}</div>
            </div>
          </div>
          
          <div class="file-metadata">
            <div class="row g-2">
              <div class="col-12">
                <label class="form-label text-danger mb-1">
                  <i class="bi bi-folder-fill me-1"></i>
                  Category <span class="text-danger">*</span>
                  <small class="text-muted ms-1">(determines retention period)</small>
                </label>
                <select 
                  v-model="fileItem.category_id" 
                  class="form-select"
                  :class="{ 'is-invalid': !fileItem.category_id && fileItem.showValidation }"
                  :disabled="fileItem.uploaded"
                  required
                >
                  <option value="">-- Select Document Category (Required) --</option>
                  <option v-for="category in categories" :key="category.id" :value="category.id">
                    {{ category.name }} {{ getCategoryRetention(category) }}
                  </option>
                </select>
                <div v-if="!fileItem.category_id && fileItem.showValidation" class="invalid-feedback">
                  Please select a category for compliance and retention purposes
                </div>
              </div>
              <div class="col-12">
                <input
                  v-model="fileItem.title"
                  type="text"
                  class="form-control form-control-sm"
                  placeholder="Document title (optional)"
                  :disabled="fileItem.uploaded"
                />
              </div>
              <div class="col-12">
                <textarea
                  v-model="fileItem.description"
                  class="form-control form-control-sm"
                  rows="2"
                  placeholder="Description (optional)"
                  :disabled="fileItem.uploaded"
                ></textarea>
              </div>
            </div>
          </div>
          
          <div class="file-actions">
            <div v-if="fileItem.uploading" class="file-progress">
              <div class="progress">
                <div 
                  class="progress-bar progress-bar-striped progress-bar-animated" 
                  :style="{ width: (fileItem.progress || 0) + '%' }"
                ></div>
              </div>
              <small>{{ fileItem.progress || 0 }}%</small>
            </div>
            
            <div v-else-if="fileItem.uploaded" class="file-success">
              <i class="bi bi-check-circle-fill text-success"></i>
              <small class="text-success">Uploaded</small>
            </div>
            
            <div v-else-if="fileItem.error" class="file-error-msg">
              <i class="bi bi-exclamation-circle-fill text-danger"></i>
              <small class="text-danger">{{ fileItem.error }}</small>
            </div>
            
            <div v-else class="file-pending">
              <button 
                class="btn btn-sm btn-outline-danger" 
                @click="removeFromQueue(index)"
                :disabled="uploading"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Upload Actions -->
      <div class="upload-actions mt-3">
        <button 
          class="btn btn-primary me-2"
          @click="uploadAllFiles"
          :disabled="uploading || fileQueue.length === 0 || allFilesUploaded"
        >
          <i class="bi bi-cloud-upload me-2"></i>
          Upload All Files
        </button>
        
        <button 
          class="btn btn-outline-secondary"
          @click="clearQueue"
          :disabled="uploading"
        >
          <i class="bi bi-x-circle me-2"></i>
          Clear Queue
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDocumentStore } from '../stores/documentStore.js'
import { documentService } from '../services/documentService.js'

const props = defineProps({
  clientId: {
    type: [Number, String],
    required: true
  },
  clientName: {
    type: String,
    default: 'Client'
  },
  initialFiles: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'uploaded'])

const documentStore = useDocumentStore()

// State
const fileInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')
const successMessage = ref('')
const fileQueue = ref([])
const categories = ref([])

const hasError = computed(() => !!errorMessage.value)
const allFilesUploaded = computed(() => 
  fileQueue.value.length > 0 && fileQueue.value.every(item => item.uploaded || item.error)
)

// Methods
const triggerFileInput = () => {
  if (!uploading.value) {
    fileInput.value.click()
  }
}

const handleDragEnter = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragOver = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  if (!e.currentTarget.contains(e.relatedTarget)) {
    isDragging.value = false
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  
  if (uploading.value) return
  
  const files = Array.from(e.dataTransfer.files)
  processFiles(files)
}

const handleFileInput = (e) => {
  const files = Array.from(e.target.files)
  processFiles(files)
  e.target.value = ''
}

const processFiles = (files) => {
  errorMessage.value = ''
  successMessage.value = ''
  
  const validFiles = []
  const errors = []
  
  files.forEach(file => {
    if (!documentService.isFileTypeAllowed(file)) {
      errors.push(`${file.name}: File type not allowed`)
      return
    }
    
    if (!documentService.validateFileSize(file)) {
      errors.push(`${file.name}: File size exceeds 50MB limit`)
      return
    }
    
    validFiles.push({
      file,
      category_id: '',
      title: '',
      description: '',
      uploading: false,
      uploaded: false,
      progress: 0,
      error: null,
      showValidation: false
    })
  })
  
  if (errors.length > 0) {
    errorMessage.value = errors.join(', ')
  }
  
  fileQueue.value.push(...validFiles)
  
  if (validFiles.length > 0) {
    successMessage.value = `Added ${validFiles.length} file(s) to upload queue`
  }
}

const removeFromQueue = (index) => {
  fileQueue.value.splice(index, 1)
}

const clearQueue = () => {
  fileQueue.value = []
  errorMessage.value = ''
  successMessage.value = ''
}

const uploadAllFiles = async () => {
  if (uploading.value || fileQueue.value.length === 0) return
  
  // Validate that all files have categories selected
  let hasInvalidFiles = false
  for (const fileItem of fileQueue.value) {
    if (!fileItem.uploaded && !fileItem.category_id) {
      fileItem.showValidation = true
      hasInvalidFiles = true
    }
  }
  
  if (hasInvalidFiles) {
    errorMessage.value = 'Please select a category for all documents. Categories are required for compliance and retention management.'
    return
  }
  
  uploading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  let successCount = 0
  let failedCount = 0
  
  for (const fileItem of fileQueue.value) {
    if (fileItem.uploaded || fileItem.error) continue
    
    try {
      fileItem.uploading = true
      fileItem.error = null
      
      const formData = new FormData()
      formData.append('file', fileItem.file)
      formData.append('client_id', props.clientId)
      
      if (fileItem.category_id) {
        formData.append('category_id', fileItem.category_id)
      }
      
      if (fileItem.title) {
        formData.append('title', fileItem.title)
      }
      
      if (fileItem.description) {
        formData.append('description', fileItem.description)
      }
      
      const progressCallback = (progress) => {
        fileItem.progress = progress
        const totalProgress = fileQueue.value.reduce((sum, item) => {
          if (item.uploaded) return sum + 100
          if (item.uploading) return sum + (item.progress || 0)
          return sum
        }, 0) / fileQueue.value.length
        uploadProgress.value = Math.round(totalProgress)
      }
      
      await documentService.uploadDocument(formData, progressCallback)
      
      fileItem.uploaded = true
      fileItem.uploading = false
      fileItem.progress = 100
      successCount++
      
    } catch (error) {
      fileItem.error = error.response?.data?.message || 'Upload failed'
      fileItem.uploading = false
      failedCount++
      console.error('Upload error:', error)
    }
  }
  
  uploading.value = false
  uploadProgress.value = 0
  
  if (successCount > 0) {
    successMessage.value = `Successfully uploaded ${successCount} file(s)`
    emit('uploaded')
  }
  
  if (failedCount > 0) {
    errorMessage.value = `Failed to upload ${failedCount} file(s)`
  }
}

const loadCategories = async () => {
  try {
    categories.value = await documentService.getCategories()
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const getFileIcon = (contentType) => {
  return documentService.getFileIcon(contentType)
}

const formatFileSize = (bytes) => {
  return documentService.formatFileSize(bytes)
}

const getCategoryRetention = (category) => {
  // Display the actual retention years from the category
  if (category.default_retention_years) {
    return `(${category.default_retention_years} years)`
  }
  return ''
}

// Lifecycle
onMounted(async () => {
  await loadCategories()
  
  // If initial files were provided, add them to the queue
  if (props.initialFiles && props.initialFiles.length > 0) {
    processFiles(props.initialFiles)
  }
  
  // Listen for files dropped from parent
  const handleDroppedFiles = (event) => {
    if (event.detail && event.detail.files && event.detail.clientId === props.clientId) {
      processFiles(event.detail.files)
    }
  }
  
  window.addEventListener('client-files-dropped', handleDroppedFiles)
  
  onUnmounted(() => {
    window.removeEventListener('client-files-dropped', handleDroppedFiles)
  })
})
</script>

<style scoped>
.upload-area {
  border: 3px dashed #007bff;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #f0f8ff 0%, #e7f3ff 100%);
  position: relative;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #0056b3;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.1);
}

.upload-area.upload-dragging {
  border-color: #0056b3;
  border-width: 4px;
  background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%);
  transform: scale(1.02);
  box-shadow: 0 8px 25px rgba(0, 123, 255, 0.2);
}

.upload-area.upload-disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.upload-area.upload-error {
  border-color: #dc3545;
  background: #fff5f5;
}

.upload-content {
  width: 100%;
}

.upload-progress .spinner-border {
  width: 3rem;
  height: 3rem;
}

.file-queue {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.file-list {
  max-height: 400px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  background: #fff;
  gap: 1rem;
  flex-wrap: wrap;
}

.file-item.file-error {
  border-color: #dc3545;
  background: #fff5f5;
}

.file-item.file-success {
  border-color: #28a745;
  background: #f0fff4;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 0 0 auto;
  min-width: 200px;
}

.file-icon i {
  font-size: 1.5rem;
}

.file-details {
  min-width: 0;
}

.file-name {
  font-weight: 500;
  font-size: 0.9rem;
  word-break: break-all;
}

.file-size {
  font-size: 0.8rem;
  color: #6c757d;
}

.file-metadata {
  flex: 1 1 300px;
  min-width: 300px;
}

.file-actions {
  flex: 0 0 auto;
  min-width: 120px;
  text-align: center;
}

.file-progress {
  width: 100px;
}

.file-progress .progress {
  height: 4px;
  margin-bottom: 2px;
}

.file-success,
.file-error-msg,
.file-pending {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.upload-actions {
  text-align: center;
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

@media (max-width: 768px) {
  .upload-area {
    padding: 1.5rem 1rem;
    min-height: 150px;
  }
  
  .file-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .file-info {
    justify-content: flex-start;
  }
  
  .file-metadata {
    min-width: 100%;
  }
  
  .file-actions {
    min-width: 100%;
  }
}

/* Category Selection Styling */
.file-metadata .form-label {
  font-weight: 600;
  font-size: 0.875rem;
}

.file-metadata select.form-select {
  border: 2px solid #dee2e6;
  background-color: #fffbf0;
  font-weight: 500;
}

.file-metadata select.form-select:focus {
  border-color: #ffc107;
  box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.25);
}

.file-metadata select.is-invalid {
  border-color: #dc3545;
  background-color: #fff5f5;
}

.file-metadata .invalid-feedback {
  font-size: 0.8rem;
  margin-top: 0.25rem;
}
</style>