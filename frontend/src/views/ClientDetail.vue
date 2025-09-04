<template>
  <div class="container-fluid" style="margin-top:80px;">
    <!-- Client Header Card -->
    <div class="row mb-3" v-if="client">
      <div class="col-12">
        <div class="card">
          <div class="card-body d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center">
              <h2 class="mb-0 me-3">{{ client.first_name }} {{ client.last_name }}</h2>
              <span class="badge bg-primary">{{ client.status || 'Active' }}</span>
            </div>
            <div>
              <router-link :to="`/clients/${client.id}/edit`" class="btn btn-secondary me-2">Edit</router-link>
              <button @click="deleteClient" class="btn btn-danger">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Tabbed Interface -->
    <ul class="nav nav-segment mb-3" id="clientDetailTabs" role="tablist">
              <li class="nav-item">
                <a class="nav-link active" id="overview-tab" data-bs-toggle="tab" 
                  href="#overview-pane" role="tab" 
                  aria-controls="overview-pane" aria-selected="true">
                  Overview
                </a>
              </li>
              <li class="nav-item" v-if="hasCRMAccess">
                <a class="nav-link" id="communications-tab" data-bs-toggle="tab" 
                  href="#communications-pane" role="tab" 
                  aria-controls="communications-pane" aria-selected="false">
                  Communications
                  <span v-if="unreadCount > 0" class="badge bg-primary ms-1">{{ unreadCount }}</span>
                </a>
              </li>
              <li class="nav-item" v-if="hasCRMAccess">
                <a class="nav-link" id="activity-tab" data-bs-toggle="tab" 
                  href="#activity-pane" role="tab" 
                  aria-controls="activity-pane" aria-selected="false">
                  Activity
                </a>
              </li>
              <li class="nav-item" v-if="hasCRMAccess">
                <a class="nav-link" id="tasks-tab" data-bs-toggle="tab" 
                  href="#tasks-pane" role="tab" 
                  aria-controls="tasks-pane" aria-selected="false">
                  Tasks
                  <span v-if="clientTasks.length > 0" class="badge bg-info ms-1">{{ clientTasks.length }}</span>
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="documents-tab" data-bs-toggle="tab" 
                  href="#documents-pane" role="tab" 
                  aria-controls="documents-pane" aria-selected="false">
                  Documents
                  <span v-if="clientDocumentCount > 0" class="badge bg-secondary ms-1">{{ clientDocumentCount }}</span>
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="portal-access-tab" data-bs-toggle="tab" 
                  href="#portal-access-pane" role="tab" 
                  aria-controls="portal-access-pane" aria-selected="false">
                  Portal Access
                  <span v-if="client?.portal_access_enabled" class="badge bg-success ms-1">Enabled</span>
                </a>
              </li>
    </ul>
    
    <!-- Tab Content -->
    <div class="tab-content">
            <!-- Overview Tab -->
            <div class="tab-pane fade show active" id="overview-pane" role="tabpanel" 
                 aria-labelledby="overview-tab">
              <!-- Two column layout with reduced spacing -->
              <div class="row gx-3">
                <div class="col-lg-4">
                  <div v-if="client">
                    <div class="card mb-4">
                      <div class="card-body">
                        <h5 class="card-title mb-4">Basic Info</h5>
                        
                        <!-- Primary Client Info -->
                        <div class="client-info-section mb-4">
                          <div class="client-info-item">
                            <span class="info-label">Email:</span>
                            <span class="info-value">{{ client.email }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Birthdate:</span>
                            <span class="info-value">{{ formatDate(client.birthdate) }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Gender:</span>
                            <span class="info-value">{{ client.gender }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Tax Status:</span>
                            <span class="info-value">{{ client.tax_status }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Status:</span>
                            <span class="info-value">
                              <span class="badge" :class="getStatusBadgeClass(client.status)">
                                {{ client.status || 'Active' }}
                              </span>
                            </span>
                          </div>
                        </div>
                        
                        <!-- Spouse Information -->
                        <div v-if="client.spouse" class="spouse-info-section">
                          <div class="section-divider mb-3">
                            <h6 class="mb-0 text-muted">Spouse Information</h6>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Name:</span>
                            <span class="info-value">{{ client.spouse.first_name }} {{ client.spouse.last_name }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Birthdate:</span>
                            <span class="info-value">{{ formatDate(client.spouse.birthdate) }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Gender:</span>
                            <span class="info-value">{{ client.spouse.gender }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="col-lg-8">
                  <div class="card mb-4">
                    <div class="card-body">
                      <div class="card-header d-flex justify-content-between align-items-center">
                        <h4 class="card-header-title">Scenarios</h4>
                        <div v-if="client && client.scenarios && client.scenarios.length">
                          <router-link :to="`/clients/${client.id}/scenarios/new`" class="btn btn-primary text-white">Add Scenario</router-link>
                        </div>
                      </div>
                      <div class="card-body">
                        <div v-if="client && client.scenarios && client.scenarios.length">
                          <table class="table scenarios-table">
                            <thead class="thead-light">
                              <tr>
                                <th scope="col">Name</th>
                                <th scope="col">Income vs Cost %</th>
                                <th scope="col">Medicare/IRMAA %</th>
                                <th scope="col">Actions</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-for="(scenario, index) in client.scenarios" :key="scenario.id">
                                <td class="scenario-name">{{ scenario.name }}</td>
                                <td>
                                  <div class="progress-container">
                                    <div class="progress" style="height: 20px;">
                                      <div class="progress-bar bg-success" 
                                           role="progressbar" 
                                           :style="{ width: (scenario.income_vs_cost_percent || 0) + '%' }"
                                           :aria-valuenow="scenario.income_vs_cost_percent || 0"
                                           aria-valuemin="0" 
                                           aria-valuemax="100">
                                      </div>
                                      <div class="progress-label">
                                        <strong>{{ scenario.income_vs_cost_percent || 0 }}%</strong>
                                      </div>
                                    </div>
                                  </div>
                                </td>
                                <td>
                                  <div class="progress-container">
                                    <div class="progress" style="height: 20px;">
                                      <div class="progress-bar bg-warning" 
                                           role="progressbar" 
                                           :style="{ width: (scenario.medicare_irmaa_percent || 0) + '%' }"
                                           :aria-valuenow="scenario.medicare_irmaa_percent || 0"
                                           aria-valuemin="0" 
                                           aria-valuemax="100">
                                      </div>
                                      <div class="progress-label">
                                        <strong>{{ scenario.medicare_irmaa_percent || 0 }}%</strong>
                                      </div>
                                    </div>
                                  </div>
                                </td>
                                <td>
                                  <div class="btn-group" role="group">
                                    <router-link :to="{ 
                                      name: 'ScenarioDetail',
                                      params: { clientId: client.id, scenarioid: scenario.id },
                                      state: { scenarios: client.scenarios }
                                      }"
                                      class="btn btn-sm btn-outline-primary">
                                      View
                                    </router-link>
                                    <button @click="showDeleteModal(scenario)" class="btn btn-sm btn-outline-danger">Delete</button>
                                  </div>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                        <div v-else>
                          <div class="text-center d-flex flex-column align-items-center" style="margin:50px;">
                            <img src="/assets/svg/illustrations/oc-project-development.svg" alt="No Scenarios" class="mb-3" style="max-width: 50%; height: auto;"/>
                            <router-link :to="`/clients/${client ? client.id : ''}/scenarios/new`" class="btn btn-primary mt-3">Create Your First Scenario!</router-link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Communications Tab -->
            <div class="tab-pane fade" id="communications-pane" role="tabpanel" 
                 aria-labelledby="communications-tab" v-if="hasCRMAccess">
              <div>
                <CommunicationSummaryWidget :client="client" class="mb-4" />
                <CommunicationList 
                  :client-filter="client ? client.id : null" 
                  :show-client-filter="false"
                  :compact-mode="true"
                  class="mt-3" 
                />
              </div>
            </div>
            
            <!-- Activity Tab -->
            <div class="tab-pane fade" id="activity-pane" role="tabpanel" 
                 aria-labelledby="activity-tab" v-if="hasCRMAccess">
              <div>
                <ActivityStream 
                  :client-filter="client ? client.id : null"
                  :max-items="20"
                  :auto-refresh="true"
                  :refresh-interval="30000"
                  @activity-click="handleActivityClick"
                  @action-executed="handleActionExecuted"
                />
              </div>
            </div>
            
            <!-- Tasks Tab -->
            <div class="tab-pane fade" id="tasks-pane" role="tabpanel" 
                 aria-labelledby="tasks-tab" v-if="hasCRMAccess">
              <div>
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5 class="mb-0">Client Tasks</h5>
                  <button @click="showCreateTaskModal" class="btn btn-primary">
                    <i class="bi bi-plus-circle me-2"></i>Create Task
                  </button>
                </div>
                
                <div v-if="loadingTasks" class="text-center py-4">
                  <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading tasks...</span>
                  </div>
                </div>
                
                <div v-else-if="clientTasks.length === 0" class="text-center py-4 text-muted">
                  <i class="bi bi-clipboard-check display-1"></i>
                  <p class="mt-2">No tasks found for this client</p>
                  <button @click="showCreateTaskModal" class="btn btn-outline-primary">
                    Create First Task
                  </button>
                </div>
                
                <div v-else>
                  <div class="row">
                    <div class="col-md-4" v-for="status in ['pending', 'in_progress', 'completed']" :key="status">
                      <div class="card mb-3">
                        <div class="card-header">
                          <h6 class="mb-0 text-capitalize">{{ status.replace('_', ' ') }}</h6>
                          <small class="text-muted">{{ getTasksByStatus(status).length }} tasks</small>
                        </div>
                        <div class="card-body p-2">
                          <div v-for="task in getTasksByStatus(status)" :key="task.id" 
                               class="card mb-2 task-card">
                            <div class="card-body p-2">
                              <h6 class="card-title mb-1">{{ task.title }}</h6>
                              <p class="card-text small text-muted mb-1">{{ task.description }}</p>
                              <div class="d-flex justify-content-between align-items-center">
                                <span class="badge" :class="getPriorityClass(task.priority)">
                                  {{ task.priority }}
                                </span>
                                <div class="btn-group" role="group">
                                  <button @click="editTask(task)" class="btn btn-sm btn-outline-secondary">
                                    <i class="bi bi-pencil"></i>
                                  </button>
                                  <button v-if="task.status !== 'completed'" 
                                          @click="markTaskComplete(task)" 
                                          class="btn btn-sm btn-outline-success">
                                    <i class="bi bi-check"></i>
                                  </button>
                                </div>
                              </div>
                              <div v-if="task.due_date" class="mt-1">
                                <small class="text-muted">
                                  <i class="bi bi-calendar"></i> 
                                  Due: {{ formatDate(task.due_date) }}
                                </small>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Documents Tab -->
            <div class="tab-pane fade" id="documents-pane" role="tabpanel" 
                 aria-labelledby="documents-tab">
              <div>
                <ClientDocuments 
                  v-if="client"
                  :clientId="client.id"
                  :clientName="`${client.first_name} ${client.last_name}`"
                  @document-count-updated="updateDocumentCount"
                />
              </div>
            </div>

            <!-- Portal Access Tab -->
            <div class="tab-pane fade" id="portal-access-pane" role="tabpanel" 
                 aria-labelledby="portal-access-tab">
              <div>
                <ClientPortalAccess 
                  v-if="client"
                  :client="client"
                  @client-updated="loadClient"
                />
              </div>
            </div>
    </div>

    <!-- Task Form Modal -->
    <TaskForm 
      :show="showTaskForm"
      :task="selectedTask"
      :preselected-client-id="client?.id"
      @close="handleTaskFormClose"
      @task-saved="handleTaskSaved"
    />
  </div>
</template>

<script>
import axios from 'axios';
import { API_CONFIG } from '@/config';
import Sortable from 'sortablejs';
import { useCommunicationStore } from '@/stores/communicationStore';
import { hasCRMAccess } from '@/utils/permissions';
import CommunicationList from '@/components/CRM/CommunicationList.vue';
import ActivityStream from '@/components/CRM/ActivityStream.vue';
import CommunicationSummaryWidget from '@/components/CRM/CommunicationSummaryWidget.vue';
import TaskForm from '@/components/TaskForm.vue';
import ClientDocuments from '@/components/ClientDocuments.vue';
import ClientPortalAccess from '@/components/ClientPortalAccess.vue';

export default {
  name: 'ClientDetail',
  components: { 
    CommunicationList,
    ActivityStream,
    CommunicationSummaryWidget,
    TaskForm,
    ClientDocuments,
    ClientPortalAccess
  },
  data() {
    return {
      client: null,
      unreadCount: 0,
      communicationStore: null,
      clientTasks: [],
      loadingTasks: false,
      showTaskForm: false,
      selectedTask: null,
      clientDocumentCount: 0,
    };
  },
  computed: {
    hasCRMAccess() {
      try {
        const { useAuthStore } = require('@/stores/auth');
        const authStore = useAuthStore();
        return hasCRMAccess(authStore.user);
      } catch (error) {
        return hasCRMAccess(null);
      }
    }
  },
  async created() {
    this.communicationStore = useCommunicationStore();
    
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const id = this.$route.params.id;
      
      if (!id) {
        console.error('Client ID is missing from route parameters');
        this.$router.push('/clients');
        return;
      }
      
      try {
        const response = await axios.get(`${API_CONFIG.API_URL}/clients/${id}/`, { headers });
        this.client = response.data;
        await this.loadUnreadCount();
        await this.fetchClientTasks();
      } catch (clientError) {
        console.error('Error loading client details:', clientError);
        this.$router.push('/clients');
        return;
      }
    } catch (error) {
      console.error('Error in created lifecycle:', error);
    }
  },
  methods: {
    async loadClient() {
      try {
        console.log('loadClient called - reloading client data')
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        const id = this.$route.params.id;
        
        if (!id) {
          console.error('Client ID is missing from route parameters');
          return;
        }
        
        console.log('Fetching client data for ID:', id)
        const response = await axios.get(`${API_CONFIG.API_URL}/clients/${id}/`, { headers });
        console.log('API response:', response.data)
        this.client = response.data;
        console.log('Client data reloaded, portal_access_enabled:', this.client.portal_access_enabled);
      } catch (error) {
        console.error('Error loading client details:', error);
      }
    },

    async loadUnreadCount() {
      try {
        if (!this.client) return;
        
        await this.communicationStore.fetchCommunications({
          client_id: this.client.id,
          is_read: false,
          limit: 1
        });
        
        this.unreadCount = this.communicationStore.totalCount || 0;
      } catch (error) {
        console.error('Error loading unread count:', error);
        this.unreadCount = 0;
      }
    },
    handleActivityClick(activity) {
      if (activity.type === 'communication') {
        const communicationsTab = document.getElementById('communications-tab');
        if (communicationsTab) {
          communicationsTab.click();
        }
      }
    },
    handleActionExecuted(action) {
      if (action.type === 'mark_read' || action.type === 'reply') {
        this.loadUnreadCount();
      }
    },
    deleteClient() {
      // Placeholder for delete functionality
      console.log('Delete client:', this.client.id);
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    getStatusBadgeClass(status) {
      switch (status?.toLowerCase()) {
        case 'active':
          return 'bg-success';
        case 'inactive':
          return 'bg-secondary';
        case 'pending':
          return 'bg-warning';
        case 'archived':
          return 'bg-secondary';
        default:
          return 'bg-primary';
      }
    },
    showDeleteModal(scenario) {
      console.log('Delete scenario:', scenario.name);
      // Add modal logic here if needed
    },

    // Task management methods
    async fetchClientTasks() {
      if (!this.client) return;
      
      this.loadingTasks = true;
      try {
        console.log('Fetching tasks for client:', this.client.id);
        const response = await axios.get(`${API_CONFIG.API_URL}/tasks/?client=${this.client.id}`);
        console.log('Client tasks response:', response.data);
        this.clientTasks = response.data || [];
      } catch (error) {
        console.error('Error fetching client tasks:', error);
        this.clientTasks = [];
      } finally {
        this.loadingTasks = false;
      }
    },

    getTasksByStatus(status) {
      return this.clientTasks.filter(task => task.status === status);
    },

    getPriorityClass(priority) {
      switch (priority) {
        case 'high': return 'bg-danger';
        case 'medium': return 'bg-warning';
        case 'low': return 'bg-success';
        case 'urgent': return 'bg-dark';
        default: return 'bg-secondary';
      }
    },

    formatDate(date) {
      return new Date(date).toLocaleDateString();
    },

    showCreateTaskModal() {
      this.selectedTask = null;
      this.showTaskForm = true;
    },

    editTask(task) {
      this.selectedTask = task;
      this.showTaskForm = true;
    },

    async markTaskComplete(task) {
      try {
        const response = await axios.patch(`/api/tasks/${task.id}/`, { 
          status: 'completed' 
        });
        // Update the task in the local array
        const taskIndex = this.clientTasks.findIndex(t => t.id === task.id);
        if (taskIndex !== -1) {
          this.clientTasks[taskIndex] = response.data;
        }
      } catch (error) {
        console.error('Error completing task:', error);
      }
    },

    handleTaskFormClose() {
      this.showTaskForm = false;
      this.selectedTask = null;
    },

    handleTaskSaved() {
      this.handleTaskFormClose();
      this.fetchClientTasks(); // Refresh the task list
    },

    updateDocumentCount(count) {
      this.clientDocumentCount = count;
    }
  }
};
</script>

<style scoped>
/* Tab styling */
.card-header-tabs {
  margin-bottom: -1px;
  border-bottom: none;
}

.card-header-tabs .nav-link {
  border: 1px solid transparent;
  border-bottom: none;
  background: transparent;
  margin-bottom: 0;
  padding: 0.75rem 1rem;
  color: #6c757d;
  font-weight: 500;
  transition: all 0.3s ease;
}

.card-header-tabs .nav-link:hover {
  color: #495057;
  background: #f8f9fa;
  border-top-left-radius: 0.375rem;
  border-top-right-radius: 0.375rem;
}

.card-header-tabs .nav-link.active {
  color: #0d6efd;
  background: #fff;
  border-color: #dee2e6 #dee2e6 #fff;
  border-top-left-radius: 0.375rem;
  border-top-right-radius: 0.375rem;
}

.tab-content {
  border: none;
}

.tab-pane {
  min-height: 400px;
}

/* Client Info Styling */
.client-info-section .client-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.client-info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: #6c757d;
  min-width: 100px;
}

/* Task card styling */
.task-card {
  transition: all 0.2s ease;
  cursor: pointer;
}

.task-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.info-value {
  text-align: right;
  color: #212529;
}

.section-divider {
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

/* Progress Bar Styling */
.progress-container {
  position: relative;
  width: 100%;
}

.progress {
  position: relative;
}

.progress-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #000;
  font-size: 0.875rem;
  z-index: 1;
}

.scenarios-table {
  margin-top: 1rem;
}

.scenarios-table th {
  background-color: #f8f9fa;
  border-top: 1px solid #dee2e6;
  font-weight: 600;
}

.scenario-name {
  font-weight: 600;
  color: #0d6efd;
}
</style>