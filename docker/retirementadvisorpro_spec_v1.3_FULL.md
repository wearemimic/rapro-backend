
## Functional Specification — `retirementadvisorpro` v1.3 (June 2025)

### 🎯 Purpose
A cloud-based financial planning platform for **advisors** to:
- Manage clients and build retirement planning scenarios.
- Run income, tax, Medicare/IRMAA, Social Security, and Roth conversion projections.
- Perform AI-powered stress testing using Monte Carlo simulation.
- Generate client-ready PDF reports.

---

### 🔐 User Roles
| Role     | Description |
|----------|-------------|
| Advisor  | Login, manage clients, create and simulate scenarios |
| Admin (future) | Manage advisors, view analytics (future) |

---

### 🧱 Modules

#### 1. **Authentication**
- `CustomUser` model (email-based)
- Includes: phone, company, branding fields, etc.

#### 2. **Client Management**
- Create/edit/delete clients
- Conditional spouse fields
- Status: draft, in_progress, reviewed, archived

#### 3. **Scenario Management**
- Multiple scenarios per client
- Retirement/Medicare/mortality ages
- Description, share toggle

#### 4. **Income Sources**
- Types: IRA, Roth, 401(k), pension, rental, etc.
- Fields: owner, balance, withdrawal age range, ROR, COLA, tax rate

#### 5. **Yearly Calculations**
- Per year:
  - Age(s), total income, taxable income
  - Federal tax, Medicare base, IRMAA surcharge, net income
- Logic includes:
  - MAGI = total income – deduction + conversions/tax-exempt
  - IRMAA brackets inflate 1%/yr; Medicare premiums 6.45%/yr
  - Surviving spouse rules

#### 6. **Social Security Worksheet**
- User inputs benefit estimates
- Lifetime value table by age
- Breakeven age comparison
- Editable life expectancy

#### 7. **IRMAA + Medicare**
- Projections begin at age 65
- Bracket-aware surcharge calculations
- MFS rules supported

#### 8. **Roth Conversion Planner**
- Inputs: years, start age, amount
- Affects MAGI and IRMAA
- Comparisons and charts

#### 9. **Report Builder**
- Choose which graphs/tables to include
- Reorder sections
- PDF download with logo and styling

#### 10. **AI Retirement Stress Test (v1.3)**
- Monte Carlo engine (NumPy, pandas, numba)
- Inputs: market return, std dev, inflation, iterations
- Output:
  - Success rate (%)
  - Summary (LLM generated)
  - Visuals (TBD)
  - PDF generation
- SimulationRun model stores results per scenario
- Vue modal UI for launching runs

---

### 🖥️ Tech Stack
| Layer         | Tech                  |
|---------------|-----------------------|
| Frontend      | Vue 3, Vite           |
| Backend       | Django, DRF           |
| Simulation    | Python 3.12, NumPy, pandas, numba |
| LLM           | GPT-4o, Mistral (TBD) |
| Database      | PostgreSQL            |
| Storage       | S3 (PDFs), Redis (TBD)|
| Hosting       | AWS                   |

---

### ✅ UX Features
- Inline scenario name editing
- Toasts and error modals
- Chart toggles and table breakdowns
- Shareable reports with branding

---

### 📌 Enhancements (Backlog)

#### From Feature Scope
- 🔜 Visual output of stress test results
- 🔜 PDF stress test report generation
- 🔜 SSA-44 form integration
- 🔜 Global toast system
- 🔜 CRM sync: Redtail, Wealthbox, Salesforce
- 🔜 Client report share link (expiring, branded)

#### From `ENHANCEMENTS.md`
- 🔜 **Update `start.sh` to check for port conflicts**
- 🔜 **Graph spend-down for asset income (e.g., 401k)**
- 🔜 **Support varying income withdrawal levels over time (e.g., Roth IRA)**
- 🔜 **AI analysis of Wealthbox clients for IRMAA exposure**

---

### 📂 Versioning Notes
- **v1.3** (June 2025): Stress test module MVP added
- Previous versions: [not yet versioned — this is the first canonical spec]

---

Should be used as the reference for QA, feature planning, and dev tasking.
