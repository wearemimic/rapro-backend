<template>
  <div class="global-search" :class="{ 'expanded': expanded }">
    <!-- Search Input -->
    <div class="search-container">
      <div class="search-input-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24">
          <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
        </svg>
        
        <input
          ref="searchInput"
          v-model="searchQuery"
          @input="handleInput"
          @focus="handleFocus"
          @keydown="handleKeydown"
          type="text"
          class="search-input"
          :placeholder="placeholder"
          autocomplete="off"
        >
        
        <div v-if="searchQuery" class="search-actions">
          <!-- Filters Toggle -->
          <button 
            @click="toggleFilters" 
            class="filter-btn"
            :class="{ 'active': showFilters }"
            title="Advanced Filters"
          >
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M14,12V19.88C14.04,20.18 13.94,20.5 13.71,20.71C13.32,21.1 12.69,21.1 12.3,20.71L10.29,18.7C10.06,18.47 9.96,18.16 10,17.87V12H9.97L4.21,4.62C3.87,4.19 3.95,3.56 4.38,3.22C4.57,3.08 4.78,3 5,3V3H19V3C19.22,3 19.43,3.08 19.62,3.22C20.05,3.56 20.13,4.19 19.79,4.62L14.03,12H14Z"/>
            </svg>
          </button>
          
          <!-- Clear Search -->
          <button 
            @click="clearSearch" 
            class="clear-btn"
            title="Clear Search"
          >
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
            </svg>
          </button>
        </div>
        
        <!-- Loading Spinner -->
        <div v-if="loading" class="search-loading">
          <svg class="spin" viewBox="0 0 24 24">
            <path d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
          </svg>
        </div>
      </div>
      
      <!-- Search Suggestions -->
      <div v-if="showSuggestions && suggestions.length" class="search-suggestions">
        <div class="suggestions-header">
          <span>Suggestions</span>
        </div>
        <button
          v-for="(suggestion, index) in suggestions"
          :key="suggestion"
          @click="selectSuggestion(suggestion)"
          @mouseenter="hoveredSuggestion = index"
          class="suggestion-item"
          :class="{ 'highlighted': hoveredSuggestion === index }"
        >
          <svg class="icon" viewBox="0 0 24 24">
            <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
          </svg>
          {{ suggestion }}
        </button>
      </div>
    </div>

    <!-- Advanced Filters Panel -->
    <transition name="slide-down">
      <div v-if="showFilters" class="filters-panel">
        <div class="filters-header">
          <h3>Advanced Filters</h3>
          <div class="filter-actions">
            <button @click="loadFilterPreset" class="btn-link">
              Load Preset
            </button>
            <button @click="saveCurrentFilters" class="btn-link">
              Save Preset
            </button>
            <button @click="clearAllFilters" class="btn-link text-danger">
              Clear All
            </button>
          </div>
        </div>
        
        <div class="filters-content">
          <!-- Content Type Filter -->
          <div class="filter-group">
            <label class="filter-label">Content Type</label>
            <div class="filter-checkboxes">
              <label
                v-for="type in availableTypes"
                :key="type.value"
                class="checkbox-label"
              >
                <input
                  v-model="filters.types"
                  :value="type.value"
                  type="checkbox"
                  class="checkbox-input"
                >
                <span class="checkbox-custom"></span>
                <span class="checkbox-text">{{ type.label }}</span>
                <span class="type-count">{{ type.count }}</span>
              </label>
            </div>
          </div>
          
          <!-- Date Range Filter -->
          <div class="filter-group">
            <label class="filter-label">Date Range</label>
            <div class="date-range-inputs">
              <input
                v-model="filters.dateRange.start"
                type="date"
                class="form-input"
                placeholder="Start date"
              >
              <span class="date-separator">to</span>
              <input
                v-model="filters.dateRange.end"
                type="date"
                class="form-input"
                placeholder="End date"
              >
            </div>
          </div>
          
          <!-- User/Author Filter -->
          <div class="filter-group">
            <label class="filter-label">User/Author</label>
            <select
              v-model="filters.user"
              class="form-select"
              multiple
            >
              <option value="">All Users</option>
              <option
                v-for="user in availableUsers"
                :key="user.id"
                :value="user.id"
              >
                {{ user.name }}
              </option>
            </select>
          </div>
          
          <!-- Status Filter -->
          <div class="filter-group">
            <label class="filter-label">Status</label>
            <div class="filter-buttons">
              <button
                v-for="status in availableStatuses"
                :key="status.value"
                @click="toggleStatusFilter(status.value)"
                class="status-btn"
                :class="{ 
                  'active': filters.status.includes(status.value),
                  [status.class]: true
                }"
              >
                {{ status.label }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="filters-footer">
          <div class="filter-summary">
            {{ activeFiltersCount }} filters active
          </div>
          <button @click="applyFilters" class="btn-primary">
            Apply Filters
          </button>
        </div>
      </div>
    </transition>

    <!-- Search Results -->
    <div v-if="showResults" class="search-results">
      <!-- Results Header -->
      <div class="results-header">
        <div class="results-info">
          <span class="results-count">
            {{ searchResults.total.toLocaleString() }} results
          </span>
          <span v-if="searchResults.search_time" class="search-time">
            ({{ searchResults.search_time }}ms)
          </span>
        </div>
        
        <div class="results-actions">
          <button @click="exportResults" class="btn-link">
            Export
          </button>
          <button @click="closeResults" class="btn-link">
            Close
          </button>
        </div>
      </div>

      <!-- Results Facets -->
      <div v-if="searchResults.facets && searchResults.facets.types" class="results-facets">
        <button
          v-for="facet in searchResults.facets.types"
          :key="facet.value"
          @click="filterByType(facet.value)"
          class="facet-btn"
          :class="{ 'active': filters.types.includes(facet.value) }"
        >
          {{ facet.label }} ({{ facet.count }})
        </button>
      </div>

      <!-- Results List -->
      <div class="results-list">
        <div
          v-for="result in searchResults.results"
          :key="`${result.type}-${result.id}`"
          class="result-item"
          @click="openResult(result)"
        >
          <div class="result-icon">
            <svg class="icon" viewBox="0 0 24 24">
              <path :d="getResultIcon(result.type)"/>
            </svg>
          </div>
          
          <div class="result-content">
            <div class="result-header">
              <h4 class="result-title" v-html="result.title"></h4>
              <span class="result-type">{{ getTypeLabel(result.type) }}</span>
            </div>
            
            <p class="result-description" v-html="result.description"></p>
            
            <div class="result-meta">
              <span v-if="result.metadata.created_at" class="result-date">
                {{ formatDate(result.metadata.created_at) }}
              </span>
              <span class="result-score">
                Score: {{ result.score.toFixed(1) }}
              </span>
            </div>
          </div>
          
          <div class="result-actions">
            <button
              @click.stop="openResult(result)"
              class="btn-sm btn-primary"
            >
              Open
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="searchResults.total_pages > 1" class="results-pagination">
        <button
          @click="previousPage"
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          Previous
        </button>
        
        <div class="pagination-info">
          Page {{ currentPage }} of {{ searchResults.total_pages }}
        </div>
        
        <button
          @click="nextPage"
          :disabled="currentPage === searchResults.total_pages"
          class="pagination-btn"
        >
          Next
        </button>
      </div>
      
      <!-- No Results -->
      <div v-if="searchResults.results.length === 0" class="no-results">
        <svg class="icon-large" viewBox="0 0 24 24">
          <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,17A1.5,1.5 0 0,1 10.5,15.5A1.5,1.5 0 0,1 12,14A1.5,1.5 0 0,1 13.5,15.5A1.5,1.5 0 0,1 12,17M12,13C10.89,13 10,12.11 10,11V8C10,6.89 10.89,6 12,6C13.11,6 14,6.89 14,8V11C14,12.11 13.11,13 12,13Z"/>
        </svg>
        <h3>No results found</h3>
        <p>Try adjusting your search terms or filters</p>
      </div>
    </div>

    <!-- Filter Preset Modal -->
    <teleport to="body">
      <div v-if="showPresetModal" class="modal-overlay" @click="closePresetModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ presetModalMode === 'save' ? 'Save Filter Preset' : 'Load Filter Preset' }}</h3>
            <button @click="closePresetModal" class="modal-close">
              <svg class="icon" viewBox="0 0 24 24">
                <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <div v-if="presetModalMode === 'save'">
              <label class="form-label">Preset Name</label>
              <input
                v-model="presetName"
                type="text"
                class="form-input"
                placeholder="Enter preset name"
                @keydown.enter="saveFilterPreset"
              >
            </div>
            
            <div v-else>
              <label class="form-label">Select Preset</label>
              <div class="preset-list">
                <div
                  v-for="preset in filterPresets"
                  :key="preset.name"
                  class="preset-item"
                  @click="loadPreset(preset)"
                >
                  <div class="preset-info">
                    <h4>{{ preset.name }}</h4>
                    <p>{{ formatDate(preset.created_at) }}</p>
                  </div>
                  <button
                    @click.stop="deletePreset(preset.name)"
                    class="preset-delete"
                  >
                    <svg class="icon" viewBox="0 0 24 24">
                      <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button @click="closePresetModal" class="btn-secondary">
              Cancel
            </button>
            <button
              v-if="presetModalMode === 'save'"
              @click="saveFilterPreset"
              :disabled="!presetName"
              class="btn-primary"
            >
              Save Preset
            </button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';

export default {
  name: 'GlobalSearch',
  props: {
    placeholder: {
      type: String,
      default: 'Search users, clients, scenarios...'
    },
    autoFocus: {
      type: Boolean,
      default: false
    }
  },
  
  setup(props) {
    const router = useRouter();
    const authStore = useAuthStore();
    
    // Refs
    const searchInput = ref(null);
    const searchQuery = ref('');
    const expanded = ref(false);
    const showFilters = ref(false);
    const showResults = ref(false);
    const showSuggestions = ref(false);
    const loading = ref(false);
    const currentPage = ref(1);
    const hoveredSuggestion = ref(-1);
    
    // Modal state
    const showPresetModal = ref(false);
    const presetModalMode = ref('save'); // 'save' or 'load'
    const presetName = ref('');
    
    // Data
    const searchResults = reactive({
      results: [],
      total: 0,
      total_pages: 0,
      search_time: 0,
      facets: {}
    });
    
    const suggestions = ref([]);
    const filterPresets = ref([]);
    
    // Filters
    const filters = reactive({
      types: [],
      dateRange: {
        start: '',
        end: ''
      },
      user: '',
      status: []
    });
    
    // Available filter options
    const availableTypes = ref([
      { value: 'user', label: 'Users', count: 0 },
      { value: 'client', label: 'Clients', count: 0 },
      { value: 'scenario', label: 'Scenarios', count: 0 },
      { value: 'ticket', label: 'Support Tickets', count: 0 },
      { value: 'audit', label: 'Audit Logs', count: 0 }
    ]);
    
    const availableUsers = ref([]);
    
    const availableStatuses = ref([
      { value: 'active', label: 'Active', class: 'status-active' },
      { value: 'inactive', label: 'Inactive', class: 'status-inactive' },
      { value: 'pending', label: 'Pending', class: 'status-pending' },
      { value: 'resolved', label: 'Resolved', class: 'status-resolved' }
    ]);
    
    // Computed
    const activeFiltersCount = computed(() => {
      let count = 0;
      count += filters.types.length;
      if (filters.dateRange.start || filters.dateRange.end) count++;
      if (filters.user) count++;
      count += filters.status.length;
      return count;
    });
    
    // Debounced search
    let searchTimeout;
    const debounceSearch = (callback, delay = 300) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(callback, delay);
    };
    
    // Methods
    const handleInput = () => {
      showSuggestions.value = true;
      
      if (searchQuery.value.length >= 2) {
        debounceSearch(() => {
          loadSuggestions();
          performSearch();
        });
      } else {
        suggestions.value = [];
        showResults.value = false;
      }
    };
    
    const handleFocus = () => {
      expanded.value = true;
      if (searchQuery.value.length >= 2) {
        showSuggestions.value = true;
      }
    };
    
    const handleKeydown = (event) => {
      if (event.key === 'Escape') {
        closeFocus();
      } else if (event.key === 'Enter') {
        if (hoveredSuggestion.value >= 0 && suggestions.value.length > 0) {
          selectSuggestion(suggestions.value[hoveredSuggestion.value]);
        } else {
          performSearch();
        }
      } else if (event.key === 'ArrowDown') {
        event.preventDefault();
        if (suggestions.value.length > 0) {
          hoveredSuggestion.value = Math.min(
            hoveredSuggestion.value + 1,
            suggestions.value.length - 1
          );
        }
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        if (suggestions.value.length > 0) {
          hoveredSuggestion.value = Math.max(hoveredSuggestion.value - 1, 0);
        }
      }
    };
    
    const selectSuggestion = (suggestion) => {
      searchQuery.value = suggestion;
      showSuggestions.value = false;
      hoveredSuggestion.value = -1;
      performSearch();
    };
    
    const loadSuggestions = async () => {
      if (!searchQuery.value || searchQuery.value.length < 2) {
        suggestions.value = [];
        return;
      }
      
      try {
        const response = await api.get('/api/admin/search/suggestions/', {
          params: { q: searchQuery.value }
        });
        suggestions.value = response.data || [];
      } catch (error) {
        console.error('Failed to load suggestions:', error);
        suggestions.value = [];
      }
    };
    
    const performSearch = async () => {
      if (!searchQuery.value.trim()) {
        showResults.value = false;
        return;
      }
      
      loading.value = true;
      showSuggestions.value = false;
      
      try {
        const params = {
          q: searchQuery.value,
          page: currentPage.value,
          ...getActiveFilters()
        };
        
        const response = await api.get('/api/admin/search/', { params });
        
        Object.assign(searchResults, response.data);
        showResults.value = true;
        
        // Update type counts
        if (response.data.facets && response.data.facets.types) {
          response.data.facets.types.forEach(facet => {
            const type = availableTypes.value.find(t => t.value === facet.value);
            if (type) {
              type.count = facet.count;
            }
          });
        }
        
      } catch (error) {
        console.error('Search failed:', error);
        showResults.value = false;
      } finally {
        loading.value = false;
      }
    };
    
    const getActiveFilters = () => {
      const activeFilters = {};
      
      if (filters.types.length > 0) {
        activeFilters.types = filters.types;
      }
      
      if (filters.dateRange.start) {
        activeFilters.start_date = filters.dateRange.start;
      }
      
      if (filters.dateRange.end) {
        activeFilters.end_date = filters.dateRange.end;
      }
      
      if (filters.user) {
        activeFilters.user = filters.user;
      }
      
      if (filters.status.length > 0) {
        activeFilters.status = filters.status;
      }
      
      return activeFilters;
    };
    
    const toggleFilters = () => {
      showFilters.value = !showFilters.value;
      if (showFilters.value) {
        loadFilterOptions();
      }
    };
    
    const toggleStatusFilter = (status) => {
      const index = filters.status.indexOf(status);
      if (index > -1) {
        filters.status.splice(index, 1);
      } else {
        filters.status.push(status);
      }
    };
    
    const filterByType = (type) => {
      const index = filters.types.indexOf(type);
      if (index > -1) {
        filters.types.splice(index, 1);
      } else {
        filters.types.push(type);
      }
      applyFilters();
    };
    
    const applyFilters = () => {
      currentPage.value = 1;
      performSearch();
    };
    
    const clearSearch = () => {
      searchQuery.value = '';
      showResults.value = false;
      showSuggestions.value = false;
      suggestions.value = [];
    };
    
    const clearAllFilters = () => {
      filters.types = [];
      filters.dateRange.start = '';
      filters.dateRange.end = '';
      filters.user = '';
      filters.status = [];
      applyFilters();
    };
    
    const closeFocus = () => {
      expanded.value = false;
      showSuggestions.value = false;
      searchInput.value?.blur();
    };
    
    const closeResults = () => {
      showResults.value = false;
    };
    
    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
        performSearch();
      }
    };
    
    const nextPage = () => {
      if (currentPage.value < searchResults.total_pages) {
        currentPage.value++;
        performSearch();
      }
    };
    
    const openResult = (result) => {
      router.push(result.url);
    };
    
    const exportResults = async () => {
      try {
        const params = {
          q: searchQuery.value,
          format: 'csv',
          ...getActiveFilters()
        };
        
        const response = await api.get('/api/admin/search/export/', {
          params,
          responseType: 'blob'
        });
        
        // Download file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `search-results-${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
      } catch (error) {
        console.error('Export failed:', error);
      }
    };
    
    const loadFilterOptions = async () => {
      try {
        const response = await api.get('/api/admin/search/filter-options/');
        availableUsers.value = response.data.users || [];
      } catch (error) {
        console.error('Failed to load filter options:', error);
      }
    };
    
    const loadFilterPreset = () => {
      presetModalMode.value = 'load';
      showPresetModal.value = true;
      loadFilterPresets();
    };
    
    const saveCurrentFilters = () => {
      presetModalMode.value = 'save';
      presetName.value = '';
      showPresetModal.value = true;
    };
    
    const loadFilterPresets = async () => {
      try {
        const response = await api.get('/api/admin/search/filter-presets/');
        filterPresets.value = response.data || [];
      } catch (error) {
        console.error('Failed to load filter presets:', error);
      }
    };
    
    const saveFilterPreset = async () => {
      if (!presetName.value) return;
      
      try {
        await api.post('/api/admin/search/filter-presets/', {
          name: presetName.value,
          filters: getActiveFilters()
        });
        
        closePresetModal();
        // Show success message
      } catch (error) {
        console.error('Failed to save filter preset:', error);
      }
    };
    
    const loadPreset = (preset) => {
      // Apply preset filters
      filters.types = preset.filters.types || [];
      filters.dateRange.start = preset.filters.start_date || '';
      filters.dateRange.end = preset.filters.end_date || '';
      filters.user = preset.filters.user || '';
      filters.status = preset.filters.status || [];
      
      closePresetModal();
      applyFilters();
    };
    
    const deletePreset = async (name) => {
      try {
        await api.delete(`/api/admin/search/filter-presets/${name}/`);
        loadFilterPresets();
      } catch (error) {
        console.error('Failed to delete preset:', error);
      }
    };
    
    const closePresetModal = () => {
      showPresetModal.value = false;
      presetName.value = '';
    };
    
    const getResultIcon = (type) => {
      const icons = {
        user: 'M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z',
        client: 'M16,4C18.21,4 20,5.79 20,8C20,10.21 18.21,12 16,12C13.79,12 12,10.21 12,8C12,5.79 13.79,4 16,4M16,14C20.42,14 24,15.79 24,18V20H8V18C8,15.79 11.58,14 16,14Z',
        scenario: 'M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,5V19H5V5H19Z',
        ticket: 'M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z',
        audit: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z'
      };
      return icons[type] || icons.user;
    };
    
    const getTypeLabel = (type) => {
      const labels = {
        user: 'User',
        client: 'Client',
        scenario: 'Scenario',
        ticket: 'Support Ticket',
        audit: 'Audit Log'
      };
      return labels[type] || type;
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString();
    };
    
    // Lifecycle
    onMounted(() => {
      if (props.autoFocus) {
        nextTick(() => {
          searchInput.value?.focus();
        });
      }
      
      // Click outside to close
      document.addEventListener('click', (event) => {
        if (!event.target.closest('.global-search')) {
          expanded.value = false;
          showSuggestions.value = false;
        }
      });
    });
    
    onUnmounted(() => {
      clearTimeout(searchTimeout);
    });
    
    return {
      // Refs
      searchInput,
      searchQuery,
      expanded,
      showFilters,
      showResults,
      showSuggestions,
      loading,
      currentPage,
      hoveredSuggestion,
      showPresetModal,
      presetModalMode,
      presetName,
      
      // Data
      searchResults,
      suggestions,
      filterPresets,
      filters,
      availableTypes,
      availableUsers,
      availableStatuses,
      
      // Computed
      activeFiltersCount,
      
      // Methods
      handleInput,
      handleFocus,
      handleKeydown,
      selectSuggestion,
      performSearch,
      toggleFilters,
      toggleStatusFilter,
      filterByType,
      applyFilters,
      clearSearch,
      clearAllFilters,
      closeFocus,
      closeResults,
      previousPage,
      nextPage,
      openResult,
      exportResults,
      loadFilterPreset,
      saveCurrentFilters,
      saveFilterPreset,
      loadPreset,
      deletePreset,
      closePresetModal,
      getResultIcon,
      getTypeLabel,
      formatDate
    };
  }
};
</script>

