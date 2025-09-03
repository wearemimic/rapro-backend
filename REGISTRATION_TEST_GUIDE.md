# Auth0 + Stripe Registration System - Test Guide

## Implementation Summary

The complete Auth0 + Stripe registration system has been implemented with the following components:

### ✅ Phase 1: Auth0 Registration Flow Integration
- **Frontend**: Updated `Register.vue` to use Auth0 Regular Web Application flow (removed Auth0 SDK)
- **Callback**: Enhanced `Auth0CallbackSimple.vue` to detect registration vs login flow
- **Backend**: Updated `auth0_exchange_code` endpoint to handle new vs existing users

### ✅ Phase 2: Professional Information Integration
- **API Endpoint**: `/api/auth0/complete-professional-info/` for collecting user profile data
- **Form Pre-population**: Auto-fills with Auth0 user data
- **Recovery Logic**: Detects incomplete registrations and resumes at correct step

### ✅ Phase 3: Stripe Subscription Integration
- **API Endpoint**: `/api/auth0/complete-registration/` with full Stripe integration
- **Customer Creation**: Creates Stripe customer with professional info
- **Subscription Management**: Handles monthly/annual plans with coupon support
- **3D Secure**: Full support for SCA authentication requirements

### ✅ Phase 4: Coupon Integration
- **API Endpoint**: `/api/validate-coupon/` for real-time coupon validation
- **Dynamic Pricing**: Shows original vs discounted prices
- **Stripe Integration**: Applies coupons to subscriptions during creation

### ✅ Phase 5: Error Handling & Recovery
- **Enhanced Error Messages**: User-friendly payment error descriptions
- **Registration Recovery**: Resumes incomplete registrations at correct step
- **State Management**: Proper cleanup of localStorage and session data

## Test Scenarios

### 1. New User Registration Flow

#### Test Case 1.1: Google Registration
1. Navigate to `/register`
2. Click "Continue with Google"
3. Complete Auth0 Google authentication
4. Should redirect to `/register?step=2` with form pre-filled
5. Fill professional information
6. Proceed to payment step
7. Enter payment information
8. Complete registration
9. Should redirect to `/dashboard`

**Expected Behavior:**
- User created in Django with `subscription_status` and `stripe_customer_id` set
- Stripe customer and subscription created
- Registration state cleared from localStorage

#### Test Case 1.2: Email Registration
1. Navigate to `/register`
2. Click "Continue with Email"
3. Complete Auth0 email/password signup
4. Follow same flow as Google registration

#### Test Case 1.3: Registration with Coupon
1. Follow any registration flow
2. At payment step, expand coupon section
3. Enter coupon code (if you have valid Stripe coupons)
4. Verify discount is applied
5. Complete registration

### 2. Registration Recovery Scenarios

#### Test Case 2.1: Incomplete Professional Info
1. Complete Auth0 authentication but don't fill professional info
2. Navigate away from registration page
3. Return to `/register`
4. Should resume at step 2 with Auth0 data pre-filled

#### Test Case 2.2: Incomplete Payment
1. Complete Auth0 authentication and professional info
2. Navigate away before payment
3. Return to `/register`
4. Should resume at step 3 with all data pre-filled

#### Test Case 2.3: Existing User Registration Attempt
1. Use an existing user account to go through registration flow
2. Should redirect to dashboard if already subscribed
3. Should resume at payment step if professional info complete but no subscription

### 3. Error Handling Tests

#### Test Case 3.1: Payment Failures
1. Use test card numbers that simulate failures:
   - `4000000000000002` (card declined)
   - `4000000000000069` (expired card)
   - `4000000000000127` (incorrect CVC)
2. Verify appropriate error messages are shown
3. Verify user can retry payment

#### Test Case 3.2: Auth0 Errors
1. Simulate network issues during Auth0 flow
2. Test invalid state parameters
3. Verify proper error handling and redirect to registration

### 4. API Endpoint Tests

#### Test Case 4.1: Coupon Validation
```bash
# Valid coupon test (if you have valid coupons in Stripe)
curl -X POST http://localhost:8000/api/validate-coupon/ \
  -H "Content-Type: application/json" \
  -d '{"coupon_code": "YOUR_COUPON_CODE", "plan": "monthly"}'

# Invalid coupon test
curl -X POST http://localhost:8000/api/validate-coupon/ \
  -H "Content-Type: application/json" \
  -d '{"coupon_code": "INVALID", "plan": "monthly"}'
```

#### Test Case 4.2: Professional Info Update
```bash
# Requires valid JWT token
curl -X POST http://localhost:8000/api/auth0/complete-professional-info/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "firstName": "Test",
    "lastName": "User", 
    "phone": "555-1234",
    "companyName": "Test Company"
  }'
```

## Environment Configuration Verification

### Frontend (.env)
```
VITE_AUTH0_DOMAIN=genai-030069804226358743.us.auth0.com
VITE_AUTH0_CLIENT_ID=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw
VITE_STRIPE_PUBLIC_KEY=pk_live_51MKmFTDXYH4nUgjBhJ8lIWxB9iNkkZIXV3tHKUxOKiNWk5Zlgkx4lOBtiYpAsW55OvI1U7E9Ty82nSErHQHxW7BS00YEJ4LkEq
VITE_API_URL=http://localhost:8000/api
```

### Backend (.env)
```
AUTH0_DOMAIN=genai-030069804226358743.us.auth0.com
AUTH0_CLIENT_ID=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw
AUTH0_CLIENT_SECRET=2V7D4JaCCztuKwGKXt4fwY6r--3qXcOa_wZZReKsDs9begcAEkBUwbBDLfwal9KA
STRIPE_SECRET_KEY=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
STRIPE_MONTHLY_PRICE_ID=price_1S2elxDXYH4nUgjBwy8RXl67
STRIPE_ANNUAL_PRICE_ID=price_1S2elxDXYH4nUgjBZI9k5dYr
```

## Auth0 Dashboard Configuration

Ensure your Auth0 application is configured as:
- **Application Type**: Regular Web Application
- **Callback URLs**: `http://localhost:3000/auth/callback`
- **Logout URLs**: `http://localhost:3000/login`
- **Web Origins**: `http://localhost:3000`

## New API Endpoints Added

1. `/api/auth0/complete-professional-info/` (POST) - Update user professional info
2. `/api/auth0/complete-registration/` (POST) - Complete registration with Stripe
3. `/api/validate-coupon/` (POST) - Validate Stripe coupon codes

## Files Modified

### Frontend
- `frontend/src/views/Register.vue` - Complete rewrite for Auth0 Regular Web Application flow
- `frontend/src/views/Auth0CallbackSimple.vue` - Enhanced registration flow detection

### Backend  
- `backend/core/auth0_views.py` - Added all registration endpoints with Stripe integration
- `backend/core/urls.py` - Added new endpoint routes

## Security Features Implemented

1. **State Validation**: CSRF protection with Auth0 state parameters
2. **Registration Flow Isolation**: Separate handling of login vs registration flows  
3. **Payment Security**: Stripe secure payment method creation and 3D Secure support
4. **Error Handling**: No sensitive data exposed in error messages
5. **Registration Recovery**: Secure resumption of incomplete registrations

## Next Steps for Production

1. **Testing**: Run through all test cases above
2. **Stripe Setup**: Ensure live Stripe keys and price IDs are correct
3. **Auth0 Production**: Update callback URLs for production domain
4. **Error Monitoring**: Add proper logging and error tracking
5. **User Feedback**: Replace `alert()` calls with proper UI notifications

The system is now ready for comprehensive testing and production deployment.