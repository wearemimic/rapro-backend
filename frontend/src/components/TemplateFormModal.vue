<template>
  <div class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.7);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            {{ isEditing ? 'Edit Template' : 'Create Template' }}
          </h5>
          <button
            type="button"
            class="btn-close"
            @click="$emit('close')"
          ></button>
        </div>
        
        <form @submit.prevent="handleSubmit">
          <div class="modal-body">
            <!-- Template Title -->
            <div class="mb-3">
              <label for="title" class="form-label required">Template Title</label>
              <input
                type="text"
                id="title"
                class="form-control"
                :class="{ 'is-invalid': errors.title }"
                v-model="form.title"
                placeholder="Enter template title..."
                required
              >
              <div v-if="errors.title" class="invalid-feedback">
                {{ errors.title }}
              </div>
            </div>

            <!-- Template Description -->
            <div class="mb-3">
              <label for="description" class="form-label">Description</label>
              <textarea
                id="description"
                class="form-control"
                :class="{ 'is-invalid': errors.description }"
                v-model="form.description"
                placeholder="Enter template description..."
                rows="3"
              ></textarea>
              <div v-if="errors.description" class="invalid-feedback">
                {{ errors.description }}
              </div>
            </div>

            <div class="row">
              <!-- Task Type -->
              <div class="col-md-6 mb-3">
                <label for="taskType" class="form-label">Task Type</label>
                <select
                  id="taskType"
                  class="form-select"
                  :class="{ 'is-invalid': errors.task_type }"
                  v-model="form.task_type"
                >
                  <option value="">Select task type</option>
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
                <div v-if="errors.task_type" class="invalid-feedback">
                  {{ errors.task_type }}
                </div>
              </div>

              <!-- Default Priority -->
              <div class="col-md-6 mb-3">
                <label for="priority" class="form-label required">Default Priority</label>
                <select
                  id="priority"
                  class="form-select"
                  :class="{ 'is-invalid': errors.default_priority }"
                  v-model="form.default_priority"
                  required
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
                <div v-if="errors.default_priority" class="invalid-feedback">
                  {{ errors.default_priority }}
                </div>
              </div>
            </div>

            <div class="row">
              <!-- Default Status -->
              <div class="col-md-6 mb-3">
                <label for="status" class="form-label required">Default Status</label>
                <select
                  id="status"
                  class="form-select"
                  :class="{ 'is-invalid': errors.default_status }"
                  v-model="form.default_status"
                  required
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                </select>
                <div v-if="errors.default_status" class="invalid-feedback">
                  {{ errors.default_status }}
                </div>
              </div>

              <!-- Default Due Days -->
              <div class="col-md-6 mb-3">
                <label for="dueDays" class="form-label">Due in (days)</label>
                <input
                  type="number"
                  id="dueDays"
                  class="form-control"
                  :class="{ 'is-invalid': errors.default_due_days }"
                  v-model.number="form.default_due_days"
                  placeholder="Number of days"
                  min="0"
                  max="365"
                >
                <small class="form-text text-muted">Leave empty for no due date</small>
                <div v-if="errors.default_due_days" class="invalid-feedback">
                  {{ errors.default_due_days }}
                </div>
              </div>
            </div>

            <!-- Checklist Items -->
            <div class="mb-3">
              <label class="form-label">Task Checklist</label>
              <div class="checklist-container">
                <div
                  v-for="(item, index) in form.checklist_items"
                  :key="index"
                  class="d-flex align-items-center mb-2"
                >
                  <input
                    type="text"
                    class="form-control me-2"
                    v-model="item.text"
                    :placeholder="`Checklist item ${index + 1}...`"
                  >
                  <button
                    type="button"
                    class="btn btn-outline-danger btn-sm"
                    @click="removeChecklistItem(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                
                <button
                  type="button"
                  class="btn btn-outline-primary btn-sm"
                  @click="addChecklistItem"
                >
                  <i class="fas fa-plus me-1"></i>Add Checklist Item
                </button>
              </div>
            </div>

            <!-- Tags -->
            <div class="mb-3">
              <label for="tags" class="form-label">Default Tags</label>
              <input
                type="text"
                id="tags"
                class="form-control"
                v-model="tagInput"
                @keydown.enter.prevent="addTag"
                @keydown.comma.prevent="addTag"
                placeholder="Add tags (press Enter or comma to add)..."
              >
              
              <div v-if="form.tags.length > 0" class="mt-2">
                <span
                  v-for="(tag, index) in form.tags"
                  :key="index"
                  class="badge bg-secondary me-1 mb-1"
                >
                  {{ tag }}
                  <button
                    type="button"
                    class="btn-close btn-close-white btn-sm ms-1"
                    @click="removeTag(index)"
                  ></button>
                </span>
              </div>
            </div>

            <!-- Template Notes -->
            <div class="mb-3">
              <label for="notes" class="form-label">Template Notes</label>
              <textarea
                id="notes"
                class="form-control"
                v-model="form.notes"
                placeholder="Internal notes about this template..."
                rows="3"
              ></textarea>
            </div>

            <!-- Template Status -->
            <div class="mb-3">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="isActive"
                  v-model="form.is_active"
                >
                <label class="form-check-label" for="isActive">
                  Template is Active
                </label>
                <small class="form-text text-muted d-block">
                  Inactive templates won't appear in the template list when creating tasks
                </small>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="$emit('close')"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isEditing ? 'Update Template' : 'Create Template' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useTaskStore } from '@/stores/taskStore.js'

