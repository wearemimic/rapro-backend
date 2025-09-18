import { defineStore } from 'pinia';

/**
 * SINGLE SOURCE OF TRUTH FOR ALL SCENARIO CALCULATIONS
 *
 * WHY THIS EXISTS:
 * - Backend provides base calculations (gross_income, taxes, etc)
 * - We need detailed per-asset breakdowns for display
 * - ALL pages must show the SAME values
 * - No duplicate calculations anywhere
 */
export const useScenarioCalculationsStore = defineStore('scenarioCalculations', {
  state: () => ({
    // Raw data from backend
    scenarioResults: [],
    assetDetails: [],
    scenario: null,
    client: null,

    // Calculated projections
    assetProjections: {},
    enhancedResults: []
  }),

  getters: {
    /**
     * Get projection for a specific asset
     */
    getAssetProjection: (state) => (assetId) => {
      return state.assetProjections[assetId] || {};
    },

    /**
     * Get enhanced results with per-asset breakdowns
     */
    getEnhancedResults: (state) => {
      return state.enhancedResults;
    }
  },

  actions: {
    /**
     * Initialize the store with scenario data
     * This is called ONCE when entering scenario details
     */
    initialize(scenarioResults, assetDetails, scenario, client) {
      console.log('Store initialization called with:', {
        scenarioResults: scenarioResults?.length,
        assetDetails: assetDetails?.length,
        scenario: !!scenario,
        client: !!client
      });

      this.scenarioResults = scenarioResults || [];
      this.assetDetails = assetDetails || [];
      this.scenario = scenario;
      this.client = client;

      // Calculate all projections
      this.calculateAllProjections();

      // Enhance results with per-asset data
      this.enhanceResults();

      console.log('Store initialized. Enhanced results:', this.enhancedResults.length);
    },

    /**
     * Calculate projections for ALL assets ONCE
     * This is the MASTER calculation that everyone uses
     */
    calculateAllProjections() {
      this.assetProjections = {};

      console.log('📊 STORE: Calculating projections for', this.assetDetails.length, 'assets');
      console.log('📊 STORE: Asset details:', this.assetDetails);

      // Calculate projection for each asset
      this.assetDetails.forEach(asset => {
        const normalizedType = this.getAssetType(asset);

        console.log(`📊 STORE: Asset ${asset.id} (${asset.income_name || asset.investment_name}):`, {
          type: normalizedType,
          income_type: asset.income_type,
          balance: asset.current_asset_balance,
          rateOfReturn: asset.rate_of_return,
          growthRate: asset.growth_rate,
          monthlyAmount: asset.monthly_amount,
          withdrawalStartAge: asset.age_to_begin_withdrawal
        });

        // Calculate for qualified/non-qualified assets OR any asset with a balance
        const hasBalance = parseFloat(asset.current_asset_balance || 0) > 0;
        const isInvestmentAccount = normalizedType === 'qualified' || normalizedType === 'non_qualified';

        if (isInvestmentAccount || hasBalance) {
          console.log(`📊 STORE: WILL calculate projection for asset ${asset.id} (type: ${normalizedType}, balance: ${asset.current_asset_balance})`);
          this.assetProjections[asset.id] = this.calculateSingleAssetProjection(asset);

          // Log some sample ages to verify calculations
          const ages = [65, 70, 73, 75, 80];
          const samples = {};
          ages.forEach(age => {
            if (this.assetProjections[asset.id][age]) {
              samples[`age${age}`] = {
                withdrawal: this.assetProjections[asset.id][age].withdrawal,
                balance: this.assetProjections[asset.id][age].balance
              };
            }
          });
          console.log(`📊 STORE: Projection samples for asset ${asset.id}:`, samples);
        } else {
          console.log(`📊 STORE: SKIPPING projection for asset ${asset.id} (not an investment account and no balance)`);
        }
      });

      console.log('📊 STORE: All projections calculated:', Object.keys(this.assetProjections));
    },

    /**
     * MASTER CALCULATION for a single asset
     *
     * WHY IT WORKS:
     * 1. Tracks balance year-over-year (not using initial balance every year)
     * 2. Applies contributions before retirement
     * 3. Calculates RMD based on CURRENT balance at each age
     * 4. Uses greater of RMD or specified withdrawal
     * 5. Applies growth to remaining balance after withdrawal
     */
    calculateSingleAssetProjection(asset) {
      console.log(`📊 STORE calculateSingleAssetProjection: Starting for asset ${asset.id}`);
      console.log(`📊 STORE: Client data:`, {
        birthdate: this.client?.birthdate,
        hasClient: !!this.client
      });

      // Get client's actual current age
      const birthYear = new Date(this.client?.birthdate).getFullYear();
      const currentYear = new Date().getFullYear();
      const actualCurrentAge = currentYear - birthYear;

      console.log(`📊 STORE: Age calculation: birthYear=${birthYear}, currentYear=${currentYear}, age=${actualCurrentAge}`);

      // WHY: We need actual age, not retirement age, to track from today
      if (isNaN(actualCurrentAge) || actualCurrentAge < 0 || actualCurrentAge > 120) {
        console.error(`📊 STORE ERROR: Invalid age calculated: ${actualCurrentAge}, birthdate: ${this.client?.birthdate}`);
        return {};
      }

      // Get parameters
      const endAge = this.scenario?.mortality_age || 90;
      const growthRate = parseFloat(asset.rate_of_return || asset.growth_rate || 0);
      const withdrawalStartAge = parseInt(asset.age_to_begin_withdrawal || 65);
      const withdrawalEndAge = parseInt(asset.age_to_end_withdrawal || endAge);
      const monthlyContribution = parseFloat(asset.monthly_contribution || 0);
      const annualContribution = monthlyContribution * 12;
      const specifiedAnnualWithdrawal = parseFloat(asset.monthly_amount || 0) * 12;

      // IRS RMD divisor table
      // WHY: Required by IRS for tax-deferred accounts starting at age 73
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

      // Calculate for EVERY year from current age to end
      // WHY: We need complete timeline for both table and graph
      for (let age = actualCurrentAge; age <= endAge; age++) {
        let withdrawal = 0;

        if (age < withdrawalStartAge) {
          // PRE-RETIREMENT PHASE
          // WHY: Still contributing, no withdrawals
          currentBalance += annualContribution;
          currentBalance *= (1 + growthRate);
        } else if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
          // RETIREMENT PHASE

          // Calculate RMD if applicable
          // WHY: IRS requires minimum distributions from qualified accounts at 73+
          if (normalizedType === 'qualified' && age >= 73 && currentBalance > 0) {
            const divisor = rmdTable[age] || (age > 115 ? 1.9 : 10);
            const rmdAmount = currentBalance / divisor;

            // WHY: Must take greater of RMD or what user specified
            withdrawal = Math.max(rmdAmount, specifiedAnnualWithdrawal);
          } else {
            withdrawal = specifiedAnnualWithdrawal;
          }

          // WHY: Can't withdraw more than available
          if (withdrawal > currentBalance) {
            withdrawal = currentBalance;
          }

          // ORDER MATTERS: Withdraw first, then apply growth to remainder
          // WHY: Growth happens on money that stays invested
          currentBalance -= withdrawal;
          currentBalance *= (1 + growthRate);
        }

        // Store both withdrawal and remaining balance
        // WHY: Table needs withdrawal, graph needs both
        projection[age] = {
          withdrawal: withdrawal,
          balance: currentBalance,
          age: age
        };
      }

      return projection;
    },

    /**
     * Enhance backend results with per-asset breakdown
     * WHY: Backend gives totals, frontend needs individual asset values
     */
    enhanceResults() {
      console.log('📊 STORE: Enhancing results with', this.assetDetails.length, 'assets');
      console.log('📊 STORE: Asset projections available:', Object.keys(this.assetProjections));

      this.enhancedResults = this.scenarioResults.map(result => {
        const enhanced = { ...result };
        enhanced.assetIncomes = {};

        // Add per-asset income breakdown
        this.assetDetails.forEach(asset => {
          const normalizedType = this.getAssetType(asset);
          const owner = asset.owned_by?.toLowerCase();
          let income = 0;

          // Debug logging for first year only
          if (result.year === this.scenarioResults[0].year) {
            console.log(`📊 STORE: Processing asset ${asset.id} (${asset.income_name || asset.investment_name}):`, {
              type: normalizedType,
              owner: owner,
              hasProjection: !!this.assetProjections[asset.id]
            });
          }

          // Social Security - backend provides these
          if (normalizedType === 'social_security') {
            if (owner === 'primary') {
              income = parseFloat(result.ss_income_primary || 0);
            } else if (owner === 'spouse' || owner === 'secondary') {
              income = parseFloat(result.ss_income_spouse || 0);
            }
          }
          // Qualified/Non-Qualified - use our projections
          else if ((normalizedType === 'qualified' || normalizedType === 'non_qualified')) {
            if (this.assetProjections[asset.id]) {
              const relevantAge = owner === 'spouse' ? result.spouse_age : result.primary_age;
              const projection = this.assetProjections[asset.id][relevantAge];
              income = projection ? projection.withdrawal : 0;

              if (result.year === this.scenarioResults[0].year) {
                console.log(`📊 STORE: Asset ${asset.id} at age ${relevantAge}: withdrawal = ${income}`, {
                  projection: projection,
                  hasProjection: !!projection,
                  allAgesInProjection: Object.keys(this.assetProjections[asset.id] || {})
                });
              }
            } else {
              console.log(`📊 STORE WARNING: No projection found for ${normalizedType} asset ${asset.id}`);
              income = 0;
            }
          }
          // For ANY asset with a balance that has a projection
          else if (this.assetProjections[asset.id]) {
            const relevantAge = owner === 'spouse' ? result.spouse_age : result.primary_age;
            const projection = this.assetProjections[asset.id][relevantAge];
            income = projection ? projection.withdrawal : 0;

            if (result.year === this.scenarioResults[0].year) {
              console.log(`📊 STORE: Asset ${asset.id} (type: ${normalizedType}) using projection at age ${relevantAge}: withdrawal = ${income}`);
            }
          }
          // Other types - need calculation (pensions, annuities, etc)
          else {
            income = this.calculateOtherAssetIncome(asset, result.primary_age, result.spouse_age);
          }

          enhanced.assetIncomes[asset.id] = income;
        });

        // Log first year for debugging
        if (result.year === this.scenarioResults[0].year) {
          console.log('📊 STORE: First year asset incomes:', enhanced.assetIncomes);
          console.log('📊 STORE: Asset income keys:', Object.keys(enhanced.assetIncomes));
          console.log('📊 STORE: Asset income values:', Object.values(enhanced.assetIncomes));
        }

        return enhanced;
      });

      console.log('📊 STORE: Enhanced results created:', this.enhancedResults.length, 'rows');
      if (this.enhancedResults.length > 0) {
        console.log('📊 STORE: Sample enhanced result:', this.enhancedResults[0]);
      }
    },

    /**
     * Calculate income for non-balance assets (pensions, annuities, etc)
     */
    calculateOtherAssetIncome(asset, primaryAge, spouseAge) {
      const owner = asset.owned_by?.toLowerCase();
      const relevantAge = owner === 'spouse' ? spouseAge : primaryAge;
      const startAge = parseInt(asset.age_to_begin_withdrawal || 65);
      const endAge = parseInt(asset.age_to_end_withdrawal || 90);

      // Check if within age range
      if (relevantAge < startAge || relevantAge > endAge) {
        return 0;
      }

      // Calculate income with COLA if applicable
      const monthlyAmount = parseFloat(asset.monthly_amount || 0);
      const cola = parseFloat(asset.cola || 0) / 100;
      const yearsActive = relevantAge - startAge;
      const inflatedAmount = monthlyAmount * Math.pow(1 + cola, yearsActive);

      return inflatedAmount * 12; // Annual amount
    },

    /**
     * Normalize asset type for consistent handling
     */
    getAssetType(asset) {
      const rawType = asset.income_type || '';
      const type = rawType.toLowerCase().replace(/\s+/g, '_');

      // Always log the first asset for debugging
      if (this.assetDetails && this.assetDetails[0] === asset) {
        console.log(`📊 STORE getAssetType DETAILED: Asset ${asset.id}`, {
          raw: rawType,
          normalized: type,
          balance: asset.current_asset_balance,
          name: asset.income_name
        });
      }

      // Map various formats to standard types
      if (type.includes('social_security')) return 'social_security';

      // Check for 401k, IRA, and similar qualified accounts
      if (type.includes('401') || type.includes('ira') || type.includes('403') || type.includes('457')) {
        console.log(`📊 STORE: Matched ${rawType} as qualified (401k/IRA pattern)`);
        return 'qualified';
      }

      // Check for "qualified" in the name
      if (type.includes('qualified') && !type.includes('non')) return 'qualified';

      // Check for non-qualified
      if (type.includes('non_qualified') || type.includes('non-qualified') || type.includes('nonqualified')) return 'non_qualified';

      // Check for Roth
      if (type.includes('roth')) return 'roth';

      // Check other types
      if (type.includes('pension')) return 'pension';
      if (type.includes('annuity')) return 'annuity';
      if (type.includes('rental')) return 'rental_income';
      if (type.includes('wage')) return 'wages';

      // FALLBACK: If nothing matches but has a balance, it's likely an investment account
      // This catches custom names like "Bob's Retirement Fund"
      const hasBalance = parseFloat(asset.current_asset_balance || 0) > 0;
      if (hasBalance) {
        console.log(`📊 STORE: Asset "${rawType}" has balance ${asset.current_asset_balance}, treating as qualified`);
        return 'qualified';
      }

      return type;
    }
  }
});