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
The application uses Auth0 Regular Web Application authentication:
- **Architecture:** Frontend handles Auth0 redirects, backend exchanges codes with client_secret
- **Flow:** Frontend → Auth0 → Frontend callback → Django token exchange → JWT tokens
- **Security:** Server-side token exchange using client_secret (not PKCE)
- **Social Providers:** Google, Facebook, Apple, and email/password
- **Protected routes:** All API endpoints require valid Django JWT tokens

**Detailed Auth0 Regular Web Application Flow:**
1. **User clicks login** → Frontend redirects directly to Auth0 (not backend URL)
2. **Auth0 authentication** → User authenticates with chosen provider (Google, etc.)
3. **Auth0 callback** → Auth0 redirects back to `localhost:3000/auth/callback` with authorization code
4. **Frontend callback handler** → Extracts code and sends POST to `/api/auth0/exchange-code/`
5. **Django backend exchange** → Uses client_secret to exchange code for Auth0 tokens
6. **User creation/retrieval** → Django creates or finds user, generates JWT tokens
7. **Frontend completion** → Stores JWT tokens and redirects to dashboard

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

**Authentication (Regular Web Application):**
- `/api/auth0/login-redirect/` - Django redirects to Auth0 (general login)
- `/api/auth0/login-google/` - Django redirects to Auth0 (Google-specific)
- `/api/auth0/callback/` - Django receives Auth0 callback directly (not used in current flow)
- `/api/auth0/exchange-code/` - Frontend sends authorization code for token exchange
- `/api/auth0/logout/` - Django handles Auth0 logout redirect

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
- `/api/medicare/inflation-rates/` - Get historical Medicare Part B and Part D inflation rates

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
1. **Auth0 Dashboard Configuration**: Ensure `http://localhost:3000/auth/callback` is in allowed callback URLs
2. **Environment Variables**: Backend must have `AUTH0_CLIENT_SECRET` in .env file
3. **Frontend Environment**: Frontend needs `VITE_AUTH0_DOMAIN` and `VITE_AUTH0_CLIENT_ID`
4. **Test Flow**: Click login → Auth0 redirect → Callback → Token exchange → Dashboard
5. **Debug**: Check browser console and Django logs for errors during token exchange

### Auth0 Regular Web Application Implementation (September 2025)
**Complete rewrite of Auth0 authentication to follow Regular Web Application pattern:**

#### **Key Architecture Changes:**
- **Removed Auth0 Vue SDK**: No more `@auth0/auth0-vue` dependency in frontend
- **Frontend Direct Auth0**: Login buttons redirect directly to Auth0 authorization endpoint
- **Backend Token Exchange**: Django exchanges authorization codes using `client_secret`
- **Hybrid Security Model**: Frontend handles redirects, backend handles secure token exchange

#### **Implementation Details:**
- **Login Flow**: `Login.vue` builds Auth0 URLs manually and redirects to Auth0
- **Callback Handling**: `Auth0CallbackSimple.vue` extracts authorization code from URL
- **Token Exchange**: Frontend POSTs code to `/api/auth0/exchange-code/` endpoint
- **Django Backend**: Exchanges code with Auth0 using `client_secret`, creates user, returns JWT tokens

#### **Files Modified:**
- `frontend/src/main.js` - Removed Auth0 Vue SDK initialization
- `frontend/src/views/Login.vue` - Manual Auth0 redirect URL construction
- `frontend/src/views/Auth0CallbackSimple.vue` - Code extraction and backend API call
- `backend/core/auth0_views.py` - Complete rewrite with clean Regular Web App endpoints
- `backend/core/urls.py` - Updated to only include necessary Auth0 endpoints

#### **Auth0 Dashboard Requirements:**
- **Application Type**: Regular Web Application (not Single Page Application)
- **Callback URLs**: `http://localhost:3000/auth/callback` (frontend receives callbacks)
- **Client Secret**: Must be configured in Django backend `.env` file
- **No audience parameter**: Removed from Auth0 configuration to avoid service errors

