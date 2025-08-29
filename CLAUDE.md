# CLAUDE.md

## IMPORTANT: NO HARDCODING URLS OR SENSITIVE DATA
- NEVER hardcode URLs, API keys, client secrets, or any sensitive information in code
- Always use environment variables or configuration files for sensitive data
- Use .env files for local development and proper secrets management for production

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
The application uses Auth0 authentication:
- **Frontend:** Direct Auth0 redirect method
- **Backend:** Custom JWT validation and user management
- **Flow:** Auth0 login → Authorization code → Backend token exchange → Django JWT tokens
- **Social Providers:** Google, Facebook, Apple, and email/password
- **Protected routes:** All API endpoints require valid Django JWT tokens

### Key Features
1. **Monte Carlo Simulation Engine** - Stress tests retirement scenarios
2. **Tax Calculations** - Including IRMAA, RMDs, and state taxes (CSV-based configuration)
3. **IRMAA Inflation System** - Automatic inflation adjustment of Medicare threshold brackets
4. **Roth Conversion Optimizer** - Multi-step wizard with tax calculations
5. **Social Security Planning** - Breakeven analysis and optimization
6. **Report Generation** - Customizable PDF reports with charts

## Current Implementation Status

### Auth0 Authentication
- Complete Auth0 integration with social login support
- User management endpoints (CRUD operations)
- Password reset via Auth0
- 3-step registration with Stripe payment integration

### Payment System
- Stripe integration with coupon support
- Comprehensive credit card form
- Real-time coupon validation
- Subscription management

### Tax Configuration System (CSV-Based)
All tax data managed through CSV files in `/backend/core/tax_data/`:
- Federal tax brackets, standard deductions
- IRMAA thresholds and Medicare rates with configurable inflation
- State tax rates and retirement income treatment
- Inflation rates configuration via `inflation_config.csv`
- Annual updates via CSV file edits (no code changes required)

### IRMAA Inflation System
The application includes a sophisticated IRMAA (Income-Related Monthly Adjustment Amount) system that automatically inflates Medicare premium thresholds each year:

**Key Components:**
- **Base Thresholds**: Stored in `irmaa_thresholds_2025.csv` with 5 bracket levels
- **Inflation Configuration**: Configurable rates in `inflation_config.csv` (default 1% annually)
- **Backend Calculations**: `tax_csv_loader.py` handles inflation adjustments and bracket determination
- **Frontend Indicators**: Orange lines and tooltips show bracket crossings across all tabs

**Implementation:**
- `get_inflated_irmaa_thresholds()` - Applies compound inflation from base year to target year
- `calculate_irmaa_with_inflation()` - Determines bracket and calculates surcharges
- Scenario results include `irmaa_bracket_number` and `irmaa_bracket_threshold` fields
- All tabs (Financial, Social Security, Medicare) use consistent backend bracket data

**Visual Indicators:**
- Orange horizontal lines appear when crossing IRMAA brackets
- Info icons (ℹ️) provide detailed bracket information in tooltips
- Tooltips show: bracket number, MAGI vs threshold, year-specific amounts
- Responsive tooltip positioning prevents off-screen display

### API Endpoints Summary

**Authentication:**
- `/api/auth0/login/` - Auth0 token exchange
- `/api/auth0/signup/` - User creation
- `/api/auth0/exchange-code/` - Authorization code exchange
- `/api/auth0/complete-registration/` - Registration completion

**Scenarios:**
- `/api/scenarios/<id>/calculate/` - Run calculations
- `/api/scenarios/<id>/duplicate/` - Duplicate scenario
- `/api/scenarios/<id>/update/` - Update scenario
- `/api/scenarios/<id>/assets/` - Get asset details

**User Management:**
- `/api/users/` - CRUD operations
- `/api/validate-coupon/` - Coupon validation
- `/api/clients/<id>/comparison-preferences/` - Save comparison selections

**Tax & IRMAA:**
- `/api/tax/federal-standard-deduction/` - Get standard deduction amounts
- `/api/tax/irmaa-thresholds/` - Get inflation-adjusted IRMAA thresholds by year

## Testing Approach

**Frontend Testing:**
- Test framework: vitest, @testing-library/vue
- No test scripts configured yet

**Backend Testing:**
- Use `pytest` for unit tests
- Test files in `/backend/core/tests/`
- Django test runner available

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

## Important Implementation Notes

### ScenarioDetail Component Architecture
Tab components must follow this pattern:

**Props Required:**
```javascript
props: {
  scenario: { type: Object, required: true },
  scenarioResults: { type: Array, required: true },
  client: { type: Object, required: true }
}
```

**Navigation Pattern:**
- URL: `/clients/{id}/scenarios/detail/{scenarioId}?tab={tabName}`
- Parent loads all data, passes to tabs via props
- No async loading in tab components

**Critical Rules:**
- ❌ NO complex watchers with `immediate: true`
- ❌ NO async data loading in mounted()
- ✅ Accept data via props
- ✅ Simple initialization only
- ✅ Use mortality ages from scenario object

