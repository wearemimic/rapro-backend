# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RetirementAdvisorPro is a full-stack SaaS platform for financial advisors to manage client retirement planning. The application provides Monte Carlo simulations, tax calculations, Roth conversion optimization, and comprehensive retirement scenario modeling.

## Tech Stack

**Frontend:**
- Vue.js 3 with Composition API
- Vite build tool
- Pinia for state management
- Vue Router for navigation
- Auth0 for authentication
- Chart.js for visualizations
- Bootstrap/Front Dashboard theme

**Backend:**
- Django 4.2 with Django REST Framework
- PostgreSQL database
- Python 3.12
- Auth0 integration via social-auth-app-django
- Stripe for payments
- Redis for caching/queues

## Development Commands

### Quick Start
```bash
# Recommended: Use the start script
./start.sh

# Or manually with Docker Compose
docker compose -f docker/docker-compose.yml up --build
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev        # Development server on port 3000
npm run build      # Production build
npm run preview    # Preview production build
```

### Backend Development
```bash
cd backend
python manage.py migrate      # Apply database migrations
python manage.py seed_data    # Load initial data
python manage.py runserver    # Development server on port 8000
python manage.py test         # Run Django tests
pytest                        # Run pytest suite
```

### Database Management
```bash
python manage.py makemigrations   # Create new migrations
python manage.py migrate          # Apply migrations
python manage.py dbshell          # Access database shell
python manage.py createsuperuser  # Create admin user
```

### Docker Commands
```bash
# View logs
docker compose -f docker/docker-compose.yml logs -f [service_name]

# Execute commands in containers
docker compose -f docker/docker-compose.yml exec backend python manage.py [command]
docker compose -f docker/docker-compose.yml exec frontend npm [command]

# Clean up
docker compose -f docker/docker-compose.yml down -v
```

## Architecture Overview

### Directory Structure
```
/retirementadvisorpro/
├── backend/
│   ├── core/                 # Main Django app (models, views, serializers)
│   ├── retirementadvisorpro/ # Django settings and configuration
│   └── media/                # User uploads (logos, templates)
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable Vue components
│   │   ├── views/           # Page components
│   │   ├── stores/          # Pinia state management
│   │   ├── router/          # Vue Router configuration
│   │   └── services/        # API service layers
│   └── public/              # Static assets
└── docker/                  # Docker configuration
```

### Key API Endpoints
- `/api/auth/` - Authentication endpoints
- `/api/clients/` - Client management
- `/api/scenarios/` - Retirement scenarios
- `/api/simulations/` - Monte Carlo simulations
- `/api/reports/` - PDF report generation

### Data Models
The core Django models include:
- `Client` - Client profiles with financial information
- `Scenario` - Retirement planning scenarios
- `Income` - Income sources (Social Security, pensions, etc.)
- `Expense` - Expense categories and amounts
- `Asset` - Investment accounts and properties
- `TaxSettings` - Tax configuration per scenario

### Authentication Flow
The application now uses a complete Auth0 authentication system:
- **Frontend:** Direct Auth0 redirect method (more reliable than Vue plugin)
- **Backend:** Custom JWT validation and user management
- **Flow:** Auth0 login → Authorization code → Backend token exchange → Django JWT tokens
- **Social Providers:** Google, Facebook, Apple, and email/password
- **Protected routes:** All API endpoints require valid Django JWT tokens

### Key Features
1. **Monte Carlo Simulation Engine** - Stress tests retirement scenarios
2. **Tax Calculations** - Including IRMAA, RMDs, and state taxes
3. **Roth Conversion Optimizer** - Analyzes optimal conversion strategies
4. **Social Security Planning** - Breakeven analysis and optimization
5. **Report Generation** - Customizable PDF reports with charts

## Current Development Status

### Recently Completed Features (Auth0 Integration Branch)

**Auth0 Authentication System:**
- ✅ Complete Auth0 integration replacing legacy authentication
- ✅ Social login support (Google, Facebook, Apple)
- ✅ Direct Auth0 redirect method (bypassing Vue plugin issues)
- ✅ Secure authorization code exchange via backend
- ✅ User management endpoints (list, update, delete users)
- ✅ Password reset functionality via Auth0

**Enhanced Registration Flow:**
- ✅ 3-step registration process with Auth0
  - Step 1: Auth0 authentication (social or email)
  - Step 2: Professional information collection
  - Step 3: Stripe payment with comprehensive credit card fields
