<template>
  <div class="document-list">
    <!-- List Header -->
    <div class="list-header">
      <div class="row align-items-center">
        <div class="col-md-6">
          <h6 class="mb-0">
            <i class="bi bi-files me-2"></i>
            Documents 
            <span class="text-muted">
              ({{ documents.length }}{{ selectedDocuments.length > 0 ? `, ${selectedDocuments.length} selected` : '' }})
            </span>
          </h6>
        </div>
        
        <div class="col-md-6 text-end">
          <!-- View Toggle -->
          <div class="btn-group me-3" role="group">
            <input 
              type="radio" 
              class="btn-check" 
              id="grid-view" 
              v-model="viewMode" 
              value="grid"
            />
            <label class="btn btn-outline-secondary btn-sm" for="grid-view">
              <i class="bi bi-grid"></i>
            </label>
            
            <input 
              type="radio" 
              class="btn-check" 
              id="list-view" 
              v-model="viewMode" 
              value="list"
            />
            <label class="btn btn-outline-secondary btn-sm" for="list-view">
              <i class="bi bi-list-ul"></i>
            </label>
          </div>
          
          <!-- Bulk Actions -->
          <div v-if="selectedDocuments.length > 0" class="btn-group">
            <button 
              class="btn btn-sm btn-outline-primary dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
            >
              Actions ({{ selectedDocuments.length }})
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <button class="dropdown-item" @click="downloadSelected">
                  <i class="bi bi-download me-2"></i>Download Selected
                </button>
              </li>
              <li>
                <button class="dropdown-item" @click="shareSelected">
                  <i class="bi bi-share me-2"></i>Share Selected
                </button>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <button class="dropdown-item" @click="archiveSelected">
                  <i class="bi bi-archive me-2"></i>Archive Selected
                </button>
              </li>
              <li>
                <button class="dropdown-item text-danger" @click="deleteSelected">
                  <i class="bi bi-trash me-2"></i>Delete Selected
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2">Loading documents...</p>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="documents.length === 0" class="empty-state text-center py-5">
      <div class="mb-4">
        <i class="bi bi-files" style="font-size: 4rem; color: #dee2e6;"></i>
      </div>
      <h5 class="text-muted">No Documents Found</h5>
      <p class="text-muted">
        {{ hasActiveFilters ? 'No documents match your current filters.' : 'Upload your first document to get started.' }}
      </p>
      <button v-if="!hasActiveFilters" class="btn btn-primary" @click="$emit('upload')">
        <i class="bi bi-cloud-upload me-2"></i>Upload Documents
      </button>
    </div>
    
    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="document-grid">
      <div class="row">
        <div 
          v-for="document in documents" 
          :key="document.id" 
          class="col-xl-3 col-lg-4 col-md-6 mb-4"
        >
          <div 
            class="document-card card h-100"
            :class="{ 
              'selected': selectedDocuments.includes(document.id),
              'quarantined': document.status === 'quarantined'
            }"
            @click="toggleSelection(document.id)"
          >
            <!-- Card Header -->
            <div class="card-header d-flex justify-content-between align-items-center">
              <div class="form-check">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  :checked="selectedDocuments.includes(document.id)"
                  @click.stop
                  @change="toggleSelection(document.id)"
                />
              </div>
              
              <div class="dropdown">
                <button 
                  class="btn btn-sm btn-outline-secondary"
                  type="button"
                  data-bs-toggle="dropdown"
                  @click.stop
                >
                  <i class="bi bi-three-dots"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li>
                    <button class="dropdown-item" @click.stop="viewDocument(document)">
                      <i class="bi bi-eye me-2"></i>View
                    </button>
                  </li>
                  <li>
                    <button class="dropdown-item" @click.stop="downloadDocument(document)">
                      <i class="bi bi-download me-2"></i>Download
                    </button>
                  </li>
                  <li>
                    <button class="dropdown-item" @click.stop="shareDocument(document)">
                      <i class="bi bi-share me-2"></i>Share
                    </button>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <button class="dropdown-item" @click.stop="editDocument(document)">
                      <i class="bi bi-pencil me-2"></i>Edit
                    </button>
                  </li>
                  <li>
                    <button class="dropdown-item" @click.stop="duplicateDocument(document)">
                      <i class="bi bi-files me-2"></i>Duplicate
                    </button>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <button class="dropdown-item text-warning" @click.stop="archiveDocument(document)">
                      <i class="bi bi-archive me-2"></i>Archive
                    </button>
                  </li>
                  <li>
                    <button class="dropdown-item text-danger" @click.stop="deleteDocument(document)">
                      <i class="bi bi-trash me-2"></i>Delete
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            
            <!-- Card Body -->
            <div class="card-body">
              <div class="document-icon text-center mb-3">
                <i :class="getFileIcon(document.content_type)" style="font-size: 2.5rem;"></i>
              </div>
              
              <h6 class="card-title text-center mb-2" :title="document.name">
                {{ truncateText(document.name, 25) }}
              </h6>
              
              <div class="document-meta">
                <small class="text-muted d-block">
                  <i class="bi bi-calendar me-1"></i>
                  {{ formatDate(document.created_at) }}
                </small>
                
                <small class="text-muted d-block">
                  <i class="bi bi-hdd me-1"></i>
                  {{ formatFileSize(document.file_size) }}
                </small>
                
                <small v-if="document.category" class="text-muted d-block">
                  <i class="bi bi-tag me-1"></i>
                  {{ document.category.name }}
                </small>
                
                <small v-if="document.client" class="text-muted d-block">
                  <i class="bi bi-person me-1"></i>
                  {{ document.client.first_name }} {{ document.client.last_name }}
                </small>
              </div>
            </div>
            
            <!-- Card Footer -->
            <div class="card-footer">
              <div class="d-flex justify-content-between align-items-center">
                <span :class="getStatusBadgeClass(document.status)">
                  {{ getStatusDisplay(document.status) }}
                </span>
                
                <div class="document-actions">
                  <button 
                    class="btn btn-sm btn-outline-primary me-1" 
                    @click.stop="viewDocument(document)"
                    :title="'View ' + document.name"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  
                  <button 
                    class="btn btn-sm btn-outline-secondary" 
                    @click.stop="downloadDocument(document)"
                    :title="'Download ' + document.name"
                  >
                    <i class="bi bi-download"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- List View -->
    <div v-else class="document-table">
      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th style="width: 40px;">
                <input 
                  type="checkbox" 
                  class="form-check-input"
                  :checked="allSelected"
                  :indeterminate="someSelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th @click="sort('name')" class="sortable">
                <i class="bi bi-file-text me-2"></i>Name
                <i v-if="sortField === 'name'" :class="sortDirection === 'asc' ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'"></i>
              </th>
              <th @click="sort('category')" class="sortable">
                <i class="bi bi-tag me-2"></i>Category
                <i v-if="sortField === 'category'" :class="sortDirection === 'asc' ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'"></i>
              </th>
              <th @click="sort('client')" class="sortable">
                <i class="bi bi-person me-2"></i>Client
                <i v-if="sortField === 'client'" :class="sortDirection === 'asc' ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'"></i>
              </th>
              <th @click="sort('file_size')" class="sortable">
                <i class="bi bi-hdd me-2"></i>Size
                <i v-if="sortField === 'file_size'" :class="sortDirection === 'asc' ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'"></i>
              </th>
              <th @click="sort('status')" class="sortable">
                <i class="bi bi-info-circle me-2"></i>Status
                <i v-if="sortField === 'status'" :class="sortDirection === 'asc' ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'"></i>
              </th>
              <th @click="sort('created_at')" class="sortable">
                <i class="bi bi-calendar me-2"></i>Created
                <i v-if="sortField === 'created_at'" :class="sortDirection === 'asc' ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'"></i>
              </th>
              <th style="width: 120px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="document in documents" 
              :key="document.id"
              :class="{ 
                'table-active': selectedDocuments.includes(document.id),
                'table-warning': document.status === 'quarantined'
              }"
              @click="toggleSelection(document.id)"
              style="cursor: pointer;"
            >
              <td @click.stop>
                <input 
                  type="checkbox" 
                  class="form-check-input"
                  :checked="selectedDocuments.includes(document.id)"
                  @change="toggleSelection(document.id)"
                />
              </td>
              
              <td>
                <div class="d-flex align-items-center">
                  <i :class="getFileIcon(document.content_type)" class="me-2"></i>
                  <div>
                    <div class="fw-medium">{{ truncateText(document.name, 40) }}</div>
                    <small class="text-muted">{{ document.content_type }}</small>
                  </div>
                </div>
              </td>
              
              <td>
                <span v-if="document.category" class="badge bg-secondary">
                  {{ document.category.name }}
                </span>
                <span v-else class="text-muted">—</span>
              </td>
              
              <td>
                <div v-if="document.client">
                  <div class="fw-medium">{{ document.client.first_name }} {{ document.client.last_name }}</div>
                  <small class="text-muted">{{ document.client.email }}</small>
                </div>
                <span v-else class="text-muted">All Clients</span>
              </td>
              
              <td>{{ formatFileSize(document.file_size) }}</td>
              
              <td>
                <span :class="getStatusBadgeClass(document.status)">
                  {{ getStatusDisplay(document.status) }}
                </span>
              </td>
              
              <td>
                <div>
                  <div class="fw-medium">{{ formatDate(document.created_at) }}</div>
                  <small class="text-muted">{{ formatTime(document.created_at) }}</small>
                </div>
              </td>
              
              <td @click.stop>
                <div class="btn-group">
                  <button 
                    class="btn btn-sm btn-outline-primary" 
                    @click="viewDocument(document)"
                    :title="'View ' + document.name"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  
                  <button 
                    class="btn btn-sm btn-outline-secondary" 
                    @click="downloadDocument(document)"
                    :title="'Download ' + document.name"
                  >
                    <i class="bi bi-download"></i>
                  </button>
                  
                  <div class="dropdown">
                    <button 
                      class="btn btn-sm btn-outline-secondary dropdown-toggle"
                      type="button"
                      data-bs-toggle="dropdown"
                    >
                      <i class="bi bi-three-dots"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                      <li>
                        <button class="dropdown-item" @click="shareDocument(document)">
                          <i class="bi bi-share me-2"></i>Share
                        </button>
                      </li>
                      <li>
                        <button class="dropdown-item" @click="editDocument(document)">
                          <i class="bi bi-pencil me-2"></i>Edit
                        </button>
                      </li>
                      <li>
                        <button class="dropdown-item" @click="duplicateDocument(document)">
                          <i class="bi bi-files me-2"></i>Duplicate
                        </button>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <button class="dropdown-item text-warning" @click="archiveDocument(document)">
                          <i class="bi bi-archive me-2"></i>Archive
                        </button>
                      </li>
                      <li>
                        <button class="dropdown-item text-danger" @click="deleteDocument(document)">
                          <i class="bi bi-trash me-2"></i>Delete
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useDocumentStore } from '../stores/documentStore.js'
import { documentService } from '../services/documentService.js'