### Docker Configuration
- Frontend runs on port 3000 (configurable via `FRONTEND_PORT`)
- Backend runs on port 8000 (configurable via `BACKEND_PORT`)
- PostgreSQL is containerized
- Media files in `/backend/media/`
- **IMPORTANT: Backend changes require restart** - Use `docker compose -f docker/docker-compose.yml restart backend` after any backend code changes
- Ensure docker-compose loads .env files:
  ```yaml
  env_file:
    - ../backend/.env
  ```

## Common Development Tasks

### Adding a New Feature
1. Add endpoint in `/backend/core/views.py`
2. Update URLs in `/backend/core/urls.py`
3. Add frontend method in appropriate store
4. Create/update UI component

### Annual Tax Updates
1. Copy previous year's CSV files (e.g., `*_2025.csv` → `*_2026.csv`)
2. Update values with new IRS/Medicare/state rates
3. Change default year in `tax_csv_loader.py`
4. Deploy - no code changes required

### IRMAA Inflation Rate Updates
1. Edit `/backend/core/tax_data/inflation_config.csv`
2. Update `irmaa_thresholds` rate (default 1.0% annually)
3. Changes apply immediately to all scenario calculations
4. No code changes or restarts required

### Testing Auth0 Integration
1. Verify configuration with `/api/auth0/debug/`
2. Check browser console for redirect URLs
3. Ensure Backend has Auth0 client secret in .env
4. Callback URLs must match in Auth0 Dashboard

## Recent Updates & Fixes

### Scenario Edit Page (ScenarioCreate.vue)
- **Investment Modal System**: Converted from inline table editing to modal-based editing for investment accounts
- **Tax Settings**: Added support for custom federal/state deductions and blind/dependent flags
- **Social Security**: Fixed label display for flat amount type ("Monthly Amount ($)")
- **Cancel Functionality**: Proper navigation back to scenario detail page when editing
- **Currency Display**: Fixed double dollar sign issue in investment current balance display

### Key Edit Page Endpoints
- `/api/scenarios/<id>/edit/` - Dedicated endpoint for editing data structure
- Uses separate serialization for edit vs detail views to maintain compatibility

### Modal Components
- **InvestmentModal.vue**: Supports both create and edit modes with proper form validation
- Fixed resetForm initialization timing issues with watchers
- Proper currency formatting without double dollar signs

### Common Issues Fixed
- **Authentication**: Token refresh logic for long editing sessions
- **Data Persistence**: Tax settings and Social Security toggles now save properly
- **Navigation**: Cancel button correctly routes back to scenario overview

### Roth Conversion Tab (RothConversionTab.vue) - Major Fixes August 2025

#### **Root Issue: Prop/Data Collision**
The component had both `scenarioResults` as a prop (from parent) and as internal data, causing data shadowing and broken functionality.

**Core Fixes:**
1. **Separated Data Concerns:**
   - `scenarioResults` (prop): General scenario results from parent ScenarioDetail component
   - `rothConversionResults` (data): Roth-specific results from optimizer API
   - Updated `filteredScenarioResults` computed property to use `rothConversionResults`

2. **Fixed Backend AttributeError:**
   - Issue: `scenario_processor.py` missing Social Security reduction fields in `from_dicts()` method
   - Location: `/backend/core/scenario_processor.py` line 847
   - Fix: Added default values for missing scenario fields:
     ```python
     required_scenario_fields = {
         'reduction_2030_ss': False,
         'ss_adjustment_year': 2030,
         'ss_adjustment_direction': 'decrease',
         'ss_adjustment_type': 'percentage',
         'ss_adjustment_amount': 23.0,
         'apply_standard_deduction': True,
     }
     ```

3. **Fixed Database Limit Validation:**
   - Issue: `roth_conversion_annual_amount` exceeded 12-digit database limit
   - Fix: Added validation and capping in API payload preparation
   - Added user-friendly UI warnings when amounts too large

4. **Enhanced Asset Timeline Graph:**
   - Fixed legend labels to show actual asset names instead of "qualified"
   - Updated all three data generation methods to use `asset.income_name || asset.investment_name`

5. **Improved UI/UX:**
   - Added helpful messages in Conversion Impact Table when no data
   - Fixed Roth Withdrawal Start Year validation to only show after "Calculate conversion"
   - Enhanced error logging and debugging throughout

#### **Key Technical Changes:**
- **Frontend:** Separated `scenarioResults` prop from `rothConversionResults` internal data
- **Backend:** Added missing scenario field defaults in `ScenarioProcessor.from_dicts()`
- **Validation:** Added database limit checking for annual conversion amounts
- **Error Handling:** Comprehensive logging and user-friendly error messages

#### **Files Modified:**
- `frontend/src/views/RothConversionTab.vue` - Core component fixes
- `backend/core/scenario_processor.py` - Missing field defaults
- Various computed properties and API response handling

#### **Testing Status:**
- Backend AttributeError resolved ✓
- 400 Bad Request errors fixed ✓
- Prop/data collision resolved ✓
- Asset graph legends showing correct names ✓
- Conversion Impact Table functionality restored ✓