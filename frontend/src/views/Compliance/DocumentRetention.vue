<template>
  <div class="document-retention container-fluid" style="margin-top:80px;">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>Document Retention Management</h2>
        <p class="text-muted">Automated FINRA-compliant document lifecycle management</p>
      </div>
      <div>
        <button @click="showPolicyModal = true" class="btn btn-primary me-2">
          <i class="bi bi-plus-circle"></i> New Retention Policy
        </button>
        <button @click="runRetentionScan" class="btn btn-outline-secondary" :disabled="isScanning">
          <i class="bi bi-search"></i> 
          <span v-if="isScanning">Scanning...</span>
          <span v-else>Scan Documents</span>
        </button>
      </div>
    </div>

    <!-- Retention Policy Overview -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-gear display-1 text-primary mb-2"></i>
            <h5>Active Policies</h5>
            <span class="badge bg-primary fs-5">{{ retentionPolicies.filter(p => p.is_active).length }}</span>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-clock-history display-1 text-warning mb-2"></i>
            <h5>Pending Review</h5>
            <span class="badge bg-warning fs-5">{{ pendingReviewCount }}</span>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-trash display-1 text-danger mb-2"></i>
            <h5>Pending Disposal</h5>
            <span class="badge bg-danger fs-5">{{ pendingDisposalCount }}</span>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi bi-shield-check display-1 text-success mb-2"></i>
            <h5>Compliant Docs</h5>
            <span class="badge bg-success fs-5">{{ compliantDocsCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Retention Policies -->
    <div class="row">
      <div class="col-md-8">
        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Retention Policies</h5>
            <div>
              <button @click="refreshPolicies" class="btn btn-outline-secondary btn-sm">
                <i class="bi bi-arrow-clockwise"></i> Refresh
              </button>
            </div>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Policy Name</th>
                    <th>Category</th>
                    <th>Retention Period</th>
                    <th>Auto Disposal</th>
                    <th>Documents</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="policy in retentionPolicies" :key="policy.id">
                    <td>
                      <div class="fw-bold">{{ policy.name }}</div>
                      <small class="text-muted">{{ policy.description }}</small>
                    </td>
                    <td>
                      <span class="badge bg-secondary">{{ policy.category_name }}</span>
                    </td>
                    <td>{{ policy.retention_years }} years</td>
                    <td>
                      <i v-if="policy.auto_disposal_enabled" class="bi bi-check-circle text-success"></i>
                      <i v-else class="bi bi-x-circle text-muted"></i>
                    </td>
                    <td>{{ policy.document_count || 0 }}</td>
                    <td>
                      <span class="badge" :class="policy.is_active ? 'bg-success' : 'bg-secondary'">
                        {{ policy.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button @click="editPolicy(policy)" class="btn btn-outline-primary">
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button @click="viewPolicyDocuments(policy)" class="btn btn-outline-secondary">
                          <i class="bi bi-files"></i>
                        </button>
                        <button @click="togglePolicyStatus(policy)" 
                                class="btn" 
                                :class="policy.is_active ? 'btn-outline-warning' : 'btn-outline-success'">
                          <i :class="policy.is_active ? 'bi-pause' : 'bi-play'"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Retention Timeline -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Upcoming Retention Events</h5>
          </div>
          <div class="card-body">
            <div v-if="upcomingEvents.length" class="timeline">
              <div v-for="event in upcomingEvents" :key="event.id" 
                   class="timeline-item d-flex align-items-start mb-4">
                <div class="timeline-marker me-3">
                  <i class="bi bi-calendar-event" :class="getEventIconClass(event.event_type)"></i>
                </div>
                <div class="timeline-content flex-grow-1">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <h6 class="mb-1">{{ event.document_title }}</h6>
                      <p class="text-muted mb-1">
                        <strong>{{ event.event_type }}:</strong> {{ formatDate(event.scheduled_date) }}
                      </p>
                      <small class="text-muted">
                        Client: {{ event.client_name }} | Category: {{ event.category }}
                      </small>
                    </div>
                    <div class="text-end">
                      <span class="badge" :class="getEventBadgeClass(event.days_until)">
                        {{ event.days_until }} days
                      </span>
                      <div class="btn-group btn-group-sm mt-1">
                        <button @click="reviewDocument(event)" class="btn btn-outline-primary btn-sm">
                          Review
                        </button>
                        <button @click="postponeEvent(event)" class="btn btn-outline-secondary btn-sm">
                          Postpone
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="progress" style="height: 4px;">
                    <div class="progress-bar" 
                         :class="getProgressBarClass(event.days_until)"
                         :style="{ width: getProgressPercentage(event.days_until) + '%' }">
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center p-4 text-muted">
              <i class="bi bi-calendar-check display-1 mb-3 text-success"></i>
              <p>No upcoming retention events. All documents are compliant.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <!-- Quick Actions -->
        <div class="card mb-4">
          <div class="card-header">
            <h6 class="mb-0">Quick Actions</h6>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <button @click="bulkReview" class="btn btn-warning" :disabled="pendingReviewCount === 0">
                <i class="bi bi-eye"></i> Bulk Review ({{ pendingReviewCount }})
              </button>
              <button @click="bulkDisposal" class="btn btn-danger" :disabled="pendingDisposalCount === 0">
                <i class="bi bi-trash"></i> Bulk Disposal ({{ pendingDisposalCount }})
              </button>
              <button @click="generateRetentionReport" class="btn btn-outline-primary">
                <i class="bi bi-file-text"></i> Generate Report
              </button>
              <button @click="exportRetentionData" class="btn btn-outline-secondary">
                <i class="bi bi-download"></i> Export Data
              </button>
            </div>
          </div>
        </div>

        <!-- Compliance Summary -->
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Compliance Summary</h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <div class="d-flex justify-content-between mb-1">
                <span>FINRA Rule 3110</span>
                <span class="text-success">✓ Compliant</span>
              </div>
              <div class="progress" style="height: 4px;">
                <div class="progress-bar bg-success" style="width: 100%"></div>
              </div>
            </div>
            <div class="mb-3">
              <div class="d-flex justify-content-between mb-1">
                <span>SEC Rule 17a-4</span>
                <span class="text-success">✓ Compliant</span>
              </div>
              <div class="progress" style="height: 4px;">
                <div class="progress-bar bg-success" style="width: 100%"></div>
              </div>
            </div>
            <div class="mb-3">
              <div class="d-flex justify-content-between mb-1">
                <span>Document Encryption</span>
                <span class="text-success">100%</span>
              </div>
              <div class="progress" style="height: 4px;">
                <div class="progress-bar bg-success" style="width: 100%"></div>
              </div>
            </div>
            <div>
              <div class="d-flex justify-content-between mb-1">
                <span>Automated Policies</span>
                <span class="text-info">{{ retentionPolicies.filter(p => p.auto_disposal_enabled).length }}/{{ retentionPolicies.length }}</span>
              </div>
              <div class="progress" style="height: 4px;">
                <div class="progress-bar bg-info" 
                     :style="{ width: (retentionPolicies.filter(p => p.auto_disposal_enabled).length / Math.max(retentionPolicies.length, 1) * 100) + '%' }">
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Policy Modal -->
    <div class="modal fade" id="policyModal" tabindex="-1" v-if="showPolicyModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingPolicy ? 'Edit Retention Policy' : 'Create Retention Policy' }}
            </h5>
            <button type="button" class="btn-close" @click="closePolicyModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="savePolicy">
              <div class="row mb-3">
                <div class="col-md-8">
                  <label class="form-label">Policy Name</label>
                  <input v-model="currentPolicy.name" type="text" class="form-control" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Status</label>
                  <select v-model="currentPolicy.is_active" class="form-select">
                    <option :value="true">Active</option>
                    <option :value="false">Inactive</option>
                  </select>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="currentPolicy.description" class="form-control" rows="3"></textarea>
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Document Category</label>
                  <select v-model="currentPolicy.category_id" class="form-select" required>
                    <option value="">Select Category</option>
                    <option v-for="category in documentCategories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Retention Period (Years)</label>
                  <input v-model="currentPolicy.retention_years" type="number" min="1" max="50" class="form-control" required>
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Trigger Type</label>
                  <select v-model="currentPolicy.trigger_type" class="form-select">
                    <option value="document_upload">When Document Uploaded</option>
                    <option value="client_termination">When Client Relationship Ends</option>
                    <option value="fixed_date">Fixed Date</option>
                    <option value="custom_event">Custom Business Event</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Disposal Method</label>
                  <select v-model="currentPolicy.disposal_method" class="form-select">
                    <option value="secure_delete">Secure Deletion</option>
                    <option value="archive_only">Archive (No Access)</option>
                    <option value="transfer_custody">Transfer to Client</option>
                  </select>
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <div class="form-check">
                    <input v-model="currentPolicy.auto_disposal_enabled" class="form-check-input" type="checkbox" id="autoDisposal">
                    <label class="form-check-label" for="autoDisposal">
                      Enable Auto Disposal
                    </label>
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Notification Days Before</label>
                  <input v-model="currentPolicy.notification_before_days" type="number" min="1" max="365" class="form-control">
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Regulatory Basis</label>
                <textarea v-model="currentPolicy.regulatory_basis" class="form-control" rows="2" 
                          placeholder="Legal justification for this retention period..."></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closePolicyModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="savePolicy">
              {{ editingPolicy ? 'Update Policy' : 'Create Policy' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'DocumentRetention',
  
  setup() {
    const retentionPolicies = ref([])
    const upcomingEvents = ref([])
    const documentCategories = ref([])
    const showPolicyModal = ref(false)
    const editingPolicy = ref(false)
    const currentPolicy = ref({})
    const isScanning = ref(false)
    
    const pendingReviewCount = computed(() => {
      return upcomingEvents.value.filter(e => e.event_type === 'Review Required' && e.days_until <= 30).length
    })
    
    const pendingDisposalCount = computed(() => {
      return upcomingEvents.value.filter(e => e.event_type === 'Disposal Scheduled' && e.days_until <= 7).length
    })
    
    const compliantDocsCount = computed(() => {
      return upcomingEvents.value.filter(e => e.days_until > 30).length + 1200 // Mock compliant count
    })
    
    const loadRetentionData = async () => {
      try {
        // Mock data - in production would fetch from API
        
        retentionPolicies.value = [
          {
            id: 1,
            name: 'Client Financial Plans',
            description: 'Retention policy for comprehensive financial planning documents',
            category_name: 'Financial Plans',
            category_id: 1,
            retention_years: 7,
            auto_disposal_enabled: true,
            document_count: 156,
            is_active: true,
            trigger_type: 'document_upload',
            disposal_method: 'secure_delete',
            notification_before_days: 30,
            regulatory_basis: 'FINRA Rule 3110 - Books and Records requirements'
          },
          {
            id: 2,
            name: 'Client Communications',
            description: 'Email and written communication records',
            category_name: 'Communications',
            category_id: 2,
            retention_years: 3,
            auto_disposal_enabled: false,
            document_count: 2847,
            is_active: true,
            trigger_type: 'client_termination',
            disposal_method: 'archive_only',
            notification_before_days: 60,
            regulatory_basis: 'SEC Rule 17a-4 - Communication records'
          },
          {
            id: 3,
            name: 'Investment Statements',
            description: 'Quarterly and annual investment statements',
            category_name: 'Investment Records',
            category_id: 3,
            retention_years: 6,
            auto_disposal_enabled: true,
            document_count: 489,
            is_active: true,
            trigger_type: 'document_upload',
            disposal_method: 'transfer_custody',
            notification_before_days: 90,
            regulatory_basis: 'FINRA Rule 4511 - Customer account information'
          }
        ]
        
        upcomingEvents.value = [
          {
            id: 1,
            document_title: 'Financial_Plan_Smith_2019.pdf',
            event_type: 'Review Required',
            scheduled_date: new Date(Date.now() + 86400000 * 15).toISOString(),
            days_until: 15,
            client_name: 'Smith, Robert',
            category: 'Financial Plans'
          },
          {
            id: 2,
            document_title: 'Investment_Statement_Q4_2020.pdf',
            event_type: 'Disposal Scheduled',
            scheduled_date: new Date(Date.now() + 86400000 * 5).toISOString(),
            days_until: 5,
            client_name: 'Johnson, Mary',
            category: 'Investment Records'
          },
          {
            id: 3,
            document_title: 'Client_Communications_2021.pdf',
            event_type: 'Archive Review',
            scheduled_date: new Date(Date.now() + 86400000 * 45).toISOString(),
            days_until: 45,
            client_name: 'Williams, Carol',
            category: 'Communications'
          }
        ]
        
        documentCategories.value = [
          { id: 1, name: 'Financial Plans' },
          { id: 2, name: 'Communications' },
          { id: 3, name: 'Investment Records' },
          { id: 4, name: 'Tax Documents' },
          { id: 5, name: 'Insurance Policies' },
          { id: 6, name: 'Estate Planning' },
          { id: 7, name: 'Compliance Documents' }
        ]
        
      } catch (error) {
        console.error('Error loading retention data:', error)
      }
    }
    
    const refreshPolicies = () => {
      loadRetentionData()
    }
    
    const editPolicy = (policy) => {
      currentPolicy.value = { ...policy }
      editingPolicy.value = true
      showPolicyModal.value = true
    }
    
    const closePolicyModal = () => {
      showPolicyModal.value = false
      editingPolicy.value = false
      currentPolicy.value = {}
    }
    
    const savePolicy = async () => {
      try {
        // Mock save - in production would POST/PUT to API
        if (editingPolicy.value) {
          const index = retentionPolicies.value.findIndex(p => p.id === currentPolicy.value.id)
          if (index !== -1) {
            retentionPolicies.value[index] = { ...currentPolicy.value }
          }
        } else {
          currentPolicy.value.id = Date.now()
          retentionPolicies.value.push({ ...currentPolicy.value })
        }
        closePolicyModal()
      } catch (error) {
        console.error('Error saving policy:', error)
      }
    }
    
    const togglePolicyStatus = async (policy) => {
      try {
        policy.is_active = !policy.is_active
        // In production would PUT to API
      } catch (error) {
        console.error('Error toggling policy status:', error)
      }
    }
    
    const viewPolicyDocuments = (policy) => {
      // Navigate to documents filtered by this policy
      window.location.href = `/documents?category=${policy.category_id}&retention_policy=${policy.id}`
    }
    
    const runRetentionScan = async () => {
      isScanning.value = true
      try {
        // Mock scan process
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        // Refresh data after scan
        await loadRetentionData()
      } catch (error) {
        console.error('Error running retention scan:', error)
      } finally {
        isScanning.value = false
      }
    }
    
    const reviewDocument = (event) => {
      // Navigate to document review page
      console.log('Reviewing document:', event.document_title)
    }
    
    const postponeEvent = (event) => {
      // Show postponement modal or inline editor
      console.log('Postponing event:', event.id)
    }
    
    const bulkReview = () => {
      // Show bulk review interface
      console.log('Starting bulk review of', pendingReviewCount.value, 'documents')
    }
    
    const bulkDisposal = () => {
      // Show bulk disposal confirmation and interface
      console.log('Starting bulk disposal of', pendingDisposalCount.value, 'documents')
    }
    
    const generateRetentionReport = async () => {
      try {
        // Mock report generation
        const element = document.createElement('a')
        element.setAttribute('href', 'data:text/plain;charset=utf-8,Document Retention Report\n\nGenerated: ' + new Date().toLocaleString())
        element.setAttribute('download', `retention_report_${new Date().toISOString().split('T')[0]}.txt`)
        element.style.display = 'none'
        document.body.appendChild(element)
        element.click()
        document.body.removeChild(element)
      } catch (error) {
        console.error('Error generating report:', error)
      }
    }
    
    const exportRetentionData = async () => {
      try {
        // Mock data export
        const csvContent = [
          'Policy Name,Category,Retention Years,Auto Disposal,Document Count,Status',
          ...retentionPolicies.value.map(policy => 
            `"${policy.name}","${policy.category_name}","${policy.retention_years}","${policy.auto_disposal_enabled}","${policy.document_count}","${policy.is_active ? 'Active' : 'Inactive'}"`
          )
        ].join('\n')
        
        const element = document.createElement('a')
        element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent))
        element.setAttribute('download', `retention_policies_${new Date().toISOString().split('T')[0]}.csv`)
        element.style.display = 'none'
        document.body.appendChild(element)
        element.click()
        document.body.removeChild(element)
      } catch (error) {
        console.error('Error exporting data:', error)
      }
    }
    
    const getEventIconClass = (eventType) => {
      const classes = {
        'Review Required': 'text-warning',
        'Disposal Scheduled': 'text-danger',
        'Archive Review': 'text-info'
      }
      return classes[eventType] || 'text-secondary'
    }
    
    const getEventBadgeClass = (daysUntil) => {
      if (daysUntil <= 7) return 'bg-danger'
      if (daysUntil <= 30) return 'bg-warning'
      return 'bg-info'
    }
    
    const getProgressBarClass = (daysUntil) => {
      if (daysUntil <= 7) return 'bg-danger'
      if (daysUntil <= 30) return 'bg-warning'
      return 'bg-success'
    }
    
    const getProgressPercentage = (daysUntil) => {
      return Math.max(10, 100 - daysUntil)
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    onMounted(() => {
      loadRetentionData()
    })
    
    return {
      retentionPolicies,
      upcomingEvents,
      documentCategories,
      showPolicyModal,
      editingPolicy,
      currentPolicy,
      isScanning,
      pendingReviewCount,
      pendingDisposalCount,
      compliantDocsCount,
      loadRetentionData,
      refreshPolicies,
      editPolicy,
      closePolicyModal,
      savePolicy,
      togglePolicyStatus,
      viewPolicyDocuments,
      runRetentionScan,
      reviewDocument,
      postponeEvent,
      bulkReview,
      bulkDisposal,
      generateRetentionReport,
      exportRetentionData,
      getEventIconClass,
      getEventBadgeClass,
      getProgressBarClass,
      getProgressPercentage,
      formatDate
    }
  }
}
</script>

<style scoped>
.timeline-marker {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f8f9fa;
  border: 2px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
}

.timeline-item {
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 19px;
  top: 40px;
  width: 2px;
  height: calc(100% - 20px);
  background-color: #e9ecef;
  z-index: -1;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.badge {
  font-size: 0.75em;
}

.progress {
  border-radius: 2px;
}
</style>