#### **Benefits of New Implementation:**
- ✅ **Server-side security**: Token exchange uses `client_secret` instead of PKCE
- ✅ **Simplified frontend**: No complex Auth0 SDK state management
- ✅ **Better error handling**: Clear separation of concerns between frontend and backend
- ✅ **Standard compliance**: Follows Auth0 Regular Web Application documentation exactly
- ✅ **Debugging friendly**: Clear request/response flow for troubleshooting

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

## Recent Development Updates (September 2025)

### Redis/Celery Async Processing System
- **Complete async processing infrastructure** for scenario calculations
- **Docker services**: Redis message broker, Celery worker, Celery beat scheduler, Celery Flower monitoring
- **Frontend integration**: Progress tracking, task cancellation, fallback to sync calculations
- **Scalability**: Supports 1000+ concurrent users with distributed task processing

### Authentication System Improvements
- **Fixed rate limiting issues** causing frequent logout redirects during navigation
- **Increased throttle rates**: Authenticated users from 100/min to 1000/min requests
- **Enhanced error handling**: Exponential backoff retry logic for rate-limited requests
- **Token consistency**: Fixed authentication token mismatches in async calculation methods
- **Batched API loading**: Staggered API calls to prevent rate limiting bursts

### Medicare Inflation Rates System
**Complete historical data analysis and dynamic dropdown implementation:**

#### **Backend Implementation:**
- **CSV data source**: `/backend/core/tax_data/medicare_inflation_rates.csv`
- **API endpoint**: `/api/medicare/inflation-rates/` with JWT authentication
- **Historical analysis**: Complete Medicare Part B data from 1966 inception through 2025
- **Calculation methodology**: Compound Annual Growth Rate (CAGR) for accurate projections

#### **Available Time Periods:**
- **From inception (59 years)**: Part B 7.3%, Part D 4.1% (Medicare started 1966, Part D 2006)
- **Last 1 year**: Part B 5.9%, Part D 6.0%
- **Last 5 years**: Part B 5.1%, Part D 4.2%
- **Last 10 years**: Part B 5.8%, Part D 4.0%
- **Last 15 years**: Part B 3.5%, Part D 3.8%
- **Last 25 years**: Part B 5.8%, Part D 3.9%

#### **Frontend Integration (ScenarioCreate.vue):**
- **Dynamic dropdowns**: Populate from API with descriptive labels
- **Custom rate option**: Users can enter custom inflation rates when needed
- **Fallback handling**: Graceful degradation if API unavailable
- **Real-time loading**: Data loaded on component mount with error handling

### Investment Modal Improvements
- **Fixed age calculation issues** in "Age Last Year of Contribution" dropdown
- **Enhanced validation**: Proper handling of client birthdate data and age ranges
- **Extended age range**: Contribution ages now go from current age to 80 years
- **Better error handling**: Debug logging and fallback values for invalid dates
- **Client data loading**: Ensures client data is loaded before opening investment modal

### Hold Harmless Act Implementation
**Added comprehensive Social Security Hold Harmless protection indicators:**

#### **Backend Calculation Logic:**
- **Medicare cost protection**: Reduces Medicare deduction instead of increasing SS income
- **IRMAA bracket eligibility**: Only applies to those in first IRMAA bracket (bracket 0)
- **Annual comparison**: Maintains previous year's net Social Security amount
- **Accurate tax calculations**: Ensures Hold Harmless doesn't affect IRMAA or tax computations

#### **Frontend Visual Indicators:**
- **Lock icon (🔒)**: Shows when beneficiary is protected by Hold Harmless
- **Detailed tooltips**: Display protection amounts and eligibility criteria
- **Indicator legends**: Right-justified in table headers for Social Security and Financial Overview tabs
- **Cross-tab consistency**: Same functionality across all relevant scenario pages

### Navigation System Restructure
**Complete navigation overhaul for cleaner user experience:**

#### **Header Navigation System:**
- **Dropdown-based navigation**: Moved scenario page links from left sidebar to header dropdowns
- **Dual dropdown design**: Scenario switcher + Page navigation dropdowns
- **Improved layout**: Client info moved to first row, navigation right-justified
- **Consistent styling**: Bootstrap-based dropdowns with identical styling
- **Label structure**: "Choose [Scenario ▼] - [Page ▼]" format

