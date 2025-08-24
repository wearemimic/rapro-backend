<template>
  <div>
    <!-- Row for Chart and Circle Card -->
    <div class="row mb-3 mb-lg-5">
      <!-- Financial Chart Card (2/3 width) -->
      <div class="col-lg-8 col-md-7 mb-3 mb-lg-0">
        <div class="card h-100">
          <div class="card-body">
            <div class="financial-chart-container">
              <Graph 
                :data="chartData" 
                :options="chartOptions"
                :height="300"
                type="line"
              />
            </div>
          </div>
        </div>
      </div>
      <!-- Circle Card (1/3 width) -->
      <div class="col-lg-4 col-md-5 mb-3 mb-lg-0">
        <div class="card h-100 d-flex flex-column justify-content-center align-items-center">
          <div class="card-body w-100">
            <h5 class="mb-4 text-center">Taxes & Medicare as % of Gross Income</h5>
            <div class="circles-chart d-flex justify-content-center" style="padding-top:20px; min-height: 180px;">
              <div class="js-circle" id="circle-financial"></div>
            </div>
            <div class="mt-4">
              <div class="row text-center">
                <div class="col-6 mb-2">
                  <small class="text-muted d-block">Total Gross Income</small>
                  <strong class="text-primary">{{ formatCurrency(totalGrossIncome) }}</strong>
                </div>
                <div class="col-6 mb-2">
                  <small class="text-muted d-block">Total Taxes</small>
                  <strong class="text-danger">{{ formatCurrency(totalTax) }}</strong>
                </div>
                <div class="col-6 mb-2">
                  <small class="text-muted d-block">Total Medicare</small>
                  <strong class="text-warning">{{ formatCurrency(totalMedicare) }}</strong>
                </div>
                <div class="col-6 mb-2">
                  <small class="text-muted d-block">Net Income</small>
                  <strong class="text-success">{{ formatCurrency(netIncome) }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- End Row -->

    <!-- Financial Flow Diagram Section -->
    <div v-if="false" class="card mb-3 mb-lg-5">
      <div class="card-header card-header-content-between">
        <h4 class="card-header-title">Financial Flow Overview</h4>
        <div class="dropdown">
          <button type="button" class="btn btn-white btn-sm dropdown-toggle" @click="toggleDropdown('flow')" :aria-expanded="isDropdownOpen.flow">
            <i class="bi-download me-2"></i> Export
          </button>
          <div class="dropdown-menu dropdown-menu-sm-end" :class="{ show: isDropdownOpen.flow }">
            <span class="dropdown-header">Export Options</span>
            <a class="dropdown-item" href="javascript:;" @click="exportFlowToPDF">
              <img class="avatar avatar-xss avatar-4x3 me-2" src="/assets/svg/brands/pdf-icon.svg" alt="PDF">
              Export flow diagram to PDF
            </a>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div class="flow-chart-container">
          <svg id="financialFlowChart"></svg>
        </div>
        <div class="mt-3">
          <p class="text-muted small">
            This diagram shows the flow of your total income through taxes, Medicare, IRMAA, and other expenses to arrive at your net income.
            The width of each flow represents the relative amount.
          </p>
        </div>
      </div>
    </div>

    <!-- Table Card -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-header">
        <h4 class="card-header-title">Financial Overview Table</h4>
      </div>
      <div class="card-body">
        <div v-if="filteredResults.length" class="table-responsive">
          <table class="table table-hover">
            <thead class="thead-light">
              <tr>
                <th>Year</th>
                <th>Primary Age</th>
                <th v-if="client?.tax_status?.toLowerCase() !== 'single'">Spouse Age</th>
                <th>Gross Income</th>
                <th>AGI</th>
                <th>MAGI</th>
                <th>Tax Bracket</th>
                <th>Federal Tax</th>
                <th>Total Medicare</th>
                <th>Remaining Income</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in filteredResults" :key="row.year" :class="{ 'irmaa-bracket-row': isIrmaaBracketHit(row, idx) }">
                <td>{{ row.year }}</td>
                <td v-if="row.primary_age <= (Number(mortalityAge) || 90)">{{ row.primary_age }}</td>
                <td v-else></td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single' && row.spouse_age <= (Number(spouseMortalityAge) || 90)">{{ row.spouse_age }}</td>
                <td v-else-if="client?.tax_status?.toLowerCase() !== 'single'"></td>
                <td>{{ formatCurrency(row.gross_income) }}</td>
                <td>{{ formatCurrency(row.agi) }}</td>
                <td>{{ formatCurrency(row.magi) }}</td>
                <td>{{ row.tax_bracket }}</td>
                <td>{{ formatCurrency(row.federal_tax) }}</td>
                <td style="position: relative;">
                  {{ formatCurrency(row.total_medicare) }}
                  <span v-if="isIrmaaBracketHit(row, idx)" class="irmaa-info-icon" @click.stop="toggleIrmaaTooltip(idx)">
                    ℹ️
                  </span>
                  <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                    IRMAA Bracket: {{ getIrmaaBracketLabel(row) }}
                  </div>
                </td>
                <td>{{ formatCurrency(parseFloat(row.gross_income) - (parseFloat(row.federal_tax) + parseFloat(row.total_medicare))) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr style="font-weight: bold;">
                <td>Total</td>
                <td></td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single'"></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td>{{ formatCurrency(filteredResults.reduce((total, row) => total + parseFloat(row.federal_tax || 0), 0)) }}</td>
                <td>{{ formatCurrency(filteredResults.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0)) }}</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Disclosures Card -->
    <DisclosuresCard />
  </div>
</template>

<script>
import { jsPDF } from 'jspdf';
import { applyPlugin } from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';
import Graph from '../components/Graph.vue';
import DisclosuresCard from '../components/DisclosuresCard.vue';

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

const IRMAA_THRESHOLDS = {
  'single': [
    106000, 133000, 167000, 200000, 500000
  ],
  'married filing jointly': [
    212000, 266000, 334000, 400000, 750000
  ],
  'married filing separately': [
    106000, 394000
  ]
};
const IRMAA_LABELS = {
  'single': [
    '≤ $106,000',
    '$106,001 – $133,000',
    '$133,001 – $167,000',
    '$167,001 – $200,000',
    '$200,001 – $500,000',
    '>$500,000'
  ],
  'married filing jointly': [
    '≤ $212,000',
    '$212,001 – $266,000',
    '$266,001 – $334,000',
    '$334,001 – $400,000',
    '$400,001 – $750,000',
    '>$750,000'
  ],
  'married filing separately': [
    '≤ $106,000',
    '$106,001 – $394,000',
    '>$394,000'
  ]
};

export default {
  components: {
    Graph,
    DisclosuresCard
  },
  props: {
    scenarioResults: {
      type: Array,
      required: true
    },
    filteredResults: {
      type: Array,
      required: true
    },
    client: {
      type: Object,
      required: true
    },
    mortalityAge: {
      type: [Number, String],
      required: false
    },
    spouseMortalityAge: {
      type: [Number, String],
      required: false
    }
  },
  data() {
    return {
      isDropdownOpen: {
        financial: false,
        flow: false
      },
      openIrmaaTooltipIdx: null
    };
  },
  computed: {
    irmaaThresholds() {
      const status = (this.client?.tax_status || '').toLowerCase();
      if (status in IRMAA_THRESHOLDS) {
        return IRMAA_THRESHOLDS[status];
      }
      return IRMAA_THRESHOLDS['single'];
    },
    irmaaLabels() {
      const status = (this.client?.tax_status || '').toLowerCase();
      if (status in IRMAA_LABELS) {
        return IRMAA_LABELS[status];
      }
      return IRMAA_LABELS['single'];
    },
    totalGrossIncome() {
      return this.filteredResults.reduce((total, row) => total + parseFloat(row.gross_income || 0), 0);
    },
    totalTax() {
      return this.filteredResults.reduce((total, row) => total + parseFloat(row.federal_tax || 0), 0);
    },
    totalMedicare() {
      return this.filteredResults.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0);
    },
    netIncome() {
      return this.filteredResults.reduce((total, row) => {
        const gross = parseFloat(row.gross_income || 0);
        const tax = parseFloat(row.federal_tax || 0);
        const medicare = parseFloat(row.total_medicare || 0);
        return total + (gross - tax - medicare);
      }, 0);
    },
    chartData() {
      if (!this.filteredResults || !this.filteredResults.length) {
        console.warn('⚠️ FinancialOverview: No filtered results, returning empty chart data');
        return { labels: [], datasets: [] };
      }

      const labels = this.filteredResults.map(row => row.year.toString());
      const datasets = [
        {
          type: 'line',
          label: 'Gross Income',
          data: this.filteredResults.map(row => parseFloat(row.gross_income) || 0),
          borderColor: '#4285f4',
          backgroundColor: 'transparent',
          borderWidth: 3,
          tension: 0.3,
          yAxisID: 'y',
          pointRadius: 3,
          pointBackgroundColor: '#4285f4',
          order: 1,
          fill: false
        },
        {
          type: 'line',
          label: 'Net Income',
          data: this.filteredResults.map(row => {
            const gross = parseFloat(row.gross_income) || 0;
            const tax = parseFloat(row.federal_tax) || 0;
            const medicare = parseFloat(row.total_medicare) || 0;
            return gross - tax - medicare;
          }),
          borderColor: '#34a853',
          backgroundColor: 'transparent',
          borderWidth: 3,
          tension: 0.3,
          yAxisID: 'y',
          pointRadius: 3,
          pointBackgroundColor: '#34a853',
          order: 1,
          fill: false
        },
        {
          type: 'bar',
          label: 'Federal Tax',
          data: this.filteredResults.map(row => parseFloat(row.federal_tax) || 0),
          backgroundColor: '#ea4335',
          stack: 'Stack 0',
          yAxisID: 'y',
          order: 2
        },
        {
          type: 'bar',
          label: 'Medicare',
          data: this.filteredResults.map(row => parseFloat(row.total_medicare) || 0),
          backgroundColor: '#fbbc05',
          stack: 'Stack 0',
          yAxisID: 'y',
          order: 2
        }
      ];

      console.log('✅ FinancialOverview chartData computed successfully:', { labels, datasets });
      return { labels, datasets };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Year'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Amount ($)'
            },
            ticks: {
              beginAtZero: true,
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            position: 'bottom'
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        }
      };
    }
  },
  watch: {
    filteredResults: {
      handler(newResults) {
        // Use nextTick to ensure DOM is ready
        this.$nextTick(() => {
          this.renderFlowChart(newResults);
          this.initializeCircles();
        });
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    renderFlowChart(results) {
      if (!results || results.length === 0) return;

      // Clear previous chart
      d3.select('#financialFlowChart').selectAll('*').remove();

      // Calculate totals for the flow
      const totalGrossIncome = results.reduce((sum, row) => sum + parseFloat(row.gross_income || 0), 0);
      const totalFederalTax = results.reduce((sum, row) => sum + parseFloat(row.federal_tax || 0), 0);
      const totalMedicare = results.reduce((sum, row) => sum + parseFloat(row.total_medicare || 0), 0);
      
      // Estimate IRMAA as a portion of Medicare (for demonstration)
      const estimatedIRMAA = totalMedicare * 0.3; // Assume 30% of Medicare is IRMAA
      const regularMedicare = totalMedicare - estimatedIRMAA;
      
      // Calculate other expenses (we'll estimate this as remaining amount after basic expenses)
      const basicExpenses = totalFederalTax + totalMedicare;
      const netIncome = totalGrossIncome - basicExpenses;
      const otherExpenses = Math.max(0, netIncome * 0.6); // Assume 60% of net goes to other expenses
      const finalNetIncome = netIncome - otherExpenses;

      // Create D3 Sankey data structure
      const data = {
        nodes: [
          { id: 0, name: 'Total Income' },
          { id: 1, name: 'Taxable Income' },
          { id: 2, name: 'Federal Tax' },
          { id: 3, name: 'Medicare' },
          { id: 4, name: 'IRMAA' },
          { id: 5, name: 'Other Expenses' },
          { id: 6, name: 'Net Income' }
        ],
        links: [
          { source: 0, target: 1, value: totalGrossIncome },
          { source: 1, target: 2, value: totalFederalTax },
          { source: 1, target: 3, value: regularMedicare },
          { source: 1, target: 4, value: estimatedIRMAA },
          { source: 1, target: 5, value: otherExpenses },
          { source: 1, target: 6, value: finalNetIncome }
        ]
      };

      // Set up SVG dimensions
      const container = document.querySelector('.flow-chart-container');
      const width = container.clientWidth;
      const height = 400;

      const svg = d3.select('#financialFlowChart')
        .attr('width', width)
        .attr('height', height);

      // Create sankey generator
      const sankeyGenerator = sankey()
        .nodeWidth(15)
        .nodePadding(10)
        .extent([[1, 1], [width - 1, height - 5]]);

      // Generate the sankey layout
      const { nodes, links } = sankeyGenerator(data);

      // Color mapping
      const colorMap = {
        'Total Income': '#4285f4',
        'Taxable Income': '#4285f4',
        'Federal Tax': '#ea4335',
        'Medicare': '#fbbc05',
        'IRMAA': '#ff6d01',
        'Other Expenses': '#9aa0a6',
        'Net Income': '#34a853'
      };

      // Draw links
      svg.append('g')
        .selectAll('.link')
        .data(links)
        .join('path')
        .attr('class', 'link')
        .attr('d', sankeyLinkHorizontal())
        .attr('stroke', d => colorMap[d.target.name] || '#ccc')
        .attr('stroke-width', d => Math.max(1, d.width))
        .attr('fill', 'none')
        .attr('opacity', 0.7)
        .append('title')
        .text(d => `${d.source.name} → ${d.target.name}\n${this.formatCurrency(d.value)}`);

      // Draw nodes
      const node = svg.append('g')
        .selectAll('.node')
        .data(nodes)
        .join('g')
        .attr('class', 'node');

      node.append('rect')
        .attr('x', d => d.x0)
        .attr('y', d => d.y0)
        .attr('height', d => d.y1 - d.y0)
        .attr('width', d => d.x1 - d.x0)
        .attr('fill', d => colorMap[d.name] || '#ccc')
        .attr('stroke', '#000')
        .attr('stroke-width', 0.5);

      // Add labels
      node.append('text')
        .attr('x', d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
        .attr('y', d => (d.y1 + d.y0) / 2)
        .attr('dy', '0.35em')
        .attr('text-anchor', d => d.x0 < width / 2 ? 'start' : 'end')
        .style('font-size', '12px')
        .style('font-weight', 'bold')
        .text(d => d.name);

      // Add value labels
      node.append('text')
        .attr('x', d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
        .attr('y', d => (d.y1 + d.y0) / 2 + 15)
        .attr('dy', '0.35em')
        .attr('text-anchor', d => d.x0 < width / 2 ? 'start' : 'end')
        .style('font-size', '10px')
        .style('fill', '#666')
        .text(d => this.formatCurrency(d.value));

      // Add tooltips to nodes
      node.append('title')
        .text(d => `${d.name}\n${this.formatCurrency(d.value)}`);
    },
    exportFlowToPDF() {
      const svg = document.getElementById('financialFlowChart');
      if (svg) {
        // Convert SVG to canvas for PDF export
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const svgData = new XMLSerializer().serializeToString(svg);
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);
        
        const img = new Image();
        img.onload = () => {
          canvas.width = svg.clientWidth;
          canvas.height = svg.clientHeight;
          ctx.drawImage(img, 0, 0);
          
          const pdf = new jsPDF();
          const imgData = canvas.toDataURL('image/png');
          pdf.addImage(imgData, 'PNG', 10, 10, 190, 100);
          pdf.save('financial-flow-diagram.pdf');
          
          URL.revokeObjectURL(url);
        };
        img.src = url;
      }
    },
    toggleDropdown(tab) {
      this.isDropdownOpen[tab] = !this.isDropdownOpen[tab];
    },
    exportGraphAndDataToPDF() {
      // Implement PDF export logic
    },
    exportGraphAndDataToExcel() {
      // Implement Excel export logic
    },
    exportTableToCSV() {
      // Implement CSV export logic
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    },
    isIrmaaBracketHit(row, idx) {
      // Returns true if this row's MAGI crosses into a new IRMAA bracket compared to the previous row
      const magi = Number(row.magi);
      const thresholds = this.irmaaThresholds;
      if (idx === 0) {
        // First row: highlight if above first threshold
        return thresholds.some(t => magi >= t);
      }
      const prevMagi = Number(this.filteredResults[idx - 1]?.magi);
      // Find the bracket index for current and previous
      const getBracket = (m) => thresholds.findIndex(t => m < t);
      const currBracket = getBracket(magi);
      const prevBracket = getBracket(prevMagi);
      // If the bracket index decreases, we've crossed up into a new bracket
      return currBracket !== prevBracket;
    },
    getIrmaaBracketLabel(row) {
      const magi = Number(row.magi);
      const thresholds = this.irmaaThresholds;
      const labels = this.irmaaLabels;
      for (let i = 0; i < thresholds.length; i++) {
        if (magi <= thresholds[i]) {
          return labels[i];
        }
      }
      return labels[labels.length - 1];
    },
    toggleIrmaaTooltip(idx) {
      this.openIrmaaTooltipIdx = this.openIrmaaTooltipIdx === idx ? null : idx;
    },
    closeIrmaaTooltip() {
      this.openIrmaaTooltipIdx = null;
    },
    handleClickOutside(event) {
      if (!event.target.closest('.irmaa-info-icon') && !event.target.closest('.irmaa-popover')) {
        this.closeIrmaaTooltip();
      }
    },
    initializeCircles() {
      this.$nextTick(() => {
        const maxRetries = 20;
        let retryCount = 0;
        const tryInit = () => {
          const CirclesGlobal = window.Circles;
          if (CirclesGlobal && typeof CirclesGlobal.create === 'function') {
            const circleElement = document.getElementById('circle-financial');
            if (circleElement) {
              // Clear previous SVG if any
              circleElement.innerHTML = '';
              const total = this.totalGrossIncome;
              const tax = this.totalTax;
              const medicare = this.totalMedicare;
              const percent = total > 0 ? Math.round(((tax + medicare) / total) * 100) : 0;
              let circleColor = '#377dff';
              if (percent > 50) {
                circleColor = '#ff0000';
              } else if (percent > 25) {
                circleColor = '#ffa500';
              } else if (percent > 15) {
                circleColor = '#ffff00';
              } else {
                circleColor = '#00ff00';
              }
              CirclesGlobal.create({
                id: 'circle-financial',
                value: percent,
                maxValue: 100,
                width: 20,
                radius: 70,
                text: function(value) { return value + '%'; },
                colors: ['#f0f0f0', circleColor],
                duration: 400,
                wrpClass: 'circles-wrp',
                textClass: 'circles-text',
                styleWrapper: true,
                styleText: true
              });
            }
          } else if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(tryInit, 100);
          }
        };
        tryInit();
      });
    }
  },
  mounted() {
    this.initializeCircles();
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  watch: {
    scenarioResults: {
      handler() {
        this.$nextTick(() => {
          this.initializeCircles();
        });
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.irmaa-bracket-row {
  border-top: 2px solid #ff8000 !important;
}
.irmaa-info-icon {
  margin-left: 6px;
  cursor: pointer;
  font-size: 1em;
  vertical-align: middle;
}
.irmaa-popover {
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  background: #fff;
  border: 1px solid #aaa;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  padding: 6px 12px;
  z-index: 10;
  font-size: 0.95em;
  white-space: nowrap;
}
.financial-chart-container {
  width: 100%;
  height: 300px;
  min-height: 300px;
  max-height: 300px;
  position: relative;
}
#financialOverviewChart {
  width: 100% !important;
  height: 100% !important;
  min-height: 300px !important;
  max-height: 300px !important;
  display: block;
}
.circles-chart {
  min-height: 160px;
  min-width: 160px;
  width: 160px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.flow-chart-container {
  width: 100%;
  height: 400px;
  min-height: 400px;
  max-height: 400px;
  position: relative;
}

#financialFlowChart {
  width: 100% !important;
  height: 100% !important;
  min-height: 400px !important;
  max-height: 400px !important;
  display: block;
}
</style> 