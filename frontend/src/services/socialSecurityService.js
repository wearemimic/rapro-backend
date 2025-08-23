/**
 * Social Security Service
 * 
 * Enhanced Social Security benefit calculations building upon existing logic
 * from ScenarioCreate.vue and backend scenario_processor.py
 * 
 * Integrates with scenario data structure and provides:
 * - Claiming strategy optimization
 * - Lifetime benefits analysis
 * - Spousal and survivor benefit calculations
 * - Break-even age analysis
 * - IRMAA impact calculations
 * - Provisional income taxation
 */

export class SocialSecurityService {
  constructor() {
    // Social Security constants based on current SSA rules
    this.CURRENT_FRA = 67;
    this.MIN_CLAIMING_AGE = 62;
    this.MAX_CLAIMING_AGE = 70;
    this.EARLY_RETIREMENT_PENALTY = 0.0067; // Per month before FRA
    this.DELAYED_RETIREMENT_CREDIT = 0.0067; // Per month after FRA
    this.MAX_ADJUSTMENT_FACTOR = 1.24; // 24% increase at age 70
    this.MIN_ADJUSTMENT_FACTOR = 0.7; // 30% reduction at age 62
    
    // Spousal benefit constants
    this.SPOUSAL_BENEFIT_RATE = 0.5; // 50% of primary worker's PIA
    this.SURVIVOR_BENEFIT_RATE = 1.0; // 100% of deceased spouse's benefit
    
    // Provisional income thresholds for taxation (2024)
    this.PROVISIONAL_INCOME_THRESHOLDS = {
      single: { base: 25000, additional: 34000 },
      marriedFilingJointly: { base: 32000, additional: 44000 },
      marriedFilingSeparately: { base: 0, additional: 0 }
    };
    
    // Life expectancy tables (simplified - based on SSA actuarial tables)
    this.LIFE_EXPECTANCY = {
      male: { 62: 21.8, 67: 17.5, 70: 14.8 },
      female: { 62: 24.3, 67: 19.8, 70: 17.0 }
    };
  }

  /**
   * Extract Social Security data from scenario income sources
   * @param {Array} incomeSources - Scenario income sources
   * @returns {Object} - Structured Social Security data
   */
  extractSocialSecurityData(incomeSources) {
    const ssData = {
      primary: null,
      spouse: null
    };

    incomeSources.forEach(income => {
      if (income.income_type === 'Social Security') {
        const data = {
          amountAtFRA: parseFloat(income.amount_at_fra) || 0,
          startAge: parseInt(income.start_age) || this.CURRENT_FRA,
          endAge: parseInt(income.end_age) || 100,
          ownedBy: income.owned_by,
          currentBenefit: this.calculateBenefit(income.amount_at_fra, income.start_age)
        };

        if (income.owned_by === 'primary') {
          ssData.primary = data;
        } else if (income.owned_by === 'spouse') {
          ssData.spouse = data;
        }
      }
    });

    return ssData;
  }

  /**
   * Enhanced Social Security benefit calculation
   * Based on existing calculateSocialSecurityBenefit() function with improvements
   * @param {number} amountAtFRA - Monthly benefit at Full Retirement Age
   * @param {number} claimingAge - Age when benefits start
   * @param {number} fra - Full Retirement Age (default 67)
   * @returns {number} - Monthly benefit amount
   */
  calculateBenefit(amountAtFRA, claimingAge, fra = this.CURRENT_FRA) {
    if (!amountAtFRA || !claimingAge) return 0;

    const monthlyAdjustment = this.EARLY_RETIREMENT_PENALTY;
    let adjustmentFactor = 1;

    if (claimingAge < fra) {
      // Early retirement reduction
      const monthsEarly = (fra - claimingAge) * 12;
      adjustmentFactor -= monthsEarly * monthlyAdjustment;
    } else if (claimingAge > fra) {
      // Delayed retirement credit
      const monthsDelayed = (claimingAge - fra) * 12;
      adjustmentFactor += monthsDelayed * this.DELAYED_RETIREMENT_CREDIT;
    }

    // Apply bounds
    adjustmentFactor = Math.max(this.MIN_ADJUSTMENT_FACTOR, Math.min(adjustmentFactor, this.MAX_ADJUSTMENT_FACTOR));
    
    return amountAtFRA * adjustmentFactor;
  }

