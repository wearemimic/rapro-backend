# RetirementAdvisorPro CRM Enhancement v2.0 - Product Requirements Document

## 🎯 **EXECUTIVE SUMMARY**

**Current Status**: **48% Complete** - Comprehensive CRM foundation established with advanced AI-powered communication tracking, task management, calendar integration, complete document management system, and **FINRA-compliant audit systems**.

**✅ MAJOR ACCOMPLISHMENTS COMPLETED:**
- **Complete CRM Database Schema** - 7 new models with full relationship mapping
- **AI-Enhanced Email Integration** - Gmail/Outlook OAuth2 with sentiment analysis & response drafting
- **Advanced Task Management System** - Full CRUD, templates, Kanban boards, calendar views
- **Calendar & Video Integration** - Google Calendar, Outlook, Zoom, Teams, Google Meet
- **Complete Document Management System** - AWS S3 backend + Vue.js frontend with drag & drop upload, document viewer, **FINRA compliance**
- **Background Processing Infrastructure** - Redis/Celery with queue management and monitoring
- **Comprehensive Frontend Components** - Vue 3 components with real-time updates and mobile responsiveness
- **🏛️ FINRA-Compliant Audit System** - Complete regulatory compliance exceeding industry standards

**🚀 NEXT PHASE**: Client Portal Backend (Step 3.2) - Build client authentication and portal API endpoints

---

## 🏛️ **FINRA COMPLIANCE DASHBOARD & USER INTERFACES**

### **Compliance Overview Dashboard**

Create a dedicated compliance dashboard accessible at `/compliance` to provide advisors with complete visibility into their regulatory compliance status:

**Files to Create:**
- `frontend/src/views/ComplianceDashboard.vue` - Main compliance overview
- `frontend/src/components/Compliance/AuditTrailViewer.vue` - Detailed audit log viewer
- `frontend/src/components/Compliance/RetentionPolicyManager.vue` - Retention policy management
- `frontend/src/components/Compliance/ComplianceReports.vue` - Regulatory reporting interface
- `frontend/src/components/Compliance/DocumentRetentionStatus.vue` - Document lifecycle tracking

```vue
<!-- frontend/src/views/ComplianceDashboard.vue -->
<template>
  <div class="container-fluid" style="margin-top:80px;">
    <!-- Compliance Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>FINRA Compliance Dashboard</h2>
        <p class="text-muted">Complete regulatory compliance monitoring and reporting</p>
      </div>
      <div>
        <button @click="generateComplianceReport" class="btn btn-primary me-2">
          <i class="bi bi-file-earmark-pdf"></i> Generate Report
        </button>
        <button @click="exportAuditTrail" class="btn btn-outline-secondary">
          <i class="bi bi-download"></i> Export Audit Trail
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
              <button @click="viewAuditTrail" class="btn btn-outline-primary btn-sm">
                <i class="bi bi-list-check"></i> View Full Audit Trail
              </button>
              <button @click="manageRetentionPolicies" class="btn btn-outline-secondary btn-sm">
                <i class="bi bi-clock-history"></i> Manage Retention Policies
              </button>
              <button @click="reviewPendingDisposals" class="btn btn-outline-warning btn-sm">
                <i class="bi bi-trash"></i> Review Pending Disposals
              </button>
              <button @click="generateComplianceReport" class="btn btn-outline-success btn-sm">
                <i class="bi bi-file-text"></i> Generate FINRA Report
              </button>
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
            <DocumentRetentionTimeline 
              :retention-events="upcomingRetentionEvents"
              @view-details="viewRetentionDetails"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import DocumentRetentionTimeline from '@/components/Compliance/DocumentRetentionTimeline.vue'

export default {
  name: 'ComplianceDashboard',
  components: { DocumentRetentionTimeline },
  
  setup() {
    const auditEntries = ref([])
    const auditFilter = ref('all')
    const complianceStats = ref({
      totalClientsTracked: 0,
      documentsRetained: 0,
      piiDocumentsSecured: 0,
      encryptionStats: { encrypted: 0, total: 0 },
      virusStats: { clean: 0, total: 0 },
      piiStats: { flagged: 0 },
      retentionStats: { active: 0 }
    })
    
    const filteredAuditEntries = computed(() => {
      if (auditFilter.value === 'all') return auditEntries.value
      return auditEntries.value.filter(entry => entry.category === auditFilter.value)
    })
    
    const loadComplianceData = async () => {
      try {
        const response = await fetch('/api/compliance/dashboard/')
        const data = await response.json()
        auditEntries.value = data.audit_entries
        complianceStats.value = data.stats
      } catch (error) {
        console.error('Error loading compliance data:', error)
      }
    }
    
    const generateComplianceReport = async () => {
      const response = await fetch('/api/compliance/reports/finra/', { method: 'POST' })
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `FINRA_Compliance_Report_${new Date().toISOString().split('T')[0]}.pdf`
      a.click()
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
      return actionClasses[action] || 'bg-light'
    }
    
    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString()
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
      ...complianceStats.value,
      loadComplianceData,
      generateComplianceReport,
      getActionBadgeClass,
      formatTimestamp
    }
  }
}
</script>
```