const props = defineProps({
  documents: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  hasActiveFilters: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['upload', 'view', 'download', 'share', 'edit', 'delete', 'archive'])

const documentStore = useDocumentStore()

const viewMode = ref('grid')
const selectedDocuments = ref([])
const sortField = ref('created_at')
const sortDirection = ref('desc')

const allSelected = computed(() => 
  props.documents.length > 0 && selectedDocuments.value.length === props.documents.length
)

const someSelected = computed(() => 
  selectedDocuments.value.length > 0 && selectedDocuments.value.length < props.documents.length
)

onMounted(() => {
  const savedViewMode = localStorage.getItem('documentListViewMode')
  if (savedViewMode) {
    viewMode.value = savedViewMode
  }
})

watch(viewMode, (newMode) => {
  localStorage.setItem('documentListViewMode', newMode)
})

function toggleSelection(documentId) {
  const index = selectedDocuments.value.indexOf(documentId)
  if (index > -1) {
    selectedDocuments.value.splice(index, 1)
  } else {
    selectedDocuments.value.push(documentId)
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedDocuments.value = []
  } else {
    selectedDocuments.value = props.documents.map(doc => doc.id)
  }
}

function sort(field) {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

function viewDocument(document) {
  emit('view', document)
}

function downloadDocument(document) {
  emit('download', document)
}

function shareDocument(document) {
  emit('share', document)
}

function editDocument(document) {
  emit('edit', document)
}

function archiveDocument(document) {
  emit('archive', document)
}

function deleteDocument(document) {
  emit('delete', document)
}

function duplicateDocument(document) {
  console.log('Duplicate document:', document)
}

async function downloadSelected() {
  for (const documentId of selectedDocuments.value) {
    const document = props.documents.find(d => d.id === documentId)
    if (document) {
      await downloadDocument(document)
    }
  }
}

function shareSelected() {
  const documents = props.documents.filter(d => selectedDocuments.value.includes(d.id))
  console.log('Share selected documents:', documents)
}

function archiveSelected() {
  const documents = props.documents.filter(d => selectedDocuments.value.includes(d.id))
  console.log('Archive selected documents:', documents)
}

function deleteSelected() {
  const documents = props.documents.filter(d => selectedDocuments.value.includes(d.id))
  console.log('Delete selected documents:', documents)
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

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString()
}

function formatTime(dateString) {
  return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function truncateText(text, maxLength) {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}
</script>

<style scoped>
.list-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.document-grid .document-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.document-grid .document-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.document-grid .document-card.selected {
  border-color: #007bff;
  background: #f8f9fa;
}

.document-grid .document-card.quarantined {
  border-color: #ffc107;
  background: #fff9e6;
}

.document-card .card-header {
  background: transparent;
  border-bottom: 1px solid #dee2e6;
  padding: 0.75rem;
}

.document-card .card-body {
  padding: 1rem 0.75rem;
}

.document-card .card-footer {
  background: transparent;
  border-top: 1px solid #dee2e6;
  padding: 0.75rem;
}

.document-meta {
  font-size: 0.875rem;
}

.document-meta small {
  margin-bottom: 0.25rem;
}

.document-table .sortable {
  cursor: pointer;
  user-select: none;
}

.document-table .sortable:hover {
  background-color: #f8f9fa;
}

.empty-state {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.table-responsive {
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.table th {
  border-top: none;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 1rem 0.75rem;
}

.table td {
  padding: 1rem 0.75rem;
  vertical-align: middle;
}

@media (max-width: 768px) {
  .list-header .col-md-6 {
    margin-bottom: 1rem;
  }
  
  .list-header .text-end {
    text-align: left !important;
  }
  
  .document-grid .col-xl-3,
  .document-grid .col-lg-4,
  .document-grid .col-md-6 {
    width: 100%;
    max-width: none;
  }
}
</style>