<template>
  <div class="report-scheduler">
    <!-- Dashboard Overview -->
    <div class="scheduler-dashboard mb-4">
      <div class="row">
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card stat-card">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="stat-icon bg-primary">
                  <i class="fas fa-clock"></i>
                </div>
                <div class="ms-3">
                  <div class="stat-value">{{ stats.total_schedules || 0 }}</div>
                  <div class="stat-label">Total Schedules</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card stat-card">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="stat-icon bg-success">
                  <i class="fas fa-play-circle"></i>
                </div>
                <div class="ms-3">
                  <div class="stat-value">{{ stats.active_schedules || 0 }}</div>
                  <div class="stat-label">Active</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card stat-card">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="stat-icon bg-warning">
                  <i class="fas fa-pause-circle"></i>
                </div>
                <div class="ms-3">
                  <div class="stat-value">{{ stats.paused_schedules || 0 }}</div>
                  <div class="stat-label">Paused</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card stat-card">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="stat-icon bg-info">
                  <i class="fas fa-chart-line"></i>
                </div>
                <div class="ms-3">
                  <div class="stat-value">{{ stats.success_rate || 0 }}%</div>
                  <div class="stat-label">Success Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>
        <i class="fas fa-calendar-alt me-2"></i>Report Schedules
      </h4>
      <button 
        @click="showCreateModal = true"
        class="btn btn-primary"
      >
        <i class="fas fa-plus me-1"></i>Create Schedule
      </button>
    </div>

    <!-- Upcoming Schedules -->
    <div v-if="stats.upcoming_schedules && stats.upcoming_schedules.length > 0" class="upcoming-schedules mb-4">
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="fas fa-calendar-check me-2"></i>Upcoming Executions
          </h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div 
              v-for="schedule in stats.upcoming_schedules" 
              :key="schedule.id"
              class="col-md-4 mb-3"
            >
              <div class="upcoming-item p-3 border rounded">
                <div class="fw-medium">{{ schedule.name }}</div>
                <div class="text-muted small">{{ schedule.frequency }}</div>
                <div class="text-primary small">
                  <i class="fas fa-clock me-1"></i>
                  {{ formatDate(schedule.next_run) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedules Filter -->
    <div class="schedules-filter mb-3">
      <div class="row">
        <div class="col-md-3">
          <select v-model="filters.status" class="form-select" @change="loadSchedules">
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="disabled">Disabled</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div class="col-md-3">
          <select v-model="filters.frequency" class="form-select" @change="loadSchedules">
            <option value="">All Frequencies</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        <div class="col-md-3">
          <button @click="loadSchedules" class="btn btn-outline-secondary">
            <i class="fas fa-sync me-1"></i>Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Schedules List -->
    <div class="schedules-list">
      <div v-if="isLoadingSchedules" class="text-center py-4">
        <div class="spinner-border text-primary" role="status"></div>
        <div class="mt-2">Loading schedules...</div>
      </div>

      <div v-else-if="schedules.length === 0" class="text-center py-5">
        <i class="fas fa-calendar-plus fa-3x text-muted mb-3"></i>
        <h6 class="text-muted">No report schedules found</h6>
        <p class="text-muted">Create your first schedule to automate report generation</p>
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Frequency</th>
              <th>Next Run</th>
              <th>Success Rate</th>
              <th>Template</th>
              <th>Target</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="schedule in schedules" :key="schedule.id">
              <td>
                <div class="fw-medium">{{ schedule.name }}</div>
                <small v-if="schedule.description" class="text-muted">{{ schedule.description }}</small>
              </td>
              <td>
                <span class="badge" :class="getStatusBadgeClass(schedule.status)">
                  {{ getStatusLabel(schedule.status) }}
                </span>
              </td>
              <td>
                <div class="text-capitalize">{{ schedule.frequency }}</div>
                <small class="text-muted">{{ getFrequencyDetails(schedule) }}</small>
              </td>
              <td>
                <div v-if="schedule.next_run" class="text-nowrap">
                  {{ formatDateTime(schedule.next_run) }}
                </div>
                <small v-else class="text-muted">Not scheduled</small>
              </td>
              <td>
                <div class="d-flex align-items-center">
                  <div class="progress me-2" style="width: 60px; height: 8px;">
                    <div 
                      class="progress-bar bg-success" 
                      :style="`width: ${schedule.success_rate}%`"
                    ></div>
                  </div>
                  <small>{{ schedule.success_rate }}%</small>
                </div>
                <small class="text-muted">{{ schedule.success_count }}/{{ schedule.run_count }} runs</small>
              </td>
              <td>
                <div class="fw-medium">{{ schedule.template.name }}</div>
              </td>
              <td>
                <div v-if="schedule.client">
                  <i class="fas fa-user me-1"></i>{{ schedule.client.name }}
                </div>
                <div v-else-if="schedule.scenario">
                  <i class="fas fa-chart-line me-1"></i>{{ schedule.scenario.name }}
                </div>
                <div v-else>
                  <i class="fas fa-users me-1"></i>Bulk
                </div>
              </td>
              <td>
                <div class="btn-group btn-group-sm">
                  <button 
                    @click="viewSchedule(schedule.id)"
                    class="btn btn-outline-primary"
                    title="View Details"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    @click="editSchedule(schedule.id)"
                    class="btn btn-outline-secondary"
                    title="Edit"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button 
                    v-if="schedule.status === 'active'"
                    @click="pauseSchedule(schedule.id)"
                    class="btn btn-outline-warning"
                    title="Pause"
                  >
                    <i class="fas fa-pause"></i>
                  </button>
                  <button 
                    v-else-if="schedule.status === 'paused'"
                    @click="resumeSchedule(schedule.id)"
                    class="btn btn-outline-success"
                    title="Resume"
                  >
                    <i class="fas fa-play"></i>
                  </button>
                  <button 
                    @click="runScheduleNow(schedule.id)"
                    class="btn btn-outline-info"
                    title="Run Now"
                  >
                    <i class="fas fa-play-circle"></i>
                  </button>
                  <button 
                    @click="deleteSchedule(schedule.id)"
                    class="btn btn-outline-danger"
                    title="Delete"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <nav v-if="pagination.total_pages > 1" class="mt-4">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: !pagination.has_previous }">
            <button 
              class="page-link" 
              @click="changePage(pagination.page - 1)"
              :disabled="!pagination.has_previous"
            >
              Previous
            </button>
          </li>
          <li 
            v-for="page in getVisiblePages()" 
            :key="page"
            class="page-item" 
            :class="{ active: page === pagination.page }"
          >
            <button class="page-link" @click="changePage(page)">{{ page }}</button>
          </li>
          <li class="page-item" :class="{ disabled: !pagination.has_next }">
            <button 
              class="page-link" 
              @click="changePage(pagination.page + 1)"
              :disabled="!pagination.has_next"
            >
              Next
            </button>
          </li>
        </ul>
      </nav>
    </div>

    <!-- Create/Edit Schedule Modal -->
    <ScheduleFormModal
      v-if="showCreateModal || showEditModal"
      :show="showCreateModal || showEditModal"
      :schedule="editingSchedule"
      @close="closeModal"
      @save="handleScheduleSave"
    />

    <!-- Schedule Details Modal -->
    <ScheduleDetailsModal
      v-if="showDetailsModal"
      :show="showDetailsModal"
      :schedule-id="viewingScheduleId"
      @close="showDetailsModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import ScheduleFormModal from './ScheduleFormModal.vue'
import ScheduleDetailsModal from './ScheduleDetailsModal.vue'

export default {
  name: 'ReportScheduler',
  components: {
    ScheduleFormModal,
    ScheduleDetailsModal
  },
  setup() {
    // Reactive data
    const isLoadingSchedules = ref(false)
    const schedules = ref([])
    const stats = ref({})
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDetailsModal = ref(false)
    const editingSchedule = ref(null)
    const viewingScheduleId = ref(null)
    
    const filters = ref({
      status: '',
      frequency: '',
      page: 1
    })
    
    const pagination = ref({
      page: 1,
      page_size: 20,
      total_count: 0,
      total_pages: 0,
      has_next: false,
      has_previous: false
    })

    // Methods
    const loadStats = async () => {
      try {
        const response = await api.get('/api/report-center/schedules/stats/')
        stats.value = response.data
      } catch (error) {
        console.error('Error loading dashboard stats:', error)
      }
    }

    const loadSchedules = async () => {
      try {
        isLoadingSchedules.value = true
        
        const params = {
          page: pagination.value.page,
          page_size: pagination.value.page_size
        }
        
        if (filters.value.status) {
          params.status = filters.value.status
        }
        
        if (filters.value.frequency) {
          params.frequency = filters.value.frequency
        }

        const response = await api.get('/api/report-center/schedules/', { params })
        
        schedules.value = response.data.schedules
        pagination.value = response.data.pagination
      } catch (error) {
        console.error('Error loading schedules:', error)
      } finally {
        isLoadingSchedules.value = false
      }
    }

    const changePage = (page) => {
      pagination.value.page = page
      loadSchedules()
    }

    const getVisiblePages = () => {
      const current = pagination.value.page
      const total = pagination.value.total_pages
      const visible = []
      
      const start = Math.max(1, current - 2)
      const end = Math.min(total, current + 2)
      
      for (let i = start; i <= end; i++) {
        visible.push(i)
      }
      
      return visible
    }

    const viewSchedule = (scheduleId) => {
      viewingScheduleId.value = scheduleId
      showDetailsModal.value = true
    }

    const editSchedule = async (scheduleId) => {
      try {
        const response = await api.get(`/api/report-center/schedules/${scheduleId}/`)
        editingSchedule.value = response.data
        showEditModal.value = true
      } catch (error) {
        console.error('Error loading schedule for editing:', error)
      }
    }

    const pauseSchedule = async (scheduleId) => {
      try {
        await api.post(`/api/report-center/schedules/${scheduleId}/pause/`)
        await loadSchedules()
        await loadStats()
      } catch (error) {
        console.error('Error pausing schedule:', error)
      }
    }

    const resumeSchedule = async (scheduleId) => {
      try {
        await api.post(`/api/report-center/schedules/${scheduleId}/resume/`)
        await loadSchedules()
        await loadStats()
      } catch (error) {
        console.error('Error resuming schedule:', error)
      }
    }

    const runScheduleNow = async (scheduleId) => {
      if (!confirm('Are you sure you want to run this schedule now?')) {
        return
      }
      
      try {
        await api.post(`/api/report-center/schedules/${scheduleId}/run/`)
        // Show success message
        console.log('Schedule executed successfully')
        await loadStats()
      } catch (error) {
        console.error('Error running schedule:', error)
      }
    }

    const deleteSchedule = async (scheduleId) => {
      if (!confirm('Are you sure you want to delete this schedule? This action cannot be undone.')) {
        return
      }
      
      try {
        await api.delete(`/api/report-center/schedules/${scheduleId}/`)
        await loadSchedules()
        await loadStats()
      } catch (error) {
        console.error('Error deleting schedule:', error)
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingSchedule.value = null
    }

    const handleScheduleSave = async () => {
      closeModal()
      await loadSchedules()
      await loadStats()
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        active: 'bg-success',
        paused: 'bg-warning text-dark',
        disabled: 'bg-secondary',
        completed: 'bg-info'
      }
      return classes[status] || 'bg-secondary'
    }

    const getStatusLabel = (status) => {
      const labels = {
        active: 'Active',
        paused: 'Paused',
        disabled: 'Disabled',
        completed: 'Completed'
      }
      return labels[status] || status
    }

    const getFrequencyDetails = (schedule) => {
      const config = schedule.frequency_config
      
      switch (schedule.frequency) {
        case 'weekly':
          const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
          return config.day_of_week !== undefined ? days[config.day_of_week] : ''
        case 'monthly':
          return config.day_of_month ? `Day ${config.day_of_month}` : ''
        case 'custom':
          return config.interval_value && config.interval_type 
            ? `Every ${config.interval_value} ${config.interval_type}`
            : ''
        default:
          return ''
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Lifecycle
    onMounted(() => {
      loadStats()
      loadSchedules()
      
      // Auto-refresh stats periodically
      const refreshInterval = setInterval(() => {
        loadStats()
      }, 30000) // Refresh every 30 seconds
      
      // Cleanup interval on unmount
      return () => clearInterval(refreshInterval)
    })

    return {
      // Data
      isLoadingSchedules,
      schedules,
      stats,
      showCreateModal,
      showEditModal,
      showDetailsModal,
      editingSchedule,
      viewingScheduleId,
      filters,
      pagination,
      
      // Methods
      loadSchedules,
      changePage,
      getVisiblePages,
      viewSchedule,
      editSchedule,
      pauseSchedule,
      resumeSchedule,
      runScheduleNow,
      deleteSchedule,
      closeModal,
      handleScheduleSave,
      getStatusBadgeClass,
      getStatusLabel,
      getFrequencyDetails,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.report-scheduler {
  padding: 2rem 0;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c3e50;
}

.stat-label {
  color: #6c757d;
  font-size: 0.875rem;
}

.upcoming-item {
  background: #f8f9fa;
  transition: all 0.2s;
}

.upcoming-item:hover {
  background: #e9ecef;
  transform: translateY(-1px);
}

.schedules-list {
  min-height: 400px;
}

.progress {
  margin-bottom: 0;
}

.btn-group-sm > .btn {
  font-size: 0.75rem;
}

.page-link {
  color: #007bff;
}

.page-item.active .page-link {
  background-color: #007bff;
  border-color: #007bff;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .stat-card {
    margin-bottom: 1rem;
  }
  
  .btn-group-sm {
    flex-direction: column;
    width: 100%;
  }
  
  .btn-group-sm > .btn {
    border-radius: 0.25rem !important;
    margin-bottom: 0.25rem;
  }
}
</style>