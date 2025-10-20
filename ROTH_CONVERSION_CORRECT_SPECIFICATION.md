# ROTH CONVERSION - CORRECT SPECIFICATION FOR ALL 4 SCENARIOS

## THE 4 SCENARIOS

### Scenario 1: Full Conversion in 1 Year
- **Setup:** $2M 401k, convert ALL $2M in year 2025
- **Years to convert:** 1
- **Annual conversion:** $2M

### Scenario 2: Partial Conversion in 1 Year
- **Setup:** $2M 401k, convert $500k in year 2025
- **Years to convert:** 1
- **Annual conversion:** $500k

### Scenario 3: Full Conversion Over Multiple Years
- **Setup:** $2M 401k, convert $200k/year for 10 years
- **Years to convert:** 10
- **Annual conversion:** $200k

### Scenario 4: Partial Conversion Over Multiple Years
- **Setup:** $2M 401k, convert $50k/year for 5 years
- **Years to convert:** 5
- **Annual conversion:** $50k

---

## CORRECT OUTPUT FOR EACH SCENARIO

### SCENARIO 1: Full Conversion in 1 Year ($2M → $0)

#### Year 2025 (Age 64, Conversion Year):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | $0 | Entire $2M converted |
| 401k Income | $0 | No RMD (age < 73, balance = $0) |
| 401k RMD | $0 | No RMD (balance = $0) |
| Roth Balance | $2,000,000 | Received full conversion |
| Roth Income (Tax-Free) | $0 | No withdrawals yet |
| Conversion Amount | $2,000,000 | Full conversion |
| Gross Income | $125,000 | Pre-retirement income only |
| AGI | $2,125,000 | $125k income + $2M conversion |
| Conversion Tax | ~$718,473 | Tax on $2M conversion |

#### Year 2026 (Age 65, Post-Conversion):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | $0 | Still $0 |
| 401k Income | $0 | No RMD (balance = $0) |
| 401k RMD | $0 | No RMD (balance = $0) |
| Roth Balance | $2,060,000 | $2M + 5% growth - $40k withdrawal |
| Roth Income (Tax-Free) | $40,000 | Tax-free withdrawal |
| Conversion Amount | $0 | No conversion this year |
| Gross Income | $54,000 | SS only (no 401k income!) |
| AGI | $54,050 | SS only |

#### Year 2036 (Age 75, 11 years post-conversion):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | $0 | Still $0 |
| 401k Income | $0 | NO RMD! Balance is $0! |
| 401k RMD | $0 | NO RMD! Balance is $0! |
| Roth Balance | ~$2,852,407 | Growing with withdrawals |
| Roth Income (Tax-Free) | $40,000 | Tax-free withdrawal |
| Gross Income | $65,826 | SS only (NO 401k income!) |
| RMD Required | EMPTY | No RMDs on any assets |
| RMD Total | $0 | No RMDs anywhere |

**CRITICAL:** After full conversion, there should be NO 401k income, NO RMDs, EVER!

---

### SCENARIO 2: Partial Conversion in 1 Year ($2M → $1.5M)

#### Year 2025 (Conversion Year):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | $1,590,000 | $2M - $500k conversion, then × 1.06 growth |
| 401k Income | $0 | No RMD (age < 73) |
| 401k RMD | $0 | No RMD (age < 73) |
| Roth Balance | $500,000 | Received partial conversion |
| Conversion Amount | $500,000 | Partial conversion |
| Gross Income | $125,000 | Pre-retirement only |

#### Year 2036 (Age 75):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | ~$3,000,000 | Growing from $1.59M over 11 years |
| 401k Income | ~$117,000 | RMD on $3M (age 75) |
| 401k RMD | ~$117,000 | Required RMD on remaining balance |
| Roth Balance | ~$750,000 | Growing from $500k |
| Gross Income | ~$182,826 | SS + 401k RMD |
| RMD Required | {401k: $117,000} | RMD on unconverted 401k |

**KEY:** RMDs happen on the REMAINING 401k balance!

---

