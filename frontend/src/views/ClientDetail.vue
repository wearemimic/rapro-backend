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
                <a class="nav-link" 
                  :class="{ 'active': activeTab === 'overview' }"
                  id="overview-tab" 
                  @click.prevent="switchTab('overview')"
                  href="#overview-pane" role="tab" 
                  aria-controls="overview-pane" 
                  :aria-selected="activeTab === 'overview'">
                  Overview
                </a>
              </li>
              <li class="nav-item" v-if="hasCRMAccess">
                <a class="nav-link" 
                  :class="{ 'active': activeTab === 'communications' }"
                  id="communications-tab" 
                  @click.prevent="switchTab('communications')"
                  href="#communications-pane" role="tab" 
                  aria-controls="communications-pane" 
                  :aria-selected="activeTab === 'communications'">
                  Communications
                  <span v-if="unreadCount > 0" class="badge bg-primary ms-1">{{ unreadCount }}</span>
                </a>
              </li>
              <li class="nav-item" v-if="hasCRMAccess">
                <a class="nav-link" 
                  :class="{ 'active': activeTab === 'activity' }"
                  id="activity-tab" 
                  @click.prevent="switchTab('activity')"
                  href="#activity-pane" role="tab" 
                  aria-controls="activity-pane" 
                  :aria-selected="activeTab === 'activity'">
                  Activity
                </a>
              </li>
              <li class="nav-item" v-if="hasCRMAccess">
                <a class="nav-link" 
                  :class="{ 'active': activeTab === 'tasks' }"
                  id="tasks-tab" 
                  @click.prevent="switchTab('tasks')"
                  href="#tasks-pane" role="tab" 
                  aria-controls="tasks-pane" 
                  :aria-selected="activeTab === 'tasks'">
                  Tasks
                  <span v-if="clientTasks.length > 0" class="badge bg-info ms-1">{{ clientTasks.length }}</span>
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" 
                  :class="{ 'active': activeTab === 'documents' }"
                  id="documents-tab" 
                  @click.prevent="switchTab('documents')"
                  href="#documents-pane" role="tab" 
                  aria-controls="documents-pane" 
                  :aria-selected="activeTab === 'documents'">
                  Documents
                  <span v-if="clientDocumentCount > 0" class="badge bg-secondary ms-1">{{ clientDocumentCount }}</span>
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" 
                  :class="{ 'active': activeTab === 'portal-access' }"
                  id="portal-access-tab" 
                  @click.prevent="switchTab('portal-access')"
                  href="#portal-access-pane" role="tab" 
                  aria-controls="portal-access-pane" 
                  :aria-selected="activeTab === 'portal-access'">
                  Portal Access
                  <span v-if="client?.portal_access_enabled" class="badge bg-success ms-1">Enabled</span>
                </a>
              </li>
    </ul>
    
    <!-- Tab Content -->
    <div class="tab-content">
            <!-- Overview Tab -->
            <div class="tab-pane fade" 
                 :class="{ 'show active': activeTab === 'overview' }"
                 id="overview-pane" role="tabpanel" 
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
                                      params: { id: client.id, scenarioid: scenario.id },
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
            <div class="tab-pane fade" 
                 :class="{ 'show active': activeTab === 'communications' }"
                 id="communications-pane" role="tabpanel" 
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
            <div class="tab-pane fade" 
                 :class="{ 'show active': activeTab === 'activity' }"
                 id="activity-pane" role="tabpanel" 
                 aria-labelledby="activity-tab" v-if="hasCRMAccess">
              <div>
                <ActivityStream 
                  ref="activityStreamRef"
                  :client-filter="client ? client.id : null"
                  :max-items="20"
                  :auto-refresh="false"
                  :refresh-interval="30000"
                  :lazy-load="false"
                  @activity-click="handleActivityClick"
                  @action-executed="handleActionExecuted"
                />
              </div>
            </div>
            
            <!-- Tasks Tab -->
            <div class="tab-pane fade" 
                 :class="{ 'show active': activeTab === 'tasks' }"
                 id="tasks-pane" role="tabpanel" 
                 aria-labelledby="tasks-tab" v-if="hasCRMAccess">
              <div>
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5 class="mb-0">Client Tasks</h5>
                  <button @click="showCreateTaskModal" class="btn btn-primary">
                    <i class="bi bi-plus-circle me-2"></i>Create Task
                  </button>
                </div>
                
                <!-- Filter Controls -->
                <div class="card mb-3">
                  <div class="card-body">
                    <div class="row align-items-end">
                      <div class="col-md-3">
                        <label class="form-label">Search</label>
                        <input
                          type="text"
                          class="form-control"
                          placeholder="Search tasks..."
                          v-model="taskFilters.search"
                        >
                      </div>
                      <div class="col-md-2">
                        <label class="form-label">Status</label>
                        <select class="form-select" v-model="taskFilters.status">
                          <option value="">All Tasks</option>
                          <option value="active">All Active</option>
                          <option value="pending">Pending</option>
                          <option value="in_progress">In Progress</option>
                          <option value="completed">Completed</option>
                          <option value="cancelled">Cancelled</option>
                        </select>
                      </div>
                      <div class="col-md-2">
                        <label class="form-label">Priority</label>
                        <select class="form-select" v-model="taskFilters.priority">
                          <option value="">All Priority</option>
                          <option value="high">High</option>
                          <option value="medium">Medium</option>
                          <option value="low">Low</option>
                        </select>
                      </div>
                      <div class="col-md-2">
                        <label class="form-label">Sort By</label>
                        <select class="form-select" v-model="taskSortBy">
                          <option value="-created_at">Newest First</option>
                          <option value="created_at">Oldest First</option>
                          <option value="due_date">Due Date</option>
                          <option value="-due_date">Due Date (Desc)</option>
                          <option value="priority">Priority</option>
                          <option value="title">Title A-Z</option>
                          <option value="-title">Title Z-A</option>
                        </select>
                      </div>
                      <div class="col-md-2">
                        <div class="form-check mt-4">
                          <input
                            class="form-check-input"
                            type="checkbox"
                            id="overdueOnly"
                            v-model="taskFilters.overdue"
                          >
                          <label class="form-check-label" for="overdueOnly">
                            Overdue Only
                          </label>
                        </div>
                      </div>
                      <div class="col-md-1">
                        <button 
                          class="btn btn-outline-secondary w-100 mt-4"
                          @click="clearFilters"
                          title="Clear Filters"
                        >
                          Clear
                        </button>
                      </div>
                    </div>
                  </div>
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
                
                <div v-else-if="filteredAndSortedTasks.length === 0" class="text-center py-4 text-muted">
                  <i class="bi bi-funnel display-1"></i>
                  <p class="mt-2">No tasks match your filters</p>
                  <button @click="clearFilters" class="btn btn-outline-secondary">
                    Clear Filters
                  </button>
                </div>
                
                <div v-else>
                  <!-- Task count and results info -->
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted">
                      Showing {{ filteredAndSortedTasks.length }} of {{ clientTasks.length }} tasks
                    </small>
                  </div>
                  
                  <!-- Task List Table -->
                  <div class="card">
                    <div class="table-responsive">
                      <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                          <tr>
                            <th scope="col" style="width: 40%">Task</th>
                            <th scope="col" style="width: 15%">Status</th>
                            <th scope="col" style="width: 15%">Priority</th>
                            <th scope="col" style="width: 15%">Due Date</th>
                            <th scope="col" style="width: 15%">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="task in filteredAndSortedTasks" :key="task.id" 
                              class="task-row"
                              :class="{ 'table-danger-light': task.is_overdue }">
                            <td>
                              <div>
                                <h6 class="mb-0" :class="{ 'text-decoration-line-through': task.status === 'completed' }">
                                  {{ task.title }}
                                </h6>
                                <small class="text-muted">{{ truncateText(task.description, 100) }}</small>
                              </div>
                            </td>
                            <td>
                              <span class="badge" :class="getStatusBadgeClass(task.status)">
                                {{ getStatusLabel(task.status) }}
                              </span>
                            </td>
                            <td>
                              <span class="badge" :class="getPriorityClass(task.priority)">
                                {{ task.priority || 'Medium' }}
                              </span>
                            </td>
                            <td>
                              <small>{{ task.due_date ? formatDate(task.due_date) : '-' }}</small>
                            </td>
                            <td>
                              <div class="btn-group" role="group">
                                <button @click="editTask(task)" 
                                        class="btn btn-sm btn-outline-secondary" 
                                        title="Edit Task">
                                  <i class="bi bi-pencil"></i>
                                </button>
                                <button v-if="task.status !== 'completed'" 
                                        @click="markTaskComplete(task)" 
                                        class="btn btn-sm btn-outline-success"
                                        title="Mark Complete">
                                  <i class="bi bi-check"></i>
                                </button>
                                <button @click="deleteTask(task)" 
                                        class="btn btn-sm btn-outline-danger"
                                        title="Delete Task">
                                  <i class="bi bi-trash"></i>
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
            </div>
            
            <!-- Documents Tab -->
            <div class="tab-pane fade" 
                 :class="{ 'show active': activeTab === 'documents' }"
                 id="documents-pane" role="tabpanel" 
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
            <div class="tab-pane fade" 
                 :class="{ 'show active': activeTab === 'portal-access' }"
                 id="portal-access-pane" role="tabpanel" 
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
      // Task filtering
      taskFilters: {
        search: '',
        status: 'active',  // Default to showing only active tasks
        priority: '',
        overdue: false
      },
      taskSortBy: '-created_at',
      // Active tab tracking
      activeTab: 'overview'
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
    },
    
    filteredAndSortedTasks() {
      // Backend now handles all filtering and sorting
      // Just return the tasks as-is since they're already filtered by the API
      return this.clientTasks;
    }
  },
  mounted() {
    // Check if there's a hash in the URL to set the initial tab
    const hash = window.location.hash;
    if (hash) {
      const tabMap = {
        '#overview-pane': 'overview',
        '#communications-pane': 'communications',
        '#activity-pane': 'activity',
        '#tasks-pane': 'tasks',
        '#documents-pane': 'documents',
        '#portal-access-pane': 'portal-access'
      };
      const tabName = tabMap[hash];
      if (tabName) {
        this.activeTab = tabName;
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
        // Build query parameters including filters
        const params = {
          client: this.client.id,
          status: this.taskFilters.status || undefined,
          priority: this.taskFilters.priority || undefined,
          search: this.taskFilters.search || undefined,
          overdue: this.taskFilters.overdue ? 'true' : undefined,
          ordering: this.taskSortBy
        };
        
        // Remove undefined values
        Object.keys(params).forEach(key => {
          if (params[key] === undefined) {
            delete params[key];
          }
        });
        
        console.log('Fetching tasks with params:', params);
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_CONFIG.API_URL}/tasks/`, {
          params,
          headers: { Authorization: `Bearer ${token}` }
        });
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

    getStatusBadgeClass(status) {
      switch (status) {
        case 'completed': return 'bg-success';
        case 'in_progress': return 'bg-primary';
        case 'pending': return 'bg-secondary';
        case 'cancelled': return 'bg-danger';
        default: return 'bg-secondary';
      }
    },

    getStatusLabel(status) {
      switch (status) {
        case 'in_progress': return 'In Progress';
        case 'completed': return 'Completed';
        case 'pending': return 'Pending';
        case 'cancelled': return 'Cancelled';
        default: return status;
      }
    },

    getTaskItemClass(task) {
      const classes = ['task-item-hover'];
      
      if (task.is_overdue) {
        classes.push('border-danger');
      } else if (task.priority === 'high') {
        classes.push('border-warning');
      } else if (task.status === 'completed') {
        classes.push('border-success');
      }
      
      return classes;
    },

    truncateText(text, length) {
      return text && text.length > length ? text.substring(0, length) + '...' : text;
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
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.patch(`${API_CONFIG.API_URL}/tasks/${task.id}/`, 
          { status: 'completed' },
          { headers }
        );
        // Update the task in the local array
        const taskIndex = this.clientTasks.findIndex(t => t.id === task.id);
        if (taskIndex !== -1) {
          this.clientTasks[taskIndex] = response.data;
        }
      } catch (error) {
        console.error('Error completing task:', error);
      }
    },

    async deleteTask(task) {
      if (confirm(`Are you sure you want to delete the task "${task.title}"?`)) {
        try {
          const token = localStorage.getItem('token');
          const headers = { Authorization: `Bearer ${token}` };
          await axios.delete(`${API_CONFIG.API_URL}/tasks/${task.id}/`, { headers });
          // Remove the task from the local array
          this.clientTasks = this.clientTasks.filter(t => t.id !== task.id);
        } catch (error) {
          console.error('Error deleting task:', error);
        }
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
    },

    switchTab(tabName) {
      this.activeTab = tabName;
      
      // Special handling for activity tab
      if (tabName === 'activity') {
        this.$nextTick(() => {
          if (this.$refs.activityStreamRef) {
            this.$refs.activityStreamRef.refreshIfNeeded();
          }
        });
      }
    },

    handleActivityClick(activity) {
      console.log('Activity clicked:', activity);
      // Handle activity click event
    },

    handleActionExecuted({ action, activity }) {
      console.log('Action executed:', action, 'for activity:', activity);
      // Handle action executed event
    },

    clearFilters() {
      this.taskFilters = {
        search: '',
        status: 'active',  // Reset to showing only active tasks
        priority: '',
        overdue: false
      };
      this.taskSortBy = '-created_at';
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

/* Task table styling */
.task-row {
  transition: background-color 0.2s ease;
}

.task-row:hover {
  background-color: #f8f9fa;
}

.table-danger-light {
  background-color: #fff5f5 !important;
}

.table-danger-light:hover {
  background-color: #ffe5e5 !important;
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