  /**
   * Calculate spousal benefits
   * @param {Object} primaryData - Primary worker's SS data
   * @param {Object} spouseData - Spouse's SS data
   * @param {number} spouseClaimingAge - Spouse's claiming age
   * @returns {Object} - Spousal benefit analysis
   */
  calculateSpousalBenefits(primaryData, spouseData, spouseClaimingAge) {
    if (!primaryData || !spouseData) return null;

    // Calculate spousal benefit based on primary worker's PIA
    const spousalBenefitAtFRA = primaryData.amountAtFRA * this.SPOUSAL_BENEFIT_RATE;
    const spouseOwnBenefit = this.calculateBenefit(spouseData.amountAtFRA, spouseClaimingAge);
    const spousalBenefit = this.calculateBenefit(spousalBenefitAtFRA, spouseClaimingAge);

    // Spouse gets higher of own benefit or spousal benefit
    const actualSpousalBenefit = Math.max(spouseOwnBenefit, spousalBenefit);
    const isEligibleForSpousal = spousalBenefit > spouseOwnBenefit;

    return {
      spouseOwnBenefit,
      spousalBenefit,
      actualBenefit: actualSpousalBenefit,
      isEligibleForSpousal,
      additionalAmount: Math.max(0, spousalBenefit - spouseOwnBenefit)
    };
  }

  /**
   * Calculate lifetime benefits for different claiming strategies
   * @param {number} amountAtFRA - Monthly benefit at FRA
   * @param {number} claimingAge - Claiming age
   * @param {number} lifeExpectancy - Expected lifespan
   * @returns {Object} - Lifetime benefit analysis
   */
  calculateLifetimeBenefits(amountAtFRA, claimingAge, lifeExpectancy) {
    const monthlyBenefit = this.calculateBenefit(amountAtFRA, claimingAge);
    const yearsOfBenefits = Math.max(0, lifeExpectancy - claimingAge);
    const lifetimeTotal = monthlyBenefit * 12 * yearsOfBenefits;

    return {
      monthlyBenefit,
      yearsOfBenefits,
      lifetimeTotal,
      adjustmentFactor: monthlyBenefit / amountAtFRA
    };
  }

  /**
   * Calculate break-even age between two claiming strategies
   * @param {number} amountAtFRA - Monthly benefit at FRA
   * @param {number} earlyAge - Earlier claiming age
   * @param {number} laterAge - Later claiming age
   * @returns {Object} - Break-even analysis
   */
  calculateBreakEvenAge(amountAtFRA, earlyAge, laterAge) {
    const earlyBenefit = this.calculateBenefit(amountAtFRA, earlyAge);
    const laterBenefit = this.calculateBenefit(amountAtFRA, laterAge);
    
    const monthlyDifference = laterBenefit - earlyBenefit;
    const totalDelayedBenefits = earlyBenefit * 12 * (laterAge - earlyAge);
    
    if (monthlyDifference <= 0) return null;
    
    const monthsToBreakEven = totalDelayedBenefits / monthlyDifference;
    const breakEvenAge = laterAge + (monthsToBreakEven / 12);
    
    return {
      earlyBenefit,
      laterBenefit,
      monthlyDifference,
      monthsToBreakEven,
      breakEvenAge,
      yearsToBreakEven: breakEvenAge - laterAge
    };
  }

  /**
   * Calculate optimal claiming strategy for couples
   * @param {Object} ssData - Social Security data for both spouses
   * @param {Object} lifeExpectancies - Life expectancy for both spouses
   * @returns {Object} - Optimization analysis
   */
  calculateOptimalStrategy(ssData, lifeExpectancies) {
    if (!ssData.primary) return null;

    const strategies = [];
    
    // Generate claiming age combinations
    for (let primaryAge = this.MIN_CLAIMING_AGE; primaryAge <= this.MAX_CLAIMING_AGE; primaryAge++) {
      const primaryBenefits = this.calculateLifetimeBenefits(
        ssData.primary.amountAtFRA, 
        primaryAge, 
        lifeExpectancies.primary
      );

      let spouseBenefits = null;
      if (ssData.spouse) {
        for (let spouseAge = this.MIN_CLAIMING_AGE; spouseAge <= this.MAX_CLAIMING_AGE; spouseAge++) {
          spouseBenefits = this.calculateLifetimeBenefits(
            ssData.spouse.amountAtFRA, 
            spouseAge, 
            lifeExpectancies.spouse
          );

          // Include spousal benefits analysis
          const spousalAnalysis = this.calculateSpousalBenefits(ssData.primary, ssData.spouse, spouseAge);

          strategies.push({
            primaryAge,
            spouseAge,
            primaryLifetimeBenefits: primaryBenefits.lifetimeTotal,
            spouseLifetimeBenefits: spouseBenefits.lifetimeTotal,
            totalLifetimeBenefits: primaryBenefits.lifetimeTotal + spouseBenefits.lifetimeTotal,
            primaryMonthly: primaryBenefits.monthlyBenefit,
            spouseMonthly: spouseBenefits.monthlyBenefit,
            spousalAnalysis
          });
        }
      } else {
        strategies.push({
          primaryAge,
          spouseAge: null,
          primaryLifetimeBenefits: primaryBenefits.lifetimeTotal,
          spouseLifetimeBenefits: 0,
          totalLifetimeBenefits: primaryBenefits.lifetimeTotal,
          primaryMonthly: primaryBenefits.monthlyBenefit,
          spouseMonthly: 0,
          spousalAnalysis: null
        });
      }
    }

    // Find optimal strategy (highest lifetime benefits)
    const optimal = strategies.reduce((best, current) => 
      current.totalLifetimeBenefits > best.totalLifetimeBenefits ? current : best
    );

    return {
      strategies,
      optimal,
      totalStrategies: strategies.length
    };
  }