- ✅ Smart billing address toggle (same as professional address)
- ✅ Real-time form validation and error handling
- ✅ Seamless Auth0 callback integration

**Payment System Enhancements:**
- ✅ Comprehensive credit card form with:
  - Cardholder name field
  - Separate Stripe elements for card number, expiry, and CVV
  - Complete billing address fields
  - Professional styling matching the design system
- ✅ **Coupon Code System:**
  - Real-time coupon validation via Stripe API
  - Dynamic price updates when discounts are applied
  - Support for percentage and fixed amount discounts
  - Visual feedback with success/error messages
  - Applied discount summary with removal option
  - Backend integration for subscription creation with coupons

**Backend Endpoints Added:**
- `/api/auth0/login/` - Auth0 token exchange
- `/api/auth0/signup/` - Auth0 user creation
- `/api/auth0/debug/` - Auth0 configuration testing
- `/api/auth0/exchange-code/` - Authorization code exchange
- `/api/auth0/complete-registration/` - Registration completion with Stripe
- `/api/validate-coupon/` - Coupon validation endpoint
- `/api/users/` - User management (CRUD operations)

**Key Implementation Details:**
- Auth0 environment variables configured in both frontend and backend
- Secure token exchange without exposing client secret
- Stripe customer creation integrated with Auth0 users
- Professional information stored with user profiles
- Subscription management with coupon support

## Testing Approach

**Frontend Testing:**
- Test framework dependencies installed (vitest, @testing-library/vue)
- No test scripts configured yet in package.json

**Backend Testing:**
- Use `pytest` for unit tests
- Test files in `/backend/core/tests/`
- Django test runner also available

## Important Notes

1. Always check the current git branch before making changes
2. The application uses Docker for consistent development environments
3. Frontend runs on port 3000, backend on port 8000
4. PostgreSQL database is containerized
5. Media files (user uploads) are stored in `/backend/media/`
6. Static files need to be collected with `python manage.py collectstatic` for production

## Environment Variables

### Frontend (.env)
```
# Auth0
VITE_AUTH0_DOMAIN=genai-030069804226358743.us.auth0.com
VITE_AUTH0_CLIENT_ID=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw
VITE_AUTH0_AUDIENCE=https://api.retirementadvisorpro.com

# Stripe
VITE_STRIPE_PUBLIC_KEY=your-stripe-public-key
```

### Backend (.env)
```
# Auth0
AUTH0_DOMAIN=genai-030069804226358743.us.auth0.com
AUTH0_CLIENT_ID=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw
AUTH0_CLIENT_SECRET=your-auth0-client-secret
AUTH0_AUDIENCE=https://api.retirementadvisorpro.com
AUTH0_ALGORITHM=RS256

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_MONTHLY_PRICE_ID=your-monthly-price-id
STRIPE_ANNUAL_PRICE_ID=your-annual-price-id
```

## Common Development Tasks

### Adding a New User Management Feature
1. Add the endpoint in `/backend/core/auth0_views.py`
2. Update URLs in `/backend/core/urls.py`
3. Add the frontend method in `/frontend/src/stores/auth.js`
4. Create/update the UI component

### Creating Stripe Coupons
1. Log into Stripe Dashboard
2. Navigate to Products → Coupons
3. Create coupon with desired discount (percentage or fixed amount)
4. Use the coupon ID in the application

### Testing Auth0 Integration
1. Use the `/api/auth0/debug/` endpoint to verify configuration
2. Check browser console for Auth0 redirect URLs
3. Verify tokens in browser DevTools → Application → Local Storage
4. Test social logins in incognito mode to avoid session conflicts

## Latest Development Session (2025-01-19)

### Scenario Duplication Feature - COMPLETED ✅

**Feature Overview:**
Implemented complete scenario duplication functionality that allows users to duplicate existing retirement scenarios with all their data and settings, then edit them in the scenario creation interface.

**Frontend Changes:**
- **ScenarioDetail.vue (line 985):** Added `createScenario` method to handle both "from scratch" and "duplicate" options
- **ScenarioDetail.vue (line 62):** Existing dropdown already had "Duplicate This Scenario" option
- **ScenarioCreate.vue (line 732):** Enhanced `onMounted` to detect duplication via query parameter
- **ScenarioCreate.vue (line 757):** Added `loadScenarioForDuplication` function to fetch and prefill scenario data

