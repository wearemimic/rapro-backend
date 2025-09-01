import json
import jwt
import requests
import time
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .authentication import create_jwt_pair_for_user, get_enhanced_user_data
from urllib.parse import urlencode
from django.core.paginator import Paginator
from django.db.models import Q

User = get_user_model()

def get_auth0_management_token():
    """
    Get Auth0 Management API token
    """
    domain = settings.AUTH0_DOMAIN
    client_id = settings.AUTH0_CLIENT_ID
    client_secret = settings.AUTH0_CLIENT_SECRET
    
    token_url = f'https://{domain}/oauth/token'
    token_payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'audience': f'https://{domain}/api/v2/',
        'grant_type': 'client_credentials'
    }
    
    token_response = requests.post(token_url, json=token_payload)
    token_data = token_response.json()
    
    if 'access_token' not in token_data:
        raise Exception('Failed to get Auth0 management token')
    
    return token_data['access_token']

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([])  # Disable throttling for Auth0 authentication
def auth0_login(request):
    """
    Exchange Auth0 token for Django JWT token
    """
    try:
        print(f"Auth0 login attempt from {request.META.get('REMOTE_ADDR', 'unknown')}")
        
        # Get the Auth0 token from the request
        auth0_token = request.data.get('auth0Token')
        if not auth0_token:
            print("Error: No Auth0 token provided")
            return Response({'message': 'Auth0 token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Auth0 token received, length: {len(auth0_token)}")

        # Verify the Auth0 token
        domain = settings.AUTH0_DOMAIN
        audience = settings.AUTH0_AUDIENCE or settings.AUTH0_CLIENT_ID  # Use audience from settings
        
        print(f"Using Auth0 domain: {domain}")
        print(f"Using Auth0 audience: {audience}")
        
        # Get the JWKS (JSON Web Key Set) from Auth0
        jwks_url = f'https://{domain}/.well-known/jwks.json'
        print(f"Fetching JWKS from: {jwks_url}")
        
        jwks_response = requests.get(jwks_url)
        if jwks_response.status_code != 200:
            print(f"Failed to fetch JWKS: {jwks_response.status_code}")
            return Response({'message': 'Failed to fetch Auth0 keys'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        jwks = jwks_response.json()
        print(f"JWKS fetched successfully, keys count: {len(jwks.get('keys', []))}")
        
        # Decode the token header to get the key ID
        try:
            token_header = jwt.get_unverified_header(auth0_token)
            key_id = token_header.get('kid')
            print(f"Token key ID: {key_id}")
        except Exception as e:
            print(f"Failed to decode token header: {str(e)}")
            return Response({'message': 'Invalid token format'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Find the matching key in the JWKS
        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == key_id:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
                break
        
        if not rsa_key:
            print(f"No matching key found for kid: {key_id}")
            return Response({'message': 'Invalid token key'}, status=status.HTTP_401_UNAUTHORIZED)
        
        print("RSA key found, decoding token...")
        
        # Decode and verify the token
        payload = jwt.decode(
            auth0_token,
            rsa_key,
            algorithms=[settings.AUTH0_ALGORITHM],
            audience=audience,
            issuer=f'https://{domain}/'
        )
        
        print(f"Token decoded successfully, subject: {payload.get('sub')}")
        
        # Get user info from payload
        email = payload.get('email')
        if not email:
            return Response({'message': 'Email not found in token'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'is_active': True,
                'first_name': payload.get('given_name', ''),
                'last_name': payload.get('family_name', '')
            }
        )
        
        # Generate Django JWT token with admin claims
        tokens = create_jwt_pair_for_user(user)
        
        # Return the token and user info
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': get_enhanced_user_data(user)
        })
    
    except jwt.ExpiredSignatureError:
        print("JWT token has expired")
        return Response({'message': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError as e:
        print(f"Invalid JWT token: {str(e)}")
        return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(f"Auth0 login exception: {str(e)}")
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def auth0_debug(request):
    """
    Debug endpoint to check Auth0 configuration (remove in production)
    """
    try:
        from django.conf import settings
        
        config_info = {
            'domain': settings.AUTH0_DOMAIN,
            'client_id': settings.AUTH0_CLIENT_ID,
            'audience': getattr(settings, 'AUTH0_AUDIENCE', 'Not set'),
            'algorithm': settings.AUTH0_ALGORITHM,
            'has_secret': bool(settings.AUTH0_CLIENT_SECRET and settings.AUTH0_CLIENT_SECRET != 'your-auth0-client-secret'),
            'jwks_url': f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
        }
        
        # Test JWKS endpoint
        try:
            import requests
            jwks_response = requests.get(config_info['jwks_url'], timeout=5)
            config_info['jwks_accessible'] = jwks_response.status_code == 200
            config_info['jwks_keys_count'] = len(jwks_response.json().get('keys', [])) if jwks_response.status_code == 200 else 0
        except Exception as e:
            config_info['jwks_accessible'] = False
            config_info['jwks_error'] = str(e)
        
        return Response(config_info)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([])  # Disable throttling for Auth0 authentication
def auth0_exchange_code(request):
    """
    Exchange Auth0 authorization code for tokens and create Django session
    """
    try:
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        
        if not code:
            return Response({'message': 'Authorization code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not redirect_uri:
            return Response({'message': 'Redirect URI is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Exchanging authorization code: {code[:10]}...")
        
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
        
        # Create or get user in Django
        email = user_info.get('email')
        if not email:
            print(f"❌ No email in user_info: {user_info}")
            return Response({'message': 'Email not found in user info'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"🔍 Auth0 returned email: '{email}'")
        print(f"🔍 Full user_info from Auth0: {user_info}")
        
        # Check if user exists first, and handle accordingly
        # Try case-insensitive lookup first
        try:
            user = User.objects.get(email__iexact=email)
            print(f"✅ Retrieved existing user: {user.email} (matched '{email}')")
            created = False
        except User.DoesNotExist:
            # User doesn't exist in our Django system
            print(f"❌ User '{email}' not found in Django system")
            print(f"🔍 Available users in system:")
            for existing_user in User.objects.all():
                print(f"   - {existing_user.email} (active: {existing_user.is_active})")
            print(f"🔍 Looking for exact match vs case-insensitive...")
            
            # For new users coming from Auth0, we need to check if they completed registration
            # If they're here, they successfully authenticated with Auth0 but we don't have them in Django
            # This means they might have used social login but never completed our registration process
            
            # Create a basic user record, but mark them as needing to complete registration
            user = User.objects.create_user(
                username=email,
                email=email,
                is_active=False,  # Inactive until they complete registration
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', '')
            )
            print(f"✅ Created placeholder user: {email} (inactive, needs registration)")
            created = True
            
            # Return a special response indicating they need to complete registration
            return Response({
                'message': 'Account authentication successful, but registration is incomplete.',
                'code': 'REGISTRATION_INCOMPLETE',
                'action': 'complete_registration',
                'user_email': email
            }, status=status.HTTP_202_ACCEPTED)
        
        # Check if user is active (completed registration)
        if not user.is_active:
            print(f"❌ User {email} exists but is inactive (incomplete registration)")
            return Response({
                'message': 'Account found but registration is incomplete. Please complete your registration.',
                'code': 'REGISTRATION_INCOMPLETE',
                'action': 'complete_registration',
                'user_email': email
            }, status=status.HTTP_202_ACCEPTED)
        
        # Generate Django JWT token with admin claims
        tokens = create_jwt_pair_for_user(user)
        
        response_data = {
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': get_enhanced_user_data(user)
        }
        
        print(f"✅ Successful auth response for {user.email}: {response_data}")
        return Response(response_data)
    
    except Exception as e:
        print(f"❌ Auth0 code exchange exception: {str(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return Response({
            'message': f'Authentication failed: {str(e)}',
            'error': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth0_complete_registration(request):
    """
    Complete Auth0 user registration with professional info and payment
    """
    try:
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        user = request.user
        data = request.data
        
        # Step 1: Update user profile with professional info and activate account
        professional_info = data.get('professionalInfo', {})
        if professional_info:
            user.first_name = professional_info.get('firstName', user.first_name)
            user.last_name = professional_info.get('lastName', user.last_name)
            # Add other professional fields if your user model supports them
            
            # Activate the user account now that they're completing registration
            user.is_active = True
            user.save()
            print(f"✅ Updated user profile and activated account for: {user.email}")
        
        # Step 2: Create Stripe customer if not exists
        if not user.stripe_customer_id:
            try:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}",
                    metadata={
                        'user_id': user.id,
                        'auth0_user': True
                    }
                )
                user.stripe_customer_id = customer.id
                user.save()
                print(f"✅ Created Stripe customer: {customer.id}")
            except Exception as e:
                print(f"❌ Failed to create Stripe customer: {str(e)}")
                return Response({
                    'message': 'Failed to create customer account'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Step 3: Handle payment if provided
        payment_info = data.get('paymentInfo')
        if payment_info:
            payment_method_id = payment_info.get('paymentMethodId')
            plan = payment_info.get('plan', 'monthly')
            coupon_code = payment_info.get('couponCode')
            
            if not payment_method_id:
                return Response({
                    'message': 'Payment method is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=user.stripe_customer_id,
            )
            
            # Set as default payment method
            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
            
            # Get the price ID based on the plan
            price_id = settings.STRIPE_MONTHLY_PRICE_ID if plan == 'monthly' else settings.STRIPE_ANNUAL_PRICE_ID
            
            # Prepare subscription creation parameters
            subscription_params = {
                'customer': user.stripe_customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': 'default_incomplete',
                'expand': ['latest_invoice.payment_intent'],
                'metadata': {
                    'user_id': user.id,
                    'plan': plan,
                    'auth0_user': True
                }
            }
            
            # Add coupon if provided
            if coupon_code:
                subscription_params['coupon'] = coupon_code
                print(f"✅ Applying coupon code: {coupon_code}")
            
            # Create the subscription
            subscription = stripe.Subscription.create(**subscription_params)
            
            # Save subscription ID to user model
            user.stripe_subscription_id = subscription.id
            user.subscription_status = subscription.status
            user.save()
            
            print(f"✅ Created subscription: {subscription.id}")
            
            return Response({
                'status': 'success',
                'message': 'Registration completed successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'subscription_status': user.subscription_status
                },
                'subscription': {
                    'id': subscription.id,
                    'status': subscription.status,
                    'client_secret': subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice.payment_intent else None
                }
            })
        else:
            # Just update profile without payment
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
    
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {str(e)}")
        return Response({
            'message': f'Payment processing failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"❌ Registration completion error: {str(e)}")
        return Response({
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def auth0_signup(request):
    """
    Create a new user via Auth0
    """
    try:
        # Get user data from request
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return Response({'message': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user in Auth0
        domain = settings.AUTH0_DOMAIN
        
        # Get Auth0 management API token
        try:
            management_token = get_auth0_management_token()
        except Exception as e:
            return Response({'message': 'Failed to get Auth0 management token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create user in Auth0
        create_url = f'https://{domain}/api/v2/users'
        create_headers = {
            'Authorization': f'Bearer {management_token}',
            'Content-Type': 'application/json'
        }
        
        create_payload = {
            'email': email,
            'password': password,
            'connection': 'Username-Password-Authentication',
            'email_verified': False,
            'given_name': data.get('first_name', ''),
            'family_name': data.get('last_name', '')
        }
        
        create_response = requests.post(create_url, headers=create_headers, json=create_payload)
        
        if create_response.status_code != 201:
            return Response({'message': 'Failed to create user in Auth0', 'details': create_response.json()}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create user in Django
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,  # This will be hashed by Django
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        # Generate JWT token with admin claims
        tokens = create_jwt_pair_for_user(user)
        
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': get_enhanced_user_data(user)
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    List all users with pagination and search
    """
    try:
        # Get query parameters
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        search = request.GET.get('search', '')
        
        # Query users from Django database
        users = User.objects.all()
        
        # Apply search filter if provided
        if search:
            users = users.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search)
            )
        
        # Paginate results
        paginator = Paginator(users, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize user data
        users_data = []
        for user in page_obj:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'subscription_status': user.subscription_status,
                'stripe_customer_id': user.stripe_customer_id
            })
        
        return Response({
            'users': users_data,
            'total': paginator.count,
            'page': page_obj.number,
            'pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })
    
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    """
    Get, update, or delete a specific user
    """
    try:
        # Get the user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            # Return user details
            return Response({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'subscription_status': user.subscription_status,
                'stripe_customer_id': user.stripe_customer_id
            })
        
        elif request.method == 'PUT':
            # Update user in both Django and Auth0
            data = request.data
            
            # Update Django user
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            user.save()
            
            # Update user in Auth0
            try:
                management_token = get_auth0_management_token()
                domain = settings.AUTH0_DOMAIN
                
                # Find Auth0 user by email
                search_url = f'https://{domain}/api/v2/users-by-email?email={user.email}'
                search_headers = {
                    'Authorization': f'Bearer {management_token}'
                }
                
                search_response = requests.get(search_url, headers=search_headers)
                auth0_users = search_response.json()
                
                if auth0_users:
                    auth0_user_id = auth0_users[0]['user_id']
                    
                    # Update Auth0 user
                    update_url = f'https://{domain}/api/v2/users/{auth0_user_id}'
                    update_headers = {
                        'Authorization': f'Bearer {management_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    update_payload = {}
                    if 'first_name' in data:
                        update_payload['given_name'] = data['first_name']
                    if 'last_name' in data:
                        update_payload['family_name'] = data['last_name']
                    
                    if update_payload:
                        requests.patch(update_url, headers=update_headers, json=update_payload)
            
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to update user in Auth0: {str(e)}")
            
            return Response({
                'message': 'User updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active
                }
            })
        
        elif request.method == 'DELETE':
            # Delete user from both Django and Auth0
            email = user.email
            
            # Delete from Auth0 first
            try:
                management_token = get_auth0_management_token()
                domain = settings.AUTH0_DOMAIN
                
                # Find Auth0 user by email
                search_url = f'https://{domain}/api/v2/users-by-email?email={email}'
                search_headers = {
                    'Authorization': f'Bearer {management_token}'
                }
                
                search_response = requests.get(search_url, headers=search_headers)
                auth0_users = search_response.json()
                
                if auth0_users:
                    auth0_user_id = auth0_users[0]['user_id']
                    
                    # Delete Auth0 user
                    delete_url = f'https://{domain}/api/v2/users/{auth0_user_id}'
                    delete_headers = {
                        'Authorization': f'Bearer {management_token}'
                    }
                    
                    requests.delete(delete_url, headers=delete_headers)
            
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to delete user from Auth0: {str(e)}")
            
            # Delete from Django
            user.delete()
            
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_coupon(request):
    """
    Validate a coupon code and return discount information
    """
    try:
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        coupon_code = request.data.get('coupon_code')
        plan = request.data.get('plan', 'monthly')
        
        if not coupon_code:
            return Response({
                'valid': False,
                'message': 'Coupon code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve coupon from Stripe
            coupon = stripe.Coupon.retrieve(coupon_code)
            
            # Check if coupon is valid
            if not coupon.valid:
                return Response({
                    'valid': False,
                    'message': 'This coupon is no longer valid'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if coupon has expired
            if coupon.redeem_by and coupon.redeem_by < int(time.time()):
                return Response({
                    'valid': False,
                    'message': 'This coupon has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if max redemptions reached
            if coupon.max_redemptions and coupon.times_redeemed >= coupon.max_redemptions:
                return Response({
                    'valid': False,
                    'message': 'This coupon has reached its usage limit'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Determine discount type and value
            discount_type = 'percentage' if coupon.percent_off else 'fixed'
            discount_value = coupon.percent_off if coupon.percent_off else (coupon.amount_off / 100)  # Convert cents to dollars
            
            # Create description
            if discount_type == 'percentage':
                description = f"{discount_value}% off"
            else:
                description = f"${discount_value} off"
            
            if coupon.duration == 'repeating':
                description += f" for {coupon.duration_in_months} months"
            elif coupon.duration == 'once':
                description += " (first payment only)"
            
            return Response({
                'valid': True,
                'coupon_id': coupon.id,
                'name': coupon.name or f"Coupon {coupon_code}",
                'description': description,
                'discount_type': discount_type,
                'discount_value': discount_value,
                'duration': coupon.duration,
                'duration_in_months': coupon.duration_in_months
            })
            
        except stripe.error.InvalidRequestError:
            return Response({
                'valid': False,
                'message': 'Invalid coupon code'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"❌ Coupon validation error: {str(e)}")
        return Response({
            'valid': False,
            'message': 'Failed to validate coupon'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_user_password(request, user_id):
    """
    Send password reset email to user via Auth0
    """
    try:
        # Get the user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Send password reset via Auth0
        domain = settings.AUTH0_DOMAIN
        client_id = settings.AUTH0_CLIENT_ID
        
        reset_url = f'https://{domain}/dbconnections/change_password'
        reset_payload = {
            'client_id': client_id,
            'email': user.email,
            'connection': 'Username-Password-Authentication'
        }
        
        reset_response = requests.post(reset_url, json=reset_payload)
        
        if reset_response.status_code == 200:
            return Response({'message': 'Password reset email sent successfully'})
        else:
            return Response(
                {'message': 'Failed to send password reset email', 'details': reset_response.text}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 