<template>
  <div class="container-fluid" style="margin-top:80px;">
    <!-- Compliance Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>FINRA Compliance Dashboard</h2>
        <p class="text-muted">Complete regulatory compliance monitoring and reporting</p>
      </div>
      <div>
        <button @click="generateComplianceReport" class="btn btn-primary me-2" :disabled="isGenerating">
          <i class="bi bi-file-earmark-pdf"></i> 
          <span v-if="isGenerating">Generating...</span>
          <span v-else>Generate Report</span>
        </button>
        <button @click="exportAuditTrail" class="btn btn-outline-secondary" :disabled="isExporting">
          <i class="bi bi-download"></i> 
          <span v-if="isExporting">Exporting...</span>
          <span v-else>Export Audit Trail</span>
        </button>
      </div>
    </div>

    <!-- Compliance Status Cards -->
    <div class="row mb-4">
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card border-success">
          <div class="card-body text-center">
            <i class="bi bi-shield-check display-1 text-success mb-3"></i>
            <h5 class="card-title">FINRA Rule 3110</h5>
            <span class="badge bg-success fs-6">COMPLIANT</span>
            <p class="card-text small mt-2">Books & Records<br>Complete audit trail active</p>
          </div>
        </div>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card border-success">
          <div class="card-body text-center">
            <i class="bi bi-person-check display-1 text-success mb-3"></i>
            <h5 class="card-title">FINRA Rule 4511</h5>
            <span class="badge bg-success fs-6">COMPLIANT</span>
            <p class="card-text small mt-2">Customer Account Info<br>{{ totalClientsTracked }} clients monitored</p>
          </div>
        </div>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card border-success">
          <div class="card-body text-center">
            <i class="bi bi-archive display-1 text-success mb-3"></i>
            <h5 class="card-title">SEC Rule 17a-4</h5>
            <span class="badge bg-success fs-6">COMPLIANT</span>
            <p class="card-text small mt-2">Record Retention<br>{{ documentsRetained }} docs preserved</p>
          </div>
        </div>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card border-success">
          <div class="card-body text-center">
            <i class="bi bi-lock display-1 text-success mb-3"></i>
            <h5 class="card-title">Regulation S-P</h5>
            <span class="badge bg-success fs-6">COMPLIANT</span>
            <p class="card-text small mt-2">Privacy Protection<br>{{ piiDocumentsSecured }} PII docs secured</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Real-Time Audit Activity -->
    <div class="row">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Real-Time Audit Trail</h5>
            <div>
              <select v-model="auditFilter" class="form-select form-select-sm">
                <option value="all">All Activities</option>
                <option value="document">Document Access</option>
                <option value="communication">Communications</option>
                <option value="client_data">Client Data Changes</option>
                <option value="compliance">Compliance Events</option>
              </select>
            </div>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
              <table class="table table-sm mb-0">
                <thead class="table-light sticky-top">
                  <tr>
                    <th>Timestamp</th>
                    <th>User</th>
                    <th>Action</th>
                    <th>Client/Document</th>
                    <th>IP Address</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="entry in filteredAuditEntries" :key="entry.id" 
                      :class="{'table-warning': entry.compliance_relevant}">
                    <td class="small">{{ formatTimestamp(entry.timestamp) }}</td>
                    <td class="small">{{ entry.user_name }}</td>
                    <td class="small">
                      <span class="badge" :class="getActionBadgeClass(entry.action)">
                        {{ entry.action_display }}
                      </span>
                    </td>
                    <td class="small">{{ entry.target_description }}</td>
                    <td class="small font-monospace">{{ entry.user_ip }}</td>
                    <td class="small">
                      <i v-if="entry.success" class="bi bi-check-circle text-success"></i>
                      <i v-else class="bi bi-x-circle text-danger"></i>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="!filteredAuditEntries.length" class="text-center p-4 text-muted">
              <i class="bi bi-info-circle display-1 mb-3"></i>
              <p>No audit entries found for the selected filter.</p>
            </div>
          </div>
          <div class="card-footer">
            <div class="d-flex justify-content-between align-items-center">
              <small class="text-muted">
                Showing {{ filteredAuditEntries.length }} of {{ auditEntries.length }} entries
              </small>
              <router-link to="/compliance/audit-trail" class="btn btn-outline-primary btn-sm">
                View Full Audit Trail
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-lg-4">
        <!-- Compliance Metrics -->
        <div class="card mb-3">
          <div class="card-header">
            <h6 class="mb-0">Security Metrics</h6>
          </div>
          <div class="card-body">
            <div class="d-flex justify-content-between mb-2">
              <small>Documents Encrypted:</small>
              <span class="badge bg-success">{{ encryptionStats.encrypted }}/{{ encryptionStats.total }}</span>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <small>Virus Scans Clean:</small>
              <span class="badge bg-success">{{ virusStats.clean }}/{{ virusStats.total }}</span>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <small>PII Documents Flagged:</small>
              <span class="badge bg-info">{{ piiStats.flagged }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <small>Retention Policies Active:</small>
              <span class="badge bg-primary">{{ retentionStats.active }}</span>
            </div>
          </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Compliance Actions</h6>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <router-link to="/compliance/audit-trail" class="btn btn-outline-primary btn-sm">
                <i class="bi bi-list-check"></i> View Full Audit Trail
              </router-link>
              <router-link to="/compliance/retention" class="btn btn-outline-secondary btn-sm">
                <i class="bi bi-clock-history"></i> Manage Retention Policies
              </router-link>
              <button @click="reviewPendingDisposals" class="btn btn-outline-warning btn-sm" :disabled="!pendingDisposals">
                <i class="bi bi-trash"></i> Review Pending Disposals
                <span v-if="pendingDisposals" class="badge bg-warning ms-1">{{ pendingDisposals }}</span>
              </button>
              <router-link to="/compliance/reports" class="btn btn-outline-success btn-sm">
                <i class="bi bi-file-text"></i> Generate FINRA Report
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Document Retention Timeline -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Document Retention Timeline</h5>
          </div>
          <div class="card-body">
            <div v-if="upcomingRetentionEvents.length" class="timeline">
              <div v-for="event in upcomingRetentionEvents" :key="event.id" 
                   class="timeline-item d-flex align-items-center mb-3">
                <div class="timeline-marker me-3">
                  <i class="bi bi-calendar-event text-primary"></i>
                </div>
                <div class="timeline-content flex-grow-1">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="mb-1">{{ event.document_title }}</h6>
                      <p class="text-muted mb-1">
                        <strong>{{ event.action }}</strong> scheduled for {{ formatDate(event.scheduled_date) }}
                      </p>
                      <small class="text-muted">Category: {{ event.category }}</small>
                    </div>
                    <div>
                      <span class="badge" :class="getRetentionBadgeClass(event.days_until)">
                        {{ event.days_until }} days
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center p-4 text-muted">
              <i class="bi bi-check-circle display-1 mb-3 text-success"></i>
              <p>All documents are compliant with retention policies.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ComplianceDashboard',
  
  setup() {
    const auditEntries = ref([])
    const auditFilter = ref('all')
    const isGenerating = ref(false)
    const isExporting = ref(false)
    
    // Compliance stats
    const totalClientsTracked = ref(0)
    const documentsRetained = ref(0)
    const piiDocumentsSecured = ref(0)
    const pendingDisposals = ref(0)
    
    const encryptionStats = ref({ encrypted: 0, total: 0 })
    const virusStats = ref({ clean: 0, total: 0 })
    const piiStats = ref({ flagged: 0 })
    const retentionStats = ref({ active: 0 })
    
    const upcomingRetentionEvents = ref([])
    
    const filteredAuditEntries = computed(() => {
      if (auditFilter.value === 'all') return auditEntries.value
      return auditEntries.value.filter(entry => entry.category === auditFilter.value)
    })
    
    const loadComplianceData = async () => {
      try {
        // For now, using mock data since backend isn't implemented yet
        // In production: const response = await fetch('/api/compliance/dashboard/')
        
        // Mock audit entries
        auditEntries.value = [
          {
            id: 1,
            timestamp: new Date().toISOString(),
            user_name: 'John Advisor',
            action: 'document_viewed',
            action_display: 'Document Viewed',
            target_description: 'Client_Financial_Plan.pdf',
            user_ip: '192.168.1.100',
            success: true,
            compliance_relevant: true,
            category: 'document'
          },
          {
            id: 2,
            timestamp: new Date(Date.now() - 300000).toISOString(),
            user_name: 'John Advisor',
            action: 'communication_sent',
            action_display: 'Email Sent',
            target_description: 'Market Update - Client: Smith',
            user_ip: '192.168.1.100',
            success: true,
            compliance_relevant: true,
            category: 'communication'
          },
          {
            id: 3,
            timestamp: new Date(Date.now() - 600000).toISOString(),
            user_name: 'John Advisor',
            action: 'client_data_modified',
            action_display: 'Client Data Updated',
            target_description: 'Client: Johnson - Contact Info',
            user_ip: '192.168.1.100',
            success: true,
            compliance_relevant: true,
            category: 'client_data'
          }
        ]
        
        // Mock stats
        totalClientsTracked.value = 45
        documentsRetained.value = 1247
        piiDocumentsSecured.value = 89
        pendingDisposals.value = 3
        
        encryptionStats.value = { encrypted: 1247, total: 1247 }
        virusStats.value = { clean: 1247, total: 1247 }
        piiStats.value = { flagged: 89 }
        retentionStats.value = { active: 12 }
        
        // Mock retention events
        upcomingRetentionEvents.value = [
          {
            id: 1,
            document_title: 'Client_Contract_2019.pdf',
            action: 'Archive Review',
            scheduled_date: new Date(Date.now() + 86400000 * 30).toISOString(),
            category: 'Contracts',
            days_until: 30
          },
          {
            id: 2,
            document_title: 'Marketing_Brochure_v2.pdf',
            action: 'Disposal Review',
            scheduled_date: new Date(Date.now() + 86400000 * 90).toISOString(),
            category: 'Marketing',
            days_until: 90
          }
        ]
        
      } catch (error) {
        console.error('Error loading compliance data:', error)
      }
    }
    
    const generateComplianceReport = async () => {
      isGenerating.value = true
      try {
        // Mock report generation
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Create and download a mock PDF
        const element = document.createElement('a')
        element.setAttribute('href', 'data:text/plain;charset=utf-8,FINRA Compliance Report\n\nGenerated: ' + new Date().toLocaleString())
        element.setAttribute('download', `FINRA_Compliance_Report_${new Date().toISOString().split('T')[0]}.txt`)
        element.style.display = 'none'
        document.body.appendChild(element)
        element.click()
        document.body.removeChild(element)
        
      } catch (error) {
        console.error('Error generating report:', error)
      } finally {
        isGenerating.value = false
      }
    }
    
    const exportAuditTrail = async () => {
      isExporting.value = true
      try {
        // Mock export
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        const csvContent = [
          'Timestamp,User,Action,Target,IP Address,Status',
          ...auditEntries.value.map(entry => 
            `${entry.timestamp},${entry.user_name},${entry.action_display},"${entry.target_description}",${entry.user_ip},${entry.success ? 'Success' : 'Failed'}`
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
        console.error('Error exporting audit trail:', error)
      } finally {
        isExporting.value = false
      }
    }
    
    const reviewPendingDisposals = () => {
      // Navigate to retention page with filter
      window.location.href = '/compliance/retention?filter=pending_disposal'
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
    
    const getRetentionBadgeClass = (daysUntil) => {
      if (daysUntil <= 7) return 'bg-danger'
      if (daysUntil <= 30) return 'bg-warning'
      return 'bg-info'
    }
    
    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    onMounted(() => {
      loadComplianceData()
      // Set up real-time updates
      setInterval(loadComplianceData, 30000) // Refresh every 30 seconds
    })
    
    return {
      auditEntries,
      auditFilter,
      filteredAuditEntries,
      isGenerating,
      isExporting,
      totalClientsTracked,
      documentsRetained,
      piiDocumentsSecured,
      pendingDisposals,
      encryptionStats,
      virusStats,
      piiStats,
      retentionStats,
      upcomingRetentionEvents,
      loadComplianceData,
      generateComplianceReport,
      exportAuditTrail,
      reviewPendingDisposals,
      getActionBadgeClass,
      getRetentionBadgeClass,
      formatTimestamp,
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

.card-header {
  background-color: rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.table-responsive::-webkit-scrollbar {
  width: 6px;
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
</style>