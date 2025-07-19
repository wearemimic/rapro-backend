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