### SCENARIO 3: Full Conversion Over 10 Years ($200k/year)

#### Year 2025 (First conversion year):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | $1,908,000 | ($2M - $200k) × 1.06 |
| 401k Income | $0 | No RMD (age < 73) |
| 401k RMD | $0 | No RMD (age < 73) |
| Roth Balance | $200,000 | First conversion |
| Conversion Amount | $200,000 | Annual conversion |

#### Year 2028 (Age 67, 4th conversion year):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | ~$1,400,000 | Diminishing (4 × $200k converted) |
| 401k Income | $0 | No RMD (age < 73) |
| 401k RMD | $0 | No RMD (age < 73) |
| Roth Balance | ~$920,000 | Accumulating conversions |
| Conversion Amount | $200,000 | Still converting |

#### Year 2031 (Age 70, 7th conversion year):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | ~$700,000 | Still diminishing |
| 401k Income | $0 | No RMD (age < 73) |
| 401k RMD | $0 | No RMD (age < 73) |
| Conversion Amount | $200,000 | Still converting |

#### Year 2034 (Age 73, 10th/LAST conversion year):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | ~$50,000 | Almost fully converted |
| 401k Income | ~$1,900 | FIRST RMD! (age 73, small balance) |
| 401k RMD | ~$1,900 | RMD on remaining $50k |
| Conversion Amount | $200,000 | Last conversion (might exceed balance!) |
| Roth Balance | ~$2,500,000 | Accumulated |

**KEY:** RMDs START when age 73, calculated on REMAINING balance during conversion!

#### Year 2035 (Age 74, post-conversion):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | $0 | Fully converted |
| 401k Income | $0 | No RMD (balance = $0) |
| 401k RMD | $0 | No RMD (balance = $0) |
| Roth Balance | ~$2,700,000 | Growing |

**KEY:** After conversion completes, NO MORE RMDs!

---

### SCENARIO 4: Partial Conversion Over 5 Years ($50k/year from $2M)

#### Year 2025 (First conversion year):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | $2,068,000 | ($2M - $50k) × 1.06 |
| 401k Income | $0 | No RMD (age < 73) |
| Conversion Amount | $50,000 | Small annual conversion |

#### Year 2029 (Age 68, Last conversion year):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | ~$2,150,000 | Still mostly unconverted (growth > conversions) |
| 401k Income | $0 | No RMD (age < 73) |
| Conversion Amount | $50,000 | Last conversion |
| Roth Balance | ~$280,000 | Small accumulated amount |

#### Year 2034 (Age 73, post-conversion):
| Field | Expected Value | Why |
|-------|---------------|-----|
| 401k Balance | ~$2,700,000 | Growing unconverted portion |
| 401k Income | ~$105,000 | RMD on large unconverted balance! |
| 401k RMD | ~$105,000 | Required RMD |
| Conversion Amount | $0 | Conversions ended |
| Roth Balance | ~$380,000 | Small Roth balance |
| Gross Income | ~$168,270 | SS + large 401k RMD |

**KEY:** RMDs happen on the LARGE unconverted portion that remains!

---

## THE CORE PROBLEM

The current code copies `baseline_row` which includes:
- `401k_income` - This is the RMD income from baseline (no conversion)
- `401k_balance` - This is the balance from baseline
- `401k_rmd` - This is the RMD amount from baseline

Then it tries to update with conversion data, but:
- Conversion uses `262_balance` (asset_id)
- Baseline uses `401k_balance` (asset_type)
- **DIFFERENT KEYS = BOTH STAY IN THE DICT!**

The same happens with `_income` and `_rmd` fields!

---

## THE CORRECT APPROACH

### Step 1: DON'T copy baseline_row
Instead, build the retirement row from SCRATCH using conversion data.

### Step 2: Calculate income from conversion balances
- If 401k balance = $0 → 401k income = $0
- If 401k balance > $0 AND age >= 73 → 401k income = RMD
- DON'T use baseline income AT ALL