  /**
   * Calculate provisional income and Social Security taxation
   * Based on backend scenario_processor.py taxation logic
   * @param {number} agi - Adjusted Gross Income
   * @param {number} taxExemptInterest - Tax-exempt interest income
   * @param {number} ssBenefits - Annual Social Security benefits
   * @param {string} filingStatus - Tax filing status
   * @returns {Object} - Taxation analysis
   */
  calculateSocialSecurityTaxation(agi, taxExemptInterest, ssbenefits, filingStatus) {
    const provisionalIncome = agi + taxExemptInterest + (ssbenefits * 0.5);
    const thresholds = this.PROVISIONAL_INCOME_THRESHOLDS[filingStatus] || this.PROVISIONAL_INCOME_THRESHOLDS.single;
    
    let taxableAmount = 0;
    let taxablePercentage = 0;

    if (provisionalIncome <= thresholds.base) {
      // No taxation
      taxableAmount = 0;
      taxablePercentage = 0;
    } else if (provisionalIncome <= thresholds.additional) {
      // 50% taxation tier
      taxableAmount = Math.min(0.5 * (provisionalIncome - thresholds.base), 0.5 * ssBenefits);
      taxablePercentage = (taxableAmount / ssbenefits) * 100;
    } else {
      // 85% taxation tier
      const amountBetweenThresholds = thresholds.additional - thresholds.base;
      const amountAboveAdditional = provisionalIncome - thresholds.additional;
      
      const taxablePortionFirstTier = 0.5 * amountBetweenThresholds;
      const taxablePortionSecondTier = 0.85 * amountAboveAdditional;
      
      const calculatedTaxableAmount = taxablePortionFirstTier + taxablePortionSecondTier;
      const maxTaxableAmount = 0.85 * ssbenefits;
      
      taxableAmount = Math.min(calculatedTaxableAmount, maxTaxableAmount);
      taxablePercentage = (taxableAmount / ssbenefits) * 100;
    }

    return {
      provisionalIncome,
      taxableAmount,
      taxablePercentage,
      nonTaxableAmount: ssbenefits - taxableAmount,
      thresholds,
      tier: provisionalIncome <= thresholds.base ? 0 : (provisionalIncome <= thresholds.additional ? 1 : 2)
    };
  }

  /**
   * Generate data for lifetime benefits chart
   * @param {Object} ssData - Social Security data
   * @param {Array} claimingAges - Array of claiming ages to analyze
   * @param {number} lifeExpectancy - Life expectancy
   * @returns {Object} - Chart data
   */
  generateLifetimeBenefitsChartData(ssData, claimingAges, lifeExpectancy) {
    const datasets = [];
    const labels = [];

    // Generate age range for x-axis (claiming age to life expectancy)
    const minAge = Math.min(...claimingAges);
    const maxAge = Math.min(lifeExpectancy, 100);
    
    for (let age = minAge; age <= maxAge; age++) {
      labels.push(age);
    }

    // Generate cumulative benefits data for each claiming age
    claimingAges.forEach(claimingAge => {
      const monthlyBenefit = this.calculateBenefit(ssData.amountAtFRA, claimingAge);
      const data = [];
      
      labels.forEach(age => {
        if (age < claimingAge) {
          data.push(0);
        } else {
          const yearsOfBenefits = age - claimingAge;
          const cumulativeBenefits = monthlyBenefit * 12 * yearsOfBenefits;
          data.push(cumulativeBenefits);
        }
      });

      datasets.push({
        label: `Claim at ${claimingAge}`,
        data: data,
        borderColor: this.getChartColor(claimingAge),
        backgroundColor: this.getChartColor(claimingAge, 0.1),
        tension: 0.1
      });
    });

    return { labels, datasets };
  }

