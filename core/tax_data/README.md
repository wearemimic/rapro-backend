# Tax Data CSV Files

This directory contains tax configuration data in CSV format for easy annual updates.

## Files Overview

### Federal Tax Data
- **`federal_tax_brackets_2025.csv`** - Federal income tax brackets by filing status
- **`standard_deductions_2025.csv`** - Standard deduction amounts by filing status

### Medicare/IRMAA Data  
- **`irmaa_thresholds_2025.csv`** - IRMAA (Medicare surcharge) thresholds and costs
- **`medicare_base_rates_2025.csv`** - Base Medicare Part B and Part D premiums

### Social Security Data
- **`social_security_thresholds_2025.csv`** - Income thresholds for SS taxation

### State Tax Data
- **`state_tax_rates_2025.csv`** - State income tax rates and retirement income treatment

## Annual Update Process

### 1. Create New Year Files
When the IRS releases new tax brackets (usually October-December):

```bash
# Copy current year files
cp federal_tax_brackets_2025.csv federal_tax_brackets_2026.csv
cp standard_deductions_2025.csv standard_deductions_2026.csv
cp irmaa_thresholds_2025.csv irmaa_thresholds_2026.csv
cp medicare_base_rates_2025.csv medicare_base_rates_2026.csv
cp social_security_thresholds_2025.csv social_security_thresholds_2026.csv
cp state_tax_rates_2025.csv state_tax_rates_2026.csv
```

### 2. Update Values
Edit the new files with updated values from:
- **IRS Publication 15** (federal brackets and standard deductions)
- **Medicare.gov** (Medicare premiums and IRMAA thresholds)
- **IRS Publication 915** (Social Security thresholds - rarely change)
- **State tax authorities** (state tax rates)

### 3. Update Application
Update the default tax year in `tax_csv_loader.py`:
```python
def __init__(self, tax_year=2026):  # Change from 2025 to 2026
```

## File Formats

### Federal Tax Brackets (`federal_tax_brackets_YYYY.csv`)
```csv
filing_status,min_income,max_income,tax_rate
Single,0,11925,0.10
Single,11925,48475,0.12
...
```

### Standard Deductions (`standard_deductions_YYYY.csv`)
```csv
filing_status,deduction_amount
Single,15000
Married Filing Jointly,30000
...
```

### IRMAA Thresholds (`irmaa_thresholds_YYYY.csv`)
```csv
filing_status,magi_threshold,part_b_surcharge,part_d_surcharge,description
Single,0,0,0,No surcharge
Single,106000,71.90,13.70,First tier
...
```

### Medicare Base Rates (`medicare_base_rates_YYYY.csv`)
```csv
coverage_type,monthly_rate,description
Part B,185.00,Standard Medicare Part B premium
Part D,71.00,Average Medicare Part D premium
...
```

### Social Security Thresholds (`social_security_thresholds_YYYY.csv`)
```csv
filing_status,base_threshold,additional_threshold,description
Single,25000,34000,Single filers thresholds for SS taxation
...
```

### State Tax Rates (`state_tax_rates_YYYY.csv`)
```csv
state,state_code,income_tax_rate,retirement_income_exempt,ss_taxed,description
California,CA,0.093,false,false,High rates but no tax on SS
Florida,FL,0.00,true,false,No state income tax
...
```

## Usage in Code

```python
from core.tax_csv_loader import TaxCSVLoader

# Load specific tax year
loader = TaxCSVLoader(tax_year=2025)

# Get federal tax brackets
brackets = loader.get_federal_tax_brackets("Single")

# Calculate federal tax
tax, bracket = loader.calculate_federal_tax(Decimal('75000'), "Single")

# Get IRMAA surcharges
part_b_surcharge, part_d_surcharge = loader.calculate_irmaa(Decimal('150000'), "Single")

# Get state tax info
state_info = loader.get_state_tax_info("CA")
```

## Validation

After updating CSV files, run the validation script:
```bash
python manage.py validate_tax_data --year 2026
```

This will check:
- File format consistency
- Missing required fields
- Logical errors (overlapping brackets, etc.)
- Comparison with previous year for reasonableness

## Sources for Annual Updates

### Federal Tax Data
- **IRS Revenue Procedure** (published annually in October)
- **IRS Publication 15** (Circular E)
- **Form 1040 Instructions**

### Medicare/IRMAA Data  
- **Medicare.gov** Part B and Part D premium announcements
- **CMS.gov** IRMAA threshold updates
- **Social Security Administration** Medicare announcements

### State Tax Data
- **Federation of Tax Administrators** (taxadmin.org)
- Individual state department of revenue websites
- **Tax Foundation** state tax guides

## Testing New Tax Years

Before deploying new tax year data:

1. **Unit Tests**: Run existing tax calculation tests
2. **Comparison Tests**: Compare results with previous year
3. **Sample Calculations**: Test with known scenarios
4. **IRMAA Verification**: Verify IRMAA calculations match Medicare.gov calculator

## Backup and Versioning

- Keep previous year files for reference
- Use git to track changes
- Document major changes in commit messages
- Test thoroughly before deploying to production

## Common Issues

### File Not Found
If you get "Tax data file not found" errors:
- Ensure CSV files exist for the requested year
- Check file naming convention matches `*_YYYY.csv`
- Verify file permissions

### Invalid Data
If calculations seem incorrect:
- Check CSV format (commas, headers, data types)
- Verify numeric fields don't have extra characters
- Ensure filing status names match exactly

### Missing States
If state tax calculations fail:
- Check state_code matches (case sensitive)
- Ensure all 50 states + DC are included
- Verify boolean fields use "true"/"false" (lowercase)