**Backend Changes:**
- **views.py (line 278):** Added `duplicate_scenario` endpoint for creating scenario copies
- **views.py (line 346):** Added `get_scenario_detail` endpoint for fetching complete scenario data
- **urls.py (line 39-40):** Added URL routes for both new endpoints:
  - `scenarios/<int:scenario_id>/detail/` - Get scenario data for duplication
  - `scenarios/<int:scenario_id>/duplicate/` - Create scenario duplicate

**Feature Workflow:**
1. User clicks "Duplicate This Scenario" in dropdown menu
2. Navigates to ScenarioCreate.vue with `?duplicate=<scenario_id>` query parameter
3. System automatically fetches original scenario data via API
4. All form fields prefill with original values (income sources, tax settings, Medicare config, etc.)
5. User can modify any values and save as new scenario
6. New scenario gets name like "Original Scenario Name (Copy)"

**Technical Implementation:**
- Complete data preservation including all income sources and their specific configurations
- Proper authentication and ownership checks on all endpoints
- Reset certain fields (percentages, model changes) to defaults for new scenarios
- UUID generation for frontend compatibility
- Error handling for failed duplications

**Files Modified:**
- `/frontend/src/views/ScenarioDetail.vue`
- `/frontend/src/views/ScenarioCreate.vue` 
- `/backend/core/views.py`
- `/backend/core/urls.py`

This feature significantly improves user workflow by allowing advisors to create variations of existing scenarios without re-entering all the complex financial data.

## Latest Development Session (2025-01-20)

### Comparison Report and UI Improvements - COMPLETED ✅

**Major Bug Fix - Comparison Report Data Issue:**
- ✅ **Fixed critical data display bug** where comparison report showed all zeros instead of actual financial calculations
- ✅ **Root cause:** Backend was calculating correctly but data extraction wasn't handling Python Decimal objects properly
- ✅ **Solution:** Added explicit Decimal-to-float conversion in `get_scenario_comparison_data` function
- ✅ **Files modified:** `/backend/core/views.py` - lines with federal tax and medicare calculations

**Comparison Report Enhancements:**
- ✅ **Database-backed preferences** - Replaced localStorage with `ComparisonPreference` model for cross-device persistence
- ✅ **Automatic preference saving** - Selections are saved automatically when scenarios are loaded
- ✅ **Preference restoration** - Previously selected scenarios are automatically loaded on page refresh
- ✅ **Backend endpoints:** `/api/clients/<id>/comparison-preferences/` for GET/POST operations
- ✅ **Files modified:** 
  - `/backend/core/models.py` - Added ComparisonPreference model
  - `/backend/core/views.py` - Added comparison_preferences endpoint
  - `/frontend/src/views/ComparisonReport.vue` - Added preference loading/saving logic

**UI Layout and Styling Fixes:**
- ✅ **Fixed table width issues** on Financial Overview, Social Security, and Medicare tabs
- ✅ **Resolved chart alignment problems** where Net Income line appeared higher than Gross Income
- ✅ **Standardized card heights** across comparison columns for consistent alignment
- ✅ **Improved page spacing** - Fixed navbar overlap and reduced excessive spacing
- ✅ **Removed debug output** from comparison report UI
- ✅ **Files modified:** Multiple tab components with CSS and Chart.js configuration updates

**Single Client Scenario Creation:**
- ✅ **Added single client awareness** - Hide spouse options in all dropdowns when client tax status is "single"
- ✅ **Dynamic dropdown filtering** - All ownership dropdowns (income, investments, etc.) conditionally show spouse
- ✅ **Computed property implementation** - `isSingle` computed based on client tax status
- ✅ **Files modified:** `/frontend/src/views/ScenarioCreate.vue`

**Investment Modal Enhancements:**
- ✅ **Converted age fields to dropdowns** - Age to Begin/End Withdrawals now use select dropdowns
- ✅ **Dynamic age ranges** - Age options respect individual lifespan settings (primary vs spouse)
- ✅ **Lifespan constraints** - End withdrawal age limited to owner's configured lifespan
- ✅ **Added Monthly Withdrawal Amount field** - New currency input for specifying monthly withdrawal amounts
- ✅ **Removed Annual Contribution Percentage** - Simplified contribution options to amount-only
- ✅ **Files modified:** `/frontend/src/components/InvestmentModal.vue`