const props = defineProps({
  template: {
    type: Object,
    default: null
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'template-saved'])

const taskStore = useTaskStore()

const form = ref({
  title: '',
  description: '',
  task_type: '',
  default_priority: 'medium',
  default_status: 'pending',
  default_due_days: null,
  checklist_items: [],
  tags: [],
  notes: '',
  is_active: true
})

const errors = ref({})
const isSubmitting = ref(false)
const tagInput = ref('')

const isEditing = computed(() => !!props.template)

const initializeForm = () => {
  if (props.template) {
    form.value = {
      title: props.template.title || '',
      description: props.template.description || '',
      task_type: props.template.task_type || '',
      default_priority: props.template.default_priority || 'medium',
      default_status: props.template.default_status || 'pending',
      default_due_days: props.template.default_due_days || null,
      checklist_items: props.template.checklist_items || [],
      tags: props.template.tags || [],
      notes: props.template.notes || '',
      is_active: props.template.is_active !== undefined ? props.template.is_active : true
    }
  } else {
    form.value = {
      title: '',
      description: '',
      task_type: '',
      default_priority: 'medium',
      default_status: 'pending',
      default_due_days: null,
      checklist_items: [],
      tags: [],
      notes: '',
      is_active: true
    }
  }
}

const validateForm = () => {
  errors.value = {}

  if (!form.value.title.trim()) {
    errors.value.title = 'Template title is required'
  }

  if (!form.value.default_priority) {
    errors.value.default_priority = 'Default priority is required'
  }

  if (!form.value.default_status) {
    errors.value.default_status = 'Default status is required'
  }

  if (form.value.default_due_days !== null && form.value.default_due_days < 0) {
    errors.value.default_due_days = 'Due days cannot be negative'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    const templateData = {
      ...form.value,
      checklist_items: form.value.checklist_items.filter(item => item.text.trim()),
      default_due_days: form.value.default_due_days || null
    }

    if (isEditing.value) {
      await taskStore.updateTaskTemplate(props.template.id, templateData)
    } else {
      await taskStore.createTaskTemplate(templateData)
    }

    emit('template-saved')
  } catch (error) {
    console.error('Failed to save template:', error)
    if (error.response?.data) {
      errors.value = error.response.data
    }
  } finally {
    isSubmitting.value = false
  }
}

const addChecklistItem = () => {
  form.value.checklist_items.push({
    text: '',
    is_completed: false
  })
}

const removeChecklistItem = (index) => {
  form.value.checklist_items.splice(index, 1)
}

const addTag = () => {
  const tag = tagInput.value.trim().replace(',', '')
  if (tag && !form.value.tags.includes(tag)) {
    form.value.tags.push(tag)
    tagInput.value = ''
  }
}

const removeTag = (index) => {
  form.value.tags.splice(index, 1)
}

watch(() => props.show, (newValue) => {
  if (newValue) {
    initializeForm()
  }
})

onMounted(() => {
  if (props.show) {
    initializeForm()
  }
})
</script>

<style scoped>
.required::after {
  content: ' *';
  color: red;
}

.modal {
  display: block;
  z-index: 1060;
}

.checklist-container {
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  padding: 1rem;
  background-color: #f8f9fa;
}

.badge .btn-close {
  font-size: 0.6em;
  padding: 0;
  margin-left: 0.25rem;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.form-check {
  margin-bottom: 0.5rem;
}

.invalid-feedback {
  display: block;
}

.form-text {
  margin-top: 0.25rem;
}
</style>