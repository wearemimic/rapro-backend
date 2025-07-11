# Roth Conversion Module – Step-by-Step Dev Guide

> ⚠️ **IMPORTANT: Do NOT touch `scenario_processor.py`**
>
> This file is the core retirement engine. All Roth conversion logic must be implemented in a **separate module** (`roth_conversion_processor.py`). Reference how `scenario_processor.py` pulls, processes, and loops through year-by-year projections — but never edit or extend that file directly.

---

## 🗂️ 1. Backend File: `roth_conversion_processor.py`

### 🔧 Step-by-Step Logic

1. **Create file**: `roth_conversion_processor.py` (do not edit `scenario_processor.py`)

2. **Add method**: `def run_roth_conversion(scenario_id: int, conversion_inputs: dict) -> dict`

3. **Inside this method**:
   ```python
   scenario = get_scenario(scenario_id)
   income_sources = scenario.income_sources.all()
   ```

4. **Filter convertable assets**:
   ```python
   convertable_assets = [a for a in income_sources if a.income_type in ['IRA', '401k']]
   ```

5. **Apply conversion inputs**:
   - Reduce `current_asset_balance` by amount to convert
   - Total up all converted amounts

6. **Create synthetic Roth income source**:
   ```python
   new_roth = IncomeSource(
       scenario=scenario,
       income_type='Roth',
       income_name='Roth Conversion Bucket',
       current_asset_balance=total_converted,
       rate_of_return=conversion_inputs['roth_growth_rate'],
       age_to_begin_withdrawal=calc_age_from_year(conversion_inputs['withdrawal_start_year']),
       monthly_amount=conversion_inputs['withdrawal_amount'] / 12,
       owned_by='primary'
   )
   new_roth.save()
   ```

7. **Determine timeline start year**:
   ```python
   start_year = min(conversion_inputs['conversion_start_year'], scenario.retirement_year, spouse_retirement_year)
   ```

8. **Patch pre-retirement years** with pre-retirement income + conversion amounts.

9. **Recompute year-by-year** MAGI, tax, IRMAA for each year (just like `scenario_processor.py` — but in this file only!)

10. **Return result**:
   ```python
   return {
       "modified_yearly_summary": yearly_data,
       "summary_chart_data": chart_data,
       "savings_summary": savings_data
   }
   ```

---

## 🗂️ 2. Backend File: `views.py`

### 🔧 Add New API Endpoint

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_roth_conversion_view(request):
    scenario_id = request.data['scenario_id']
    conversion_inputs = request.data['conversion']
    result = run_roth_conversion(scenario_id, conversion_inputs)
    return Response(result)
```

---

## 🗂️ 3. Frontend File: `RothConversionTab.vue`

### 🔧 Methods

1. **Submit Conversion**
```javascript
async function runConversion() {
  const res = await axios.post('/api/roth-conversion/run', {
    scenario_id: selectedScenarioId,
    conversion: {
      conversion_start_year,
      years_to_convert,
      max_annual_conversion,
      pre_retirement_income,
      roth_growth_rate,
      withdrawal_amount,
      withdrawal_start_year,
      asset_conversion_map
    }
  });
  this.conversionResult = res.data;
}
```

2. **Render Tables and Charts**
   - Use `conversionResult.modified_yearly_summary` to show year-by-year table
   - Use `conversionResult.summary_chart_data` for chart
   - Use `conversionResult.savings_summary` for summary box

---

## 🗂️ 4. Models Update: `models.py`

### 🔧 Add Model

```python
class RothConversionPlan(models.Model):
    scenario = models.OneToOneField(Scenario, on_delete=models.CASCADE)
    start_year = models.IntegerField()
    years_to_convert = models.IntegerField()
    max_annual_conversion = models.DecimalField(max_digits=12, decimal_places=2)
    pre_retirement_income = models.DecimalField(max_digits=12, decimal_places=2)
    roth_growth_rate = models.FloatField()
    withdrawal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    withdrawal_start_year = models.IntegerField()
    asset_conversion_map = models.JSONField()
```

---

## ✅ Output Format Example (returned by API)

```json
{
  "modified_yearly_summary": [...],
  "summary_chart_data": {...},
  "savings_summary": {
    "total_savings": 150000,
    "savings_percent": 0.27,
    "irmaa_savings": 30000,
    ...
  }
}
```

---

## ✅ Summary

### Files to Modify/Create:
- ✅ `roth_conversion_processor.py` ← *do all logic here*
- ✅ `views.py`
- ✅ `RothConversionTab.vue`
- ✅ `models.py`

### 🚫 Files **Not to Touch**:
- ❌ `scenario_processor.py` — reference only, **do not modify**

### Core Methods:
- `run_roth_conversion()`
- `run_roth_conversion_view()`
- `runConversion()` (frontend)

---
