<template>
  <div class="advanced-filter">
    <!-- Filter Toggle Button -->
    <div class="filter-header d-flex justify-content-between align-items-center mb-3">
      <div class="d-flex align-items-center">
        <button 
          @click="showFilters = !showFilters"
          class="btn btn-outline-secondary me-3"
          :class="{ 'active': showFilters }"
        >
          <i class="fas fa-filter me-1"></i>
          Filters
          <span v-if="activeFiltersCount > 0" class="badge bg-primary ms-1">
            {{ activeFiltersCount }}
          </span>
        </button>
        
        <!-- Quick Search -->
        <div class="search-input-group">
          <div class="input-group">
            <span class="input-group-text">
              <i class="fas fa-search"></i>
            </span>
            <input 
              v-model="searchQuery"
              type="text" 
              class="form-control"
              placeholder="Search templates, reports, clients..."
              @input="debouncedSearch"
            >
            <button 
              v-if="searchQuery"
              @click="clearSearch"
              class="btn btn-outline-secondary"
              type="button"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Filter Actions -->
      <div class="filter-actions">
        <button 
          v-if="hasActiveFilters"
          @click="clearAllFilters"
          class="btn btn-sm btn-outline-warning me-2"
        >
          <i class="fas fa-times me-1"></i>Clear All
        </button>
        
        <div class="btn-group btn-group-sm">
          <button 
            @click="applyFilters"
            class="btn btn-primary"
            :disabled="!hasChanges"
          >
            <i class="fas fa-check me-1"></i>Apply
          </button>
          <button 
            @click="saveFilterPreset"
            class="btn btn-outline-primary"
            :disabled="!hasActiveFilters"
          >
            <i class="fas fa-bookmark me-1"></i>Save
          </button>
        </div>
      </div>
    </div>

    <!-- Active Filter Tags -->
    <div v-if="hasActiveFilters" class="active-filters mb-3">
      <div class="d-flex flex-wrap gap-2">
        <span 
          v-for="tag in activeFilterTags" 
          :key="tag.key"
          class="badge bg-primary d-flex align-items-center"
        >
          {{ tag.label }}: {{ tag.value }}
          <button 
            @click="removeFilter(tag.key, tag.subkey)"
            class="btn-close btn-close-white ms-2"
            style="font-size: 0.6rem;"
          ></button>
        </span>
      </div>
    </div>

    <!-- Advanced Filters Panel -->
    <div v-show="showFilters" class="filters-panel">
      <div class="card">
        <div class="card-body">
          <div class="row">
            <!-- Content Type Filter -->
            <div class="col-lg-3 col-md-6 mb-4">
              <h6 class="filter-section-title">Content Type</h6>
              <div class="form-check mb-2">
                <input 
                  id="filterTemplates" 
                  v-model="filters.contentTypes" 
                  type="checkbox" 
                  class="form-check-input"
                  value="templates"
                >
                <label for="filterTemplates" class="form-check-label">Templates</label>
              </div>
              <div class="form-check mb-2">
                <input 
                  id="filterReports" 
                  v-model="filters.contentTypes" 
                  type="checkbox" 
                  class="form-check-input"
                  value="reports"
                >
                <label for="filterReports" class="form-check-label">Reports</label>
              </div>
              <div class="form-check mb-2">
                <input 
                  id="filterExports" 
                  v-model="filters.contentTypes" 
                  type="checkbox" 
                  class="form-check-input"
                  value="exports"
                >
                <label for="filterExports" class="form-check-label">Export Jobs</label>
              </div>
            </div>

            <!-- Category Filter -->
            <div class="col-lg-3 col-md-6 mb-4">
              <h6 class="filter-section-title">Categories</h6>
              <div class="category-filters">
                <div 
                  v-for="category in availableCategories" 
                  :key="category"
                  class="form-check mb-2"
                >
                  <input 
                    :id="`category-${category}`"
                    v-model="filters.categories" 
                    type="checkbox" 
                    class="form-check-input"
                    :value="category"
                  >
                  <label :for="`category-${category}`" class="form-check-label text-capitalize">
                    {{ category.replace('_', ' ') }}
                  </label>
                </div>
              </div>
            </div>

            <!-- Status Filter -->
            <div class="col-lg-3 col-md-6 mb-4">
              <h6 class="filter-section-title">Status</h6>
              <div class="status-filters">
                <!-- Template Status -->
                <div v-if="filters.contentTypes.includes('templates')" class="mb-3">
                  <label class="form-label small text-muted">Templates</label>
                  <div class="form-check">
                    <input 
                      id="templateActive" 
                      v-model="filters.templateStatus" 
                      type="checkbox" 
                      class="form-check-input"
                      value="active"
                    >
                    <label for="templateActive" class="form-check-label">Active</label>
                  </div>
                  <div class="form-check">
                    <input 
                      id="templatePublic" 
                      v-model="filters.templateStatus" 
                      type="checkbox" 
                      class="form-check-input"
                      value="public"
                    >
                    <label for="templatePublic" class="form-check-label">Public</label>
                  </div>
                  <div class="form-check">
                    <input 
                      id="templateSystem" 
                      v-model="filters.templateStatus" 
                      type="checkbox" 
                      class="form-check-input"
                      value="system"
                    >
                    <label for="templateSystem" class="form-check-label">System</label>
                  </div>
                </div>

                <!-- Report Status -->
                <div v-if="filters.contentTypes.includes('reports')">
                  <label class="form-label small text-muted">Reports</label>
                  <div class="form-check">
                    <input 
                      id="reportReady" 
                      v-model="filters.reportStatus" 
                      type="checkbox" 
                      class="form-check-input"
                      value="ready"
                    >
                    <label for="reportReady" class="form-check-label">Ready</label>
                  </div>
                  <div class="form-check">
                    <input 
                      id="reportGenerating" 
                      v-model="filters.reportStatus" 
                      type="checkbox" 
                      class="form-check-input"
                      value="generating"
                    >
                    <label for="reportGenerating" class="form-check-label">Generating</label>
                  </div>
                  <div class="form-check">
                    <input 
                      id="reportShared" 
                      v-model="filters.reportStatus" 
                      type="checkbox" 
                      class="form-check-input"
                      value="shared"
                    >
                    <label for="reportShared" class="form-check-label">Shared</label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Date Filters -->
            <div class="col-lg-3 col-md-6 mb-4">
              <h6 class="filter-section-title">Date Range</h6>
              
              <!-- Date Range Presets -->
              <div class="mb-3">
                <label class="form-label small text-muted">Quick Select</label>
                <select v-model="filters.datePreset" class="form-select form-select-sm" @change="applyDatePreset">
                  <option value="">Custom Range</option>
                  <option value="today">Today</option>
                  <option value="yesterday">Yesterday</option>
                  <option value="last7days">Last 7 Days</option>
                  <option value="last30days">Last 30 Days</option>
                  <option value="last90days">Last 90 Days</option>
                  <option value="thismonth">This Month</option>
                  <option value="lastmonth">Last Month</option>
                  <option value="thisyear">This Year</option>
                </select>
              </div>
              
              <!-- Custom Date Range -->
              <div class="mb-2">
                <label class="form-label small">From Date</label>
                <input 
                  v-model="filters.dateFrom" 
                  type="date" 
                  class="form-control form-control-sm"
                >
              </div>
              <div class="mb-2">
                <label class="form-label small">To Date</label>
                <input 
                  v-model="filters.dateTo" 
                  type="date" 
                  class="form-control form-control-sm"
                >
              </div>
            </div>
          </div>

          <!-- Advanced Options Row -->
          <div class="row mt-4 pt-4 border-top">
            <!-- Client Filter -->
            <div class="col-lg-4 mb-4">
              <h6 class="filter-section-title">Client Filter</h6>
              <div class="client-search-container">
                <div class="input-group input-group-sm">
                  <input 
                    v-model="clientSearchTerm"
                    type="text" 
                    class="form-control"
                    placeholder="Search clients..."
                    @input="searchClients"
                  >
                  <button 
                    v-if="clientSearchTerm"
                    @click="clientSearchTerm = ''"
                    class="btn btn-outline-secondary"
                    type="button"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                
                <!-- Selected Clients -->
                <div v-if="filters.selectedClients.length > 0" class="selected-clients mt-2">
                  <div class="d-flex flex-wrap gap-1">
                    <span 
                      v-for="client in getSelectedClientNames()" 
                      :key="client.id"
                      class="badge bg-light text-dark"
                    >
                      {{ client.name }}
                      <button 
                        @click="removeClientFilter(client.id)"
                        class="btn-close ms-1"
                        style="font-size: 0.6rem;"
                      ></button>
                    </span>
                  </div>
                </div>

                <!-- Client Search Results -->
                <div 
                  v-if="clientSearchTerm && filteredClients.length > 0" 
                  class="client-results mt-2 border rounded p-2"
                  style="max-height: 200px; overflow-y: auto;"
                >
                  <div 
                    v-for="client in filteredClients.slice(0, 10)" 
                    :key="client.id"
                    class="client-result-item p-1 cursor-pointer"
                    :class="{ 'selected': filters.selectedClients.includes(client.id) }"
                    @click="toggleClientSelection(client)"
                  >
                    <div class="d-flex align-items-center">
                      <input 
                        type="checkbox" 
                        :checked="filters.selectedClients.includes(client.id)"
                        class="form-check-input me-2"
                      >
                      <div>
                        <div class="fw-medium">{{ client.first_name }} {{ client.last_name }}</div>
                        <small class="text-muted">{{ client.email }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Sort Options -->
            <div class="col-lg-4 mb-4">
              <h6 class="filter-section-title">Sort Options</h6>
              <div class="mb-2">
                <label class="form-label small">Sort By</label>
                <select v-model="filters.sortBy" class="form-select form-select-sm">
                  <option value="created_at">Created Date</option>
                  <option value="updated_at">Updated Date</option>
                  <option value="name">Name</option>
                  <option value="usage_count">Usage Count</option>
                  <option value="category">Category</option>
                  <option value="status">Status</option>
                </select>
              </div>
              <div class="mb-2">
                <label class="form-label small">Order</label>
                <select v-model="filters.sortOrder" class="form-select form-select-sm">
                  <option value="desc">Newest First</option>
                  <option value="asc">Oldest First</option>
                </select>
              </div>
            </div>

            <!-- Display Options -->
            <div class="col-lg-4 mb-4">
              <h6 class="filter-section-title">Display Options</h6>
              <div class="mb-2">
                <label class="form-label small">Items Per Page</label>
                <select v-model="filters.pageSize" class="form-select form-select-sm">
                  <option value="10">10 items</option>
                  <option value="20">20 items</option>
                  <option value="50">50 items</option>
                  <option value="100">100 items</option>
                </select>
              </div>
              <div class="form-check">
                <input 
                  id="showPreview" 
                  v-model="filters.showPreview" 
                  type="checkbox" 
                  class="form-check-input"
                >
                <label for="showPreview" class="form-check-label">Show Preview Cards</label>
              </div>
              <div class="form-check">
                <input 
                  id="compactView" 
                  v-model="filters.compactView" 
                  type="checkbox" 
                  class="form-check-input"
                >
                <label for="compactView" class="form-check-label">Compact View</label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Presets -->
    <div v-if="showFilters && filterPresets.length > 0" class="filter-presets mt-3">
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">Saved Filters</h6>
        </div>
        <div class="card-body">
          <div class="d-flex flex-wrap gap-2">
            <button 
              v-for="preset in filterPresets" 
              :key="preset.id"
              @click="applyFilterPreset(preset)"
              class="btn btn-sm btn-outline-secondary d-flex align-items-center"
            >
              <i class="fas fa-bookmark me-1"></i>
              {{ preset.name }}
              <button 
                @click.stop="deleteFilterPreset(preset.id)"
                class="btn-close ms-2"
                style="font-size: 0.6rem;"
              ></button>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Filter Preset Modal -->
    <div 
      v-if="showSavePresetModal" 
      class="modal d-block"
      style="background: rgba(0,0,0,0.5);"
      @click.self="showSavePresetModal = false"
    >
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Save Filter Preset</h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="showSavePresetModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Preset Name</label>
              <input 
                v-model="newPresetName"
                type="text" 
                class="form-control"
                placeholder="Enter preset name..."
                @keyup.enter="confirmSavePreset"
              >
            </div>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="showSavePresetModal = false"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="confirmSavePreset"
              :disabled="!newPresetName"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { debounce } from 'lodash'
import api from '@/services/api'

export default {
  name: 'AdvancedFilter',
  emits: ['filter-change', 'search-change'],
  setup(props, { emit }) {
    // Reactive data
    const showFilters = ref(false)
    const searchQuery = ref('')
    const clientSearchTerm = ref('')
    const showSavePresetModal = ref(false)
    const newPresetName = ref('')
    
    const clients = ref([])
    const filterPresets = ref([])
    
    const filters = ref({
      contentTypes: ['templates', 'reports'],
      categories: [],
      templateStatus: [],
      reportStatus: [],
      datePreset: '',
      dateFrom: '',
      dateTo: '',
      selectedClients: [],
      sortBy: 'created_at',
      sortOrder: 'desc',
      pageSize: 20,
      showPreview: true,
      compactView: false
    })
    
    // Store original filters for change detection
    const originalFilters = ref({ ...filters.value })

    // Computed properties
    const availableCategories = computed(() => [
      'retirement',
      'tax',
      'comparison',
      'irmaa',
      'roth',
      'general',
      'comprehensive',
      'summary',
      'analysis'
    ])

    const hasActiveFilters = computed(() => {
      return (
        filters.value.categories.length > 0 ||
        filters.value.templateStatus.length > 0 ||
        filters.value.reportStatus.length > 0 ||
        filters.value.dateFrom ||
        filters.value.dateTo ||
        filters.value.selectedClients.length > 0 ||
        searchQuery.value.length > 0
      )
    })

    const activeFiltersCount = computed(() => {
      let count = 0
      if (filters.value.categories.length > 0) count++
      if (filters.value.templateStatus.length > 0) count++
      if (filters.value.reportStatus.length > 0) count++
      if (filters.value.dateFrom || filters.value.dateTo) count++
      if (filters.value.selectedClients.length > 0) count++
      if (searchQuery.value.length > 0) count++
      return count
    })

    const hasChanges = computed(() => {
      return JSON.stringify(filters.value) !== JSON.stringify(originalFilters.value) ||
             searchQuery.value.length > 0
    })

    const activeFilterTags = computed(() => {
      const tags = []
      
      if (searchQuery.value) {
        tags.push({ key: 'search', label: 'Search', value: searchQuery.value })
      }
      
      filters.value.categories.forEach(category => {
        tags.push({ key: 'categories', subkey: category, label: 'Category', value: category })
      })
      
      filters.value.templateStatus.forEach(status => {
        tags.push({ key: 'templateStatus', subkey: status, label: 'Template', value: status })
      })
      
      filters.value.reportStatus.forEach(status => {
        tags.push({ key: 'reportStatus', subkey: status, label: 'Report', value: status })
      })
      
      if (filters.value.dateFrom || filters.value.dateTo) {
        const dateRange = `${filters.value.dateFrom || 'Start'} - ${filters.value.dateTo || 'End'}`
        tags.push({ key: 'dateRange', label: 'Date', value: dateRange })
      }
      
      getSelectedClientNames().forEach(client => {
        tags.push({ key: 'selectedClients', subkey: client.id, label: 'Client', value: client.name })
      })
      
      return tags
    })

    const filteredClients = computed(() => {
      if (!clientSearchTerm.value) return []
      
      const searchTerm = clientSearchTerm.value.toLowerCase()
      return clients.value.filter(client =>
        `${client.first_name} ${client.last_name}`.toLowerCase().includes(searchTerm) ||
        client.email.toLowerCase().includes(searchTerm)
      )
    })

    // Methods
    const debouncedSearch = debounce(() => {
      emitChanges()
    }, 300)

    const clearSearch = () => {
      searchQuery.value = ''
      emitChanges()
    }

    const applyDatePreset = () => {
      const today = new Date()
      const preset = filters.value.datePreset
      
      switch (preset) {
        case 'today':
          filters.value.dateFrom = today.toISOString().split('T')[0]
          filters.value.dateTo = today.toISOString().split('T')[0]
          break
        case 'yesterday':
          const yesterday = new Date(today)
          yesterday.setDate(today.getDate() - 1)
          filters.value.dateFrom = yesterday.toISOString().split('T')[0]
          filters.value.dateTo = yesterday.toISOString().split('T')[0]
          break
        case 'last7days':
          const last7Days = new Date(today)
          last7Days.setDate(today.getDate() - 7)
          filters.value.dateFrom = last7Days.toISOString().split('T')[0]
          filters.value.dateTo = today.toISOString().split('T')[0]
          break
        case 'last30days':
          const last30Days = new Date(today)
          last30Days.setDate(today.getDate() - 30)
          filters.value.dateFrom = last30Days.toISOString().split('T')[0]
          filters.value.dateTo = today.toISOString().split('T')[0]
          break
        case 'last90days':
          const last90Days = new Date(today)
          last90Days.setDate(today.getDate() - 90)
          filters.value.dateFrom = last90Days.toISOString().split('T')[0]
          filters.value.dateTo = today.toISOString().split('T')[0]
          break
        case 'thismonth':
          filters.value.dateFrom = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0]
          filters.value.dateTo = today.toISOString().split('T')[0]
          break
        case 'lastmonth':
          const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1)
          const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0)
          filters.value.dateFrom = lastMonth.toISOString().split('T')[0]
          filters.value.dateTo = lastMonthEnd.toISOString().split('T')[0]
          break
        case 'thisyear':
          filters.value.dateFrom = new Date(today.getFullYear(), 0, 1).toISOString().split('T')[0]
          filters.value.dateTo = today.toISOString().split('T')[0]
          break
      }
    }

    const searchClients = debounce(async () => {
      if (!clientSearchTerm.value) return
      
      try {
        const response = await api.get('/api/clients/', {
          params: { search: clientSearchTerm.value }
        })
        clients.value = response.data.results || response.data
      } catch (error) {
        console.error('Error searching clients:', error)
      }
    }, 300)

    const toggleClientSelection = (client) => {
      const index = filters.value.selectedClients.indexOf(client.id)
      if (index === -1) {
        filters.value.selectedClients.push(client.id)
      } else {
        filters.value.selectedClients.splice(index, 1)
      }
    }

    const removeClientFilter = (clientId) => {
      const index = filters.value.selectedClients.indexOf(clientId)
      if (index !== -1) {
        filters.value.selectedClients.splice(index, 1)
      }
    }

    const getSelectedClientNames = () => {
      return filters.value.selectedClients.map(id => {
        const client = clients.value.find(c => c.id === id)
        return client ? {
          id: client.id,
          name: `${client.first_name} ${client.last_name}`
        } : { id, name: `Client ${id}` }
      })
    }

    const removeFilter = (key, subkey = null) => {
      if (key === 'search') {
        searchQuery.value = ''
      } else if (key === 'dateRange') {
        filters.value.dateFrom = ''
        filters.value.dateTo = ''
        filters.value.datePreset = ''
      } else if (subkey) {
        const index = filters.value[key].indexOf(subkey)
        if (index !== -1) {
          filters.value[key].splice(index, 1)
        }
      }
      
      emitChanges()
    }

    const clearAllFilters = () => {
      searchQuery.value = ''
      filters.value = {
        contentTypes: ['templates', 'reports'],
        categories: [],
        templateStatus: [],
        reportStatus: [],
        datePreset: '',
        dateFrom: '',
        dateTo: '',
        selectedClients: [],
        sortBy: 'created_at',
        sortOrder: 'desc',
        pageSize: 20,
        showPreview: true,
        compactView: false
      }
      
      emitChanges()
    }

    const applyFilters = () => {
      originalFilters.value = { ...filters.value }
      emitChanges()
    }

    const emitChanges = () => {
      const filterData = {
        search: searchQuery.value,
        filters: { ...filters.value }
      }
      
      emit('filter-change', filterData)
      emit('search-change', searchQuery.value)
    }

    const saveFilterPreset = () => {
      if (!hasActiveFilters.value) return
      showSavePresetModal.value = true
    }

    const confirmSavePreset = () => {
      if (!newPresetName.value) return
      
      const preset = {
        id: Date.now(),
        name: newPresetName.value,
        filters: { ...filters.value },
        search: searchQuery.value,
        created_at: new Date().toISOString()
      }
      
      filterPresets.value.push(preset)
      localStorage.setItem('reportCenterFilterPresets', JSON.stringify(filterPresets.value))
      
      showSavePresetModal.value = false
      newPresetName.value = ''
    }

    const applyFilterPreset = (preset) => {
      filters.value = { ...preset.filters }
      searchQuery.value = preset.search || ''
      emitChanges()
    }

    const deleteFilterPreset = (presetId) => {
      filterPresets.value = filterPresets.value.filter(p => p.id !== presetId)
      localStorage.setItem('reportCenterFilterPresets', JSON.stringify(filterPresets.value))
    }

    const loadFilterPresets = () => {
      try {
        const saved = localStorage.getItem('reportCenterFilterPresets')
        if (saved) {
          filterPresets.value = JSON.parse(saved)
        }
      } catch (error) {
        console.error('Error loading filter presets:', error)
      }
    }

    const loadClients = async () => {
      try {
        const response = await api.get('/api/clients/')
        clients.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading clients:', error)
      }
    }

    // Watchers
    watch(filters, () => {
      if (filters.value.datePreset === '') {
        // Clear preset when custom dates are used
      }
    }, { deep: true })

    // Lifecycle
    onMounted(() => {
      loadFilterPresets()
      loadClients()
      
      // Apply default filters
      emitChanges()
    })

    return {
      // Data
      showFilters,
      searchQuery,
      clientSearchTerm,
      showSavePresetModal,
      newPresetName,
      filters,
      filterPresets,
      clients,
      
      // Computed
      availableCategories,
      hasActiveFilters,
      activeFiltersCount,
      hasChanges,
      activeFilterTags,
      filteredClients,
      
      // Methods
      debouncedSearch,
      clearSearch,
      applyDatePreset,
      searchClients,
      toggleClientSelection,
      removeClientFilter,
      getSelectedClientNames,
      removeFilter,
      clearAllFilters,
      applyFilters,
      saveFilterPreset,
      confirmSavePreset,
      applyFilterPreset,
      deleteFilterPreset
    }
  }
}
</script>

<style scoped>
.advanced-filter {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 2rem;
}

.filter-header {
  background: white;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.search-input-group {
  min-width: 300px;
}

.active-filters {
  padding: 0.5rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.filters-panel {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

.filter-section-title {
  color: #495057;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.client-results {
  background: white;
  z-index: 1050;
}

.client-result-item {
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.client-result-item:hover {
  background-color: #f8f9fa;
}

.client-result-item.selected {
  background-color: #e3f2fd;
}

.cursor-pointer {
  cursor: pointer;
}

.selected-clients .badge {
  border: 1px solid #dee2e6;
}

.btn.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.modal {
  z-index: 1060;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .search-input-group {
    min-width: 200px;
    margin-top: 0.5rem;
  }
  
  .filter-header {
    flex-direction: column;
    align-items: stretch !important;
  }
  
  .filter-actions {
    margin-top: 1rem;
    text-align: center;
  }
}

/* Filter badge animations */
.active-filters .badge {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>