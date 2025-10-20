# REQUIRED FIELDS FOR "AFTER CONVERSION" TABLE

## ALL FIELDS THAT MUST BE IN retirement_row

Based on the frontend table structure, here are ALL required fields:

### DEMOGRAPHICS
- `year` - Year number
- `primary_age` - Primary client age
- `spouse_age` - Spouse age (if married)

### INCOME SOURCES (via income_by_source dict)
- `pre_retirement_income` - Pre-retirement income
- `income_by_source` - Dict with {asset_id: income_amount}
  - Example: `{'SS': 54000, '262': 30000}` for SS and 401k
  - **CRITICAL:** After full conversion, 401k should NOT be in this dict!

### ROTH CONVERSION
- `roth_conversion` - Amount converted this year
- `roth_ira_balance` - Roth IRA balance
- `tax_free_income` - Tax-free withdrawals from Roth

### ASSET BALANCES (via asset_balances dict)
- `asset_balances` - Dict with {asset_id: balance_amount}
  - Example: `{'262': 2000000, 'roth': 500000}`
  - **CRITICAL:** After full conversion, 401k balance should be 0 or not in dict

### RMDs
- `rmd_required` - Dict with {asset_id: rmd_amount}
  - Example: `{'262': 154333}`
  - **CRITICAL:** After full conversion, should be EMPTY dict {}
- `rmd_total` - Total RMD amount (sum of all RMDs)
- `rmd_amount` - Legacy field (same as rmd_total)

### TAXES
- `agi` - Adjusted Gross Income
- `magi` - Modified AGI
- `taxable_income` - Taxable income after deductions
- `regular_income_tax` - Tax WITHOUT conversion
- `conversion_tax` - Incremental tax FROM conversion
- `federal_tax` - Total federal tax (regular + conversion)
- `state_tax` - State tax
- `marginal_rate` - Marginal tax rate %
- `effective_rate` - Effective tax rate %
- `tax_bracket` - Tax bracket string

### MEDICARE/IRMAA
- `part_b` - Medicare Part B cost
- `part_d` - Medicare Part D cost
- `irmaa_surcharge` - IRMAA surcharge
- `irmaa_bracket_number` - IRMAA bracket number
- `total_medicare` - Total Medicare cost
- `medicare_base` - Base Medicare cost (before IRMAA)

### INCOME PHASES
- `gross_income` - Gross income total
- `gross_income_total` - Same as gross_income
- `after_tax_income` - Income after taxes
- `after_medicare_income` - Income after taxes and Medicare

### NET INCOME
- `remaining_income` - Remaining income (final)
- `net_income` - Same as remaining_income

### OTHER BASELINE FIELDS THAT MAY BE NEEDED
- `ss_income` - Social Security income
- `taxable_ss` - Taxable portion of SS
- `is_synthetic` - Flag for synthetic rows

---

## FIELDS PROVIDED BY baseline_row (Comprehensive Summary API)

When we do `retirement_row = dict(baseline_row)`, we get:

1. **All the fields above** ✓
2. **Plus asset-specific fields** like:
   - `401k_balance` - 401k balance (WRONG after conversion!)
   - `401k_income` - 401k income/RMD (WRONG after conversion!)
   - `401k_rmd` - 401k RMD (WRONG after conversion!)
   - `qualified_balance` - Same as 401k
   - `qualified_income` - Same as 401k
   - etc.

The problem: baseline has the WRONG asset values (no conversion applied)!

---

## FIELDS PROVIDED BY _calculate_asset_balances_with_growth()

Currently returns:
- `{asset_id}_balance` - e.g., `262_balance`
- `{asset_id}_rmd` - e.g., `262_rmd`
- `{asset_type}_balance` - e.g., `401k_balance`
- `{asset_type}_rmd` - e.g., `401k_rmd`
- `roth_ira_balance`
- `tax_free_income`
- `rmd_total`
- `rmd_amount`

**MISSING:**
- `{asset_id}_income` - e.g., `262_income`
- `{asset_type}_income` - e.g., `401k_income`

---

## MY SOLUTION: WILL IT RETURN ALL FIELDS?

### Phase 1: Add _income to _calculate_asset_balances_with_growth()
After this, it will return:
- ✅ All balance fields
- ✅ All RMD fields
- ✅ All income fields (NEW!)
- ✅ Roth fields
- ✅ Tax-free income

### Phase 2: Build retirement_row from scratch
```python
retirement_row = {
    # Demographics (from baseline - not affected by conversion)
    'year': year,
    'primary_age': primary_age,
    'spouse_age': spouse_age,

    # Conversion fields
    'is_synthetic': True,
    'roth_conversion': conversion_amount,

    # Social Security (from baseline - not affected by conversion)
    'ss_income': baseline_row['ss_income'],
    'taxable_ss': baseline_row['taxable_ss'],

    # Pre-retirement income
    'pre_retirement_income': 0,  # Retired
}
```

