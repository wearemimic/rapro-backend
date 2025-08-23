<template>
  <div>

    <!-- Social Security Planning Tools Section -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-header">
        <h5 class="card-title">Social Security Planning Tools</h5>
        <p class="card-text">Specialized tools for Social Security optimization and client education</p>
      </div>
      <div class="card-body">
        <!-- Tool Navigation Tabs -->
        <ul class="nav nav-tabs" id="ssToolsTabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="provisional-income-tab" data-bs-toggle="tab" data-bs-target="#provisional-income" type="button" role="tab">
              Provisional Income Calculator
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="spousal-benefits-tab" data-bs-toggle="tab" data-bs-target="#spousal-benefits" type="button" role="tab">
              Spousal & Survivor Benefits
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="wep-gpo-tab" data-bs-toggle="tab" data-bs-target="#wep-gpo" type="button" role="tab">
              WEP/GPO Impact
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="strategy-comparison-tab" data-bs-toggle="tab" data-bs-target="#strategy-comparison" type="button" role="tab">
              Strategy Comparison
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="edge-case-tab" data-bs-toggle="tab" data-bs-target="#edge-case" type="button" role="tab">
              Edge Case Tester
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="explanation-engine-tab" data-bs-toggle="tab" data-bs-target="#explanation-engine" type="button" role="tab">
              Explanation Engine
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="ssa-rulebook-tab" data-bs-toggle="tab" data-bs-target="#ssa-rulebook" type="button" role="tab">
              SSA Rulebook
            </button>
          </li>
        </ul>

        <!-- Tool Content -->
        <div class="tab-content" id="ssToolsTabContent">
          <!-- 1. Provisional Income & SS Taxation Calculator -->
          <div class="tab-pane fade show active" id="provisional-income" role="tabpanel">
            <div class="row mt-4">
              <div class="col-md-5">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Calculate Taxable Social Security</h6>
                    <p class="small text-muted mb-3">Determine what portion of Social Security benefits are taxable based on provisional income.</p>
                    
                    <div class="mb-3">
                      <label for="filingStatus" class="form-label">Filing Status</label>
                      <select class="form-select" id="filingStatus" v-model="provisionalIncomeCalc.filingStatus">
                        <option value="single">Single</option>
                        <option value="joint">Married Filing Jointly</option>
                        <option value="separate">Married Filing Separately</option>
                      </select>
                    </div>
                    
                    <div class="mb-3">
                      <label for="agi" class="form-label">Adjusted Gross Income (without SS)</label>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="agi" v-model="provisionalIncomeCalc.agi">
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <label for="taxExemptInterest" class="form-label">Tax-Exempt Interest</label>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="taxExemptInterest" v-model="provisionalIncomeCalc.taxExemptInterest">
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <label for="ssBenefits" class="form-label">Social Security Benefits (Annual)</label>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="ssBenefits" v-model="provisionalIncomeCalc.ssBenefits">
                      </div>
                    </div>
                    
                    <button class="btn btn-primary" @click="calculateTaxableSS">Calculate</button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-7">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Results</h6>
                    
                    <div v-if="provisionalIncomeCalc.calculated">
                      <div class="alert" :class="provisionalIncomeCalc.alertClass">
                        <h4 class="alert-heading">{{ provisionalIncomeCalc.taxablePercentage }}% of Social Security is taxable</h4>
                        <hr>
                        <p class="mb-0">{{ provisionalIncomeCalc.explanation }}</p>
                      </div>
                      
                      <div class="table-responsive mt-4">
                        <table class="table table-bordered">
                          <tbody>
                            <tr>
                              <th scope="row">Adjusted Gross Income</th>
                              <td>${{ provisionalIncomeCalc.agi.toLocaleString() }}</td>
                            </tr>
                            <tr>
                              <th scope="row">+ Tax-Exempt Interest</th>
                              <td>${{ provisionalIncomeCalc.taxExemptInterest.toLocaleString() }}</td>
                            </tr>
                            <tr>
                              <th scope="row">+ 50% of Social Security</th>
                              <td>${{ (provisionalIncomeCalc.ssBenefits * 0.5).toLocaleString() }}</td>
                            </tr>
                            <tr class="table-primary">
                              <th scope="row">= Provisional Income</th>
                              <td>${{ provisionalIncomeCalc.provisionalIncome.toLocaleString() }}</td>
                            </tr>
                            <tr>
                              <th scope="row">Base Amount ({{ provisionalIncomeCalc.filingStatus }})</th>
                              <td>${{ provisionalIncomeCalc.baseAmount.toLocaleString() }}</td>
                            </tr>
                            <tr>
                              <th scope="row">Adjusted Base Amount</th>
                              <td>${{ provisionalIncomeCalc.adjustedBaseAmount.toLocaleString() }}</td>
                            </tr>
                            <tr class="table-success">
                              <th scope="row">Taxable Social Security Amount</th>
                              <td>${{ provisionalIncomeCalc.taxableAmount.toLocaleString() }}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                    
                    <div v-else class="text-center py-5">
                      <i class="bi bi-calculator fs-1 text-muted"></i>
                      <p class="mt-3 text-muted">Enter your details and click Calculate to see what portion of Social Security benefits are taxable.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 3. Spousal & Survivor Benefit Optimizer -->
          <div class="tab-pane fade" id="spousal-benefits" role="tabpanel">
            <div class="row mt-4">
              <div class="col-md-5">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Spousal & Survivor Benefit Calculator</h6>
                    <p class="small text-muted mb-3">Calculate and compare various spousal and survivor benefit options.</p>
                    
                    <div class="mb-3">
                      <label class="form-label">Calculation Type</label>
                      <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="benefitType" id="spousalRadio" value="spousal" v-model="spousalBenefitCalc.benefitType">
                        <label class="btn btn-outline-primary" for="spousalRadio">Spousal</label>
                        
                        <input type="radio" class="btn-check" name="benefitType" id="survivorRadio" value="survivor" v-model="spousalBenefitCalc.benefitType">
                        <label class="btn btn-outline-primary" for="survivorRadio">Survivor</label>
                        
                        <input type="radio" class="btn-check" name="benefitType" id="divorcedRadio" value="divorced" v-model="spousalBenefitCalc.benefitType">
                        <label class="btn btn-outline-primary" for="divorcedRadio">Divorced</label>
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <label for="primaryDob" class="form-label">Primary's Date of Birth</label>
                      <input type="date" class="form-control" id="primaryDob" v-model="spousalBenefitCalc.primaryDob">
                    </div>
                    
                    <div class="mb-3">
                      <label for="spouseDob" class="form-label">Spouse's Date of Birth</label>
                      <input type="date" class="form-control" id="spouseDob" v-model="spousalBenefitCalc.spouseDob">
                    </div>
                    
                    <div class="mb-3">
                      <label for="primaryPia" class="form-label">Primary's PIA (Primary Insurance Amount)</label>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="primaryPia" v-model="spousalBenefitCalc.primaryPia">
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <label for="spousePia" class="form-label">Spouse's PIA</label>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="spousePia" v-model="spousalBenefitCalc.spousePia">
                      </div>
                    </div>
                    
                    <div v-if="spousalBenefitCalc.benefitType === 'divorced'" class="mb-3">
                      <label for="marriageDuration" class="form-label">Marriage Duration (years)</label>
                      <input type="number" class="form-control" id="marriageDuration" v-model="spousalBenefitCalc.marriageDuration">
                    </div>
                    
                    <button class="btn btn-primary" @click="calculateSpousalBenefit">Calculate Benefits</button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-7">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Benefit Options</h6>
                    
                    <div v-if="spousalBenefitCalc.calculated">
                      <div class="alert alert-info mb-4">
                        <div class="d-flex">
                          <div class="flex-shrink-0">
                            <i class="bi bi-info-circle fs-3"></i>
                          </div>
                          <div class="flex-grow-1 ms-3">
                            <h6 class="alert-heading">{{ spousalBenefitCalc.strategyHeading }}</h6>
                            <p class="mb-0">{{ spousalBenefitCalc.strategyExplanation }}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div class="table-responsive">
                        <table class="table table-bordered">
                          <thead>
                            <tr>
                              <th>Filing Strategy</th>
                              <th>Monthly Benefit</th>
                              <th>Notes</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(option, index) in spousalBenefitCalc.options" :key="index" :class="option.optimal ? 'table-success' : ''">
                              <td>{{ option.strategy }}</td>
                              <td>${{ option.monthlyBenefit.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                              <td>{{ option.notes }}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      
                      <div class="mt-4">
                        <h6>Key Dates & Milestones:</h6>
                        <ul class="list-group">
                          <li v-for="(date, index) in spousalBenefitCalc.keyDates" :key="index" class="list-group-item d-flex justify-content-between align-items-center">
                            {{ date.description }}
                            <span class="badge bg-primary rounded-pill">{{ date.date }}</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                    
                    <div v-else class="text-center py-5">
                      <i class="bi bi-people fs-1 text-muted"></i>
                      <p class="mt-3 text-muted">Enter benefit details to compare spousal, survivor, or divorced spouse benefit options.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 4. WEP/GPO Impact Simulator -->
          <div class="tab-pane fade" id="wep-gpo" role="tabpanel">
            <div class="row mt-4">
              <div class="col-md-5">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">WEP/GPO Impact Calculator</h6>
                    <p class="small text-muted mb-3">Calculate how the Windfall Elimination Provision (WEP) and Government Pension Offset (GPO) affect Social Security benefits.</p>
                    
                    <div class="mb-3">
                      <label class="form-label">Calculation Type</label>
                      <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="wepGpoType" id="wepRadio" value="wep" v-model="wepGpoCalc.calcType">
                        <label class="btn btn-outline-primary" for="wepRadio">WEP</label>
                        
                        <input type="radio" class="btn-check" name="wepGpoType" id="gpoRadio" value="gpo" v-model="wepGpoCalc.calcType">
                        <label class="btn btn-outline-primary" for="gpoRadio">GPO</label>
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <label for="ssaBenefit" class="form-label">Estimated Monthly Social Security Benefit</label>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="ssaBenefit" v-model="wepGpoCalc.ssaBenefit">
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <label for="pensionAmount" class="form-label">Monthly Non-Covered Pension Amount</label>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="pensionAmount" v-model="wepGpoCalc.pensionAmount">
                      </div>
                    </div>
                    
                    <div v-if="wepGpoCalc.calcType === 'wep'" class="mb-3">
                      <label for="yearsSubstantialEarnings" class="form-label">Years of Substantial Earnings</label>
                      <input type="number" class="form-control" id="yearsSubstantialEarnings" v-model="wepGpoCalc.yearsSubstantialEarnings" min="0" max="35">
                      <div class="form-text">Years with earnings at or above the substantial earnings threshold ($27,300 in 2022)</div>
                    </div>
                    
                    <button class="btn btn-primary" @click="calculateWepGpoImpact">Calculate Impact</button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-7">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Results</h6>
                    
                    <div v-if="wepGpoCalc.calculated">
                      <div class="alert" :class="wepGpoCalc.alertClass">
                        <h4 class="alert-heading">{{ wepGpoCalc.impactHeading }}</h4>
                        <hr>
                        <p>{{ wepGpoCalc.impactExplanation }}</p>
                      </div>
                      
                      <div class="table-responsive mt-4">
                        <table class="table table-bordered">
                          <tbody>
                            <tr>
                              <th scope="row">Original Monthly Benefit</th>
                              <td>${{ wepGpoCalc.ssaBenefit.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                            </tr>
                            <tr>
                              <th scope="row">{{ wepGpoCalc.calcType.toUpperCase() }} Reduction</th>
                              <td class="text-danger">-${{ wepGpoCalc.reduction.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                            </tr>
                            <tr class="table-primary">
                              <th scope="row">Adjusted Monthly Benefit</th>
                              <td>${{ wepGpoCalc.adjustedBenefit.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                            </tr>
                            <tr>
                              <th scope="row">Annual Reduction</th>
                              <td class="text-danger">-${{ (wepGpoCalc.reduction * 12).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                    
                    <div v-else class="text-center py-5">
                      <i class="bi bi-exclamation-triangle fs-1 text-muted"></i>
                      <p class="mt-3 text-muted">Enter your details to calculate the impact of WEP or GPO on your Social Security benefits.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 7. Provisional Income Layering Sandbox -->
          
          <!-- 8. Filing Strategy Comparison Report Generator -->
          <div class="tab-pane fade" id="strategy-comparison" role="tabpanel">
            <div class="row mt-4">
              <div class="col-12 mb-4">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Strategy Comparison Report Generator</h6>
                    <p class="small text-muted mb-3">Generate side-by-side comparisons of different Social Security claiming strategies.</p>
                  </div>
                </div>
              </div>
              
              <div class="col-md-4">
                <div class="card">
                  <div class="card-header">
                    <h6 class="mb-0">Strategies to Compare</h6>
                  </div>
                  <div class="card-body">
                    <div v-for="(strategy, index) in strategyComparison.strategies" :key="index" class="mb-3 border p-3 rounded" :class="{'border-primary': strategy.selected}">
                      <div class="d-flex justify-content-between align-items-center mb-2">
                        <div class="form-check">
                          <input class="form-check-input" type="checkbox" :id="`strategy-${index}`" v-model="strategy.selected">
                          <label class="form-check-label" :for="`strategy-${index}`">
                            <strong>{{ strategy.name }}</strong>
                          </label>
                        </div>
                        <span class="badge" :class="strategy.badgeClass">{{ strategy.primaryAge }}</span>
                      </div>
                      <p class="small text-muted mb-0">{{ strategy.description }}</p>
                    </div>
                    
                    <div class="mb-3">
                      <label class="form-label">Add Custom Strategy</label>
                      <div class="input-group mb-2">
                        <input type="text" class="form-control" placeholder="Strategy Name" v-model="strategyComparison.newStrategy.name">
                        <button class="btn btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#customStrategyCollapse">
                          <i class="bi bi-plus-lg"></i>
                        </button>
                      </div>
                      
                      <div class="collapse" id="customStrategyCollapse">
                        <div class="card card-body">
                          <div class="mb-2">
                            <label class="form-label">Primary Claiming Age</label>
                            <select class="form-select" v-model="strategyComparison.newStrategy.primaryAge">
                              <option v-for="age in strategyComparison.availableAges" :key="age" :value="age">{{ age }}</option>
                            </select>
                          </div>
                          
                          <div class="mb-2">
                            <label class="form-label">Spouse Claiming Age</label>
                            <select class="form-select" v-model="strategyComparison.newStrategy.spouseAge">
                              <option v-for="age in strategyComparison.availableAges" :key="age" :value="age">{{ age }}</option>
                            </select>
                          </div>
                          
                          <div class="mb-2">
                            <label class="form-label">Strategy Description</label>
                            <textarea class="form-control" rows="2" v-model="strategyComparison.newStrategy.description"></textarea>
                          </div>
                          
                          <button class="btn btn-sm btn-primary" @click="addCustomStrategy">Add Strategy</button>
                        </div>
                      </div>
                    </div>
                    
                    <button class="btn btn-primary w-100" :disabled="!strategyComparison.hasSelectedStrategies" @click="generateStrategyComparison">
                      Generate Comparison
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-8">
                <div class="card h-100">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Comparison Results</h6>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="exportStrategyComparisonToPDF">
                        <i class="bi bi-file-pdf me-1"></i> PDF
                      </button>
                      <button class="btn btn-outline-primary" @click="exportStrategyComparisonToExcel">
                        <i class="bi bi-file-excel me-1"></i> Excel
                      </button>
                    </div>
                  </div>
                  
                  <div class="card-body">
                    <div v-if="strategyComparison.generated">
                      <!-- Strategy Comparison Chart -->
                      <div style="height: 250px">
                        <Graph 
                          :data="strategyComparisonChartData" 
                          :options="strategyComparisonChartOptions"
                          :height="250"
                        />
                      </div>
                      
                      <div class="table-responsive mt-4">
                        <table class="table table-bordered">
                          <thead>
                            <tr>
                              <th>Strategy</th>
                              <th v-for="(header, index) in strategyComparison.tableHeaders" :key="index">{{ header }}</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(row, index) in strategyComparison.tableData" :key="index" :class="row.optimal ? 'table-success' : ''">
                              <td>{{ row.name }}</td>
                              <td v-for="(header, hIndex) in strategyComparison.tableHeaders" :key="`${index}-${hIndex}`">
                                {{ row[header.toLowerCase().replace(/\s/g, '_')] }}
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      
                      <div class="alert alert-info mt-4">
                        <h6 class="alert-heading">Optimal Strategy</h6>
                        <p class="mb-0">{{ strategyComparison.optimalStrategyText }}</p>
                      </div>
                    </div>
                    
                    <div v-else class="text-center py-5">
                      <i class="bi bi-bar-chart fs-1 text-muted"></i>
                      <p class="mt-3 text-muted">Select strategies to compare and click "Generate Comparison" to see a detailed analysis.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 9. Edge Case Scenario Tester -->
          <div class="tab-pane fade" id="edge-case" role="tabpanel">
            <div class="row mt-4">
              <div class="col-md-5">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Edge Case Scenario Tester</h6>
                    <p class="small text-muted mb-3">Test how special situations impact Social Security benefits and claiming strategies.</p>
                    
                    <div class="mb-3">
                      <label class="form-label">Select Edge Case Scenario</label>
                      <select class="form-select" v-model="edgeCaseTest.selectedScenario">
                        <option v-for="(scenario, index) in edgeCaseTest.scenarios" :key="index" :value="scenario.id">
                          {{ scenario.name }}
                        </option>
                      </select>
                    </div>
                    
                    <div class="alert alert-light">
                      <p class="mb-0 small">{{ edgeCaseTest.scenarioDescription }}</p>
                    </div>
                    
                    <!-- Dynamic form fields based on selected scenario -->
                    <div class="mb-3" v-for="(field, index) in edgeCaseTest.fields" :key="index">
                      <label :for="`edge-case-field-${index}`" class="form-label">{{ field.label }}</label>
                      
                      <select v-if="field.type === 'select'" :id="`edge-case-field-${index}`" class="form-select" v-model="edgeCaseTest.values[field.id]">
                        <option v-for="(option, optIndex) in field.options" :key="optIndex" :value="option.value">
                          {{ option.label }}
                        </option>
                      </select>
                      
                      <div v-else-if="field.type === 'checkbox'" class="form-check">
                        <input :id="`edge-case-field-${index}`" class="form-check-input" type="checkbox" v-model="edgeCaseTest.values[field.id]">
                        <label class="form-check-label" :for="`edge-case-field-${index}`">{{ field.checkboxLabel }}</label>
                      </div>
                      
                      <div v-else-if="field.type === 'date'">
                        <input :id="`edge-case-field-${index}`" type="date" class="form-control" v-model="edgeCaseTest.values[field.id]">
                      </div>
                      
                      <div v-else-if="field.type === 'currency'" class="input-group">
                        <span class="input-group-text">$</span>
                        <input :id="`edge-case-field-${index}`" type="number" class="form-control" v-model="edgeCaseTest.values[field.id]">
                      </div>
                      
                      <input v-else :id="`edge-case-field-${index}`" :type="field.type" class="form-control" v-model="edgeCaseTest.values[field.id]">
                      
                      <div class="form-text" v-if="field.hint">{{ field.hint }}</div>
                    </div>
                    
                    <button class="btn btn-primary w-100" @click="runEdgeCaseTest">Run Scenario Test</button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-7">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Scenario Results</h6>
                    
                    <div v-if="edgeCaseTest.testRun">
                      <div class="alert" :class="edgeCaseTest.resultClass">
                        <h5 class="alert-heading">{{ edgeCaseTest.resultTitle }}</h5>
                        <p>{{ edgeCaseTest.resultSummary }}</p>
                      </div>
                      
                      <div class="table-responsive mt-4">
                        <table class="table table-bordered">
                          <thead>
                            <tr>
                              <th>Factor</th>
                              <th>Impact</th>
                              <th>Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(result, index) in edgeCaseTest.resultFactors" :key="index">
                              <td>{{ result.factor }}</td>
                              <td>
                                <span :class="result.impactClass">{{ result.impact }}</span>
                              </td>
                              <td>{{ result.value }}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      
                      <div v-if="edgeCaseTest.recommendedActions.length > 0" class="mt-4">
                        <h6>Recommended Actions:</h6>
                        <ul class="list-group">
                          <li v-for="(action, index) in edgeCaseTest.recommendedActions" :key="index" class="list-group-item">
                            <i class="bi bi-check-circle-fill text-success me-2"></i> {{ action }}
                          </li>
                        </ul>
                      </div>
                      
                      <div v-if="edgeCaseTest.warnings.length > 0" class="mt-4">
                        <h6>Warnings:</h6>
                        <ul class="list-group">
                          <li v-for="(warning, index) in edgeCaseTest.warnings" :key="index" class="list-group-item list-group-item-warning">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ warning }}
                          </li>
                        </ul>
                      </div>
                      
                      <div class="mt-4">
                        <h6>Relevant SSA Rules:</h6>
                        <div class="card bg-light">
                          <div class="card-body">
                            <p class="mb-0 small" v-html="edgeCaseTest.relevantRules"></p>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div v-else class="text-center py-5">
                      <i class="bi bi-puzzle fs-1 text-muted"></i>
                      <p class="mt-3 text-muted">Select a scenario and fill in the required information to see how special situations affect Social Security benefits.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 10. Advisor-Facing Explanation Engine -->
          <div class="tab-pane fade" id="explanation-engine" role="tabpanel">
            <div class="row mt-4">
              <div class="col-md-5">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">Social Security Explanation Engine</h6>
                    <p class="small text-muted mb-3">Get clear, client-ready explanations for complex Social Security concepts and calculations.</p>
                    
                    <div class="mb-3">
                      <label class="form-label">Explanation Type</label>
                      <select class="form-select" v-model="explanationEngine.selectedType">
                        <option value="taxable-ss">Why is X% of Social Security taxable?</option>
                        <option value="irmaa-increase">Why did IRMAA increase this year?</option>
                        <option value="breakeven">When is the breakeven point between two claiming ages?</option>
                        <option value="wep-reduction">Why is my benefit reduced due to WEP?</option>
                        <option value="survivor-rules">How do survivor benefits work?</option>
                        <option value="restricted-app">What is a restricted application?</option>
                        <option value="fra-impact">How does my Full Retirement Age affect benefits?</option>
                        <option value="custom-question">Custom question</option>
                      </select>
                    </div>
                    
                    <div v-if="explanationEngine.selectedType === 'taxable-ss'" class="mb-3">
                      <label for="ssPercentage" class="form-label">Percentage of Social Security that is taxable</label>
                      <select class="form-select" id="ssPercentage" v-model="explanationEngine.taxableSSPercentage">
                        <option value="0">0%</option>
                        <option value="50">50%</option>
                        <option value="85">85%</option>
                      </select>
                    </div>
                    
                    <div v-if="explanationEngine.selectedType === 'breakeven'" class="mb-3">
                      <label for="earlierAge" class="form-label">Earlier Claiming Age</label>
                      <select class="form-select" id="earlierAge" v-model="explanationEngine.earlierAge">
                        <option v-for="age in explanationEngine.claimingAges" :key="`early-${age}`" :value="age">{{ age }}</option>
                      </select>
                      
                      <label for="laterAge" class="form-label mt-2">Later Claiming Age</label>
                      <select class="form-select" id="laterAge" v-model="explanationEngine.laterAge">
                        <option v-for="age in explanationEngine.claimingAges" :key="`late-${age}`" :value="age">{{ age }}</option>
                      </select>
                    </div>
                    
                    <div v-if="explanationEngine.selectedType === 'custom-question'" class="mb-3">
                      <label for="customQuestion" class="form-label">Your Question</label>
                      <textarea class="form-control" id="customQuestion" rows="3" v-model="explanationEngine.customQuestion" placeholder="Enter your Social Security question here..."></textarea>
                    </div>
                    
                    <div v-if="explanationEngine.needsClientContext" class="mb-3">
                      <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="useClientData" v-model="explanationEngine.useClientData">
                        <label class="form-check-label" for="useClientData">
                          Use current client data
                        </label>
                      </div>
                      
                      <div v-if="!explanationEngine.useClientData">
                        <label for="clientContext" class="form-label">Client Context</label>
                        <textarea class="form-control" id="clientContext" rows="3" v-model="explanationEngine.clientContext" placeholder="Briefly describe the client's situation (age, filing status, income sources, etc.)"></textarea>
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <label class="form-label">Explanation Format</label>
                      <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="formatType" id="formatSimple" value="simple" v-model="explanationEngine.format">
                        <label class="btn btn-outline-primary" for="formatSimple">Simple</label>
                        
                        <input type="radio" class="btn-check" name="formatType" id="formatDetailed" value="detailed" v-model="explanationEngine.format">
                        <label class="btn btn-outline-primary" for="formatDetailed">Detailed</label>
                        
                        <input type="radio" class="btn-check" name="formatType" id="formatTechnical" value="technical" v-model="explanationEngine.format">
                        <label class="btn btn-outline-primary" for="formatTechnical">Technical</label>
                      </div>
                    </div>
                    
                    <button class="btn btn-primary w-100" @click="generateExplanation">Generate Explanation</button>
                  </div>
                </div>
              </div>
              
              <div class="col-md-7">
                <div class="card h-100">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                      <h6 class="card-subtitle mb-0">Explanation</h6>
                      <div v-if="explanationEngine.generated">
                        <button class="btn btn-sm btn-outline-primary me-2" @click="copyExplanationToClipboard">
                          <i class="bi bi-clipboard me-1"></i> Copy
                        </button>
                        <button class="btn btn-sm btn-outline-primary" @click="downloadExplanationAsPDF">
                          <i class="bi bi-download me-1"></i> Download
                        </button>
                      </div>
                    </div>
                    
                    <div v-if="explanationEngine.generated">
                      <div v-if="explanationEngine.showVisual" class="mb-4">
                        <div style="height: 200px">
                          <Graph 
                            :data="explanationVisualData" 
                            :options="explanationVisualOptions"
                            :height="200"
                          />
                        </div>
                      </div>
                      
                      <div class="card bg-light mb-4">
                        <div class="card-body">
                          <h5 class="card-title">{{ explanationEngine.title }}</h5>
                          <div v-html="explanationEngine.explanation"></div>
                        </div>
                      </div>
                      
                      <div v-if="explanationEngine.format === 'detailed' || explanationEngine.format === 'technical'">
                        <h6>Key Points:</h6>
                        <ul class="list-group mb-4">
                          <li v-for="(point, index) in explanationEngine.keyPoints" :key="index" class="list-group-item">
                            <i class="bi bi-check-circle-fill text-success me-2"></i> {{ point }}
                          </li>
                        </ul>
                      </div>
                      
                      <div v-if="explanationEngine.format === 'technical'">
                        <h6>Relevant References:</h6>
                        <div class="table-responsive">
                          <table class="table table-sm table-bordered">
                            <thead class="table-light">
                              <tr>
                                <th>Source</th>
                                <th>Section</th>
                                <th>Description</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-for="(ref, index) in explanationEngine.references" :key="index">
                                <td>{{ ref.source }}</td>
                                <td>{{ ref.section }}</td>
                                <td>{{ ref.description }}</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    
                    <div v-else class="text-center py-5">
                      <i class="bi bi-chat-quote fs-1 text-muted"></i>
                      <p class="mt-3 text-muted">Select a topic and click "Generate Explanation" to create a clear, client-ready explanation.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Bonus: SSA/IRS Rulebook Quick Reference -->
          <div class="tab-pane fade" id="ssa-rulebook" role="tabpanel">
            <div class="row mt-4">
              <div class="col-md-4">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-subtitle mb-3">SSA/IRS Rulebook</h6>
                    <p class="small text-muted mb-3">Quick reference guide to Social Security and IRS rules affecting retirement planning.</p>
                    
                    <div class="mb-3">
                      <div class="input-group">
                        <input type="text" class="form-control" placeholder="Search rules..." v-model="ssaRulebook.searchQuery">
                        <button class="btn btn-outline-secondary" type="button" @click="searchRules">
                          <i class="bi bi-search"></i>
                        </button>
                      </div>
                    </div>
                    
                    <div class="list-group mb-3">
                      <button
                        v-for="(category, index) in ssaRulebook.categories"
                        :key="index"
                        class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                        :class="{ active: ssaRulebook.selectedCategory === category.id }"
                        @click="selectRuleCategory(category.id)"
                      >
                        {{ category.name }}
                        <span class="badge bg-primary rounded-pill">{{ category.count }}</span>
                      </button>
                    </div>
                    
                    <div class="card bg-light">
                      <div class="card-body">
                        <h6 class="card-title">Updated Rules</h6>
                        <div class="small" v-for="(update, index) in ssaRulebook.recentUpdates" :key="index">
                          <div class="d-flex align-items-center mt-2">
                            <span class="badge bg-warning me-2">{{ update.date }}</span>
                            <span>{{ update.description }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-8">
                <div class="card h-100">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">{{ ssaRulebook.selectedCategoryName }}</h6>
                    <div>
                      <button class="btn btn-sm btn-outline-primary me-2" @click="downloadRulebookSection">
                        <i class="bi bi-download me-1"></i> Download
                      </button>
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-secondary" :class="{ active: ssaRulebook.view === 'list' }" @click="ssaRulebook.view = 'list'">
                          <i class="bi bi-list-ul"></i>
                        </button>
                        <button class="btn btn-outline-secondary" :class="{ active: ssaRulebook.view === 'cards' }" @click="ssaRulebook.view = 'cards'">
                          <i class="bi bi-grid"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <div class="card-body">
                    <div v-if="ssaRulebook.view === 'list'" class="accordion" id="rulesAccordion">
                      <div v-for="(rule, index) in ssaRulebook.filteredRules" :key="index" class="accordion-item">
                        <h2 class="accordion-header" :id="`heading-${index}`">
                          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" :data-bs-target="`#collapse-${index}`" aria-expanded="false" :aria-controls="`collapse-${index}`">
                            <div>
                              {{ rule.title }}
                              <span v-if="rule.isNew" class="badge bg-success ms-2">New</span>
                              <span v-if="rule.isUpdated" class="badge bg-warning ms-2">Updated</span>
                            </div>
                          </button>
                        </h2>
                        <div :id="`collapse-${index}`" class="accordion-collapse collapse" :aria-labelledby="`heading-${index}`" data-bs-parent="#rulesAccordion">
                          <div class="accordion-body">
                            <p v-html="rule.description"></p>
                            
                            <div v-if="rule.table" class="table-responsive mt-3">
                              <table class="table table-sm table-bordered">
                                <thead class="table-light">
                                  <tr>
                                    <th v-for="(header, hIndex) in rule.table.headers" :key="hIndex">{{ header }}</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  <tr v-for="(row, rIndex) in rule.table.data" :key="rIndex">
                                    <td v-for="(header, hIndex) in rule.table.headers" :key="`${rIndex}-${hIndex}`">
                                      {{ row[header.toLowerCase().replace(/\s/g, '_')] }}
                                    </td>
                                  </tr>
                                </tbody>
                              </table>
                            </div>
                            
                            <div class="mt-3">
                              <span class="badge bg-light text-muted me-2">Source:</span>
                              <a :href="rule.sourceUrl" target="_blank" class="small">{{ rule.source }}</a>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div v-else-if="ssaRulebook.view === 'cards'" class="row g-3">
                      <div v-for="(rule, index) in ssaRulebook.filteredRules" :key="index" class="col-md-6">
                        <div class="card h-100">
                          <div class="card-header d-flex justify-content-between align-items-center py-2">
                            <h6 class="mb-0 small">{{ rule.title }}</h6>
                            <div>
                              <span v-if="rule.isNew" class="badge bg-success">New</span>
                              <span v-if="rule.isUpdated" class="badge bg-warning">Updated</span>
                            </div>
                          </div>
                          <div class="card-body">
                            <p class="small" v-html="rule.description"></p>
                            <div class="mt-2 small">
                              <span class="badge bg-light text-muted me-1">Source:</span>
                              <a :href="rule.sourceUrl" target="_blank" class="small">{{ rule.source }}</a>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div v-if="ssaRulebook.filteredRules.length === 0" class="text-center py-5">
                      <i class="bi bi-journal-x fs-1 text-muted"></i>
                      <p class="mt-3 text-muted">No rules found. Try a different category or search term.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { jsPDF } from 'jspdf';
import { applyPlugin } from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import Graph from '../components/Graph.vue';

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

export default {
  components: {
    Graph
  },
  props: {
    scenarioResults: {
      type: Array,
      required: true
    },
    client: {
      type: Object,
      required: true
    },
    benefitByAge: {
      type: Object,
      required: true
    },
    socialSecurityCola: {
      type: Number,
      required: true
    },
    medicareCosts: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      isDropdownOpen: {
        worksheets: false
      },
      // 1. Provisional Income & SS Taxation Calculator
      provisionalIncomeCalc: {
        filingStatus: 'single',
        agi: 30000,
        taxExemptInterest: 0,
        ssBenefits: 18000,
        calculated: false,
        provisionalIncome: 0,
        taxablePercentage: 0,
        taxableAmount: 0,
        explanation: '',
        alertClass: 'alert-info',
        baseAmount: 0,
        adjustedBaseAmount: 0
      },
      // 3. Spousal & Survivor Benefit Optimizer
      spousalBenefitCalc: {
        benefitType: 'spousal',
        primaryDob: '',
        spouseDob: '',
        primaryPia: 2000,
        spousePia: 800,
        marriageDuration: 10,
        calculated: false,
        strategyHeading: '',
        strategyExplanation: '',
        options: [],
        keyDates: []
      },
      // 4. WEP/GPO Impact Simulator
      wepGpoCalc: {
        calcType: 'wep',
        ssaBenefit: 1500,
        pensionAmount: 1200,
        yearsSubstantialEarnings: 20,
        calculated: false,
        reduction: 0,
        adjustedBenefit: 0,
        impactHeading: '',
        impactExplanation: '',
        alertClass: 'alert-info',
        relevantRules: ''
      },
      // 7. Provisional Income Layering Sandbox
      // 8. Filing Strategy Comparison Report Generator
      strategyComparison: {
        strategies: [
          { 
            name: 'Early Claiming', 
            primaryAge: '62 & 0 mo', 
            spouseAge: '62 & 0 mo', 
            description: 'Both claim at earliest eligibility', 
            selected: true,
            badgeClass: 'bg-warning'
          },
          { 
            name: 'Full Retirement Age', 
            primaryAge: '67 & 0 mo', 
            spouseAge: '67 & 0 mo', 
            description: 'Both claim at FRA', 
            selected: true,
            badgeClass: 'bg-primary'
          },
          { 
            name: 'Maximize Primary', 
            primaryAge: '70 & 0 mo', 
            spouseAge: '67 & 0 mo', 
            description: 'Primary maximizes, spouse at FRA', 
            selected: true,
            badgeClass: 'bg-success'
          }
        ],
        newStrategy: {
          name: '',
          primaryAge: '65 & 0 mo',
          spouseAge: '65 & 0 mo',
          description: ''
        },
        availableAges: [
          '62 & 0 mo', '63 & 0 mo', '64 & 0 mo', '65 & 0 mo', 
          '66 & 0 mo', '67 & 0 mo', '68 & 0 mo', '69 & 0 mo', '70 & 0 mo'
        ],
        generated: false,
        tableHeaders: ['Monthly Benefit', 'Lifetime Value', 'Breakeven Age', 'Value at 85'],
        tableData: [],
        optimalStrategyText: '',
        hasSelectedStrategies: true
      },
      // 9. Edge Case Scenario Tester
      edgeCaseTest: {
        scenarios: [
          { id: 'wep-gpo', name: 'WEP/GPO Impact' },
          { id: 'remarriage', name: 'Remarriage After 60' },
          { id: 'divorce', name: 'Divorce After 10+ Years' },
          { id: 'income-spike', name: 'IRMAA Income Spike' },
          { id: 'disability', name: 'Disability Transition' }
        ],
        selectedScenario: 'wep-gpo',
        scenarioDescription: 'Test how the Windfall Elimination Provision (WEP) or Government Pension Offset (GPO) affects Social Security benefits for those with non-covered pensions.',
        fields: [],
        values: {},
        testRun: false,
        resultTitle: '',
        resultSummary: '',
        resultClass: 'alert-info',
        resultFactors: [],
        recommendedActions: [],
        warnings: [],
        relevantRules: ''
      },
      // 10. Advisor-Facing Explanation Engine
      explanationEngine: {
        selectedType: 'taxable-ss',
        taxableSSPercentage: 85,
        claimingAges: [62, 63, 64, 65, 66, 67, 68, 69, 70],
        earlierAge: 62,
        laterAge: 70,
        customQuestion: '',
        useClientData: true,
        clientContext: '',
        needsClientContext: true,
        format: 'simple',
        generated: false,
        title: '',
        explanation: '',
        showVisual: false,
        keyPoints: [],
        references: []
      },
      // Bonus: SSA/IRS Rulebook Quick Reference
      ssaRulebook: {
        searchQuery: '',
        selectedCategory: 'all',
        selectedCategoryName: 'All Rules',
        view: 'list',
        categories: [
          { id: 'all', name: 'All Rules', count: 42 },
          { id: 'claiming', name: 'Claiming Rules', count: 12 },
          { id: 'taxation', name: 'Taxation Rules', count: 8 },
          { id: 'spousal', name: 'Spousal Benefits', count: 7 },
          { id: 'wep-gpo', name: 'WEP & GPO', count: 5 },
          { id: 'earnings', name: 'Earnings Limits', count: 3 },
          { id: 'irmaa', name: 'IRMAA & Medicare', count: 7 }
        ],
        recentUpdates: [
          { date: '2023-10-12', description: 'COLA update for 2024 (3.2% increase)' },
          { date: '2023-09-24', description: 'Medicare Part B premium change for 2024' },
          { date: '2023-08-15', description: 'IRMAA brackets adjusted for inflation' }
        ],
        filteredRules: [],
        rules: []
      }
    };
  },
  computed: {
    breakevenChartData() {
      const datasets = Object.entries(this.benefitByAge).map(([age, benefit], i) => {
        const label = `Age ${age}`;
        const data = [];
        let cumulativeIncome = 0;
        const startYear = 62 + (parseInt(age) - 62);
        
        for (let year = 62; year <= 90; year++) {
          if (year >= startYear) {
            cumulativeIncome += benefit;
            data.push(cumulativeIncome);
          } else {
            data.push(null);
          }
        }
        
        return {
          type: 'line',
          label,
          data,
          borderColor: `hsl(${(i * 40) % 360}, 70%, 50%)`,
          backgroundColor: `hsla(${(i * 40) % 360}, 70%, 50%, 0.1)`,
          borderWidth: 2,
          tension: 0.3
        };
      });
      
      return {
        labels: Array.from({ length: 29 }, (_, i) => (62 + i).toString()),
        datasets
      };
    },
    breakevenChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Age'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Cumulative Social Security ($)'
            },
            ticks: {
              beginAtZero: true
            }
          }
        },
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
          title: {
            display: true,
            text: 'Social Security Breakeven Analysis'
          },
          legend: {
            position: 'bottom'
          }
        }
      };
    },
    medicareAdjustedBreakevenChartData() {
      const datasets = Object.entries(this.benefitByAge).map(([age, benefit], i) => {
        const label = `Age ${age}`;
        const data = [];
        let cumulativeIncome = 0;
        const startYear = 62 + (parseInt(age) - 62);
        
        for (let year = 62; year <= 90; year++) {
          if (year >= startYear) {
            // Find Medicare costs for this year
            const medicareCost = this.getMedicareCostForAge(year);
            const adjustedBenefit = benefit - (medicareCost * 12); // Annual adjusted benefit
            
            cumulativeIncome += adjustedBenefit;
            data.push(cumulativeIncome);
          } else {
            data.push(null);
          }
        }
        
        return {
          type: 'line',
          label,
          data,
          borderColor: `hsl(${(i * 40) % 360}, 70%, 50%)`,
          backgroundColor: `hsla(${(i * 40) % 360}, 70%, 50%, 0.1)`,
          borderWidth: 2,
          tension: 0.3
        };
      });
      
      return {
        labels: Array.from({ length: 29 }, (_, i) => (62 + i).toString()),
        datasets
      };
    },
    medicareAdjustedBreakevenChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Age'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Cumulative Net Social Security ($)'
            },
            ticks: {
              beginAtZero: true
            }
          }
        },
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
          title: {
            display: true,
            text: 'Medicare-Adjusted Social Security Breakeven Analysis'
          },
          legend: {
            position: 'bottom'
          }
        }
      };
    },
    // Strategy Comparison Chart Data
    strategyComparisonChartData() {
      if (!this.strategyComparison.generated) {
        return { labels: [], datasets: [] };
      }
      
      // Extract strategy names for labels
      const labels = this.strategyComparison.tableData.map(row => row.name);
      
      // Create datasets for different metrics
      return {
        labels,
        datasets: [
          {
            type: 'bar',
            label: 'Monthly Benefit',
            data: this.strategyComparison.tableData.map(row => parseFloat(row.monthly_benefit.replace('$', '').replace(',', ''))),
            backgroundColor: 'rgba(55, 125, 255, 0.7)',
            borderColor: 'rgb(55, 125, 255)',
            borderWidth: 1,
            yAxisID: 'y'
          },
          {
            type: 'line',
            label: 'Lifetime Value',
            data: this.strategyComparison.tableData.map(row => parseFloat(row.lifetime_value.replace('$', '').replace(',', '')) / 1000),
            borderColor: 'rgb(255, 193, 7)',
            backgroundColor: 'rgba(255, 193, 7, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            yAxisID: 'y1'
          }
        ]
      };
    },
    strategyComparisonChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: 'Monthly Benefit ($)'
            },
            ticks: {
              beginAtZero: true,
              callback: (value) => `$${value.toLocaleString()}`
            }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: {
              display: true,
              text: 'Lifetime Value ($K)'
            },
            ticks: {
              beginAtZero: true,
              callback: (value) => `$${value}K`
            },
            grid: {
              drawOnChartArea: false
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  if (context.dataset.label === 'Lifetime Value') {
                    label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y * 1000);
                  } else {
                    label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                  }
                }
                return label;
              }
            }
          },
          title: {
            display: true,
            text: 'Strategy Comparison'
          },
          legend: {
            position: 'bottom'
          }
        }
      };
    },
    // Explanation Engine Visual Data
    explanationVisualData() {
      if (!this.explanationEngine.generated || !this.explanationEngine.showVisual) {
        return { labels: [], datasets: [] };
      }
      
      // Example breakeven visualization (for breakeven explanation type)
      if (this.explanationEngine.selectedType === 'breakeven') {
        const labels = Array.from({ length: 29 }, (_, i) => (62 + i).toString());
        
        // Calculate cumulative benefits for both claiming ages
        const earlierData = [];
        const laterData = [];
        
        let earlierCumulative = 0;
        let laterCumulative = 0;
        const earlierMonthly = 1000 + ((this.explanationEngine.earlierAge - 62) * 75);
        const laterMonthly = 1000 + ((this.explanationEngine.laterAge - 62) * 75);
        
        for (let age = 62; age <= 90; age++) {
          if (age >= this.explanationEngine.earlierAge) {
            earlierCumulative += earlierMonthly * 12;
            earlierData.push(earlierCumulative);
          } else {
            earlierData.push(null);
          }
          
          if (age >= this.explanationEngine.laterAge) {
            laterCumulative += laterMonthly * 12;
            laterData.push(laterCumulative);
          } else {
            laterData.push(null);
          }
        }
        
        return {
          labels,
          datasets: [
            {
              type: 'line',
              label: `Claim at ${this.explanationEngine.earlierAge}`,
              data: earlierData,
              borderColor: 'rgb(255, 99, 132)',
              backgroundColor: 'rgba(255, 99, 132, 0.1)',
              borderWidth: 2,
              tension: 0.3
            },
            {
              type: 'line',
              label: `Claim at ${this.explanationEngine.laterAge}`,
              data: laterData,
              borderColor: 'rgb(54, 162, 235)',
              backgroundColor: 'rgba(54, 162, 235, 0.1)',
              borderWidth: 2,
              tension: 0.3
            }
          ]
        };
      }
      
      // Default empty data
      return { labels: [], datasets: [] };
    },
    explanationVisualOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Age'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Cumulative Benefits ($)'
            },
            ticks: {
              callback: (value) => `$${value.toLocaleString()}`
            }
          }
        },
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                }
                return label;
              }
            }
          },
          legend: {
            position: 'bottom'
          }
        }
      };
    }
  },
  methods: {
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
    getAverageMedicareCostByAge(age) {
      // Find all scenario results where primary_age matches the given age
      const matchingYears = this.medicareCosts.filter(year => year.primary_age === parseInt(age));
      
      // If no matching years, return 0
      if (matchingYears.length === 0) return 0;
      
      // Calculate the average monthly Medicare cost
      const totalMedicareCost = matchingYears.reduce((sum, year) => sum + parseFloat(year.total_medicare || 0), 0);
      return totalMedicareCost / matchingYears.length / 12; // Monthly cost
    },
    getMedicareCostForAge(age) {
      // Find the Medicare cost for the given age
      const matchingYear = this.medicareCosts.find(year => year.primary_age === parseInt(age));
      return matchingYear ? parseFloat(matchingYear.total_medicare || 0) : 0;
    },
    // Provisional Income Calculator
    calculateTaxableSS() {
      // Calculate provisional income
      const agi = parseFloat(this.provisionalIncomeCalc.agi);
      const taxExemptInterest = parseFloat(this.provisionalIncomeCalc.taxExemptInterest);
      const halfSS = parseFloat(this.provisionalIncomeCalc.ssBenefits) * 0.5;
      const provisionalIncome = agi + taxExemptInterest + halfSS;
      
      // Set base amounts based on filing status
      let baseAmount = 25000;
      let adjustedBaseAmount = 34000;
      
      if (this.provisionalIncomeCalc.filingStatus === 'joint') {
        baseAmount = 32000;
        adjustedBaseAmount = 44000;
      } else if (this.provisionalIncomeCalc.filingStatus === 'separate') {
        baseAmount = 0;
        adjustedBaseAmount = 0;
      }
      
      // Calculate taxable amount
      let taxablePercentage = 0;
      let taxableAmount = 0;
      let explanation = '';
      let alertClass = 'alert-success';
      
      if (provisionalIncome < baseAmount) {
        taxablePercentage = 0;
        taxableAmount = 0;
        explanation = `Your provisional income is below the base amount for your filing status, so none of your Social Security benefits are taxable.`;
      } else if (provisionalIncome < adjustedBaseAmount) {
        taxablePercentage = 50;
        taxableAmount = Math.min(
          halfSS,
          0.5 * (provisionalIncome - baseAmount)
        );
        explanation = `Your provisional income exceeds the base amount but is below the adjusted base amount, so up to 50% of your Social Security benefits are taxable.`;
        alertClass = 'alert-warning';
      } else {
        taxablePercentage = 85;
        taxableAmount = Math.min(
          0.85 * this.provisionalIncomeCalc.ssBenefits,
          halfSS + 0.85 * (provisionalIncome - adjustedBaseAmount)
        );
        explanation = `Your provisional income exceeds the adjusted base amount, so up to 85% of your Social Security benefits are taxable.`;
        alertClass = 'alert-danger';
      }
      
      // Update the data model
      this.provisionalIncomeCalc.provisionalIncome = provisionalIncome;
      this.provisionalIncomeCalc.taxablePercentage = Math.round((taxableAmount / this.provisionalIncomeCalc.ssBenefits) * 100);
      this.provisionalIncomeCalc.taxableAmount = taxableAmount;
      this.provisionalIncomeCalc.explanation = explanation;
      this.provisionalIncomeCalc.alertClass = alertClass;
      this.provisionalIncomeCalc.baseAmount = baseAmount;
      this.provisionalIncomeCalc.adjustedBaseAmount = adjustedBaseAmount;
      this.provisionalIncomeCalc.calculated = true;
    },
    // For other tools - add stub methods
    calculateSpousalBenefit() {
      // Implement spousal benefit calculation
      this.spousalBenefitCalc.calculated = true;
    },
    calculateWepGpoImpact() {
      // Implement WEP/GPO impact calculation
      this.wepGpoCalc.calculated = true;
    },
    addCustomStrategy() {
      // Add custom strategy to the list
    },
    generateStrategyComparison() {
      // Generate strategy comparison
      this.strategyComparison.generated = true;
    },
    runEdgeCaseTest() {
      // Run edge case test
      this.edgeCaseTest.testRun = true;
    },
    generateExplanation() {
      // Generate explanation
      this.explanationEngine.generated = true;
      this.explanationEngine.showVisual = this.explanationEngine.selectedType === 'breakeven';
    },
    searchRules() {
      // Search rules
    },
    selectRuleCategory(categoryId) {
      this.ssaRulebook.selectedCategory = categoryId;
      // Update selected category name
      const category = this.ssaRulebook.categories.find(c => c.id === categoryId);
      if (category) {
        this.ssaRulebook.selectedCategoryName = category.name;
      }
    },
    downloadRulebookSection() {
      // Download rulebook section
    },
    copyExplanationToClipboard() {
      // Copy explanation to clipboard
    },
    downloadExplanationAsPDF() {
      // Download explanation as PDF
    }
  }
};
</script> 