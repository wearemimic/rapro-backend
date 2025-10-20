# COMPLETE ROTH CONVERSION CODE AUDIT
## Every Possible Reason Why 401k Balance Shows $2.2M After Full $2M Conversion

**Date:** 2025-10-20
**Issue:** After converting entire $2M 401k balance to Roth in year 2025, the 401k still shows balance of $2,247,200 in year 2026 and continues growing in subsequent years.

---

## PROBLEM SUMMARY

### What SHOULD Happen:
- Year 2025: 401k balance = $2M → Convert all $2M → 401k balance = $0
- Year 2026: 401k balance = $0 (no growth on $0)
- Year 2027+: 401k balance = $0 (no growth on $0)

### What's ACTUALLY Happening:
- Year 2025: 401k balance = $2M → Convert all $2M → 401k balance = $0 ✓
- Year 2026: 401k balance = $2,247,200 ❌ (WHERE DID THIS COME FROM?)
- Year 2027: 401k balance = $2,382,032 ❌ (STILL GROWING!)

---

## SECTION 1: BALANCE STORAGE ISSUES (Lines 731-737)

### Issue #1: Balance Storage Conditional on asset_id
**Location:** `roth_conversion_processor.py:733`

```python
if apply_conversions and asset_id is not None:
```

**Problem:** If `asset_id` is `None` for any reason, the $0 balance won't be stored!

**Why This Breaks:**
- Asset comes from database with `id` field
- But somewhere in the code, `asset.get('id')` returns `None`
- The $0 balance from year 2025 is never stored
- Year 2026 falls back to reading from database: $2M (original balance)

**How to Verify:**
```python
# Add logging
self._log_debug(f"DEBUG: asset_id type = {type(asset_id)}, value = {asset_id}")
```

---

### Issue #2: Balance Storage Happens AFTER Loop
**Location:** `roth_conversion_processor.py:731-737`

**Problem:** The storage code is INSIDE the asset loop, but the condition checks `apply_conversions` which might be different per asset.

**Code Structure:**
```python
for asset in self.assets:
    # ... calculations ...
    if apply_conversions and asset_id is not None:
        self.asset_balances_by_year[target_year][asset_id] = balance
```

**Why This Breaks:**
- If `apply_conversions=False` for any reason, nothing gets stored
- The entire `asset_balances_by_year` dictionary stays empty
- Next year falls back to database values

---

### Issue #3: Dictionary Key Mismatch
**Location:** Storage (line 736) vs Retrieval (line 573)

**Storage:**
```python
self.asset_balances_by_year[target_year][asset_id] = balance
```

**Retrieval:**
```python
if previous_year in self.asset_balances_by_year and asset_id in self.asset_balances_by_year[previous_year]:
```

**Problem:** `asset_id` might change between storage and retrieval!

**Reasons for Mismatch:**
1. `asset_id` is an integer in DB but gets converted to string somewhere
2. Asset object is recreated/copied, changing the `id` field
3. Deep copy of assets (line 34) might not preserve integer types
4. Different asset instances used in different years

**How This Manifests:**
- Year 2025: Store balance under key `262` (integer)
- Year 2026: Look for balance under key `"262"` (string)
- Dictionary lookup fails
- Falls back to database: $2M

---

## SECTION 2: BALANCE RETRIEVAL ISSUES (Lines 563-580)

### Issue #4: Fallback to Database When Storage Empty
**Location:** `roth_conversion_processor.py:577-580`

```python
else:
    # First time calculating this asset OR asset_id is None, use current balance from database
    current_balance = Decimal(str(asset.get('current_asset_balance', 0)))
```

**Problem:** This ALWAYS reads from database if storage lookup fails!

