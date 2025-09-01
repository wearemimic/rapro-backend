<template>
  <div class="tax-data-management">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 admin-page-header">
      <div>
        <h3 class="mb-1">Tax Data Management</h3>
        <p class="text-muted mb-0">Manage tax CSV files, upload updates, and maintain backups</p>
      </div>
      <div>
        <button 
          class="btn btn-primary me-2" 
          @click="showUploadModal = true"
          :disabled="loading"
        >
          <i class="bi bi-cloud-upload me-2"></i>
          Upload Tax File
        </button>
        <button 
          class="btn btn-outline-secondary" 
          @click="loadTaxDataFiles"
          :disabled="loading"
        >
          <i class="bi bi-arrow-clockwise me-2"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">Total Files</h6>
                <h4 class="text-primary mb-0">{{ taxDataSummary.totalFiles }}</h4>
              </div>
              <div class="text-primary">
                <i class="bi bi-file-earmark-text fs-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">Current Tax Year</h6>
                <h4 class="text-info mb-0">{{ taxDataSummary.currentTaxYear }}</h4>
              </div>
              <div class="text-info">
                <i class="bi bi-calendar4-range fs-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">File Types</h6>
                <h4 class="text-success mb-0">{{ taxDataSummary.fileTypes }}</h4>
              </div>
              <div class="text-success">
                <i class="bi bi-collection fs-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">Backups</h6>
                <h4 class="text-warning mb-0">{{ backupsSummary.totalBackups }}</h4>
              </div>
              <div class="text-warning">
                <i class="bi bi-shield-check fs-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4" id="taxDataTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link"
          :class="{ active: activeTab === 'files' }"
          @click="activeTab = 'files'"
          type="button"
        >
          <i class="bi bi-files me-2"></i>
          Tax Data Files
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link"
          :class="{ active: activeTab === 'backups' }"
          @click="activeTab = 'backups'"
          type="button"
        >
          <i class="bi bi-archive me-2"></i>
          Backups
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link"
          :class="{ active: activeTab === 'validation' }"
          @click="activeTab = 'validation'"
          type="button"
        >
          <i class="bi bi-check-circle me-2"></i>
          Validation Rules
        </button>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content">
      
      <!-- Tax Data Files Tab -->
      <div v-if="activeTab === 'files'" class="tab-pane active">
        <!-- Year Filter -->
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div class="d-flex align-items-center">
            <label class="form-label me-3 mb-0">Filter by Year:</label>
            <select v-model="selectedYear" class="form-select" style="width: auto;">
              <option value="">All Years</option>
              <option v-for="year in availableYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>
          <div class="text-muted small">
            {{ filteredTaxFiles.length }} of {{ taxDataFiles.length }} files
          </div>
        </div>

        <!-- Files Table -->
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="filteredTaxFiles.length === 0" class="text-center py-4">
              <i class="bi bi-folder2-open text-muted fs-1 mb-3"></i>
              <p class="text-muted mb-0">No tax data files found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>File Name</th>
                    <th>Type</th>
                    <th>Tax Year</th>
                    <th>Size</th>
                    <th>Last Modified</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="file in filteredTaxFiles" :key="file.filename">
                    <td>
                      <div class="d-flex align-items-center">
                        <i class="bi bi-file-earmark-spreadsheet text-success me-2"></i>
                        <span class="fw-medium">{{ file.filename }}</span>
                      </div>
                    </td>
                    <td>
                      <span class="badge bg-primary">{{ file.file_type }}</span>
                    </td>
                    <td>
                      <span v-if="file.tax_year" class="badge bg-info">{{ file.tax_year }}</span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td>{{ file.size_display }}</td>
                    <td>
                      <span class="text-muted small">
                        {{ formatDate(file.modified_at) }}
                      </span>
                    </td>
                    <td>
                      <span class="badge bg-success" v-if="file.is_active">Active</span>
                      <span class="badge bg-secondary" v-else>Inactive</span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          class="btn btn-outline-primary"
                          @click="viewFileContent(file.filename)"
                          title="View Content"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button 
                          class="btn btn-outline-secondary"
                          @click="editFile(file.filename)"
                          title="Edit File"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          class="btn btn-outline-warning"
                          @click="downloadFile(file.filename)"
                          title="Download"
                        >
                          <i class="bi bi-download"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Backups Tab -->
      <div v-if="activeTab === 'backups'" class="tab-pane active">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div v-if="loadingBackups" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading backups...</span>
              </div>
            </div>
            
            <div v-else-if="backups.length === 0" class="text-center py-4">
              <i class="bi bi-archive text-muted fs-1 mb-3"></i>
              <p class="text-muted mb-0">No backup files found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Backup File</th>
                    <th>Original File</th>
                    <th>Backup Date</th>
                    <th>Size</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="backup in backups" :key="backup.backup_filename">
                    <td>
                      <div class="d-flex align-items-center">
                        <i class="bi bi-archive-fill text-warning me-2"></i>
                        <span class="fw-medium">{{ backup.backup_filename }}</span>
                      </div>
                    </td>
                    <td>{{ backup.original_filename || 'Unknown' }}</td>
                    <td>
                      <span class="text-muted small">
                        {{ backup.backup_timestamp ? formatDate(backup.backup_timestamp) : 'Unknown' }}
                      </span>
                    </td>
                    <td>{{ backup.size_display }}</td>
                    <td>
                      <button 
                        class="btn btn-outline-success btn-sm"
                        @click="restoreBackup(backup)"
                        title="Restore from backup"
                      >
                        <i class="bi bi-arrow-counterclockwise me-1"></i>
                        Restore
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Validation Rules Tab -->
      <div v-if="activeTab === 'validation'" class="tab-pane active">
        <div class="row">
          <div class="col-md-4">
            <div class="card border-0 shadow-sm">
              <div class="card-body">
                <h6 class="card-title">File Types</h6>
                <div class="list-group list-group-flush">
                  <button 
                    v-for="fileType in availableFileTypes" 
                    :key="fileType"
                    class="list-group-item list-group-item-action"
                    :class="{ active: selectedFileType === fileType }"
                    @click="selectedFileType = fileType"
                  >
                    {{ fileType }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-8">
            <div class="card border-0 shadow-sm">
              <div class="card-body">
                <h6 class="card-title">
                  Validation Rules for: 
                  <span class="text-primary">{{ selectedFileType }}</span>
                </h6>
                
                <div v-if="selectedValidationRules">
                  <h6 class="mt-3">Required Headers:</h6>
                  <div class="row">
                    <div class="col-md-6">
                      <ul class="list-unstyled">
                        <li v-for="header in selectedValidationRules.required_headers" :key="header">
                          <i class="bi bi-check-circle text-success me-2"></i>
                          <code>{{ header }}</code>
                          <span class="text-muted ms-2">({{ selectedValidationRules.header_types[header] }})</span>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <h6 class="mt-3">Validation Checks:</h6>
                  <ul class="list-unstyled">
                    <li v-for="check in selectedValidationRules.validation_checks" :key="check" class="mb-2">
                      <i class="bi bi-info-circle text-info me-2"></i>
                      {{ check }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div class="modal fade" id="uploadModal" tabindex="-1" v-if="showUploadModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Upload Tax Data File</h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="showUploadModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="uploadTaxFile">
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">File Type</label>
                  <select v-model="uploadForm.file_type" class="form-select" required>
                    <option value="">Select file type</option>
                    <option v-for="type in availableFileTypes" :key="type" :value="type">
                      {{ type }}
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Tax Year</label>
                  <select v-model="uploadForm.tax_year" class="form-select" required>
                    <option value="">Select tax year</option>
                    <option v-for="year in [2024, 2025, 2026, 2027, 2028]" :key="year" :value="year">
                      {{ year }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">CSV File</label>
                <input 
                  type="file" 
                  class="form-control"
                  accept=".csv"
                  @change="handleFileSelect"
                  required
                >
                <div class="form-text">
                  Only CSV files are accepted. The file will be validated before upload.
                </div>
              </div>

              <div class="mb-3">
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    v-model="uploadForm.create_backup"
                    id="createBackup"
                  >
                  <label class="form-check-label" for="createBackup">
                    Create backup of existing file (recommended)
                  </label>
                </div>
              </div>

              <!-- File Preview -->
              <div v-if="uploadPreview" class="border rounded p-3 mb-3">
                <h6>File Preview:</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p class="mb-1"><strong>Filename:</strong> {{ uploadPreview.name }}</p>
                    <p class="mb-1"><strong>Size:</strong> {{ (uploadPreview.size / 1024).toFixed(1) }} KB</p>
                  </div>
                  <div class="col-md-6">
                    <p class="mb-1"><strong>Type:</strong> {{ uploadPreview.type }}</p>
                    <p class="mb-1"><strong>Last Modified:</strong> {{ formatDate(uploadPreview.lastModified) }}</p>
                  </div>
                </div>
              </div>

              <!-- Validation Results -->
              <div v-if="validationResults" class="border rounded p-3 mb-3">
                <div v-if="validationResults.is_valid" class="alert alert-success">
                  <i class="bi bi-check-circle me-2"></i>
                  File validation passed! Ready to upload.
                </div>
                <div v-else class="alert alert-danger">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  File validation failed. Please fix the errors below:
                  <ul class="mt-2 mb-0">
                    <li v-for="error in validationResults.errors" :key="error">{{ error }}</li>
                  </ul>
                </div>
                <div v-if="validationResults.warnings && validationResults.warnings.length > 0">
                  <div class="alert alert-warning mt-2">
                    <i class="bi bi-info-circle me-2"></i>
                    Warnings:
                    <ul class="mt-2 mb-0">
                      <li v-for="warning in validationResults.warnings" :key="warning">{{ warning }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="showUploadModal = false"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="uploadTaxFile"
              :disabled="!validationResults || !validationResults.is_valid || uploading"
            >
              <div v-if="uploading" class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Uploading...</span>
              </div>
              Upload File
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- File Content Modal -->
    <div class="modal fade" id="fileContentModal" tabindex="-1" v-if="showFileContentModal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedFile?.filename }}</h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="showFileContentModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingFileContent" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading file content...</span>
              </div>
            </div>
            
            <div v-else-if="fileContent">
              <!-- File Metadata -->
              <div class="row mb-3">
                <div class="col-md-3">
                  <p class="mb-1"><strong>File Type:</strong> {{ fileContent.file_type }}</p>
                  <p class="mb-1"><strong>Tax Year:</strong> {{ fileContent.tax_year || 'Unknown' }}</p>
                </div>
                <div class="col-md-3">
                  <p class="mb-1"><strong>Rows:</strong> {{ fileContent.file_metadata.row_count }}</p>
                  <p class="mb-1"><strong>Columns:</strong> {{ fileContent.file_metadata.column_count }}</p>
                </div>
                <div class="col-md-6">
                  <p class="mb-1"><strong>Size:</strong> {{ (fileContent.file_metadata.size_bytes / 1024).toFixed(1) }} KB</p>
                  <p class="mb-1"><strong>Modified:</strong> {{ formatDate(fileContent.file_metadata.modified_at) }}</p>
                </div>
              </div>

              <!-- Data Table -->
              <div class="table-responsive" style="max-height: 400px;">
                <table class="table table-sm table-striped">
                  <thead class="table-dark">
                    <tr>
                      <th v-for="header in fileContent.headers" :key="header">
                        {{ header }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in fileContent.data.slice(0, 100)" :key="index">
                      <td v-for="header in fileContent.headers" :key="header">
                        {{ row[header] }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div v-if="fileContent.data.length > 100" class="text-muted mt-2">
                Showing first 100 rows of {{ fileContent.data.length }} total rows.
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="showFileContentModal = false"
            >
              Close
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="editFile(selectedFile.filename)"
              v-if="selectedFile"
            >
              <i class="bi bi-pencil me-2"></i>
              Edit File
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, watch } from 'vue';
import api from '@/services/api.js';

export default {
  name: 'AdminTaxData',
  setup() {
    // Reactive data
    const loading = ref(false);
    const loadingBackups = ref(false);
    const loadingFileContent = ref(false);
    const uploading = ref(false);
    
    const activeTab = ref('files');
    const selectedYear = ref('');
    const selectedFileType = ref('federal');
    
    const taxDataFiles = ref([]);
    const backups = ref([]);
    const validationRules = ref({});
    const fileContent = ref(null);
    const selectedFile = ref(null);
    
    const showUploadModal = ref(false);
    const showFileContentModal = ref(false);
    
    const uploadForm = reactive({
      file_type: '',
      tax_year: '',
      create_backup: true
    });
    
    const uploadPreview = ref(null);
    const validationResults = ref(null);
    const selectedCsvFile = ref(null);

    // Computed properties
    const taxDataSummary = computed(() => ({
      totalFiles: taxDataFiles.value.length,
      currentTaxYear: new Date().getFullYear(),
      fileTypes: new Set(taxDataFiles.value.map(f => f.file_type)).size
    }));

    const backupsSummary = computed(() => ({
      totalBackups: backups.value.length
    }));

    const filteredTaxFiles = computed(() => {
      if (!selectedYear.value) return taxDataFiles.value;
      return taxDataFiles.value.filter(file => 
        file.tax_year === parseInt(selectedYear.value)
      );
    });

    const availableYears = computed(() => {
      const years = [...new Set(taxDataFiles.value
        .filter(f => f.tax_year)
        .map(f => f.tax_year)
      )];
      return years.sort((a, b) => b - a);
    });

    const availableFileTypes = computed(() => {
      return Object.keys(validationRules.value.validation_rules || {});
    });

    const selectedValidationRules = computed(() => {
      return validationRules.value.validation_rules?.[selectedFileType.value] || null;
    });

    // Methods
    const loadTaxDataFiles = async () => {
      try {
        loading.value = true;
        const response = await api.get('/admin/tax-data/files/');
        taxDataFiles.value = response.data.tax_data_files || [];
      } catch (error) {
        console.error('Error loading tax data files:', error);
        // Show error notification
      } finally {
        loading.value = false;
      }
    };

    const loadBackups = async () => {
      try {
        loadingBackups.value = true;
        const response = await api.get('/admin/tax-data/backups/');
        backups.value = response.data.backups || [];
      } catch (error) {
        console.error('Error loading backups:', error);
      } finally {
        loadingBackups.value = false;
      }
    };

    const loadValidationRules = async () => {
      try {
        const response = await api.get('/admin/tax-data/validation-rules/');
        validationRules.value = response.data;
      } catch (error) {
        console.error('Error loading validation rules:', error);
      }
    };

    const viewFileContent = async (filename) => {
      try {
        loadingFileContent.value = true;
        selectedFile.value = taxDataFiles.value.find(f => f.filename === filename);
        showFileContentModal.value = true;
        
        const response = await api.get(`/admin/tax-data/files/${filename}/`);
        fileContent.value = response.data;
      } catch (error) {
        console.error('Error loading file content:', error);
      } finally {
        loadingFileContent.value = false;
      }
    };

    const editFile = (filename) => {
      // Navigate to edit view or show edit modal
      // For now, just log
      console.log('Edit file:', filename);
    };

    const downloadFile = (filename) => {
      // Create download link
      const link = document.createElement('a');
      link.href = `/api/admin/tax-data/files/${filename}/`;
      link.download = filename;
      link.click();
    };

    const handleFileSelect = (event) => {
      const file = event.target.files[0];
      if (file) {
        selectedCsvFile.value = file;
        uploadPreview.value = {
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: new Date(file.lastModified)
        };
        
        // Auto-validate when file is selected
        if (uploadForm.file_type) {
          validateUploadFile();
        }
      }
    };

    const validateUploadFile = async () => {
      if (!selectedCsvFile.value || !uploadForm.file_type) return;
      
      try {
        const reader = new FileReader();
        reader.onload = async (e) => {
          const csvContent = e.target.result;
          const lines = csvContent.split('\n');
          const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
          
          const data = [];
          for (let i = 1; i < lines.length && i < 11; i++) { // Sample first 10 rows
            if (lines[i].trim()) {
              const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
              const row = {};
              headers.forEach((header, index) => {
                row[header] = values[index] || '';
              });
              data.push(row);
            }
          }

          try {
            const response = await api.post('/admin/tax-data/validate/', {
              file_type: uploadForm.file_type,
              headers: headers,
              data: data
            });
            validationResults.value = response.data;
          } catch (error) {
            console.error('Error validating file:', error);
            validationResults.value = {
              is_valid: false,
              errors: ['Failed to validate file structure'],
              warnings: []
            };
          }
        };
        
        reader.readAsText(selectedCsvFile.value);
      } catch (error) {
        console.error('Error reading file:', error);
      }
    };

    const uploadTaxFile = async () => {
      if (!selectedCsvFile.value || !validationResults.value?.is_valid) return;
      
      try {
        uploading.value = true;
        const formData = new FormData();
        formData.append('file', selectedCsvFile.value);
        formData.append('file_type', uploadForm.file_type);
        formData.append('tax_year', uploadForm.tax_year);
        formData.append('create_backup', uploadForm.create_backup);

        const response = await api.post('/admin/tax-data/upload/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        // Success - reload files and close modal
        await loadTaxDataFiles();
        showUploadModal.value = false;
        resetUploadForm();
        
        // Show success message
        console.log('File uploaded successfully:', response.data);
      } catch (error) {
        console.error('Error uploading file:', error);
      } finally {
        uploading.value = false;
      }
    };

    const restoreBackup = async (backup) => {
      if (!confirm(`Are you sure you want to restore ${backup.original_filename} from this backup?`)) {
        return;
      }
      
      try {
        const response = await api.post(
          `/admin/tax-data/backups/${backup.backup_filename}/restore/`,
          { create_backup: true }
        );
        
        // Reload files and backups
        await Promise.all([loadTaxDataFiles(), loadBackups()]);
        
        console.log('Backup restored successfully:', response.data);
      } catch (error) {
        console.error('Error restoring backup:', error);
      }
    };

    const resetUploadForm = () => {
      uploadForm.file_type = '';
      uploadForm.tax_year = '';
      uploadForm.create_backup = true;
      selectedCsvFile.value = null;
      uploadPreview.value = null;
      validationResults.value = null;
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown';
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    // Watch for file type changes to re-validate
    watch(() => uploadForm.file_type, () => {
      if (selectedCsvFile.value) {
        validateUploadFile();
      }
    });

    // Watch for tab changes to load data
    watch(activeTab, (newTab) => {
      if (newTab === 'backups' && backups.value.length === 0) {
        loadBackups();
      }
      if (newTab === 'validation' && Object.keys(validationRules.value).length === 0) {
        loadValidationRules();
      }
    });

    // Load initial data
    onMounted(() => {
      loadTaxDataFiles();
      loadValidationRules();
    });

    return {
      // Reactive data
      loading,
      loadingBackups,
      loadingFileContent,
      uploading,
      activeTab,
      selectedYear,
      selectedFileType,
      taxDataFiles,
      backups,
      validationRules,
      fileContent,
      selectedFile,
      showUploadModal,
      showFileContentModal,
      uploadForm,
      uploadPreview,
      validationResults,
      selectedCsvFile,

      // Computed
      taxDataSummary,
      backupsSummary,
      filteredTaxFiles,
      availableYears,
      availableFileTypes,
      selectedValidationRules,

      // Methods
      loadTaxDataFiles,
      loadBackups,
      loadValidationRules,
      viewFileContent,
      editFile,
      downloadFile,
      handleFileSelect,
      validateUploadFile,
      uploadTaxFile,
      restoreBackup,
      resetUploadForm,
      formatDate
    };
  }
};
</script>

<style scoped>
.tax-data-management {
  padding: 1.5rem;
}
.admin-page-header {
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
}

.tax-data-management-content {
  padding: 0;
}

.nav-tabs .nav-link {
  border: none;
  color: #6c757d;
  padding: 12px 20px;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  border-bottom: 2px solid #0d6efd;
  background-color: transparent;
}

.table th {
  border-top: none;
  padding: 12px;
  font-weight: 600;
  color: #495057;
}

.table td {
  padding: 12px;
  vertical-align: middle;
}

.btn-group .btn {
  padding: 6px 10px;
}

.modal-xl {
  max-width: 1200px;
}

.table-responsive {
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
}

.table-dark th {
  background-color: #495057;
  border-color: #495057;
}

.list-group-item.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.alert {
  border-radius: 0.375rem;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>