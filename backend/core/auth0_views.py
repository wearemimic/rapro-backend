import json
import jwt
import requests
import time
import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .authentication import create_jwt_pair_for_user, get_enhanced_user_data
from urllib.parse import urlencode, quote

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()

# Django Regular Web Application Auth0 Views - Following Auth0 Django Quickstart Exactly
@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_login_redirect(request):
    """
    Redirect to Auth0 for authentication - Regular Web Application flow
    Following Django quickstart: Auth0 redirects back to Django backend directly
    """
    domain = settings.AUTH0_DOMAIN
    client_id = settings.AUTH0_CLIENT_ID
    # Critical: Use Django backend callback URL - Auth0 will callback here
    callback_url = request.build_absolute_uri('/api/auth0/callback/')
    
    # Build Auth0 authorization URL exactly as per Django quickstart
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': callback_url,
        'scope': 'openid profile email',
        'state': 'login'
    }
    
    auth_url = f'https://{domain}/authorize?' + urlencode(params)
    print(f"🔗 Redirecting to Auth0: {auth_url}")
    print(f"🔗 Callback URL: {callback_url}")
    return redirect(auth_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_login_google(request):
    """
    Redirect to Auth0 for Google authentication - Regular Web Application flow
    """
    domain = settings.AUTH0_DOMAIN
    client_id = settings.AUTH0_CLIENT_ID
    # Critical: Use Django backend callback URL
    callback_url = request.build_absolute_uri('/api/auth0/callback/')
    
    # Build Auth0 authorization URL with Google connection
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': callback_url,
        'scope': 'openid profile email',
        'connection': 'google-oauth2',
        'state': 'login'
    }
    
    auth_url = f'https://{domain}/authorize?' + urlencode(params)
    print(f"🔗 Redirecting to Auth0 Google: {auth_url}")
    print(f"🔗 Callback URL: {callback_url}")
    return redirect(auth_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_callback(request):
    """
    Handle Auth0 callback - Regular Web Application flow
    Following Django quickstart: Django backend receives the callback directly from Auth0
    This is the key difference from SPA - Auth0 calls the backend directly
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        error_description = request.GET.get('error_description', 'Unknown error')
        print(f"❌ Auth0 error: {error} - {error_description}")
        # Redirect to frontend with error
        frontend_url = f'{settings.FRONTEND_URL}/login?error={quote(f"{error}: {error_description}")}'
        return redirect(frontend_url)
    
    if not code:
        print("❌ No authorization code received")
        frontend_url = f'{settings.FRONTEND_URL}/login?error=no_code'
        return redirect(frontend_url)
    
    try:
        print(f"✅ Django backend received authorization code: {code[:10]}...")
        
        # Exchange code for tokens with Auth0 - Server-side with client_secret
        domain = settings.AUTH0_DOMAIN
        client_id = settings.AUTH0_CLIENT_ID
        client_secret = settings.AUTH0_CLIENT_SECRET
        callback_url = request.build_absolute_uri('/api/auth0/callback/')
        
        token_url = f'https://{domain}/oauth/token'
        token_payload = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,  # This is the key - server-side with secret
            'code': code,
            'redirect_uri': callback_url
        }
        
        print(f"🔄 Exchanging code for tokens with client_secret...")
        token_response = requests.post(token_url, json=token_payload)
        
        if token_response.status_code != 200:
            print(f"❌ Token exchange failed: {token_response.status_code}")
            print(f"Response: {token_response.text}")
            frontend_url = f'{settings.FRONTEND_URL}/login?error=token_exchange_failed'
            return redirect(frontend_url)
        
        tokens = token_response.json()
        print(f"✅ Token exchange successful")
        
        # Get user info from Auth0
        userinfo_url = f'https://{domain}/userinfo'
        userinfo_headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)
        
        if userinfo_response.status_code != 200:
            print(f"❌ Failed to get user info: {userinfo_response.status_code}")
            frontend_url = f'{settings.FRONTEND_URL}/login?error=user_info_failed'
            return redirect(frontend_url)
        
        user_info = userinfo_response.json()
        email = user_info.get('email')
        print(f"✅ User info retrieved: {email}")
        
        if not email:
            print("❌ No email in user info")
            frontend_url = f'{settings.FRONTEND_URL}/login?error=no_email'
            return redirect(frontend_url)
        
        # Check if Django user already exists with active subscription
        try:
            existing_user = User.objects.get(email=email)
            
            # Check if user has an active subscription
            has_active_subscription = (
                existing_user.subscription_status == 'active' and
                (existing_user.subscription_end_date is None or existing_user.is_subscription_active)
            )
            
            if has_active_subscription or existing_user.is_superuser:
                print(f"✅ Existing user with active subscription: {email}")
                
                # Update user with latest Auth0 info
                existing_user.first_name = user_info.get('given_name', existing_user.first_name)
                existing_user.last_name = user_info.get('family_name', existing_user.last_name)
                existing_user.auth0_sub = user_info.get('sub')
                existing_user.auth_provider = auth_provider
                existing_user.save()
                
                # Create Django JWT tokens for authenticated user
                jwt_tokens = create_jwt_pair_for_user(existing_user)
                
                # Prepare user data for frontend
                user_data = {
                    'id': existing_user.id,
                    'email': existing_user.email,
                    'first_name': existing_user.first_name,
                    'last_name': existing_user.last_name,
                    'username': existing_user.username,
                    'is_active': existing_user.is_active
                }
                
                # Redirect to frontend with tokens and user data
                frontend_url = (
                    f'{settings.FRONTEND_URL}/auth/success?'
                    f'access_token={jwt_tokens["access"]}&'
                    f'refresh_token={jwt_tokens["refresh"]}&'
                    f'user={quote(json.dumps(user_data))}'
                )
                print(f"✅ Redirecting existing user to dashboard: {frontend_url[:100]}...")
                return redirect(frontend_url)
            else:
                print(f"❌ Existing user without active subscription: {email}")
                # Redirect to registration to complete payment
                frontend_url = f'{settings.FRONTEND_URL}/register?email={quote(email)}&social_login=true&message=Please complete your subscription to access the platform'
                return redirect(frontend_url)
                
        except User.DoesNotExist:
            print(f"🔄 New social login user needs to complete registration: {email}")
            # SECURITY: New users must complete registration with payment
            # Store their Auth0 info temporarily and redirect to registration
            frontend_url = f'{settings.FRONTEND_URL}/register?email={quote(email)}&social_login=true&first_name={quote(user_info.get("given_name", ""))}&last_name={quote(user_info.get("family_name", ""))}&auth0_sub={quote(user_info.get("sub", ""))}'
            print(f"✅ Redirecting new user to complete registration: {frontend_url[:100]}...")
            return redirect(frontend_url)
        
    except Exception as e:
        print(f"❌ Auth0 callback error: {str(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        frontend_url = f'{settings.FRONTEND_URL}/login?error={quote(str(e))}'
        return redirect(frontend_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_logout(request):
    """
    Logout from Auth0 and redirect to frontend
    """
    domain = settings.AUTH0_DOMAIN
    client_id = settings.AUTH0_CLIENT_ID
    return_url = f'{settings.FRONTEND_URL}/login'
    
    logout_params = {
        'client_id': client_id,
        'returnTo': return_url
    }
    
    logout_url = f'https://{domain}/v2/logout?' + urlencode(logout_params)
    return redirect(logout_url)

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([])
def auth0_exchange_code(request):
    """
    Exchange Auth0 authorization code for Django JWT tokens
    Enhanced to handle both login and registration flows
    """
    try:
        code = request.data.get('code')
        flow_type = request.data.get('flow_type', 'login')  # 'login' or 'registration'
        
        if not code:
            return Response({'message': 'Authorization code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use the same redirect_uri that was used in the authorization request
        redirect_uri = f'{settings.FRONTEND_URL}/auth/callback'
        
        print(f"Exchanging authorization code for {flow_type} flow: {code[:10]}...")
        
        # Exchange code for tokens with Auth0
        domain = settings.AUTH0_DOMAIN
        client_id = settings.AUTH0_CLIENT_ID
        client_secret = settings.AUTH0_CLIENT_SECRET
        
        token_url = f'https://{domain}/oauth/token'
        token_payload = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        print(f"Making token request to: {token_url}")
        token_response = requests.post(token_url, json=token_payload)
        
        if token_response.status_code != 200:
            print(f"Token exchange failed: {token_response.status_code}")
            print(f"Response: {token_response.text}")
            return Response(
                {'message': 'Failed to exchange authorization code', 'details': token_response.text}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tokens = token_response.json()
        print(f"✅ Token exchange successful")
        
        # Get user info from Auth0 using the access token
        userinfo_url = f'https://{domain}/userinfo'
        userinfo_headers = {
            'Authorization': f'Bearer {tokens["access_token"]}'
        }
        
        userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)
        
        if userinfo_response.status_code != 200:
            print(f"Failed to get user info: {userinfo_response.status_code}")
            return Response(
                {'message': 'Failed to get user information'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_info = userinfo_response.json()
        print(f"✅ User info retrieved: {user_info.get('email')}")
        
        # Extract auth provider from the sub field
        sub = user_info.get('sub', '')
        auth_provider = 'password'  # default
        if sub.startswith('google-oauth2|'):
            auth_provider = 'google-oauth2'
        elif sub.startswith('facebook|'):
            auth_provider = 'facebook'
        elif sub.startswith('apple|'):
            auth_provider = 'apple'
        elif sub.startswith('linkedin|'):
            auth_provider = 'linkedin'
        elif sub.startswith('windowslive|') or sub.startswith('microsoft|'):
            auth_provider = 'microsoft'
        elif sub.startswith('auth0|'):
            auth_provider = 'password'
        
        print(f"Auth provider detected: {auth_provider} from sub: {sub[:20]}...")
        
        email = user_info.get('email')
        if not email:
            return Response({'message': 'Email not found in user info'}, status=status.HTTP_400_BAD_REQUEST)
        
        # SECURITY: Check if Django user exists and has active subscription
        try:
            existing_user = User.objects.get(email=email)
            
            # Check if user has an active subscription
            has_active_subscription = (
                existing_user.subscription_status == 'active' and
                (existing_user.subscription_end_date is None or existing_user.is_subscription_active)
            )
            
            if has_active_subscription or existing_user.is_superuser:
                print(f"✅ Existing user with active subscription: {email}")
                
                # Update user with latest Auth0 info
                existing_user.first_name = user_info.get('given_name', existing_user.first_name)
                existing_user.last_name = user_info.get('family_name', existing_user.last_name)
                existing_user.auth0_sub = user_info.get('sub')
                existing_user.auth_provider = auth_provider
                existing_user.save()
                
                # Generate Django JWT tokens for authenticated user
                jwt_tokens = create_jwt_pair_for_user(existing_user)
                
                # Prepare response data
                response_data = {
                    'access': jwt_tokens['access'],
                    'refresh': jwt_tokens['refresh'],
                    'user': get_enhanced_user_data(existing_user),
                    'is_new_user': False,
                    'registration_complete': True
                }
            else:
                print(f"❌ Existing user without active subscription: {email}")
                # Return special response indicating registration needed
                return Response({
                    'message': 'Registration required',
                    'requires_registration': True,
                    'email': email,
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                    'auth0_sub': user_info.get('sub'),
                    'social_login': True
                }, status=status.HTTP_402_PAYMENT_REQUIRED)  # Payment Required
                
        except User.DoesNotExist:
            print(f"🔄 New social login user needs to complete registration: {email}")
            # SECURITY: New users must complete registration with payment
            return Response({
                'message': 'Registration required',
                'requires_registration': True,
                'email': email,
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'auth0_sub': user_info.get('sub'),
                'social_login': True,
                'is_new_user': True
            }, status=status.HTTP_402_PAYMENT_REQUIRED)  # Payment Required
        
        print(f"✅ Authenticated user response prepared")
        
        return Response(response_data)
        
    except Exception as e:
        print(f"Auth0 exchange code error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_professional_info(request):
    """
    Complete professional information for user registration
    Phase 2 of registration flow
    """
    try:
        user = request.user
        data = request.data
        
        print(f"🔄 Completing professional info for user: {user.email}")
        
        # Extract and validate professional info
        required_fields = ['firstName', 'lastName', 'phone', 'smsConsent']
        missing_fields = []
        
        for field in required_fields:
            if field == 'smsConsent':
                # SMS consent must be explicitly True
                if not data.get(field) or data.get(field) != True:
                    missing_fields.append('SMS consent')
            elif not data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return Response(
                {'message': f'Missing required fields: {", ".join(missing_fields)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update user with professional information
        user.first_name = data.get('firstName', '').strip()
        user.last_name = data.get('lastName', '').strip()
        user.phone_number = data.get('phone', '').strip()
        user.sms_consent = data.get('smsConsent', False)
        
        # Set consent date if consenting for the first time
        if data.get('smsConsent') and not user.sms_consent_date:
            from django.utils import timezone
            user.sms_consent_date = timezone.now()
        
        # Save the updated user
        user.save()
        
        print(f"✅ Professional info updated for: {user.email}")
        
        return Response({
            'status': 'success',
            'message': 'Professional information updated successfully',
            'user': get_enhanced_user_data(user)
        })
        
    except Exception as e:
        print(f"❌ Professional info completion error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated - authenticate AFTER payment
def auth0_complete_registration(request):
    """
    Complete Auth0 registration with Stripe subscription
    Phase 3 of registration flow - handles professional info + payment
    SECURITY: Authenticates user ONLY AFTER successful payment
    """
    try:
        data = request.data
        
        # Extract registration credentials (stored in sessionStorage)
        registration_email = data.get('registrationEmail')
        registration_password = data.get('registrationPassword')
        auth0_sub = data.get('auth0Sub', '')  # For social logins
        
        # Determine auth provider from auth0_sub
        auth_provider = 'password'  # default
        if auth0_sub:
            if auth0_sub.startswith('google-oauth2|'):
                auth_provider = 'google-oauth2'
            elif auth0_sub.startswith('facebook|'):
                auth_provider = 'facebook'
            elif auth0_sub.startswith('apple|'):
                auth_provider = 'apple'
            elif auth0_sub.startswith('linkedin|'):
                auth_provider = 'linkedin'
            elif auth0_sub.startswith('windowslive|') or auth0_sub.startswith('microsoft|'):
                auth_provider = 'microsoft'
            elif auth0_sub.startswith('auth0|'):
                auth_provider = 'password'
        
        if not registration_email or not registration_password:
            return Response({
                'message': 'Registration credentials required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"🔄 Processing payment for registration: {registration_email}")
        
        # Extract data
        professional_info = data.get('professionalInfo', {})
        payment_info = data.get('paymentInfo', {})
        
        # Validate required data
        if not professional_info or not payment_info:
            return Response(
                {'message': 'Both professionalInfo and paymentInfo are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # SECURITY: Process payment BEFORE authentication
        print(f"🔒 Processing payment before authentication (secure flow)")
        
        # Extract payment info
        payment_method_id = payment_info.get('paymentMethodId')
        plan = payment_info.get('plan')  # 'monthly' or 'annual'
        billing_details = payment_info.get('billingDetails', {})
        coupon_code = payment_info.get('couponCode')
        is_zero_cost = payment_info.get('isZeroCost', False)
        
        if not plan:
            return Response(
                {'message': 'Plan selection is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # For paid subscriptions, require payment method
        if not is_zero_cost and not payment_method_id:
            return Response(
                {'message': 'Payment method is required for paid subscriptions'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Stripe customer (before authentication)
        try:
            customer_data = {
                'email': registration_email,
                'name': f"{professional_info.get('firstName', '')} {professional_info.get('lastName', '')}".strip(),
                'phone': professional_info.get('phone', '')
            }
            
            # Only add payment method and billing info for paid subscriptions
            if not is_zero_cost and payment_method_id:
                customer_data.update({
                    'payment_method': payment_method_id,
                    'invoice_settings': {
                        'default_payment_method': payment_method_id
                    },
                    'address': {
                        'line1': billing_details.get('address', {}).get('line1'),
                        'city': billing_details.get('address', {}).get('city'),
                        'state': billing_details.get('address', {}).get('state'),
                        'postal_code': billing_details.get('address', {}).get('postal_code'),
                        'country': billing_details.get('address', {}).get('country', 'US')
                    }
                })
                
                # Remove None values from address
                if 'address' in customer_data:
                    customer_data['address'] = {k: v for k, v in customer_data['address'].items() if v}
            
            # Remove None values
            customer_data = {k: v for k, v in customer_data.items() if v}
            
            customer = stripe.Customer.create(**customer_data)
            print(f"✅ Stripe customer created: {customer.id}")
            
        except stripe.error.StripeError as e:
            print(f"❌ Stripe customer creation failed: {str(e)}")
            return Response(
                {'message': f'Payment setup failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine price ID based on plan
        if plan == 'monthly':
            price_id = settings.STRIPE_MONTHLY_PRICE_ID
        elif plan == 'annual':
            price_id = settings.STRIPE_ANNUAL_PRICE_ID
        else:
            return Response(
                {'message': 'Invalid plan type'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create subscription
        try:
            subscription_data = {
                'customer': customer.id,
                'items': [{'price': price_id}],
                'expand': ['latest_invoice.payment_intent'],
            }
            
            # For paid subscriptions, set incomplete payment behavior
            if not is_zero_cost:
                subscription_data['payment_behavior'] = 'default_incomplete'
            
            # Apply coupon if provided (using new discounts format)
            if coupon_code:
                subscription_data['discounts'] = [{'coupon': coupon_code}]
                print(f"✅ Applying coupon via discounts: {coupon_code}")
            
            subscription = stripe.Subscription.create(**subscription_data)
            print(f"✅ Stripe subscription created: {subscription.id}")
            
            # Store subscription end date for user creation later
            subscription_end_date = None
            if hasattr(subscription, 'current_period_end') and subscription.current_period_end:
                from datetime import datetime
                subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
            
            # Handle payment intent if needed (only for paid subscriptions)
            payment_intent = None
            requires_action = False
            
            if not is_zero_cost and subscription.latest_invoice and subscription.latest_invoice.payment_intent:
                payment_intent = subscription.latest_invoice.payment_intent
                if payment_intent.status == 'requires_action':
                    requires_action = True
                    print(f"⚠️  Payment requires additional action")
            elif is_zero_cost:
                print(f"✅ Zero-cost subscription activated immediately")
            
            # SECURITY: Create Django user ONLY after successful payment
            print(f"🔐 Payment successful, now creating Django user: {registration_email}")
            
            # Create Django user directly with professional info and payment details
            # This avoids Auth0 Resource Owner Password Grant issues
            user_defaults = {
                'username': registration_email,
                'first_name': professional_info.get('firstName', ''),
                'last_name': professional_info.get('lastName', ''),
                'phone_number': professional_info.get('phone', ''),
                'sms_consent': professional_info.get('smsConsent', False),
                'is_active': True,
                'stripe_customer_id': customer.id,
                'stripe_subscription_id': subscription.id,
                'subscription_status': subscription.status,
                'subscription_plan': plan,
                'auth_provider': auth_provider,
            }
            
            # Add subscription end date if available
            if subscription_end_date:
                user_defaults['subscription_end_date'] = subscription_end_date
            
            user, created = User.objects.get_or_create(
                email=registration_email,
                defaults=user_defaults
            )
            
            # Update existing user if needed
            if not created:
                user.first_name = professional_info.get('firstName', '')
                user.last_name = professional_info.get('lastName', '')
                user.phone_number = professional_info.get('phone', '')
                user.sms_consent = professional_info.get('smsConsent', False)
                user.stripe_customer_id = customer.id
                user.stripe_subscription_id = subscription.id
                user.subscription_status = subscription.status
                user.subscription_plan = plan
                user.auth_provider = auth_provider
                if subscription_end_date:
                    user.subscription_end_date = subscription_end_date
                user.save()
                
            print(f"✅ Django user {'created' if created else 'updated'}: {registration_email}")
            
            # Set SMS consent date if consenting for the first time
            if professional_info.get('smsConsent') and not user.sms_consent_date:
                from django.utils import timezone
                user.sms_consent_date = timezone.now()
                user.save()
            
            print(f"✅ Django user {'created' if created else 'updated'} with payment info: {registration_email}")
            
            # Generate Django JWT tokens
            jwt_tokens = create_jwt_pair_for_user(user)
            
            response_data = {
                'status': 'success',
                'message': 'Registration completed successfully' if not is_zero_cost else 'Free account activated successfully',
                'access': jwt_tokens['access'],  # Return JWT tokens
                'refresh': jwt_tokens['refresh'],
                'user': get_enhanced_user_data(user),
                'is_zero_cost': is_zero_cost,
                'subscription': {
                    'id': subscription.id,
                    'status': subscription.status,
                    'plan': plan,
                    'current_period_end': getattr(subscription, 'current_period_end', None)
                }
            }
            
            # Add payment intent info if action required
            if requires_action and payment_intent:
                response_data['payment_intent'] = {
                    'client_secret': payment_intent.client_secret,
                    'status': payment_intent.status
                }
            
            return Response(response_data)
            
        except stripe.error.StripeError as e:
            print(f"❌ Stripe subscription creation failed: {str(e)}")
            # Try to delete the customer if subscription failed
            try:
                stripe.Customer.delete(customer.id)
            except:
                pass
            return Response(
                {'message': f'Subscription creation failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        print(f"❌ Registration completion error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for Auth0 users with password authentication
    """
    try:
        user = request.user
        
        # Check if user is using password authentication
        if user.auth_provider != 'password':
            return Response({
                'message': 'Password change is only available for email/password authentication. Please use your social provider to change your password.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validate passwords
        if not new_password or not confirm_password:
            return Response({
                'message': 'Both new password and confirmation are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'message': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({
                'message': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get Auth0 Management API token
        domain = settings.AUTH0_DOMAIN
        client_id = settings.AUTH0_CLIENT_ID
        client_secret = settings.AUTH0_CLIENT_SECRET
        
        # Get management API token
        token_url = f'https://{domain}/oauth/token'
        token_payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'audience': f'https://{domain}/api/v2/'
        }
        
        token_response = requests.post(token_url, json=token_payload)
        
        if token_response.status_code != 200:
            print(f"Failed to get management token: {token_response.text}")
            return Response({
                'message': 'Failed to authenticate with Auth0'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        management_token = token_response.json()['access_token']
        
        # Get user's Auth0 ID
        # First, search for user by email in Auth0
        search_url = f'https://{domain}/api/v2/users-by-email'
        search_headers = {
            'Authorization': f'Bearer {management_token}'
        }
        search_params = {
            'email': user.email
        }
        
        search_response = requests.get(search_url, headers=search_headers, params=search_params)
        
        if search_response.status_code != 200 or not search_response.json():
            print(f"Failed to find user in Auth0: {search_response.text}")
            return Response({
                'message': 'User not found in Auth0'
            }, status=status.HTTP_404_NOT_FOUND)
        
        auth0_users = search_response.json()
        # Find the user with password connection
        auth0_user = None
        for u in auth0_users:
            if u.get('identities'):
                for identity in u['identities']:
                    if identity.get('connection') == 'Username-Password-Authentication':
                        auth0_user = u
                        break
            if auth0_user:
                break
        
        if not auth0_user:
            return Response({
                'message': 'Password authentication not found for this user'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        auth0_user_id = auth0_user['user_id']
        
        # Update password in Auth0
        update_url = f'https://{domain}/api/v2/users/{auth0_user_id}'
        update_headers = {
            'Authorization': f'Bearer {management_token}',
            'Content-Type': 'application/json'
        }
        update_payload = {
            'password': new_password,
            'connection': 'Username-Password-Authentication'
        }
        
        update_response = requests.patch(update_url, headers=update_headers, json=update_payload)
        
        if update_response.status_code != 200:
            print(f"Failed to update password: {update_response.text}")
            error_data = update_response.json() if update_response.text else {}
            error_message = error_data.get('message', 'Failed to update password')
            return Response({
                'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"✅ Password updated successfully for user: {user.email}")
        
        return Response({
            'message': 'Password updated successfully'
        })
        
    except Exception as e:
        print(f"Password change error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return Response({
            'message': 'An error occurred while changing your password'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated access for coupon validation
def validate_coupon(request):
    """
    Validate Stripe coupon code and return discount information
    Phase 4 of registration flow - supports dynamic pricing
    """
    try:
        data = request.data
        coupon_code = data.get('coupon_code', '').strip()
        plan = data.get('plan', 'monthly')  # 'monthly' or 'annual'
        
        if not coupon_code:
            return Response(
                {'message': 'Coupon code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"🔄 Validating coupon: {coupon_code} for plan: {plan}")
        
        # Try to retrieve coupon from Stripe
        try:
            coupon = stripe.Coupon.retrieve(coupon_code)
            print(f"✅ Coupon found: {coupon.id}")
            
            # Check if coupon is valid
            if not coupon.valid:
                return Response({
                    'valid': False,
                    'message': 'This coupon is no longer valid'
                })
            
            # Check if coupon has usage limits
            if coupon.max_redemptions and coupon.times_redeemed >= coupon.max_redemptions:
                return Response({
                    'valid': False,
                    'message': 'This coupon has reached its usage limit'
                })
            
            # Check if coupon is expired
            if coupon.redeem_by and coupon.redeem_by < int(time.time()):
                return Response({
                    'valid': False,
                    'message': 'This coupon has expired'
                })
            
            # Get base price for calculation
            base_price = 99 if plan == 'monthly' else 999  # Default prices
            
            # Calculate discount
            discount_amount = 0
            discount_type = 'percentage' if coupon.percent_off else 'fixed'
            
            if coupon.percent_off:
                discount_amount = coupon.percent_off
                discounted_price = base_price * (1 - coupon.percent_off / 100)
            else:
                # Handle amount_off (in cents)
                discount_amount = coupon.amount_off / 100  # Convert cents to dollars
                discounted_price = max(0, base_price - discount_amount)
            
            # Prepare response
            response_data = {
                'valid': True,
                'coupon_id': coupon.id,
                'name': coupon.name or f"Coupon {coupon.id}",
                'description': f"Save {coupon.percent_off}%" if coupon.percent_off else f"Save ${discount_amount}",
                'discount_type': discount_type,
                'discount_value': discount_amount,
                'original_price': base_price,
                'discounted_price': round(discounted_price, 2),
                'currency': coupon.currency or 'usd'
            }
            
            print(f"✅ Coupon valid: {response_data}")
            return Response(response_data)
            
        except stripe.error.StripeError as e:
            error_code = getattr(e, 'code', '')
            if error_code == 'resource_missing':
                return Response({
                    'valid': False,
                    'message': 'Invalid coupon code'
                })
            else:
                print(f"❌ Stripe coupon validation error: {str(e)}")
                return Response({
                    'valid': False,
                    'message': 'Unable to validate coupon. Please try again.'
                })
                
    except Exception as e:
        print(f"❌ Coupon validation error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_account(request):
    """
    Create Auth0 account only (no authentication)
    This avoids the Resource Owner Password Grant issues
    """
    try:
        data = request.data
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength (basic validation)
        if len(password) < 8:
            return Response({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"🔄 Creating Auth0 account (no auth): {email}")
        
        # Call Auth0's /dbconnections/signup endpoint
        auth0_domain = settings.AUTH0_DOMAIN
        signup_url = f"https://{auth0_domain}/dbconnections/signup"
        
        signup_data = {
            "client_id": settings.AUTH0_CLIENT_ID,
            "connection": "Username-Password-Authentication",
            "email": email,
            "password": password,
            "user_metadata": {
                "signup_source": "embedded_form",
                "signup_timestamp": str(int(time.time()))
            }
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Make request to Auth0
        auth0_response = requests.post(signup_url, json=signup_data, headers=headers, timeout=30)
        
        if auth0_response.status_code in [200, 201]:
            print(f"✅ Auth0 account created successfully: {email}")
            
            return Response({
                'success': True,
                'message': 'Account created successfully',
                'email': email
            })
        else:
            print(f"❌ Auth0 signup failed: {auth0_response.status_code}")
            auth0_error = auth0_response.json() if auth0_response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"📋 Auth0 error details: {auth0_error}")
            
            # Handle different error message formats
            if 'name' in auth0_error and auth0_error['name'] == 'PasswordStrengthError':
                return Response({
                    'success': False,
                    'message': 'Password does not meet requirements. Please use at least 8 characters with a mix of uppercase, lowercase, numbers, and special characters.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Handle "Invalid sign up" - usually means user already exists
            if 'code' in auth0_error and auth0_error['code'] == 'invalid_signup':
                return Response({
                    'success': True,  # Treat as success since account exists
                    'message': 'Account already exists, proceeding with registration',
                    'email': email
                })
            
            # Extract error message
            error_message = auth0_error.get('description', auth0_error.get('error_description', auth0_error.get('message', 'Account creation failed')))
            if isinstance(error_message, dict):
                error_message = auth0_error.get('message', 'Account creation failed')
            
            return Response({
                'success': False,
                'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.exceptions.Timeout:
        print("❌ Auth0 API request timed out")
        return Response({
            'success': False,
            'message': 'Request timed out. Please try again.'
        }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Auth0 API request failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to connect to authentication service. Please try again.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        print(f"❌ Account creation error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return Response({
            'success': False,
            'message': 'An unexpected error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def embedded_signup(request):
    """
    Embedded Auth0 signup using Auth0 Authentication API
    Creates user directly without redirect to Auth0 hosted pages
    """
    try:
        data = request.data
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength (basic validation)
        if len(password) < 8:
            return Response({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"🔄 Creating user via Auth0 API: {email}")
        
        # Call Auth0's /dbconnections/signup endpoint
        auth0_domain = settings.AUTH0_DOMAIN
        signup_url = f"https://{auth0_domain}/dbconnections/signup"
        
        signup_data = {
            "client_id": settings.AUTH0_CLIENT_ID,
            "connection": "Username-Password-Authentication",
            "email": email,
            "password": password,
            "user_metadata": {
                "signup_source": "embedded_form",
                "signup_timestamp": str(int(time.time()))
            }
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Make request to Auth0
        auth0_response = requests.post(signup_url, json=signup_data, headers=headers, timeout=30)
        
        if auth0_response.status_code == 200:
            auth0_data = auth0_response.json()
            print(f"✅ Auth0 user created successfully: {email}")
            
            # Now authenticate the user to get tokens
            # Use Auth0's Resource Owner Password Grant (if enabled)
            token_url = f"https://{auth0_domain}/oauth/token"
            
            token_data = {
                "grant_type": "password",
                "username": email,
                "password": password,
                "client_id": settings.AUTH0_CLIENT_ID,
                "client_secret": settings.AUTH0_CLIENT_SECRET,
                "connection": "Username-Password-Authentication",
                "scope": "openid profile email"
            }
            
            token_response = requests.post(token_url, json=token_data, headers=headers, timeout=30)
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data.get('access_token')
                
                # Get user profile from Auth0
                profile_url = f"https://{auth0_domain}/userinfo"
                profile_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                profile_response = requests.get(profile_url, headers=profile_headers, timeout=30)
                
                if profile_response.status_code == 200:
                    auth0_profile = profile_response.json()
                    
                    # Create or update local Django user
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            'username': email,
                            'first_name': auth0_profile.get('given_name', ''),
                            'last_name': auth0_profile.get('family_name', ''),
                            'auth0_sub': auth0_profile.get('sub'),
                            'is_active': True
                        }
                    )
                    
                    if not created:
                        # Update existing user's Auth0 info
                        user.auth0_sub = auth0_profile.get('sub')
                        user.save()
                    
                    print(f"✅ Django user {'created' if created else 'updated'}: {email}")
                    
                    # Generate Django JWT tokens
                    jwt_tokens = create_jwt_pair_for_user(user)
                    
                    return Response({
                        'success': True,
                        'message': 'Account created successfully',
                        'access': jwt_tokens['access'],
                        'refresh': jwt_tokens['refresh'],
                        'user': get_enhanced_user_data(user),
                        'is_new_user': created,
                        'registration_complete': False  # Still need to complete registration steps
                    })
                else:
                    print(f"❌ Failed to get user profile: {profile_response.status_code}")
                    return Response({
                        'success': False,
                        'message': 'Account created but failed to retrieve profile'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                print(f"❌ Failed to authenticate user: {token_response.status_code}")
                error_data = token_response.json() if token_response.headers.get('content-type', '').startswith('application/json') else {}
                error_message = error_data.get('error_description', 'Failed to authenticate')
                
                return Response({
                    'success': False,
                    'message': f'Account created but authentication failed: {error_message}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(f"❌ Auth0 signup failed: {auth0_response.status_code}")
            auth0_error = auth0_response.json() if auth0_response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"📋 Auth0 error details: {auth0_error}")
            
            # Handle different error message formats
            if 'name' in auth0_error and auth0_error['name'] == 'PasswordStrengthError':
                return Response({
                    'success': False,
                    'message': 'Password does not meet requirements. Please use at least 8 characters with a mix of uppercase, lowercase, numbers, and special characters.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Handle "Invalid sign up" - usually means user already exists
            if 'code' in auth0_error and auth0_error['code'] == 'invalid_signup':
                print(f"🔍 User may already exist, attempting login for: {email}")
                
                # Try to authenticate the existing user instead
                token_url = f"https://{auth0_domain}/oauth/token"
                token_data = {
                    "grant_type": "password",
                    "username": email,
                    "password": password,
                    "client_id": settings.AUTH0_CLIENT_ID,
                    "client_secret": settings.AUTH0_CLIENT_SECRET,
                    "connection": "Username-Password-Authentication",
                    "scope": "openid profile email"
                }
                
                token_response = requests.post(token_url, json=token_data, headers=headers, timeout=30)
                
                if token_response.status_code == 200:
                    print(f"✅ User authenticated successfully: {email}")
                    token_data = token_response.json()
                    access_token = token_data.get('access_token')
                    
                    # Get user profile from Auth0
                    profile_url = f"https://{auth0_domain}/userinfo"
                    profile_headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    profile_response = requests.get(profile_url, headers=profile_headers, timeout=30)
                    
                    if profile_response.status_code == 200:
                        auth0_profile = profile_response.json()
                        print(f"✅ Retrieved user profile: {auth0_profile.get('email')}")
                        
                        # Create or update local Django user
                        user, created = User.objects.get_or_create(
                            email=email,
                            defaults={
                                'username': email,
                                'first_name': auth0_profile.get('given_name', ''),
                                'last_name': auth0_profile.get('family_name', ''),
                                'auth0_sub': auth0_profile.get('sub'),
                                'is_active': True
                            }
                        )
                        
                        if not created:
                            # Update existing user's Auth0 info
                            user.auth0_sub = auth0_profile.get('sub')
                            user.save()
                        
                        print(f"✅ Django user {'created' if created else 'found'}: {email}")
                        
                        # Generate Django JWT tokens
                        jwt_tokens = create_jwt_pair_for_user(user)
                        
                        return Response({
                            'success': True,
                            'message': 'Account accessed successfully',
                            'access': jwt_tokens['access'],
                            'refresh': jwt_tokens['refresh'],
                            'user': get_enhanced_user_data(user),
                            'is_new_user': created,
                            'registration_complete': False  # Still need to complete registration steps
                        })
                    else:
                        print(f"❌ Failed to get user profile: {profile_response.status_code}")
                else:
                    print(f"❌ Failed to authenticate existing user: {token_response.status_code}")
                    return Response({
                        'success': False,
                        'message': 'An account with this email already exists, but the password is incorrect. Please check your password or use the forgot password option.'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Extract error message (handle both string and dict formats)
            error_message = auth0_error.get('description', auth0_error.get('error_description', auth0_error.get('message', 'Signup failed')))
            if isinstance(error_message, dict):
                error_message = auth0_error.get('message', 'Signup failed')
            
            print(f"📋 Extracted error message: {error_message}")
            
            # Handle specific error cases
            if isinstance(error_message, str):
                if 'user already exists' in error_message.lower():
                    return Response({
                        'success': False,
                        'message': 'An account with this email already exists. Please try logging in instead.'
                    }, status=status.HTTP_409_CONFLICT)
                elif auth0_response.status_code == 400:
                    # For 400 errors, provide more specific messaging
                    if 'password' in error_message.lower():
                        return Response({
                            'success': False,
                            'message': 'Password does not meet requirements. Please choose a stronger password.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    elif 'email' in error_message.lower():
                        return Response({
                            'success': False,
                            'message': 'Please enter a valid email address.'
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': False,
                'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.exceptions.Timeout:
        print("❌ Auth0 API request timed out")
        return Response({
            'success': False,
            'message': 'Request timed out. Please try again.'
        }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Auth0 API request failed: {str(e)}")
        return Response({
            'success': False,
            'message': 'Unable to connect to authentication service. Please try again.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        print(f"❌ Embedded signup error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return Response({
            'success': False,
            'message': 'An unexpected error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)