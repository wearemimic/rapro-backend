<template>
  <div class="lifetime-benefits-chart">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import socialSecurityService from '@/services/socialSecurityService.js';

Chart.register(...registerables);

export default {
  name: 'LifetimeBenefitsChart',
  props: {
    ssData: {
      type: Object,
      required: true
    },
    primaryClaimingAge: {
      type: Number,
      required: true
    },
    spouseClaimingAge: {
      type: Number,
      default: null
    },
    primaryLifeExpectancy: {
      type: Number,
      required: true
    },
    spouseLifeExpectancy: {
      type: Number,
      default: null
    },
    height: {
      type: Number,
      default: 400
    }
  },
  data() {
    return {
      chart: null,
      claimingAges: [62, 63, 64, 65, 66, 67, 68, 69, 70]
    };
  },
  watch: {
    primaryClaimingAge() {
      this.updateChart();
    },
    spouseClaimingAge() {
      this.updateChart();
    },
    primaryLifeExpectancy() {
      this.updateChart();
    },
    spouseLifeExpectancy() {
      this.updateChart();
    },
    ssData: {
      handler() {
        this.updateChart();
      },
      deep: true
    }
  },
  mounted() {
    this.$nextTick(() => {
      if (this.$refs.chartCanvas) {
        this.initializeChart();
      } else {
        console.log('⚠️ Chart canvas not available yet');
        setTimeout(() => {
          if (this.$refs.chartCanvas) {
            this.initializeChart();
          }
        }, 100);
      }
    });
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
  methods: {
    initializeChart() {
      if (!this.$refs.chartCanvas) {
        console.error('Chart canvas element not found');
        return;
      }
      
      const ctx = this.$refs.chartCanvas.getContext('2d');
      
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: []
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Cumulative Social Security Benefits by Age',
              font: {
                size: 16,
                weight: 'bold'
              }
            },
            legend: {
              display: true,
              position: 'bottom'
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  const value = context.raw;
                  const formattedValue = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                  }).format(value);
                  return `${context.dataset.label}: ${formattedValue}`;
                }
              }
            }
          },
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: 'Age',
                font: {
                  weight: 'bold'
                }
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            y: {
              display: true,
              title: {
                display: true,
                text: 'Cumulative Benefits ($)',
                font: {
                  weight: 'bold'
                }
              },
              ticks: {
                callback: function(value) {
                  return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                  }).format(value);
                }
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          }
        }
      });
      
      this.updateChart();
    },

    updateChart() {
      if (!this.chart || !this.ssData.primary) {
        return;
      }

      const datasets = [];
      const labels = [];

      // Generate age range for x-axis
      const minAge = Math.min(...this.claimingAges);
      const maxAge = Math.max(this.primaryLifeExpectancy, this.spouseLifeExpectancy || 0);
      
      for (let age = minAge; age <= maxAge; age++) {
        labels.push(age);
      }

      // Generate datasets for different claiming ages
      this.claimingAges.forEach(claimingAge => {
        // Primary worker benefits
        const primaryData = [];
        const primaryMonthlyBenefit = socialSecurityService.calculateBenefit(
          this.ssData.primary.amountAtFRA,
          claimingAge
        );
        
        labels.forEach(age => {
          if (age < claimingAge) {
            primaryData.push(0);
          } else {
            const yearsOfBenefits = age - claimingAge;
            const cumulativeBenefits = primaryMonthlyBenefit * 12 * yearsOfBenefits;
            primaryData.push(cumulativeBenefits);
          }
        });

        // Highlight current claiming age with thicker line
        const isCurrentClaimingAge = claimingAge === Math.round(this.primaryClaimingAge);
        
        datasets.push({
          label: `Primary - Claim at ${claimingAge}`,
          data: primaryData,
          borderColor: socialSecurityService.getChartColor(claimingAge, isCurrentClaimingAge ? 1 : 0.6),
          backgroundColor: socialSecurityService.getChartColor(claimingAge, 0.1),
          borderWidth: isCurrentClaimingAge ? 4 : 2,
          tension: 0.1,
          pointRadius: isCurrentClaimingAge ? 6 : 3,
          pointHoverRadius: 8,
          fill: false
        });

        // Spouse benefits if available
        if (this.ssData.spouse && this.spouseLifeExpectancy) {
          const spouseData = [];
          const spouseMonthlyBenefit = socialSecurityService.calculateBenefit(
            this.ssData.spouse.amountAtFRA,
            claimingAge
          );
          
          labels.forEach(age => {
            if (age < claimingAge) {
              spouseData.push(0);
            } else {
              const yearsOfBenefits = age - claimingAge;
              const cumulativeBenefits = spouseMonthlyBenefit * 12 * yearsOfBenefits;
              spouseData.push(cumulativeBenefits);
            }
          });

          const isCurrentSpouseClaimingAge = claimingAge === Math.round(this.spouseClaimingAge || 67);
          
          datasets.push({
            label: `Spouse - Claim at ${claimingAge}`,
            data: spouseData,
            borderColor: socialSecurityService.getChartColor(claimingAge, isCurrentSpouseClaimingAge ? 1 : 0.4),
            backgroundColor: socialSecurityService.getChartColor(claimingAge, 0.05),
            borderWidth: isCurrentSpouseClaimingAge ? 4 : 1,
            borderDash: [5, 5], // Dashed line for spouse
            tension: 0.1,
            pointRadius: isCurrentSpouseClaimingAge ? 6 : 2,
            pointHoverRadius: 8,
            fill: false
          });
        }
      });

      // Add break-even markers if applicable
      if (this.primaryClaimingAge !== 67) {
        const breakEvenAnalysis = socialSecurityService.calculateBreakEvenAge(
          this.ssData.primary.amountAtFRA,
          67,
          this.primaryClaimingAge
        );
        
        if (breakEvenAnalysis && breakEvenAnalysis.breakEvenAge <= maxAge) {
          const breakEvenIndex = labels.findIndex(age => age >= breakEvenAnalysis.breakEvenAge);
          if (breakEvenIndex !== -1) {
            // Add vertical line annotation for break-even point
            datasets.push({
              label: `Break-Even Age (${Math.round(breakEvenAnalysis.breakEvenAge)})`,
              data: labels.map(age => age === labels[breakEvenIndex] ? this.getMaxYValue(datasets) : null),
              borderColor: 'rgba(255, 193, 7, 0.8)',
              backgroundColor: 'rgba(255, 193, 7, 0.2)',
              borderWidth: 3,
              pointRadius: 8,
              pointStyle: 'triangle',
              showLine: false,
              fill: false
            });
          }
        }
      }

      // Update chart data
      this.chart.data.labels = labels;
      this.chart.data.datasets = datasets;
      this.chart.update('none');
    },

    getMaxYValue(datasets) {
      let maxValue = 0;
      datasets.forEach(dataset => {
        if (dataset.data && Array.isArray(dataset.data)) {
          const dataMax = Math.max(...dataset.data.filter(val => val !== null && !isNaN(val)));
          if (dataMax > maxValue) {
            maxValue = dataMax;
          }
        }
      });
      return maxValue;
    },

    exportChart() {
      if (this.chart) {
        const link = document.createElement('a');
        link.download = 'lifetime-benefits-chart.png';
        link.href = this.chart.toBase64Image();
        link.click();
      }
    }
  }
};
</script>

<style scoped>
.lifetime-benefits-chart {
  position: relative;
  width: 100%;
  height: 100%;
}

canvas {
  max-width: 100%;
  height: auto !important;
}
</style>