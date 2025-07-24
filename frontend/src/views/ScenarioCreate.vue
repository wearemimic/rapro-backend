<template>
  <div class="p-6 max-w-7xl mx-auto">
    <div class="row d-flex align-items-stretch" style="margin-top:20px;">
      <div class="col-sm-6 col-xl-3 mb-3 mb-xl-6">
        <div class="card h-100">
          <div class="card-body">
            <h3 class="card-title">Create New Scenario</h3>
            <div class="mb-3">
              <label class="block mb-1 font-medium">Scenario Name</label>
              <input v-model="scenario.name" type="text" class="input form-control" placeholder="Enter scenario name" />
            </div>
            <div class="mb-3">
              <label class="block mt-4 mb-1 font-medium">2030 Reduction in SS</label>
              <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" v-model="scenario.reduction_2030_ss" />
              </div>
            </div>
            <div class="mb-3">
              <label class="block mt-4 mb-1 font-medium">Apply Standard Deductions</label>
              <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" v-model="scenario.apply_standard_deduction" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-xl-3 mb-3 mb-xl-6">
        <div class="card h-100">
          <div class="card-body">
            <h3 class="card-title">Scenario Options</h3>
            <div class="mb-3">
              <label class="block mb-1 font-medium">Model Change in Taxes</label>
              <select v-model="scenario.model_tax_change" class="form-control">
                <option value="">No Change</option>
                <option value="sunset_tcja">Sunset of TCJA (2026)</option>
                <option value="raise_top_bracket">Raise Top Bracket to 39.6%</option>
                <option value="lower_standard_deduction">Lower Standard Deduction</option>
                <option value="cap_itemized_deductions">Cap on Itemized Deductions</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="block mt-4 mb-1 font-medium">Medicare Part B Inflation Rate</label>
              <select v-model="scenario.part_b_inflation_rate" class="form-control">
                <option value="6">6%</option>
                <option value="7">7%</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="block mt-4 mb-1 font-medium">Medicare Part D Inflation Rate</label>
              <select v-model="scenario.part_d_inflation_rate" class="form-control">
                <option value="6">6%</option>
                <option value="7">7%</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-xl-3 mb-3 mb-xl-6">
        <div class="card h-100">
          <div class="card-body">  
            <h3 class="text-lg font-semibold mb-2">{{ primaryFirstName }}</h3>
            <div class="mb-3">
              <label class="block mt-2">Medicare Start Age</label>
              <select v-model.number="scenario.primary_medicare_age" class="form-control">
                <option v-for="age in Array.from({ length: 11 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="block mt-2">Lifespan (Age)</label>
              <select v-model.number="scenario.primary_lifespan" class="form-control">
                <option v-for="age in Array.from({ length: 31 }, (_, i) => 70 + i)" :key="age" :value="age">{{ age }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="block mt-2">State</label>
              <select v-model="scenario.primary_state" class="form-control">
                <option value="">Select a state</option>
                <option value="AL">Alabama</option>
                <option value="AK">Alaska</option>
                <option value="AZ">Arizona</option>
                <option value="AR">Arkansas</option>
                <option value="CA">California</option>
                <option value="CO">Colorado</option>
                <option value="CT">Connecticut</option>
                <option value="DE">Delaware</option>
                <option value="FL">Florida</option>
                <option value="GA">Georgia</option>
                <option value="HI">Hawaii</option>
                <option value="ID">Idaho</option>
                <option value="IL">Illinois</option>
                <option value="IN">Indiana</option>
                <option value="IA">Iowa</option>
                <option value="KS">Kansas</option>
                <option value="KY">Kentucky</option>
                <option value="LA">Louisiana</option>
                <option value="ME">Maine</option>
                <option value="MD">Maryland</option>
                <option value="MA">Massachusetts</option>
                <option value="MI">Michigan</option>
                <option value="MN">Minnesota</option>
                <option value="MS">Mississippi</option>
                <option value="MO">Missouri</option>
                <option value="MT">Montana</option>
                <option value="NE">Nebraska</option>
                <option value="NV">Nevada</option>
                <option value="NH">New Hampshire</option>
                <option value="NJ">New Jersey</option>
                <option value="NM">New Mexico</option>
                <option value="NY">New York</option>
                <option value="NC">North Carolina</option>
                <option value="ND">North Dakota</option>
                <option value="OH">Ohio</option>
                <option value="OK">Oklahoma</option>
                <option value="OR">Oregon</option>
                <option value="PA">Pennsylvania</option>
                <option value="RI">Rhode Island</option>
                <option value="SC">South Carolina</option>
                <option value="SD">South Dakota</option>
                <option value="TN">Tennessee</option>
                <option value="TX">Texas</option>
                <option value="UT">Utah</option>
                <option value="VT">Vermont</option>
                <option value="VA">Virginia</option>
                <option value="WA">Washington</option>
                <option value="WV">West Virginia</option>
                <option value="WI">Wisconsin</option>
                <option value="WY">Wyoming</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-xl-3 mb-3 mb-xl-6">
        <div v-if="clientTaxStatus !== 'single'" class="card h-100">
          <div class="card-body">  
            <h3 class="text-lg font-semibold mb-2">{{ spouseFirstName }}</h3>
            <div class="mb-3">
              <label class="block mt-2">Medicare Start Age</label>
              <select v-model.number="scenario.spouse_medicare_age" class="form-control">
                <option v-for="age in Array.from({ length: 11 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="block mt-2">Lifespan (Age)</label>
              <select v-model.number="scenario.spouse_lifespan" class="form-control">
                <option v-for="age in Array.from({ length: 31 }, (_, i) => 70 + i)" :key="age" :value="age">{{ age }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>   

    <div v-if="scenario.apply_standard_deduction" class="row">
      <div class="card">
        <div class="card-body">
          <h3 class="card-title">Standard Deduction Options</h3>
          <div class="mb-3">
            <label class="form-label">Primary is Blind</label>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" v-model="scenario.primary_blind" />
            </div>
          </div>
          <div v-if="clientTaxStatus !== 'single'" class="mb-3">
            <label class="form-label">Spouse is Blind</label>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" v-model="scenario.spouse_blind" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Client Can Be Claimed as a Dependent</label>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" v-model="scenario.is_dependent" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="card" >
        <div class="card-body"> 
          <h3 class="card-title">Retirement Income Information</h3> 
          <div class="row mb-3">
            <div class="col-auto">
              <select v-model="newIncome.income_type" class="form-control">
                <option disabled value="">Select income type</option>
                <option
                  v-for="option in incomeTypes"
                  :key="option"
                  :value="option"
                >{{ option.replace(/_/g, ' ') }}</option>
              </select>
            </div>
            <div class="col-auto">
              <button class="btn btn-primary" @click="addIncome">Add Income Product</button>
            </div>
          </div>

          <div v-for="(group, type) in groupedIncome" :key="type" class="mt-5">
            <h5 class="font-semibold text-lg mb-3">{{ type }}</h5>
            <div class="table-responsive">
              <table class="table table-bordered">
                <thead class="thead-light">
                  <tr>
                    <template v-if="type === 'Wages' || type === 'Reverse_Mortgage'">
                      <th>Owner</th>
                      <th>Amount per Month</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'social_security'">
                      <th>Owner</th>
                      <th>Amount at FRA</th>
                      <th>Start Age</th>
                      <th>COLA %</th>
                      <th>Actual Benefit Amount</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Life_Insurance'">
                      <th>Owner</th>
                      <th>Monthly Loan Amount</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Pension'">
                      <th>Owner</th>
                      <th>Monthly Income</th>
                      <th>COLA %</th>
                      <th>Start Age</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Annuity'">
                      <th>Owner</th>
                      <th>Monthly Income</th>
                      <th>% Taxable</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="['Roth_IRA', 'Traditional_IRA', 'Roth_401k', 'Traditional_401k'].includes(type)">
                      <th>Owner</th>
                      <th>Current Balance</th>
                      <th>Monthly Contribution</th>
                      <th>Growth Rate (%)</th>
                      <th>Start Age</th>
                      <th>Monthly Withdrawal</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Brokerage_Account'">
                      <th>Owner</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th colspan="2"></th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Rental_Income'">
                      <th>Owner</th>
                      <th>Monthly Income</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th colspan="1"></th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else>
                      <th v-if="type === 'other_taxable_income'">Title</th>
                      <th>Owner</th>
                      <th>Monthly Amount</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th style="width: 90px;">Action</th>
                    </template>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="income in group" :key="income.id">

                    <!-- Wages / Reverse Mortgage -->
                    <tr v-if="['Wages', 'Reverse_Mortgage'].includes(income.income_type)">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Social Security -->
                    <tr v-else-if="income.income_type === 'social_security'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_at_fra" type="number" class="form-control" placeholder="Amount at FRA" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control" placeholder="Start Age" @change="checkMedicareAdjustment(income)">
                          <option v-for="age in Array.from({ length: 9 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td><input v-model.number="income.cola" type="number" class="form-control" placeholder="COLA %" /></td>
                      <td>{{ calculateSocialSecurityBenefit(income.amount_at_fra, income.start_age) }}</td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Life Insurance -->
                    <tr v-else-if="income.income_type === 'Life_Insurance'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.loan_amount" type="number" class="form-control" placeholder="Monthly Loan" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Pension -->
                    <tr v-else-if="income.income_type === 'Pension'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td><input v-model.number="income.cola" type="number" class="form-control" placeholder="COLA %" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Annuity -->
                    <tr v-else-if="income.income_type === 'Annuity'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td><input v-model.number="income.percent_taxable" type="number" class="form-control" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Retirement Accounts -->
                    <tr v-else-if="['Roth_IRA', 'Traditional_IRA', 'Roth_401k', 'Traditional_401k'].includes(income.income_type)">
                      <td>
                        <select v-model="income.owned_by" class="form-control">
                          <option value="primary">{{ primaryFirstName }}</option>
                          <option value="spouse">{{ spouseFirstName }}</option>
                        </select>
                      </td>
                      <td>
                        <input v-model.number="income.current_balance" type="number" class="form-control" />
                      </td>
                      <td>
                        <input v-model.number="income.monthly_contribution" type="number" class="form-control" />
                      </td>
                      <td>
                        <input v-model.number="income.growth_rate" type="number" class="form-control" />
                      </td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <input v-model.number="income.withdrawal_amount" type="number" class="form-control" placeholder="Monthly Withdrawal" />
                      </td>
                      <td class="text-end" style="width: 90px;">
                        <button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button>
                      </td>
                    </tr>

                    <!-- Brokerage -->
                    <tr v-else-if="income.income_type === 'Brokerage_Account'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td colspan="2"></td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Rental Income -->
                    <tr v-else-if="income.income_type === 'Rental_Income'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td colspan="1"></td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Other Taxable Income -->
                    <tr v-else>
                      <td v-if="type === 'other_taxable_income'"><input v-model="income.title" class="form-control" placeholder="Income Title" /></td>
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                  </template>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Investment Accounts Section -->
    <div class="row" style="margin-top:40px;">
      <div class="card">
        <div class="card-body">
          <h3 class="card-title">Investment Accounts</h3>
          <div class="row mb-3">
            <div class="col-auto">
              <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#investmentModal">
                Add Investment Account
              </button>
            </div>
          </div>

          <div v-for="(group, type) in groupedInvestments" :key="type" class="mt-4">
            <h5 class="font-semibold text-lg mb-3">{{ type }}</h5>
            <div class="table-responsive">
              <table class="table table-bordered">
                <thead class="thead-light">
                  <tr>
                    <th>Owner</th>
                    <th>Investment Name</th>
                    <th>Current Balance</th>
                    <th>Rate of Return</th>
                    <th>Age Start Taking</th>
                    <th>Age Stop Taking</th>
                    <th class="text-center" style="width: 90px;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="investment in group" :key="investment.id">
                    <td>
                      <select v-model="investment.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option value="spouse">{{ spouseFirstName }}</option>
                      </select>
                    </td>
                    <td>
                      <input v-model="investment.income_name" type="text" class="form-control" />
                    </td>
                    <td>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input v-model.number="investment.current_balance" type="number" class="form-control" />
                      </div>
                    </td>
                    <td>
                      <div class="input-group">
                        <input v-model.number="investment.growth_rate" type="number" class="form-control" step="0.01" />
                        <span class="input-group-text">%</span>
                      </div>
                    </td>
                    <td>
                      <input v-model.number="investment.start_age" type="number" class="form-control" />
                    </td>
                    <td>
                      <input v-model.number="investment.end_age" type="number" class="form-control" />
                    </td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-danger" @click="removeInvestmentById(investment.id)">Remove</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

<!-- Medicare Coverage Information Table -->
<div class="row" style="margin-top:40px;">
  <div class="card w-100">
    <div class="card-body">
      <h3 class="card-title">Coverage Information (Cost per Individual)</h3>
      <p class="text-muted">Please choose the types of coverage you would like to have in retirement. Note Part B is mandatory, also the associated costs are per individual.</p>
      <table class="table table-bordered mt-3">
        <thead class="thead-light">
          <tr>
            <th></th>
            <th>Coverage</th>
            <th>Current Base Monthly Premium</th>
            <th>Choose the Expected Inflation Rate</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td></td>
            <td>Medicare Part B</td>
            <td>$185.00</td>
            <td>
              <select class="form-control">
                <option>Average Historical Inflation (7.42%)</option>
                <option>Custom Inflation Rate</option>
              </select>
            </td>
          </tr>
          <tr>
            <td><input type="checkbox" class="form-check-input" checked /></td>
            <td>Medicare Part D</td>
            <td>$0</td>
            <td>
              <select class="form-control">
                <option>Average Historical Inflation (6.73%)</option>
                <option>Custom Inflation Rate</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

    <!-- Submit -->
    <button class="btn btn-primary" @click="submitScenario" style="margin:10px 10px 0px 0px;">Create Scenario</button>
    <button class="btn btn-secondary" @click="router.push(`/clients/${clientId}`)" style="margin-top:10px;">Cancel</button>
</div>

<!-- Medicare Modal -->
<div v-if="showMedicareModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0, 0, 0, 0.5);">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content shadow-lg border-0">
      <div class="modal-header bg-light">
        <h5 class="modal-title">Adjust Medicare Start Age</h5>
        <button type="button" class="btn-close" @click="showMedicareModal = false" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <p>
          You've selected age {{ medicareModalData.suggestedAge }} for
          {{ medicareModalData.isPrimary ? primaryFirstName : spouseFirstName }}'s Social Security benefits,
          but their Medicare start age is different.
        </p>
        <p>Would you like to update their Medicare start age to match?</p>
      </div>
      <div class="modal-footer bg-light">
        <button class="btn btn-secondary" @click="showMedicareModal = false">Cancel</button>
        <button class="btn btn-primary" @click="handleMedicareAdjustment">Yes, Update</button>
      </div>
    </div>
  </div>
</div>

<InvestmentModal 
  :primary-first-name="primaryFirstName" 
  :spouse-first-name="spouseFirstName"
  @save="addInvestment"
/>

</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import InvestmentModal from '../components/InvestmentModal.vue';

const route = useRoute();
const router = useRouter();
const clientId = route.params.id;

const primaryFirstName = ref('Primary');
const spouseFirstName = ref('Spouse');
const clientTaxStatus = ref('single');

const scenario = ref({
  name: '',
  description: '',
  primary_retirement_age: 65,
  primary_medicare_age: 65,
  primary_lifespan: 90,
  spouse_retirement_age: 65,
  spouse_medicare_age: 65,
  spouse_lifespan: 90,
  income: [],
  investments: [],
  model_tax_change: '',
  reduction_2030_ss: false,
  apply_standard_deduction: true,
  primary_blind: false,
  spouse_blind: false,
  is_dependent: false,
  part_b_inflation_rate: '6',
  part_d_inflation_rate: '6',
  primary_state: '',
});

const incomeTypes = [
  'social_security',
  'Pension',
  'Wages',
  'Rental_Income',
  'Other'
];

const newIncome = ref({ income_type: '' });

function addIncome() {
  if (!newIncome.value.income_type) return;
  scenario.value.income.push({
    id: uuidv4(),
    income_type: newIncome.value.income_type,
    owned_by: 'primary',
    start_age: 65,
    end_age: 90,
    current_balance: 0,
    monthly_contribution: 0,
    growth_rate: 0
  });
  newIncome.value.income_type = '';
}

// Remove by id for grouped income
function removeIncomeById(id) {
  scenario.value.income = scenario.value.income.filter(income => income.id !== id);
}

// Group income products by type
const groupedIncome = computed(() => {
  return scenario.value.income.reduce((acc, item) => {
    if (!acc[item.income_type]) acc[item.income_type] = [];
    acc[item.income_type].push(item);
    return acc;
  }, {});
});

// Investment functions
function addInvestment(investmentData) {
  // Convert growth_rate back to percentage for display
  investmentData.growth_rate = investmentData.growth_rate * 100;
  scenario.value.investments.push(investmentData);
}

function removeInvestmentById(id) {
  scenario.value.investments = scenario.value.investments.filter(investment => investment.id !== id);
}

// Group investments by type
const groupedInvestments = computed(() => {
  return scenario.value.investments.reduce((acc, item) => {
    if (!acc[item.income_type]) acc[item.income_type] = [];
    acc[item.income_type].push(item);
    return acc;
  }, {});
});

async function submitScenario() {
  try {
    // Validate scenario name and provide fallback if blank
    if (!scenario.value.name || scenario.value.name.trim() === "") {
      const timestamp = new Date().getTime();
      scenario.value.name = `Scenario ${timestamp}`;
    }

    // Clean and map income sources for API payload
    const incomeSources = scenario.value.income;
    const cleanedIncomeSources = incomeSources.map(row => {
      const sanitized = { ...row };
      // Ensure fields match expected database schema
      sanitized.owned_by = row.owned_by;
      sanitized.income_type = row.income_type;
      sanitized.income_name = row.income_type.replace(/_/g, ' ');
      sanitized.current_asset_balance = row.current_balance;
      sanitized.monthly_amount = row.withdrawal_amount || row.amount_at_fra || 0;
      sanitized.monthly_contribution = row.monthly_contribution || 0;
      sanitized.age_to_begin_withdrawal = row.start_age;
      sanitized.age_to_end_withdrawal = row.end_age;
      sanitized.rate_of_return = row.growth_rate;
      sanitized.cola = row.cola || 0;
      sanitized.exclusion_ratio = row.exclusion_ratio || 0;
      sanitized.tax_rate = row.tax_rate || 0;
      return sanitized;
    });

    // Clean and map investment sources for API payload
    const investments = scenario.value.investments;
    const cleanedInvestments = investments.map(row => {
      const sanitized = { ...row };
      // Ensure fields match expected database schema
      sanitized.owned_by = row.owned_by;
      sanitized.income_type = row.income_type;
      sanitized.income_name = row.income_name;
      sanitized.current_asset_balance = row.current_balance;
      sanitized.monthly_amount = 0; // Calculated withdrawal amount
      sanitized.monthly_contribution = row.monthly_contribution || 0;
      sanitized.age_to_begin_withdrawal = row.start_age;
      sanitized.age_to_end_withdrawal = row.end_age;
      sanitized.rate_of_return = row.growth_rate / 100; // Convert percentage to decimal
      sanitized.cola = 0;
      sanitized.exclusion_ratio = 0;
      sanitized.tax_rate = 0;
      return sanitized;
    });

    // Combine income and investment sources
    const allIncomeSources = [...cleanedIncomeSources, ...cleanedInvestments];

    // Debug log of payload before submission
    const payload = {
      client: clientId,
      name: scenario.value.name,
      description: scenario.value.description,
      primary_retirement_age: scenario.value.primary_retirement_age,
      primary_medicare_age: scenario.value.primary_medicare_age,
      mortality_age: scenario.value.primary_lifespan,
      spouse_retirement_age: scenario.value.spouse_retirement_age,
      spouse_medicare_age: scenario.value.spouse_medicare_age,
      spouse_mortality_age: scenario.value.spouse_lifespan,
      income_sources: allIncomeSources,
      model_tax_change: scenario.value.model_tax_change,
      reduction_2030_ss: scenario.value.reduction_2030_ss,
      apply_standard_deduction: scenario.value.apply_standard_deduction,
      primary_blind: scenario.value.primary_blind,
      spouse_blind: scenario.value.spouse_blind,
      is_dependent: scenario.value.is_dependent,
      part_b_inflation_rate: scenario.value.part_b_inflation_rate,
      part_d_inflation_rate: scenario.value.part_d_inflation_rate,
      primary_state: scenario.value.primary_state,
    };
    console.log("🚀 Payload to submit:", payload);
    const response = await axios.post(
      `http://localhost:8000/api/clients/${clientId}/scenarios/create/`,
      payload
    );
    router.push(`/clients/${clientId}/scenarios/detail/${response.data.id}`);
  } catch (error) {
    //console.log("🚀 income_sources payload:", JSON.parse(JSON.stringify(scenario.value.income)));
    //console.log("🚀 income_sources payload:", scenario.value.income);
    //console.error('❌ Error saving scenario:', error);
    //console.error('❌ Response data:', error.response?.data);
    //console.error('Failed to create scenario:', error);
  }
}

onMounted(async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/clients/${clientId}/`);
    const client = response.data;
    if (!client || !client.first_name) {
      console.warn('Client data missing or incomplete:', client);
    }
    primaryFirstName.value = client.first_name ?? 'Primary';
    spouseFirstName.value = client.spouse?.first_name?.trim() || 'Spouse';
    clientTaxStatus.value = client.tax_status?.toLowerCase() ?? 'single';

    // Check if we're duplicating a scenario
    const duplicateId = route.query.duplicate;
    if (duplicateId) {
      await loadScenarioForDuplication(duplicateId);
    }
  } catch (err) {
    if (err.response && err.response.status === 404) {
      console.error(`Client with ID ${clientId} not found (404).`);
    } else {
      console.error('Failed to load client data:', err);
    }
  }
});

async function loadScenarioForDuplication(scenarioId) {
  try {
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };
    const response = await axios.get(`http://localhost:8000/api/scenarios/${scenarioId}/detail/`, { headers });
    const scenarioData = response.data;
    
    // Prefill the scenario object with data from the duplicated scenario
    scenario.value = {
      ...scenario.value,
      ...scenarioData,
      // Ensure investments array exists even if empty
      investments: scenarioData.investments || []
    };
    
    console.log('Loaded scenario data for duplication:', scenarioData);
  } catch (error) {
    console.error('Failed to load scenario for duplication:', error);
    alert('Failed to load scenario data for duplication. Please try again.');
  }
}

function calculateSocialSecurityBenefit(amountAtFRA, startAge) {
  if (!amountAtFRA || !startAge) return '';
  const FRA = 67;
  const monthlyAdjustment = 0.0067;
  let adjustmentFactor = 1;

  if (startAge < FRA) {
    const monthsEarly = (FRA - startAge) * 12;
    adjustmentFactor -= monthsEarly * monthlyAdjustment;
  } else if (startAge > FRA) {
    const monthsDelayed = (startAge - FRA) * 12;
    adjustmentFactor += monthsDelayed * 0.0067; // Delayed credit
  }

  adjustmentFactor = Math.max(0.7, Math.min(adjustmentFactor, 1.24));
  return (amountAtFRA * adjustmentFactor).toFixed(2);
}

// Medicare Modal State and Functions
const showMedicareModal = ref(false);
const medicareModalData = ref({
  isPrimary: true,
  suggestedAge: 65
});

function handleMedicareAdjustment() {
  const { isPrimary, suggestedAge } = medicareModalData.value;
  if (isPrimary) {
    scenario.value.primary_medicare_age = suggestedAge;
  } else {
    scenario.value.spouse_medicare_age = suggestedAge;
  }
  showMedicareModal.value = false;
}

function checkMedicareAdjustment(income) {
  if (income.income_type !== 'Social Security') return;

  const isPrimary = income.owned_by === 'primary';
  const selectedSSAge = income.start_age;
  const medicareAge = isPrimary ? scenario.value.primary_medicare_age : scenario.value.spouse_medicare_age;

  if (selectedSSAge !== medicareAge) {
    medicareModalData.value = {
      isPrimary,
      suggestedAge: selectedSSAge
    };
    showMedicareModal.value = true;
  }
}
</script>

<style scoped>
.input {
  @apply w-full border border-gray-300 rounded px-3 py-2 mt-1;
}
.textarea {
  @apply w-full border border-gray-300 rounded px-3 py-2 h-24 mt-1;
}
.btn {
  @apply bg-gray-600 text-white px-4 py-2 rounded;
}
.btn-primary {
  @apply bg-blue-600 text-white px-6 py-2 rounded mt-4;
}
</style>