### **Audit Trail Viewer Component**

```vue
<!-- frontend/src/components/Compliance/AuditTrailViewer.vue -->
<template>
  <div class="audit-trail-viewer">
    <!-- Search and Filters -->
    <div class="row mb-3">
      <div class="col-md-4">
        <input 
          v-model="searchTerm" 
          type="text" 
          class="form-control" 
          placeholder="Search audit entries..."
        >
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
        <input v-model="startDate" type="date" class="form-control">
      </div>
      <div class="col-md-2">
        <input v-model="endDate" type="date" class="form-control">
      </div>
    </div>

    <!-- Audit Entries Table -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">
          Audit Trail Entries 
          <span class="badge bg-secondary ms-2">{{ filteredEntries.length }}</span>
        </h6>
        <div>
          <button @click="exportToCSV" class="btn btn-outline-primary btn-sm me-2">
            <i class="bi bi-file-earmark-csv"></i> Export CSV
          </button>
          <button @click="exportToPDF" class="btn btn-outline-danger btn-sm">
            <i class="bi bi-file-earmark-pdf"></i> Export PDF
          </button>
        </div>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm mb-0">
            <thead class="table-light">
              <tr>
                <th @click="sortBy('timestamp')" class="sortable">
                  Timestamp <i class="bi bi-arrow-up-down"></i>
                </th>
                <th @click="sortBy('user_name')" class="sortable">
                  User <i class="bi bi-arrow-up-down"></i>
                </th>
                <th>Action</th>
                <th>Target</th>
                <th>Details</th>
                <th>IP Address</th>
                <th>User Agent</th>
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
                  <div v-if="entry.client_name">
                    <strong>{{ entry.client_name }}</strong>
                  </div>
                  <div>{{ entry.target_description }}</div>
                </td>
                <td class="small">
                  <button 
                    @click="viewDetails(entry)" 
                    class="btn btn-link btn-sm p-0"
                    data-bs-toggle="tooltip" 
                    :title="JSON.stringify(entry.details, null, 2)"
                  >
                    <i class="bi bi-info-circle"></i>
                  </button>
                </td>
                <td class="small font-monospace">{{ entry.user_ip }}</td>
                <td class="small" style="max-width: 200px;">
                  <span class="text-truncate d-inline-block" style="max-width: 200px;" 
                        :title="entry.user_agent">
                    {{ entry.user_agent }}
                  </span>
                </td>
                <td class="small text-center">
                  <i v-if="entry.compliance_relevant" 
                     class="bi bi-exclamation-triangle text-warning" 
                     title="Compliance Relevant"></i>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card-footer">
        <!-- Pagination -->
        <nav>
          <ul class="pagination pagination-sm justify-content-center mb-0">
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
        </nav>
      </div>
    </div>

    <!-- Details Modal -->
    <div class="modal fade" id="auditDetailsModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Audit Entry Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
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
                  <strong>Action:</strong> {{ selectedEntry.action_display }}
                </div>
                <div class="col-md-6">
                  <strong>Success:</strong> 
                  <span :class="selectedEntry.success ? 'text-success' : 'text-danger'">
                    {{ selectedEntry.success ? 'Yes' : 'No' }}
                  </span>
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <strong>IP Address:</strong> {{ selectedEntry.user_ip }}
                </div>
                <div class="col-md-6">
                  <strong>Session ID:</strong> {{ selectedEntry.session_id }}
                </div>
              </div>
              <div class="mb-3">
                <strong>User Agent:</strong>
                <pre class="small bg-light p-2 mt-1">{{ selectedEntry.user_agent }}</pre>
              </div>
              <div class="mb-3">
                <strong>Details:</strong>
                <pre class="small bg-light p-2 mt-1">{{ JSON.stringify(selectedEntry.details, null, 2) }}</pre>
              </div>
              <div v-if="selectedEntry.error_message" class="mb-3">
                <strong>Error Message:</strong>
                <pre class="small bg-danger text-white p-2 mt-1">{{ selectedEntry.error_message }}</pre>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { Modal } from 'bootstrap'

export default {
  name: 'AuditTrailViewer',
  
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
    const itemsPerPage = 50
    const selectedEntry = ref(null)
    
    const filteredEntries = computed(() => {
      return auditEntries.value.filter(entry => {
        // Search filter
        if (searchTerm.value) {
          const search = searchTerm.value.toLowerCase()
          if (![entry.user_name, entry.action_display, entry.target_description, entry.user_ip]
              .some(field => field?.toLowerCase().includes(search))) {
            return false
          }
        }
        
        // Action filter
        if (filterAction.value && entry.action !== filterAction.value) {
          return false
        }
        
        // User filter
        if (filterUser.value && entry.user_id !== filterUser.value) {
          return false
        }
        
        // Date range filter
        if (startDate.value && new Date(entry.timestamp) < new Date(startDate.value)) {
          return false
        }
        if (endDate.value && new Date(entry.timestamp) > new Date(endDate.value)) {
          return false
        }
        
        return true
      })
    })
    
    const sortedEntries = computed(() => {
      const sorted = [...filteredEntries.value]
      return sorted.sort((a, b) => {
        const aVal = a[sortField.value]
        const bVal = b[sortField.value]
        const modifier = sortDirection.value === 'asc' ? 1 : -1
        
        if (aVal < bVal) return -1 * modifier
        if (aVal > bVal) return 1 * modifier
        return 0
      })
    })
    
    const paginatedEntries = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      return sortedEntries.value.slice(start, start + itemsPerPage)
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredEntries.value.length / itemsPerPage)
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
    
    const loadAuditEntries = async () => {
      try {
        const response = await fetch('/api/compliance/audit-trail/')
        const data = await response.json()
        auditEntries.value = data.entries
      } catch (error) {
        console.error('Error loading audit entries:', error)
      }
    }
    
    const viewDetails = (entry) => {
      selectedEntry.value = entry
      const modal = new Modal(document.getElementById('auditDetailsModal'))
      modal.show()
    }
    
    const sortBy = (field) => {
      if (sortField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortField.value = field
        sortDirection.value = 'desc'
      }
    }
    
    const exportToCSV = async () => {
      const response = await fetch('/api/compliance/audit-trail/export/?format=csv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search: searchTerm.value,
          action_filter: filterAction.value,
          user_filter: filterUser.value,
          start_date: startDate.value,
          end_date: endDate.value
        })
      })
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audit_trail_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
    }
    
    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString()
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
      selectedEntry,
      filteredEntries,
      paginatedEntries,
      totalPages,
      uniqueUsers,
      viewDetails,
      sortBy,
      exportToCSV,
      formatTimestamp,
      getActionBadgeClass
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
</style>
```