<style scoped>
/* Global Search Styles */
.global-search {
  position: relative;
  max-width: 600px;
  width: 100%;
}

.global-search.expanded {
  z-index: 1000;
}

/* Search Container */
.search-container {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.search-input-wrapper:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-icon {
  width: 20px;
  height: 20px;
  fill: #6b7280;
  margin-right: 12px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  background: transparent;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
}

.filter-btn, .clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn {
  background: #f1f5f9;
  color: #64748b;
}

.filter-btn:hover {
  background: #e2e8f0;
  color: #475569;
}

.filter-btn.active {
  background: #3b82f6;
  color: white;
}

.clear-btn {
  background: #fee2e2;
  color: #dc2626;
}

.clear-btn:hover {
  background: #fecaca;
}

.search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.search-loading svg {
  width: 20px;
  height: 20px;
  fill: #3b82f6;
}

.spin {
  animation: spin 1s linear infinite;
}

/* Search Suggestions */
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-top: 4px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  overflow: hidden;
  z-index: 1100;
}

.suggestions-header {
  padding: 12px 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
  width: 100%;
}

.suggestion-item:hover,
.suggestion-item.highlighted {
  background: #f1f5f9;
}

.suggestion-item .icon {
  width: 16px;
  height: 16px;
  fill: #6b7280;
}

