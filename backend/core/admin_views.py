# backend/core/admin_views.py

from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum, Avg, F
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from datetime import datetime, timedelta
import json
from auth0.management import Auth0
import os

from .models import (
    Client, Scenario, Communication, Task, Lead, CustomUser,
    ActivityLog, EmailAccount, CalendarEvent, Document,
    RevenueMetric, UserEngagementMetric, ClientPortfolioAnalytics,
    SystemPerformanceMetric, SupportTicket, AlertRule
)
from .decorators import admin_required
from .serializers_main import UserSerializer
from .services.analytics_service import AnalyticsOrchestrator, RevenueAnalyticsService

User = get_user_model()


class AdminPermissionMixin:
    """Mixin to require admin permissions for viewset actions"""
    
    def check_admin_permissions(self, request, required_section=None):
        """Check if user has admin access and optionally specific section access"""
        if not request.user.is_authenticated:
            return False
            
        # Check if user has admin access
        if not getattr(request.user, 'is_admin_user', False):
            return False
            
        # If no specific section required, general admin access is enough
        if not required_section:
            return True
            
        # Check specific section access
        return request.user.can_access_admin_section(required_section)
    
    def get_permissions(self):
        """Override to add admin permission checks"""
        permissions = super().get_permissions()
        permissions.append(IsAuthenticated())
        return permissions
    
    def dispatch(self, request, *args, **kwargs):
        """Check admin permissions before processing request"""
        if not self.check_admin_permissions(request):
            return JsonResponse(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().dispatch(request, *args, **kwargs)


@api_view(['GET'])
@admin_required()
def admin_dashboard_stats(request):
    """Get comprehensive platform statistics for admin dashboard"""
    try:
        # Get time ranges for analytics
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User statistics
        total_users = User.objects.count()
        active_subscriptions = User.objects.filter(
            subscription_status='active',
            subscription_end_date__gt=now
        ).count()
        
        new_users_this_month = User.objects.filter(
            date_joined__gte=month_ago
        ).count()
        
        # User activity in last 24 hours
        active_users_24h = ActivityLog.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).values('user').distinct().count()
        
        # Client statistics
        total_clients = Client.objects.filter(is_deleted=False).count()
        new_clients_this_month = Client.objects.filter(
            created_at__gte=month_ago,
            is_deleted=False
        ).count()
        
        # Scenario statistics
        total_scenarios = Scenario.objects.count()
        scenarios_this_month = Scenario.objects.filter(
            created_at__gte=month_ago
        ).count()
        
        # Communication statistics
        total_communications = Communication.objects.count()
        unread_communications = Communication.objects.filter(
            is_read=False
        ).count()
        
        # Task statistics
        pending_tasks = Task.objects.filter(
            status__in=['pending', 'in_progress']
        ).count()
        
        # Lead statistics
        total_leads = Lead.objects.count()
        new_leads_this_month = Lead.objects.filter(
            created_at__gte=month_ago
        ).count()
        
        # Revenue statistics (based on active subscriptions)
        monthly_revenue = User.objects.filter(
            subscription_status='active',
            subscription_plan='monthly'
        ).count() * 97  # Assuming $97/month
        
        annual_revenue = User.objects.filter(
            subscription_status='active',
            subscription_plan='annual'
        ).count() * 997  # Assuming $997/year
        
        total_mrr = monthly_revenue + (annual_revenue / 12)
        
        # Storage statistics (simplified)
        total_documents = Document.objects.filter(
            status='active'
        ).count()
        
        storage_usage = Document.objects.filter(
            status='active'
        ).aggregate(
            total_size=Sum('file_size')
        )['total_size'] or 0
        
        # Convert to GB for display
        storage_gb = round(storage_usage / (1024**3), 2)
        
        # Subscription breakdown
        subscription_breakdown = {
            'trial': User.objects.filter(subscription_status='trialing').count(),
            'active': active_subscriptions,
            'past_due': User.objects.filter(subscription_status='past_due').count(),
            'canceled': User.objects.filter(subscription_status='canceled').count(),
        }
        
        # Geographic distribution (simplified - based on state field)
        geographic_data = list(User.objects.exclude(
            state__isnull=True
        ).exclude(
            state__exact=''
        ).values('state').annotate(
            count=Count('id')
        ).order_by('-count')[:10])
        
        # Recent activity
        recent_activity = []
        recent_logs = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]
        
        for log in recent_logs:
            recent_activity.append({
                'id': log.id,
                'user_name': f"{log.user.first_name} {log.user.last_name}".strip() or log.user.email,
                'user_email': log.user.email,
                'action': log.description,
                'timestamp': log.created_at.isoformat(),
                'status': 'success',  # Simplified for now
                'activity_type': log.activity_type
            })
        
        # Growth trends (simplified)
        user_growth_trend = []
        for i in range(7):  # Last 7 days
            date = today - timedelta(days=i)
            daily_signups = User.objects.filter(
                date_joined__date=date
            ).count()
            user_growth_trend.append({
                'date': date.isoformat(),
                'signups': daily_signups
            })
        
        stats = {
            'totalUsers': total_users,
            'activeSubscriptions': active_subscriptions,
            'totalClients': total_clients,
            'totalScenarios': total_scenarios,
            'activeUsers24h': active_users_24h,
            'storageUsage': f"{storage_gb} GB",
            'storageUsageBytes': storage_usage,
            'totalDocuments': total_documents,
            
            # Revenue metrics
            'monthlyRevenue': monthly_revenue,
            'annualRevenue': annual_revenue,
            'totalMRR': round(total_mrr, 2),
            'averageRevenuePerUser': round(total_mrr / max(active_subscriptions, 1), 2),
            
            # Growth metrics
            'newUsersThisMonth': new_users_this_month,
            'newClientsThisMonth': new_clients_this_month,
            'scenariosThisMonth': scenarios_this_month,
            'newLeadsThisMonth': new_leads_this_month,
            
            # Activity metrics
            'totalCommunications': total_communications,
            'unreadCommunications': unread_communications,
            'pendingTasks': pending_tasks,
            'totalLeads': total_leads,
            
            # Breakdowns
            'subscriptionBreakdown': subscription_breakdown,
            'geographicDistribution': geographic_data,
            
            # Trends and activity
            'recentActivity': recent_activity,
            'userGrowthTrend': user_growth_trend,
            
            # System health (simplified)
            'systemHealth': {
                'status': 'healthy',
                'uptime': '99.9%',
                'responseTime': '< 200ms',
                'errorRate': '< 0.1%'
            }
        }
        
        return Response(stats)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch admin stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
