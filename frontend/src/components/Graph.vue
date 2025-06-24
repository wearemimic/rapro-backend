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
      const options = {
        responsive: true,
        maintainAspectRatio: false,
        ...this.options
      };
      this.chartInstance = new Chart(this.$refs.canvas, {
        type: 'line',
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