#### **Sidebar Cleanup:**
- **Removed scenario page sections**: Eliminated collapsible scenario page navigation
- **Direct scenario links**: Simplified links that go directly to scenario overview
- **Reduced clutter**: Cleaner left navigation focused on core functionality

### Scenario Calculation Fixes
- **Division by zero error**: Fixed Social Security taxation percentage calculation
- **Error handling**: Proper handling of scenarios without Social Security income
- **Debugging improvements**: Enhanced logging for troubleshooting calculation issues
- **Fallback mechanisms**: Graceful degradation when calculations encounter edge cases

### Performance Optimizations
- **Batched data loading**: Concurrent loading of client data and configuration
- **API call optimization**: Staggered requests to prevent rate limiting
- **Enhanced caching**: Better use of browser and server-side caching
- **Database query optimization**: Improved query patterns for faster response times

## Development Workflow Updates

### Backend Restart Requirements
After making changes to:
- CSV configuration files (tax data, Medicare rates)
- Backend Python code
- Environment variables

**Always restart the backend:**
```bash
docker compose -f docker/docker-compose.yml restart backend
```

### Configuration File Management
**Medicare Inflation Rates:**
- File: `/backend/core/tax_data/medicare_inflation_rates.csv`
- Update process: Edit CSV → Restart backend → Hard refresh frontend
- No code changes required for rate updates

**Tax Data Updates:**
- Annual updates via CSV files only
- Automatic inflation calculations via `tax_csv_loader.py`
- Version control friendly (CSV diffs)

### Debugging Best Practices
- **Browser console**: Check for API errors and authentication issues
- **Backend logs**: Monitor Docker container logs for calculation errors
- **Rate limiting**: Watch for 429 status codes in network tab
- **Token validation**: Verify JWT tokens are properly formatted and valid

## Architecture Decisions

### Async Processing
- **Redis**: Message broker and result backend
- **Celery**: Distributed task queue with worker processes
- **Progress tracking**: Real-time updates via polling mechanism
- **Fault tolerance**: Automatic fallback to synchronous calculations

### Data Management
- **CSV-based configuration**: Easy updates without code deployment
- **Historical data accuracy**: Research-based inflation calculations
- **API-driven dropdowns**: Dynamic configuration loading
- **Caching strategies**: Balance between performance and data freshness

### User Experience
- **Progressive enhancement**: Graceful degradation when services unavailable
- **Clear visual feedback**: Loading states, progress bars, error messages
- **Responsive design**: Works across different screen sizes and devices
- **Accessibility**: Proper ARIA labels and keyboard navigation support

## Billing System Implementation (September 2025)

### Complete Stripe Integration for Subscription Management
**Implemented comprehensive billing system with real-time Stripe API integration:**

#### **Backend Implementation:**
- **API Endpoints**: Complete set of billing management endpoints in `backend/core/billing_views.py`
- **Live Stripe Data**: All subscription data pulled directly from Stripe API (no database caching)
- **Dual Format Support**: Handles both old (plan-based) and new (items-based) Stripe subscription formats
- **Comprehensive Error Handling**: Proper Stripe API error handling and logging

#### **Key API Endpoints:**
- `/api/billing/subscription/` - Get subscription details, invoices, and payment methods
- `/api/billing/cancel-subscription/` - Cancel subscription at period end with reason tracking
- `/api/billing/reactivate-subscription/` - Reactivate canceled subscriptions
- `/api/billing/update-payment-method/` - Create setup intent for payment method updates
- `/api/billing/download-invoice/<invoice_id>/` - Get invoice download URLs

#### **Frontend Implementation:**
- **Complete Billing Page**: `frontend/src/views/Billing.vue` with subscription overview, billing history, and actions
- **Real-time Status Updates**: Live data fetched from Stripe on every page load
- **Custom Vue Modal**: Implemented cancellation modal without Bootstrap JS dependencies
- **Responsive Design**: Mobile-friendly layout with Bootstrap components

#### **Key Features:**
1. **Subscription Status Display:**
   - Current plan details with pricing and billing cycle
   - Payment method information with masked card details
   - Subscription status badges with color coding
   - Next billing date and period information

