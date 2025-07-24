<template>
  <div class="content container-fluid">
    <!-- Page Header -->
    <div class="page-header">
      <div class="row align-items-end">
        <div class="col-sm">
          <h1 class="page-header-title">Scenario Comparison Report</h1>
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb breadcrumb-no-gutter">
              <li class="breadcrumb-item"><a class="breadcrumb-link" href="#">Clients</a></li>
              <li class="breadcrumb-item"><a class="breadcrumb-link" href="#">{{ clientName }}</a></li>
              <li class="breadcrumb-item active" aria-current="page">Comparison Report</li>
            </ol>
          </nav>
        </div>
      </div>
    </div>
    <!-- End Page Header -->

    <!-- Comparison Table -->
    <div class="card">
      <div class="card-body">
        <div class="row">
          <!-- Column 1 -->
          <div class="col-md-4">
            <div class="mb-4">
              <select class="form-select" v-model="selectedScenario1" @change="loadScenarioData(1)">
                <option value="">Select Scenario</option>
                <option v-for="scenario in scenarios" :key="scenario.id" :value="scenario.id">
                  {{ scenario.name }}
                </option>
              </select>
            </div>
            
            <div v-if="scenarioData1" class="scenario-column">
              <h4 class="text-primary text-center mb-4">{{ scenarioData1.name }}</h4>
              
              <!-- IRMAA Status -->
              <div v-if="scenarioData1.irmaa_reached" class="alert alert-danger text-center mb-4">
                <strong>IRMAA REACHED</strong>
              </div>
              
              <!-- Financial Data -->
              <div class="comparison-row">
                <div class="comparison-label">Medicare</div>
                <div class="comparison-value">${{ formatNumber(scenarioData1.medicare_cost) }}</div>
              </div>
              
              <div class="comparison-row">
                <div class="comparison-label">Fed Taxes</div>
                <div class="comparison-value">${{ formatNumber(scenarioData1.federal_taxes) }}</div>
              </div>
              
              <div class="comparison-row">
                <div class="comparison-label">Solution Cost</div>
                <div class="comparison-value">${{ formatNumber(scenarioData1.solution_cost) }}</div>
              </div>
              
              <hr>
              
              <div class="comparison-row">
                <div class="comparison-label"><strong>Total Costs</strong></div>
                <div class="comparison-value"><strong>${{ formatNumber(scenarioData1.total_costs) }}</strong></div>
              </div>
              
              <div class="comparison-row mt-3">
                <div class="comparison-label">Out of Pocket</div>
                <div class="comparison-value text-danger"><strong>${{ formatNumber(scenarioData1.out_of_pocket) }}</strong></div>
              </div>
            </div>
          </div>
          
          <!-- Column 2 -->
          <div class="col-md-4">
            <div class="mb-4">
              <select class="form-select" v-model="selectedScenario2" @change="loadScenarioData(2)">
                <option value="">Select Scenario</option>
                <option v-for="scenario in scenarios" :key="scenario.id" :value="scenario.id">
                  {{ scenario.name }}
                </option>
              </select>
            </div>
            
            <div v-if="scenarioData2" class="scenario-column">
              <h4 class="text-primary text-center mb-4">{{ scenarioData2.name }}</h4>
              
              <!-- IRMAA Status -->
              <div v-if="scenarioData2.irmaa_reached" class="alert alert-danger text-center mb-4">
                <strong>IRMAA REACHED</strong>
              </div>
              
              <!-- Financial Data -->
              <div class="comparison-row">
                <div class="comparison-label">Medicare</div>
                <div class="comparison-value">${{ formatNumber(scenarioData2.medicare_cost) }}</div>
              </div>
              
              <div class="comparison-row">
                <div class="comparison-label">Fed Taxes</div>
                <div class="comparison-value">${{ formatNumber(scenarioData2.federal_taxes) }}</div>
              </div>
              
              <div class="comparison-row">
                <div class="comparison-label">Solution Cost</div>
                <div class="comparison-value">${{ formatNumber(scenarioData2.solution_cost) }}</div>
              </div>
              
              <hr>
              
              <div class="comparison-row">
                <div class="comparison-label"><strong>Total Costs</strong></div>
                <div class="comparison-value"><strong>${{ formatNumber(scenarioData2.total_costs) }}</strong></div>
              </div>
              
              <div class="comparison-row mt-3">
                <div class="comparison-label">Out of Pocket</div>
                <div class="comparison-value text-danger"><strong>${{ formatNumber(scenarioData2.out_of_pocket) }}</strong></div>
              </div>
            </div>
          </div>
          
          <!-- Column 3 -->
          <div class="col-md-4">
            <div class="mb-4">
              <select class="form-select" v-model="selectedScenario3" @change="loadScenarioData(3)">
                <option value="">Select Scenario</option>
                <option v-for="scenario in scenarios" :key="scenario.id" :value="scenario.id">
                  {{ scenario.name }}
                </option>
              </select>
            </div>
            
            <div v-if="scenarioData3" class="scenario-column">
              <h4 class="text-primary text-center mb-4">{{ scenarioData3.name }}</h4>
              
              <!-- IRMAA Status -->
              <div v-if="scenarioData3.irmaa_reached" class="alert alert-danger text-center mb-4">
                <strong>IRMAA REACHED</strong>
              </div>
              
              <!-- Financial Data -->
              <div class="comparison-row">
                <div class="comparison-label">Medicare</div>
                <div class="comparison-value">${{ formatNumber(scenarioData3.medicare_cost) }}</div>
              </div>
              
              <div class="comparison-row">
                <div class="comparison-label">Fed Taxes</div>
                <div class="comparison-value">${{ formatNumber(scenarioData3.federal_taxes) }}</div>
              </div>
              
              <div class="comparison-row">
                <div class="comparison-label">Solution Cost</div>
                <div class="comparison-value">${{ formatNumber(scenarioData3.solution_cost) }}</div>
              </div>
              
              <hr>
              
              <div class="comparison-row">
                <div class="comparison-label"><strong>Total Costs</strong></div>
                <div class="comparison-value"><strong>${{ formatNumber(scenarioData3.total_costs) }}</strong></div>
              </div>
              
              <div class="comparison-row mt-3">
                <div class="comparison-label">Out of Pocket</div>
                <div class="comparison-value text-danger"><strong>${{ formatNumber(scenarioData3.out_of_pocket) }}</strong></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- End Comparison Table -->
  </div>
