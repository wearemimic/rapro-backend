# Medicare Premium Historical Analysis

## Medicare Part B Premium History (2006-2025)

| Year | Monthly Premium | $ Change | % Change | Notes |
|------|----------------|----------|----------|-------|
| 2006 | $88.50 | - | - | Base year for analysis |
| 2007 | $93.50 | +$5.00 | +5.65% | |
| 2008 | $96.40 | +$2.90 | +3.10% | |
| 2009 | $96.40 | $0.00 | 0.00% | No increase |
| 2010 | $110.50 | +$14.10 | +14.63% | Large increase |
| 2011 | $115.40 | +$4.90 | +4.43% | |
| 2012 | $99.90 | -$15.50 | -13.43% | **Decrease** |
| 2013 | $104.90 | +$5.00 | +5.01% | |
| 2014 | $104.90 | $0.00 | 0.00% | No increase |
| 2015 | $104.90 | $0.00 | 0.00% | No increase |
| 2016 | $121.80 | +$16.90 | +16.11% | Large increase |
| 2017 | $134.00 | +$12.20 | +10.02% | |
| 2018 | $134.00 | $0.00 | 0.00% | No increase |
| 2019 | $135.50 | +$1.50 | +1.12% | |
| 2020 | $144.60 | +$9.10 | +6.72% | |
| 2021 | $148.50 | +$3.90 | +2.70% | |
| 2022 | $170.10 | +$21.60 | +14.55% | Large increase |
| 2023 | $164.90 | -$5.20 | -3.06% | **Decrease** |
| 2024 | $174.70 | +$9.80 | +5.94% | |
| 2025 | $185.00 | +$10.30 | +5.90% | |

### Part B Statistical Analysis

**Period Analysis:**
- **1 Year (2024-2025)**: 5.90% ✓ Matches our CSV
- **5 Years (2020-2025)**: 
  - CAGR = ((185.00/144.60)^(1/5)) - 1 = 5.05%
  - Average annual increase = 5.57%
  - **Our CSV shows 6.8% - may be HIGH**
  
- **10 Years (2015-2025)**:
  - CAGR = ((185.00/104.90)^(1/10)) - 1 = 5.84%
  - **Our CSV shows 4.9% - may be LOW**
  
- **19 Years (2006-2025)**:
  - CAGR = ((185.00/88.50)^(1/19)) - 1 = 3.96%
  - **Our CSV shows 4.3% - close, reasonable**

---

## Medicare Part D Premium History (2006-2025)

| Year | Avg Monthly Premium | $ Change | % Change | Notes |
|------|-------------------|----------|----------|-------|
| 2006 | $25.93 | - | - | Program inception |
| 2007 | $27.35 | +$1.42 | +5.48% | |
| 2008 | $28.50 | +$1.15 | +4.20% | |
| 2009 | $30.20 | +$1.70 | +5.96% | |
| 2010 | $32.34 | +$2.14 | +7.09% | |
| 2011 | $32.34 | $0.00 | 0.00% | No increase |
| 2012 | $33.19 | +$0.85 | +2.63% | |
| 2013 | $38.95 | +$5.76 | +17.36% | Large increase |
| 2014 | $37.90 | -$1.05 | -2.70% | **Decrease** |
| 2015 | $37.02 | -$0.88 | -2.32% | **Decrease** |
| 2016 | $34.10 | -$2.92 | -7.89% | **Decrease** |
| 2017 | $35.63 | +$1.53 | +4.49% | |
| 2018 | $33.59 | -$2.04 | -5.73% | **Decrease** |
| 2019 | $33.19 | -$0.40 | -1.19% | **Decrease** |
| 2020 | $27.00 | -$6.19 | -18.65% | Large **decrease** |
| 2021 | $31.47 | +$4.47 | +16.56% | Large increase |
| 2022 | $33.37 | +$1.90 | +6.04% | |
| 2023 | $45.00 | +$11.63 | +34.84% | Very large increase |
| 2024 | $48.00 | +$3.00 | +6.67% | IRA 6% cap in effect |
| 2025 | $55.00 | +$7.00 | +14.58% | Projected (may be capped) |

### Part D Statistical Analysis

**Period Analysis:**
- **1 Year (2024-2025)**: 14.58% actual, but IRA caps at 6%
  - **Our CSV shows 3.5% - CONSERVATIVE**
  
- **5 Years (2020-2025)**:
  - CAGR = ((55.00/27.00)^(1/5)) - 1 = 15.31%
  - But highly volatile with massive swings
  - **Our CSV shows 4.2% - VERY CONSERVATIVE**
  
- **10 Years (2015-2025)**:
  - CAGR = ((55.00/37.02)^(1/10)) - 1 = 4.04%
  - **Our CSV shows 3.8% - close, reasonable**
  
- **19 Years (2006-2025)**:
  - CAGR = ((55.00/25.93)^(1/19)) - 1 = 4.05%
  - **Our CSV shows 3.7% - close, reasonable**

---

## Recommended Adjustments

Based on this analysis, here are the actual rates vs. what we have:

### Medicare Part B
| Period | Actual CAGR | Our CSV | Recommendation |
|--------|------------|---------|----------------|
| 1 year | 5.90% | 5.9% | ✓ Correct |
| 5 years | 5.05% | 6.8% | **Reduce to 5.1%** |
| 10 years | 5.84% | 4.9% | **Increase to 5.8%** |
| 19 years | 3.96% | 4.3% | ✓ Close enough |

### Medicare Part D
| Period | Actual CAGR | Our CSV | Recommendation |
|--------|------------|---------|----------------|
| 1 year | 14.58%* | 3.5% | Keep conservative due to IRA cap |
| 5 years | 15.31%** | 4.2% | Keep at 4.2% (too volatile) |
| 10 years | 4.04% | 3.8% | ✓ Close enough |
| 19 years | 4.05% | 3.7% | ✓ Close enough |

*Subject to 6% IRA cap starting 2024
**Extremely volatile period with -18.65% and +34.84% swings

## Key Observations

1. **Part B Premium Patterns**:
   - Two periods of decrease (2012, 2023)
   - Three periods of no increase (2009, 2014-2015, 2018)
   - Large spikes in 2010 (14.63%), 2016 (16.11%), 2022 (14.55%)

2. **Part D Premium Patterns**:
   - Much more volatile than Part B
   - Six years of decreases (2014-2016, 2018-2020)
   - Extreme volatility in recent years
   - IRA cap of 6% now in effect starting 2024

3. **Calculation Notes**:
   - Simple averages can be misleading due to volatility
   - CAGR (Compound Annual Growth Rate) is more accurate
   - Recent Part D volatility makes projections difficult
   - Conservative estimates may be prudent for Part D given uncertainty