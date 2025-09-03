# Auth0 + Stripe Registration System PRD

## Executive Summary
Implement a complete registration system that integrates Auth0 Regular Web Application authentication with Stripe subscription payments. Users will authenticate via Auth0 (Google, Facebook, Apple, Email) and complete professional information + payment in a seamless 3-step flow.

## Current State Analysis

### ✅ What's Already Working:
- **Auth0 Regular Web Application flow**: Login works with frontend → Auth0 → callback → Django token exchange
- **Stripe Integration**: Backend has live Stripe keys and price IDs configured
- **Registration UI**: Complete 3-step registration form exists in `Register.vue`
- **Backend Infrastructure**: Django endpoints for user management and Stripe processing

### ❌ What Needs to Be Fixed:
- **Auth0 Registration Integration**: Current registration uses old Auth0 Vue SDK
- **Backend Registration Endpoints**: Need to update for Regular Web Application flow
- **Registration Callback Flow**: Must match the login callback pattern
- **Stripe Registration Completion**: Integration with Auth0 user creation

## Implementation Plan

### Phase 1: Auth0 Registration Flow Integration
**Goal**: Make registration use the same Auth0 Regular Web Application pattern as login

#### Task 1.1: Update Frontend Registration Auth0 Calls ✅
- **File**: `frontend/src/views/Register.vue`
- **Action**: Replace Auth0 Vue SDK calls with direct Auth0 redirects
- **Details**: 
  - Remove `useAuth0()` import and usage
  - Update `signupWithAuth0()` function to build Auth0 URLs manually
  - Add `screen_hint=signup` parameter to Auth0 URLs
  - Use same callback URL as login (`localhost:3000/auth/callback`)

#### Task 1.2: Create Registration State Management ✅
- **File**: `frontend/src/views/Auth0CallbackSimple.vue`
- **Action**: Detect registration vs login flow in callback
- **Details**:
  - Check `localStorage.getItem('auth0_flow')` for 'registration'
  - After token exchange, redirect to `/register?step=2` instead of dashboard
  - Pass registration completion flag to registration page

#### Task 1.3: Update Backend Auth0 Exchange for Registration ✅  
- **File**: `backend/core/auth0_views.py`
- **Action**: Enhance `auth0_exchange_code` to handle registration flow
- **Details**:
  - Detect new vs existing users during token exchange
  - For new users: create with `is_registration_complete=False`
  - Return registration status in API response
  - Create placeholder professional profile

### Phase 2: Professional Information Integration
**Goal**: Seamlessly collect professional info after Auth0 authentication

#### Task 2.1: Pre-populate Registration Form ✅
- **File**: `frontend/src/views/Register.vue` 
- **Action**: Auto-fill form with Auth0 user data
- **Details**:
  - Extract first_name, last_name, email from Auth0 user
  - Skip step 1 (account creation) for Auth0 users
  - Show "Complete Registration" messaging
  - Validate all professional info fields

#### Task 2.2: Create Professional Profile API ✅
- **File**: `backend/core/views.py`
- **Action**: Create/update professional profile endpoint
- **Details**:
  - `POST /api/complete-professional-info/`
  - Update user professional fields
  - Validate required fields (firstName, lastName, phone)
  - Return updated user data

### Phase 3: Stripe Subscription Integration
**Goal**: Complete Stripe subscription creation with professional info

#### Task 3.1: Create Registration Completion Endpoint ✅
- **File**: `backend/core/auth0_views.py`
- **Action**: Create `auth0_complete_registration` endpoint
- **Details**:
  - Accept professional info + payment data
  - Create Stripe customer with professional info
  - Create subscription with selected plan
  - Handle coupon codes and discounts
  - Update user `is_registration_complete=True`
  - Return success/failure status

#### Task 3.2: Stripe Payment Method Integration ✅
- **File**: `frontend/src/views/Register.vue`
- **Action**: Process Stripe payment in registration flow
- **Details**:
  - Create payment method with billing address
  - Send to backend for subscription creation
  - Handle 3D Secure authentication if needed
  - Show payment success/error states

#### Task 3.3: Handle Registration Completion ✅
- **File**: `frontend/src/views/Register.vue`
- **Action**: Complete registration flow
- **Details**:
  - Call `auth0_complete_registration` endpoint
  - Handle success → redirect to dashboard
  - Handle errors → show user-friendly messages
  - Clean up localStorage registration flags