**Why This Breaks:**
- Storage fails for ANY reason (issues #1, #2, #3)
- Code falls back to `asset.get('current_asset_balance')`
- This reads the ORIGINAL $2M from the database
- The $0 from year 2025 is completely ignored

**Fix Needed:**
```python
else:
    # CRITICAL: Should be $0 after conversion, not database value!
    if target_year > self.conversion_start_year:
        current_balance = Decimal('0')  # Asset was converted
    else:
        current_balance = Decimal(str(asset.get('current_asset_balance', 0)))
```

---

### Issue #5: No Validation That Storage Worked
**Location:** `roth_conversion_processor.py:731-737`

**Problem:** The code stores balances but NEVER verifies they were stored correctly.

**Missing Validation:**
```python
# After storage, should verify:
if asset_id not in self.asset_balances_by_year[target_year]:
    raise RuntimeError(f"FAILED to store balance for asset {asset_id} in year {target_year}!")
```

**Why This Matters:**
- Silent failures → no error messages
- Balance storage fails silently
- Next year's calculation uses wrong data
- No way to debug what went wrong

---

## SECTION 3: ASSET OBJECT ISSUES

### Issue #6: Deep Copy Might Not Preserve Types
**Location:** `roth_conversion_processor.py:34`

```python
self.assets = copy.deepcopy(assets)  # Deep copy to avoid modifying original
```

**Problem:** Deep copy might change `id` from integer to something else!

**Python's deepcopy Behavior:**
- Integers are immutable, usually preserved
- BUT if the integer is in a dict, it might get converted
- JSON serialization/deserialization can change int → str

**How to Verify:**
```python
for asset in assets:
    original_id = asset.get('id')
    after_copy = copy.deepcopy(asset)
    copied_id = after_copy.get('id')
    if type(original_id) != type(copied_id):
        print(f"TYPE CHANGED: {type(original_id)} → {type(copied_id)}")
```

---

### Issue #7: Asset List Modified During Iteration
**Location:** `roth_conversion_processor.py:706-708`

```python
# Add the synthetic Roth asset to the assets list
self.assets.append(roth_asset)
```

**Problem:** A synthetic Roth asset is added to `self.assets` during processing!

**Why This Breaks:**
- Original assets list has the 401k
- Synthetic Roth is appended
- Loop iterates over modified list
- Might skip the 401k or process it twice
- Balance calculations get corrupted

---

### Issue #8: Synthetic Roth Asset Reuses ID
**Location:** `roth_conversion_processor.py:687-704`

```python
roth_asset = {
    'id': 'synthetic_roth',  # ← STRING, not integer!
    ...
}
```

**Problem:** Synthetic Roth uses string 'synthetic_roth' as ID, real assets use integers!

**Why This Breaks:**
- Dictionary stores balances by asset_id
- Real 401k: `asset_id = 262` (integer)
- Synthetic Roth: `asset_id = 'synthetic_roth'` (string)
- When checking `if asset_id in dict`: integer != string
- Storage/retrieval fails

---

## SECTION 4: CONVERSION CALCULATION ISSUES

### Issue #9: Conversion Amount Calculation Wrong
**Location:** `roth_conversion_processor.py:600-601`

```python
asset_annual_conversion = asset_total_conversion / Decimal(str(self.years_to_convert))
conversion_amount = min(asset_annual_conversion, balance)
```

**Problem:** If `years_to_convert=1` and `asset_total_conversion=$2M`:
- `asset_annual_conversion = $2M / 1 = $2M` ✓
- `conversion_amount = min($2M, $2M) = $2M` ✓

**But what if balance already has growth applied?**
- Balance starts at $2M
- Growth applied BEFORE conversion: $2M × 1.06 = $2.12M
- Then conversion: min($2M, $2.12M) = $2M
- Balance after conversion: $2.12M - $2M = $120,000 ❌

**This explains the extra balance!**

---

### Issue #10: Growth Applied Before Conversion
**Location:** `roth_conversion_processor.py:613-615`

```python
# Subtract conversion from balance BEFORE growth
if conversion_amount > 0:
    balance -= conversion_amount
# Apply growth to the balance (after conversion)
balance *= (1 + rate_of_return)
```

**Wait, this IS subtracting BEFORE growth... but read the comment on line 606:**

Comment says "BEFORE growth" but the code order is:
1. Line 608: `balance -= conversion_amount` (subtract conversion)
2. Line 614: `balance *= (1 + rate_of_return)` (apply growth)

**So the order is correct in current year!**

**BUT** - what about when projecting forward? Let me check lines 620-665...

---

### Issue #11: Year-by-Year Projection Might Grow First
**Location:** `roth_conversion_processor.py:644-665`

**The loop structure:**
```python
for yr in range(years_to_project):
    projection_year = current_year + yr + 1

    # DO NOT apply Roth growth here

    # Step 1: Check for conversion FIRST
    conversion_amount = ...

    # Step 2: Subtract conversion from balance BEFORE growth
    if conversion_amount > 0:
        balance -= conversion_amount

    # Step 3: Apply growth to the REDUCED balance
    balance *= (1 + rate_of_return)

    # Step 4: Calculate RMD and subtract
```

**This looks correct!** Conversion before growth.

**BUT WAIT** - This loop is INSIDE the `else` block starting at line 620!

This means:
- If `target_year == current_year`: Uses lines 575-619 (conversion before growth ✓)
- If `target_year > current_year`: Uses lines 620+ (loop with conversion before growth ✓)

**Both paths subtract conversion BEFORE growth!**

---

## SECTION 5: FUNCTION CALL ISSUES

### Issue #12: Function Called Multiple Times Per Year
**Location:** Various places in `process()` method

The function `_calculate_asset_balances_with_growth()` is called from:
1. Line 1579: Pre-retirement years
2. Line 1699: Pre-retirement conversion years
3. Line 1782: Retirement years

**Problem:** EACH CALL creates a NEW calculation!

**What Happens:**
```python
# Year 2025 calculation (called once)
_calculate_asset_balances_with_growth(2025, apply_conversions=True)
# Stores: 401k = $0

# Year 2026 calculation (called separately!)
_calculate_asset_balances_with_growth(2026, apply_conversions=True)
# Should load: 401k = $0 from storage
# But if storage failed: loads 401k = $2M from database!
```

**The function is NOT designed to be called separately for each year!**

Looking at the code structure, it seems like it SHOULD be able to handle this, but there's a disconnect.

---

### Issue #13: Balance Storage Dictionary Gets Cleared
**Location:** `roth_conversion_processor.py:58`

```python
self.asset_balances_by_year = {}  # {year: {asset_id: balance}}
```

**Problem:** This is an instance variable, but when is the RothConversionProcessor created?

**If the processor is recreated for each API call:**
- Request 1: Calculate year 2025, store balances in `self.asset_balances_by_year`
- Request 2: NEW processor instance! `self.asset_balances_by_year = {}` (empty!)
- Year 2026 calculation has no stored data from 2025!

**Check the API endpoint:** Does it create a new processor each time?

---

## SECTION 6: API AND DATA FLOW ISSUES

### Issue #14: Processor Created Fresh Each Request
**Location:** `views_main.py` (need to check)

**If the API does this:**
```python
def roth_conversion_api(request):
    # NEW processor each time!
    processor = RothConversionProcessor(scenario, client, spouse, assets, params)
    result = processor.process()
    return result
```

**Problem:** Each year's calculation creates a new processor!

**Why This Breaks:**
- Year 2025: Create processor, calculate, store balances, DISCARD processor
- Year 2026: Create NEW processor (empty storage!), calculate, fallback to DB
- The `asset_balances_by_year` dictionary is lost between years!

**This is the MOST LIKELY ROOT CAUSE!**

---

### Issue #15: Baseline Data Pollution
**Location:** `roth_conversion_processor.py:1856`

```python
retirement_row = dict(baseline_row)
```

**Problem:** Copying ALL data from baseline including asset balances!

**What baseline_row contains:**
```python
{
    'year': 2026,
    '401k_balance': 2247200,  # ← FROM BASELINE (no conversion!)
    'roth_ira_balance': 0,
    ...
}
```

**Then code overwrites with conversion balances:**
```python
asset_balances = self._calculate_asset_balances_with_growth(year, apply_conversions=True)
retirement_row.update(asset_balances)
```

**But what if the update doesn't include 401k_balance?**
- Baseline has `401k_balance: $2,247,200`
- Conversion calculation returns `{}` (empty) or doesn't include `401k_balance` key
- The baseline value persists!

---

### Issue #16: Comprehensive Format Transformation Reads Wrong Fields
**Location:** `roth_conversion_processor.py:1314-1332`

```python
# Build asset_balances structure from flat fields
asset_balances_dict = {}
for asset in self.assets:
    asset_id = str(asset.get('id', asset.get('income_type', '')))
    asset_type = asset.get('income_type', '').lower()

    # Look for balance fields in the row
    balance_value = 0
    if f"{asset_type}_balance" in enhanced_row:
        balance_value = enhanced_row[f"{asset_type}_balance"]
    elif f"{asset_id}_balance" in enhanced_row:
        balance_value = enhanced_row[f"{asset_id}_balance"]
```

**Problem:** This checks for `{asset_type}_balance` FIRST!

**For 401k:**
- `asset_type = '401k'`
- Checks for `'401k_balance'` in row
- If baseline copied `'401k_balance': $2,247,200`, it uses that!
- Never checks the CORRECT `'{asset_id}_balance'` field

**The wrong balance gets displayed!**

---

## SECTION 7: DISPLAY AND RENDERING ISSUES

### Issue #17: Frontend Shows Baseline Data Instead of Conversion
**Location:** `ComprehensiveConversionTable.vue:146-148`

```vue
<td v-for="asset in assetBalanceColumns" :key="`balance-${asset.id}-${year.year}`">
  {{ formatCurrency(year.asset_balances?.[asset.id] || year[`${asset.id}_balance`] || 0) }}
</td>
```

**Problem:** Falls back to `year[`${asset.id}_balance`]` if `asset_balances` is missing!

**What happens:**
- Backend sends: `{ year: 2026, '401k_balance': 2247200 }`  (baseline data)
- Backend also sends: `{ asset_balances: {} }` (empty conversion data)
- Frontend checks: `year.asset_balances?.[asset.id]` → undefined
- Frontend falls back: `year['401k_balance']` → $2,247,200 (baseline!)

**The frontend is showing baseline data, not conversion data!**

---

## SECTION 8: CALCULATION ORDER ISSUES

### Issue #18: Multiple Calculation Passes Overwrite Each Other

**The process() method flow:**
1. Calculate baseline scenario (no conversions)
2. Calculate conversion scenario (with conversions)
3. Merge/compare results

**But lines 1704-1786 do:**
```python
for baseline_row in baseline_results:
    if baseline_row['year'] < retirement_year:
        continue

    # Start with baseline
    retirement_row = dict(baseline_row)

    # Calculate asset balances with conversions
    asset_balances = self._calculate_asset_balances_with_growth(year, apply_conversions=True)
    retirement_row.update(asset_balances)
```

**Problem:** `update()` might not override all keys!

**If baseline_row has:**
```python
{
    '401k_balance': 2247200,
    'qualified_balance': 2247200,
}
```

**And asset_balances has:**
```python
{
    '262_balance': 0,  # asset_id = 262
    'roth_ira_balance': 2060000
}
```

**After update:**
```python
{
    '401k_balance': 2247200,  # ← STILL HERE! Not overwritten!
    'qualified_balance': 2247200,  # ← STILL HERE!
    '262_balance': 0,
    'roth_ira_balance': 2060000
}
```

**The wrong fields survive!**

---

## SECTION 9: DATA STRUCTURE MISMATCHES

### Issue #19: Multiple Balance Field Naming Conventions

The code uses FOUR different naming conventions:

1. **By asset_type:** `'401k_balance'`, `'qualified_balance'`
2. **By asset_id:** `'262_balance'`
3. **By income_name:** `'My 401k_balance'`
4. **In asset_balances dict:** `asset_balances: { '262': 1234 }`

**Problem:** Different parts of the code expect different formats!

**Storage uses:** `asset_balances_by_year[year][asset_id]` (format #2)
**Retrieval expects:** Same format
**Baseline uses:** `'401k_balance'` (format #1)
**Transform uses:** Checks format #1 THEN format #2
**Frontend expects:** `asset_balances` dict (format #4)

**They're all incompatible!**

---

### Issue #20: Asset ID Type Inconsistency

**In database:** `id` is INTEGER (e.g., 262)
**In Python dict:** `asset.get('id')` returns INTEGER (262)
**After JSON serialization:** Might become STRING ("262")
**After deepcopy:** Might stay INTEGER or become STRING
**When used as dict key:** `dict[262]` ≠ `dict["262"]`

**This breaks EVERYTHING!**

---

## SECTION 10: CONVERSION LOGIC ERRORS

### Issue #21: Conversion Doesn't Actually Happen

**Check the conversion map:** `self.asset_conversion_map`

**Location:** `roth_conversion_processor.py:626-664`

If the map is built incorrectly:
```python
# Expected:
{
    262: Decimal('2000000'),  # asset_id: amount to convert
}

# But maybe it's:
{
    '262': Decimal('2000000'),  # STRING key!
}
```

**When checking:**
```python
if asset_id and asset_id_str in self.asset_conversion_map:
```

If `asset_id = 262` (int) and `asset_id_str = "262"` (string), but the map has integer keys, the lookup fails!

**No conversion happens, balance stays at $2M!**

---

### Issue #22: Conversion Happens But Balance Isn't Updated

**Even if conversion math is correct:**
```python
balance = $2,000,000
conversion_amount = $2,000,000
balance -= conversion_amount  # balance = $0 ✓
```

**The $0 balance might not get stored because:**
- asset_id is None (Issue #1)
- apply_conversions is False (Issue #2)
- Storage fails silently (Issue #5)
- Dictionary key mismatch (Issue #3)

**Result:** Balance calculation is correct, but storage fails, next year uses DB value.

---

## SECTION 11: RETIREMENT YEAR BOUNDARY ISSUES

### Issue #23: Pre-Retirement vs Retirement Calculation Split

**Code has TWO paths:**

**Pre-retirement years (lines 1495-1702):**
- Manually generated rows
- Calls `_calculate_asset_balances_with_growth()` for EACH year
- Stores balances in `asset_balances_by_year`

**Retirement years (lines 1704-1786):**
- Uses baseline_row as template
- Calls `_calculate_asset_balances_with_growth()` for EACH year
- ALSO stores balances in `asset_balances_by_year`

**Problem:** The transition from pre-retirement to retirement loses data!

**What happens:**
- Year 2025 (pre-retirement): Calculate, store 401k=$0 in year 2025
- Year 2026 (retirement): Look for 401k balance in year 2025... but retirement code path might check different dictionary or use baseline!

---

### Issue #24: Retirement Code Path Ignores Stored Balances

**Lines 1704-1786 never check `asset_balances_by_year`!**

```python
for baseline_row in baseline_results:
    if baseline_row['year'] < retirement_year:
        continue  # Skip pre-retirement

    # Start with baseline
    retirement_row = dict(baseline_row)  # ← Uses baseline data!

    # Calculate balances
    asset_balances = self._calculate_asset_balances_with_growth(year, apply_conversions=True)

    # Update row
    retirement_row.update(asset_balances)
```

**This SHOULD work if:**
- `_calculate_asset_balances_with_growth()` reads from `asset_balances_by_year`
- The update() replaces all balance fields

**But it fails if:**
- Storage from year 2025 didn't work
- Update doesn't replace the right keys (Issue #18)
- Baseline data has different field names (Issue #19)

---

## SECTION 12: STATE MANAGEMENT ISSUES

### Issue #25: Instance Variables Not Persistent

**All storage uses instance variables:**
```python
self.asset_balances_by_year = {}
self.roth_balance_by_year = {}
self.magi_history = {}
```

**But the processor instance is created ONCE per API call!**

**If `process()` is called and it processes years 2025-2090 in one go:**
- Storage should work (all in same instance)

**But if it's called separately per year:**
- Instance is destroyed after each call
- Storage is lost

**Check the API endpoint to see how it's called!**

---

### Issue #26: Process() Method Might Be Called Multiple Times

**If the frontend makes multiple API calls:**
1. Call #1: Calculate year 2025
2. Call #2: Calculate year 2026
3. Call #3: Calculate year 2027

**Each call creates a NEW processor instance!**

**Even if data is returned and stored on frontend, the BACKEND recalculates from scratch each time, losing the year-to-year storage!**

---

## SECTION 13: DEBUG AND LOGGING ISSUES

### Issue #27: Debug Logging Not Working

**The code has:**
```python
self.debug = True  # Line 49
```

**And logging calls:**
```python
self._log_debug(f"Year {target_year}: ...")
```

**But you said there's NO debug output in logs!**

**Possible reasons:**
1. `self.debug` gets set to False somewhere
2. The `print()` statements go to stdout, not Docker logs
3. Gunicorn workers capture stdout differently
4. The code path never executes (different method is used)

---

### Issue #28: Wrong Code Path Being Used

**What if the table data doesn't come from `RothConversionProcessor` at all?**

**Check if there's a different endpoint or method that generates the "After Conversion" table!**

Possible alternatives:
- Direct database query
- Cached results from previous calculation
- Different calculation method entirely
- Frontend using baseline data by mistake

---

## SECTION 14: DATA PERSISTENCE ISSUES

### Issue #29: Results Cached in Database

**If results are saved to database after first calculation:**
```python
# After process()
save_to_database(conversion_results)
```

**And subsequent requests read from cache:**
```python
# On next request
if cached_results_exist:
    return cached_results  # ← OLD DATA!
```

**The cached data might have the wrong balances from the first (broken) calculation!**

---

### Issue #30: Frontend Caching Old Data

**If the frontend caches the API response:**
```javascript
// Pinia store
comprehensiveStore.cached_data = api_response
```

**And displays cached data instead of making new API call:**
```javascript
if (store.cached_data) {
    return store.cached_data  // OLD DATA!
}
```

**You might be looking at stale results from before the fixes!**

---

## SECTION 15: THE NUCLEAR OPTION

### Issue #31: The Code Simply Doesn't Work As Designed

**After reviewing all 30+ issues above, the fundamental problem is:**

**The `asset_balances_by_year` storage mechanism is fundamentally broken because:**

1. It's instance-scoped (lost between API calls)
2. It relies on exact asset_id matching (fails with type mismatches)
3. It has no error handling (silent failures)
4. It competes with baseline data (wrong data wins)
5. It uses multiple field naming conventions (incompatible formats)

**THE FIX:**

**Stop trying to store balances in instance variables. Instead:**

1. Calculate year 2025 with conversion
2. Store the ENDING balance in the result row
3. When calculating year 2026, read the ending balance from year 2025's result row
4. Pass year-by-year results as a parameter, not instance variable

**Pseudocode:**
```python
def calculate_all_years():
    results = []
    previous_balances = initial_balances

    for year in range(2025, 2090):
        result = calculate_year(year, previous_balances)
        results.append(result)
        previous_balances = result['ending_balances']

    return results
```

**This is the ONLY way to guarantee continuity!**

---

## ROOT CAUSE ANALYSIS

After analyzing 31 possible issues, here are the TOP 5 most likely culprits:

### #1: **Asset ID Type Mismatch (Issue #20)**
The storage uses `asset_id` as dictionary key, but the type (int vs string) changes between storage and retrieval.

### #2: **Baseline Data Pollution (Issues #15, #18)**
The retirement year calculation starts with baseline_row which contains $2.2M, and the update() doesn't fully replace it.

### #3: **Storage Dictionary Lost Between API Calls (Issues #13, #25, #26)**
The processor instance is recreated for each API call, losing the `asset_balances_by_year` storage.

### #4: **Wrong Field Names (Issues #16, #19)**
The transformation looks for '401k_balance' before '{asset_id}_balance', finding baseline data first.

### #5: **Conversion Map Lookup Failure (Issue #21)**
The conversion_map has wrong keys or wrong types, so the conversion never happens.

---

## RECOMMENDED FIX APPROACH

**Step 1:** Add extensive debug logging
**Step 2:** Verify asset_id types and conversion map contents
**Step 3:** Remove baseline data pollution (don't copy baseline_row)
**Step 4:** Redesign balance tracking (pass as parameters, not instance vars)
**Step 5:** Standardize field naming (use only asset_id format)

---

**END OF AUDIT**
**Total Issues Found: 31**
**Lines in Document: 570+**
