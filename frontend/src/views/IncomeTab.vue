<template>
  <div>
    <!-- Comprehensive Financial Table -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="mb-0">Income Analysis</h5>
          <button
            @click="exportToCSV"
            class="btn btn-sm btn-outline-secondary">
            <i class="bi bi-download me-1"></i>
            Export CSV
          </button>
        </div>
        <ComprehensiveFinancialTable
          :scenario-id="scenario.id"
          :client="client"
        />
      </div>
    </div>

    <!-- Original Income Projection Table (Hidden) -->
    <div v-if="false" class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Income Projection Table</h5>

        <!-- Loading state for table -->
        <div v-if="!incomeProjectionTable || incomeProjectionTable.length === 0" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading income data...</span>
          </div>
          <p class="mt-2 text-muted">Loading income projections...</p>
        </div>

        <!-- Table content -->
        <div v-else class="table-responsive" style="overflow-x: auto; max-width: 100%;">
          <table class="table table-hover table-sm" style="min-width: 800px;">
            <thead class="thead-light">
              <tr>
                <th :style="`position: sticky; left: ${stickyPositions.year.left}; background-color: #f8f9fa; z-index: 10; min-width: ${stickyPositions.year.width};`">Year</th>
                <th :style="`position: sticky; left: ${stickyPositions.primaryAge.left}; background-color: #f8f9fa; z-index: 10; min-width: ${stickyPositions.primaryAge.width};`">{{ client?.first_name || 'Primary' }} Age</th>
                <th v-if="client?.tax_status && client?.tax_status.toLowerCase() !== 'single'" :style="`position: sticky; left: ${stickyPositions.spouseAge.left}; background-color: #f8f9fa; z-index: 10; min-width: ${stickyPositions.spouseAge.width};`">{{ client?.spouse?.first_name || 'Spouse' }} Age</th>
                <th v-for="asset in assetDetails" :key="'header-' + asset.id">
                  <div class="d-flex align-items-center justify-content-center">
                    <span>{{ formatAssetColumnHeader(asset) }}</span>
                    <button
                      @click="showAssetModal(asset)"
                      class="btn btn-link btn-sm p-0 ms-1"
                      style="text-decoration: none;"
                      title="View graph and details">
                      <i class="bi bi-graph-up"></i>
                    </button>
                  </div>
                </th>
                <th v-if="hasQualifiedAssets">401k Balance</th>
                <th style="position: sticky; right: 0; background-color: #f8f9fa; z-index: 10; min-width: 120px;">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in incomeProjectionTable" :key="row.year">
                <td :style="`position: sticky; left: ${stickyPositions.year.left}; background-color: white; z-index: 5; min-width: ${stickyPositions.year.width};`">{{ row.year }}</td>
                <td :style="`position: sticky; left: ${stickyPositions.primaryAge.left}; background-color: white; z-index: 5; min-width: ${stickyPositions.primaryAge.width};`">{{ row.primaryAge || '-' }}</td>
                <td v-if="client?.tax_status && client?.tax_status.toLowerCase() !== 'single'" :style="`position: sticky; left: ${stickyPositions.spouseAge.left}; background-color: white; z-index: 5; min-width: ${stickyPositions.spouseAge.width};`">{{ row.spouseAge || '-' }}</td>
                <td v-for="asset in assetDetails" :key="'data-' + asset.id + '-' + row.year">
                  {{ formatCurrency(row.incomes[asset.id] || 0) }}
                </td>
                <td v-if="hasQualifiedAssets">{{ formatCurrency(row.qualifiedBalance || 0) }}</td>
                <td style="position: sticky; right: 0; background-color: #f8f9fa; z-index: 5; min-width: 120px; font-weight: 600;">{{ formatCurrency(row.total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Asset Detail Modal -->
    <div v-if="showAssetDetailModal" class="modal fade show" tabindex="-1" style="display:block; background:rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" style="text-transform: capitalize;">
              {{ selectedAsset?.income_type.replace(/_/g, ' ') }} Details
            </h5>
            <button type="button" class="btn-close" @click="closeAssetModal"></button>
          </div>
          <div class="modal-body">
            <!-- Asset Details Table -->
            <div class="mb-4">
              <h6 class="mb-3">Asset Information</h6>
              
              <!-- Table for Social Security -->
              <table v-if="getAssetType(selectedAsset) === 'social_security'" class="table table-hover mb-3">
                <thead class="thead-light">
                  <tr>
                    <th>Owner</th>
                    <th>Amount at FRA</th>
                    <th>Start Age</th>
                    <th>COLA %</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{{ selectedAsset.owned_by }}</td>
                    <td>${{ parseFloat(selectedAsset.monthly_amount || 0).toLocaleString() }}</td>
                    <td>{{ selectedAsset.age_to_begin_withdrawal }}</td>
                    <td>{{ selectedAsset.cola }}%</td>
                  </tr>
                </tbody>
              </table>
              
              <!-- Table for Pension -->
              <table v-else-if="getAssetType(selectedAsset) === 'pension'" class="table table-hover mb-3">
                <thead class="thead-light">
                  <tr>
                    <th>Owner</th>
                    <th>Monthly Income</th>
                    <th>COLA %</th>
                    <th>Start Age</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{{ selectedAsset.owned_by }}</td>
                    <td>${{ parseFloat(selectedAsset.monthly_amount || 0).toLocaleString() }}</td>
                    <td>{{ selectedAsset.cola }}%</td>
                    <td>{{ selectedAsset.age_to_begin_withdrawal }}</td>
                  </tr>
                </tbody>
              </table>
              
              <!-- Table for Qualified/Non-Qualified Assets -->
              <table v-else-if="['qualified', 'non_qualified'].includes(getAssetType(selectedAsset))" class="table table-hover mb-3">
                <thead class="thead-light">
                  <tr>
                    <th>Owner</th>
                    <th>Asset Type</th>
                    <th>Starting Balance</th>
                    <th>Monthly Contribution</th>
                    <th>Growth Rate</th>
                    <th>Withdrawal Start</th>
                    <th>Withdrawal End</th>
                    <th>Monthly Withdrawal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{{ selectedAsset.owned_by }}</td>
                    <td>{{ selectedAsset.income_type }}</td>
                    <td>${{ parseFloat(selectedAsset.current_asset_balance || 0).toLocaleString() }}</td>
                    <td>${{ parseFloat(selectedAsset.monthly_contribution || 0).toLocaleString() }}</td>
                    <td>{{ (parseFloat(selectedAsset.rate_of_return || selectedAsset.growth_rate || 0) * 100).toFixed(2) }}%</td>
                    <td>{{ selectedAsset.age_to_begin_withdrawal }}</td>
                    <td>{{ selectedAsset.age_to_end_withdrawal }}</td>
                    <td>${{ parseFloat(selectedAsset.monthly_amount || 0).toLocaleString() }}</td>
                  </tr>
                </tbody>
              </table>
              
              <!-- Default table for other asset types -->
              <table v-else class="table table-hover mb-3">
                <thead class="thead-light">
                  <tr>
                    <th>Owner</th>
                    <th>Monthly Amount</th>
                    <th>Start Age</th>
                    <th>End Age</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{{ selectedAsset.owned_by }}</td>
                    <td>${{ parseFloat(selectedAsset.monthly_amount || 0).toLocaleString() }}</td>
                    <td>{{ selectedAsset.age_to_begin_withdrawal }}</td>
                    <td>{{ selectedAsset.age_to_end_withdrawal }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Asset Graph -->
            <div>
              <h6 class="mb-3">Projection Graph</h6>
              <div v-if="isLoadingGraph" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading graph data...</span>
                </div>
                <p class="mt-2 text-muted">Calculating projections...</p>
              </div>
              <div v-else-if="!selectedAsset" class="alert alert-info">No asset selected</div>
              <div v-else-if="!getGraphData(selectedAsset.income_type).labels" class="alert alert-warning">
                No graph data available for this asset
              </div>
              <Graph v-else :data="getGraphData(selectedAsset.income_type)" :height="300" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeAssetModal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Disclosures Card -->
    <DisclosuresCard />

  </div>
</template>

<script>
import Graph from '../components/Graph.vue';
import DisclosuresCard from '../components/DisclosuresCard.vue';
import ComprehensiveFinancialTable from '../components/ComprehensiveFinancialTable.vue';
import { useScenarioCalculationsStore } from '@/stores/scenarioCalculations';
import { useComprehensiveStore } from '@/stores/comprehensiveStore';

export default {
  components: {
    Graph,
    DisclosuresCard,
    ComprehensiveFinancialTable
  },
  props: {
    scenario: {
      type: Object,
      required: true
    },
    assetDetails: {
      type: Array,
      required: true
    },
    scenarioResults: {
      type: Array,
      required: true
    },
    client: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      preRetirementIncome: 0,
      availableYears: [],
      conversionStartYear: null,
      yearsToConvert: 0,
      rothGrowthRate: 0,
      // Modal state
      showAssetDetailModal: false,
      selectedAsset: null,
      isLoadingGraph: false
    };
  },
  mounted() {
    // Force a re-compute when store updates
    const store = useScenarioCalculationsStore();
    console.log('🔥 INCOME TAB MOUNTED');
    console.log('🔥 Props received:', {
      scenario: !!this.scenario,
      scenarioResults: this.scenarioResults?.length || 0,
      assetDetails: this.assetDetails?.length || 0,
      client: !!this.client
    });
    console.log('🔥 Asset Details:', this.assetDetails);
    console.log('🔥 Asset IDs from assetDetails:', this.assetDetails?.map(a => a.id));
    console.log('🔥 First scenario result:', this.scenarioResults?.[0]);
    console.log('🔥 First result asset_incomes:', this.scenarioResults?.[0]?.asset_incomes);
    console.log('🔥 Keys in first result:', this.scenarioResults?.[0] ? Object.keys(this.scenarioResults[0]) : 'No results');
    console.log('🔥 Store state:', {
      hasResults: store.enhancedResults.length > 0,
      hasAssets: store.assetDetails.length > 0
    });

    // Initialize store if we have all the data
    if (this.assetDetails && this.assetDetails.length > 0 &&
        this.scenarioResults && this.scenarioResults.length > 0) {
      console.log('🔥 Initializing store from IncomeTab mounted');
      store.initialize(
        this.scenarioResults,
        this.assetDetails,
        this.scenario,
        this.client
      );
    }
  },
  watch: {
    assetDetails: {
      handler(newVal) {
        console.log('🔥 INCOME TAB: assetDetails changed:', newVal?.length || 0, 'assets');
        if (newVal && newVal.length > 0 && this.scenarioResults && this.scenarioResults.length > 0) {
          const store = useScenarioCalculationsStore();
          console.log('🔥 INCOME TAB: Reinitializing store with new asset data');
          store.initialize(
            this.scenarioResults,
            this.assetDetails,
            this.scenario,
            this.client
          );
        }
      },
      immediate: true
    }
  },
  computed: {
    calculationsStore() {
      return useScenarioCalculationsStore();
    },
    hasQualifiedAssets() {
      return this.assetDetails.some(asset => {
        const type = this.getAssetType(asset);
        return type === 'qualified';
      });
    },
    stickyPositions() {
      // Calculate sticky positions based on whether spouse column is shown
      const isMarried = this.client?.tax_status && this.client?.tax_status.toLowerCase() !== 'single';
      return {
        year: { left: '0px', width: '80px' },
        primaryAge: { left: '80px', width: '100px' },
        spouseAge: { left: '180px', width: '100px' },
        totalOffset: isMarried ? '280px' : '180px'
      };
    },
    incomeFields() {
      if (!this.scenarioResults || !this.scenarioResults.length) return [];

      const firstRow = this.scenarioResults[0];
      const knownKeys = [
        'year', 'primary_age', 'spouse_age', 'gross_income', 'taxable_income', 
        'federal_tax', 'total_medicare', 'remaining_ssi', 'social_security_benefit',
        'part_b', 'part_d', 'medicare_income'
      ];

      // List any field that seems to represent income but is not excluded
      return Object.keys(firstRow)
        .filter(key => key.includes('income') && !knownKeys.includes(key));
    },
    incomeProjectionTable() {
      // Use the central store's enhanced results
      const store = useScenarioCalculationsStore();
      const enhancedResults = store.enhancedResults;

      console.log('IncomeTab checking store:', {
        storeInitialized: !!store,
        enhancedResultsLength: enhancedResults?.length || 0,
        assetDetailsLength: store.assetDetails?.length || 0,
        scenarioResultsLength: this.scenarioResults?.length || 0
      });

      // If store has data, use it
      if (enhancedResults && enhancedResults.length > 0) {
        console.log('Using enhanced results from store:', enhancedResults.length);
        console.log('First row assetIncomes:', enhancedResults[0]?.assetIncomes);

        // Transform enhanced results into table format
        return enhancedResults.map(result => ({
          year: result.year,
          primaryAge: result.primary_age,
          spouseAge: result.spouse_age,
          incomes: result.assetIncomes || {},
          qualifiedBalance: result.qualified_balance || 0,
          total: parseFloat(result.gross_income || 0)
        }));
      }

      // If store not ready but we have scenario results, try to initialize store
      if (this.scenarioResults && this.scenarioResults.length > 0 && this.assetDetails && this.assetDetails.length > 0) {
        console.log('Store not ready, attempting initialization with local data');
        console.log('🔥 Client prop:', this.client);
        console.log('🔥 Scenario.client:', this.scenario?.client);
        console.log('🔥 Using client:', this.client);

        store.initialize(
          this.scenarioResults,
          this.assetDetails,
          this.scenario,
          this.client  // Use the client prop directly
        );

        // After initialization, try to get enhanced results again
        const newEnhancedResults = store.enhancedResults;
        if (newEnhancedResults && newEnhancedResults.length > 0) {
          console.log('Store initialized successfully, using enhanced results');
          return newEnhancedResults.map(result => ({
            year: result.year,
            primaryAge: result.primary_age,
            spouseAge: result.spouse_age,
            incomes: result.assetIncomes || {},
            qualifiedBalance: result.qualified_balance || 0,
            total: parseFloat(result.gross_income || 0)
          }));
        }
      }

      // Ultimate fallback - just show totals
      if (this.scenarioResults && this.scenarioResults.length > 0) {
        console.log('Store initialization failed, using basic scenario results');
        return this.scenarioResults.map(result => ({
          year: result.year,
          primaryAge: result.primary_age,
          spouseAge: result.spouse_age,
          incomes: {},
          qualifiedBalance: result.qualified_balance || 0,
          total: parseFloat(result.gross_income || 0)
        }));
      }

      return [];
      
      
      // Get client ages - handle invalid dates
      const currentYear = new Date().getFullYear();
      let clientBirthYear = null;
      let spouseBirthYear = null;
      let currentClientAge = null;
      let currentSpouseAge = null;
      
      if (this.scenario.client?.birthdate) {
        const birthDate = new Date(this.scenario.client.birthdate);
        if (!isNaN(birthDate.getTime())) {
          clientBirthYear = birthDate.getFullYear();
          currentClientAge = currentYear - clientBirthYear;
        }
      }
      
      if (this.scenario.client?.spouse?.birthdate) {
        const spouseBirthDate = new Date(this.scenario.client.spouse.birthdate);
        if (!isNaN(spouseBirthDate.getTime())) {
          spouseBirthYear = spouseBirthDate.getFullYear();
          currentSpouseAge = currentYear - spouseBirthYear;
        }
      }
      
      // If we can't determine ages, use defaults
      if (currentClientAge === null) {
        console.warn('Could not determine client age from birthdate, using default age 50');
        currentClientAge = 50;
      }
      
      // Get scenario parameters
      const primaryRetirementAge = this.scenario.primary_retirement_age || 65;
      const spouseRetirementAge = this.scenario.spouse_retirement_age || 65;
      const mortalityAge = this.scenario.mortality_age || 90;
      const spouseMortalityAge = this.scenario.spouse_mortality_age || 90;
      
      // Calculate the starting year and ending year for the table
      let startYear, endYear;
      
      if (currentSpouseAge !== null) {
        // Married - use earliest retirement and latest mortality
        const primaryRetirementYear = currentYear + (primaryRetirementAge - currentClientAge);
        const spouseRetirementYear = currentYear + (spouseRetirementAge - currentSpouseAge);
        startYear = Math.min(primaryRetirementYear, spouseRetirementYear);
        
        const primaryMortalityYear = currentYear + (mortalityAge - currentClientAge);
        const spouseMortalityYear = currentYear + (spouseMortalityAge - currentSpouseAge);
        endYear = Math.max(primaryMortalityYear, spouseMortalityYear);
      } else {
        // Single - use primary's retirement and mortality years
        startYear = currentYear + (primaryRetirementAge - currentClientAge);
        endYear = currentYear + (mortalityAge - currentClientAge);
      }
      
      // Generate rows from earliest retirement year to latest mortality year
      for (let year = startYear; year <= endYear; year++) {
        const yearsFromNow = year - currentYear;
        const primaryAge = currentClientAge + yearsFromNow;
        const spouseAge = currentSpouseAge !== null ? currentSpouseAge + yearsFromNow : null;
        
        // Only show age if person is still alive
        const primaryAgeDisplay = primaryAge <= mortalityAge ? primaryAge : null;
        const spouseAgeDisplay = (spouseAge !== null && spouseAge <= spouseMortalityAge) ? spouseAge : null;
        
        const row = {
          year: year,
          primaryAge: primaryAgeDisplay,
          spouseAge: spouseAgeDisplay,
          incomes: {},
          total: 0
        };
        
        // Calculate income for each asset
        this.assetDetails.forEach(asset => {
          const income = this.calculateAssetIncomeForYear(asset, primaryAge, primaryAgeDisplay, spouseAgeDisplay);
          row.incomes[asset.id] = income;
          row.total += income;
        });
        
        projections.push(row);
      }
      
      return projections;
    }
  },
  methods: {
    getAssetIncome(result, assetId) {
      // Get income for a specific asset from the result's asset_incomes
      if (!result.asset_incomes) {
        console.warn(`No asset_incomes in result for year ${result.year}`);
        return 0;
      }

      // Debug: Log what we're looking for and what we have
      const income = result.asset_incomes[assetId] || result.asset_incomes[String(assetId)] || 0;
      if (income > 0) {
        console.log(`Year ${result.year}, Asset ${assetId}: Found income ${income}`);
      }

      return income;
    },

    getAssetBalance(result, asset) {
      // Get the balance for an investment asset
      // The backend tracks individual asset balances in asset_incomes
      // For investment accounts, we need to look at specific balance tracking

      // Check if this is an investment type asset
      if (!this.isInvestmentAsset(asset)) return 0;

      // Look for asset-specific balance in the result
      // The backend should be tracking this per asset
      const assetType = (asset.income_type || '').toLowerCase().replace(/\s+/g, '_');
      const balanceKey = `${assetType}_balance_${asset.id}`;

      if (result[balanceKey] !== undefined) {
        return result[balanceKey];
      }

      // For now, return the qualified_balance if it's a qualified asset
      // This will be improved when backend tracks per-asset balances
      if (this.isQualifiedAsset(asset)) {
        return result.qualified_balance || 0;
      }

      return 0;
    },

    isInvestmentAsset(asset) {
      // Check if an asset is any type of investment account
      const investmentTypes = [
        'qualified',
        'non-qualified',
        'roth',
        'inherited traditional spouse',
        'inherited roth spouse',
        'inherited traditional non-spouse',
        'inherited roth non-spouse'
      ];

      const type = (asset.income_type || '').toLowerCase();
      return investmentTypes.includes(type);
    },

    isQualifiedAsset(asset) {
      // Check if an asset is a qualified (tax-deferred) retirement account
      // These are subject to RMDs at age 73 (or 75 for those born after 1959)
      const type = (asset.income_type || '').toLowerCase();
      return type === 'qualified' ||
             type === 'inherited traditional spouse' ||
             type === 'inherited traditional non-spouse';
    },

    isRothAsset(asset) {
      // Check if an asset is a Roth account (no RMDs during owner's lifetime)
      const type = (asset.income_type || '').toLowerCase();
      return type === 'roth' ||
             type === 'inherited roth spouse' ||
             type === 'inherited roth non-spouse';
    },

    isInheritedAsset(asset) {
      // Check if an asset is inherited (has special RMD rules)
      const type = (asset.income_type || '').toLowerCase();
      return type.includes('inherited');
    },

    getRMDStartAge(asset) {
      // Get the RMD start age based on asset type and IRS rules
      const type = (asset.income_type || '').toLowerCase();

      // Inherited non-spouse accounts must start RMDs immediately
      if (type.includes('inherited') && type.includes('non-spouse')) {
        return asset.age_to_begin_withdrawal || 0; // Start immediately
      }

      // Inherited spouse accounts have more flexibility
      if (type.includes('inherited') && type.includes('spouse')) {
        // Spouse can treat as own, so use regular RMD rules
        return 73; // SECURE Act 2.0 rules
      }

      // Regular qualified accounts - RMD starts at 73 (or 75 for younger people)
      if (this.isQualifiedAsset(asset)) {
        // Could check birth year here for 73 vs 75 rule
        return 73;
      }

      // Roth accounts - no RMDs during owner's lifetime
      if (type === 'roth') {
        return 999; // Effectively never
      }

      // Inherited Roth accounts do have RMDs
      if (type.includes('inherited') && type.includes('roth')) {
        return asset.age_to_begin_withdrawal || 0;
      }

      return null;
    },

    getAssetTooltip(asset) {
      // Generate detailed tooltip text for asset column headers
      const type = this.getAssetType(asset);
      let tooltip = `Type: ${asset.income_type}`;

      if (asset.owned_by) {
        tooltip += `\nOwner: ${asset.owned_by}`;
      }

      // Add RMD information for applicable assets
      const rmdAge = this.getRMDStartAge(asset);
      if (rmdAge && rmdAge < 999) {
        tooltip += `\nRMD Starts: Age ${rmdAge}`;
      }

      if (asset.age_to_begin_withdrawal) {
        tooltip += `\nWithdrawals Start: Age ${asset.age_to_begin_withdrawal}`;
      }

      if (asset.age_to_end_withdrawal) {
        tooltip += `\nWithdrawals End: Age ${asset.age_to_end_withdrawal}`;
      }

      if (asset.monthly_amount) {
        tooltip += `\nMonthly Withdrawal: $${parseFloat(asset.monthly_amount).toLocaleString()}`;
      }

      if (asset.current_asset_balance) {
        tooltip += `\nStarting Balance: $${parseFloat(asset.current_asset_balance).toLocaleString()}`;
      }

      if (asset.rate_of_return) {
        tooltip += `\nGrowth Rate: ${(parseFloat(asset.rate_of_return) * 100).toFixed(2)}%`;
      }

      return tooltip;
    },

    /**
     * SINGLE SOURCE OF TRUTH for asset calculations
     * This calculates the COMPLETE projection for an asset from current age to end age
     * Returns a dictionary with withdrawal amounts for each age
     */
    calculateAssetProjection(asset) {
      // Get client's actual current age
      const birthYear = new Date(this.client?.birthdate).getFullYear();
      const currentYear = new Date().getFullYear();
      const actualCurrentAge = currentYear - birthYear;

      // Get scenario parameters
      const endAge = this.scenario?.mortality_age || 90;
      const growthRate = parseFloat(asset.rate_of_return || asset.growth_rate || 0);
      const withdrawalStartAge = parseInt(asset.age_to_begin_withdrawal || 65);
      const withdrawalEndAge = parseInt(asset.age_to_end_withdrawal || endAge);
      const monthlyContribution = parseFloat(asset.monthly_contribution || 0);
      const annualContribution = monthlyContribution * 12;
      const specifiedAnnualWithdrawal = parseFloat(asset.monthly_amount || 0) * 12;

      // RMD table from IRS
      const rmdTable = {
        72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0,
        79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0,
        86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8,
        93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4,
        101: 6.0, 102: 5.6, 103: 5.2, 104: 4.9, 105: 4.5, 106: 4.2, 107: 3.9,
        108: 3.7, 109: 3.4, 110: 3.1, 111: 2.9, 112: 2.6, 113: 2.4, 114: 2.1, 115: 1.9
      };

      const normalizedType = this.getAssetType(asset);
      const projection = {};
      let currentBalance = parseFloat(asset.current_asset_balance || 0);

      // Calculate for each year from current age to end age
      for (let age = actualCurrentAge; age <= endAge; age++) {
        let withdrawal = 0;

        if (age < withdrawalStartAge) {
          // Pre-retirement: contributions and growth only
          currentBalance += annualContribution;
          currentBalance *= (1 + growthRate);
        } else if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
          // Retirement phase: calculate withdrawals

          // Calculate RMD if applicable (qualified accounts at age 73+)
          if (normalizedType === 'qualified' && age >= 73 && currentBalance > 0) {
            const divisor = rmdTable[age] || (age > 115 ? 1.9 : 10);
            const rmdAmount = currentBalance / divisor;
            withdrawal = Math.max(rmdAmount, specifiedAnnualWithdrawal);
          } else {
            withdrawal = specifiedAnnualWithdrawal;
          }

          // Don't withdraw more than available
          if (withdrawal > currentBalance) {
            withdrawal = currentBalance;
          }

          // Subtract withdrawal, then apply growth
          currentBalance -= withdrawal;
          currentBalance *= (1 + growthRate);
        }

        projection[age] = {
          withdrawal: withdrawal,
          balance: currentBalance
        };
      }

      return projection;
    },
    generateTableFromScenarioResults() {
      // Generate income table using accurate backend scenario results
      const projections = [];

      // Pre-calculate projections for all qualified/non-qualified assets
      const assetProjections = {};
      this.assetDetails.forEach(asset => {
        const normalizedType = this.getAssetType(asset);
        if (normalizedType === 'qualified' || normalizedType === 'non_qualified') {
          assetProjections[asset.id] = this.calculateAssetProjection(asset);
        }
      });

      // Process each year from scenario results
      this.scenarioResults.forEach(result => {
        const row = {
          year: result.year,
          primaryAge: result.primary_age,
          spouseAge: result.spouse_age,
          incomes: {},
          qualifiedBalance: result.qualified_balance || 0,
          total: result.total || result.gross_income || 0  // USE BACKEND'S TOTAL - NO CALCULATIONS
        };
        
        
        // Use backend's asset_incomes if available, otherwise fall back to calculations
        if (result.asset_incomes && Object.keys(result.asset_incomes).length > 0) {
          // Backend provides individual asset incomes - use them directly
          console.log('Backend asset_incomes for year', result.year, ':', result.asset_incomes);
          console.log('Asset details IDs:', this.assetDetails.map(a => ({id: a.id, name: a.income_name})));

          this.assetDetails.forEach(asset => {
            // Try both string and number keys since JSON may convert IDs
            const income = result.asset_incomes[asset.id] || result.asset_incomes[String(asset.id)] || 0;
            row.incomes[asset.id] = income;
            // DON'T CALCULATE TOTAL - USE BACKEND'S TOTAL
          });
        } else {
          // Fallback: Map the backend results to our assets (for backwards compatibility)
          this.assetDetails.forEach(asset => {
            let income = 0;
            const normalizedType = this.getAssetType(asset);
            const owner = asset.owned_by?.toLowerCase();

            // Map backend results to frontend assets
            if (normalizedType === 'social_security') {
              if (owner === 'primary') {
                income = parseFloat(result.ss_income_primary || 0);
              } else if (owner === 'spouse' || owner === 'secondary') {
                income = parseFloat(result.ss_income_spouse || 0);
              }

            } else if ((normalizedType === 'qualified' || normalizedType === 'non_qualified') && assetProjections[asset.id]) {
              // Use the pre-calculated projection for this asset
              const relevantAge = owner === 'spouse' ? result.spouse_age : result.primary_age;
              const projection = assetProjections[asset.id][relevantAge];
              income = projection ? projection.withdrawal : 0;

            } else {
              // For other asset types, use the calculated method
              const primaryAgeDisplay = result.primary_age;
              const spouseAgeDisplay = result.spouse_age;
              income = this.calculateAssetIncomeForYear(asset, result.primary_age, primaryAgeDisplay, spouseAgeDisplay);
            }

            row.incomes[asset.id] = income;
            // DON'T CALCULATE TOTAL - USE BACKEND'S TOTAL
          });
        }
        
        projections.push(row);
      });
      
      return projections;
    },
    getAssetType(asset) {
      // Normalize asset type for consistent comparison
      const type = (asset.income_type || '').toLowerCase().trim();
      
      // Map various social security formats
      if (type === 'social_security' || type === 'social security' || type === 'socialsecurity') {
        return 'social_security';
      }
      // Map pension formats
      if (type === 'pension' || type === 'pensions') {
        return 'pension';
      }
      // Map annuity formats
      if (type === 'annuity' || type === 'annuities') {
        return 'annuity';
      }
      // Map rental income formats
      if (type === 'rental_income' || type === 'rental income' || type === 'rentalincome' || type === 'rental') {
        return 'rental_income';
      }
      // Map wages formats
      if (type === 'wages' || type === 'wage' || type === 'salary' || type === 'salaries') {
        return 'wages';
      }
      // Map reverse mortgage formats
      if (type === 'reverse_mortgage' || type === 'reverse mortgage' || type === 'reversemortgage') {
        return 'reverse_mortgage';
      }
      // Map qualified assets
      if (type === 'qualified' || type === 'qualified_asset') {
        return 'qualified';
      }
      // Map non-qualified assets
      if (type === 'non-qualified' || type === 'non_qualified' || type === 'nonqualified') {
        return 'non_qualified';
      }
      
      // Return normalized type or original if no match
      return type;
    },
    getGraphData(incomeType) {
      // Find the asset for this incomeType
      const asset = this.assetDetails.find(a => a.income_type === incomeType);
      if (!asset) return {};
      
      // Get client's actual current age from birthdate
      const birthYear = new Date(this.client?.birthdate).getFullYear();
      const currentYear = new Date().getFullYear();
      let actualCurrentAge = currentYear - birthYear;

      console.log(`Client birthdate: ${this.client?.birthdate}, Birth year: ${birthYear}, Current age: ${actualCurrentAge}`);
      
      // If we couldn't get the birthdate, use a fallback
      if (!birthYear || isNaN(actualCurrentAge)) {
        actualCurrentAge = 50; // Fallback value based on common scenario
        console.warn('Could not determine client age from birthdate, using fallback age:', actualCurrentAge);
      }
      
      // Get scenario ages
      const endAge = this.scenario?.mortality_age || 90;
      const retirementAge = this.scenario?.retirement_age || 65;
      const rmdStartAge = 73; // SECURE Act 2.0 default
      
      // Asset fields
      const startBalance = parseFloat(asset.current_asset_balance || 0);
      const monthlyContribution = parseFloat(asset.monthly_contribution || 0);
      const annualContribution = monthlyContribution * 12;
      const growthRate = parseFloat(asset.rate_of_return || asset.growth_rate || 0);
      const withdrawalStartAge = parseInt(asset.age_to_begin_withdrawal || retirementAge);
      const withdrawalEndAge = parseInt(asset.age_to_end_withdrawal || endAge);
      const annualWithdrawal = parseFloat(asset.monthly_amount || 0) * 12;
      
      // Get normalized income type for comparison
      const normalizedType = this.getAssetType(asset);

      // Qualified/Non-Qualified: handle investment accounts with balances
      if (normalizedType === 'qualified' || normalizedType === 'non_qualified') {
        console.log('📊 getGraphData: Creating graph for qualified asset', asset.id);

        // Use the SAME unified calculation method
        const projection = this.calculateAssetProjection(asset);
        console.log('📊 getGraphData: Projection calculated, keys:', Object.keys(projection).length);

        const labels = [];
        const withdrawals = [];
        const balances = [];

        // Extract data from projection for graph
        for (let age = actualCurrentAge; age <= endAge; age++) {
          if (projection[age]) {
            labels.push(age);
            withdrawals.push(projection[age].withdrawal);
            balances.push(projection[age].balance);
          }
        }

        console.log('📊 getGraphData: Graph data built:', {
          labelsCount: labels.length,
          firstLabels: labels.slice(0, 5),
          firstWithdrawals: withdrawals.slice(0, 5),
          firstBalances: balances.slice(0, 5)
        });

        return {
          labels,
          datasets: [
            {
              label: 'Balance',
              data: balances,
              borderColor: 'green',
              backgroundColor: 'rgba(0, 128, 0, 0.1)',
              borderWidth: 2,
              fill: false,
              tension: 0.3,
              yAxisID: 'y',
              order: 1
            },
            {
              label: 'Withdrawals',
              data: withdrawals,
              borderColor: 'red',
              backgroundColor: 'rgba(255, 0, 0, 0.1)',
              borderWidth: 2,
              fill: false,
              tension: 0.3,
              yAxisID: 'y',
              order: 2
            }
          ]
        };
      } else if (normalizedType === 'qualified__OLD' || normalizedType === 'non_qualified__OLD' || startBalance > 0) {
        console.log(`Retirement account data:`, {
          type: asset.income_type,
          currentAge: actualCurrentAge,
          retirementAge: withdrawalStartAge,
          startBalance,
          monthlyContribution,
          growthRate: growthRate * 100 + '%'
        });
        
        // Calculate the actual projection
        const balances = [];
        const withdrawals = [];
        const contributions = [];
        const labels = [];
        
        // Start with the current balance at current age
        let currentBalance = startBalance;
        
        // Generate data points for each year from current age to end age
        for (let age = actualCurrentAge; age <= endAge; age++) {
          labels.push(age);
          
          // Debugging
          if (age === actualCurrentAge) {
            console.log(`Initial balance at age ${age}: $${currentBalance.toFixed(2)}`);
          }
          
          // Pre-retirement phase: apply contributions and growth
          if (age < withdrawalStartAge) {
            // Add contribution for this year
            const yearlyContribution = annualContribution;
            contributions.push(yearlyContribution);
            
            // Apply contribution
            currentBalance += yearlyContribution;
            
            // Apply growth
            currentBalance *= (1 + growthRate);
            
            // Store balance and zero withdrawal
            balances.push(parseFloat(currentBalance.toFixed(2)));
            withdrawals.push(0);
            
            // Debug log at specific intervals
            if (age === actualCurrentAge || age === actualCurrentAge + 5 || age === withdrawalStartAge - 1) {
              console.log(`Age ${age}: Balance after contribution and growth: $${currentBalance.toFixed(2)}`);
            }
          } 
          // Retirement phase: apply withdrawals and growth
          else {
            // No more contributions
            contributions.push(0);
            
            // Calculate RMD if applicable (only for Qualified accounts)
            let rmd = 0;
            if (age >= rmdStartAge && normalizedType === 'qualified') {
              const rmdTable = {
                72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0,
                79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0,
                86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8,
                93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4,
                101: 6.0, 102: 5.6, 103: 5.2, 104: 4.9, 105: 4.5, 106: 4.2, 107: 3.9,
                108: 3.7, 109: 3.4, 110: 3.1, 111: 2.9, 112: 2.6, 113: 2.4, 114: 2.1, 115: 1.9
              };
              
              const divisor = rmdTable[age] || (age > 115 ? 1.9 : 27.4);
              rmd = currentBalance / divisor;
              
              if (age === rmdStartAge) {
                console.log(`Age ${age}: First RMD calculation: $${rmd.toFixed(2)} (balance: $${currentBalance.toFixed(2)}, divisor: ${divisor})`);
              }
            }
            
            // Calculate withdrawal amount (greater of specified withdrawal or RMD)
            let withdrawal = annualWithdrawal;
            if (rmd > withdrawal) {
              withdrawal = rmd;
            }
            
            // Don't withdraw more than available
            if (withdrawal > currentBalance) {
              withdrawal = currentBalance;
            }
            
            // Apply withdrawal
            currentBalance -= withdrawal;
            withdrawals.push(parseFloat(withdrawal.toFixed(2)));
            
            // Apply growth to remaining balance
            currentBalance *= (1 + growthRate);
            
            // Store balance
            balances.push(parseFloat(currentBalance.toFixed(2)));
            
            // Debug log at key points
            if (age === withdrawalStartAge || age === rmdStartAge || age === endAge) {
              console.log(`Age ${age}: Withdrawal: $${withdrawal.toFixed(2)}, Balance after withdrawal and growth: $${currentBalance.toFixed(2)}`);
            }
          }
        }
        
        // Log final dataset
        console.log(`Final projection generated: ${labels.length} data points from age ${actualCurrentAge} to ${endAge}`);
        console.log(`Balance at retirement age (${withdrawalStartAge}): $${balances[withdrawalStartAge - actualCurrentAge].toLocaleString()}`);
        
        return {
          labels,
          datasets: [
            {
              label: 'Balance',
              data: balances,
              borderColor: 'green',
              backgroundColor: 'rgba(0, 128, 0, 0.1)',
              fill: true
            },
            {
              label: 'Withdrawals',
              data: withdrawals,
              borderColor: 'red',
              backgroundColor: 'rgba(255, 0, 0, 0.1)',
              fill: true
            },
            {
              label: 'Contributions',
              data: contributions,
              borderColor: 'blue',
              backgroundColor: 'rgba(0, 0, 255, 0.1)',
              fill: true
            }
          ]
        };
      }
      // Social Security: payout graph only
      if (normalizedType === 'social_security') {
        const cola = parseFloat(asset.cola || 0) / 100;
        const payouts = [];
        const labels = [];
        
        // Monthly amount adjusted annually by COLA
        const monthlyAmount = parseFloat(asset.monthly_amount || 0);
        const annualAmount = monthlyAmount * 12;
        
        let payout = annualAmount;
        
        // Start from withdrawal start age (when SS benefits begin)
        const startAge = withdrawalStartAge;
        
        for (let age = startAge; age <= endAge; age++) {
          labels.push(age);
          
          // Check if we're in the eligible age range for benefits
          if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
            payouts.push(parseFloat(payout.toFixed(2)));
            
            // Apply COLA for next year
            payout *= (1 + cola);
          } else {
            payouts.push(0);
          }
        }
        
        return {
          labels,
          datasets: [
            {
              label: 'Social Security Benefits',
              data: payouts,
              borderColor: '#1877F2',
              backgroundColor: 'rgba(24, 119, 242, 0.1)',
              fill: true
            }
          ]
        };
      }
      // Other types: simple payout graph if monthly_amount is present
      if (annualWithdrawal > 0) {
        const payouts = [];
        const labels = [];
        
        // Start from withdrawal start age for income types (pensions, annuities, etc.)
        const startAge = withdrawalStartAge;
        
        for (let age = startAge; age <= endAge; age++) {
          labels.push(age);
          
          // Check if we're in the eligible age range for payouts
          if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
            // Apply COLA adjustment if applicable
            let yearlyPayout = annualWithdrawal;
            if (asset.cola) {
              const cola = parseFloat(asset.cola || 0) / 100;
              const yearsWithCola = age - withdrawalStartAge;
              yearlyPayout *= Math.pow(1 + cola, yearsWithCola);
            }
            
            payouts.push(parseFloat(yearlyPayout.toFixed(2)));
          } else {
            payouts.push(0);
          }
        }
        
        // Choose appropriate color based on income type
        let borderColor = '#8959A8'; // Default purple
        let backgroundColor = 'rgba(137, 89, 168, 0.1)';
        
        if (normalizedType === 'pension') {
          borderColor = '#5B8C5A'; // Green for pension
          backgroundColor = 'rgba(91, 140, 90, 0.1)';
        } else if (normalizedType === 'annuity') {
          borderColor = '#D89614'; // Gold for annuity
          backgroundColor = 'rgba(216, 150, 20, 0.1)';
        } else if (normalizedType === 'rental_income') {
          borderColor = '#E15759'; // Red for rental
          backgroundColor = 'rgba(225, 87, 89, 0.1)';
        }
        
        return {
          labels,
          datasets: [
            {
              label: `${asset.income_type.replace(/_/g, ' ')} Income`,
              data: payouts,
              borderColor: borderColor,
              backgroundColor: backgroundColor,
              fill: true
            }
          ]
        };
      }
      // Default: empty
      return {};
    },
    recalculateConversion() {
      // Implement recalculation logic
    },
    saveRothConversionScenario() {
      // Implement save logic
    },
    exportComparisonReport() {
      // Implement PDF export logic
    },
    exportToCSV() {
      // Use the comprehensive store to export data
      const comprehensiveStore = useComprehensiveStore();
      comprehensiveStore.exportToCSV(this.scenario.id);
    },
    getProjectedBalance(asset) {
      // Only calculate for retirement accounts
      if (!['Traditional_401k', 'Roth_401k', 'Traditional_IRA', 'Roth_IRA'].includes(asset.income_type)) {
        return null;
      }
      
      // Get the necessary data
      const startBalance = parseFloat(asset.current_asset_balance || 0);
      const monthlyContribution = parseFloat(asset.monthly_contribution || 0);
      const annualContribution = monthlyContribution * 12;
      const growthRate = parseFloat(asset.rate_of_return || asset.growth_rate || 0);
      const withdrawalStartAge = parseInt(asset.age_to_begin_withdrawal || 65);
      
      // Get the client's actual current age
      const birthYear = new Date(this.scenario?.client?.birthdate).getFullYear();
      if (!birthYear) return null;
      
      const currentYear = new Date().getFullYear();
      const actualCurrentAge = currentYear - birthYear;
      
      // Calculate years until retirement
      const yearsToRetirement = withdrawalStartAge - actualCurrentAge;
      if (yearsToRetirement <= 0) return startBalance; // Already at or past retirement
      
      // Calculate projected balance at retirement
      let projectedBalance = startBalance;
      for (let i = 0; i < yearsToRetirement; i++) {
        projectedBalance += annualContribution;
        projectedBalance *= (1 + growthRate);
      }
      
      return parseFloat(projectedBalance.toFixed(2));
    },
    calculateAssetIncomeForYear(asset, primaryAge, actualPrimaryAge, actualSpouseAge) {
      // Calculate the income from an asset for a specific year
      const normalizedType = this.getAssetType(asset);
      const startAge = parseInt(asset.age_to_begin_withdrawal || 65);
      const endAge = parseInt(asset.age_to_end_withdrawal || 90);
      
      // Determine which age to use based on owner
      let relevantAge = actualPrimaryAge;
      const ownerLower = (asset.owned_by || '').toLowerCase();
      if ((ownerLower === 'spouse' || ownerLower === 'secondary') && actualSpouseAge !== null) {
        relevantAge = actualSpouseAge;
      }
      
      
      // No income if person is deceased or outside age range
      if (!relevantAge || relevantAge < startAge || relevantAge > endAge) {
        return 0;
      }
      
      // For qualified/non-qualified assets, calculate withdrawals and RMDs
      if ((normalizedType === 'qualified' || normalizedType === 'non_qualified')) {
        const currentBalance = parseFloat(asset.current_asset_balance || 0);
        
        // For RMD calculation (age 73+)
        if (normalizedType === 'qualified' && relevantAge >= 73 && currentBalance > 0) {
          // RMD divisor table from IRS
          const rmdTable = {
            73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0,
            79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 
            85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2
          };
          
          const divisor = rmdTable[relevantAge] || 10; // Default divisor for ages > 90
          // Simple RMD calculation - in reality would need to track balance changes
          // For now, use initial balance as approximation
          const rmdAmount = currentBalance / divisor;
          
          // Use the greater of RMD or specified withdrawal
          const monthlyAmount = parseFloat(
            asset.monthly_amount || 
            asset.monthly_withdrawal || 
            asset.withdrawal_amount || 
            0
          );
          const annualWithdrawal = monthlyAmount * 12;
          
          const finalAmount = Math.max(rmdAmount, annualWithdrawal);
          
          console.log(`RMD calculation for age ${relevantAge}:`, {
            balance: currentBalance,
            divisor,
            rmdAmount,
            specifiedWithdrawal: annualWithdrawal,
            finalAmount
          });
          
          return finalAmount;
        }
        
        // Regular withdrawals (before RMD age or for non-qualified)
        // Check various possible fields for the withdrawal amount
        const monthlyAmount = parseFloat(
          asset.monthly_amount || 
          asset.monthly_withdrawal || 
          asset.withdrawal_amount || 
          0
        );
        const annualAmount = monthlyAmount * 12;
        
        // Debug log to see what withdrawal amount is being used
        if (relevantAge === startAge) {
          console.log(`Qualified asset withdrawal at age ${relevantAge}:`, {
            monthlyAmount,
            annualAmount,
            balance: currentBalance,
            asset_details: {
              monthly_amount: asset.monthly_amount,
              withdrawal_amount: asset.withdrawal_amount,
              monthly_withdrawal: asset.monthly_withdrawal
            }
          });
        }
        
        // Only return income if there's an actual withdrawal amount specified
        // Don't use a default - the user should specify their withdrawal strategy
        return annualAmount;
      }
      
      // Calculate income for other asset types
      const monthlyAmount = parseFloat(asset.monthly_amount || 0);
      const annualAmount = monthlyAmount * 12;
      
      // Apply COLA if applicable (for Social Security, Pensions, etc.)
      if (asset.cola && relevantAge >= startAge) {
        const cola = parseFloat(asset.cola || 0) / 100;
        const yearsWithCola = relevantAge - startAge;
        return annualAmount * Math.pow(1 + cola, yearsWithCola);
      }
      
      return annualAmount;
    },
    formatAssetColumnHeader(asset) {
      // Format the column header for each asset
      const type = this.getAssetType(asset);
      const ownerName = asset.owned_by === 'spouse' ? 
        (this.client?.spouse?.first_name || 'Spouse') : 
        (this.client?.first_name || 'Primary');
      
      // Use actual asset name if available, otherwise use type-specific labels
      let displayName = '';
      
      // For investment accounts, use the income_name if available
      if ((type === 'qualified' || type === 'non_qualified' || type === 'roth') && asset.income_name) {
        displayName = asset.income_name;
      } else {
        // Special formatting for different asset types
        switch(type) {
          case 'social_security':
            displayName = 'SSI';
            break;
          case 'pension':
            displayName = asset.income_name || 'Pension';
            break;
          case 'annuity':
            displayName = asset.income_name || 'Annuity';
            break;
          case 'qualified':
            displayName = '401k/IRA';
            break;
          case 'non_qualified':
            displayName = 'Non-Qual';
            break;
          case 'rental_income':
            displayName = asset.income_name || 'Rental';
            break;
          default:
            displayName = asset.income_name || asset.income_type.replace(/_/g, ' ');
        }
      }
      
      return `${displayName} (${ownerName})`;
    },
    formatCurrency(value) {
      if (value === 0 || value === null || value === undefined) return '-';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    },
    showAssetModal(asset) {
      this.selectedAsset = asset;
      this.showAssetDetailModal = true;
      this.isLoadingGraph = true;

      // Simulate loading time for complex calculations
      // In real scenario, this would be during actual async data fetch
      setTimeout(() => {
        this.isLoadingGraph = false;
      }, 500); // Half second loading time for UX feedback
    },
    closeAssetModal() {
      this.showAssetDetailModal = false;
      this.selectedAsset = null;
      this.isLoadingGraph = false;
    }
  }
};
</script> 