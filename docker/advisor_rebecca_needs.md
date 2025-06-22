# Roth Conversion Planning Guide for Middle-Tier Financial Advisors

## Persona: Rebecca Miller

### Overview

- **Name**: Rebecca Miller  
- **Title**: Independent Financial Advisor, CFP®  
- **Location**: Midwest U.S.  
- **Years in Practice**: 10-15 years  
- **Client Base**: ~150 households, mostly pre-retirees and retirees  
- **Average Client Net Worth**: $500k–$2.5M  
- **Revenue Model**: Fee-based AUM + insurance and annuities

### Characteristics

- Solid on basic financial planning; limited advanced tax expertise.
- Comfortable selling but occasionally overwhelmed by technical details.
- Uses software but relies heavily on defaults.
- Seeks easy-to-use, integrated technology with minimal training.
- Wants tools that build confidence and client trust.

### Services Provided

- Social Security timing (basic-to-intermediate)
- Retirement income projections
- Insurance and annuity reviews
- Roth IRA conversions (needs assistance)
- Medicare guidance (light IRMAA understanding)
- Estate planning coordination (refers out)

### Pain Points

- Modeling Roth conversions across multiple years
- IRMAA impact modeling and visuals
- Social Security coordination complexities
- Tax planning across retirement phases
- Client-friendly explanations for technical issues
- Tool integration across CRM, planning, tax, insurance
- Lacks "next steps" planning prompts

---

## Rebecca’s Needs for a Roth Conversion Tool

### 1️⃣ Guided Workflow

- Step-by-step guidance for non-tax-expert advisors.
- Explain why and how each input matters.
- Include helpful prompts:
  - Fill tax brackets?
  - Avoid future RMD spikes?
  - Consider Medicare surcharges?
  - Legacy optimization?

### 2️⃣ Simplified Inputs

- CRM and planning software integrations.
- Tax return uploads with OCR parsing.
- Minimal manual inputs:
  - Filing status
  - IRA balances
  - Non-IRA income
  - Existing Roth accounts
  - State residency

### 3️⃣ Multi-Year Modeling

- Auto-run scenarios for multiple years.
- Model partial vs. full conversions.
- Visualize impact on RMDs, tax brackets, and long-term taxes.

### 4️⃣ IRMAA & Social Security Integration

- Model IRMAA tier impacts.
- Include inflation adjustments.
- Show Social Security taxation changes.

### 5️⃣ Client-Friendly Outputs

- Side-by-side comparisons.
- Visual charts for client discussions.
- Executive summary with minimal jargon.
- Printable reports.

### 6️⃣ "Next Steps" Engine

- Actionable task list:
  - Conversion amounts.
  - Tax estimate reminders.
  - CPA communication prompts.
  - IRA custodian paperwork.

### 7️⃣ Advisor Confidence Builders

- Guardrails to prevent errors.
- Warnings for IRMAA jumps.
- Educational tooltips.

### 8️⃣ Time Savings & Automation

- Auto paperwork generation.
- Custodian integration.
- Annual update reminders.

---

# 2️⃣ Sample Workflow for Rebecca's Roth Conversion Planning

## A. Client Fact Gathering (automated where possible)

- Import client data from CRM & planning software.
- Upload latest tax return (OCR parsing).
- Confirm:
  - Filing status
  - State residency
  - IRA balances
  - Non-IRA income
  - Existing Roth balances

## B. Goal Setting

- Advisor selects objectives:
  - Minimize RMDs
  - Maximize Roth inheritance
  - Stay under IRMAA
  - Utilize lower tax brackets
  - Legacy & estate planning

## C. Scenario Building (Multi-Year Projections)

- Auto-calculate:
  - Conversion amounts per year
  - Tax bracket usage
  - Future RMD comparisons
  - IRMAA projections
  - Social Security taxation

## D. Client Impact Summary

- Compare:
  - Tax cost vs. savings
  - IRMAA surcharges vs. avoided RMDs
  - Legacy value differences

## E. Actionable Next Steps

- Suggested conversion amount.
- Estimated taxes due.
- CPA notification checklist.
- IRA custodian form prompts.

## F. Annual Review Flow

- Annual updates:
  - Taxable income refresh
  - New Roth opportunities
  - IRMAA monitoring
  - Multi-year plan adjustments

---

# 3️⃣ Sample Screen UI Mockup (Text Description)

## Main Screen: "Roth Conversion Planning Dashboard"

### Top Bar:
- Client Name | DOB | Filing Status | State | Advisor Notes

### Left Sidebar Menu:
- Client Data Input
- Goals & Priorities
- Conversion Scenarios
- Tax Impact Summary
- Next Steps & Task List
- Client Report Generator

### Main Panel: Conversion Scenarios Table

| Year | Conversion Amount | Tax Bracket Used | IRMAA Bracket Hit | Total Tax Cost | Future RMD Savings |
|------|-------------------|------------------|-------------------|----------------|-------------------|
| 2025 | $30,000 | 22% | Tier 1 | $6,600 | $15,000 |
| 2026 | $35,000 | 24% | Tier 2 | $8,400 | $18,000 |

