# affiliate_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg
from django.http import JsonResponse, HttpResponseRedirect
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
import logging

from .affiliate_models import (
    Affiliate,
    AffiliateLink,
    AffiliateClick,
    AffiliateConversion,
    Commission,
    AffiliatePayout,
    AffiliateDiscountCode
)
from .affiliate_emails import (
    send_affiliate_welcome_email,
    send_affiliate_conversion_notification
)
from .affiliate_serializers import (
    AffiliateSerializer,
    AffiliateListSerializer,
    AffiliateLinkSerializer,
    AffiliateClickSerializer,
    AffiliateConversionSerializer,
    CommissionSerializer,
    AffiliatePayoutSerializer,
    AffiliateDiscountCodeSerializer,
    AffiliateDashboardSerializer,
    CreateAffiliateLinkSerializer,
    TrackClickSerializer
)
from .permissions import IsAdminUser

logger = logging.getLogger(__name__)


class AffiliateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing affiliates
    Admin users can manage all affiliates
    Affiliates can only view/edit their own data
    """
    queryset = Affiliate.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AffiliateListSerializer
        elif self.action == 'dashboard':
            return AffiliateDashboardSerializer
        return AffiliateSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin users can see all affiliates
        if user.is_staff or getattr(user, 'is_platform_admin', False):
            queryset = Affiliate.objects.all()
        else:
            # Regular users can only see their own affiliate account
            queryset = Affiliate.objects.filter(user=user)
        
        # Apply filters
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(business_name__icontains=search) |
                Q(email__icontains=search) |
                Q(affiliate_code__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a new affiliate and send welcome email"""
        affiliate = serializer.save()
        
        # Send welcome email asynchronously
        send_affiliate_welcome_email.delay(str(affiliate.id))
        
        return affiliate
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Approve an affiliate application"""
        affiliate = self.get_object()
        
        if affiliate.status != 'pending':
            return Response(
                {'error': 'Only pending affiliates can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        affiliate.status = 'active'
        affiliate.approved_at = timezone.now()
        affiliate.approved_by = request.user
        affiliate.save()
        
        # Send approval email
        from .affiliate_emails import AffiliateEmailService
        AffiliateEmailService.send_approval_email(affiliate)
        
        return Response({'status': 'Affiliate approved successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def suspend(self, request, pk=None):
        """Suspend an affiliate"""
        affiliate = self.get_object()
        
        if affiliate.status == 'suspended':
            return Response(
                {'error': 'Affiliate is already suspended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        affiliate.status = 'suspended'
        affiliate.save()
        
        # Deactivate all affiliate links
        affiliate.links.update(is_active=False)
        
        return Response({'status': 'Affiliate suspended successfully'})
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get comprehensive dashboard data for an affiliate"""
        affiliate = self.get_object()
        serializer = self.get_serializer(affiliate)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_link(self, request, pk=None):
        """Generate a new tracking link for an affiliate"""
        affiliate = self.get_object()
        
        # Check if affiliate is active
        if affiliate.status != 'active':
            return Response(
                {'error': 'Only active affiliates can generate links'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreateAffiliateLinkSerializer(data=request.data)
        if serializer.is_valid():
            link = serializer.save(affiliate=affiliate)
            return Response(
                AffiliateLinkSerializer(link).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def links(self, request, pk=None):
        """Get all tracking links for an affiliate"""
        affiliate = self.get_object()
        links = affiliate.links.all()
        
        # Apply filters
        active_only = request.query_params.get('active_only', 'false').lower() == 'true'
        if active_only:
            links = links.filter(is_active=True)
        
        serializer = AffiliateLinkSerializer(links, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def commissions(self, request, pk=None):
        """Get commission history for an affiliate"""
        affiliate = self.get_object()
        commissions = affiliate.commissions.all()
        
        # Apply filters
        status_filter = request.query_params.get('status', None)
        if status_filter:
            commissions = commissions.filter(status=status_filter)
        
        # Date range filter
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        if start_date:
            commissions = commissions.filter(created_at__gte=start_date)
        if end_date:
            commissions = commissions.filter(created_at__lte=end_date)
        
        commissions = commissions.order_by('-created_at')
        serializer = CommissionSerializer(commissions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def track_click(self, request):
        """
        Track affiliate click via API (for frontend integration)
        """
        affiliate_code = request.data.get('affiliate_code')
        page_url = request.data.get('page_url', '')
        referrer = request.data.get('referrer', '')
        
        if not affiliate_code:
            return Response(
                {'error': 'Affiliate code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            affiliate = Affiliate.objects.get(affiliate_code=affiliate_code)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'Invalid affiliate code'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get client IP and user agent
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Generate session ID
        import uuid
        session_id = request.session.session_key or f"session_{uuid.uuid4().hex[:16]}"
        
        # Create click record
        click = AffiliateClick.objects.create(
            affiliate=affiliate,
            session_id=session_id,
            tracking_code=affiliate_code,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer[:1000] if referrer else ''
        )
        
        return Response({
            'success': True,
            'message': 'Click tracked successfully',
            'session_id': session_id
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def portal_login(self, request):
        """
        Affiliate portal login endpoint.
        Accepts email/code or email/password for authentication.
        """
        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            affiliate = Affiliate.objects.get(email=email)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if using code or password
        if code:
            # Verify affiliate code
            if affiliate.affiliate_code != code:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check if password needs to be set up
            if not hasattr(affiliate, 'portal_password') or not affiliate.portal_password:
                return Response(
                    {'error': 'Password setup required', 'needs_password_setup': True},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        elif password:
            # Verify password
            if not hasattr(affiliate, 'portal_password') or not affiliate.portal_password:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if not check_password(password, affiliate.portal_password):
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {'error': 'Code or password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update last activity
        affiliate.last_activity_at = timezone.now()
        affiliate.save(update_fields=['last_activity_at'])
        
        # Generate JWT tokens for the affiliate
        refresh = RefreshToken()
        refresh['user_id'] = str(affiliate.id)  # Convert UUID to string
        refresh['is_affiliate_portal'] = True
        refresh['affiliate_code'] = affiliate.affiliate_code
        
        # Create session data (convert UUID to string)
        session_data = {
            'affiliate_id': str(affiliate.id),
            'affiliate_code': affiliate.affiliate_code,
            'name': affiliate.business_name,
            'email': affiliate.email,
            'company': affiliate.business_name,
            'is_affiliate_portal': True
        }
        
        return Response({
            'success': True,
            'affiliate': AffiliateSerializer(affiliate).data,
            'session': {
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'affiliate': session_data
            }
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def setup_password(self, request):
        """
        Set up password for first-time affiliate portal access.
        """
        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')
        
        if not all([email, code, password]):
            return Response(
                {'error': 'Email, code, and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            affiliate = Affiliate.objects.get(email=email, affiliate_code=code)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Set the password
        affiliate.portal_password = make_password(password)
        affiliate.last_activity_at = timezone.now()
        affiliate.save(update_fields=['portal_password', 'last_activity_at'])
        
        # Generate JWT tokens
        refresh = RefreshToken()
        refresh['user_id'] = str(affiliate.id)  # Convert UUID to string
        refresh['is_affiliate_portal'] = True
        refresh['affiliate_code'] = affiliate.affiliate_code
        
        # Create session data (convert UUID to string)
        session_data = {
            'affiliate_id': str(affiliate.id),
            'affiliate_code': affiliate.affiliate_code,
            'name': affiliate.business_name,
            'email': affiliate.email,
            'company': affiliate.business_name,
            'is_affiliate_portal': True
        }
        
        return Response({
            'success': True,
            'affiliate': AffiliateSerializer(affiliate).data,
            'session': {
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'affiliate': session_data
            }
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def portal_dashboard(self, request):
        """
        Get dashboard data for authenticated affiliate.
        Uses affiliate_id from JWT token or query parameter.
        """
        # Get affiliate_id from request (would be set by authentication middleware)
        affiliate_id = request.GET.get('affiliate_id')
        
        if not affiliate_id:
            # Try to get from JWT token if available
            if hasattr(request, 'user') and hasattr(request.user, 'id'):
                affiliate_id = request.user.id
            else:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        try:
            affiliate = Affiliate.objects.get(id=affiliate_id)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'Affiliate not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get performance metrics
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        clicks = AffiliateClick.objects.filter(
            affiliate=affiliate,
            clicked_at__gte=thirty_days_ago
        )
        
        conversions = AffiliateConversion.objects.filter(
            affiliate=affiliate,
            conversion_date__gte=thirty_days_ago.date()
        )
        
        commissions = Commission.objects.filter(
            affiliate=affiliate,
            created_at__gte=thirty_days_ago
        )
        
        # Calculate metrics
        total_clicks = clicks.count()
        total_conversions = conversions.count()
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        total_commission = commissions.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
        
        # Get recent activity
        recent_clicks = clicks.order_by('-clicked_at')[:10]
        recent_conversions = conversions.order_by('-conversion_date')[:5]
        
        # Get active links
        active_links = AffiliateLink.objects.filter(
            affiliate=affiliate,
            is_active=True
        ).annotate(
            click_count=Count('clicks'),
            conversion_count=Count('clicks__conversion')
        )
        
        return Response({
            'affiliate': AffiliateSerializer(affiliate).data,
            'metrics': {
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'conversion_rate': round(conversion_rate, 2),
                'total_commission': float(total_commission),
                'pending_commission': float(
                    commissions.filter(status='pending').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
                ),
                'paid_commission': float(
                    commissions.filter(status='paid').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
                )
            },
            'recent_activity': {
                'clicks': [{
                    'id': str(click.id),  # Convert UUID to string
                    'clicked_at': click.clicked_at,
                    'source': getattr(click, 'source', 'direct'),
                    'ip_address': click.ip_address
                } for click in recent_clicks],
                'conversions': [{
                    'id': str(conv.id),  # Convert UUID to string
                    'converted_at': conv.conversion_date,
                    'conversion_value': float(conv.subscription_amount)
                } for conv in recent_conversions]
            },
            'links': AffiliateLinkSerializer(active_links, many=True).data
        })


class AffiliateLinkViewSet(viewsets.ModelViewSet):
    """ViewSet for managing affiliate links"""
    queryset = AffiliateLink.objects.all()
    serializer_class = AffiliateLinkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin users can see all links
        if user.is_staff or getattr(user, 'is_platform_admin', False):
            return AffiliateLink.objects.all()
        
        # Regular users can only see their affiliate's links
        try:
            affiliate = Affiliate.objects.get(user=user)
            return AffiliateLink.objects.filter(affiliate=affiliate)
        except Affiliate.DoesNotExist:
            return AffiliateLink.objects.none()
    
    def perform_create(self, serializer):
        """Create a new link for the user's affiliate account"""
        user = self.request.user
        
        # Admin can specify affiliate, regular users use their own
        if user.is_staff and 'affiliate' in self.request.data:
            affiliate_id = self.request.data['affiliate']
            affiliate = get_object_or_404(Affiliate, id=affiliate_id)
        else:
            affiliate = get_object_or_404(Affiliate, user=user)
        
        serializer.save(affiliate=affiliate)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a tracking link"""
        link = self.get_object()
        link.is_active = False
        link.save()
        return Response({'status': 'Link deactivated successfully'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a tracking link"""
        link = self.get_object()
        link.is_active = True
        link.save()
        return Response({'status': 'Link activated successfully'})


def track_click(request, tracking_code):
    """
    Track affiliate link clicks and redirect to destination
    This is a public endpoint that handles link redirection
    """
    try:
        # Get the affiliate link
        link = get_object_or_404(AffiliateLink, tracking_code=tracking_code, is_active=True)
        
        # Check if link is expired
        if link.is_expired:
            logger.warning(f"Expired link clicked: {tracking_code}")
            return HttpResponseRedirect('/')  # Redirect to home if expired
        
        # Check max uses
        if link.is_max_uses_reached:
            logger.warning(f"Max uses reached for link: {tracking_code}")
            return HttpResponseRedirect('/')
        
        # Get click data
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        # Get or create session ID (for attribution)
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        
        # Store affiliate tracking in session for conversion attribution
        request.session['affiliate_id'] = str(link.affiliate.id)
        request.session['affiliate_link_id'] = str(link.id)
        request.session['affiliate_tracking_code'] = tracking_code
        request.session['affiliate_click_time'] = timezone.now().isoformat()
        request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
        
        # Detect if mobile
        is_mobile = any(device in user_agent.lower() for device in ['mobile', 'android', 'iphone'])
        
        # Detect bot traffic (basic detection)
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
        is_bot = any(indicator in user_agent.lower() for indicator in bot_indicators)
        
        # Create click record
        click = AffiliateClick.objects.create(
            affiliate=link.affiliate,
            link=link,
            session_id=session_id,
            tracking_code=tracking_code,
            ip_address=ip_address,
            user_agent=user_agent[:500],  # Truncate if too long
            referrer=referrer[:1000] if referrer else '',
            is_mobile=is_mobile,
            is_bot=is_bot,
            is_valid=not is_bot  # Mark bot traffic as invalid
        )
        
        # Update link statistics
        link.total_clicks += 1
        link.current_uses += 1
        link.save()
        
        # Update affiliate statistics
        link.affiliate.total_clicks += 1
        link.affiliate.last_activity_at = timezone.now()
        link.affiliate.save()
        
        # Build destination URL with UTM parameters
        destination = link.destination_url
        utm_params = []
        
        if link.utm_source:
            utm_params.append(f'utm_source={link.utm_source}')
        if link.utm_medium:
            utm_params.append(f'utm_medium={link.utm_medium}')
        if link.utm_campaign:
            utm_params.append(f'utm_campaign={link.utm_campaign}')
        
        # Add affiliate tracking parameter
        utm_params.append(f'ref={link.affiliate.affiliate_code}')
        
        # Apply discount code if present
        if link.discount_code:
            utm_params.append(f'discount={link.discount_code}')
        
        # Construct final URL
        if utm_params:
            separator = '&' if '?' in destination else '?'
            destination = f"{destination}{separator}{'&'.join(utm_params)}"
        
        return HttpResponseRedirect(destination)
        
    except Exception as e:
        logger.error(f"Error tracking click for {tracking_code}: {str(e)}")
        return HttpResponseRedirect('/')


class CommissionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing commissions"""
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin users can see all commissions
        if user.is_staff or getattr(user, 'is_platform_admin', False):
            return Commission.objects.all()
        
        # Regular users can only see their affiliate's commissions
        try:
            affiliate = Affiliate.objects.get(user=user)
            return Commission.objects.filter(affiliate=affiliate)
        except Affiliate.DoesNotExist:
            return Commission.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        """Get all pending commissions for approval"""
        commissions = Commission.objects.filter(status='pending')
        
        # Group by affiliate
        affiliate_id = request.query_params.get('affiliate_id', None)
        if affiliate_id:
            commissions = commissions.filter(affiliate_id=affiliate_id)
        
        serializer = self.get_serializer(commissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a commission for payout"""
        commission = self.get_object()
        
        if commission.status != 'pending':
            return Response(
                {'error': 'Only pending commissions can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        commission.status = 'approved'
        commission.approved_at = timezone.now()
        commission.save()
        
        # Update affiliate's pending balance
        affiliate = commission.affiliate
        affiliate.pending_commission_balance += commission.commission_amount
        affiliate.save()
        
        return Response({'status': 'Commission approved successfully'})
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def calculate_monthly(self, request):
        """Calculate commissions for the previous month"""
        # Get date range for previous month
        today = timezone.now().date()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        # Get all conversions for the previous month
        conversions = AffiliateConversion.objects.filter(
            conversion_date__gte=first_day_previous_month,
            conversion_date__lt=first_day_current_month,
            is_valid=True,
            is_refunded=False
        )
        
        commissions_created = []
        
        for conversion in conversions:
            # Check if commission already exists
            existing = Commission.objects.filter(
                conversion=conversion,
                commission_type='first_month'
            ).exists()
            
            if not existing:
                # Calculate commission
                affiliate = conversion.affiliate
                commission_rate = affiliate.get_commission_rate(is_first_month=True)
                
                if affiliate.commission_type == 'flat':
                    commission_amount = commission_rate
                else:
                    commission_amount = conversion.subscription_amount * (commission_rate / 100)
                
                # Create commission record
                commission = Commission.objects.create(
                    affiliate=affiliate,
                    conversion=conversion,
                    commission_type='first_month',
                    description=f"Commission for {conversion.user_email}",
                    base_amount=conversion.subscription_amount,
                    commission_rate=commission_rate / 100 if affiliate.commission_type != 'flat' else 0,
                    commission_amount=commission_amount,
                    period_start=first_day_previous_month,
                    period_end=last_day_previous_month,
                    status='pending'
                )
                commissions_created.append(commission)
        
        return Response({
            'commissions_created': len(commissions_created),
            'period': f"{first_day_previous_month} to {last_day_previous_month}"
        })


class AffiliatePayoutViewSet(viewsets.ModelViewSet):
    """ViewSet for managing affiliate payouts"""
    queryset = AffiliatePayout.objects.all()
    serializer_class = AffiliatePayoutSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def create_batch(self, request):
        """Create batch payouts for all affiliates with pending commissions"""
        # Get all affiliates with pending balance above minimum payout
        affiliates = Affiliate.objects.filter(
            pending_commission_balance__gte=50.00  # Default minimum
        )
        
        payouts_created = []
        
        for affiliate in affiliates:
            # Get unpaid approved commissions
            commissions = Commission.objects.filter(
                affiliate=affiliate,
                status='approved',
                payout__isnull=True
            )
            
            if commissions.exists():
                # Calculate total
                total = commissions.aggregate(total=Sum('commission_amount'))['total']
                
                # Create payout record
                payout = AffiliatePayout.objects.create(
                    affiliate=affiliate,
                    payout_period_start=commissions.earliest('period_start').period_start,
                    payout_period_end=commissions.latest('period_end').period_end,
                    total_commissions=total,
                    net_payout=total,  # Can be adjusted for fees
                    payment_method=affiliate.payment_method,
                    status='pending',
                    tax_year=timezone.now().year
                )
                
                # Link commissions to payout
                commissions.update(payout=payout, status='paid')
                
                # Update affiliate balance
                affiliate.pending_commission_balance -= total
                affiliate.total_commissions_paid += total
                affiliate.save()
                
                payouts_created.append(payout)
        
        serializer = self.get_serializer(payouts_created, many=True)
        return Response({
            'payouts_created': len(payouts_created),
            'payouts': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a payout (integrate with payment provider)"""
        payout = self.get_object()
        
        if payout.status != 'pending':
            return Response(
                {'error': 'Only pending payouts can be processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Integrate with Stripe Connect or PayPal to process actual payment
        # For now, just mark as completed
        
        payout.status = 'completed'
        payout.processed_at = timezone.now()
        payout.completed_at = timezone.now()
        payout.processed_by = request.user
        payout.payment_reference = f"MANUAL-{payout.id}"
        payout.save()
        
        return Response({'status': 'Payout processed successfully'})


class AffiliateDiscountCodeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing affiliate discount codes"""
    queryset = AffiliateDiscountCode.objects.all()
    serializer_class = AffiliateDiscountCodeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin users can see all discount codes
        if user.is_staff or getattr(user, 'is_platform_admin', False):
            return AffiliateDiscountCode.objects.all()
        
        # Regular users can only see their affiliate's codes
        try:
            affiliate = Affiliate.objects.get(user=user)
            return AffiliateDiscountCode.objects.filter(affiliate=affiliate)
        except Affiliate.DoesNotExist:
            return AffiliateDiscountCode.objects.none()
    
    def perform_create(self, serializer):
        """Create a new discount code for an affiliate"""
        user = self.request.user
        
        # Admin can specify affiliate, regular users use their own
        if user.is_staff and 'affiliate' in self.request.data:
            affiliate_id = self.request.data['affiliate']
            affiliate = get_object_or_404(Affiliate, id=affiliate_id)
        else:
            affiliate = get_object_or_404(Affiliate, user=user)
        
        serializer.save(affiliate=affiliate)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def validate(self, request):
        """Validate a discount code (public endpoint)"""
        code = request.query_params.get('code', '').upper()
        
        if not code:
            return Response(
                {'valid': False, 'error': 'No code provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            discount = AffiliateDiscountCode.objects.get(code=code)
            
            if not discount.is_valid:
                return Response({
                    'valid': False,
                    'error': 'This discount code is not valid'
                })
            
            # Store discount code in session for attribution
            if not request.session.session_key:
                request.session.create()
            request.session['affiliate_discount_code'] = code
            request.session['affiliate_id'] = str(discount.affiliate.id)
            request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
            
            return Response({
                'valid': True,
                'discount_type': discount.discount_type,
                'discount_value': str(discount.discount_value),
                'description': discount.description
            })
            
        except AffiliateDiscountCode.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid discount code'
            })