2. **Cancellation System:**
   - Modal-based cancellation with reason collection
   - Immediate Stripe API updates with `cancel_at_period_end=true`
   - Cancellation feedback tracking in Stripe metadata
   - Visual indicators for pending cancellations

3. **Billing History:**
   - Last 12 invoices with status and amounts
   - Direct PDF download links from Stripe
   - Hosted invoice URLs for online viewing
   - Invoice status tracking and display

4. **Subscription Actions:**
   - Cancel subscription with reason tracking
   - Reactivate canceled subscriptions
   - Update payment method (setup intent creation)
   - Context-aware action buttons based on subscription state

#### **Effective Status System:**
- **Real-time Status Calculation**: Backend determines `effective_status` from live Stripe data
- **Canceled Pending State**: Detects when subscription is active but set to cancel at period end
- **Visual Indicators**: Prominent warning banner and status badge updates for pending cancellations
- **Status Logic**:
  ```python
  effective_status = subscription.status
  if subscription.status == 'active' and getattr(subscription, 'cancel_at_period_end', False):
      effective_status = 'canceled_pending'
  ```

#### **User Experience Enhancements:**
- **Cancellation Banner**: Prominent alert showing cancellation status and end date
- **Status Badge Updates**: "CANCELED (ACTIVE UNTIL END)" for pending cancellations
- **Action Button Logic**: Context-aware buttons based on subscription state
- **Proper Z-index**: Ensures banners appear above navigation elements
- **Debug Information**: Temporary debug section for development troubleshooting

#### **Navigation Integration:**
- **Header Dropdown**: Added "Billing" option to user dropdown menu in `frontend/src/components/Header.vue`
- **Router Integration**: Added billing route with authentication requirements
- **Protected Route**: Requires authentication to access billing information

#### **Technical Implementation Details:**
- **API Architecture**: RESTful endpoints following Django REST Framework patterns
- **Authentication**: JWT token-based authentication for all billing endpoints
- **Error Handling**: Comprehensive error handling for Stripe API failures
- **Logging**: Detailed logging for debugging and audit trails
- **Security**: Customer data verification to prevent unauthorized access

#### **Stripe Data Flow:**
1. **Frontend Request**: User visits billing page, frontend calls `/api/billing/subscription/`
2. **Backend Processing**: Django authenticates user, retrieves Stripe subscription data
3. **Live API Calls**: Fresh Stripe API calls for subscription, invoices, and payment methods
4. **Status Calculation**: Backend calculates effective status from Stripe data
5. **Response**: Structured JSON response with all billing information
6. **Frontend Display**: Vue.js renders subscription details, history, and action buttons

#### **Files Created/Modified:**
- `backend/core/billing_views.py` - Complete billing API implementation
- `backend/core/urls.py` - Added billing URL patterns
- `frontend/src/views/Billing.vue` - Complete billing page component
- `frontend/src/components/Header.vue` - Added billing dropdown option
- `frontend/src/router/index.js` - Added billing route
- `backend/core/management/commands/check_stripe_customer.py` - Stripe customer verification tool
- `backend/core/management/commands/check_cancel_status.py` - Detailed cancellation status checker

#### **Admin User Impersonation System Fixes:**
- **Exit Impersonation**: Fixed `end_user_impersonation` endpoint to allow impersonated users to exit
- **Banner Visibility**: Fixed z-index and condition issues with impersonation banner
- **Permission Logic**: Removed admin requirement from exit endpoint while maintaining security
- **Status Detection**: Fixed `isImpersonating` flag logic to use `originalUser` presence

#### **Testing and Verification:**
- **Stripe Integration**: Verified with live Stripe data for customer mark@irmaacertifiedplanner.com
- **Cancellation Flow**: Tested cancel subscription functionality updates Stripe properly
- **Status Detection**: Confirmed `cancel_at_period_end=true` properly detected and displayed
- **API Endpoints**: All billing endpoints tested and working with proper authentication

