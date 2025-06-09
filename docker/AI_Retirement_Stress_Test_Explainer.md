
# AI Retirement Stress‑Test Explainer

## Overview
The AI Retirement Stress-Test Explainer is a browser-based SaaS tool designed for financial advisors. It allows them to simulate retirement scenarios using Monte Carlo simulations and includes Medicare IRMAA surcharges. The tool generates plain-language, client-ready PDFs that highlight failure points and suggest improvements.

## Purpose & Value
| For Advisers | For Clients |
|--------------|-------------|
| Automates simulations and IRMAA calculations | Understand risk of running out of money |
| Generates branded PDFs for review meetings | Gain actionable insights for retirement planning |

## Key Inputs
- Household demographics (DOBs, filing status)
- Account balances (IRA, Roth, 401k, taxable)
- Income timeline
- Spending assumptions
- Market and inflation assumptions
- Roth conversion strategy toggles

## Core Engines
- **Monte Carlo Simulator**: Generates thousands of retirement paths.
- **IRMAA Estimator**: Calculates annual surcharges with bracket lookback.
- **Tax Module**: Computes federal taxes and RMDs.
- **Cash Flow Ledger**: Tracks balances, withdrawals, and coverage needs.
- **Narrative LLM**: Summarizes findings in client-friendly language.
- **PDF Composer**: Creates downloadable PDFs with charts and summaries.

## Tech Stack
- Back-end: Python 3.12, FastAPI
- Simulation: NumPy, pandas, numba
- LLM: OpenAI GPT-4o or Mistral 7B fine-tuned
- Front-end: React + Tailwind (optional)
- Storage: Postgres, Redis, S3
- Security: SOC-2, encrypted data at rest/in transit

## Workflow
1. Input or import client data
2. Run async simulation
3. Process results (e.g., success probability, IRMAA chart)
4. Generate narrative with LLM
5. Create and download PDF
6. Optionally, edit and approve narrative before sharing

## User Experience
- Wizard-based setup
- Real-time what-if sliders for Roth conversions
- Downloadable, styled report for meetings
- Toggle between detailed/advisor view and simplified/client view

## Future Enhancements
- Voice-enabled Q&A
- ESG overlays
- Embedded client signature flows

This tool delivers high-trust, high-impact insights in under 10 minutes, enabling financial advisors to communicate retirement risk and planning options clearly and efficiently.