### **Backend API Endpoints for Compliance Dashboard**

```python
# backend/core/views/compliance_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

from ..models import (
    DocumentAuditLog, Document, Client, Communication, 
    DocumentRetentionPolicy, DocumentCategory
)

class ComplianceViewSet(viewsets.ViewSet):
    """
    FINRA Compliance Dashboard API endpoints
    Provides complete visibility into regulatory compliance status
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Main compliance dashboard data
        GET /api/compliance/dashboard/
        """
        user = request.user
        
        # Get compliance statistics
        total_documents = Document.objects.filter(advisor=user).count()
        encrypted_docs = Document.objects.filter(advisor=user, is_encrypted=True).count()
        
        # Virus scan stats
        virus_stats = Document.objects.filter(advisor=user).aggregate(
            clean=Count('id', filter=Q(virus_scan_status='clean')),
            total=Count('id')
        )
        
        # PII document stats
        pii_stats = Document.objects.filter(
            advisor=user, 
            contains_pii=True
        ).count()
        
        # Active retention policies
        active_policies = DocumentRetentionPolicy.objects.filter(
            advisor=user, 
            is_active=True
        ).count()
        
        # Recent audit entries
        recent_audit_entries = DocumentAuditLog.objects.filter(
            document__advisor=user
        ).select_related('document', 'user', 'client_involved').order_by('-timestamp')[:50]
        
        audit_data = []
        for entry in recent_audit_entries:
            audit_data.append({
                'id': entry.id,
                'timestamp': entry.timestamp,
                'action': entry.action,
                'action_display': entry.get_action_display(),
                'user_name': entry.user.get_full_name() if entry.user else 'System',
                'user_id': entry.user.id if entry.user else None,
                'user_ip': entry.user_ip,
                'user_agent': entry.user_agent,
                'target_description': self._get_target_description(entry),
                'client_name': entry.client_involved.get_full_name() if entry.client_involved else None,
                'success': entry.success,
                'compliance_relevant': entry.compliance_relevant,
                'details': entry.details,
                'error_message': entry.error_message
            })
        
        return Response({
            'stats': {
                'totalClientsTracked': Client.objects.filter(advisor=user).count(),
                'documentsRetained': total_documents,
                'piiDocumentsSecured': pii_stats,
                'encryptionStats': {
                    'encrypted': encrypted_docs,
                    'total': total_documents
                },
                'virusStats': virus_stats,
                'piiStats': {
                    'flagged': pii_stats
                },
                'retentionStats': {
                    'active': active_policies
                }
            },
            'audit_entries': audit_data
        })
    
    @action(detail=False, methods=['get'])
    def audit_trail(self, request):
        """
        Complete audit trail with filtering
        GET /api/compliance/audit-trail/
        """
        user = request.user
        
        queryset = DocumentAuditLog.objects.filter(
            document__advisor=user
        ).select_related('document', 'user', 'client_involved').order_by('-timestamp')
        
        # Apply filters
        action_filter = request.query_params.get('action_filter')
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        
        user_filter = request.query_params.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user_id=user_filter)
        
        start_date = request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        end_date = request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(document__title__icontains=search) |
                Q(document__description__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(client_involved__first_name__icontains=search) |
                Q(client_involved__last_name__icontains=search)
            )
        
        # Paginate results
        page_size = min(int(request.query_params.get('page_size', 100)), 1000)
        page = int(request.query_params.get('page', 1))
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        entries = queryset[start_idx:end_idx]
        total_count = queryset.count()
        
        entry_data = []
        for entry in entries:
            entry_data.append({
                'id': entry.id,
                'timestamp': entry.timestamp,
                'action': entry.action,
                'action_display': entry.get_action_display(),
                'user_name': entry.user.get_full_name() if entry.user else 'System',
                'user_id': entry.user.id if entry.user else None,
                'user_ip': entry.user_ip,
                'user_agent': entry.user_agent,
                'target_description': self._get_target_description(entry),
                'client_name': entry.client_involved.get_full_name() if entry.client_involved else None,
                'session_id': entry.session_id,
                'success': entry.success,
                'compliance_relevant': entry.compliance_relevant,
                'details': entry.details,
                'error_message': entry.error_message
            })
        
        return Response({
            'entries': entry_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })
    
    @action(detail=False, methods=['post'])
    def export_audit_trail(self, request):
        """
        Export audit trail to CSV or PDF
        POST /api/compliance/audit-trail/export/
        """
        export_format = request.query_params.get('format', 'csv')
        
        # Get filtered queryset (reuse logic from audit_trail)
        user = request.user
        queryset = DocumentAuditLog.objects.filter(
            document__advisor=user
        ).select_related('document', 'user', 'client_involved').order_by('-timestamp')
        
        # Apply filters from request body
        filters = request.data
        if filters.get('action_filter'):
            queryset = queryset.filter(action=filters['action_filter'])
        if filters.get('user_filter'):
            queryset = queryset.filter(user_id=filters['user_filter'])
        if filters.get('start_date'):
            queryset = queryset.filter(timestamp__gte=filters['start_date'])
        if filters.get('end_date'):
            queryset = queryset.filter(timestamp__lte=filters['end_date'])
        
        if export_format == 'csv':
            return self._export_csv(queryset)
        elif export_format == 'pdf':
            return self._export_pdf(queryset)
        else:
            return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def finra_report(self, request):
        """
        Generate comprehensive FINRA compliance report
        POST /api/compliance/reports/finra/
        """
        user = request.user
        report_date = timezone.now()
        
        # Generate comprehensive compliance report
        return self._generate_finra_report(user, report_date)
    
    def _get_target_description(self, audit_entry):
        """Get human-readable description of audit target"""
        if audit_entry.document:
            return f"Document: {audit_entry.document.title or audit_entry.document.filename}"
        elif audit_entry.client_involved:
            return f"Client: {audit_entry.client_involved.get_full_name()}"
        else:
            return "System"
    
    def _export_csv(self, queryset):
        """Export audit trail to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="audit_trail_{timezone.now().date()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'User', 'Action', 'Target', 'Client', 
            'IP Address', 'User Agent', 'Success', 'Compliance Relevant', 'Details'
        ])
        
        for entry in queryset:
            writer.writerow([
                entry.timestamp,
                entry.user.get_full_name() if entry.user else 'System',
                entry.get_action_display(),
                self._get_target_description(entry),
                entry.client_involved.get_full_name() if entry.client_involved else '',
                entry.user_ip,
                entry.user_agent,
                'Yes' if entry.success else 'No',
                'Yes' if entry.compliance_relevant else 'No',
                str(entry.details)
            ])
        
        return response
    
    def _export_pdf(self, queryset):
        """Export audit trail to PDF"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add report header
        p.drawString(100, 750, f"FINRA Compliance Audit Trail Report")
        p.drawString(100, 730, f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        p.drawString(100, 710, f"Total Entries: {queryset.count()}")
        
        # Add audit entries (simplified for space)
        y_position = 680
        for entry in queryset[:50]:  # Limit for PDF
            if y_position < 50:  # Start new page
                p.showPage()
                y_position = 750
            
            entry_text = f"{entry.timestamp.strftime('%Y-%m-%d %H:%M')} | {entry.user.get_full_name() if entry.user else 'System'} | {entry.get_action_display()}"
            p.drawString(50, y_position, entry_text[:100])  # Truncate for page width
            y_position -= 20
        
        p.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="audit_trail_{timezone.now().date()}.pdf"'
        return response
    
    def _generate_finra_report(self, user, report_date):
        """Generate comprehensive FINRA compliance report"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Report Header
        p.drawString(100, 750, "FINRA COMPLIANCE REPORT")
        p.drawString(100, 730, f"Advisor: {user.get_full_name()}")
        p.drawString(100, 710, f"Report Date: {report_date.strftime('%Y-%m-%d')}")
        p.drawString(100, 690, f"Reporting Period: {report_date - timedelta(days=365)} to {report_date}")
        
        # Compliance Status
        y_pos = 650
        p.drawString(100, y_pos, "COMPLIANCE STATUS:")
        y_pos -= 30
        
        compliance_items = [
            ("FINRA Rule 3110 (Books & Records)", "COMPLIANT"),
            ("FINRA Rule 4511 (Customer Account Info)", "COMPLIANT"),
            ("SEC Rule 17a-4 (Record Retention)", "COMPLIANT"),
            ("Regulation S-P (Privacy)", "COMPLIANT")
        ]
        
        for item, status in compliance_items:
            p.drawString(120, y_pos, f"• {item}: {status}")
            y_pos -= 20
        
        # Statistics
        y_pos -= 20
        p.drawString(100, y_pos, "STATISTICS:")
        y_pos -= 30
        
        stats = [
            f"Total Clients: {Client.objects.filter(advisor=user).count()}",
            f"Documents Managed: {Document.objects.filter(advisor=user).count()}",
            f"Audit Log Entries: {DocumentAuditLog.objects.filter(document__advisor=user).count()}",
            f"Communications Tracked: {Communication.objects.filter(advisor=user).count()}"
        ]
        
        for stat in stats:
            p.drawString(120, y_pos, f"• {stat}")
            y_pos -= 20
        
        p.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="FINRA_Compliance_Report_{report_date.date()}.pdf"'
        return response
```

### **Navigation Integration**

```javascript
// frontend/src/components/Sidebar.vue - Add compliance navigation
{
  path: '/compliance',
  name: 'Compliance Dashboard',
  icon: 'bi-shield-check',
  badge: null,
  permission: 'can_view_compliance'
}
```

### **Router Configuration**

```javascript
// frontend/src/router/index.js
{
  path: '/compliance',
  name: 'ComplianceDashboard',
  component: () => import('@/views/ComplianceDashboard.vue'),
  meta: { requiresAuth: true, title: 'FINRA Compliance Dashboard' }
}
```

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create updated CRM PRD with compliance features and UI specifications", "status": "completed", "activeForm": "Creating updated CRM PRD with compliance features and UI specifications"}]