import requests
import os
import sys
import tempfile
import shutil
from django.contrib.auth import authenticate
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .throttles import LoginRateThrottle
from .serializers import CustomUserSerializer, UserSerializer, ClientSerializer
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Scenario, Client, RealEstate, ReportTemplate, TemplateSlide, IncomeSource
from rest_framework.exceptions import PermissionDenied
from .serializers import ClientDetailSerializer, ClientEditSerializer, ClientCreateSerializer, RealEstateSerializer
from .serializers import ScenarioCreateSerializer, ScenarioUpdateSerializer, IncomeSourceUpdateSerializer
from .serializers import ReportTemplateSerializer, ReportTemplateDetailSerializer, TemplateSlideSerializer
from .scenario_processor import ScenarioProcessor
from django.http import HttpResponse, JsonResponse
import logging
from .serializers import AdvisorRegistrationSerializer
import stripe
from django.conf import settings
from rest_framework import viewsets
import json
from PIL import Image, ImageDraw
from io import BytesIO
import uuid
from .pptx_utils import create_enhanced_thumbnails
from pptx_to_png import convert_pptx_to_png
from decimal import Decimal, InvalidOperation

# Add the python-pptx library for handling PowerPoint files
try:
    from pptx import Presentation
except ImportError:
    # We'll handle this in the view with a proper error response
    pass

User = get_user_model()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def home_view(request):
    return render(request, 'home.html')

