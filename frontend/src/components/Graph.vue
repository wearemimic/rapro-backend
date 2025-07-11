<template>
  <div :style="`height: ${height}px;`">
    <canvas ref="canvas" :height="height" :style="`height: ${height}px;`"></canvas>
  </div>
</template>

<script>
import { Chart } from 'chart.js';

export default {
  props: {
    data: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    },
    height: {
      type: Number,
      default: 200
    },
    type: {
      type: String,
      default: 'line'
    },
    // Add a unique ID prop to distinguish between different graph instances
    graphId: {
      type: String,
      default: () => `graph-${Math.random().toString(36).substr(2, 9)}`
    }
  },
  data() {
    return {
      chartInstance: null,
      // Track registered plugins to avoid duplicate registration
      registeredPlugins: new Set()
    };
  },
  mounted() {
    this.renderChart();
  },
  watch: {
    data: {
      handler(newData) {
        // Create a deep copy of the data to avoid reference issues
        const dataCopy = JSON.parse(JSON.stringify(newData));
        this.renderChart(dataCopy);
      },
      deep: true
    },
    options: {
      handler(newOptions) {
        // Create a deep copy of the options to avoid reference issues
        const optionsCopy = JSON.parse(JSON.stringify(newOptions));
        this.renderChart(undefined, optionsCopy);
      },
      deep: true
    }
  },
  methods: {
    renderChart(dataCopy, optionsCopy) {
      try {
        // Use provided data copies or make copies of the props
        const safeData = dataCopy || (this.data ? JSON.parse(JSON.stringify(this.data)) : null);
        const safeOptions = optionsCopy || (this.options ? JSON.parse(JSON.stringify(this.options)) : {});
        
        // Only destroy the chart if we have new valid data to replace it
        if (safeData && safeData.labels && safeData.datasets && safeData.datasets.length) {
          // Destroy previous chart instance if exists
          if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
          }
        } else {
          // If we don't have valid data and no chart exists, just return
          if (!this.chartInstance) {
            return;
          }
          
          // If we have an existing chart but invalid data, keep the existing chart
          if (this.chartInstance) {
            console.log('Skipping chart update due to invalid data');
            return;
          }
        }
        
        // Validate data again after potential destruction
        if (!safeData || !safeData.labels || !safeData.datasets || !safeData.datasets.length) {
          console.error('Invalid chart data:', safeData);
          return;
        }
        
        const options = {
          responsive: true,
          maintainAspectRatio: false,
          ...safeOptions,
          animation: {
            duration: 500 // Shorter animation for smoother updates
          }
        };
        
        // Support mixed chart types: if any dataset has a 'type', use 'bar' as root type
        let chartType = this.type || 'line';
        if (safeData.datasets.some(ds => ds.type)) {
          chartType = 'bar';
        }
        
        // Register custom plugins if they exist, using the graphId to make them unique
        if (options.plugins && options.plugins.totalColumnHighlight) {
          const pluginId = `totalColumnHighlight-${this.graphId}`;
          
          // Only register if not already registered
          if (!this.registeredPlugins.has(pluginId)) {
            Chart.register({
              id: pluginId,
              beforeDraw: options.plugins.totalColumnHighlight.beforeDraw
            });
            this.registeredPlugins.add(pluginId);
          }
          
          // Update plugin reference in options to use our unique ID
          options.plugins.totalColumnHighlight = {
            ...options.plugins.totalColumnHighlight,
            id: pluginId
          };
        }
        
        this.chartInstance = new Chart(this.$refs.canvas, {
          type: chartType,
          data: safeData,
          options
        });
      } catch (error) {
        console.error('Error rendering chart:', error);
      }
    }
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  }
};
</script>