### Step 3: Use conversion's asset_balances directly
- `_calculate_asset_balances_with_growth(year, apply_conversions=True)`
- This ALREADY returns correct balances and RMDs
- Use this data DIRECTLY, don't merge with baseline

### Step 4: For fields NOT in asset_balances
- SS income: Same as baseline (not affected by conversion)
- Taxes: Recalculate with conversion amount
- Medicare: Recalculate with new AGI
- Everything else: Calculate fresh, don't copy

---

## REQUIRED FIELDS IN CONVERSION DATA

`_calculate_asset_balances_with_growth()` must return:
```python
{
    # Balances (by asset_id)
    '262_balance': 0,           # 401k balance
    'roth_ira_balance': 2000000,  # Roth balance

    # RMDs (by asset_id)
    '262_rmd': 0,               # 401k RMD
    'rmd_total': 0,             # Total RMDs

    # Income (by asset_id) - MUST ADD THIS!
    '262_income': 0,            # Income from this asset (RMD if applicable)

    # Tax-free income
    'tax_free_income': 40000,   # Roth withdrawals
}
```

**CRITICAL ADDITION:** The function must ALSO return `{asset_id}_income` fields!

Currently it returns `_balance` and `_rmd` but NOT `_income`!

The `_income` field should equal:
- If asset generates income (pension, wages): use that
- If asset requires RMD: `_income = _rmd`
- Otherwise: `_income = 0`

---

## IMPLEMENTATION PLAN

### Phase 1: Add income fields to asset_balances return
In `_calculate_asset_balances_with_growth()`:
```python
# After calculating RMD (line 710)
if rmd_for_target_year > 0:
    # Store RMD
    balances[f"{asset_id}_rmd"] = float(rmd_for_target_year)

    # ALSO store as income (RMD becomes income)
    balances[f"{asset_id}_income"] = float(rmd_for_target_year)
else:
    # No RMD = no income from this asset
    balances[f"{asset_id}_income"] = 0
```

### Phase 2: Stop copying baseline_row
Instead of:
```python
retirement_row = dict(baseline_row)  # WRONG!
```

Do:
```python
retirement_row = {
    'year': year,
    'primary_age': age,
    'spouse_age': spouse_age,
    'is_synthetic': True,
    # ... only non-asset fields from baseline
}
```

### Phase 3: Build retirement_row from conversion data
```python
# Get conversion asset data
asset_balances = self._calculate_asset_balances_with_growth(year, apply_conversions=True)

# Merge directly (no conflicts because we started fresh)
retirement_row.update(asset_balances)

# Add SS income (not affected by conversion)
retirement_row['ss_income'] = baseline_row['ss_income']
retirement_row['taxable_ss'] = baseline_row['taxable_ss']

# Calculate taxes with conversion
# ... tax calculations ...

# Calculate Medicare with new AGI
# ... Medicare calculations ...
```

This ensures:
- ✅ 401k balance comes from conversion data (correct)
- ✅ 401k RMD comes from conversion data (correct)
- ✅ 401k income comes from conversion data (correct)
- ✅ No baseline pollution
- ✅ Works for all 4 scenarios

---

## VERIFICATION CHECKLIST

After implementation, verify each scenario:

### Scenario 1 (Full 1-year):
- [ ] Year 2025: 401k balance = $0
- [ ] Year 2026+: 401k income = $0
- [ ] Year 2026+: RMD total = $0
- [ ] Year 2036: No 401k in income_by_source

### Scenario 2 (Partial 1-year):
- [ ] Year 2025: 401k balance = $1.59M
- [ ] Year 2036: 401k income = RMD on remaining
- [ ] Year 2036: RMD shows in RMD Required

### Scenario 3 (Full multi-year):
- [ ] Years 2025-2033: Diminishing 401k balance
- [ ] Year 2034: Small RMD on remaining balance
- [ ] Year 2035+: 401k balance = $0, income = $0

### Scenario 4 (Partial multi-year):
- [ ] Years 2025-2029: Slightly reduced balance
- [ ] Year 2034+: Large RMD on unconverted portion
- [ ] RMD continues indefinitely

---

**END OF SPECIFICATION**