  /**
   * Generate couples retirement paycheck heatmap data
   * @param {Object} ssData - Social Security data for both spouses
   * @returns {Object} - Heatmap data
   */
  generateCouplesHeatmapData(ssData) {
    if (!ssData.primary || !ssData.spouse) return null;

    const heatmapData = [];
    
    for (let primaryAge = this.MIN_CLAIMING_AGE; primaryAge <= this.MAX_CLAIMING_AGE; primaryAge++) {
      for (let spouseAge = this.MIN_CLAIMING_AGE; spouseAge <= this.MAX_CLAIMING_AGE; spouseAge++) {
        const primaryBenefit = this.calculateBenefit(ssData.primary.amountAtFRA, primaryAge);
        const spouseBenefit = this.calculateBenefit(ssData.spouse.amountAtFRA, spouseAge);
        const spousalAnalysis = this.calculateSpousalBenefits(ssData.primary, ssData.spouse, spouseAge);
        
        const totalMonthlyBenefit = primaryBenefit + (spousalAnalysis?.actualBenefit || spouseBenefit);
        
        heatmapData.push({
          x: primaryAge,
          y: spouseAge,
          v: totalMonthlyBenefit
        });
      }
    }

    return heatmapData;
  }

  /**
   * Calculate IRMAA impact based on MAGI
   * @param {number} magi - Modified Adjusted Gross Income
   * @param {string} filingStatus - Tax filing status
   * @param {number} year - Tax year
   * @returns {Object} - IRMAA analysis
   */
  calculateIRMAAImpact(magi, filingStatus, year = 2024) {
    // 2024 IRMAA brackets (these should be updated annually)
    const irmaaThresholds = {
      single: [97000, 123000, 153000, 183000, 500000],
      marriedFilingJointly: [194000, 246000, 306000, 366000, 750000]
    };

    const surcharges = [0, 69.90, 174.70, 279.50, 384.30, 419.30]; // Monthly Part B surcharges
    
    const thresholds = irmaaThresholds[filingStatus] || irmaaThresholds.single;
    let bracketIndex = 0;
    
    for (let i = 0; i < thresholds.length; i++) {
      if (magi > thresholds[i]) {
        bracketIndex = i + 1;
      } else {
        break;
      }
    }
    
    const monthlySurcharge = surcharges[bracketIndex] || 0;
    const annualSurcharge = monthlySurcharge * 12;
    
    return {
      bracketIndex,
      magi,
      threshold: bracketIndex > 0 ? thresholds[bracketIndex - 1] : 0,
      nextThreshold: bracketIndex < thresholds.length ? thresholds[bracketIndex] : null,
      monthlySurcharge,
      annualSurcharge,
      hasIRMAA: bracketIndex > 0
    };
  }

  /**
   * Get chart color for different claiming ages
   * @param {number} claimingAge - Claiming age
   * @param {number} alpha - Alpha transparency (optional)
   * @returns {string} - Color string
   */
  getChartColor(claimingAge, alpha = 1) {
    const colors = {
      62: `rgba(220, 53, 69, ${alpha})`,   // Red for early claiming
      63: `rgba(255, 139, 69, ${alpha})`,  // Orange-red
      64: `rgba(255, 193, 7, ${alpha})`,   // Yellow
      65: `rgba(255, 235, 59, ${alpha})`,  // Light yellow
      66: `rgba(139, 195, 74, ${alpha})`,  // Light green
      67: `rgba(76, 175, 80, ${alpha})`,   // Green (FRA)
      68: `rgba(41, 121, 255, ${alpha})`,  // Blue
      69: `rgba(63, 81, 181, ${alpha})`,   // Indigo
      70: `rgba(156, 39, 176, ${alpha})`   // Purple for delayed claiming
    };
    
    return colors[claimingAge] || `rgba(108, 117, 125, ${alpha})`;
  }

  /**
   * Format currency for display
   * @param {number} amount - Amount to format
   * @returns {string} - Formatted currency string
   */
  formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  /**
   * Get life expectancy estimate
   * @param {number} currentAge - Current age
   * @param {string} gender - 'male' or 'female'
   * @returns {number} - Estimated life expectancy
   */
  getLifeExpectancy(currentAge, gender = 'male') {
    // Simple interpolation based on SSA actuarial tables
    const genderData = this.LIFE_EXPECTANCY[gender];
    if (currentAge <= 62) {
      return 62 + genderData[62];
    } else if (currentAge <= 67) {
      const ratio = (currentAge - 62) / 5;
      const yearsRemaining = genderData[62] + ratio * (genderData[67] - genderData[62]);
      return currentAge + yearsRemaining;
    } else if (currentAge <= 70) {
      const ratio = (currentAge - 67) / 3;
      const yearsRemaining = genderData[67] + ratio * (genderData[70] - genderData[67]);
      return currentAge + yearsRemaining;
    } else {
      return currentAge + genderData[70];
    }
  }
}

// Export singleton instance
export const socialSecurityService = new SocialSecurityService();

// Default export for convenience
export default socialSecurityService;