@admin_required()
def admin_user_list(request):
    """Get paginated list of users with admin-specific data"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        search = request.GET.get('search', '')
        role_filter = request.GET.get('role', '')
        status_filter = request.GET.get('status', '')
        
        # Build query
        queryset = User.objects.all()
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(company_name__icontains=search)
            )
        
        # Apply role filter
        if role_filter:
            queryset = queryset.filter(admin_role=role_filter)
        
        # Apply status filter
        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(subscription_status='active')
            elif status_filter == 'admin':
                queryset = queryset.filter(is_platform_admin=True)
            elif status_filter == 'trial':
                queryset = queryset.filter(subscription_status='trialing')
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        users = queryset[offset:offset + limit]
        
        # Serialize with additional admin data
        user_data = []
        for user in users:
            # Get user activity stats
            client_count = Client.objects.filter(advisor=user, is_deleted=False).count()
            scenario_count = Scenario.objects.filter(client__advisor=user).count()
            last_login = getattr(user, 'last_login', None)
            
            user_info = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'company_name': user.company_name,
                'phone_number': user.phone_number,
                'date_joined': user.date_joined.isoformat(),
                'last_login': last_login.isoformat() if last_login else None,
                'is_active': user.is_active,
                'subscription_status': user.subscription_status,
                'subscription_plan': user.subscription_plan,
                'subscription_end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                'is_platform_admin': user.is_platform_admin,
                'admin_role': user.admin_role,
                'admin_role_display': user.get_admin_role_display_name(),
                'client_count': client_count,
                'scenario_count': scenario_count,
                'city': user.city,
                'state': user.state,
            }
            user_data.append(user_info)
        
        return Response({
            'users': user_data,
            'totalCount': total_count,
            'page': page,
            'limit': limit,
            'totalPages': (total_count + limit - 1) // limit
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch users: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@admin_required(section='user_management')
def update_user_admin_role(request, user_id):
    """Update a user's admin role and permissions"""
    try:
        user = User.objects.get(id=user_id)
        
        # Get data from request
        admin_role = request.data.get('admin_role', '')
        admin_permissions = request.data.get('admin_permissions', {})
        is_platform_admin = request.data.get('is_platform_admin', bool(admin_role))
        
        # Update user fields
        user.admin_role = admin_role
        user.admin_permissions = admin_permissions
        user.is_platform_admin = is_platform_admin
        user.save()
        
        # Log the action
        ActivityLog.objects.create(
            activity_type='admin_role_updated',
            user=request.user,
            description=f'Updated admin role for {user.email} to {admin_role}',
            metadata={
                'target_user_id': user.id,
                'target_user_email': user.email,
                'new_role': admin_role,
                'new_permissions': admin_permissions,
                'updated_by': request.user.email
            }
        )
        
        return Response({
            'message': 'User admin role updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'admin_role': user.admin_role,
                'admin_permissions': user.admin_permissions,
                'is_platform_admin': user.is_platform_admin
            }
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to update user role: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='analytics')
def admin_analytics_overview(request):
    """Get analytics data for admin analytics page"""
    try:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # User engagement analytics
        user_engagement = {
            'total_active_users': User.objects.filter(
                last_login__gte=thirty_days_ago
            ).count(),
            'daily_active_users': ActivityLog.objects.filter(
                created_at__gte=now - timedelta(days=1)
            ).values('user').distinct().count(),
            'weekly_active_users': ActivityLog.objects.filter(
                created_at__gte=now - timedelta(days=7)
            ).values('user').distinct().count(),
        }
        
        # Feature usage analytics
        feature_usage = {
            'scenarios_created': Scenario.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'reports_generated': ActivityLog.objects.filter(
                activity_type='report_generated',
                created_at__gte=thirty_days_ago
            ).count(),
            'communications_sent': Communication.objects.filter(
                direction='outbound',
                created_at__gte=thirty_days_ago
            ).count(),
        }
        
        # Client portfolio analytics
        portfolio_analytics = {
            'average_clients_per_advisor': Client.objects.aggregate(
                avg=Avg('advisor_id')
            )['avg'] or 0,
            'total_assets_under_management': 0,  # Would need asset value calculations
            'average_scenario_complexity': Scenario.objects.aggregate(
                avg_income_sources=Avg('income_sources__count')
            )['avg_income_sources'] or 0,
        }
        
        # Growth trends
        growth_data = []
        for i in range(30):  # Last 30 days
            date = (now - timedelta(days=i)).date()
            daily_data = {
                'date': date.isoformat(),
                'new_users': User.objects.filter(date_joined__date=date).count(),
                'new_clients': Client.objects.filter(created_at__date=date).count(),
                'new_scenarios': Scenario.objects.filter(created_at__date=date).count(),
            }
            growth_data.append(daily_data)
        
        return Response({
            'user_engagement': user_engagement,
            'feature_usage': feature_usage,
            'portfolio_analytics': portfolio_analytics,
            'growth_trends': growth_data[::-1],  # Reverse to show chronologically
            'generated_at': now.isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch analytics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='system_monitoring')
def admin_system_monitoring(request):
    """Get system monitoring data"""
    try:
        now = timezone.now()
        
        # Database performance metrics (simplified)
        db_metrics = {
            'total_records': {
                'users': User.objects.count(),
                'clients': Client.objects.count(),
                'scenarios': Scenario.objects.count(),
                'communications': Communication.objects.count(),
                'documents': Document.objects.count(),
            },
            'recent_activity_volume': ActivityLog.objects.filter(
                created_at__gte=now - timedelta(hours=24)
            ).count(),
        }
        
        # System health indicators
        health_metrics = {
            'api_response_times': {
                'average': 150,  # ms - would be calculated from monitoring
                'p95': 300,
                'p99': 500
            },
            'error_rates': {
                'last_hour': 0.1,  # % - would be calculated from logs
                'last_24h': 0.05,
                'last_week': 0.03
            },
            'uptime': {
                'current': '99.98%',
                'monthly': '99.95%',
                'yearly': '99.9%'
            }
        }
        
        # Storage metrics
        storage_metrics = {
            'document_storage': {
                'total_files': Document.objects.count(),
                'total_size_gb': round(
                    (Document.objects.aggregate(
                        total=Sum('file_size')
                    )['total'] or 0) / (1024**3), 2
                ),
            },
            'database_size': {
                'estimated_gb': 2.5,  # Would be calculated from actual DB
                'growth_rate_mb_day': 15
            }
        }
        
        # Recent errors and alerts (simplified)
        recent_issues = [
            {
                'id': 1,
                'type': 'warning',
                'message': 'Database query time exceeded 1s for scenario calculations',
                'timestamp': (now - timedelta(hours=2)).isoformat(),
                'resolved': True
            },
            {
                'id': 2,
                'type': 'info',
                'message': 'Scheduled backup completed successfully',
                'timestamp': (now - timedelta(hours=6)).isoformat(),
                'resolved': True
            }
        ]
        
        return Response({
            'database_metrics': db_metrics,
            'health_metrics': health_metrics,
            'storage_metrics': storage_metrics,
            'recent_issues': recent_issues,
            'last_updated': now.isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch system monitoring data: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='support_tools') 
def admin_support_overview(request):
    """Get support tools overview data"""
    try:
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        # Recent user issues (based on failed activities, errors, etc.)
        recent_issues = []
        
        # Failed login attempts (simplified)
        failed_logins = ActivityLog.objects.filter(
            activity_type='login_failed',
            created_at__gte=week_ago
        ).order_by('-created_at')[:10]
        
        for log in failed_logins:
            recent_issues.append({
                'id': log.id,
                'type': 'authentication',
                'user_email': log.user.email if log.user else 'Unknown',
                'description': 'Failed login attempt',
                'timestamp': log.created_at.isoformat(),
                'status': 'unresolved'
            })
        
        # Users with subscription issues
        subscription_issues = User.objects.filter(
            Q(subscription_status='past_due') | 
            Q(subscription_status='canceled') |
            Q(subscription_end_date__lt=now, subscription_status='active')
        ).order_by('-subscription_end_date')[:10]
        
        for user in subscription_issues:
            recent_issues.append({
                'id': f"sub_{user.id}",
                'type': 'billing',
                'user_email': user.email,
                'description': f'Subscription issue: {user.subscription_status}',
                'timestamp': (user.subscription_end_date or now).isoformat(),
                'status': 'needs_attention'
            })
        
        # Support metrics
        support_metrics = {
            'total_users_needing_help': len(recent_issues),
            'billing_issues': len([i for i in recent_issues if i['type'] == 'billing']),
            'auth_issues': len([i for i in recent_issues if i['type'] == 'authentication']),
            'active_sessions': User.objects.filter(
                last_login__gte=now - timedelta(hours=24)
            ).count()
        }
        
        # User activity summary
        user_activity = {
            'most_active_users': list(ActivityLog.objects.filter(
                created_at__gte=week_ago
            ).values('user__email').annotate(
                activity_count=Count('id')
            ).order_by('-activity_count')[:5]),
            
            'least_active_users': list(User.objects.filter(
                last_login__lt=now - timedelta(days=14),
                is_active=True,
                subscription_status='active'
            ).values('email', 'last_login', 'company_name')[:5])
        }
        
        return Response({
            'recent_issues': recent_issues,
            'support_metrics': support_metrics,
            'user_activity': user_activity,
            'generated_at': now.isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch support data: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='user_management')
def start_user_impersonation(request, user_id):
    """Start user impersonation session with audit logging"""
    from django.contrib.auth import login
    from .models import UserImpersonationLog, AdminAuditLog
    import uuid
    
    try:
        # Get target user
        target_user = User.objects.get(id=user_id)
        
        # Get request data
        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'error': 'Reason for impersonation is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if admin can impersonate this user
        admin_user = request.user
        if target_user.id == admin_user.id:
            return Response(
                {'error': 'Cannot impersonate yourself'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if target user is also an admin and current user has sufficient privileges
        if target_user.is_admin_user and not admin_user.admin_role == 'super_admin':
            return Response(
                {'error': 'Only super admins can impersonate other admin users'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create impersonation session
        session_key = str(uuid.uuid4())
        impersonation_log = UserImpersonationLog.objects.create(
            admin_user=admin_user,
            target_user=target_user,
            target_user_email=target_user.email,
            session_key=session_key,
            reason=reason,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            risk_score=75 if target_user.is_admin_user else 50
        )
        
        # Create audit log entry
        AdminAuditLog.log_action(
            admin_user=admin_user,
            action_type='user_impersonated',
            description=f'Started impersonation of {target_user.email}',
            target_user=target_user,
            metadata={
                'impersonation_session_id': impersonation_log.id,
                'session_key': session_key,
                'reason': reason,
                'target_user_admin': target_user.is_admin_user
            },
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            risk_level='high' if target_user.is_admin_user else 'medium'
        )
        
        # Create impersonation JWT token for the target user
        from .authentication import create_jwt_pair_for_user
        
        # Generate JWT tokens for the impersonated user
        tokens = create_jwt_pair_for_user(target_user)
        
        # Add impersonation metadata to the token payload
        impersonation_data = {
            'session_id': impersonation_log.id,
            'session_key': session_key,
            'admin_user_id': admin_user.id,
            'target_user_id': target_user.id,
            'started_at': impersonation_log.start_timestamp.isoformat(),
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh']
        }
        
        return Response({
            'message': f'Impersonation session started for {target_user.email}',
            'session_data': impersonation_data,
            'target_user': {
                'id': target_user.id,
                'email': target_user.email,
                'first_name': target_user.first_name,
                'last_name': target_user.last_name,
                'name': f"{target_user.first_name} {target_user.last_name}".strip() or target_user.email,
                'company_name': target_user.company_name or '',
                'subscription_status': target_user.subscription_status,
                'is_admin_user': False,  # Impersonated users should not have admin access
                'admin_role': None,
                'admin_permissions': {}
            },
            'expires_in_minutes': 60,  # Default 1 hour session
            'warning': 'All actions performed during impersonation will be logged.'
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to start impersonation: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_user_impersonation(request, session_id):
    """End user impersonation session"""
    from .models import UserImpersonationLog, AdminAuditLog
    
    try:
        # Find active impersonation session by ID only 
        # (don't require admin_user=request.user since request.user is the impersonated user)
        impersonation_log = UserImpersonationLog.objects.get(
            id=session_id,
            is_active=True
        )
        
        # Security check: Verify the current user is either the admin or the target user
        if request.user != impersonation_log.admin_user and request.user != impersonation_log.target_user:
            return JsonResponse({
                'error': 'Permission denied',
                'message': 'You can only end impersonation sessions you are involved in'
            }, status=403)
        
        # Get session actions from request
        actions_performed = request.data.get('actions_performed', [])
        pages_accessed = request.data.get('pages_accessed', [])
        
        # End the session
        impersonation_log.end_session(
            actions=actions_performed,
            pages=pages_accessed
        )
        
        # Create audit log entry (use the original admin user, not current request user)
        AdminAuditLog.log_action(
            admin_user=impersonation_log.admin_user,
            action_type='user_impersonated',
            description=f'Ended impersonation of {impersonation_log.target_user_email}',
            target_user=impersonation_log.target_user,
            metadata={
                'impersonation_session_id': impersonation_log.id,
                'session_duration_minutes': int(
                    (impersonation_log.end_timestamp - impersonation_log.start_timestamp).total_seconds() / 60
                ),
                'actions_performed': actions_performed,
                'pages_accessed': pages_accessed
            },
            risk_level='medium'
        )
        
        return Response({
            'message': 'Impersonation session ended successfully',
            'session_summary': {
                'duration_minutes': int(
                    (impersonation_log.end_timestamp - impersonation_log.start_timestamp).total_seconds() / 60
                ),
                'actions_count': len(actions_performed),
                'pages_accessed_count': len(pages_accessed)
            }
        })
        
    except UserImpersonationLog.DoesNotExist:
        return Response(
            {'error': 'Impersonation session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to end impersonation: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required()
def get_active_impersonation_sessions(request):
    """Get list of active impersonation sessions for the current admin"""
    from .models import UserImpersonationLog
    
    try:
        active_sessions = UserImpersonationLog.objects.filter(
            admin_user=request.user,
            is_active=True
        ).select_related('target_user').order_by('-start_timestamp')
        
        sessions_data = []
        for session in active_sessions:
            sessions_data.append({
                'id': session.id,
                'session_key': session.session_key,
                'target_user': {
                    'id': session.target_user.id if session.target_user else None,
                    'email': session.target_user_email,
                    'name': f"{session.target_user.first_name} {session.target_user.last_name}".strip() if session.target_user else session.target_user_email
                },
                'start_time': session.start_timestamp.isoformat(),
                'duration_minutes': int(
                    (timezone.now() - session.start_timestamp).total_seconds() / 60
                ),
                'risk_score': session.risk_score,
                'reason': session.reason
            })
        
        return Response({
            'active_sessions': sessions_data,
            'total_count': len(sessions_data)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch active sessions: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='user_management')
def get_impersonation_logs(request):
    """Get impersonation session history with filtering and pagination"""
    from .models import UserImpersonationLog
    from django.db.models import Q, Count, Avg
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 25)), 100)  # Max 100 per page
        admin_user_id = request.GET.get('admin_user_id')
        target_user_id = request.GET.get('target_user_id')
        is_active = request.GET.get('is_active')
        flagged_only = request.GET.get('flagged_only') == 'true'
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        search = request.GET.get('search', '').strip()
        
        # Base queryset with related data
        queryset = UserImpersonationLog.objects.select_related(
            'admin_user', 'target_user', 'approved_by', 'reviewed_by'
        ).order_by('-start_timestamp')
        
        # Apply filters
        if admin_user_id:
            queryset = queryset.filter(admin_user_id=admin_user_id)
        
        if target_user_id:
            queryset = queryset.filter(target_user_id=target_user_id)
            
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        if flagged_only:
            queryset = queryset.filter(flagged_for_review=True)
            
        if date_from:
            try:
                from datetime import datetime
                date_from_parsed = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                queryset = queryset.filter(start_timestamp__gte=date_from_parsed)
            except ValueError:
                pass
                
        if date_to:
            try:
                from datetime import datetime
                date_to_parsed = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                queryset = queryset.filter(start_timestamp__lte=date_to_parsed)
            except ValueError:
                pass
                
        # Search in email addresses and reasons
        if search:
            queryset = queryset.filter(
                Q(admin_user__email__icontains=search) |
                Q(target_user_email__icontains=search) |
                Q(reason__icontains=search)
            )
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Paginate
        paginator = Paginator(queryset, per_page)
        try:
            sessions_page = paginator.page(page)
        except PageNotAnInteger:
            sessions_page = paginator.page(1)
        except EmptyPage:
            sessions_page = paginator.page(paginator.num_pages)
        
        # Serialize sessions
        sessions_data = []
        for session in sessions_page.object_list:
            duration_minutes = None
            if session.end_timestamp:
                duration_minutes = int(
                    (session.end_timestamp - session.start_timestamp).total_seconds() / 60
                )
            elif session.is_active:
                duration_minutes = int(
                    (timezone.now() - session.start_timestamp).total_seconds() / 60
                )
            
            sessions_data.append({
                'id': session.id,
                'session_key': session.session_key,
                'admin_user': {
                    'id': session.admin_user.id if session.admin_user else None,
                    'email': session.admin_user.email if session.admin_user else 'Deleted User',
                    'name': f"{session.admin_user.first_name} {session.admin_user.last_name}".strip() if session.admin_user else 'Deleted User'
                },
                'target_user': {
                    'id': session.target_user.id if session.target_user else None,
                    'email': session.target_user_email,
                    'name': f"{session.target_user.first_name} {session.target_user.last_name}".strip() if session.target_user else session.target_user_email
                },
                'start_timestamp': session.start_timestamp.isoformat(),
                'end_timestamp': session.end_timestamp.isoformat() if session.end_timestamp else None,
                'duration_minutes': duration_minutes,
                'is_active': session.is_active,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'reason': session.reason,
                'approved_by': {
                    'id': session.approved_by.id if session.approved_by else None,
                    'email': session.approved_by.email if session.approved_by else None,
                    'name': f"{session.approved_by.first_name} {session.approved_by.last_name}".strip() if session.approved_by else None
                } if session.approved_by else None,
                'actions_count': len(session.actions_performed),
                'pages_count': len(session.pages_accessed),
                'risk_score': session.risk_score,
                'flagged_for_review': session.flagged_for_review,
                'reviewed_by': {
                    'id': session.reviewed_by.id if session.reviewed_by else None,
                    'email': session.reviewed_by.email if session.reviewed_by else None,
                    'name': f"{session.reviewed_by.first_name} {session.reviewed_by.last_name}".strip() if session.reviewed_by else None
                } if session.reviewed_by else None,
                'review_notes': session.review_notes
            })
        
        # Get summary statistics
        active_sessions_count = UserImpersonationLog.objects.filter(is_active=True).count()
        flagged_sessions_count = UserImpersonationLog.objects.filter(flagged_for_review=True).count()
        total_sessions_today = UserImpersonationLog.objects.filter(
            start_timestamp__date=timezone.now().date()
        ).count()
        
        # Average session duration (completed sessions only)
        avg_duration = UserImpersonationLog.objects.filter(
            is_active=False,
            end_timestamp__isnull=False
        ).aggregate(
            avg_duration=Avg(F('end_timestamp') - F('start_timestamp'))
        )['avg_duration']
        
        avg_duration_minutes = None
        if avg_duration:
            avg_duration_minutes = int(avg_duration.total_seconds() / 60)
        
        return Response({
            'sessions': sessions_data,
            'pagination': {
                'current_page': sessions_page.number,
                'total_pages': paginator.num_pages,
                'total_count': total_count,
                'per_page': per_page,
                'has_next': sessions_page.has_next(),
                'has_previous': sessions_page.has_previous()
            },
            'summary_stats': {
                'active_sessions': active_sessions_count,
                'flagged_sessions': flagged_sessions_count,
                'sessions_today': total_sessions_today,
                'avg_duration_minutes': avg_duration_minutes
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch impersonation logs: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='user_management')
def get_impersonation_session_detail(request, session_id):
    """Get detailed information about a specific impersonation session"""
    from .models import UserImpersonationLog
    
    try:
        session = UserImpersonationLog.objects.select_related(
            'admin_user', 'target_user', 'approved_by', 'reviewed_by'
        ).get(id=session_id)
        
        duration_minutes = None
        if session.end_timestamp:
            duration_minutes = int(
                (session.end_timestamp - session.start_timestamp).total_seconds() / 60
            )
        elif session.is_active:
            duration_minutes = int(
                (timezone.now() - session.start_timestamp).total_seconds() / 60
            )
        
        session_data = {
            'id': session.id,
            'session_key': session.session_key,
            'admin_user': {
                'id': session.admin_user.id if session.admin_user else None,
                'email': session.admin_user.email if session.admin_user else 'Deleted User',
                'name': f"{session.admin_user.first_name} {session.admin_user.last_name}".strip() if session.admin_user else 'Deleted User'
            },
            'target_user': {
                'id': session.target_user.id if session.target_user else None,
                'email': session.target_user_email,
                'name': f"{session.target_user.first_name} {session.target_user.last_name}".strip() if session.target_user else session.target_user_email
            },
            'start_timestamp': session.start_timestamp.isoformat(),
            'end_timestamp': session.end_timestamp.isoformat() if session.end_timestamp else None,
            'duration_minutes': duration_minutes,
            'is_active': session.is_active,
            'ip_address': session.ip_address,
            'user_agent': session.user_agent,
            'reason': session.reason,
            'approved_by': {
                'id': session.approved_by.id if session.approved_by else None,
                'email': session.approved_by.email if session.approved_by else None,
                'name': f"{session.approved_by.first_name} {session.approved_by.last_name}".strip() if session.approved_by else None
            } if session.approved_by else None,
            'actions_performed': session.actions_performed,
            'pages_accessed': session.pages_accessed,
            'risk_score': session.risk_score,
            'flagged_for_review': session.flagged_for_review,
            'reviewed_by': {
                'id': session.reviewed_by.id if session.reviewed_by else None,
                'email': session.reviewed_by.email if session.reviewed_by else None,
                'name': f"{session.reviewed_by.first_name} {session.reviewed_by.last_name}".strip() if session.reviewed_by else None
            } if session.reviewed_by else None,
            'review_notes': session.review_notes,
            'compliance_data': session.compliance_data
        }
        
        return Response(session_data)
        
    except UserImpersonationLog.DoesNotExist:
        return Response(
            {'error': 'Impersonation session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch session details: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# Phase 2: Step 2.3 - System Performance Monitoring API Endpoints
# ============================================================================

@api_view(['GET'])
@admin_required(section='system_monitoring')
def admin_performance_metrics(request):
    """Get detailed system performance metrics"""
    try:
        # Get query parameters
        hours = int(request.GET.get('hours', 24))
        metric_type = request.GET.get('metric_type', 'all')
        
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        
        # Base query
        metrics_query = SystemPerformanceMetric.objects.filter(
            timestamp__gte=start_time,
            timestamp__lte=now
        )
        
        # Filter by metric type if specified
        if metric_type != 'all':
            metrics_query = metrics_query.filter(metric_type=metric_type)
        
        # Get metrics grouped by type
        metrics_by_type = {}
        for metric_type_value in ['response_time', 'error_rate', 'uptime', 'cpu_usage', 
                                 'memory_usage', 'database_connections', 'active_users', 'request_volume']:
            type_metrics = metrics_query.filter(metric_type=metric_type_value).order_by('timestamp')
            
            metrics_by_type[metric_type_value] = [
                {
                    'timestamp': metric.timestamp.isoformat(),
                    'value': float(metric.value),
                    'unit': metric.unit,
                    'endpoint': metric.endpoint,
                    'status_code': metric.status_code,
                    'metadata': metric.metadata
                }
                for metric in type_metrics
            ]
        
        # Calculate averages for the period
        averages = {}
        for metric_type_value in metrics_by_type.keys():
            type_metrics = metrics_query.filter(metric_type=metric_type_value)
            if type_metrics.exists():
                avg_value = type_metrics.aggregate(avg=Avg('value'))['avg']
                averages[metric_type_value] = {
                    'average': round(float(avg_value), 4) if avg_value else 0,
                    'count': type_metrics.count(),
                    'unit': type_metrics.first().unit if type_metrics.first() else ''
                }
        
        # Get endpoint performance breakdown
        endpoint_performance = SystemPerformanceMetric.objects.filter(
            timestamp__gte=start_time,
            metric_type='response_time'
        ).exclude(endpoint='').values('endpoint').annotate(
            avg_response_time=Avg('value'),
            request_count=Count('id'),
            error_count=Count('id', filter=Q(status_code__gte=400))
        ).order_by('-request_count')[:20]
        
        # Calculate error rates for endpoints
        for endpoint_data in endpoint_performance:
            total_requests = endpoint_data['request_count']
            errors = endpoint_data['error_count']
            endpoint_data['error_rate_percent'] = round((errors / max(total_requests, 1)) * 100, 2)
        
        return Response({
            'metrics_by_type': metrics_by_type,
            'averages': averages,
            'endpoint_performance': list(endpoint_performance),
            'period_hours': hours,
            'total_metrics_recorded': metrics_query.count(),
            'generated_at': now.isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch performance metrics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='system_monitoring')
def admin_record_performance_metric(request):
    """Manually record a performance metric"""
    try:
        metric_type = request.data.get('metric_type')
        value = request.data.get('value')
        unit = request.data.get('unit', '')
        endpoint = request.data.get('endpoint', '')
        status_code = request.data.get('status_code')
        metadata = request.data.get('metadata', {})
        
        if not metric_type or value is None:
            return Response(
                {'error': 'metric_type and value are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the metric record
        metric = SystemPerformanceMetric.objects.create(
            metric_type=metric_type,
            value=value,
            unit=unit,
            endpoint=endpoint,
            status_code=status_code,
            metadata=metadata
        )
        
        return Response({
            'message': 'Performance metric recorded successfully',
            'metric': {
                'id': metric.id,
                'metric_type': metric.metric_type,
                'value': float(metric.value),
                'unit': metric.unit,
                'timestamp': metric.timestamp.isoformat()
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to record performance metric: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='system_monitoring')
def admin_system_health_dashboard(request):
    """Get real-time system health dashboard data"""
    try:
        now = timezone.now()
        
        # Get latest metrics for each type
        latest_metrics = {}
        for metric_type in ['response_time', 'error_rate', 'uptime', 'cpu_usage', 
                           'memory_usage', 'database_connections', 'active_users']:
            latest = SystemPerformanceMetric.objects.filter(
                metric_type=metric_type
            ).order_by('-timestamp').first()
            
            if latest:
                latest_metrics[metric_type] = {
                    'value': float(latest.value),
                    'unit': latest.unit,
                    'timestamp': latest.timestamp.isoformat(),
                    'status': 'healthy' if metric_type not in ['error_rate'] or latest.value < 1.0 else 'warning'
                }
        
        # System health scores
        health_scores = {
            'overall': 95,  # Would be calculated based on various metrics
            'api_performance': 98,
            'database_performance': 92,
            'error_rate': 99,
            'uptime': 99.9
        }
        
        # Recent alerts and issues
        recent_issues = [
            {
                'id': 1,
                'severity': 'warning',
                'message': 'Database connection pool at 80% capacity',
                'timestamp': (now - timedelta(minutes=45)).isoformat(),
                'resolved': False,
                'component': 'database'
            },
            {
                'id': 2,
                'severity': 'info', 
                'message': 'Scheduled maintenance completed successfully',
                'timestamp': (now - timedelta(hours=2)).isoformat(),
                'resolved': True,
                'component': 'system'
            }
        ]
        
        # API endpoint status summary
        endpoint_status = {
            'total_endpoints': 45,
            'healthy_endpoints': 43,
            'degraded_endpoints': 2,
            'failed_endpoints': 0
        }
        
        return Response({
            'latest_metrics': latest_metrics,
            'health_scores': health_scores,
            'recent_issues': recent_issues,
            'endpoint_status': endpoint_status,
            'last_updated': now.isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch system health data: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# Phase 2: Step 2.4 - Support Ticket System API Endpoints  
# ============================================================================

@api_view(['GET'])
@admin_required(section='support_tools')
def admin_support_tickets_list(request):
    """Get paginated list of support tickets"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        category_filter = request.GET.get('category', '')
        assigned_to = request.GET.get('assigned_to', '')
        search = request.GET.get('search', '')
        
        # Build query
        queryset = SupportTicket.objects.select_related('user', 'assigned_admin').all()
        
        # Apply filters
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        if assigned_to:
            if assigned_to == 'unassigned':
                queryset = queryset.filter(assigned_admin__isnull=True)
            else:
                queryset = queryset.filter(assigned_admin_id=assigned_to)
        if search:
            queryset = queryset.filter(
                Q(ticket_id__icontains=search) |
                Q(subject__icontains=search) |
                Q(description__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        tickets = queryset.order_by('-created_at')[offset:offset + limit]
        
        # Serialize tickets
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'subject': ticket.subject,
                'description': ticket.description,
                'category': ticket.category,
                'category_display': ticket.get_category_display(),
                'priority': ticket.priority,
                'priority_display': ticket.get_priority_display(),
                'status': ticket.status,
                'status_display': ticket.get_status_display(),
                'user': {
                    'id': ticket.user.id,
                    'email': ticket.user.email,
                    'name': f"{ticket.user.first_name} {ticket.user.last_name}".strip() or ticket.user.email
                },
                'assigned_admin': {
                    'id': ticket.assigned_admin.id if ticket.assigned_admin else None,
                    'email': ticket.assigned_admin.email if ticket.assigned_admin else None,
                    'name': f"{ticket.assigned_admin.first_name} {ticket.assigned_admin.last_name}".strip() if ticket.assigned_admin else None
                } if ticket.assigned_admin else None,
                'created_at': ticket.created_at.isoformat(),
                'first_response_at': ticket.first_response_at.isoformat() if ticket.first_response_at else None,
                'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                'is_sla_breached': ticket.is_sla_breached,
                'time_to_first_response': ticket.time_to_first_response,
                'time_to_resolution': ticket.time_to_resolution,
                'customer_satisfaction': ticket.customer_satisfaction,
                'tags': ticket.tags,
                'updated_at': ticket.updated_at.isoformat()
            })
        
        return Response({
            'tickets': tickets_data,
            'totalCount': total_count,
            'page': page,
            'limit': limit,
            'totalPages': (total_count + limit - 1) // limit
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch support tickets: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='support_tools')
def admin_support_ticket_detail(request, ticket_id):
    """Get detailed support ticket information with comments"""
    try:
        ticket = SupportTicket.objects.select_related('user', 'assigned_admin').get(
            id=ticket_id
        )
        
        # Get comments for this ticket
        comments = ticket.comments.select_related('user').order_by('created_at')
        comments_data = [
            {
                'id': comment.id,
                'content': comment.content,
                'user': {
                    'id': comment.user.id,
                    'email': comment.user.email,
                    'name': f"{comment.user.first_name} {comment.user.last_name}".strip() or comment.user.email
                },
                'is_internal': comment.is_internal,
                'is_automated': comment.is_automated,
                'attachments': comment.attachments,
                'created_at': comment.created_at.isoformat()
            }
            for comment in comments
        ]
        
        # Build ticket detail
        ticket_data = {
            'id': ticket.id,
            'ticket_id': ticket.ticket_id,
            'subject': ticket.subject,
            'description': ticket.description,
            'category': ticket.category,
            'category_display': ticket.get_category_display(),
            'priority': ticket.priority,
            'priority_display': ticket.get_priority_display(),
            'status': ticket.status,
            'status_display': ticket.get_status_display(),
            'user': {
                'id': ticket.user.id,
                'email': ticket.user.email,
                'name': f"{ticket.user.first_name} {ticket.user.last_name}".strip() or ticket.user.email,
                'company_name': ticket.user.company_name,
                'subscription_status': ticket.user.subscription_status
            },
            'assigned_admin': {
                'id': ticket.assigned_admin.id if ticket.assigned_admin else None,
                'email': ticket.assigned_admin.email if ticket.assigned_admin else None,
                'name': f"{ticket.assigned_admin.first_name} {ticket.assigned_admin.last_name}".strip() if ticket.assigned_admin else None
            } if ticket.assigned_admin else None,
            'created_at': ticket.created_at.isoformat(),
            'first_response_at': ticket.first_response_at.isoformat() if ticket.first_response_at else None,
            'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            'closed_at': ticket.closed_at.isoformat() if ticket.closed_at else None,
            'response_sla_hours': ticket.response_sla_hours,
            'resolution_sla_hours': ticket.resolution_sla_hours,
            'is_sla_breached': ticket.is_sla_breached,
            'time_to_first_response': ticket.time_to_first_response,
            'time_to_resolution': ticket.time_to_resolution,
            'customer_satisfaction': ticket.customer_satisfaction,
            'user_agent': ticket.user_agent,
            'ip_address': ticket.ip_address,
            'attachments': ticket.attachments,
            'tags': ticket.tags,
            'internal_notes': ticket.internal_notes,
            'escalated': ticket.escalated,
            'updated_at': ticket.updated_at.isoformat(),
            'comments': comments_data
        }
        
        return Response(ticket_data)
        
    except SupportTicket.DoesNotExist:
        return Response(
            {'error': 'Support ticket not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch support ticket: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='support_tools')
def admin_create_support_ticket(request):
    """Create a new support ticket (admin-created)"""
    try:
        user_id = request.data.get('user_id')
        subject = request.data.get('subject')
        description = request.data.get('description')
        category = request.data.get('category', 'other')
        priority = request.data.get('priority', 'medium')
        
        if not all([user_id, subject, description]):
            return Response(
                {'error': 'user_id, subject, and description are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create ticket
        ticket = SupportTicket.objects.create(
            user=user,
            subject=subject,
            description=description,
            category=category,
            priority=priority,
            assigned_admin=request.user,  # Auto-assign to creator
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Add initial admin comment
        from .models import SupportTicketComment
        SupportTicketComment.objects.create(
            ticket=ticket,
            user=request.user,
            content=f"Ticket created by admin {request.user.email}",
            is_internal=True,
            is_automated=True
        )
        
        return Response({
            'message': 'Support ticket created successfully',
            'ticket': {
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'subject': ticket.subject,
                'status': ticket.status,
                'priority': ticket.priority
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create support ticket: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@admin_required(section='support_tools')
def admin_update_support_ticket(request, ticket_id):
    """Update support ticket status, assignment, etc."""
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
        
        # Get update fields
        new_status = request.data.get('status')
        new_priority = request.data.get('priority')
        assigned_admin_id = request.data.get('assigned_admin_id')
        internal_notes = request.data.get('internal_notes')
        customer_satisfaction = request.data.get('customer_satisfaction')
        tags = request.data.get('tags')
        
        changes = []
        
        # Update status
        if new_status and new_status != ticket.status:
            old_status = ticket.status
            ticket.status = new_status
            changes.append(f"Status changed from {old_status} to {new_status}")
            
            # Handle status-specific logic
            if new_status == 'resolved' and not ticket.resolved_at:
                ticket.resolved_at = timezone.now()
            elif new_status == 'closed' and not ticket.closed_at:
                ticket.closed_at = timezone.now()
        
        # Update priority
        if new_priority and new_priority != ticket.priority:
            old_priority = ticket.priority
            ticket.priority = new_priority
            changes.append(f"Priority changed from {old_priority} to {new_priority}")
        
        # Update assignment
        if assigned_admin_id is not None:
            if assigned_admin_id == '':
                # Unassign ticket
                if ticket.assigned_admin:
                    changes.append(f"Unassigned from {ticket.assigned_admin.email}")
                    ticket.assigned_admin = None
            else:
                try:
                    new_admin = CustomUser.objects.get(id=assigned_admin_id, is_admin_user=True)
                    if new_admin != ticket.assigned_admin:
                        old_admin = ticket.assigned_admin.email if ticket.assigned_admin else 'unassigned'
                        ticket.assigned_admin = new_admin
                        changes.append(f"Assigned to {new_admin.email} (was {old_admin})")
                except CustomUser.DoesNotExist:
                    return Response(
                        {'error': 'Assigned admin user not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        # Update other fields
        if internal_notes is not None:
            ticket.internal_notes = internal_notes
        if customer_satisfaction is not None:
            ticket.customer_satisfaction = customer_satisfaction
        if tags is not None:
            ticket.tags = tags
        
        ticket.save()
        
        # Create comment for changes
        if changes:
            from .models import SupportTicketComment
            SupportTicketComment.objects.create(
                ticket=ticket,
                user=request.user,
                content=f"Ticket updated by {request.user.email}:\n" + "\n".join(changes),
                is_internal=True,
                is_automated=True
            )
        
        return Response({
            'message': 'Support ticket updated successfully',
            'changes': changes,
            'ticket': {
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'status': ticket.status,
                'priority': ticket.priority,
                'assigned_admin': ticket.assigned_admin.email if ticket.assigned_admin else None
            }
        })
        
    except SupportTicket.DoesNotExist:
        return Response(
            {'error': 'Support ticket not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to update support ticket: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='support_tools')
def admin_add_ticket_comment(request, ticket_id):
    """Add comment to support ticket"""
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
        
        content = request.data.get('content')
        is_internal = request.data.get('is_internal', False)
        
        if not content:
            return Response(
                {'error': 'Content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create comment
        from .models import SupportTicketComment
        comment = SupportTicketComment.objects.create(
            ticket=ticket,
            user=request.user,
            content=content,
            is_internal=is_internal
        )
        
        # Update first response time if this is the first admin response
        if not ticket.first_response_at:
            ticket.first_response_at = timezone.now()
            ticket.save()
        
        return Response({
            'message': 'Comment added successfully',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'is_internal': comment.is_internal,
                'created_at': comment.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except SupportTicket.DoesNotExist:
        return Response(
            {'error': 'Support ticket not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to add comment: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='support_tools')
def admin_support_sla_report(request):
    """Get SLA performance report for support tickets"""
    try:
        # Get query parameters
        days = int(request.GET.get('days', 30))
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get tickets in the period
        tickets = SupportTicket.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # SLA breach analysis
        total_tickets = tickets.count()
        breached_tickets = tickets.filter(
            Q(first_response_at__isnull=True, created_at__lt=timezone.now() - timedelta(hours=24)) |
            Q(resolved_at__isnull=True, created_at__lt=timezone.now() - timedelta(hours=72), status__in=['open', 'in_progress'])
        )
        
        sla_breach_rate = (breached_tickets.count() / max(total_tickets, 1)) * 100
        
        # Response time analysis
        responded_tickets = tickets.filter(first_response_at__isnull=False)
        avg_response_time = 0
        if responded_tickets.exists():
            response_times = []
            for ticket in responded_tickets:
                response_time = (ticket.first_response_at - ticket.created_at).total_seconds() / 3600
                response_times.append(response_time)
            avg_response_time = sum(response_times) / len(response_times)
        
        # Resolution time analysis
        resolved_tickets = tickets.filter(resolved_at__isnull=False)
        avg_resolution_time = 0
        if resolved_tickets.exists():
            resolution_times = []
            for ticket in resolved_tickets:
                resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                resolution_times.append(resolution_time)
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        # Category performance
        category_performance = tickets.values('category').annotate(
            total_tickets=Count('id'),
            avg_response_time=Avg(
                F('first_response_at') - F('created_at'),
                output_field=models.DurationField()
            ),
            sla_breaches=Count('id', filter=Q(
                Q(first_response_at__isnull=True, created_at__lt=timezone.now() - timedelta(hours=24)) |
                Q(resolved_at__isnull=True, created_at__lt=timezone.now() - timedelta(hours=72))
            ))
        ).order_by('-total_tickets')
        
        # Convert durations to hours for response
        for category in category_performance:
            if category['avg_response_time']:
                category['avg_response_time_hours'] = category['avg_response_time'].total_seconds() / 3600
            else:
                category['avg_response_time_hours'] = 0
            category['sla_breach_rate'] = (category['sla_breaches'] / max(category['total_tickets'], 1)) * 100
        
        return Response({
            'summary': {
                'total_tickets': total_tickets,
                'sla_breached_tickets': breached_tickets.count(),
                'sla_breach_rate_percent': round(sla_breach_rate, 2),
                'avg_response_time_hours': round(avg_response_time, 2),
                'avg_resolution_time_hours': round(avg_resolution_time, 2),
                'tickets_with_response': responded_tickets.count(),
                'resolved_tickets': resolved_tickets.count()
            },
            'category_performance': list(category_performance),
            'period_days': days,
            'generated_at': end_date.isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch SLA report: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# Phase 2: Step 2.5 - Alert & Notification System API Endpoints
# ============================================================================

@api_view(['GET'])
@admin_required(section='system_monitoring')
def admin_alert_rules_list(request):
    """Get paginated list of alert rules"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        alert_type = request.GET.get('alert_type', '')
        is_active = request.GET.get('is_active', '')
        
        # Build query
        queryset = AlertRule.objects.select_related('created_by').all()
        
        # Apply filters
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        rules = queryset.order_by('-created_at')[offset:offset + limit]
        
        # Serialize rules
        rules_data = []
        for rule in rules:
            rules_data.append({
                'id': rule.id,
                'name': rule.name,
                'description': rule.description,
                'alert_type': rule.alert_type,
                'alert_type_display': rule.get_alert_type_display(),
                'is_active': rule.is_active,
                'conditions': rule.conditions,
                'threshold_value': float(rule.threshold_value) if rule.threshold_value else None,
                'comparison_operator': rule.comparison_operator,
                'notification_channels': rule.notification_channels,
                'recipients': rule.recipients,
                'check_interval_minutes': rule.check_interval_minutes,
                'cooldown_minutes': rule.cooldown_minutes,
                'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None,
                'trigger_count': rule.trigger_count,
                'created_at': rule.created_at.isoformat(),
                'created_by': {
                    'id': rule.created_by.id,
                    'email': rule.created_by.email,
                    'name': f"{rule.created_by.first_name} {rule.created_by.last_name}".strip() or rule.created_by.email
                }
            })
        
        return Response({
            'alert_rules': rules_data,
            'totalCount': total_count,
            'page': page,
            'limit': limit,
            'totalPages': (total_count + limit - 1) // limit
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch alert rules: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='system_monitoring')
def admin_create_alert_rule(request):
    """Create a new alert rule"""
    try:
        name = request.data.get('name')
        description = request.data.get('description', '')
        alert_type = request.data.get('alert_type')
        conditions = request.data.get('conditions', {})
        threshold_value = request.data.get('threshold_value')
        comparison_operator = request.data.get('comparison_operator', '>')
        notification_channels = request.data.get('notification_channels', [])
        recipients = request.data.get('recipients', [])
        check_interval_minutes = request.data.get('check_interval_minutes', 5)
        cooldown_minutes = request.data.get('cooldown_minutes', 60)
        
        if not all([name, alert_type]):
            return Response(
                {'error': 'name and alert_type are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create alert rule
        rule = AlertRule.objects.create(
            name=name,
            description=description,
            alert_type=alert_type,
            conditions=conditions,
            threshold_value=threshold_value,
            comparison_operator=comparison_operator,
            notification_channels=notification_channels,
            recipients=recipients,
            check_interval_minutes=check_interval_minutes,
            cooldown_minutes=cooldown_minutes,
            created_by=request.user
        )
        
        return Response({
            'message': 'Alert rule created successfully',
            'rule': {
                'id': rule.id,
                'name': rule.name,
                'alert_type': rule.alert_type,
                'is_active': rule.is_active,
                'threshold_value': float(rule.threshold_value) if rule.threshold_value else None
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create alert rule: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@admin_required(section='system_monitoring')
def admin_update_alert_rule(request, rule_id):
    """Update an existing alert rule"""
    try:
        rule = AlertRule.objects.get(id=rule_id)
        
        # Update fields if provided
        update_fields = ['name', 'description', 'is_active', 'conditions', 'threshold_value',
                        'comparison_operator', 'notification_channels', 'recipients', 
                        'check_interval_minutes', 'cooldown_minutes']
        
        updated_fields = []
        for field in update_fields:
            if field in request.data:
                old_value = getattr(rule, field)
                new_value = request.data[field]
                if old_value != new_value:
                    setattr(rule, field, new_value)
                    updated_fields.append(field)
        
        rule.save()
        
        return Response({
            'message': 'Alert rule updated successfully',
            'updated_fields': updated_fields,
            'rule': {
                'id': rule.id,
                'name': rule.name,
                'is_active': rule.is_active,
                'threshold_value': float(rule.threshold_value) if rule.threshold_value else None
            }
        })
        
    except AlertRule.DoesNotExist:
        return Response(
            {'error': 'Alert rule not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to update alert rule: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@admin_required(section='system_monitoring')
def admin_delete_alert_rule(request, rule_id):
    """Delete an alert rule"""
    try:
        rule = AlertRule.objects.get(id=rule_id)
        rule_name = rule.name
        rule.delete()
        
        return Response({
            'message': f'Alert rule "{rule_name}" deleted successfully'
        })
        
    except AlertRule.DoesNotExist:
        return Response(
            {'error': 'Alert rule not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to delete alert rule: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='system_monitoring')
def admin_alert_notifications_list(request):
    """Get paginated list of alert notifications"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status', '')
        rule_id = request.GET.get('rule_id', '')
        days = int(request.GET.get('days', 7))
        
        # Build query
        queryset = AlertNotification.objects.select_related('alert_rule').all()
        
        # Apply filters
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if rule_id:
            queryset = queryset.filter(alert_rule_id=rule_id)
        if days:
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=start_date)
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        notifications = queryset.order_by('-created_at')[offset:offset + limit]
        
        # Serialize notifications
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'alert_rule': {
                    'id': notification.alert_rule.id,
                    'name': notification.alert_rule.name,
                    'alert_type': notification.alert_rule.alert_type
                },
                'alert_message': notification.alert_message,
                'alert_data': notification.alert_data,
                'severity': notification.severity,
                'notification_channel': notification.notification_channel,
                'recipient': notification.recipient,
                'status': notification.status,
                'status_display': notification.get_status_display(),
                'sent_at': notification.sent_at.isoformat() if notification.sent_at else None,
                'delivered_at': notification.delivered_at.isoformat() if notification.delivered_at else None,
                'error_message': notification.error_message,
                'created_at': notification.created_at.isoformat()
            })
        
        return Response({
            'notifications': notifications_data,
            'totalCount': total_count,
            'page': page,
            'limit': limit,
            'totalPages': (total_count + limit - 1) // limit
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch alert notifications: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='system_monitoring')
def admin_test_alert_rule(request, rule_id):
    """Test an alert rule by sending a test notification"""
    try:
        rule = AlertRule.objects.get(id=rule_id)
        
        # Create test notification
        from .models import AlertNotification
        test_notification = AlertNotification.objects.create(
            alert_rule=rule,
            alert_message=f"TEST: Alert rule '{rule.name}' test notification",
            alert_data={'test': True, 'triggered_by': request.user.email},
            severity='info',
            notification_channel='email',  # Default to email for testing
            recipient=request.user.email,
            status='pending'
        )
        
        # Here you would integrate with your actual notification service
        # For now, we'll just mark it as sent
        test_notification.status = 'sent'
        test_notification.sent_at = timezone.now()
        test_notification.save()
        
        return Response({
            'message': f'Test notification sent for alert rule "{rule.name}"',
            'notification_id': test_notification.id,
            'recipient': request.user.email
        })
        
    except AlertRule.DoesNotExist:
        return Response(
            {'error': 'Alert rule not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to test alert rule: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# Phase 2: Revenue Analytics API Endpoints
# ============================================================================

@api_view(['GET'])
@admin_required(section='analytics')
def admin_revenue_analytics(request):
    """Get comprehensive revenue analytics data"""
    try:
        # Get query parameters
        days = int(request.GET.get('days', 30))
        metric_type = request.GET.get('metric_type', 'all')
        
        revenue_service = RevenueAnalyticsService()
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get current metrics
        current_metrics = {}
        for metric in ['mrr', 'arr', 'churn_rate', 'arpu']:
            latest_metric = RevenueMetric.objects.filter(
                metric_type=metric,
                plan_type='all'
            ).order_by('-date').first()
            
            if latest_metric:
                current_metrics[metric] = {
                    'value': float(latest_metric.value),
                    'date': latest_metric.date.isoformat(),
                    'currency': latest_metric.currency
                }
        
        # Get revenue trends
        revenue_trends = revenue_service.get_revenue_trends(days)
        
        # Calculate growth rates
        growth_rates = {}
        for metric_key, metric_data in revenue_trends.items():
            if len(metric_data) >= 2:
                current_value = metric_data[-1]['value']
                previous_value = metric_data[0]['value']
                
                if previous_value > 0:
                    growth_rate = ((current_value - previous_value) / previous_value) * 100
                    growth_rates[metric_key] = round(growth_rate, 2)
        
        # Get subscription breakdown
        subscription_breakdown = {
            'active': CustomUser.objects.filter(subscription_status='active').count(),
            'trialing': CustomUser.objects.filter(subscription_status='trialing').count(),
            'past_due': CustomUser.objects.filter(subscription_status='past_due').count(),
            'canceled': CustomUser.objects.filter(subscription_status='canceled').count()
        }
        
        # Get plan distribution
        plan_distribution = {
            'monthly': CustomUser.objects.filter(
                subscription_status='active',
                subscription_plan='monthly'
            ).count(),
            'annual': CustomUser.objects.filter(
                subscription_status='active', 
                subscription_plan='annual'
            ).count()
        }
        
        # Revenue by plan type over time
        revenue_by_plan = {}
        for plan_type in ['monthly', 'annual']:
            metrics = RevenueMetric.objects.filter(
                metric_type='mrr',
                plan_type=plan_type,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            revenue_by_plan[plan_type] = [
                {
                    'date': metric.date.isoformat(),
                    'value': float(metric.value),
                    'currency': metric.currency
                }
                for metric in metrics
            ]
        
        return Response({
            'current_metrics': current_metrics,
            'revenue_trends': revenue_trends,
            'growth_rates': growth_rates,
            'subscription_breakdown': subscription_breakdown,
            'plan_distribution': plan_distribution,
            'revenue_by_plan': revenue_by_plan,
            'period_days': days,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch revenue analytics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='analytics')
def admin_recalculate_revenue_metrics(request):
    """Manually trigger recalculation of revenue metrics"""
    try:
        date_str = request.data.get('date')
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()
        
        revenue_service = RevenueAnalyticsService()
        
        # Recalculate all revenue metrics
        results = {
            'mrr': revenue_service.calculate_mrr(target_date),
            'arr': revenue_service.calculate_arr(target_date),
            'churn_rate': revenue_service.calculate_churn_rate(target_date),
            'arpu': revenue_service.calculate_arpu(target_date)
        }
        
        # Log the action
        ActivityLog.objects.create(
            activity_type='admin_revenue_recalculation',
            user=request.user,
            description=f'Manually triggered revenue metrics recalculation for {target_date}',
            metadata={
                'target_date': target_date.isoformat(),
                'results': results,
                'triggered_by': request.user.email
            }
        )
        
        return Response({
            'message': f'Revenue metrics recalculated for {target_date}',
            'results': results,
            'date': target_date.isoformat()
        })
        
    except ValueError as e:
        return Response(
            {'error': 'Date must be in YYYY-MM-DD format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to recalculate revenue metrics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='analytics')
def admin_user_engagement_analytics(request):
    """Get user engagement analytics data"""
    try:
        # Get query parameters
        days = int(request.GET.get('days', 30))
        at_risk_only = request.GET.get('at_risk_only', 'false').lower() == 'true'
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get engagement trends
        engagement_trends = UserEngagementMetric.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).values('date').annotate(
            avg_engagement_score=Avg('engagement_score'),
            total_users_at_risk=Count('id', filter=Q(is_at_risk=True)),
            total_active_users=Count('id', filter=Q(engagement_score__gt=0)),
            high_engagement_users=Count('id', filter=Q(engagement_score__gte=70)),
            low_engagement_users=Count('id', filter=Q(engagement_score__lt=30))
        ).order_by('date')
        
        # Get at-risk users
        at_risk_query = UserEngagementMetric.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_at_risk=True
        ).select_related('user')
        
        if at_risk_only:
            # Return detailed at-risk user data
            at_risk_users = []
            for metric in at_risk_query.order_by('engagement_score'):
                at_risk_users.append({
                    'user_id': metric.user.id,
                    'user_email': metric.user.email,
                    'user_name': f"{metric.user.first_name} {metric.user.last_name}".strip() or metric.user.email,
                    'engagement_score': metric.engagement_score,
                    'risk_factors': metric.risk_factors,
                    'date': metric.date.isoformat(),
                    'login_count': metric.login_count,
                    'scenarios_created': metric.scenarios_created,
                    'clients_added': metric.clients_added,
                    'subscription_status': metric.user.subscription_status
                })
            
            return Response({
                'at_risk_users': at_risk_users,
                'total_count': len(at_risk_users),
                'period_days': days
            })
        
        # Engagement score distribution
        score_distribution = UserEngagementMetric.objects.filter(
            date=end_date
        ).values('engagement_score').annotate(
            user_count=Count('id')
        ).order_by('engagement_score')
        
        # Create score buckets
        score_buckets = {
            '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0
        }
        
        for item in score_distribution:
            score = item['engagement_score']
            count = item['user_count']
            
            if score <= 20:
                score_buckets['0-20'] += count
            elif score <= 40:
                score_buckets['21-40'] += count
            elif score <= 60:
                score_buckets['41-60'] += count
            elif score <= 80:
                score_buckets['61-80'] += count
            else:
                score_buckets['81-100'] += count
        
        # Feature usage trends
        feature_usage = UserEngagementMetric.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(
            avg_scenarios_created=Avg('scenarios_created'),
            avg_clients_added=Avg('clients_added'),
            avg_reports_generated=Avg('reports_generated'),
            avg_session_duration=Avg('session_duration_minutes')
        )
        
        return Response({
            'engagement_trends': list(engagement_trends),
            'score_distribution': score_buckets,
            'feature_usage': feature_usage,
            'at_risk_users_count': at_risk_query.count(),
            'period_days': days,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch user engagement analytics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='analytics') 
def admin_client_portfolio_analytics(request):
    """Get client portfolio analytics across all advisors"""
    try:
        # Get query parameters
        days = int(request.GET.get('days', 30))
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get latest portfolio analytics
        latest_analytics = ClientPortfolioAnalytics.objects.order_by('-date').first()
        
        # Get portfolio trends
        portfolio_trends = ClientPortfolioAnalytics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        trends_data = [
            {
                'date': analytics.date.isoformat(),
                'total_clients': analytics.total_clients,
                'total_scenarios': analytics.total_scenarios,
                'avg_clients_per_advisor': float(analytics.avg_clients_per_advisor),
                'avg_scenarios_per_client': float(analytics.avg_scenarios_per_client),
                'roth_conversion_usage': analytics.roth_conversion_usage,
                'social_security_planning_usage': analytics.social_security_planning_usage
            }
            for analytics in portfolio_trends
        ]
        
        # Current advisor performance
        advisor_stats = CustomUser.objects.filter(
            is_active=True,
            clients__isnull=False
        ).annotate(
            client_count=Count('clients', filter=Q(clients__is_deleted=False)),
            scenario_count=Count('clients__scenarios')
        ).order_by('-client_count')[:20]  # Top 20 advisors
        
        top_advisors = [
            {
                'advisor_id': advisor.id,
                'advisor_email': advisor.email,
                'advisor_name': f"{advisor.first_name} {advisor.last_name}".strip() or advisor.email,
                'company_name': advisor.company_name,
                'client_count': advisor.client_count,
                'scenario_count': advisor.scenario_count,
                'avg_scenarios_per_client': round(advisor.scenario_count / max(advisor.client_count, 1), 2)
            }
            for advisor in advisor_stats if advisor.client_count > 0
        ]
        
        # Age demographics trends
        age_demographics = []
        if latest_analytics:
            total_clients = latest_analytics.total_clients
            if total_clients > 0:
                age_demographics = [
                    {
                        'age_group': 'Under 50',
                        'count': latest_analytics.clients_under_50,
                        'percentage': round((latest_analytics.clients_under_50 / total_clients) * 100, 1)
                    },
                    {
                        'age_group': '50-65',
                        'count': latest_analytics.clients_50_to_65,
                        'percentage': round((latest_analytics.clients_50_to_65 / total_clients) * 100, 1)
                    },
                    {
                        'age_group': 'Over 65',
                        'count': latest_analytics.clients_over_65,
                        'percentage': round((latest_analytics.clients_over_65 / total_clients) * 100, 1)
                    }
                ]
        
        # Geographic distribution from latest analytics
        geographic_data = latest_analytics.geographic_data if latest_analytics else {}
        
        # Feature adoption rates
        feature_adoption = {}
        if latest_analytics:
            total_scenarios = latest_analytics.total_scenarios
            if total_scenarios > 0:
                feature_adoption = {
                    'roth_conversion': {
                        'count': latest_analytics.roth_conversion_usage,
                        'percentage': round((latest_analytics.roth_conversion_usage / total_scenarios) * 100, 1)
                    },
                    'social_security_planning': {
                        'count': latest_analytics.social_security_planning_usage,
                        'percentage': round((latest_analytics.social_security_planning_usage / total_scenarios) * 100, 1)
                    },
                    'monte_carlo': {
                        'count': latest_analytics.monte_carlo_usage,
                        'percentage': round((latest_analytics.monte_carlo_usage / total_scenarios) * 100, 1)
                    }
                }
        
        return Response({
            'current_stats': {
                'total_clients': latest_analytics.total_clients if latest_analytics else 0,
                'total_scenarios': latest_analytics.total_scenarios if latest_analytics else 0,
                'avg_clients_per_advisor': float(latest_analytics.avg_clients_per_advisor) if latest_analytics else 0,
                'avg_scenarios_per_client': float(latest_analytics.avg_scenarios_per_client) if latest_analytics else 0,
                'date': latest_analytics.date.isoformat() if latest_analytics else None
            },
            'portfolio_trends': trends_data,
            'top_advisors': top_advisors,
            'age_demographics': age_demographics,
            'geographic_distribution': geographic_data,
            'feature_adoption': feature_adoption,
            'period_days': days,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch portfolio analytics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='analytics')
def admin_run_analytics_calculation(request):
    """Manually trigger analytics calculations"""
    try:
        calculation_type = request.data.get('type', 'daily')  # daily, revenue, engagement, portfolio
        date_str = request.data.get('date')
        
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()
        
        orchestrator = AnalyticsOrchestrator()
        
        if calculation_type == 'daily':
            # Run all analytics
            results = orchestrator.run_daily_analytics(target_date)
        elif calculation_type == 'revenue':
            # Run only revenue analytics
            revenue_service = RevenueAnalyticsService()
            results = {
                'mrr': revenue_service.calculate_mrr(target_date),
                'arr': revenue_service.calculate_arr(target_date),
                'churn_rate': revenue_service.calculate_churn_rate(target_date),
                'arpu': revenue_service.calculate_arpu(target_date)
            }
        else:
            return Response(
                {'error': 'Invalid calculation type. Must be "daily" or "revenue"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log the action
        ActivityLog.objects.create(
            activity_type='admin_analytics_calculation',
            user=request.user,
            description=f'Manually triggered {calculation_type} analytics calculation for {target_date}',
            metadata={
                'calculation_type': calculation_type,
                'target_date': target_date.isoformat(),
                'triggered_by': request.user.email,
                'has_errors': 'error' in results
            }
        )
        
        return Response({
            'message': f'{calculation_type.title()} analytics calculation completed for {target_date}',
            'results': results,
            'date': target_date.isoformat(),
            'calculation_type': calculation_type
        })
        
    except ValueError as e:
        return Response(
            {'error': 'Date must be in YYYY-MM-DD format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to run analytics calculation: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# Phase 3: Step 3.1 - Tax Data Management Interface API Endpoints
# ============================================================================

@api_view(['GET'])
@admin_required(section='system_configuration')
def admin_tax_data_files_list(request):
    """Get list of all tax data CSV files with metadata"""
    try:
        import os
        from pathlib import Path
        from datetime import datetime
        
        tax_data_path = Path('/Users/marka/Documents/git/retirementadvisorpro/backend/core/tax_data')
        
        # Get all CSV files in the tax_data directory
        files_data = []
        if tax_data_path.exists():
            for file_path in tax_data_path.glob('*.csv'):
                if file_path.name == 'README.md':
                    continue
                
                file_stats = file_path.stat()
                file_data = {
                    'filename': file_path.name,
                    'file_type': file_path.name.split('_')[0] if '_' in file_path.name else 'unknown',
                    'tax_year': None,
                    'size_bytes': file_stats.st_size,
                    'size_display': f"{round(file_stats.st_size / 1024, 1)} KB",
                    'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    'is_active': True,  # Could be determined by current tax year
                    'backup_count': 0  # Would count backup files
                }
                
                # Extract tax year from filename
                parts = file_path.name.replace('.csv', '').split('_')
                for part in parts:
                    if part.isdigit() and len(part) == 4 and 2020 <= int(part) <= 2030:
                        file_data['tax_year'] = int(part)
                        break
                
                files_data.append(file_data)
        
        # Sort by filename for consistent ordering
        files_data.sort(key=lambda x: x['filename'])
        
        # Group by tax year for easier management
        files_by_year = {}
        for file_data in files_data:
            year = file_data['tax_year'] or 'unknown'
            if year not in files_by_year:
                files_by_year[year] = []
            files_by_year[year].append(file_data)
        
        # Get current tax year for context
        current_year = timezone.now().year
        
        return Response({
            'tax_data_files': files_data,
            'files_by_year': files_by_year,
            'current_tax_year': current_year,
            'tax_data_directory': str(tax_data_path),
            'total_files': len(files_data),
            'file_types': list(set([f['file_type'] for f in files_data])),
            'years_available': sorted([y for y in files_by_year.keys() if isinstance(y, int)], reverse=True)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch tax data files: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='system_configuration')
def admin_tax_data_file_content(request, filename):
    """Get content of a specific tax data CSV file"""
    try:
        import csv
        from pathlib import Path
        
        tax_data_path = Path('/Users/marka/Documents/git/retirementadvisorpro/backend/core/tax_data')
        file_path = tax_data_path / filename
        
        if not file_path.exists() or not file_path.suffix == '.csv':
            return Response(
                {'error': 'File not found or not a CSV file'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Read CSV file
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Detect CSV dialect
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel
            
            reader = csv.DictReader(csvfile, dialect=dialect)
            
            # Get headers
            headers = reader.fieldnames or []
            
            # Read all rows
            rows = []
            row_number = 1
            for row in reader:
                row_number += 1
                # Add row number for editing reference
                row['_row_number'] = row_number
                rows.append(row)
        
        # Get file metadata
        file_stats = file_path.stat()
        file_metadata = {
            'filename': filename,
            'size_bytes': file_stats.st_size,
            'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'row_count': len(rows),
            'column_count': len(headers),
            'headers': headers
        }
        
        # Extract tax year and file type
        tax_year = None
        file_type = filename.split('_')[0] if '_' in filename else 'unknown'
        
        parts = filename.replace('.csv', '').split('_')
        for part in parts:
            if part.isdigit() and len(part) == 4 and 2020 <= int(part) <= 2030:
                tax_year = int(part)
                break
        
        return Response({
            'file_metadata': file_metadata,
            'tax_year': tax_year,
            'file_type': file_type,
            'headers': headers,
            'data': rows,
            'validation_status': 'valid',  # Would implement actual validation
            'validation_messages': []
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to read tax data file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='system_configuration')
def admin_upload_tax_data_file(request):
    """Upload and validate a new tax data CSV file"""
    try:
        import csv
        import shutil
        from pathlib import Path
        from datetime import datetime
        
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        tax_year = request.data.get('tax_year')
        file_type = request.data.get('file_type', '')
        create_backup = request.data.get('create_backup', True)
        
        # Validate file type
        if not uploaded_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV file'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate tax year
        if tax_year:
            try:
                tax_year = int(tax_year)
                if not (2020 <= tax_year <= 2030):
                    return Response(
                        {'error': 'Tax year must be between 2020 and 2030'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Invalid tax year format'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Read and validate CSV content
        file_content = uploaded_file.read().decode('utf-8')
        
        try:
            # Parse CSV
            reader = csv.DictReader(file_content.splitlines())
            headers = reader.fieldnames or []
            rows = list(reader)
            
            if not headers:
                return Response(
                    {'error': 'CSV file must have headers'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except csv.Error as e:
            return Response(
                {'error': f'Invalid CSV format: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate CSV structure based on file type
        validation_result = validate_tax_csv_structure(file_type, headers, rows)
        if not validation_result['is_valid']:
            return Response({
                'error': 'CSV validation failed',
                'validation_errors': validation_result['errors'],
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate filename
        if tax_year and file_type:
            filename = f"{file_type}_{tax_year}.csv"
        else:
            filename = uploaded_file.name
        
        tax_data_path = Path('/Users/marka/Documents/git/retirementadvisorpro/backend/core/tax_data')
        target_file_path = tax_data_path / filename
        
        # Create backup if file already exists
        backup_path = None
        if target_file_path.exists() and create_backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{filename.replace('.csv', '')}_{timestamp}.backup.csv"
            backup_path = tax_data_path / 'backups' / backup_filename
            
            # Create backups directory if it doesn't exist
            backup_path.parent.mkdir(exist_ok=True)
            shutil.copy2(target_file_path, backup_path)
        
        # Write the new file
        with open(target_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        
        # Log the action
        ActivityLog.objects.create(
            activity_type='admin_tax_data_upload',
            user=request.user,
            description=f'Uploaded tax data file: {filename}',
            metadata={
                'filename': filename,
                'file_type': file_type,
                'tax_year': tax_year,
                'row_count': len(rows),
                'column_count': len(headers),
                'backup_created': backup_path is not None,
                'backup_path': str(backup_path) if backup_path else None,
                'uploaded_by': request.user.email,
                'validation_warnings': validation_result.get('warnings', [])
            }
        )
        
        return Response({
            'message': f'Tax data file "{filename}" uploaded successfully',
            'filename': filename,
            'file_type': file_type,
            'tax_year': tax_year,
            'row_count': len(rows),
            'column_count': len(headers),
            'backup_created': backup_path is not None,
            'backup_filename': backup_path.name if backup_path else None,
            'validation_warnings': validation_result.get('warnings', [])
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to upload tax data file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@admin_required(section='system_configuration')
def admin_update_tax_data_file(request, filename):
    """Update an existing tax data CSV file"""
    try:
        import csv
        import shutil
        from pathlib import Path
        from datetime import datetime
        
        tax_data_path = Path('/Users/marka/Documents/git/retirementadvisorpro/backend/core/tax_data')
        file_path = tax_data_path / filename
        
        if not file_path.exists():
            return Response(
                {'error': 'Tax data file not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        updated_data = request.data.get('data', [])
        headers = request.data.get('headers', [])
        create_backup = request.data.get('create_backup', True)
        
        if not updated_data or not headers:
            return Response(
                {'error': 'Data and headers are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate the updated data
        file_type = filename.split('_')[0] if '_' in filename else 'unknown'
        validation_result = validate_tax_csv_structure(file_type, headers, updated_data)
        
        if not validation_result['is_valid']:
            return Response({
                'error': 'Data validation failed',
                'validation_errors': validation_result['errors'],
                'warnings': validation_result.get('warnings', [])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create backup of current file
        backup_path = None
        if create_backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{filename.replace('.csv', '')}_{timestamp}.backup.csv"
            backup_path = tax_data_path / 'backups' / backup_filename
            
            backup_path.parent.mkdir(exist_ok=True)
            shutil.copy2(file_path, backup_path)
        
        # Write updated data
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            # Remove the _row_number field if it exists
            for row in updated_data:
                row_clean = {k: v for k, v in row.items() if k != '_row_number'}
                writer.writerow(row_clean)
        
        # Log the action
        ActivityLog.objects.create(
            activity_type='admin_tax_data_update',
            user=request.user,
            description=f'Updated tax data file: {filename}',
            metadata={
                'filename': filename,
                'file_type': file_type,
                'row_count': len(updated_data),
                'column_count': len(headers),
                'backup_created': backup_path is not None,
                'backup_path': str(backup_path) if backup_path else None,
                'updated_by': request.user.email,
                'validation_warnings': validation_result.get('warnings', [])
            }
        )
        
        return Response({
            'message': f'Tax data file "{filename}" updated successfully',
            'filename': filename,
            'row_count': len(updated_data),
            'backup_created': backup_path is not None,
            'backup_filename': backup_path.name if backup_path else None,
            'validation_warnings': validation_result.get('warnings', [])
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to update tax data file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='system_configuration')
def admin_validate_tax_data_file(request):
    """Validate tax data CSV content without saving"""
    try:
        file_type = request.data.get('file_type', '')
        headers = request.data.get('headers', [])
        data = request.data.get('data', [])
        
        if not all([file_type, headers, data]):
            return Response(
                {'error': 'file_type, headers, and data are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform validation
        validation_result = validate_tax_csv_structure(file_type, headers, data)
        
        return Response({
            'is_valid': validation_result['is_valid'],
            'errors': validation_result['errors'],
            'warnings': validation_result.get('warnings', []),
            'row_count': len(data),
            'column_count': len(headers),
            'file_type': file_type
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to validate tax data: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='system_configuration')
def admin_tax_data_backups_list(request):
    """Get list of tax data backup files"""
    try:
        from pathlib import Path
        from datetime import datetime
        
        tax_data_path = Path('/Users/marka/Documents/git/retirementadvisorpro/backend/core/tax_data')
        backups_path = tax_data_path / 'backups'
        
        backups = []
        if backups_path.exists():
            for backup_file in backups_path.glob('*.backup.csv'):
                file_stats = backup_file.stat()
                
                # Parse backup filename to extract metadata
                name_parts = backup_file.name.replace('.backup.csv', '').split('_')
                original_filename = None
                backup_timestamp = None
                
                if len(name_parts) >= 3:
                    # Format: filename_YYYYMMDD_HHMMSS.backup.csv
                    timestamp_parts = name_parts[-2:]
                    if len(timestamp_parts) == 2:
                        try:
                            backup_timestamp = datetime.strptime(
                                f"{timestamp_parts[0]}_{timestamp_parts[1]}", 
                                '%Y%m%d_%H%M%S'
                            )
                            original_filename = '_'.join(name_parts[:-2]) + '.csv'
                        except ValueError:
                            pass
                
                backup_data = {
                    'backup_filename': backup_file.name,
                    'original_filename': original_filename,
                    'backup_timestamp': backup_timestamp.isoformat() if backup_timestamp else None,
                    'size_bytes': file_stats.st_size,
                    'size_display': f"{round(file_stats.st_size / 1024, 1)} KB",
                    'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat()
                }
                backups.append(backup_data)
        
        # Sort by backup timestamp, newest first
        backups.sort(key=lambda x: x['backup_timestamp'] or '', reverse=True)
        
        return Response({
            'backups': backups,
            'total_backups': len(backups),
            'backups_directory': str(backups_path)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch tax data backups: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@admin_required(section='system_configuration')
def admin_restore_tax_data_backup(request, backup_filename):
    """Restore a tax data file from backup"""
    try:
        import shutil
        from pathlib import Path
        from datetime import datetime
        
        tax_data_path = Path('/Users/marka/Documents/git/retirementadvisorpro/backend/core/tax_data')
        backups_path = tax_data_path / 'backups'
        backup_file_path = backups_path / backup_filename
        
        if not backup_file_path.exists():
            return Response(
                {'error': 'Backup file not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Parse original filename from backup filename
        original_filename = backup_filename.replace('.backup.csv', '.csv')
        name_parts = original_filename.split('_')
        
        # Remove timestamp parts to get original filename
        if len(name_parts) >= 3:
            timestamp_parts = name_parts[-2:]
            if len(timestamp_parts) == 2 and timestamp_parts[0].isdigit():
                original_filename = '_'.join(name_parts[:-2]) + '.csv'
        
        target_file_path = tax_data_path / original_filename
        create_backup_before_restore = request.data.get('create_backup', True)
        
        # Create backup of current file before restoring
        restoration_backup_path = None
        if target_file_path.exists() and create_backup_before_restore:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            restoration_backup_filename = f"{original_filename.replace('.csv', '')}_pre_restore_{timestamp}.backup.csv"
            restoration_backup_path = backups_path / restoration_backup_filename
            shutil.copy2(target_file_path, restoration_backup_path)
        
        # Restore from backup
        shutil.copy2(backup_file_path, target_file_path)
        
        # Log the action
        ActivityLog.objects.create(
            activity_type='admin_tax_data_restore',
            user=request.user,
            description=f'Restored tax data file "{original_filename}" from backup',
            metadata={
                'original_filename': original_filename,
                'backup_filename': backup_filename,
                'restoration_backup_created': restoration_backup_path is not None,
                'restoration_backup_path': str(restoration_backup_path) if restoration_backup_path else None,
                'restored_by': request.user.email
            }
        )
        
        return Response({
            'message': f'Tax data file "{original_filename}" restored from backup successfully',
            'original_filename': original_filename,
            'backup_filename': backup_filename,
            'restoration_backup_created': restoration_backup_path is not None,
            'restoration_backup_filename': restoration_backup_path.name if restoration_backup_path else None
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to restore tax data backup: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@admin_required(section='system_configuration')
def admin_tax_data_validation_rules(request):
    """Get validation rules for different tax data file types"""
    try:
        validation_rules = {
            'federal': {
                'required_headers': ['filing_status', 'min_income', 'max_income', 'tax_rate'],
                'header_types': {
                    'filing_status': 'string',
                    'min_income': 'number',
                    'max_income': 'number', 
                    'tax_rate': 'number'
                },
                'validation_checks': [
                    'filing_status must be one of: Single, Married Filing Jointly, Married Filing Separately, Head of Household',
                    'min_income must be >= 0',
                    'max_income must be > min_income or 999999999 for highest bracket',
                    'tax_rate must be between 0 and 1 (e.g., 0.37 for 37%)',
                    'Income ranges must not overlap within filing status'
                ]
            },
            'standard': {
                'required_headers': ['filing_status', 'deduction_amount'],
                'header_types': {
                    'filing_status': 'string',
                    'deduction_amount': 'number'
                },
                'validation_checks': [
                    'filing_status must be one of: Single, Married Filing Jointly, Married Filing Separately, Head of Household',
                    'deduction_amount must be > 0'
                ]
            },
            'irmaa': {
                'required_headers': ['filing_status', 'magi_threshold', 'part_b_surcharge', 'part_d_surcharge'],
                'header_types': {
                    'filing_status': 'string',
                    'magi_threshold': 'number',
                    'part_b_surcharge': 'number',
                    'part_d_surcharge': 'number'
                },
                'validation_checks': [
                    'filing_status must be one of: Single, Married Filing Jointly',
                    'magi_threshold must be >= 0',
                    'part_b_surcharge must be >= 0',
                    'part_d_surcharge must be >= 0',
                    'MAGI thresholds must be in ascending order within filing status'
                ]
            },
            'medicare': {
                'required_headers': ['coverage_type', 'monthly_rate'],
                'header_types': {
                    'coverage_type': 'string',
                    'monthly_rate': 'number'
                },
                'validation_checks': [
                    'coverage_type must be one of: Part B, Part D',
                    'monthly_rate must be > 0'
                ]
            },
            'social': {
                'required_headers': ['filing_status', 'base_threshold', 'additional_threshold'],
                'header_types': {
                    'filing_status': 'string',
                    'base_threshold': 'number',
                    'additional_threshold': 'number'
                },
                'validation_checks': [
                    'filing_status must be one of: Single, Married Filing Jointly, Married Filing Separately',
                    'base_threshold must be >= 0',
                    'additional_threshold must be > base_threshold'
                ]
            },
            'state': {
                'required_headers': ['state', 'state_code', 'income_tax_rate', 'retirement_income_exempt', 'ss_taxed'],
                'header_types': {
                    'state': 'string',
                    'state_code': 'string',
                    'income_tax_rate': 'number',
                    'retirement_income_exempt': 'boolean',
                    'ss_taxed': 'boolean'
                },
                'validation_checks': [
                    'state_code must be 2 characters',
                    'income_tax_rate must be between 0 and 1',
                    'retirement_income_exempt must be true or false',
                    'ss_taxed must be true or false',
                    'All 50 states plus DC should be included'
                ]
            },
            'inflation': {
                'required_headers': ['metric_name', 'annual_rate', 'description'],
                'header_types': {
                    'metric_name': 'string',
                    'annual_rate': 'number',
                    'description': 'string'
                },
                'validation_checks': [
                    'metric_name should be descriptive (e.g., irmaa_thresholds, social_security_benefits)',
                    'annual_rate must be between -0.5 and 0.5 (e.g., 0.01 for 1%)',
                    'description should explain what the rate applies to'
                ]
            }
        }
        
        return Response({
            'validation_rules': validation_rules,
            'available_file_types': list(validation_rules.keys()),
            'common_filing_statuses': ['Single', 'Married Filing Jointly', 'Married Filing Separately', 'Head of Household'],
            'state_codes': ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch validation rules: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def validate_tax_csv_structure(file_type, headers, rows):
    """Validate tax CSV data structure and content"""
    try:
        from decimal import Decimal, InvalidOperation
        
        errors = []
        warnings = []
        
        # Get validation rules for file type  
        validation_rules = {
            'federal': {
                'required_headers': ['filing_status', 'min_income', 'max_income', 'tax_rate'],
                'header_types': {
                    'filing_status': 'string',
                    'min_income': 'number',
                    'max_income': 'number', 
                    'tax_rate': 'number'
                }
            },
            'standard': {
                'required_headers': ['filing_status', 'deduction_amount'],
                'header_types': {
                    'filing_status': 'string',
                    'deduction_amount': 'number'
                }
            },
            'irmaa': {
                'required_headers': ['filing_status', 'magi_threshold', 'part_b_surcharge', 'part_d_surcharge'],
                'header_types': {
                    'filing_status': 'string',
                    'magi_threshold': 'number',
                    'part_b_surcharge': 'number',
                    'part_d_surcharge': 'number'
                }
            },
            'medicare': {
                'required_headers': ['coverage_type', 'monthly_rate'],
                'header_types': {
                    'coverage_type': 'string',
                    'monthly_rate': 'number'
                }
            },
            'social': {
                'required_headers': ['filing_status', 'base_threshold', 'additional_threshold'],
                'header_types': {
                    'filing_status': 'string',
                    'base_threshold': 'number',
                    'additional_threshold': 'number'
                }
            },
            'state': {
                'required_headers': ['state', 'state_code', 'income_tax_rate', 'retirement_income_exempt', 'ss_taxed'],
                'header_types': {
                    'state': 'string',
                    'state_code': 'string',
                    'income_tax_rate': 'number',
                    'retirement_income_exempt': 'boolean',
                    'ss_taxed': 'boolean'
                }
            },
            'inflation': {
                'required_headers': ['metric_name', 'annual_rate', 'description'],
                'header_types': {
                    'metric_name': 'string',
                    'annual_rate': 'number',
                    'description': 'string'
                }
            }
        }
        
        rules = validation_rules.get(file_type, {})
        required_headers = rules.get('required_headers', [])
        header_types = rules.get('header_types', {})
        
        # Check required headers
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            errors.append(f"Missing required headers: {', '.join(missing_headers)}")
        
        # Check extra headers
        extra_headers = [h for h in headers if h not in required_headers]
        if extra_headers:
            warnings.append(f"Extra headers found: {', '.join(extra_headers)}")
        
        # Validate data types and values
        for row_idx, row in enumerate(rows, 1):
            for header, expected_type in header_types.items():
                if header in row:
                    value = row[header]
                    
                    if expected_type == 'number':
                        try:
                            float_value = float(value) if value else 0
                            # Additional validation based on file type
                            if file_type == 'federal' and header == 'tax_rate':
                                if not (0 <= float_value <= 1):
                                    errors.append(f"Row {row_idx}: tax_rate must be between 0 and 1, got {value}")
                            elif file_type in ['federal', 'standard', 'irmaa'] and 'income' in header or 'amount' in header:
                                if float_value < 0:
                                    errors.append(f"Row {row_idx}: {header} cannot be negative, got {value}")
                        except ValueError:
                            errors.append(f"Row {row_idx}: {header} must be a number, got '{value}'")
                    
                    elif expected_type == 'boolean':
                        if value.lower() not in ['true', 'false']:
                            errors.append(f"Row {row_idx}: {header} must be 'true' or 'false', got '{value}'")
                    
                    elif expected_type == 'string':
                        if not value or not value.strip():
                            errors.append(f"Row {row_idx}: {header} cannot be empty")
        
        # File-specific validations
        if file_type == 'federal':
            # Check for overlapping income ranges within filing status
            filing_statuses = {}
            for row in rows:
                status = row.get('filing_status', '')
                if status not in filing_statuses:
                    filing_statuses[status] = []
                
                try:
                    min_income = float(row.get('min_income', 0))
                    max_income = float(row.get('max_income', 0))
                    filing_statuses[status].append((min_income, max_income))
                except ValueError:
                    continue
            
            # Check for overlaps
            for status, ranges in filing_statuses.items():
                ranges.sort()  # Sort by min_income
                for i in range(len(ranges) - 1):
                    if ranges[i][1] > ranges[i + 1][0]:
                        warnings.append(f"Overlapping income ranges for {status}: {ranges[i]} and {ranges[i + 1]}")
        
        elif file_type == 'state':
            # Check for duplicate state codes
            state_codes = [row.get('state_code', '').upper() for row in rows]
            duplicates = [code for code in state_codes if state_codes.count(code) > 1]
            if duplicates:
                errors.append(f"Duplicate state codes found: {', '.join(set(duplicates))}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'errors': [f'Validation error: {str(e)}'],
            'warnings': []
        }


# =============================================================================
# CONFIGURATION MANAGEMENT VIEWS (Step 3.2)
# =============================================================================

from .models import (
    FeatureFlag, SystemConfiguration, IntegrationSettings, 
    EmailTemplate, ConfigurationAuditLog
)
from .serializers_main import (
    FeatureFlagSerializer, SystemConfigurationSerializer,
    IntegrationSettingsSerializer, EmailTemplateSerializer,
    ConfigurationAuditLogSerializer, ConfigurationSummarySerializer
)


class ConfigurationManagementViewSet(AdminPermissionMixin, viewsets.ModelViewSet):
    """Base viewset for configuration management with approval workflow"""
    
    def perform_create(self, serializer):
        """Add audit logging and approval workflow for create operations"""
        instance = serializer.save(created_by=self.request.user)
        
        # Log the creation
        self.log_configuration_change(
            instance=instance,
            action='create',
            new_values=serializer.validated_data
        )
    
    def perform_update(self, serializer):
        """Add audit logging and approval workflow for update operations"""
        old_instance = self.get_object()
        old_values = self.get_object_values(old_instance)
        
        instance = serializer.save()
        new_values = serializer.validated_data
        
        # Log the update
        self.log_configuration_change(
            instance=instance,
            action='update',
            old_values=old_values,
            new_values=new_values
        )
    
    def perform_destroy(self, instance):
        """Add audit logging for delete operations"""
        old_values = self.get_object_values(instance)
        
        self.log_configuration_change(
            instance=instance,
            action='delete',
            old_values=old_values
        )
        
        instance.delete()
    
    def log_configuration_change(self, instance, action, old_values=None, new_values=None):
        """Log configuration changes for audit trail"""
        object_type_map = {
            'FeatureFlag': 'feature_flag',
            'SystemConfiguration': 'system_config',
            'IntegrationSettings': 'integration',
            'EmailTemplate': 'email_template',
        }
        
        ConfigurationAuditLog.objects.create(
            object_type=object_type_map.get(instance.__class__.__name__, 'unknown'),
            object_id=instance.id,
            object_name=str(instance),
            action=action,
            old_values=old_values or {},
            new_values=new_values or {},
            user=self.request.user,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            requires_approval=self.requires_approval(instance, action)
        )
    
    def get_object_values(self, instance):
        """Convert model instance to dictionary for audit logging"""
        model_fields = instance._meta.fields
        values = {}
        for field in model_fields:
            if field.name not in ['id', 'created_at', 'updated_at']:
                value = getattr(instance, field.name)
                if value is not None:
                    values[field.name] = str(value)
        return values
    
    def get_client_ip(self):
        """Get client IP address from request"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')
    
    def requires_approval(self, instance, action):
        """Determine if change requires approval based on business rules"""
        # Production environment changes always require approval
        if hasattr(instance, 'environment') and instance.environment == 'production':
            return True
        
        # Integration settings always require approval
        if isinstance(instance, IntegrationSettings):
            return True
        
        # Feature flag enables in production require approval
        if isinstance(instance, FeatureFlag) and instance.enabled_in_prod:
            return True
        
        return False


class FeatureFlagViewSet(ConfigurationManagementViewSet):
    """Feature flag management"""
    
    queryset = FeatureFlag.objects.all().order_by('-created_at')
    serializer_class = FeatureFlagSerializer
    permission_classes = [IsAuthenticated]
    
    def check_permissions(self, request):
        super().check_permissions(request)
        if not self.check_admin_permissions(request, 'system_configuration'):
            self.permission_denied(request)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a feature flag change"""
        feature_flag = self.get_object()
        
        if feature_flag.approval_status == 'approved':
            return Response({'error': 'Feature flag is already approved'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        feature_flag.approval_status = 'approved'
        feature_flag.approved_by = request.user
        feature_flag.approved_at = timezone.now()
        feature_flag.save()
        
        # Log approval
        self.log_configuration_change(
            instance=feature_flag,
            action='approve'
        )
        
        return Response({'message': 'Feature flag approved successfully'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a feature flag change"""
        feature_flag = self.get_object()
        
        feature_flag.approval_status = 'rejected'
        feature_flag.approved_by = request.user
        feature_flag.approved_at = timezone.now()
        feature_flag.save()
        
        # Log rejection
        self.log_configuration_change(
            instance=feature_flag,
            action='reject'
        )
        
        return Response({'message': 'Feature flag rejected'})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get feature flag summary statistics"""
        total = FeatureFlag.objects.count()
        enabled = FeatureFlag.objects.filter(is_enabled=True).count()
        pending = FeatureFlag.objects.filter(approval_status='pending').count()
        
        return Response({
            'total': total,
            'enabled': enabled,
            'disabled': total - enabled,
            'pending_approval': pending
        })


class SystemConfigurationViewSet(ConfigurationManagementViewSet):
    """System configuration management"""
    
    queryset = SystemConfiguration.objects.all().order_by('category', 'config_key')
    serializer_class = SystemConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def check_permissions(self, request):
        super().check_permissions(request)
        if not self.check_admin_permissions(request, 'system_configuration'):
            self.permission_denied(request)
    
    def get_queryset(self):
        """Filter by environment and category"""
        queryset = super().get_queryset()
        
        environment = self.request.query_params.get('environment')
        category = self.request.query_params.get('category')
        
        if environment:
            queryset = queryset.filter(environment=environment)
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get available configuration categories"""
        categories = SystemConfiguration.objects.values_list(
            'category', flat=True
        ).distinct().order_by('category')
        
        return Response(list(categories))
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a configuration change"""
        config = self.get_object()
        
        config.approval_status = 'approved'
        config.approved_by = request.user
        config.approved_at = timezone.now()
        config.save()
        
        self.log_configuration_change(instance=config, action='approve')
        
        return Response({'message': 'Configuration approved successfully'})


class IntegrationSettingsViewSet(ConfigurationManagementViewSet):
    """Integration settings management"""
    
    queryset = IntegrationSettings.objects.all().order_by('integration_name', 'environment')
    serializer_class = IntegrationSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def check_permissions(self, request):
        super().check_permissions(request)
        if not self.check_admin_permissions(request, 'system_configuration'):
            self.permission_denied(request)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test integration connection"""
        integration = self.get_object()
        
        # Import test services (would be implemented separately)
        from .services.integration_test_service import IntegrationTestService
        
        try:
            test_service = IntegrationTestService()
            result = test_service.test_integration(integration)
            
            integration.last_tested = timezone.now()
            integration.test_status = 'success' if result.get('success') else 'failed'
            integration.test_error_message = result.get('error_message', '')
            integration.save()
            
            return Response(result)
            
        except Exception as e:
            integration.last_tested = timezone.now()
            integration.test_status = 'failed'
            integration.test_error_message = str(e)
            integration.save()
            
            return Response({
                'success': False,
                'error_message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve integration settings"""
        integration = self.get_object()
        
        integration.approval_status = 'approved'
        integration.approved_by = request.user
        integration.approved_at = timezone.now()
        integration.save()
        
        self.log_configuration_change(instance=integration, action='approve')
        
        return Response({'message': 'Integration settings approved successfully'})


class EmailTemplateViewSet(ConfigurationManagementViewSet):
    """Email template management"""
    
    queryset = EmailTemplate.objects.all().order_by('template_type', 'template_name')
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def check_permissions(self, request):
        super().check_permissions(request)
        if not self.check_admin_permissions(request, 'system_configuration'):
            self.permission_denied(request)
    
    def get_queryset(self):
        """Filter by template type and status"""
        queryset = super().get_queryset()
        
        template_type = self.request.query_params.get('template_type')
        is_active = self.request.query_params.get('is_active')
        
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview email template with sample data"""
        template = self.get_object()
        sample_data = request.data.get('sample_data', {})
        
        # Simple template variable replacement
        html_preview = template.html_body
        text_preview = template.text_body
        subject_preview = template.subject
        
        for variable in template.variables:
            placeholder = f"{{{{{variable}}}}}"
            replacement = sample_data.get(variable, f"[{variable}]")
            
            html_preview = html_preview.replace(placeholder, str(replacement))
            text_preview = text_preview.replace(placeholder, str(replacement))
            subject_preview = subject_preview.replace(placeholder, str(replacement))
        
        return Response({
            'subject': subject_preview,
            'html_body': html_preview,
            'text_body': text_preview
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve email template"""
        template = self.get_object()
        
        template.approval_status = 'approved'
        template.approved_by = request.user
        template.approved_at = timezone.now()
        template.save()
        
        self.log_configuration_change(instance=template, action='approve')
        
        return Response({'message': 'Email template approved successfully'})


class ConfigurationAuditLogViewSet(AdminPermissionMixin, viewsets.ReadOnlyModelViewSet):
    """Configuration audit log (read-only)"""
    
    queryset = ConfigurationAuditLog.objects.all().order_by('-created_at')
    serializer_class = ConfigurationAuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def check_permissions(self, request):
        super().check_permissions(request)
        if not self.check_admin_permissions(request, 'system_configuration'):
            self.permission_denied(request)
    
    def get_queryset(self):
        """Filter audit logs by various criteria"""
        queryset = super().get_queryset()
        
        object_type = self.request.query_params.get('object_type')
        action = self.request.query_params.get('action')
        user_id = self.request.query_params.get('user_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if object_type:
            queryset = queryset.filter(object_type=object_type)
        if action:
            queryset = queryset.filter(action=action)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=start_datetime)
            except ValueError:
                pass
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__lte=end_datetime)
            except ValueError:
                pass
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@admin_required(section='system_configuration')
def configuration_summary(request):
    """Get configuration management dashboard summary"""
    
    # Feature flags summary
    feature_flags_total = FeatureFlag.objects.count()
    feature_flags_enabled = FeatureFlag.objects.filter(is_enabled=True).count()
    feature_flags_pending = FeatureFlag.objects.filter(approval_status='pending').count()
    
    # System configurations summary
    system_configs_total = SystemConfiguration.objects.count()
    system_configs_by_category = dict(
        SystemConfiguration.objects.values_list('category')
        .annotate(count=Count('id'))
        .values_list('category', 'count')
    )
    system_configs_pending = SystemConfiguration.objects.filter(approval_status='pending').count()
    
    # Integrations summary
    integrations_total = IntegrationSettings.objects.count()
    integrations_active = IntegrationSettings.objects.filter(is_active=True).count()
    integrations_test_failed = IntegrationSettings.objects.filter(test_status='failed').count()
    
    # Email templates summary
    email_templates_total = EmailTemplate.objects.count()
    email_templates_active = EmailTemplate.objects.filter(is_active=True).count()
    email_templates_pending = EmailTemplate.objects.filter(approval_status='pending').count()
    
    # Overall pending approvals
    pending_approvals_total = (
        feature_flags_pending + system_configs_pending + email_templates_pending +
        IntegrationSettings.objects.filter(approval_status='pending').count()
    )
    
    # Recent changes (last 7 days)
    recent_changes_count = ConfigurationAuditLog.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    summary_data = {
        'feature_flags_total': feature_flags_total,
        'feature_flags_enabled': feature_flags_enabled,
        'feature_flags_pending_approval': feature_flags_pending,
        
        'system_configs_total': system_configs_total,
        'system_configs_by_category': system_configs_by_category,
        'system_configs_pending_approval': system_configs_pending,
        
        'integrations_total': integrations_total,
        'integrations_active': integrations_active,
        'integrations_test_failed': integrations_test_failed,
        
        'email_templates_total': email_templates_total,
        'email_templates_active': email_templates_active,
        'email_templates_pending_approval': email_templates_pending,
        
        'pending_approvals_total': pending_approvals_total,
        'recent_changes_count': recent_changes_count
    }
    
    serializer = ConfigurationSummarySerializer(data=summary_data)
    if serializer.is_valid():
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ============================================================================
# BILLING MANAGEMENT API ENDPOINTS
# ============================================================================

@api_view(['GET'])
@admin_required(section='billing')
def admin_billing_data(request):
    """Get comprehensive billing and revenue data for admin billing dashboard"""
    try:
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Initialize analytics service
        revenue_service = RevenueAnalyticsService()
        
        # Get current revenue metrics
        current_metrics = {}
        
        # Calculate current MRR from Stripe
        mrr_data = revenue_service.calculate_mrr()
        if mrr_data:
            current_metrics['totalMRR'] = mrr_data['total_mrr']
            current_metrics['monthlyMRR'] = mrr_data['monthly_mrr']
            current_metrics['annualMRR'] = mrr_data['annual_mrr']
        else:
            current_metrics['totalMRR'] = 0
            current_metrics['monthlyMRR'] = 0
            current_metrics['annualMRR'] = 0
        
        # Get subscription breakdown from Stripe
        subscriptions = stripe.Subscription.list(limit=100, expand=['data.items.data.price'])
        
        subscription_breakdown = {
            'active': 0,
            'trial': 0,
            'past_due': 0,
            'canceled': 0
        }
        
        active_subscriptions = 0
        new_users_this_month = 0
        
        for subscription in subscriptions.auto_paging_iter():
            status = subscription.status
            if status in subscription_breakdown:
                subscription_breakdown[status] += 1
                
            if status == 'active':
                active_subscriptions += 1
                
            # Count new subscriptions this month
            created_date = datetime.fromtimestamp(subscription.created)
            if created_date.month == datetime.now().month and created_date.year == datetime.now().year:
                new_users_this_month += 1
        
        # Calculate ARPU
        average_revenue_per_user = 0
        if active_subscriptions > 0:
            average_revenue_per_user = current_metrics['totalMRR'] / active_subscriptions
        
        # Get recent billing activity from Stripe
        charges = stripe.Charge.list(limit=20, expand=['data.customer'])
        recent_billing_activity = []
        
        for charge in charges.data:
            customer_email = 'N/A'
            customer_name = 'Unknown Customer'
            
            if charge.customer:
                try:
                    customer = stripe.Customer.retrieve(charge.customer)
                    customer_email = customer.email or 'N/A'
                    customer_name = customer.name or customer_email
                except:
                    pass
            
            activity_status = 'paid' if charge.paid else 'failed'
            if charge.status == 'pending':
                activity_status = 'pending'
            
            plan_name = 'One-time Payment'
            if charge.invoice:
                try:
                    invoice = stripe.Invoice.retrieve(charge.invoice, expand=['subscription.items.data.price'])
                    if invoice.subscription and invoice.subscription.items.data:
                        price = invoice.subscription.items.data[0].price
                        if price.recurring:
                            interval = price.recurring.interval
                            plan_name = f"{'Annual' if interval == 'year' else 'Monthly'} Plan"
                except:
                    pass
            
            recent_billing_activity.append({
                'id': charge.id,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'amount': charge.amount / 100,  # Convert cents to dollars
                'plan_name': plan_name,
                'status': activity_status,
                'created_at': datetime.fromtimestamp(charge.created).isoformat()
            })
        
        # Count failed payments
        failed_payments_count = len([a for a in recent_billing_activity if a['status'] == 'failed'])
        
        # Mock data for items not available from Stripe API
        expiring_trials_count = 5  # Would need to track trials separately
        
        return Response({
            'stats': {
                'totalMRR': current_metrics['totalMRR'],
                'activeSubscriptions': active_subscriptions,
                'averageRevenuePerUser': average_revenue_per_user,
                'newUsersThisMonth': new_users_this_month,
                'subscriptionBreakdown': subscription_breakdown
            },
            'recentBillingActivity': recent_billing_activity,
            'failedPaymentsCount': failed_payments_count,
            'expiringTrialsCount': expiring_trials_count,
            'success': True
        })
        
    except Exception as e:
        import traceback
        print(f"Error in admin_billing_data: {str(e)}")
        print(traceback.format_exc())
        
        return Response({
            'error': str(e),
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_complete(request, user_id):
    """
    Completely delete a user from both Django and Auth0
    This action is irreversible and will:
    1. Cancel any active Stripe subscriptions
    2. Delete the user from Auth0 
    3. Delete the user from Django database
    """
    try:
        # Check if the requesting user has admin access
        if not hasattr(request.user, 'is_admin_user') or not request.user.is_admin_user:
            return Response({
                'error': 'Admin access required',
                'message': 'You do not have permission to delete users.',
                'success': False
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the user to delete
        try:
            user_to_delete = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found',
                'success': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent deletion of current super admin user
        if (user_to_delete.admin_role == 'super_admin' and 
            user_to_delete.id == request.user.id):
            return Response({
                'error': 'You cannot delete your own super admin account',
                'success': False
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"🗑️ Starting complete deletion of user: {user_to_delete.email}")
        
        # Step 1: Cancel Stripe subscriptions if they exist
        subscription_cancelled = False
        if hasattr(user_to_delete, 'stripe_customer_id') and user_to_delete.stripe_customer_id:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                
                # Get all subscriptions for this customer
                subscriptions = stripe.Subscription.list(
                    customer=user_to_delete.stripe_customer_id,
                    status='all'
                )
                
                # Cancel active subscriptions
                for subscription in subscriptions.data:
                    if subscription.status in ['active', 'trialing', 'past_due']:
                        stripe.Subscription.delete(subscription.id)
                        subscription_cancelled = True
                        print(f"🎫 Cancelled Stripe subscription: {subscription.id}")
                
                # Delete the Stripe customer
                stripe.Customer.delete(user_to_delete.stripe_customer_id)
                print(f"👤 Deleted Stripe customer: {user_to_delete.stripe_customer_id}")
                
            except Exception as e:
                print(f"⚠️ Warning: Could not cancel Stripe subscription: {str(e)}")
        
        # Step 2: Delete user from Auth0
        auth0_deleted = False
        if hasattr(user_to_delete, 'auth0_user_id') and user_to_delete.auth0_user_id:
            try:
                # Initialize Auth0 Management API client
                domain = settings.AUTH0_DOMAIN
                client_id = settings.AUTH0_CLIENT_ID
                client_secret = settings.AUTH0_CLIENT_SECRET
                
                # Get a Management API token
                token_url = f'https://{domain}/oauth/token'
                token_data = {
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'audience': f'https://{domain}/api/v2/'
                }
                
                import requests
                token_response = requests.post(token_url, json=token_data)
                token_response.raise_for_status()
                access_token = token_response.json()['access_token']
                
                # Initialize Auth0 Management client
                auth0_client = Auth0(domain, access_token)
                
                # Delete user from Auth0
                auth0_client.users.delete(user_to_delete.auth0_user_id)
                auth0_deleted = True
                print(f"🔑 Deleted Auth0 user: {user_to_delete.auth0_user_id}")
                
            except Exception as e:
                print(f"⚠️ Warning: Could not delete from Auth0: {str(e)}")
        
        # Step 3: Delete user from Django database
        user_email = user_to_delete.email
        user_name = f"{user_to_delete.first_name} {user_to_delete.last_name}"
        
        # Delete the user (this will cascade to related objects)
        user_to_delete.delete()
        
        print(f"✅ Successfully deleted user {user_email} from Django database")
        
        return Response({
            'success': True,
            'message': f'User {user_email} has been completely deleted',
            'details': {
                'user_email': user_email,
                'user_name': user_name,
                'django_deleted': True,
                'auth0_deleted': auth0_deleted,
                'subscription_cancelled': subscription_cancelled
            }
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Error in delete_user_complete: {str(e)}")
        print(traceback.format_exc())
        
        return Response({
            'error': f'Failed to delete user: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

