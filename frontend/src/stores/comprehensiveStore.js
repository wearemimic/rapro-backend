import { defineStore } from 'pinia';
import axios from 'axios';
import { apiService } from '@/services/api';

export const useComprehensiveStore = defineStore('comprehensive', {
  state: () => ({
    // Data storage
    comprehensiveData: {},  // Keyed by scenarioId

    // Loading states
    loading: {},  // Keyed by scenarioId

    // Error states
    errors: {},  // Keyed by scenarioId

    // Column visibility preferences
    columnPreferences: {
      showDemographics: true,
      showIncomeSources: true,
      showAssetBalances: true,
      showRMDs: true,
      showTaxes: true,
      showMedicare: true,
      showNetIncome: true
    },

    // Cache timestamp (to implement cache expiration)
    cacheTimestamps: {}  // Keyed by scenarioId
  }),

  getters: {
    /**
     * Get comprehensive data for a specific scenario
     */
    getScenarioData: (state) => (scenarioId) => {
      return state.comprehensiveData[scenarioId] || null;
    },

    /**
     * Check if data is loading for a scenario
     */
    isLoading: (state) => (scenarioId) => {
      return state.loading[scenarioId] || false;
    },

    /**
     * Get error for a specific scenario
     */
    getError: (state) => (scenarioId) => {
      return state.errors[scenarioId] || null;
    },

    /**
     * Get years array for a specific scenario
     */
    getYears: (state) => (scenarioId) => {
      return state.comprehensiveData[scenarioId]?.years || [];
    },

    /**
     * Get summary metadata for a scenario
     */
    getSummary: (state) => (scenarioId) => {
      return state.comprehensiveData[scenarioId]?.summary || null;
    },

    /**
     * Check if cache is valid (within 5 minutes)
     */
    isCacheValid: (state) => (scenarioId) => {
      const timestamp = state.cacheTimestamps[scenarioId];
      if (!timestamp) return false;

      const fiveMinutes = 5 * 60 * 1000;
      return (Date.now() - timestamp) < fiveMinutes;
    },

    /**
     * Get all unique income source IDs from the data
     */
    getIncomeSourceIds: (state) => (scenarioId) => {
      const years = state.comprehensiveData[scenarioId]?.years || [];
      const sourceIds = new Set();

      years.forEach(year => {
        if (year.income_by_source) {
          Object.keys(year.income_by_source).forEach(id => sourceIds.add(id));
        }
      });

      return Array.from(sourceIds);
    },

    /**
     * Get all unique asset IDs from the data
     */
    getAssetIds: (state) => (scenarioId) => {
      const years = state.comprehensiveData[scenarioId]?.years || [];
      const assetIds = new Set();

      years.forEach(year => {
        if (year.asset_balances) {
          Object.keys(year.asset_balances).forEach(id => assetIds.add(id));
        }
      });

      return Array.from(assetIds);
    }
  },

  actions: {
    /**
     * Fetch comprehensive data for a scenario
     */
    async fetchComprehensiveData(scenarioId, forceRefresh = false) {
      // Check cache validity
      if (!forceRefresh && this.isCacheValid(scenarioId)) {
        console.log(`Using cached data for scenario ${scenarioId}`);
        return this.comprehensiveData[scenarioId];
      }

      // Set loading state
      this.loading[scenarioId] = true;
      this.errors[scenarioId] = null;

      try {
        const config = apiService.getConfig();
        const url = apiService.getUrl(`/api/scenarios/${scenarioId}/comprehensive-summary/`);

        const response = await axios.get(url, config);

        // Store the data
        this.comprehensiveData[scenarioId] = response.data;
        this.cacheTimestamps[scenarioId] = Date.now();

        console.log(`Fetched comprehensive data for scenario ${scenarioId}:`, response.data);

        return response.data;
      } catch (error) {
        console.error(`Error fetching comprehensive data for scenario ${scenarioId}:`, error);

        const errorMessage = error.response?.data?.error ||
                           error.response?.data?.message ||
                           'Failed to load comprehensive financial summary';

        this.errors[scenarioId] = errorMessage;
        throw error;
      } finally {
        this.loading[scenarioId] = false;
      }
    },

    /**
     * Clear data for a specific scenario
     */
    clearScenarioData(scenarioId) {
      delete this.comprehensiveData[scenarioId];
      delete this.loading[scenarioId];
      delete this.errors[scenarioId];
      delete this.cacheTimestamps[scenarioId];
    },

    /**
     * Clear all cached data
     */
    clearAllData() {
      this.comprehensiveData = {};
      this.loading = {};
      this.errors = {};
      this.cacheTimestamps = {};
    },

    /**
     * Update column preferences
     */
    updateColumnPreferences(preferences) {
      this.columnPreferences = {
        ...this.columnPreferences,
        ...preferences
      };

      // Save to localStorage for persistence
      localStorage.setItem('comprehensiveColumnPreferences', JSON.stringify(this.columnPreferences));
    },

    /**
     * Load column preferences from localStorage
     */
    loadColumnPreferences() {
      const saved = localStorage.getItem('comprehensiveColumnPreferences');
      if (saved) {
        try {
          this.columnPreferences = JSON.parse(saved);
        } catch (e) {
          console.error('Failed to load column preferences:', e);
        }
      }
    },

    /**
     * Export data to CSV
     */
    exportToCSV(scenarioId) {
      const data = this.comprehensiveData[scenarioId];
      if (!data || !data.years || data.years.length === 0) {
        console.error('No data to export');
        return;
      }

      const years = data.years;

      // Build CSV headers
      const headers = [
        'Year', 'Primary Age', 'Spouse Age',
        'Gross Income', 'Federal Tax', 'State Tax', 'After Tax Income',
        'Medicare Total', 'After Medicare Income', 'Remaining Income'
      ];

      // Build CSV rows
      const rows = years.map(year => [
        year.year,
        year.primary_age || '',
        year.spouse_age || '',
        year.gross_income_total || 0,
        year.federal_tax || 0,
        year.state_tax || 0,
        year.after_tax_income || 0,
        year.total_medicare || 0,
        year.after_medicare_income || 0,
        year.remaining_income || 0
      ]);

      // Convert to CSV string
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');

      // Create download link
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);

      link.setAttribute('href', url);
      link.setAttribute('download', `comprehensive_summary_${scenarioId}_${Date.now()}.csv`);
      link.style.visibility = 'hidden';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }
});