### Phase 4: Coupon and Pricing Integration
**Goal**: Enable coupon codes and dynamic pricing

#### Task 4.1: Restore Coupon Validation Endpoint ✅
- **File**: `backend/core/auth0_views.py`  
- **Action**: Add back `validate_coupon` function
- **Details**:
  - Validate Stripe coupon codes
  - Return discount information
  - Handle percentage vs fixed amount coupons
  - Calculate discounted prices

#### Task 4.2: Dynamic Price Display ✅
- **File**: `frontend/src/views/Register.vue`
- **Action**: Show real-time pricing with discounts
- **Details**:
  - Fetch pricing from Stripe price IDs
  - Apply coupon discounts dynamically
  - Show original vs discounted prices
  - Update totals when plan changes

### Phase 5: Error Handling and Edge Cases
**Goal**: Handle all registration failure scenarios gracefully

#### Task 5.1: Auth0 Registration Errors ✅
- **Action**: Handle Auth0 signup failures
- **Details**:
  - Account already exists → redirect to login
  - Auth0 service errors → show retry options
  - State validation failures → clear and retry
  - Network errors → show offline message

#### Task 5.2: Stripe Payment Errors ✅  
- **Action**: Handle Stripe payment failures
- **Details**:
  - Card declined → show error, allow retry
  - 3D Secure required → handle authentication flow
  - Network errors → retry mechanism
  - Invalid coupon codes → clear and retry

#### Task 5.3: Incomplete Registration Recovery ✅
- **Action**: Handle partially completed registrations
- **Details**:
  - User authenticated but no professional info → redirect to step 2
  - User has professional info but no payment → redirect to step 3
  - Payment failed → allow retry from step 3
  - Session expired → restart from step 1

## Technical Requirements

### Frontend Environment Variables
```
VITE_AUTH0_DOMAIN=genai-030069804226358743.us.auth0.com
VITE_AUTH0_CLIENT_ID=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw
VITE_STRIPE_PUBLIC_KEY=pk_live_51MKmFTDXYH4nUgjBhJ8lIWxB9iNkkZIXV3tHKUxOKiNWk5Zlgkx4lOBtiYpAsW55OvI1U7E9Ty82nSErHQHxW7BS00YEJ4LkEq
VITE_API_URL=http://localhost:8000/api
```

### Backend Environment Variables  
```
AUTH0_DOMAIN=genai-030069804226358743.us.auth0.com
AUTH0_CLIENT_ID=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw
AUTH0_CLIENT_SECRET=[required - add to .env]
STRIPE_SECRET_KEY=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
STRIPE_MONTHLY_PRICE_ID=price_1S2elxDXYH4nUgjBwy8RXl67
STRIPE_ANNUAL_PRICE_ID=price_1S2elxDXYH4nUgjBZI9k5dYr
```

### Auth0 Dashboard Configuration
- **Application Type**: Regular Web Application
- **Callback URLs**: `http://localhost:3000/auth/callback`
- **Logout URLs**: `http://localhost:3000/login`
- **Web Origins**: `http://localhost:3000`

### Stripe Configuration
- **Products**: Already configured with monthly/annual prices
- **Webhooks**: Configured for subscription events
- **Coupons**: Various discount codes available

## API Endpoints to Implement/Update

### Registration Flow Endpoints
```
POST /api/auth0/exchange-code/
- Enhanced to detect registration vs login
- Create new users with registration_complete=False
- Return registration status

POST /api/auth0/complete-registration/
- Accept professional info + payment data  
- Create Stripe customer and subscription
- Complete user registration
- Return success status

POST /api/validate-coupon/
- Validate Stripe coupon codes
- Return discount information
- Calculate final prices
```

## User Flow Diagrams

### Registration Flow
```
1. User visits /register
2. Clicks "Continue with Google" (or other provider)
3. Redirects to Auth0 with screen_hint=signup
4. Auth0 handles authentication
5. Auth0 redirects to /auth/callback with code
6. Frontend extracts code, sends to Django
7. Django exchanges code, creates new user
8. Frontend redirects to /register?step=2
9. User fills professional information
10. User proceeds to payment (step 3)
11. User enters payment information
12. Frontend creates Stripe payment method
13. Frontend calls complete-registration API
14. Django creates Stripe subscription
15. Registration complete → redirect to dashboard
```

