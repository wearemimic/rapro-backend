<template>
  <div>
    <h3>Test Chart</h3>
    <canvas ref="testCanvas" width="400" height="200"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'TestChart',
  mounted() {
    console.log('🧪 TestChart mounted');
    console.log('🧪 Canvas ref:', this.$refs.testCanvas);
    
    try {
      const chart = new Chart(this.$refs.testCanvas, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
          datasets: [{
            label: 'Test Data',
            data: [12, 19, 3, 5, 2],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
          }]
        },
        options: {
          responsive: false,
          plugins: {
            legend: {
              display: true
            }
          }
        }
      });
      console.log('✅ Test chart created successfully:', chart);
    } catch (error) {
      console.error('❌ Test chart error:', error);
      console.error('❌ Stack:', error.stack);
    }
  }
}
</script>