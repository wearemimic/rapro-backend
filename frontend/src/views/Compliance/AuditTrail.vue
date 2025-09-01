<template>
  <div class="audit-trail-viewer container-fluid" style="margin-top:80px;">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>Audit Trail</h2>
        <p class="text-muted">Complete audit log with advanced filtering and search capabilities</p>
      </div>
      <div>
        <button @click="exportToCSV" class="btn btn-outline-primary me-2" :disabled="isExporting">
          <i class="bi bi-file-earmark-csv"></i> 
          <span v-if="isExporting">Exporting...</span>
          <span v-else>Export CSV</span>
        </button>
        <button @click="exportToPDF" class="btn btn-outline-danger" :disabled="isExporting">
          <i class="bi bi-file-earmark-pdf"></i> Export PDF
        </button>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="row mb-3">
      <div class="col-md-4">
        <div class="input-group">
          <span class="input-group-text"><i class="bi bi-search"></i></span>
          <input 
            v-model="searchTerm" 
            type="text" 
            class="form-control" 
            placeholder="Search audit entries..."
          >
          <button v-if="searchTerm" @click="clearSearch" class="btn btn-outline-secondary">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
      <div class="col-md-2">
        <select v-model="filterAction" class="form-select">
          <option value="">All Actions</option>
          <option value="document_viewed">Document Viewed</option>
          <option value="document_downloaded">Document Downloaded</option>
          <option value="document_shared">Document Shared</option>
          <option value="document_deleted">Document Deleted</option>
          <option value="client_data_modified">Client Data Modified</option>
          <option value="communication_sent">Communication Sent</option>
        </select>
      </div>
      <div class="col-md-2">
        <select v-model="filterUser" class="form-select">
          <option value="">All Users</option>
          <option v-for="user in uniqueUsers" :key="user.id" :value="user.id">
            {{ user.name }}
          </option>
        </select>
      </div>
      <div class="col-md-2">
        <input v-model="startDate" type="date" class="form-control" placeholder="Start Date">
      </div>
      <div class="col-md-2">
        <input v-model="endDate" type="date" class="form-control" placeholder="End Date">
      </div>
    </div>

    <!-- Filter Summary -->
    <div v-if="hasActiveFilters" class="alert alert-info d-flex justify-content-between align-items-center mb-3">
      <div>
        <i class="bi bi-funnel me-2"></i>
        Filters applied: 
        <span v-if="searchTerm" class="badge bg-primary me-1">Search: "{{ searchTerm }}"</span>
        <span v-if="filterAction" class="badge bg-secondary me-1">Action: {{ getActionDisplayName(filterAction) }}</span>
        <span v-if="filterUser" class="badge bg-secondary me-1">User: {{ getUserName(filterUser) }}</span>
        <span v-if="startDate" class="badge bg-secondary me-1">From: {{ startDate }}</span>
        <span v-if="endDate" class="badge bg-secondary me-1">To: {{ endDate }}</span>
      </div>
      <button @click="clearAllFilters" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-x-circle"></i> Clear All
      </button>
    </div>

    <!-- Audit Entries Table -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">
          Audit Trail Entries 
          <span class="badge bg-secondary ms-2">{{ filteredEntries.length }}</span>
          <span v-if="filteredEntries.length !== auditEntries.length" class="text-muted">
            of {{ auditEntries.length }} total
          </span>
        </h6>
        <div class="d-flex align-items-center">
          <small class="text-muted me-3">Last updated: {{ lastUpdated }}</small>
          <button @click="refreshData" class="btn btn-outline-secondary btn-sm" :disabled="isLoading">
            <i class="bi bi-arrow-clockwise" :class="{ 'spin': isLoading }"></i>
            <span v-if="isLoading">Refreshing...</span>
            <span v-else>Refresh</span>
          </button>
        </div>
      </div>
      <div class="card-body p-0">
        <div v-if="isLoading" class="text-center p-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading audit entries...</p>
        </div>
        <div v-else-if="!filteredEntries.length" class="text-center p-4 text-muted">
          <i class="bi bi-inbox display-1 mb-3"></i>
          <p v-if="hasActiveFilters">No audit entries match your current filters.</p>
          <p v-else>No audit entries available.</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-sm mb-0">
            <thead class="table-light">
              <tr>
                <th @click="sortBy('timestamp')" class="sortable" style="min-width: 150px;">
                  Timestamp 
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="sortBy('user_name')" class="sortable">
                  User 
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th>Action</th>
                <th style="max-width: 200px;">Target</th>
                <th>Details</th>
                <th style="min-width: 120px;">IP Address</th>
                <th style="max-width: 150px;">User Agent</th>
                <th>Compliance</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in paginatedEntries" :key="entry.id" 
                  :class="{'table-warning': entry.compliance_relevant, 'table-danger': !entry.success}">
                <td class="small font-monospace">{{ formatTimestamp(entry.timestamp) }}</td>
                <td class="small">{{ entry.user_name }}</td>
                <td class="small">
                  <span class="badge" :class="getActionBadgeClass(entry.action)">
                    {{ entry.action_display }}
                  </span>
                </td>
                <td class="small">
                  <div v-if="entry.client_name" class="fw-bold">{{ entry.client_name }}</div>
                  <div class="text-truncate" style="max-width: 200px;" :title="entry.target_description">
                    {{ entry.target_description }}
                  </div>
                </td>
                <td class="small">
                  <button 
                    @click="viewDetails(entry)" 
                    class="btn btn-link btn-sm p-0"
                    data-bs-toggle="tooltip" 
                    :title="'Click to view detailed information'"
                  >
                    <i class="bi bi-info-circle"></i>
                  </button>
                </td>
                <td class="small font-monospace">{{ entry.user_ip }}</td>
                <td class="small">
                  <span class="text-truncate d-inline-block" style="max-width: 150px;" 
                        :title="entry.user_agent">
                    {{ entry.user_agent }}
                  </span>
                </td>
                <td class="small text-center">
                  <i v-if="entry.compliance_relevant" 
                     class="bi bi-exclamation-triangle text-warning" 
                     title="Compliance Relevant"
                     data-bs-toggle="tooltip"></i>
                  <i v-else class="bi bi-dash text-muted"></i>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card-footer" v-if="filteredEntries.length">
        <!-- Pagination -->
        <nav class="d-flex justify-content-between align-items-center">
          <div>
            <small class="text-muted">
              Showing {{ startIndex + 1 }}-{{ Math.min(startIndex + itemsPerPage, filteredEntries.length) }} 
              of {{ filteredEntries.length }} entries
            </small>
          </div>
          <ul class="pagination pagination-sm mb-0">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button @click="currentPage--" class="page-link">Previous</button>
            </li>
            <li v-for="page in visiblePages" :key="page" 
                class="page-item" :class="{ active: page === currentPage }">
              <button @click="currentPage = page" class="page-link">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button @click="currentPage++" class="page-link">Next</button>
            </li>
          </ul>
          <div>
            <select v-model="itemsPerPage" class="form-select form-select-sm" style="width: auto;">
              <option :value="25">25 per page</option>
              <option :value="50">50 per page</option>
              <option :value="100">100 per page</option>
            </select>
          </div>
        </nav>
      </div>
    </div>

    <!-- Details Modal -->
    <div class="modal fade" id="auditDetailsModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Audit Entry Details</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedEntry">
              <div class="row mb-3">
                <div class="col-md-6">
                  <strong>Timestamp:</strong> {{ formatTimestamp(selectedEntry.timestamp) }}
                </div>
                <div class="col-md-6">
                  <strong>User:</strong> {{ selectedEntry.user_name }}
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <strong>Action:</strong> 
                  <span class="badge ms-1" :class="getActionBadgeClass(selectedEntry.action)">
                    {{ selectedEntry.action_display }}
                  </span>
                </div>
                <div class="col-md-6">
                  <strong>Success:</strong> 
                  <span :class="selectedEntry.success ? 'text-success' : 'text-danger'">
                    <i :class="selectedEntry.success ? 'bi bi-check-circle' : 'bi bi-x-circle'"></i>
                    {{ selectedEntry.success ? 'Yes' : 'No' }}
                  </span>
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <strong>IP Address:</strong> 
                  <code>{{ selectedEntry.user_ip }}</code>
                </div>
                <div class="col-md-6">
                  <strong>Session ID:</strong> 
                  <code>{{ selectedEntry.session_id || 'N/A' }}</code>
                </div>
              </div>
              <div class="mb-3">
                <strong>Target:</strong>
                <div class="mt-1">
                  <div v-if="selectedEntry.client_name" class="mb-1">
                    <strong>Client:</strong> {{ selectedEntry.client_name }}
                  </div>
                  <div>{{ selectedEntry.target_description }}</div>
                </div>
              </div>
              <div class="mb-3">
                <strong>User Agent:</strong>
                <pre class="small bg-light p-2 mt-1">{{ selectedEntry.user_agent }}</pre>
              </div>
              <div v-if="selectedEntry.details" class="mb-3">
                <strong>Additional Details:</strong>
                <pre class="small bg-light p-2 mt-1">{{ JSON.stringify(selectedEntry.details, null, 2) }}</pre>
              </div>
              <div v-if="selectedEntry.error_message" class="mb-3">
                <strong>Error Message:</strong>
                <pre class="small bg-danger text-white p-2 mt-1">{{ selectedEntry.error_message }}</pre>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <strong>Compliance Relevant:</strong>
                  <span :class="selectedEntry.compliance_relevant ? 'text-warning' : 'text-muted'">
                    <i :class="selectedEntry.compliance_relevant ? 'bi bi-exclamation-triangle' : 'bi bi-dash'"></i>
                    {{ selectedEntry.compliance_relevant ? 'Yes' : 'No' }}
                  </span>
                </div>
                <div class="col-md-6">
                  <strong>Entry ID:</strong> 
                  <code>{{ selectedEntry.id }}</code>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'AuditTrail',
  
  setup() {
    const auditEntries = ref([])
    const searchTerm = ref('')
    const filterAction = ref('')
    const filterUser = ref('')
    const startDate = ref('')
    const endDate = ref('')
    const sortField = ref('timestamp')
    const sortDirection = ref('desc')
    const currentPage = ref(1)
    const itemsPerPage = ref(50)
    const selectedEntry = ref(null)
    const isLoading = ref(false)
    const isExporting = ref(false)
    const lastUpdated = ref('')
    
    const filteredEntries = computed(() => {
      return auditEntries.value.filter(entry => {
        // Search filter
        if (searchTerm.value) {
          const search = searchTerm.value.toLowerCase()
          if (![entry.user_name, entry.action_display, entry.target_description, entry.user_ip, entry.client_name]
              .some(field => field?.toLowerCase().includes(search))) {
            return false
          }
        }
        
        // Action filter
        if (filterAction.value && entry.action !== filterAction.value) {
          return false
        }
        
        // User filter
        if (filterUser.value && entry.user_id !== parseInt(filterUser.value)) {
          return false
        }
        
        // Date range filter
        if (startDate.value && new Date(entry.timestamp) < new Date(startDate.value)) {
          return false
        }
        if (endDate.value && new Date(entry.timestamp) > new Date(endDate.value + 'T23:59:59')) {
          return false
        }
        
        return true
      })
    })
    
    const sortedEntries = computed(() => {
      const sorted = [...filteredEntries.value]
      return sorted.sort((a, b) => {
        let aVal = a[sortField.value]
        let bVal = b[sortField.value]
        
        // Handle date sorting
        if (sortField.value === 'timestamp') {
          aVal = new Date(aVal)
          bVal = new Date(bVal)
        }
        
        const modifier = sortDirection.value === 'asc' ? 1 : -1
        
        if (aVal < bVal) return -1 * modifier
        if (aVal > bVal) return 1 * modifier
        return 0
      })
    })
    
    const paginatedEntries = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      return sortedEntries.value.slice(start, start + itemsPerPage.value)
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredEntries.value.length / itemsPerPage.value)
    })
    
    const startIndex = computed(() => {
      return (currentPage.value - 1) * itemsPerPage.value
    })
    
    const visiblePages = computed(() => {
      const pages = []
      const maxVisible = 5
      let startPage = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
      let endPage = Math.min(totalPages.value, startPage + maxVisible - 1)
      
      if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1)
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }
      
      return pages
    })
    
    const uniqueUsers = computed(() => {
      const users = auditEntries.value.reduce((acc, entry) => {
        if (!acc.find(u => u.id === entry.user_id)) {
          acc.push({ id: entry.user_id, name: entry.user_name })
        }
        return acc
      }, [])
      return users.sort((a, b) => a.name.localeCompare(b.name))
    })
    
    const hasActiveFilters = computed(() => {
      return searchTerm.value || filterAction.value || filterUser.value || startDate.value || endDate.value
    })
    
    const loadAuditEntries = async () => {
      isLoading.value = true
      try {
        // Mock data for now - in production would fetch from API
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        auditEntries.value = [
          {
            id: 1,
            timestamp: new Date().toISOString(),
            user_name: 'John Advisor',
            user_id: 1,
            action: 'document_viewed',
            action_display: 'Document Viewed',
            target_description: 'Client_Financial_Plan.pdf',
            client_name: 'Smith, Robert',
            user_ip: '192.168.1.100',
            user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            success: true,
            compliance_relevant: true,
            session_id: 'sess_abc123',
            details: { file_size: '2.5MB', download_time: '1.2s' }
          },
          {
            id: 2,
            timestamp: new Date(Date.now() - 300000).toISOString(),
            user_name: 'John Advisor',
            user_id: 1,
            action: 'communication_sent',
            action_display: 'Email Sent',
            target_description: 'Market Update - Client Communication',
            client_name: 'Johnson, Mary',
            user_ip: '192.168.1.100',
            user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            success: true,
            compliance_relevant: true,
            session_id: 'sess_abc123',
            details: { subject: 'Market Update', recipients: 1 }
          },
          {
            id: 3,
            timestamp: new Date(Date.now() - 600000).toISOString(),
            user_name: 'Sarah Assistant',
            user_id: 2,
            action: 'client_data_modified',
            action_display: 'Client Data Updated',
            target_description: 'Contact Information Updated',
            client_name: 'Williams, Carol',
            user_ip: '192.168.1.101',
            user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            success: true,
            compliance_relevant: true,
            session_id: 'sess_def456',
            details: { fields_changed: ['phone', 'email'] }
          },
          {
            id: 4,
            timestamp: new Date(Date.now() - 900000).toISOString(),
            user_name: 'John Advisor',
            user_id: 1,
            action: 'document_downloaded',
            action_display: 'Document Downloaded',
            target_description: 'Tax_Return_2023.pdf',
            client_name: 'Brown, Michael',
            user_ip: '192.168.1.100',
            user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            success: true,
            compliance_relevant: true,
            session_id: 'sess_abc123',
            details: { file_size: '1.8MB', download_duration: '0.8s' }
          },
          {
            id: 5,
            timestamp: new Date(Date.now() - 1200000).toISOString(),
            user_name: 'John Advisor',
            user_id: 1,
            action: 'document_shared',
            action_display: 'Document Shared',
            target_description: 'Investment_Portfolio_Summary.pdf',
            client_name: 'Davis, Jennifer',
            user_ip: '192.168.1.100',
            user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            success: true,
            compliance_relevant: true,
            session_id: 'sess_abc123',
            details: { shared_with: 'client', expiry: '7 days' }
          }
        ]
        
        lastUpdated.value = new Date().toLocaleTimeString()
      } catch (error) {
        console.error('Error loading audit entries:', error)
      } finally {
        isLoading.value = false
      }
    }
    
    const refreshData = () => {
      loadAuditEntries()
    }
    
    const viewDetails = (entry) => {
      selectedEntry.value = entry
      // Use a simple approach to show modal
      const modal = document.getElementById('auditDetailsModal')
      if (modal) {
        modal.classList.add('show')
        modal.style.display = 'block'
        document.body.classList.add('modal-open')
      }
    }
    
    const closeModal = () => {
      const modal = document.getElementById('auditDetailsModal')
      if (modal) {
        modal.classList.remove('show')
        modal.style.display = 'none'
        document.body.classList.remove('modal-open')
      }
      selectedEntry.value = null
    }
    
    const sortBy = (field) => {
      if (sortField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortField.value = field
        sortDirection.value = 'desc'
      }
      currentPage.value = 1
    }
    
    const clearSearch = () => {
      searchTerm.value = ''
    }
    
    const clearAllFilters = () => {
      searchTerm.value = ''
      filterAction.value = ''
      filterUser.value = ''
      startDate.value = ''
      endDate.value = ''
      currentPage.value = 1
    }
    
    const exportToCSV = async () => {
      isExporting.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        const csvContent = [
          'Timestamp,User,Action,Target,Client,IP Address,User Agent,Success,Compliance Relevant',
          ...filteredEntries.value.map(entry => 
            `"${entry.timestamp}","${entry.user_name}","${entry.action_display}","${entry.target_description}","${entry.client_name || ''}","${entry.user_ip}","${entry.user_agent}","${entry.success ? 'Success' : 'Failed'}","${entry.compliance_relevant ? 'Yes' : 'No'}"`
          )
        ].join('\n')
        
        const element = document.createElement('a')
        element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent))
        element.setAttribute('download', `audit_trail_${new Date().toISOString().split('T')[0]}.csv`)
        element.style.display = 'none'
        document.body.appendChild(element)
        element.click()
        document.body.removeChild(element)
        
      } catch (error) {
        console.error('Error exporting to CSV:', error)
      } finally {
        isExporting.value = false
      }
    }
    
    const exportToPDF = async () => {
      isExporting.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Mock PDF export - in production would generate actual PDF
        const element = document.createElement('a')
        element.setAttribute('href', 'data:text/plain;charset=utf-8,FINRA Audit Trail Report\n\nGenerated: ' + new Date().toLocaleString() + '\nTotal Entries: ' + filteredEntries.value.length)
        element.setAttribute('download', `audit_trail_${new Date().toISOString().split('T')[0]}.pdf`)
        element.style.display = 'none'
        document.body.appendChild(element)
        element.click()
        document.body.removeChild(element)
        
      } catch (error) {
        console.error('Error exporting to PDF:', error)
      } finally {
        isExporting.value = false
      }
    }
    
    const getActionDisplayName = (action) => {
      const actionNames = {
        'document_viewed': 'Document Viewed',
        'document_downloaded': 'Document Downloaded',
        'document_shared': 'Document Shared',
        'document_deleted': 'Document Deleted',
        'client_data_modified': 'Client Data Modified',
        'communication_sent': 'Communication Sent'
      }
      return actionNames[action] || action
    }
    
    const getUserName = (userId) => {
      const user = uniqueUsers.value.find(u => u.id === parseInt(userId))
      return user ? user.name : 'Unknown'
    }
    
    const getActionBadgeClass = (action) => {
      const actionClasses = {
        'document_viewed': 'bg-info',
        'document_downloaded': 'bg-primary',
        'document_shared': 'bg-warning',
        'document_deleted': 'bg-danger',
        'client_data_modified': 'bg-secondary',
        'communication_sent': 'bg-success'
      }
      return actionClasses[action] || 'bg-light text-dark'
    }
    
    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }
    
    // Watch for filter changes to reset pagination
    const resetPagination = () => {
      currentPage.value = 1
    }
    
    onMounted(() => {
      loadAuditEntries()
    })
    
    return {
      auditEntries,
      searchTerm,
      filterAction,
      filterUser,
      startDate,
      endDate,
      currentPage,
      itemsPerPage,
      selectedEntry,
      isLoading,
      isExporting,
      lastUpdated,
      filteredEntries,
      paginatedEntries,
      totalPages,
      startIndex,
      visiblePages,
      uniqueUsers,
      hasActiveFilters,
      loadAuditEntries,
      refreshData,
      viewDetails,
      closeModal,
      sortBy,
      clearSearch,
      clearAllFilters,
      exportToCSV,
      exportToPDF,
      getActionDisplayName,
      getUserName,
      getActionBadgeClass,
      formatTimestamp
    }
  }
}
</script>

<style scoped>
.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #f8f9fa;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

pre {
  white-space: pre-wrap;
  word-break: break-all;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.table-responsive::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.table-responsive::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-responsive::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.table-responsive::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.badge {
  font-size: 0.75em;
}
</style>