### Error Recovery Flow
```
If user is authenticated but registration incomplete:
- Check registration_complete flag
- Redirect to appropriate step (2 or 3)
- Allow completion from any step
- Handle payment retry scenarios
```

## Success Criteria

### Phase 1 Success ✅
- [ ] Registration uses Auth0 Regular Web Application flow
- [ ] No more Auth0 Vue SDK dependencies in registration
- [ ] Auth0 callback correctly handles registration flow
- [ ] Users can sign up with Google, Facebook, Apple, Email

### Phase 2 Success ✅  
- [ ] Professional info form pre-populates with Auth0 data
- [ ] All professional fields validate correctly
- [ ] Users can navigate back/forward between steps
- [ ] Form state persists during navigation

### Phase 3 Success ✅
- [ ] Stripe payment integration works end-to-end
- [ ] Subscriptions created successfully in Stripe
- [ ] Payment errors handled gracefully
- [ ] Users receive confirmation of successful registration

### Phase 4 Success ✅
- [ ] Coupon codes validate against Stripe
- [ ] Pricing updates dynamically with coupons
- [ ] Both monthly and annual plans supported
- [ ] Discount calculations are accurate

### Phase 5 Success ✅
- [ ] All error scenarios handled gracefully
- [ ] Users can retry failed payments
- [ ] Incomplete registrations can be resumed
- [ ] Clear error messages guide user actions

## Implementation Priority

### High Priority (Must Have)
1. **Auth0 Registration Integration** - Core functionality
2. **Stripe Subscription Creation** - Revenue critical  
3. **Professional Info Collection** - Business requirement
4. **Error Handling** - User experience critical

### Medium Priority (Should Have)  
1. **Coupon Code Support** - Marketing feature
2. **Dynamic Pricing Display** - UX enhancement
3. **Registration Recovery** - Edge case handling

### Low Priority (Nice to Have)
1. **Advanced Stripe features** (3D Secure, etc.)
2. **Registration analytics** - Future optimization
3. **A/B testing framework** - Future experiments

## Testing Checklist

### Auth0 Integration Tests ✅
- [ ] Google signup creates new user
- [ ] Facebook signup creates new user  
- [ ] Apple signup creates new user
- [ ] Email signup creates new user
- [ ] Existing user redirected to login
- [ ] State validation works correctly

### Stripe Integration Tests ✅
- [ ] Monthly subscription created successfully
- [ ] Annual subscription created successfully
- [ ] Valid coupon codes apply discounts
- [ ] Invalid coupon codes show errors
- [ ] Payment method creation works
- [ ] Failed payments show appropriate errors

### User Experience Tests ✅
- [ ] Complete registration flow works end-to-end
- [ ] Form validation prevents submission with missing fields
- [ ] Navigation between steps preserves form data
- [ ] Error messages are clear and actionable
- [ ] Success confirmation is clear
- [ ] Registration completion redirects to dashboard

## Dependencies

### External Services
- **Auth0**: Regular Web Application configured
- **Stripe**: Live keys and products configured  
- **Frontend**: Vue 3 + Composition API
- **Backend**: Django + DRF

### Internal Dependencies  
- **Auth Store**: Must work with Auth0 Regular Web Application tokens
- **Registration Store**: State management for multi-step form
- **API Services**: HTTP client for backend communication

## Risks and Mitigation

### High Risk
- **Auth0 Configuration**: Wrong application type breaks flow
  - *Mitigation*: Verify Regular Web Application setup
- **Stripe Live Keys**: Production keys in development
  - *Mitigation*: Use test keys for development, live for production

### Medium Risk  
- **Payment Failures**: Complex error scenarios
  - *Mitigation*: Comprehensive error handling and retry logic
- **State Management**: Registration state inconsistencies
  - *Mitigation*: Clear localStorage management and validation

### Low Risk
- **Performance**: Large form with multiple steps
  - *Mitigation*: Lazy loading and form optimization
- **Browser Compatibility**: Stripe Elements compatibility
  - *Mitigation*: Test on major browsers, fallback options