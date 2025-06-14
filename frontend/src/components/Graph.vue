<template>
  <canvas ref="canvas" style="height: 300px;"></canvas>
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
      this.chartInstance = new Chart(this.$refs.canvas, {
        type: 'line',
        data: this.data,
        options: this.options
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