**Key Technical Implementations:**
- Database migration for ComparisonPreference model with user/client foreign keys
- Computed properties for dynamic age ranges based on ownership and lifespan
- Proper null checks in Vue templates to prevent compilation errors
- Chart.js configuration fixes for proper line/bar chart stacking
- Bootstrap CSS improvements for consistent card layouts and spacing

**API Endpoints Added:**
- `GET/POST /api/clients/<id>/comparison-preferences/` - Manage comparison selections

This session focused heavily on UI/UX improvements, data accuracy fixes, and form enhancements to streamline the advisor workflow when creating and comparing retirement scenarios.

## Latest Development Session (2025-01-20 - Evening)

### Current Age Display Fix - COMPLETED ✅

**Problem Fixed:**
- ✅ **Scenario Detail Page Age Display** - Fixed "Current age: Not Specified" issue on scenario detail pages
- ✅ **Root cause:** Frontend was looking for `client.age` field that doesn't exist in the database model
- ✅ **Solution:** Added computed properties to calculate current age from `client.birthdate` field
- ✅ **Files modified:** `/frontend/src/views/ScenarioDetail.vue` - Added `currentAge()` and `spouseAge()` computed properties

### UI and Logo Updates - COMPLETED ✅

**Default Logo Update:**
- ✅ **Updated default logo** across all pages to use `RAD-white-logo.png`
- ✅ **Files modified:**
  - `/frontend/src/components/Header.vue` - Updated default and fallback logo references
  - `/frontend/src/views/Login.vue` - Updated logo on login page  
  - `/frontend/src/views/Register.vue` - Updated logo on registration page

**Authentication Page Styling:**
- ✅ **Blue background theme** - Login and registration pages now use header blue (`#377dff`) background
- ✅ **White card contrast** - Maintained white cards with enhanced shadows for better visual separation
- ✅ **Consistent branding** - Matches internal application header color scheme

### Financial Flow Overview Hiding - COMPLETED ✅

**UI Improvement:**
- ✅ **Hidden Financial Flow Overview card** from Financial Overview tab as requested
- ✅ **Implementation:** Used `v-if="false"` directive for easy future re-enabling
- ✅ **Files modified:** `/frontend/src/views/FinancialOverviewTab.vue`

### Enhanced Scenario Management - COMPLETED ✅

**Edit Scenario Functionality:**
- ✅ **Added "Edit Scenario" button** next to New Scenario dropdown in scenario detail pages
- ✅ **Smart navigation logic:**
  - "From Scratch" → Clean scenario creation page
  - "Duplicate This Scenario" → Pre-filled scenario creation (existing functionality)
  - "Edit Scenario" → Pre-filled scenario creation with original ID preserved
- ✅ **Dynamic form behavior:**
  - Button text changes: "Create Scenario" vs "Update Scenario"
  - API calls: POST for creation, PUT for updates
  - Cancel behavior: Returns to original scenario when editing, client page when creating

**Investment Modal Enhancements:**
- ✅ **Added Monthly Withdrawal Amount field** to investment information modal
- ✅ **Updated layout:** Converted withdrawal row from 2 columns to 3 columns (`col-md-4`)
- ✅ **Backend integration:** Field properly mapped to `withdrawal_amount` in save function

**Smart Cancel Navigation:**
- ✅ **Context-aware cancel button:**
  - When editing: Returns to `/clients/{id}/scenarios/detail/{scenarioId}`
  - When creating/duplicating: Returns to `/clients/{id}`
- ✅ **Prevents user navigation loss** during scenario editing workflows

### Investment Account Categorization Fix - COMPLETED ✅

**Data Separation Bug Fix:**
- ✅ **Fixed investment accounts appearing in Income Sources** when editing/duplicating scenarios
- ✅ **Root cause:** Backend returns all income sources in single array without proper categorization
- ✅ **Solution:** Added data filtering logic in `loadScenarioForDuplication()` and `loadScenarioForEditing()` functions
- ✅ **Investment account types properly categorized:**
  - Qualified, Non-Qualified, Roth accounts → Investment Accounts section
  - Social Security, Pension, etc. → Income Sources section
- ✅ **Files modified:** `/frontend/src/views/ScenarioCreate.vue`