/* Filters Panel */
.filters-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-top: 4px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  z-index: 1050;
}

.filters-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.filters-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.filter-actions {
  display: flex;
  gap: 16px;
}

.btn-link {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 14px;
  text-decoration: none;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-link.text-danger {
  color: #dc2626;
}

.filters-content {
  padding: 20px;
  display: grid;
  gap: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

/* Filter Controls */
.filter-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 16px;
  height: 16px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  position: relative;
  transition: all 0.2s ease;
}

.checkbox-input:checked + .checkbox-custom {
  background: #3b82f6;
  border-color: #3b82f6;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 5px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-text {
  font-size: 14px;
  color: #374151;
}

.type-count {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: auto;
}

.date-range-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-separator {
  font-size: 14px;
  color: #6b7280;
}

.form-input, .form-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.status-btn {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.status-btn:hover {
  background: #f9fafb;
}

.status-btn.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.status-active.active {
  border-color: #10b981;
  background: #d1fae5;
  color: #047857;
}

.status-inactive.active {
  border-color: #6b7280;
  background: #f3f4f6;
  color: #374151;
}

.status-pending.active {
  border-color: #f59e0b;
  background: #fef3c7;
  color: #92400e;
}

.status-resolved.active {
  border-color: #8b5cf6;
  background: #ede9fe;
  color: #6d28d9;
}

.filters-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
}

.filter-summary {
  font-size: 14px;
  color: #6b7280;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-primary:hover {
  background: #2563eb;
}

/* Search Results */
.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-top: 4px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  max-height: 600px;
  overflow: hidden;
  z-index: 1000;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.results-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.results-count {
  font-weight: 600;
  color: #374151;
}

.search-time {
  font-size: 12px;
  color: #6b7280;
}

.results-actions {
  display: flex;
  gap: 16px;
}

.results-facets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.facet-btn {
  padding: 4px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  color: #6b7280;
  transition: all 0.2s ease;
}

.facet-btn:hover {
  background: #f9fafb;
}

.facet-btn.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.results-list {
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.result-item:hover {
  background: #f9fafb;
}

.result-item:last-child {
  border-bottom: none;
}

.result-icon {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 8px;
  flex-shrink: 0;
  margin-top: 4px;
}

.result-icon .icon {
  width: 20px;
  height: 20px;
  fill: #6b7280;
  margin-top: 10px;
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 4px;
}

.result-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #111827;
  line-height: 1.4;
}

.result-title :deep(mark) {
  background: #fef3c7;
  color: #92400e;
  padding: 1px 2px;
  border-radius: 2px;
}

.result-type {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.result-description {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.4;
}

.result-description :deep(mark) {
  background: #fef3c7;
  color: #92400e;
  padding: 1px 2px;
  border-radius: 2px;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #9ca3af;
}

.result-actions {
  display: flex;
  align-items: flex-start;
  margin-top: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.btn-sm.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-sm.btn-primary:hover {
  background: #2563eb;
}

/* Pagination */
.results-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.pagination-btn:hover:not(:disabled) {
  background: #f9fafb;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

/* No Results */
.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.icon-large {
  width: 48px;
  height: 48px;
  fill: #d1d5db;
  margin-bottom: 16px;
}

.no-results h3 {
  margin: 0 0 8px 0;
  color: #374151;
}

.no-results p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px rgba(0,0,0,0.25);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.modal-close:hover {
  background: #f3f4f6;
}

.modal-close .icon {
  width: 20px;
  height: 20px;
  fill: #6b7280;
}

.modal-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.preset-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.preset-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preset-item:hover {
  background: #f9fafb;
  border-color: #3b82f6;
}

.preset-info {
  flex: 1;
  min-width: 0;
}

.preset-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
}

.preset-info p {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
}

.preset-delete {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  color: #dc2626;
}

.preset-delete:hover {
  background: #fee2e2;
}

.preset-delete .icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e2e8f0;
}

.btn-secondary {
  background: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from, .slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Common icon styles */
.icon {
  fill: currentColor;
}

/* Responsive */
@media (max-width: 768px) {
  .filters-content {
    grid-template-columns: 1fr;
  }
  
  .filter-checkboxes {
    flex-direction: column;
    gap: 8px;
  }
  
  .date-range-inputs {
    flex-direction: column;
    align-items: stretch;
  }
  
  .result-item {
    flex-direction: column;
    gap: 12px;
  }
  
  .result-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
}
</style>