# @csrf_exempt
@api_view(['GET', 'POST'])
@throttle_classes([LoginRateThrottle])
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'GET':
        return Response({"message": "Use POST to login."}, status=200)

    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'message': 'Email and password are required'}, status=400)

    user_obj = User.objects.filter(email=email).first()
    if user_obj is None:
        return Response({'message': 'Invalid credentials'}, status=401)

    user = authenticate(request, username=user_obj.email, password=password)
    if user is None:
        return Response({'message': 'Invalid credentials'}, status=401)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        # Blacklist the refresh token (if used)
        refresh_token = request.data.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data
    if User.objects.filter(email=data.get('email')).exists():
        return Response({'message': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=data.get('email'),
        email=data.get('email'),
        password=data.get('password'),
        first_name=data.get('firstName'),
        last_name=data.get('lastName')
    )
    # return Response({'message': 'User created'}, status=status.HTTP_201_CREATED)
    #user = User.objects.create_user(username=email, email=email, password=password)

    # ✅ Generate JWT token
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def run_scenario_calculation(request, scenario_id):
    try:
        scenario = Scenario.objects.get(id=scenario_id)
        # New instantiation: only pass scenario_id and debug
        processor = ScenarioProcessor(scenario_id=scenario.id, debug=True)
        result = processor.calculate()
        return Response(result)
    except Scenario.DoesNotExist:
        return Response({"error": "Scenario not found."}, status=404)
    
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        # Handle file uploads
        data = request.data.copy()
        
        # Handle empty string for website_url to prevent validation errors
        if 'website_url' in data and data['website_url'] == '':
            data['website_url'] = None
        
        # Create a serializer with the data and possible file
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            # Handle logo file upload separately if present
            if 'logo' in request.FILES:
                user.logo = request.FILES['logo']
                user.save(update_fields=['logo'])
            
            # Save the rest of the data
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Return detailed error messages
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_scenario(request, client_id):
    try:
        client = Client.objects.get(id=client_id, advisor=request.user)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found or access denied.'}, status=404)

    data = request.data.copy()
    data['client'] = client.id

    serializer = ScenarioCreateSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        scenario = serializer.save()
        return Response({'id': scenario.id}, status=201)
    else:
        return Response(serializer.errors, status=400)  

@csrf_exempt
def proxy_to_wealthbox(request):
    api_key = '020dfe66ac3f4213beefb36641a96721'  # Replace with your actual API key
    # Log the incoming request path
    print(f"Received request path: {request.path}")
    url = f"https://api.crmworkspace.com/{request.path.replace('/proxy', '')}"
    print(f"Proxying request to URL: {url}")
    headers = {'ACCESS_TOKEN': api_key}

    try:
        response = requests.get(url, headers=headers)
        # Log the response status code
        # self._log_debug(f"Response status code: {response.status_code}")
        return JsonResponse(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


class AdvisorClientListView(generics.ListAPIView):
    serializer_class = ClientSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(advisor=self.request.user)
    
  
class ClientDetailView(generics.RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        client = get_object_or_404(Client, pk=self.kwargs['pk'])
        print(f"Client advisor ID: {client.advisor.id}")
        print(f"Requesting user ID: {self.request.user.id}")
        if client.advisor != self.request.user:
            raise PermissionDenied("You do not have permission to view this client.")
        return client
    
class ClientEditView(generics.RetrieveUpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientEditSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Client.objects.all()
        return Client.objects.filter(advisor=user)

    def get_object(self):
        client = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        return client
    
class ClientCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = ClientCreateSerializer(data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            validated_data = serializer.validated_data.copy()
            validated_data.pop('advisor', None)  # Remove advisor if it's already in validated_data
            client = serializer.save(advisor=self.request.user)
            return Response(ClientDetailSerializer(client).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ScenarioCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, client_id):
        serializer = ScenarioCreateSerializer(data=request.data, context={'request': request, 'client_id': client_id})
        if serializer.is_valid():
            scenario = serializer.save()
            return Response({'id': scenario.id, 'message': 'Scenario created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scenario_assets(request, scenario_id):
    try:
        scenario = Scenario.objects.get(id=scenario_id)
        assets = scenario.income_sources.all()
        asset_details = [
            {
                'id': asset.id,
                'owned_by': asset.owned_by,
                'income_type': asset.income_type,
                'income_name': asset.income_name,
                'current_asset_balance': asset.current_asset_balance,
                'monthly_amount': asset.monthly_amount,
                'monthly_contribution': asset.monthly_contribution,
                'age_to_begin_withdrawal': asset.age_to_begin_withdrawal,
                'age_to_end_withdrawal': asset.age_to_end_withdrawal,
                'rate_of_return': asset.rate_of_return,
                'cola': asset.cola,
                'exclusion_ratio': asset.exclusion_ratio,
                'tax_rate': asset.tax_rate,
                'scenario_id': asset.scenario_id
            }
            for asset in assets
        ]
        return Response(asset_details)
    except Scenario.DoesNotExist:
        return Response({'error': 'Scenario not found.'}, status=404)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_scenario(request, scenario_id):
    """
    Update a scenario with Roth conversion parameters
    """
    try:
        scenario = Scenario.objects.get(id=scenario_id)
        
        # Check if the user has access to this scenario
        if scenario.client.advisor != request.user:
            return Response(
                {"error": "You don't have permission to modify this scenario"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ScenarioUpdateSerializer(scenario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Scenario.DoesNotExist:
        return Response({'error': 'Scenario not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_scenario_assets(request, scenario_id):
    """
    Update assets associated with a scenario, particularly for Roth conversion
    """
    try:
        scenario = Scenario.objects.get(id=scenario_id)
        
        # Check if the user has access to this scenario
        if scenario.client.advisor != request.user:
            return Response(
                {"error": "You don't have permission to modify this scenario's assets"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'assets' not in request.data:
            return Response(
                {"error": "Assets data is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assets_data = request.data['assets']
        updated_assets = []
        
        for asset_data in assets_data:
            asset_id = asset_data.get('id')
            if not asset_id:
                continue
                
            try:
                asset = IncomeSource.objects.get(id=asset_id, scenario=scenario)
                
                # Only update max_to_convert field
                if 'max_to_convert' in asset_data:
                    asset.max_to_convert = asset_data['max_to_convert']
                    asset.save()
                    updated_assets.append({
                        'id': asset.id,
                        'income_type': asset.income_type,
                        'max_to_convert': asset.max_to_convert
                    })
            except IncomeSource.DoesNotExist:
                # Skip assets that don't exist or don't belong to this scenario
                continue
        
        return Response({
            'message': f'Updated {len(updated_assets)} assets',
            'assets': updated_assets
        })
    except Scenario.DoesNotExist:
        return Response({'error': 'Scenario not found.'}, status=status.HTTP_404_NOT_FOUND)

class RothOptimizeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            scenario = request.data.get('scenario')
            client = request.data.get('client')
            spouse = request.data.get('spouse')
            assets = request.data.get('assets')
            optimizer_params = request.data.get('optimizer_params')
            
            print("Received data:")
            print(f"Scenario: {scenario}")
            print(f"Client: {client}")
            print(f"Spouse: {spouse}")
            print(f"Assets count: {len(assets) if assets else 0}")
            print(f"Optimizer params: {optimizer_params}")
            
            if not optimizer_params:
                print("ERROR: Missing optimizer_params")
                return Response({'error': 'Missing optimizer_params'}, status=status.HTTP_400_BAD_REQUEST)
            
            mode = optimizer_params.get('mode', 'auto')  # default to auto if not specified

            if not scenario or not client or assets is None or not optimizer_params:
                missing = []
                if not scenario: missing.append('scenario')
                if not client: missing.append('client')
                if assets is None: missing.append('assets')
                if not optimizer_params: missing.append('optimizer_params')
                error_msg = f"Missing required fields: {', '.join(missing)}"
                print(f"ERROR: {error_msg}")
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

            if mode == 'manual':
                # Manual mode: straight calculation
                try:
                    years_to_convert = int(optimizer_params.get('years_to_convert', 1))
                    start_year = int(optimizer_params.get('conversion_start_year', scenario.get('current_year', 2025)))
                    
                    # Sum max_to_convert for selected assets
                    total_to_convert = Decimal('0')
                    for asset in assets:
                        if asset.get('max_to_convert'):
                            try:
                                max_to_convert = Decimal(str(asset.get('max_to_convert', '0')))
                                total_to_convert += max_to_convert
                            except (ValueError, TypeError, InvalidOperation):
                                print(f"Warning: Invalid max_to_convert value: {asset.get('max_to_convert')}")
                    
                    # Calculate annual conversion amount
                    annual_conversion = Decimal('0')
                    if years_to_convert > 0:
                        annual_conversion = total_to_convert / Decimal(str(years_to_convert))

                    # Prepare the scenario with conversion parameters
                    scenario_manual = {
                        **scenario,
                        'roth_conversion_start_year': start_year,
                        'roth_conversion_duration': years_to_convert,
                        'roth_conversion_annual_amount': annual_conversion
                    }
                    
                    # Ensure required fields are present
                    if 'part_b_inflation_rate' not in scenario_manual:
                        scenario_manual['part_b_inflation_rate'] = 3.0
                    if 'part_d_inflation_rate' not in scenario_manual:
                        scenario_manual['part_d_inflation_rate'] = 3.0
                    if 'retirement_age' not in scenario_manual:
                        scenario_manual['retirement_age'] = 65
                    if 'mortality_age' not in scenario_manual:
                        scenario_manual['mortality_age'] = 90

                    # Create ScenarioProcessor instance with debug enabled
                    try:
                        processor = ScenarioProcessor.from_dicts(
                            scenario=scenario_manual,
                            client=client,
                            spouse=spouse,
                            assets=assets,
                            debug=True  # Enable debug logging
                        )
                    except Exception as e:
                        print(f"ERROR creating ScenarioProcessor: {e}")
                        return Response({'error': f'Error initializing scenario processor: {str(e)}'}, 
                                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # Calculate year by year results
                    try:
                        year_by_year = processor.calculate()
                    except Exception as e:
                        print(f"ERROR calculating scenario: {e}")
                        return Response({'error': f'Error calculating scenario: {str(e)}'}, 
                                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # Filter results to only include years from the start year
                    year_by_year = [row for row in year_by_year if row.get('year', 0) >= start_year]

                    # Extract metrics for the conversion period
                    try:
                        metrics = RothConversionOptimizer._extract_metrics(self=None, results=year_by_year)
                    except Exception as e:
                        print(f"ERROR extracting metrics: {e}")
                        metrics = {
                            'lifetime_tax': 0,
                            'lifetime_medicare': 0,
                            'total_irmaa': 0,
                            'final_roth': 0,
                            'cumulative_net_income': 0,
                            'income_stability': 0
                        }

                    # Log the conversion schedule
                    print(f"Manual Roth Conversion Schedule:")
                    print(f"Start Year: {start_year}")
                    print(f"Duration: {years_to_convert} years")
                    print(f"Total to Convert: ${total_to_convert:,.2f}")
                    print(f"Annual Amount: ${annual_conversion:,.2f}")

                    return Response({
                        "optimal_schedule": {
                            "start_year": start_year,
                            "duration": years_to_convert,
                            "annual_amount": annual_conversion,
                            "total_amount": total_to_convert,
                            "score_breakdown": metrics
                        },
                        "baseline": {},
                        "comparison": {},
                        "year_by_year": year_by_year
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    print(f"ERROR in manual mode: {e}")
                    return Response({'error': f'Error in manual mode: {str(e)}'}, 
                                   status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Auto mode: run optimizer as before
                optimizer = RothConversionOptimizer(scenario, client, spouse, assets, optimizer_params)
                result = optimizer.run()
                # Filter results to only years >= roth_conversion_start_year if set
                filter_year = optimizer_params.get('conversion_start_year') or scenario.get('roth_conversion_start_year')
                if filter_year and result.get('year_by_year'):
                    try:
                        filter_year = int(filter_year)
                        result['year_by_year'] = [row for row in result['year_by_year'] if row.get('year', 0) >= filter_year]
                    except Exception:
                        pass
                return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_advisor(request):
    """
    Register a new advisor (Step 1 and 2)
    """
    serializer = AdvisorRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # Create the user
            user = serializer.save()
            
            # Create Stripe customer
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
                metadata={
                    'user_id': user.id,
                    'company_name': user.company_name
                }
            )
            
            # Save Stripe customer ID to user model
            user.stripe_customer_id = stripe_customer.id
            user.save()

            # Generate tokens for automatic login
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': 'Advisor registered successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If there's an error, delete the user if it was created
            if 'user' in locals():
                user.delete()
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_registration(request):
    """
    Complete advisor registration with payment (Step 3)
    """
    try:
        user = request.user
        payment_method_id = request.data.get('paymentMethodId')
        plan = request.data.get('plan')

        if not payment_method_id or not plan:
            return Response({
                'status': 'error',
                'message': 'Payment method and plan are required'
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

        # Create the subscription
        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{'price': price_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
            metadata={
                'user_id': user.id,
                'plan': plan
            }
        )

        # Save subscription ID to user model
        user.stripe_subscription_id = subscription.id
        user.subscription_status = subscription.status
        user.save()

        return Response({
            'status': 'success',
            'subscription': {
                'id': subscription.id,
                'status': subscription.status,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret
            }
        })

    except stripe.error.StripeError as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Real Estate API Views
class ListCreateRealEstateView(generics.ListCreateAPIView):
    serializer_class = RealEstateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return RealEstate.objects.filter(client_id=client_id)

    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        client = get_object_or_404(Client, id=client_id, advisor=self.request.user)
        serializer.save(client=client)

class RealEstateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RealEstate.objects.all()
    serializer_class = RealEstateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class ReportTemplateViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, client_pk=None):
        """List all templates for a specific client"""
        client = get_object_or_404(Client, pk=client_pk, advisor=request.user)
        templates = ReportTemplate.objects.filter(client=client)
        serializer = ReportTemplateSerializer(templates, many=True, context={'request': request})
        return Response(serializer.data)
    
    def create(self, request, client_pk=None):
        """Upload a new PowerPoint template and process its slides"""
        try:
            # Check if python-pptx is installed
            from pptx import Presentation
        except ImportError:
            return Response(
                {"error": "The python-pptx library is not installed on the server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        client = get_object_or_404(Client, pk=client_pk, advisor=request.user)
        
        # Validate request data
        if 'name' not in request.data:
            return Response({"error": "Template name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'file' not in request.FILES:
            return Response({"error": "PowerPoint file is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        pptx_file = request.FILES['file']
        
        # Check file extension
        if not pptx_file.name.endswith('.pptx'):
            return Response(
                {"error": "Only PowerPoint files (.pptx) are supported"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the template record
        template = ReportTemplate.objects.create(
            client=client,
            name=request.data['name'],
            file=pptx_file
        )
        
        # Process the PowerPoint file to extract slide thumbnails
        try:
            self._process_slides(template, pptx_file)
        except Exception as e:
            # If slide processing fails, delete the template and return error
            template.delete()
            return Response(
                {"error": f"Failed to process PowerPoint file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = ReportTemplateSerializer(template, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """Get details of a specific template including all slides"""
        template = get_object_or_404(ReportTemplate, pk=pk)
        
        # Check if the user has access to this template
        if template.client.advisor != request.user:
            return Response(
                {"error": "You don't have permission to access this template"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReportTemplateDetailSerializer(template, context={'request': request})
        return Response(serializer.data)
    
    def destroy(self, request, pk=None):
        """Delete a template and all its slides"""
        template = get_object_or_404(ReportTemplate, pk=pk)
        
        # Check if the user has access to this template
        if template.client.advisor != request.user:
            return Response(
                {"error": "You don't have permission to delete this template"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        template.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def slides(self, request, pk=None):
        """Get all slides for a specific template"""
        template = get_object_or_404(ReportTemplate, pk=pk)
        
        # Check if the user has access to this template
        if template.client.advisor != request.user:
            return Response(
                {"error": "You don't have permission to access this template"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        slides = template.slides.all().order_by('order')
        serializer = TemplateSlideSerializer(slides, many=True, context={'request': request})
        
        return Response({"slides": serializer.data})
    
    @action(detail=True, methods=['post'])
    def update_slides(self, request, pk=None):
        """Update slide order and remove slides"""
        template = get_object_or_404(ReportTemplate, pk=pk)
        
        # Check if the user has access to this template
        if template.client.advisor != request.user:
            return Response(
                {"error": "You don't have permission to modify this template"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'slides' not in request.data:
            return Response(
                {"error": "Slides data is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all current slides
        current_slides = {str(slide.id): slide for slide in template.slides.all()}
        
        # Process the update
        for idx, slide_data in enumerate(request.data['slides']):
            slide_id = slide_data.get('id')
            
            if not slide_id or slide_id not in current_slides:
                continue
                
            # Update the order
            slide = current_slides[slide_id]
            slide.order = idx
            slide.save()
            
            # Remove from the current_slides dict to track which ones to delete
            current_slides.pop(slide_id)
        
        # Delete any slides not included in the request
        for slide in current_slides.values():
            slide.delete()
        
        # Return the updated slides
        slides = template.slides.all().order_by('order')
        serializer = TemplateSlideSerializer(slides, many=True, context={'request': request})
        
        return Response({"slides": serializer.data})
    
    def _process_slides(self, template, pptx_file):
        """Process a PowerPoint file and extract slide thumbnails"""
        try:
            # Create a temporary file to save the uploaded file
            with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as temp_file:
                for chunk in pptx_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Create output directory for thumbnails
            thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
            os.makedirs(thumbnails_dir, exist_ok=True)
            
            # Initialize png_paths to empty list
            png_paths = []
            
            try:
                # Convert PowerPoint to PNG using our new converter
                png_paths = convert_pptx_to_png(temp_file_path, thumbnails_dir, dpi=300)
                
                # Save each thumbnail as a slide
                for i, png_path in enumerate(png_paths):
                    # Open the PNG file
                    with open(png_path, 'rb') as f:
                        image_data = f.read()
                    
                    # Create the slide record
                    slide_filename = f"slide_{i+1}.png"
                    template_slide = TemplateSlide(
                        template=template,
                        order=i
                    )
                    template_slide.thumbnail.save(slide_filename, BytesIO(image_data), save=True)
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
                for png_path in png_paths:
                    try:
                        os.unlink(png_path)
                    except:
                        pass
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing PowerPoint file: {str(e)}")
            raise e

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def client_report_templates(request, client_id):
    """
    GET: List all report templates for a client
    POST: Create a new report template for a client
    """
    client = get_object_or_404(Client, pk=client_id, advisor=request.user)
    
    if request.method == 'GET':
        templates = ReportTemplate.objects.filter(client=client)
        serializer = ReportTemplateSerializer(templates, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        try:
            # Check if python-pptx is installed
            from pptx import Presentation
        except ImportError:
            return Response(
                {"error": "The python-pptx library is not installed on the server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Validate request data
        if 'name' not in request.data:
            return Response({"error": "Template name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'file' not in request.FILES:
            return Response({"error": "PowerPoint file is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        pptx_file = request.FILES['file']
        
        # Check file extension
        if not pptx_file.name.endswith('.pptx'):
            return Response(
                {"error": "Only PowerPoint files (.pptx) are supported"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the template record
        template = ReportTemplate.objects.create(
            client=client,
            name=request.data['name'],
            file=pptx_file
        )
        
        # Process the PowerPoint file to extract slide thumbnails
        try:
            process_pptx_slides(template, pptx_file)
        except Exception as e:
            # If slide processing fails, delete the template and return error
            template.delete()
            return Response(
                {"error": f"Failed to process PowerPoint file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = ReportTemplateSerializer(template, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def process_pptx_slides(template, pptx_file):
    """Process a PowerPoint file and extract slide thumbnails"""
    try:
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as temp_file:
            for chunk in pptx_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Create output directory for thumbnails
        thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Initialize png_paths to empty list
        png_paths = []
        
        try:
            # Convert PowerPoint to PNG using our new converter
            png_paths = convert_pptx_to_png(temp_file_path, thumbnails_dir, dpi=300)
            
            # Save each thumbnail as a slide
            for i, png_path in enumerate(png_paths):
                # Open the PNG file
                with open(png_path, 'rb') as f:
                    image_data = f.read()
                
                # Create the slide record
                slide_filename = f"slide_{i+1}.png"
                template_slide = TemplateSlide(
                    template=template,
                    order=i
                )
                template_slide.thumbnail.save(slide_filename, BytesIO(image_data), save=True)
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            for png_path in png_paths:
                try:
                    os.unlink(png_path)
                except:
                    pass
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing PowerPoint file: {str(e)}")
        raise e

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def report_template_detail(request, template_id):
    """
    GET: Retrieve details of a specific template
    DELETE: Delete a template
    """
    template = get_object_or_404(ReportTemplate, pk=template_id)
    
    # Check if the user has access to this template
    if template.client.advisor != request.user:
        return Response(
            {"error": "You don't have permission to access this template"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        serializer = ReportTemplateDetailSerializer(template, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        template.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_slides(request, template_id):
    """Get all slides for a specific template"""
    template = get_object_or_404(ReportTemplate, pk=template_id)
    
    # Check if the user has access to this template
    if template.client.advisor != request.user:
        return Response(
            {"error": "You don't have permission to access this template"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    slides = template.slides.all().order_by('order')
    serializer = TemplateSlideSerializer(slides, many=True, context={'request': request})
    
    return Response({"slides": serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_template_slides(request, template_id):
    """Update slide order and remove slides"""
    template = get_object_or_404(ReportTemplate, pk=template_id)
    
    # Check if the user has access to this template
    if template.client.advisor != request.user:
        return Response(
            {"error": "You don't have permission to modify this template"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if 'slides' not in request.data:
        return Response(
            {"error": "Slides data is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get all current slides
    current_slides = {str(slide.id): slide for slide in template.slides.all()}
    
    # Process the update
    for idx, slide_data in enumerate(request.data['slides']):
        slide_id = slide_data.get('id')
        
        if not slide_id or slide_id not in current_slides:
            continue
            
        # Update the order
        slide = current_slides[slide_id]
        slide.order = idx
        slide.save()
        
        # Remove from the current_slides dict to track which ones to delete
        current_slides.pop(slide_id)
    
    # Delete any slides not included in the request
    for slide in current_slides.values():
        slide.delete()
    
    # Return the updated slides
    slides = template.slides.all().order_by('order')
    serializer = TemplateSlideSerializer(slides, many=True, context={'request': request})
    
    return Response({"slides": serializer.data})