**Key Technical Implementations:**
- Computed properties for age calculation from birthdates with proper month/day handling
- Dynamic logo system with fallback support and cache-busting
- Comprehensive scenario management with create/edit/duplicate workflows
- Data filtering and categorization for proper UI component separation
- Context-aware navigation patterns for improved user experience

**API Endpoints Enhanced:**
- `PUT /api/scenarios/<id>/update/` - Update existing scenarios (used by edit functionality)
- Enhanced query parameter support: `?edit=scenarioId` vs `?duplicate=scenarioId`

This session focused on resolving user experience issues, fixing data display problems, and enhancing the scenario management workflow with comprehensive edit capabilities.

## Latest Development Session (2025-08-17)

### Tax Configuration System - COMPLETED ✅

**Problem Addressed:**
Tax rates, brackets, IRMAA thresholds, and Medicare costs were hardcoded throughout the codebase, making annual updates difficult and error-prone.

**Solution Implemented:**
- ✅ **CSV-Based Tax Configuration System** - Created centralized tax data management using easily editable CSV files
- ✅ **Comprehensive Tax Data Coverage** - Federal brackets, state taxes, IRMAA thresholds, Medicare rates, Social Security thresholds
- ✅ **Annual Update Process** - Simple copy-and-edit workflow for tax year updates

**Files Created:**
- **Tax Data CSVs** (all in `/backend/core/tax_data/`):
  - `federal_tax_brackets_2025.csv` - All federal tax brackets by filing status
  - `standard_deductions_2025.csv` - Standard deduction amounts
  - `irmaa_thresholds_2025.csv` - Medicare IRMAA thresholds and surcharges  
  - `medicare_base_rates_2025.csv` - Base Medicare Part B/D premiums
  - `social_security_thresholds_2025.csv` - Social Security taxation thresholds
  - `state_tax_rates_2025.csv` - All 50 states' tax rates and retirement income treatment
- **Python Loader:** `/backend/core/tax_csv_loader.py` - Loads CSV data with caching and calculation methods
- **Documentation:** `/backend/core/tax_data/README.md` - Complete guide for annual updates
- **Analysis Document:** `/TAX_ANALYSIS_AND_CENTRALIZATION.md` - Implementation plan and benefits

**Key Features:**
- **Easy Annual Updates**: Copy previous year's CSVs and update values - no code changes required
- **Automatic Data Conversion**: CSV loader converts strings to Decimal for precision financial calculations
- **Comprehensive State Coverage**: All 50 states plus DC with retirement income tax treatment
- **Calculation Methods**: Built-in federal tax and IRMAA calculation functions
- **Caching System**: Performance optimization with intelligent caching
- **Version Control**: Each tax year has separate files for historical reference

**Usage Examples:**
```python
# Load 2025 tax data
from core.tax_csv_loader import TaxCSVLoader
loader = TaxCSVLoader(2025)

# Calculate federal tax
tax, bracket = loader.calculate_federal_tax(Decimal('75000'), "Single")

# Get IRMAA surcharges
part_b, part_d = loader.calculate_irmaa(Decimal('150000'), "Married Filing Jointly") 

# Get state tax info
ca_tax = loader.get_state_tax_info("CA")
```

**Annual Update Process:**
1. Copy previous year's CSV files (e.g., `*_2025.csv` → `*_2026.csv`)
2. Update values with new IRS/Medicare/state rates
3. Change default year in `tax_csv_loader.py` 
4. Test and deploy

**Benefits:**
- **Maintainability**: All tax values in one location
- **Accuracy**: Single source of truth prevents inconsistencies
- **Compliance**: Easy to update for annual tax law changes
- **State Tax Ready**: Framework supports all state tax calculations
- **Audit Trail**: Git tracks all changes to tax values

### Roth Calculator Updates - PARTIALLY COMPLETED ⚠️

**Problem Addressed:**
Roth conversion calculator was using outdated asset type filtering and missing conversion amounts in pre-retirement years.

**Fixes Applied:**
- ✅ **Asset Type Filtering Fix** (`/frontend/src/views/RothConversionTab.vue` lines 583-597):
  - Updated from old types (`traditional_401k`, `traditional_ira`) 
  - Now correctly filters for `Qualified`, `Inherited Traditional Spouse`, `Inherited Traditional Non-Spouse`
- ✅ **Backend Parameter Fix** (`/frontend/src/views/RothConversionTab.vue` line 1033):
  - Added missing `roth_conversion_annual_amount` field to scenario data
