<template>
  <div class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Task Templates</h5>
          <button
            type="button"
            class="btn-close"
            @click="$emit('close')"
          ></button>
        </div>
        
        <div class="modal-body">
          <!-- Template Actions -->
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h6 class="mb-0">Manage Task Templates</h6>
              <small class="text-muted">Create reusable templates for common tasks</small>
            </div>
            <button
              class="btn btn-primary btn-sm"
              @click="openCreateTemplate"
            >
              <i class="fas fa-plus me-1"></i>New Template
            </button>
          </div>

          <!-- Search and Filter -->
          <div class="row mb-4">
            <div class="col-md-6">
              <input
                type="text"
                class="form-control"
                placeholder="Search templates..."
                v-model="searchQuery"
              >
            </div>
            <div class="col-md-3">
              <select class="form-select" v-model="filterStatus">
                <option value="">All Templates</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
              </select>
            </div>
            <div class="col-md-3">
              <select class="form-select" v-model="filterType">
                <option value="">All Types</option>
                <option value="follow_up">Follow Up</option>
                <option value="meeting">Meeting</option>
                <option value="call">Phone Call</option>
                <option value="email">Email</option>
                <option value="review">Review</option>
                <option value="analysis">Analysis</option>
                <option value="administrative">Administrative</option>
                <option value="prospecting">Prospecting</option>
                <option value="client_service">Client Service</option>
              </select>
            </div>
          </div>

          <!-- Templates Grid -->
          <div v-if="taskStore.loading.templates" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading templates...</span>
            </div>
          </div>

          <div v-else-if="filteredTemplates.length === 0" class="text-center py-5">
            <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
            <h5 class="text-muted">No templates found</h5>
            <p class="text-muted">Create your first template to get started.</p>
          </div>

          <div v-else class="row">
            <div
              v-for="template in filteredTemplates"
              :key="template.id"
              class="col-md-6 col-lg-4 mb-3"
            >
              <div
                class="card template-card h-100"
                :class="{ 'border-muted': !template.is_active }"
              >
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="card-title mb-1" :class="{ 'text-muted': !template.is_active }">
                      {{ template.title }}
                    </h6>
                    <div class="dropdown">
                      <button
                        class="btn btn-sm btn-outline-secondary dropdown-toggle"
                        type="button"
                        data-bs-toggle="dropdown"
                      >
                        <i class="fas fa-ellipsis-v"></i>
                      </button>
                      <ul class="dropdown-menu dropdown-menu-end">
                        <li>
                          <button
                            class="dropdown-item"
                            @click="useTemplate(template)"
                          >
                            <i class="fas fa-plus me-2"></i>Create Task
                          </button>
                        </li>
                        <li>
                          <button
                            class="dropdown-item"
                            @click="editTemplate(template)"
                          >
                            <i class="fas fa-edit me-2"></i>Edit
                          </button>
                        </li>
                        <li>
                          <button
                            class="dropdown-item"
                            @click="duplicateTemplate(template)"
                          >
                            <i class="fas fa-copy me-2"></i>Duplicate
                          </button>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                          <button
                            class="dropdown-item"
                            @click="toggleTemplateStatus(template)"
                          >
                            <i class="fas me-2" :class="template.is_active ? 'fa-pause' : 'fa-play'"></i>
                            {{ template.is_active ? 'Deactivate' : 'Activate' }}
                          </button>
                        </li>
                        <li>
                          <button
                            class="dropdown-item text-danger"
                            @click="deleteTemplate(template.id)"
                          >
                            <i class="fas fa-trash me-2"></i>Delete
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div class="template-meta mb-2">
                    <span class="badge me-1" :class="template.is_active ? 'bg-success' : 'bg-secondary'">
                      {{ template.is_active ? 'Active' : 'Inactive' }}
                    </span>
                    <span v-if="template.task_type" class="badge bg-light text-dark me-1">
                      {{ getTaskTypeLabel(template.task_type) }}
                    </span>
                    <span class="badge" :class="getPriorityBadgeClass(template.default_priority)">
                      {{ getPriorityLabel(template.default_priority) }}
                    </span>
                  </div>

                  <p v-if="template.description" class="card-text text-muted small">
                    {{ truncateText(template.description, 100) }}
                  </p>

                  <div class="template-details text-muted small">
                    <div v-if="template.default_due_days" class="mb-1">
                      <i class="fas fa-calendar me-1"></i>
                      Due in {{ template.default_due_days }} days
                    </div>
                    <div>
                      <i class="fas fa-clock me-1"></i>
                      Created {{ formatRelativeDate(template.created_at) }}
                    </div>
                    <div v-if="template.usage_count > 0" class="mt-1">
                      <i class="fas fa-chart-bar me-1"></i>
                      Used {{ template.usage_count }} {{ template.usage_count === 1 ? 'time' : 'times' }}
                    </div>
                  </div>
                </div>

                <div class="card-footer bg-transparent">
                  <button
                    class="btn btn-primary btn-sm w-100"
                    @click="useTemplate(template)"
                    :disabled="!template.is_active"
                  >
                    <i class="fas fa-plus me-1"></i>Use Template
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            @click="$emit('close')"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Template Form Modal -->
    <TemplateFormModal
      v-if="showTemplateForm"
      :template="selectedTemplate"
      :show="showTemplateForm"
      @close="closeTemplateForm"
      @template-saved="handleTemplateSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTaskStore } from '@/stores/taskStore.js'