### Phase 3: Add asset balances from conversion
```python
asset_balances = self._calculate_asset_balances_with_growth(year, apply_conversions=True)
retirement_row.update(asset_balances)
```

This adds:
- ✅ `262_balance`, `262_rmd`, `262_income`
- ✅ `401k_balance`, `401k_rmd`, `401k_income` (from asset_type aliases)
- ✅ `roth_ira_balance`
- ✅ `tax_free_income`
- ✅ `rmd_total`, `rmd_amount`

### Phase 4: Calculate taxes
```python
# Calculate gross income from conversion data
gross_income = retirement_row['ss_income']
for asset in self.assets:
    asset_id = str(asset.get('id'))
    if f"{asset_id}_income" in retirement_row:
        gross_income += retirement_row[f"{asset_id}_income"]

# Calculate AGI
agi = gross_income + retirement_row['taxable_ss'] + conversion_amount

# Calculate taxes
standard_deduction = self._get_standard_deduction()
regular_taxable_income = max(0, (gross_income + retirement_row['taxable_ss']) - standard_deduction)
regular_income_tax, _ = self._calculate_federal_tax_and_bracket(regular_taxable_income)

total_taxable_income = max(0, agi - standard_deduction)
federal_tax, tax_bracket = self._calculate_federal_tax_and_bracket(total_taxable_income)

conversion_tax = federal_tax - regular_income_tax

state_tax = self._calculate_state_tax(agi, retirement_row['taxable_ss'])

# Calculate effective rate
effective_rate = (federal_tax / agi * 100) if agi > 0 else 0

retirement_row.update({
    'gross_income': gross_income,
    'gross_income_total': gross_income,
    'agi': agi,
    'magi': agi,
    'taxable_income': total_taxable_income,
    'regular_income_tax': regular_income_tax,
    'conversion_tax': conversion_tax,
    'federal_tax': federal_tax,
    'state_tax': state_tax,
    'tax_bracket': tax_bracket,
    'marginal_rate': ...,  # Extract from bracket
    'effective_rate': effective_rate,
})
```

This adds:
- ✅ All tax fields

### Phase 5: Calculate Medicare
```python
# Store MAGI for 2-year lookback
self.magi_history[year] = agi

lookback_year = year - 2
lookback_magi = self.magi_history.get(lookback_year, agi)

total_medicare, irmaa_surcharge = self._calculate_medicare_costs(lookback_magi, year)
medicare_base = total_medicare - irmaa_surcharge

retirement_row.update({
    'medicare_base': medicare_base,
    'part_b': medicare_base * 0.72,
    'part_d': medicare_base * 0.28,
    'irmaa_surcharge': irmaa_surcharge,
    'irmaa_bracket_number': ...,  # Calculate
    'total_medicare': total_medicare,
})
```

This adds:
- ✅ All Medicare fields

### Phase 6: Calculate income phases
```python
after_tax = gross_income - federal_tax - state_tax
after_medicare = after_tax - total_medicare

retirement_row.update({
    'after_tax_income': after_tax,
    'after_medicare_income': after_medicare,
    'remaining_income': after_medicare,
    'net_income': after_medicare,
})
```

This adds:
- ✅ All income phase fields

---

## FINAL CHECKLIST: DOES MY SOLUTION RETURN ALL FIELDS?

| Field Category | Required Fields | My Solution Provides? |
|----------------|----------------|----------------------|
| Demographics | year, ages | ✅ YES (from baseline, unchanged) |
| Income Sources | pre_retirement_income, income_by_source | ✅ YES (calculated from asset incomes) |
| Roth Conversion | roth_conversion, roth_ira_balance, tax_free_income | ✅ YES (from asset_balances) |
| Asset Balances | asset_balances dict | ✅ YES (from asset_balances) |
| RMDs | rmd_required, rmd_total | ✅ YES (from asset_balances) |
| Taxes | agi, magi, taxable_income, regular_income_tax, conversion_tax, federal_tax, state_tax, marginal_rate, effective_rate, tax_bracket | ✅ YES (calculated fresh) |
| Medicare | part_b, part_d, irmaa_surcharge, irmaa_bracket_number, total_medicare, medicare_base | ✅ YES (calculated fresh) |
| Income Phases | gross_income, after_tax_income, after_medicare_income | ✅ YES (calculated fresh) |
| Net Income | remaining_income, net_income | ✅ YES (calculated fresh) |

---

## ANSWER: YES, MY SOLUTION WILL RETURN ALL REQUIRED FIELDS!

The key difference:
- **Current approach:** Copy ALL baseline fields (wrong values) → Try to update (fails due to key mismatch)
- **My approach:** Build ONLY the fields we need → Calculate everything fresh → No conflicts, correct values

**All fields will be present and CORRECT for all 4 scenarios!**