#### **Current Status:**
- ✅ **Complete billing system implemented**
- ✅ **Stripe integration working with live data**
- ✅ **Cancellation system functional**
- ✅ **Visual indicators for canceled subscriptions**
- ✅ **Navigation integration complete**
- ✅ **Admin impersonation system fixed**
- 🔄 **Awaiting user testing of cancellation banner visibility**

#### **Known Configuration:**
- **Live Stripe Environment**: Using production Stripe keys
- **Customer Verified**: mark@irmaacertifiedplanner.com exists in Stripe with active subscription
- **Cancellation Confirmed**: Subscription shows `cancel_at_period_end=true` in Stripe
- **API Data Flow**: Real-time data from Stripe API, no database caching

## Recent Development Updates (September 10, 2025)

### Report Generator System Fixed and Enabled
**Complete restoration of advanced report generation system with PDF/PowerPoint export:**

#### **Issues Fixed:**
1. **Enabled Report Center URLs**: Uncommented line 30 in `/backend/retirementadvisorpro/urls.py`
2. **Fixed Import Errors**: 
   - Corrected model imports (`Asset`, `Income`, `Expense` → `IncomeSource`)
   - Fixed service imports (`report_file_storage` → `file_storage_service`)
   - Fixed `scenario_data_integration_service` → `scenario_integration_service`
3. **Fixed URL Path Duplication**: Removed duplicate `/api/` prefix in report_center URLs
4. **Updated Model References**: Adapted to use `income_sources` instead of non-existent models

#### **Report Generator Features Now Available:**
- **Template Management**: CRUD operations for report templates
- **Report Generation**: PDF and PowerPoint export formats
- **AI-Powered Content**: Automatic content generation for reports
- **Background Processing**: Async report generation via Celery
- **Report History**: Track and manage all generated reports
- **Custom Branding**: Upload logos and customize templates

#### **API Endpoints Activated:**
- `/api/report-center/templates/` - Template management
- `/api/report-center/reports/` - Report generation and history
- `/api/report-center/ai/executive-summary/` - AI executive summaries
- `/api/report-center/ai/slide-recommendations/` - AI slide recommendations
- `/api/report-center/ai/content-suggestions/` - AI content generation

### Affiliate System UI Fixes

#### **Layout Issues Fixed:**
- **Affiliate Detail Page**: Added `margin-top: 60px` to push content below fixed header
- **Affiliate List Page**: Added `margin-top: 60px` to fix header overlap

#### **Functionality Fixes:**
1. **Generate Link Button**:
   - Added missing modal component for link generation
   - Implemented `generateLink` method with form validation
   - Added reactive data for `newLink` and `generatingLink` states
   - Modal includes fields for link name, destination URL, and campaign

2. **Edit Button**:
   - Created new `AffiliateEdit.vue` component with complete edit form
   - Updated router configuration to use the new component
   - Form includes all affiliate fields (business name, email, contact, status, commission rate, payment method, etc.)
   - Proper navigation between edit and detail views

#### **Affiliate Portal Password System:**
- **No Auto-Generation**: Passwords are user-created, not auto-generated
- **First-Time Login Flow**:
  1. Affiliate logs in with email + affiliate code
  2. System detects no password → shows password setup form
  3. Affiliate creates password (min 8 characters)
  4. Password is hashed and stored securely
- **Fixed Error Handling**: Updated frontend to properly show password setup form instead of error message
- **Test Affiliate**: `test@affiliate.com` with code `E8QE1ID8` ready for password setup

#### **Files Created/Modified:**
- `/frontend/src/views/affiliate/AffiliateEdit.vue` - New edit component
- `/frontend/src/views/affiliate/AffiliateDetail.vue` - Added modal and functionality
- `/frontend/src/views/affiliate/AffiliateList.vue` - Fixed layout
- `/frontend/src/views/affiliate/AffiliatePortalLogin.vue` - Fixed password setup flow
- `/frontend/src/router/index.js` - Updated routing
- `/backend/report_center/services/scenario_integration_service.py` - Fixed model references
- `/backend/report_center/services/powerpoint_generator.py` - Fixed imports
- `/backend/report_center/services/bulk_export_service.py` - Fixed imports
- `/backend/report_center/urls.py` - Fixed URL paths