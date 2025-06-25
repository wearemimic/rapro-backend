<template>
  <div class="image-dropzone">
    <div 
      class="dropzone-container" 
      :class="{ 'drag-over': isDragging, 'has-image': hasPreview }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="triggerFileSelect"
    >
      <div v-if="hasPreview" class="image-preview">
        <img :src="previewUrl" alt="Preview" class="preview-image">
        <button type="button" class="btn btn-sm btn-danger remove-btn" @click.stop="removeImage">
          <i class="bi-x"></i>
        </button>
      </div>
      <div v-else class="dropzone-content">
        <i class="bi-cloud-arrow-up-fill dropzone-icon"></i>
        <p class="dropzone-text">Drag and drop your logo here or click to browse</p>
        <p class="dropzone-subtext">Accepted formats: JPG, PNG, GIF. Max size: 2MB</p>
      </div>
    </div>
    <input 
      type="file" 
      ref="fileInput" 
      class="file-input"
      accept="image/*"
      @change="onFileSelect"
    >
    <div v-if="errorMessage" class="dropzone-error mt-2">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits, defineProps, watch } from 'vue'

const props = defineProps({
  value: {
    type: [File, String, null],
    default: null
  },
  existingImageUrl: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:value', 'fileChanged'])

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const errorMessage = ref('')

const hasPreview = computed(() => {
  return !!previewUrl.value
})

const previewUrl = computed(() => {
  if (selectedFile.value) {
    return URL.createObjectURL(selectedFile.value)
  } else if (props.existingImageUrl) {
    // Handle existing image URL
    if (props.existingImageUrl.startsWith('http')) {
      return props.existingImageUrl
    } else {
      // Prepend API URL for relative paths
      return `http://localhost:8000${props.existingImageUrl}`
    }
  }
  return null
})

// Watch for external value changes
watch(() => props.value, (newValue) => {
  if (newValue instanceof File) {
    selectedFile.value = newValue
  } else if (newValue === null) {
    selectedFile.value = null
  }
})

const triggerFileSelect = () => {
  fileInput.value.click()
}

const onFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const onDragOver = (event) => {
  isDragging.value = true
  event.dataTransfer.dropEffect = 'copy'
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file) => {
  errorMessage.value = ''
  
  // Validate file type
  const validTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!validTypes.includes(file.type)) {
    errorMessage.value = 'Please select a valid image file (JPG, PNG, GIF)'
    return
  }
  
  // Validate file size (2MB limit)
  const maxSize = 2 * 1024 * 1024 // 2MB in bytes
  if (file.size > maxSize) {
    errorMessage.value = 'File size exceeds 2MB limit'
    return
  }
  
  selectedFile.value = file
  emit('update:value', file)
  emit('fileChanged', file)
}

const removeImage = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('update:value', null)
  emit('fileChanged', null)
}
</script>

<style scoped>
.image-dropzone {
  width: 100%;
}

.dropzone-container {
  width: 100%;
  height: 180px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.dropzone-container:hover {
  border-color: #377dff;
  background-color: rgba(55, 125, 255, 0.05);
}

.drag-over {
  border-color: #377dff;
  background-color: rgba(55, 125, 255, 0.1);
}

.has-image {
  border-style: solid;
}

.dropzone-content {
  text-align: center;
  padding: 20px;
}

.dropzone-icon {
  font-size: 40px;
  color: #377dff;
  margin-bottom: 10px;
}

.dropzone-text {
  margin: 0;
  color: #495057;
  font-size: 16px;
  font-weight: 500;
}

.dropzone-subtext {
  margin: 5px 0 0;
  color: #6c757d;
  font-size: 13px;
}

.file-input {
  position: absolute;
  width: 0;
  height: 0;
  overflow: hidden;
  opacity: 0;
}

.image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.remove-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(220, 53, 69, 0.9);
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background-color: #dc3545;
}

.dropzone-error {
  color: #dc3545;
  font-size: 13px;
}
</style> 