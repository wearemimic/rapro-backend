
# Roth Conversion Optimizer - Master Build Plan (Developer Execution Roadmap)
## Author: Dr. Elena Vargas

---

## 🏗️ Phase 0 — Project Preparation

- ✅ Load complete Calculation Engine Spec (STEP 1-7)
- ✅ Load full Roth Optimizer Spec (STEP 6 enhancements)
- ✅ Load UI Flow Spec, API Spec, Monte Carlo Spec, Report Spec

---

## 🏗️ Phase 1 — Core Engine Build (STEP 1-7)

- ✅ Module 1: Scenario Initialization
- ✅ Module 2: Income Mapping
- ✅ Module 3: Taxable Income & MAGI Engine
- ✅ Module 4: Federal Tax & AMT Engine
- ✅ Module 5: Medicare & IRMAA Engine (2-year lookback)
- ✅ Module 6: Roth Conversion Module (Joint Household, Phase 1)
- ✅ Module 7: Asset Spend-Down & Growth Engine

Deliverable: Fully functional year-by-year scenario calculator.

---

## 🏗️ Phase 2 — Monte Carlo Optimization Engine Build

- ✅ Build Monte Carlo candidate schedule generator (per Sampling Spec)
- ✅ Implement pre-filtering logic to reject invalid schedules early
- ✅ Build parallel processing runner for thousands of full-engine executions per candidate
- ✅ Integrate scoring engine (lifetime taxes, Medicare, IRMAA, Roth growth, income stability)

Deliverable: Fully functioning Roth optimizer backend module.

---

## 🏗️ Phase 3 — API Layer Integration

- ✅ Build `/api/optimizer/run-roth-optimizer` POST endpoint
- ✅ Accept scenario_id & client_id from frontend
- ✅ Manage async job execution if desired for long-running simulations
- ✅ Return full optimizer response payload (per API Spec)

Deliverable: Secure, scalable optimizer backend service callable by frontend.

---

## 🏗️ Phase 4 — Frontend Advisor UI Build

- ✅ Build Roth Optimization Tab in existing UI
- ✅ Connect "Run Optimizer" button to backend API
- ✅ Display optimal schedule, scoring summary, and key output charts (from API response)
- ✅ Build interactive advisor override fields (future enhancement)

Deliverable: Fully guided advisor experience.

---

## 🏗️ Phase 5 — Report PDF Generator Build

- ✅ Build report export pipeline (per PDF Report Spec)
- ✅ Integrate charts, tables, summary, disclosures
- ✅ Allow advisor branding insertion

Deliverable: Professional client-facing PDF reports.

---

## 🏗️ Phase 6 — Deployment & Performance Optimization

- ✅ Containerize Monte Carlo optimizer service (separate microservice architecture recommended)
- ✅ Optimize compute cores & parallel job handling
- ✅ Establish job queue management for multi-advisor concurrency

Deliverable: Scalable production system ready for SaaS deployment.

---

## 🏗️ Optional Phase 7 — Phase 2 Enhancements

- Separate spouse Roth schedules
- Tier targeting controls
- Advisor optimization goal sliders
- Dynamic IRMAA avoidance targeting
- Post-death survivor Roth optimization

---

## 📊 Team Requirements

- Full Stack Developer (Python/Django/NumPy/Numba)
- Frontend Vue Developer (existing UI integration)
- Data Engineer (parallel computing & optimization)
- PDF Report Developer
- QA Test Engineer (test multiple real-world scenarios)

---

## 🚀 Estimated Build Timeline

| Phase | Estimated Time |
|-------|----------------|
| Phase 1 | 4-5 weeks |
| Phase 2 | 3-4 weeks |
| Phase 3 | 1-2 weeks |
| Phase 4 | 2-3 weeks |
| Phase 5 | 1-2 weeks |
| Phase 6 | 2 weeks |
| TOTAL | ~13-18 weeks full build |

---

## ✅ End of Master Build Plan