- ✅ **Field Name Consistency** (`/backend/core/roth_conversion_processor.py` lines 687, 591):
  - Changed `conversion_amount` to `roth_conversion` for frontend compatibility
- ✅ **Enhanced Pre-retirement Data** (`/backend/core/roth_conversion_processor.py`):
  - Added complete field structure for pre-retirement conversion years

**Remaining Issue:**
Despite fixes, conversion amounts still show as `$0.00` in the table. Root cause appears to be:
- Backend changes may not have taken effect properly
- RothConversionProcessor may not be executing correctly
- Frontend may be displaying baseline instead of conversion results

**Documentation:**
- ✅ **Analysis Document:** `/ROTH_CALCULATOR_ANALYSIS.md` - Complete technical reference with fixes applied

This session established a robust tax configuration system and made significant progress on Roth calculator fixes, with debugging still required for the conversion amount display issue.

## Latest Development Session (2025-08-17)

### CSV Tax System Integration - COMPLETED ✅

**Objective:**
Integrate the existing CSV-based tax configuration system with the actual scenario processing code to replace all hardcoded tax values.

**Integration Completed:**
- ✅ **Federal Tax Brackets** (`/backend/core/scenario_processor.py` lines 821-840):
  - Replaced hardcoded 2025 tax brackets with CSV loader
  - Added tax status normalization for CSV lookup
  - Maintained same calculation accuracy with improved maintainability
- ✅ **IRMAA Calculations** (`/backend/core/scenario_processor.py` lines 842-872):
  - Replaced hardcoded IRMAA thresholds with CSV data
  - Updated Medicare cost calculation to use CSV base rates
  - Proper filing status mapping for all scenarios
- ✅ **Standard Deductions** (`/backend/core/scenario_processor.py` lines 399-417):
  - Replaced hardcoded standard deduction amounts with CSV loader
  - Dynamic lookup based on filing status
  - Maintains existing logic flow with improved data source
- ✅ **Medicare Base Rates** (integrated within IRMAA calculation):
  - Base Part B and Part D rates now loaded from CSV
  - Automatic doubling for married filing jointly cases

**Technical Implementation:**
- **Tax Loader Import:** Added `from core.tax_csv_loader import get_tax_loader` to scenario processor
- **Status Mapping:** Consistent normalization of tax status strings for CSV lookups
- **Error Handling:** Graceful fallbacks for missing data or invalid filing statuses
- **Performance:** Cached CSV loading prevents repeated file reads

**Files Modified:**
- `/backend/core/scenario_processor.py` - Integrated CSV tax loader throughout tax calculations
- Updated imports and replaced 4 major hardcoded tax calculation sections

**Testing Results:**
```
Federal tax on $75,000 (Single): $11,414.00 at 22% bracket
Standard deduction (Single): $15,000.00
IRMAA on $150,000 (Single): Part B +$179.80, Part D +$35.30
Medicare base rates: Part B $185.00, Part D $71.00
```

**Benefits Achieved:**
- **Centralized Tax Data**: All tax values now loaded from single CSV source
- **Easy Annual Updates**: Change CSV files without touching code
- **Consistency**: Eliminates duplicate/conflicting hardcoded values
- **Audit Trail**: Git tracks all tax rate changes
- **State Tax Ready**: Framework prepared for state tax integration

**Annual Update Process:**
1. Copy current year CSVs to new year (e.g., `*_2025.csv` → `*_2026.csv`)
2. Update CSV values with new IRS/Medicare rates
3. Change default year in `tax_csv_loader.py` line 220: `def get_tax_loader(tax_year=2026)`
4. Deploy - no code changes required

The tax system is now fully integrated and production-ready with the CSV configuration approach.

## Latest Development Session (2025-08-17 - Roth Conversion Interface)

### Multi-Step Roth Conversion Wizard - COMPLETED ✅

**Objective:**
Redesign the Roth conversion interface from a single-page form to a guided multi-step wizard with better user experience and validation.

**New Interface Design:**
- ✅ **3-Step Wizard Layout** - Step-by-step guided process replacing single complex form
- ✅ **Progressive Summary** - Right-side summary panel that builds as user completes steps
- ✅ **Smart Validation** - Button activation based on completion and conversion amount validation
- ✅ **Improved Layout** - 3/4 left wizard, 1/4 right summary with sticky positioning

### Step-by-Step Implementation:

