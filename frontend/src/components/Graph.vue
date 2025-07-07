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
    }
  },
  data() {
    return {
      chartInstance: null
    };
  },
  mounted() {
    this.renderChart();
  },
  watch: {
    data: {
      handler() {
        this.renderChart();
      },
      deep: true
    },
    options: {
      handler() {
        this.renderChart();
      },
      deep: true
    }
  },
  methods: {
    renderChart() {
      // Destroy previous chart instance if exists
      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
      // Only render if data and at least one dataset
      if (!this.data || !this.data.labels || !this.data.datasets || !this.data.datasets.length) {
        return;
      }
      const options = {
        responsive: true,
        maintainAspectRatio: false,
        ...this.options
      };
      
      // Determine chart type based on data structure
      let chartType = this.type || 'line';
      
      // If data has multiple datasets with single values per dataset, it's likely a bar chart
      if (this.data.datasets.length > 1 && 
          this.data.datasets[0].data && 
          this.data.datasets[0].data.length > 1 && 
          this.options && 
          this.options.indexAxis) {
        chartType = 'bar';
      }
      
      // Register custom plugins if they exist
      if (options.plugins && options.plugins.totalColumnHighlight) {
        Chart.register({
          id: 'totalColumnHighlight',
          beforeDraw: options.plugins.totalColumnHighlight.beforeDraw
        });
        // Remove from options to avoid duplicate registration
        delete options.plugins.totalColumnHighlight;
      }
      
      this.chartInstance = new Chart(this.$refs.canvas, {
        type: chartType,
        data: this.data,
        options
      });
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