### Visuals:

- Tax Bracket Utilization Bar Chart (stacked)
- IRMAA Threshold Alerts (color-coded)
- Lifetime Tax Savings vs. Cost Chart

### Footer:

- Generate Client Report
- View Next Steps
- Send to CPA

---

# 4️⃣ Feature Checklist for Product Design

| Feature | Must-Have | Nice-to-Have |
|---------|-----------|--------------|
| CRM & Planning Software Integration | ✅ | |
| Tax Return OCR Import | ✅ | |
| Simple, Guided Data Entry | ✅ | |
| Goal-Based Scenario Engine | ✅ | |
| Multi-Year Roth Conversion Modeling | ✅ | |
| IRMAA Impact Projections | ✅ | |
| Social Security Tax Impact Modeling | ✅ | |
| Client-Friendly Report Generator | ✅ | |
| Actionable Next Steps Engine | ✅ | |
| CPA Communication Templates | ✅ | |
| Annual Plan Refresh Automation | ✅ | |
| Educational Tooltips for Advisor | ✅ | |
| Integration with IRA Custodians | | ✅ |
| AI-powered “Smart Suggestions” | | ✅ |
| Real-Time Legislative Update Monitoring | | ✅ |

---

UI SAMPLE: 

 --------------------------------------------------------------
| Client Name: John Doe   DOB: 1957   Filing: MFJ   State: OH  |
 --------------------------------------------------------------
| Client Data Input        |  Main Panel: Conversion Scenarios |
| Goals & Priorities       |                                    |
| Conversion Scenarios     |  --------------------------------  |
| Tax Impact Summary       |  | Year | Conv Amt | Tax | IRMAA | |
| Next Steps & Task List   |  | 2025 | 30k     | 22% | Tier 1| |
| Client Report Generator  |  | 2026 | 35k     | 24% | Tier 2| |
|                          |  --------------------------------  |
|                          |                                    |
|                          |  [Tax Bracket Usage Chart]        |
|                          |  [IRMAA Threshold Alert]          |
|                          |  [Lifetime Tax Savings Chart]     |
 --------------------------------------------------------------
| [Generate Report]  [Next Steps]  [Send to CPA]                |
 --------------------------------------------------------------

 # Goal setting screen:
  ---------------------------------------------------------
| Client Name: John Doe   DOB: 1957   Filing: MFJ   State: OH |
 ---------------------------------------------------------
| Left Sidebar:                                             |
| > Client Data Input                                       |
| > Goals & Priorities (Active)                             |
| > Conversion Scenarios                                    |
| > Tax Impact Summary                                      |
| > Next Steps & Task List                                  |
| > Client Report Generator                                 |
 ---------------------------------------------------------
| Main Panel: Client Goals                                   |
| --------------------------------------------------------  |
| [ ] Minimize RMDs                                          |
| [ ] Avoid IRMAA Surprises                                  |
| [ ] Maximize Roth Inheritance                              |
| [ ] Optimize Lifetime Tax Liability                        |
| [ ] Minimize SS Taxation                                   |
|                                                            |
| [AI Suggest Goals Based on Client Data]                    |
 ---------------------------------------------------------
| [Save & Continue]                                         |
 ---------------------------------------------------------

 # CLient report Mockup

  ---------------------------------------------------------
| Client Report: Roth Conversion Strategy                  |
 ---------------------------------------------------------
| Summary:                                                  |
| - Multi-Year Roth Conversion Plan                         |
| - Projected Tax Costs vs. Lifetime Savings                |
| - IRMAA Exposure Summary                                   |
|                                                            |
| Charts:                                                   |
| [Tax Bracket Utilization] [IRMAA Threshold Impact]        |
| [Future RMD Reduction]                                     |
|                                                            |
| Table:                                                    |
| Year | Conversion | Tax Bracket | IRMAA Impact | Net Benefit |
| 2025 | $30,000    | 22%         | Tier 1       | $8,400       |
| 2026 | $35,000    | 24%         | Tier 2       | $9,800       |
 ---------------------------------------------------------
| Notes Section for Client Explanation                      |
 ---------------------------------------------------------
| [Export PDF] [Save to Client Record]                      |
 ---------------------------------------------------------

 # Next Steps Engine UI

  ---------------------------------------------------------
| Next Steps for 2025 Execution Plan                       |
 ---------------------------------------------------------
| 1. Convert $30,000 before December 31st                  |
| 2. Notify CPA of additional income                        |
| 3. Review IRMAA thresholds for next year                  |
| 4. Adjust quarterly estimated tax payments if needed      |
| 5. Prepare Roth paperwork for Custodian XYZ               |
 ---------------------------------------------------------
| Advisor Notes:                                            |
| [Editable Notes Box]                                      |
 ---------------------------------------------------------
| [Mark Complete] [Generate Task List for CRM]              |
 ---------------------------------------------------------

 