import TemplateFormModal from '@/components/TemplateFormModal.vue'

const emit = defineEmits(['close', 'template-used'])

const taskStore = useTaskStore()

const searchQuery = ref('')
const filterStatus = ref('')
const filterType = ref('')
const showTemplateForm = ref(false)
const selectedTemplate = ref(null)

const filteredTemplates = computed(() => {
  let templates = taskStore.taskTemplates || []

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    templates = templates.filter(template =>
      template.title.toLowerCase().includes(query) ||
      (template.description && template.description.toLowerCase().includes(query))
    )
  }

  // Filter by status
  if (filterStatus.value) {
    templates = templates.filter(template => {
      if (filterStatus.value === 'active') return template.is_active
      if (filterStatus.value === 'inactive') return !template.is_active
      return true
    })
  }

  // Filter by type
  if (filterType.value) {
    templates = templates.filter(template => template.task_type === filterType.value)
  }

  return templates
})

const openCreateTemplate = () => {
  selectedTemplate.value = null
  showTemplateForm.value = true
}

const editTemplate = (template) => {
  selectedTemplate.value = template
  showTemplateForm.value = true
}

const useTemplate = (template) => {
  emit('template-used', template.id, {})
}

const duplicateTemplate = async (template) => {
  try {
    const duplicateData = {
      title: `Copy of ${template.title}`,
      description: template.description,
      task_type: template.task_type,
      default_priority: template.default_priority,
      default_status: template.default_status,
      default_due_days: template.default_due_days,
      checklist_items: template.checklist_items || [],
      tags: template.tags || [],
      notes: template.notes,
      is_active: true
    }

    await taskStore.createTaskTemplate(duplicateData)
    await taskStore.fetchTaskTemplates()
  } catch (error) {
    console.error('Failed to duplicate template:', error)
  }
}

const toggleTemplateStatus = async (template) => {
  try {
    await taskStore.updateTaskTemplate(template.id, {
      is_active: !template.is_active
    })
    await taskStore.fetchTaskTemplates()
  } catch (error) {
    console.error('Failed to update template status:', error)
  }
}

const deleteTemplate = async (templateId) => {
  if (confirm('Are you sure you want to delete this template? This action cannot be undone.')) {
    try {
      await taskStore.deleteTaskTemplate(templateId)
      await taskStore.fetchTaskTemplates()
    } catch (error) {
      console.error('Failed to delete template:', error)
    }
  }
}

const closeTemplateForm = () => {
  showTemplateForm.value = false
  selectedTemplate.value = null
}

const handleTemplateSaved = () => {
  closeTemplateForm()
  taskStore.fetchTaskTemplates()
}

const getTaskTypeLabel = (taskType) => {
  if (!taskType) return ''
  return taskType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getPriorityBadgeClass = (priority) => {
  switch (priority) {
    case 'high': return 'bg-danger'
    case 'medium': return 'bg-warning text-dark'
    case 'low': return 'bg-info'
    default: return 'bg-secondary'
  }
}

const getPriorityLabel = (priority) => {
  return priority ? priority.charAt(0).toUpperCase() + priority.slice(1) : 'Medium'
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatRelativeDate = (date) => {
  const now = new Date()
  const templateDate = new Date(date)
  const diffInDays = Math.floor((now - templateDate) / (1000 * 60 * 60 * 24))
  
  if (diffInDays === 0) return 'today'
  if (diffInDays === 1) return 'yesterday'
  if (diffInDays < 7) return `${diffInDays} days ago`
  if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`
  if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`
  return `${Math.floor(diffInDays / 365)} years ago`
}

onMounted(() => {
  if (!taskStore.taskTemplates.length) {
    taskStore.fetchTaskTemplates()
  }
})
</script>

<style scoped>
.modal {
  display: block;
}

.template-card {
  transition: all 0.2s ease;
  cursor: default;
}

.template-card:hover {
  box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.template-meta .badge {
  font-size: 0.7em;
  font-weight: normal;
}

.template-details {
  font-size: 0.8em;
  line-height: 1.4;
}

.card-footer {
  padding: 0.75rem;
}

.dropdown-toggle::after {
  display: none;
}

.border-muted {
  border-color: #dee2e6 !important;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .col-md-6,
  .col-lg-4 {
    margin-bottom: 1rem;
  }
}
</style>