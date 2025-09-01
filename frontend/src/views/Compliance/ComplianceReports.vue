<template>
  <div class="compliance-reports container-fluid" style="margin-top:80px;">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>Compliance Reports</h2>
        <p class="text-muted">Generate comprehensive FINRA and SEC compliance reports for regulatory examinations</p>
      </div>
      <div>
        <button @click="scheduleReport" class="btn btn-outline-primary me-2">
          <i class="bi bi-calendar-plus"></i> Schedule Report
        </button>
        <button @click="showCustomReportModal = true" class="btn btn-primary">
          <i class="bi bi-plus-circle"></i> Custom Report
        </button>
      </div>
    </div>

    <!-- Quick Report Generation -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card h-100 report-card" @click="generateFINRAReport" :class="{ 'generating': isGeneratingFINRA }">
          <div class="card-body text-center">
            <i class="bi bi-shield-check display-1 text-primary mb-3"></i>
            <h5>FINRA Compliance Report</h5>
            <p class="text-muted small">Complete regulatory compliance overview</p>
            <button class="btn btn-primary btn-sm" :disabled="isGeneratingFINRA">
              <span v-if="isGeneratingFINRA">Generating...</span>
              <span v-else>Generate Now</span>
            </button>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100 report-card" @click="generateAuditReport" :class="{ 'generating': isGeneratingAudit }">
          <div class="card-body text-center">
            <i class="bi bi-list-check display-1 text-success mb-3"></i>
            <h5>Audit Trail Report</h5>
            <p class="text-muted small">Complete activity and access logs</p>
            <button class="btn btn-success btn-sm" :disabled="isGeneratingAudit">
              <span v-if="isGeneratingAudit">Generating...</span>
              <span v-else>Generate Now</span>
            </button>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100 report-card" @click="generateRetentionReport" :class="{ 'generating': isGeneratingRetention }">
          <div class="card-body text-center">
            <i class="bi bi-clock-history display-1 text-warning mb-3"></i>
            <h5>Document Retention</h5>
            <p class="text-muted small">Retention policies and compliance status</p>
            <button class="btn btn-warning btn-sm" :disabled="isGeneratingRetention">
              <span v-if="isGeneratingRetention">Generating...</span>
              <span v-else>Generate Now</span>
            </button>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100 report-card" @click="generateSecurityReport" :class="{ 'generating': isGeneratingSecurity }">
          <div class="card-body text-center">
            <i class="bi bi-lock display-1 text-info mb-3"></i>
            <h5>Security Report</h5>
            <p class="text-muted small">Encryption, access controls, and security metrics</p>
            <button class="btn btn-info btn-sm" :disabled="isGeneratingSecurity">
              <span v-if="isGeneratingSecurity">Generating...</span>
              <span v-else>Generate Now</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Report History -->
    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Report History</h5>
            <div>
              <button @click="refreshReports" class="btn btn-outline-secondary btn-sm">
                <i class="bi bi-arrow-clockwise"></i> Refresh
              </button>
            </div>
          </div>
          <div class="card-body p-0">
            <div v-if="reportHistory.length" class="table-responsive">
              <table class="table mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Report Name</th>
                    <th>Type</th>
                    <th>Generated</th>
                    <th>Period</th>
                    <th>Size</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="report in reportHistory" :key="report.id">
                    <td>
                      <div class="fw-bold">{{ report.name }}</div>
                      <small class="text-muted">{{ report.description }}</small>
                    </td>
                    <td>
                      <span class="badge" :class="getReportTypeBadge(report.type)">
                        {{ report.type }}
                      </span>
                    </td>
                    <td>
                      <div>{{ formatDateTime(report.generated_at) }}</div>
                      <small class="text-muted">by {{ report.generated_by }}</small>
                    </td>
                    <td>
                      <small>{{ formatDateRange(report.period_start, report.period_end) }}</small>
                    </td>
                    <td>{{ formatFileSize(report.file_size) }}</td>
                    <td>
                      <span class="badge" :class="getStatusBadge(report.status)">
                        {{ report.status }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button @click="downloadReport(report)" 
                                class="btn btn-outline-primary" 
                                :disabled="report.status !== 'Ready'">
                          <i class="bi bi-download"></i>
                        </button>
                        <button @click="viewReport(report)" 
                                class="btn btn-outline-secondary"
                                :disabled="report.status !== 'Ready'">
                          <i class="bi bi-eye"></i>
                        </button>
                        <button @click="shareReport(report)" 
                                class="btn btn-outline-info"
                                :disabled="report.status !== 'Ready'">
                          <i class="bi bi-share"></i>
                        </button>
                        <button @click="deleteReport(report)" 
                                class="btn btn-outline-danger">
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center p-4 text-muted">
              <i class="bi bi-file-earmark-text display-1 mb-3"></i>
              <p>No reports generated yet. Create your first compliance report above.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <!-- Report Templates -->
        <div class="card mb-4">
          <div class="card-header">
            <h6 class="mb-0">Report Templates</h6>
          </div>
          <div class="card-body">
            <div class="list-group list-group-flush">
              <div v-for="template in reportTemplates" :key="template.id" 
                   class="list-group-item d-flex justify-content-between align-items-center p-2">
                <div>
                  <div class="fw-bold">{{ template.name }}</div>
                  <small class="text-muted">{{ template.description }}</small>
                </div>
                <button @click="useTemplate(template)" class="btn btn-outline-primary btn-sm">
                  Use
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Compliance Status -->
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Current Compliance Status</h6>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="fw-bold">FINRA Rule 3110</span>
                <span class="badge bg-success">Compliant</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-success" style="width: 100%"></div>
              </div>
              <small class="text-muted">Books & Records - Last audit: {{ lastAuditDate }}</small>
            </div>
            
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="fw-bold">SEC Rule 17a-4</span>
                <span class="badge bg-success">Compliant</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-success" style="width: 100%"></div>
              </div>
              <small class="text-muted">Record Retention - {{ retentionStats.compliant }} docs compliant</small>
            </div>
            
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="fw-bold">Document Security</span>
                <span class="badge bg-success">100%</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-success" style="width: 100%"></div>
              </div>
              <small class="text-muted">{{ securityStats.encrypted }} docs encrypted</small>
            </div>
            
            <div>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="fw-bold">Audit Trail</span>
                <span class="badge bg-info">Active</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-info" style="width: 95%"></div>
              </div>
              <small class="text-muted">{{ auditStats.entries }} entries in last 30 days</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Report Modal -->
    <div class="modal fade" id="customReportModal" tabindex="-1" v-if="showCustomReportModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Custom Compliance Report</h5>
            <button type="button" class="btn-close" @click="showCustomReportModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="generateCustomReport">
              <div class="row mb-3">
                <div class="col-md-8">
                  <label class="form-label">Report Name</label>
                  <input v-model="customReport.name" type="text" class="form-control" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Format</label>
                  <select v-model="customReport.format" class="form-select">
                    <option value="pdf">PDF</option>
                    <option value="excel">Excel</option>
                    <option value="csv">CSV</option>
                  </select>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="customReport.description" class="form-control" rows="2"></textarea>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Start Date</label>
                  <input v-model="customReport.startDate" type="date" class="form-control" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">End Date</label>
                  <input v-model="customReport.endDate" type="date" class="form-control" required>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Report Sections</label>
                <div class="row">
                  <div class="col-md-6">
                    <div class="form-check">
                      <input v-model="customReport.includeAuditTrail" class="form-check-input" type="checkbox" id="includeAudit">
                      <label class="form-check-label" for="includeAudit">Audit Trail</label>
                    </div>
                    <div class="form-check">
                      <input v-model="customReport.includeDocuments" class="form-check-input" type="checkbox" id="includeDocs">
                      <label class="form-check-label" for="includeDocs">Document Management</label>
                    </div>
                    <div class="form-check">
                      <input v-model="customReport.includeCommunications" class="form-check-input" type="checkbox" id="includeComms">
                      <label class="form-check-label" for="includeComms">Communications</label>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="form-check">
                      <input v-model="customReport.includeRetention" class="form-check-input" type="checkbox" id="includeRetention">
                      <label class="form-check-label" for="includeRetention">Retention Policies</label>
                    </div>
                    <div class="form-check">
                      <input v-model="customReport.includeSecurity" class="form-check-input" type="checkbox" id="includeSecurity">
                      <label class="form-check-label" for="includeSecurity">Security Metrics</label>
                    </div>
                    <div class="form-check">
                      <input v-model="customReport.includeClients" class="form-check-input" type="checkbox" id="includeClients">
                      <label class="form-check-label" for="includeClients">Client Data</label>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Client Filter (Optional)</label>
                <select v-model="customReport.clientFilter" class="form-select">
                  <option value="">All Clients</option>
                  <option v-for="client in clients" :key="client.id" :value="client.id">
                    {{ client.name }}
                  </option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCustomReportModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="generateCustomReport" :disabled="isGeneratingCustom">
              <span v-if="isGeneratingCustom">Generating...</span>
              <span v-else>Generate Report</span>
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
  name: 'ComplianceReports',
  
  setup() {
    const reportHistory = ref([])
    const reportTemplates = ref([])
    const clients = ref([])
    const showCustomReportModal = ref(false)
    const customReport = ref({
      name: '',
      description: '',
      format: 'pdf',
      startDate: '',
      endDate: '',
      includeAuditTrail: true,
      includeDocuments: true,
      includeCommunications: true,
      includeRetention: true,
      includeSecurity: true,
      includeClients: false,
      clientFilter: ''
    })
    
    // Loading states
    const isGeneratingFINRA = ref(false)
    const isGeneratingAudit = ref(false)
    const isGeneratingRetention = ref(false)
    const isGeneratingSecurity = ref(false)
    const isGeneratingCustom = ref(false)
    
    // Stats
    const lastAuditDate = ref('2024-08-15')
    const retentionStats = ref({ compliant: 1247 })
    const securityStats = ref({ encrypted: 1247 })
    const auditStats = ref({ entries: 1850 })
    
    const loadReportData = async () => {
      try {
        // Mock data - in production would fetch from API
        
        reportHistory.value = [
          {
            id: 1,
            name: 'Monthly FINRA Compliance Report',
            description: 'Complete regulatory compliance overview for August 2024',
            type: 'FINRA',
            generated_at: new Date(Date.now() - 86400000 * 2).toISOString(),
            generated_by: 'John Advisor',
            period_start: new Date(Date.now() - 86400000 * 32).toISOString(),
            period_end: new Date(Date.now() - 86400000 * 2).toISOString(),
            file_size: 2547892,
            status: 'Ready',
            format: 'pdf'
          },
          {
            id: 2,
            name: 'Audit Trail Report - Q3 2024',
            description: 'Complete activity logs for third quarter',
            type: 'Audit Trail',
            generated_at: new Date(Date.now() - 86400000 * 7).toISOString(),
            generated_by: 'John Advisor',
            period_start: new Date(Date.now() - 86400000 * 92).toISOString(),
            period_end: new Date(Date.now() - 86400000 * 7).toISOString(),
            file_size: 1847293,
            status: 'Ready',
            format: 'excel'
          },
          {
            id: 3,
            name: 'Document Retention Analysis',
            description: 'Retention policy compliance and upcoming events',
            type: 'Retention',
            generated_at: new Date(Date.now() - 86400000 * 1).toISOString(),
            generated_by: 'System',
            period_start: new Date(Date.now() - 86400000 * 365).toISOString(),
            period_end: new Date().toISOString(),
            file_size: 892473,
            status: 'Generating',
            format: 'pdf'
          }
        ]
        
        reportTemplates.value = [
          {
            id: 1,
            name: 'FINRA Examination',
            description: 'Standard FINRA regulatory examination report',
            sections: ['audit_trail', 'documents', 'communications', 'retention']
          },
          {
            id: 2,
            name: 'SEC Compliance',
            description: 'SEC Rule 17a-4 compliance documentation',
            sections: ['retention', 'documents', 'security']
          },
          {
            id: 3,
            name: 'Internal Audit',
            description: 'Monthly internal compliance review',
            sections: ['audit_trail', 'security', 'communications']
          },
          {
            id: 4,
            name: 'Client Data Review',
            description: 'Client information and communication summary',
            sections: ['clients', 'communications', 'documents']
          }
        ]
        
        clients.value = [
          { id: 1, name: 'Smith, Robert' },
          { id: 2, name: 'Johnson, Mary' },
          { id: 3, name: 'Williams, Carol' },
          { id: 4, name: 'Brown, Michael' },
          { id: 5, name: 'Davis, Jennifer' }
        ]
        
        // Set default dates for custom report
        const today = new Date()
        const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
        customReport.value.endDate = today.toISOString().split('T')[0]
        customReport.value.startDate = thirtyDaysAgo.toISOString().split('T')[0]
        
      } catch (error) {
        console.error('Error loading report data:', error)
      }
    }
    
    const generateFINRAReport = async () => {
      isGeneratingFINRA.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        // Add to report history
        const newReport = {
          id: Date.now(),
          name: 'FINRA Compliance Report - ' + new Date().toLocaleDateString(),
          description: 'Complete regulatory compliance overview',
          type: 'FINRA',
          generated_at: new Date().toISOString(),
          generated_by: 'Current User',
          period_start: new Date(Date.now() - 86400000 * 30).toISOString(),
          period_end: new Date().toISOString(),
          file_size: 2100000 + Math.random() * 1000000,
          status: 'Ready',
          format: 'pdf'
        }
        
        reportHistory.value.unshift(newReport)
        
        // Mock download
        downloadMockReport('FINRA_Compliance_Report', 'pdf')
        
      } catch (error) {
        console.error('Error generating FINRA report:', error)
      } finally {
        isGeneratingFINRA.value = false
      }
    }
    
    const generateAuditReport = async () => {
      isGeneratingAudit.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 2500))
        
        const newReport = {
          id: Date.now(),
          name: 'Audit Trail Report - ' + new Date().toLocaleDateString(),
          description: 'Complete activity and access logs',
          type: 'Audit Trail',
          generated_at: new Date().toISOString(),
          generated_by: 'Current User',
          period_start: new Date(Date.now() - 86400000 * 30).toISOString(),
          period_end: new Date().toISOString(),
          file_size: 1800000 + Math.random() * 500000,
          status: 'Ready',
          format: 'excel'
        }
        
        reportHistory.value.unshift(newReport)
        downloadMockReport('Audit_Trail_Report', 'xlsx')
        
      } catch (error) {
        console.error('Error generating audit report:', error)
      } finally {
        isGeneratingAudit.value = false
      }
    }
    
    const generateRetentionReport = async () => {
      isGeneratingRetention.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        const newReport = {
          id: Date.now(),
          name: 'Document Retention Report - ' + new Date().toLocaleDateString(),
          description: 'Retention policies and compliance status',
          type: 'Retention',
          generated_at: new Date().toISOString(),
          generated_by: 'Current User',
          period_start: new Date(Date.now() - 86400000 * 365).toISOString(),
          period_end: new Date().toISOString(),
          file_size: 900000 + Math.random() * 300000,
          status: 'Ready',
          format: 'pdf'
        }
        
        reportHistory.value.unshift(newReport)
        downloadMockReport('Document_Retention_Report', 'pdf')
        
      } catch (error) {
        console.error('Error generating retention report:', error)
      } finally {
        isGeneratingRetention.value = false
      }
    }
    
    const generateSecurityReport = async () => {
      isGeneratingSecurity.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 2200))
        
        const newReport = {
          id: Date.now(),
          name: 'Security Report - ' + new Date().toLocaleDateString(),
          description: 'Encryption, access controls, and security metrics',
          type: 'Security',
          generated_at: new Date().toISOString(),
          generated_by: 'Current User',
          period_start: new Date(Date.now() - 86400000 * 30).toISOString(),
          period_end: new Date().toISOString(),
          file_size: 1200000 + Math.random() * 400000,
          status: 'Ready',
          format: 'pdf'
        }
        
        reportHistory.value.unshift(newReport)
        downloadMockReport('Security_Report', 'pdf')
        
      } catch (error) {
        console.error('Error generating security report:', error)
      } finally {
        isGeneratingSecurity.value = false
      }
    }
    
    const generateCustomReport = async () => {
      if (!customReport.value.name) return
      
      isGeneratingCustom.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 3500))
        
        const newReport = {
          id: Date.now(),
          name: customReport.value.name,
          description: customReport.value.description,
          type: 'Custom',
          generated_at: new Date().toISOString(),
          generated_by: 'Current User',
          period_start: new Date(customReport.value.startDate).toISOString(),
          period_end: new Date(customReport.value.endDate).toISOString(),
          file_size: 1500000 + Math.random() * 1000000,
          status: 'Ready',
          format: customReport.value.format
        }
        
        reportHistory.value.unshift(newReport)
        downloadMockReport(customReport.value.name.replace(/\s+/g, '_'), customReport.value.format)
        
        showCustomReportModal.value = false
        
        // Reset form
        customReport.value = {
          name: '',
          description: '',
          format: 'pdf',
          startDate: customReport.value.startDate,
          endDate: customReport.value.endDate,
          includeAuditTrail: true,
          includeDocuments: true,
          includeCommunications: true,
          includeRetention: true,
          includeSecurity: true,
          includeClients: false,
          clientFilter: ''
        }
        
      } catch (error) {
        console.error('Error generating custom report:', error)
      } finally {
        isGeneratingCustom.value = false
      }
    }
    
    const downloadMockReport = (reportName, format) => {
      const content = `${reportName}\n\nGenerated: ${new Date().toLocaleString()}\nFormat: ${format}\n\nThis is a mock ${format.toUpperCase()} report download.`
      const extension = format === 'excel' ? 'xlsx' : format
      
      const element = document.createElement('a')
      element.setAttribute('href', `data:text/plain;charset=utf-8,${encodeURIComponent(content)}`)
      element.setAttribute('download', `${reportName}_${new Date().toISOString().split('T')[0]}.${extension}`)
      element.style.display = 'none'
      document.body.appendChild(element)
      element.click()
      document.body.removeChild(element)
    }
    
    const downloadReport = (report) => {
      downloadMockReport(report.name.replace(/\s+/g, '_'), report.format)
    }
    
    const viewReport = (report) => {
      console.log('Viewing report:', report.name)
      // In production, would open report viewer or navigate to report detail page
    }
    
    const shareReport = (report) => {
      console.log('Sharing report:', report.name)
      // In production, would show sharing options modal
    }
    
    const deleteReport = (report) => {
      if (confirm('Are you sure you want to delete this report?')) {
        const index = reportHistory.value.findIndex(r => r.id === report.id)
        if (index !== -1) {
          reportHistory.value.splice(index, 1)
        }
      }
    }
    
    const refreshReports = () => {
      loadReportData()
    }
    
    const scheduleReport = () => {
      console.log('Scheduling report')
      // In production, would show scheduling modal
    }
    
    const useTemplate = (template) => {
      customReport.value.name = template.name + ' - ' + new Date().toLocaleDateString()
      customReport.value.description = template.description
      
      // Set sections based on template
      customReport.value.includeAuditTrail = template.sections.includes('audit_trail')
      customReport.value.includeDocuments = template.sections.includes('documents')
      customReport.value.includeCommunications = template.sections.includes('communications')
      customReport.value.includeRetention = template.sections.includes('retention')
      customReport.value.includeSecurity = template.sections.includes('security')
      customReport.value.includeClients = template.sections.includes('clients')
      
      showCustomReportModal.value = true
    }
    
    const getReportTypeBadge = (type) => {
      const badges = {
        'FINRA': 'bg-primary',
        'Audit Trail': 'bg-success',
        'Retention': 'bg-warning',
        'Security': 'bg-info',
        'Custom': 'bg-secondary'
      }
      return badges[type] || 'bg-light text-dark'
    }
    
    const getStatusBadge = (status) => {
      const badges = {
        'Ready': 'bg-success',
        'Generating': 'bg-warning',
        'Failed': 'bg-danger',
        'Scheduled': 'bg-info'
      }
      return badges[status] || 'bg-secondary'
    }
    
    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString()
    }
    
    const formatDateRange = (startDate, endDate) => {
      const start = new Date(startDate).toLocaleDateString()
      const end = new Date(endDate).toLocaleDateString()
      return `${start} - ${end}`
    }
    
    const formatFileSize = (bytes) => {
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      if (bytes === 0) return '0 Bytes'
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }
    
    onMounted(() => {
      loadReportData()
    })
    
    return {
      reportHistory,
      reportTemplates,
      clients,
      showCustomReportModal,
      customReport,
      isGeneratingFINRA,
      isGeneratingAudit,
      isGeneratingRetention,
      isGeneratingSecurity,
      isGeneratingCustom,
      lastAuditDate,
      retentionStats,
      securityStats,
      auditStats,
      generateFINRAReport,
      generateAuditReport,
      generateRetentionReport,
      generateSecurityReport,
      generateCustomReport,
      downloadReport,
      viewReport,
      shareReport,
      deleteReport,
      refreshReports,
      scheduleReport,
      useTemplate,
      getReportTypeBadge,
      getStatusBadge,
      formatDateTime,
      formatDateRange,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.report-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.report-card.generating {
  opacity: 0.7;
  cursor: not-allowed;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.badge {
  font-size: 0.75em;
}

.list-group-item {
  border-left: none;
  border-right: none;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}

.progress {
  border-radius: 3px;
}
</style>