**Step 1: Asset Selection**
- ✅ **Asset Selection Panel** - Full-width asset table for better visibility
- ✅ **Conversion Amount Validation** - "Next" button disabled until at least one asset has conversion amount > 0
- ✅ **Asset Name Display Fix** - Shows actual asset names (e.g., "John's 401k") instead of generic types ("Qualified")
- ✅ **Real-time Summary** - Selected assets and total conversion amount displayed in summary panel

**Step 2: Conversion Schedule**  
- ✅ **Core Parameters** - Conversion Start Year, Max Annual Conversion Amount, Years to Convert
- ✅ **Auto-calculated Fields** - Max Annual Amount auto-updates based on total conversion ÷ years
- ✅ **Year Validation** - Roth Withdrawal Start Year automatically defaults to Conversion Start Year + 1
- ✅ **Schedule Summary** - Conversion timeline details added to summary panel

**Step 3: Income and Withdrawal Details**
- ✅ **Final Parameters** - Pre-Retirement Income, Roth Growth Rate, Withdrawal Amount, Withdrawal Start Year  
- ✅ **Smart Calculate Button** - Changes to green "Calculate Conversion" when all steps complete
- ✅ **Year Dependencies** - Withdrawal year auto-updates when conversion year changes
- ✅ **Complete Summary** - All configuration details shown in summary panel

### Button and Validation Logic:

**Smart Button States:**
- ✅ **Step Navigation** - Previous/Next buttons with proper enabling/disabling
- ✅ **Calculate Button** - Only enabled when conversion amounts > 0 are entered
- ✅ **Visual Feedback** - Button colors change (gray → blue → green) based on completion status
- ✅ **Tooltips** - Helpful messages explain why buttons are disabled

**Year Validation Logic:**
- ✅ **Auto-defaulting** - Roth Withdrawal Start Year = Conversion Start Year + 1 on page load
- ✅ **Dependency Handling** - Withdrawal year auto-updates when conversion year changes
- ✅ **Validation Feedback** - Red border and error messages for invalid year selections

### User Experience Improvements:

**Visual Design:**
- ✅ **Step Indicators** - Numbered badges (1→2→3) showing progress
- ✅ **Dynamic Headers** - Card title changes to show current step ("Step 1: Select Assets to Convert")
- ✅ **Progress Bar** - Visual completion indicator in summary panel
- ✅ **Consistent Styling** - Light gray headers with black text for proper contrast

**Summary Panel Features:**
- ✅ **Sticky Positioning** - Summary stays visible during scrolling
- ✅ **Progressive Building** - Information appears as user completes each step
- ✅ **Asset Details** - Shows selected assets with conversion amounts
- ✅ **Schedule Overview** - Start year, duration, and annual limits
- ✅ **Final Configuration** - All parameters in one consolidated view

### Technical Implementation:

**Vue.js Components:**
- ✅ **Step Management** - `currentStep` data property (1-3) controls wizard flow
- ✅ **Navigation Methods** - `nextStep()`, `previousStep()` for wizard control
- ✅ **Computed Properties** - `currentStepTitle()`, `canProceedFromStep1()`, `canRecalculateConversion()`
- ✅ **Dynamic Display** - `v-show` directives based on current step

**Data Flow Improvements:**
- ✅ **Asset Name Mapping** - Fixed display to show `asset.income_name || asset.investment_name || asset.income_type`
- ✅ **Auto-calculation** - Max Annual Amount updates when total conversion amount changes
- ✅ **Year Dependencies** - Withdrawal year watcher automatically adjusts based on conversion year

**Files Modified:**
- `/frontend/src/views/RothConversionTab.vue` - Complete wizard implementation
- `/frontend/src/components/RothConversion/AssetSelectionPanel.vue` - Asset name display fix

### Benefits Achieved:

1. **Guided Process** - Step-by-step wizard prevents user confusion and errors
2. **Better Validation** - Smart button states and real-time feedback guide user input
3. **Improved Visibility** - Asset names show meaningful titles instead of generic types
4. **Progressive Disclosure** - Complex form broken into logical, manageable steps
5. **Visual Feedback** - Progress indicators and summary panel reinforce user choices
6. **Automatic Calculations** - Smart defaults and auto-updating fields reduce manual input

The Roth conversion interface now provides a significantly improved user experience with better guidance, validation, and visual feedback while maintaining all existing functionality in a more organized and intuitive format.