</template>

<script>
export default {
  name: 'ComparisonReport',
  data() {
    return {
      clientId: null,
      clientName: '',
      scenarios: [],
      selectedScenario1: '',
      selectedScenario2: '',
      selectedScenario3: '',
      scenarioData1: null,
      scenarioData2: null,
      scenarioData3: null
    };
  },
  mounted() {
    this.clientId = this.$route.params.id;
    this.loadClientData();
  },
  methods: {
    async loadClientData() {
      const token = localStorage.getItem('token');
      if (!token) {
        this.$router.push('/login');
        return;
      }

      try {
        const response = await fetch(`http://localhost:8000/api/clients/${this.clientId}/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          this.clientName = `${data.first_name} ${data.last_name}`;
          this.scenarios = data.scenarios || [];
        }
      } catch (error) {
        console.error('Error loading client data:', error);
      }
    },

    async loadScenarioData(column) {
      const scenarioId = column === 1 ? this.selectedScenario1 : 
                        column === 2 ? this.selectedScenario2 : 
                        this.selectedScenario3;
      
      if (!scenarioId) return;

      const token = localStorage.getItem('token');
      
      try {
        const response = await fetch(`http://localhost:8000/api/scenarios/${scenarioId}/comparison-data/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          
          if (column === 1) {
            this.scenarioData1 = data;
          } else if (column === 2) {
            this.scenarioData2 = data;
          } else {
            this.scenarioData3 = data;
          }
        }
      } catch (error) {
        console.error('Error loading scenario data:', error);
      }
    },

    formatNumber(value) {
      if (!value) return '0.00';
      return parseFloat(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    }
  }
};
</script>

<style scoped>
.scenario-column {
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background-color: #f9fafb;
}

.comparison-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e5e7eb;
}

.comparison-row:last-child {
  border-bottom: none;
}

.comparison-label {
  font-size: 14px;
  color: #374151;
}

.comparison-value {
  font-size: 16px;
  font-weight: 500;
  color: #111827;
  text-align: right;
}

.alert-danger {
  background-color: #ef4444;
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-weight: bold;
}
</style>