"""
Stripe Connect integration for affiliate payouts
Handles onboarding, account management, and automated payouts
"""

import stripe
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal
import uuid

from .affiliate_models import Affiliate, AffiliatePayout, Commission
from .affiliate_serializers import AffiliateSerializer
from .affiliate_emails import send_affiliate_payout_confirmation

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_connect_account(request):
    """
    Create a Stripe Connect account for an affiliate
    """
    try:
        # Get affiliate account for the user
        try:
            affiliate = Affiliate.objects.get(user=request.user)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'No affiliate account found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already has a Stripe account
        if affiliate.stripe_connect_account_id:
            return Response(
                {'error': 'Stripe account already exists', 'account_id': affiliate.stripe_connect_account_id},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Stripe Connect account
        account = stripe.Account.create(
            type='express',  # Using Express accounts for simplicity
            country='US',
            email=affiliate.email,
            capabilities={
                'transfers': {'requested': True},
            },
            business_type='individual',
            business_profile={
                'name': affiliate.business_name,
                'url': affiliate.website_url if affiliate.website_url else None,
            },
            metadata={
                'affiliate_id': str(affiliate.id),
                'affiliate_code': affiliate.affiliate_code
            }
        )
        
        # Save the account ID
        affiliate.stripe_connect_account_id = account.id
        affiliate.save(update_fields=['stripe_connect_account_id'])
        
        return Response({
            'success': True,
            'account_id': account.id,
            'message': 'Stripe Connect account created successfully'
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_account_link(request):
    """
    Create an account link for Stripe Connect onboarding
    """
    try:
        # Get affiliate account
        try:
            affiliate = Affiliate.objects.get(user=request.user)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'No affiliate account found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create account if doesn't exist
        if not affiliate.stripe_connect_account_id:
            # First create the account
            account = stripe.Account.create(
                type='express',
                country='US',
                email=affiliate.email,
                capabilities={
                    'transfers': {'requested': True},
                },
                metadata={
                    'affiliate_id': str(affiliate.id),
                    'affiliate_code': affiliate.affiliate_code
                }
            )
            affiliate.stripe_connect_account_id = account.id
            affiliate.save(update_fields=['stripe_connect_account_id'])
        
        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=affiliate.stripe_connect_account_id,
            refresh_url=f"{settings.FRONTEND_URL}/affiliates/{affiliate.id}/stripe-connect?refresh=true",
            return_url=f"{settings.FRONTEND_URL}/affiliates/{affiliate.id}/stripe-connect?success=true",
            type='account_onboarding',
        )
        
        return Response({
            'success': True,
            'url': account_link.url,
            'expires_at': account_link.expires_at
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_status(request):
    """
    Get the status of an affiliate's Stripe Connect account
    """
    try:
        # Get affiliate account
        try:
            affiliate = Affiliate.objects.get(user=request.user)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'No affiliate account found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not affiliate.stripe_connect_account_id:
            return Response({
                'status': 'not_created',
                'message': 'No Stripe Connect account exists'
            })
        
        # Get account details from Stripe
        account = stripe.Account.retrieve(affiliate.stripe_connect_account_id)
        
        # Update affiliate record with latest status
        affiliate.stripe_account_status = 'active' if account.charges_enabled else 'pending'
        affiliate.stripe_payouts_enabled = account.payouts_enabled
        affiliate.save(update_fields=['stripe_account_status', 'stripe_payouts_enabled'])
        
        return Response({
            'status': 'active' if account.charges_enabled else 'pending',
            'account_id': account.id,
            'charges_enabled': account.charges_enabled,
            'payouts_enabled': account.payouts_enabled,
            'details_submitted': account.details_submitted,
            'requirements': {
                'currently_due': account.requirements.currently_due if account.requirements else [],
                'eventually_due': account.requirements.eventually_due if account.requirements else [],
                'past_due': account.requirements.past_due if account.requirements else [],
            },
            'capabilities': account.capabilities,
            'business_profile': account.business_profile
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payout(request):
    """
    Create a manual payout to an affiliate
    Admin only - usually payouts are automated
    """
    try:
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        affiliate_id = request.data.get('affiliate_id')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'usd')
        description = request.data.get('description', 'Affiliate commission payout')
        
        if not affiliate_id or not amount:
            return Response(
                {'error': 'affiliate_id and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get affiliate
        try:
            affiliate = Affiliate.objects.get(id=affiliate_id)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'Affiliate not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not affiliate.stripe_connect_account_id:
            return Response(
                {'error': 'Affiliate has no Stripe Connect account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create transfer to Connect account
        transfer = stripe.Transfer.create(
            amount=int(Decimal(amount) * 100),  # Convert to cents
            currency=currency,
            destination=affiliate.stripe_connect_account_id,
            description=description,
            metadata={
                'affiliate_id': str(affiliate.id),
                'affiliate_code': affiliate.affiliate_code,
                'payout_type': 'manual'
            }
        )
        
        # Create payout record
        payout = AffiliatePayout.objects.create(
            affiliate=affiliate,
            payout_period_start=timezone.now().date(),
            payout_period_end=timezone.now().date(),
            total_commissions=Decimal(amount),
            net_payout=Decimal(amount),
            payment_method='stripe_connect',
            stripe_transfer_id=transfer.id,
            payment_reference=transfer.id,
            status='completed',
            processed_at=timezone.now(),
            tax_year=timezone.now().year,
            notes=f"Manual payout: {description}"
        )
        
        # Send payout confirmation email
        send_affiliate_payout_confirmation.delay(str(affiliate.id), str(payout.id))
        
        return Response({
            'success': True,
            'transfer_id': transfer.id,
            'payout_id': str(payout.id),
            'amount': amount,
            'status': 'completed'
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_batch_payouts(request):
    """
    Process batch payouts for all eligible affiliates
    Admin only - can be called manually or via cron job
    """
    try:
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get date range for payouts (default: last month)
        from datetime import date, timedelta
        from dateutil.relativedelta import relativedelta
        
        end_date = request.data.get('end_date')
        if end_date:
            end_date = date.fromisoformat(end_date)
        else:
            # Default to end of last month
            today = date.today()
            end_date = date(today.year, today.month, 1) - timedelta(days=1)
        
        start_date = request.data.get('start_date')
        if start_date:
            start_date = date.fromisoformat(start_date)
        else:
            # Default to start of last month
            start_date = date(end_date.year, end_date.month, 1)
        
        # Minimum payout threshold
        min_payout = Decimal(request.data.get('min_payout', '50.00'))
        
        # Get all affiliates with Stripe accounts
        affiliates = Affiliate.objects.filter(
            stripe_connect_account_id__isnull=False,
            stripe_payouts_enabled=True,
            status='active'
        )
        
        results = []
        
        for affiliate in affiliates:
            # Get unpaid commissions for the period
            unpaid_commissions = Commission.objects.filter(
                affiliate=affiliate,
                status='approved',
                payout__isnull=True,
                period_start__gte=start_date,
                period_end__lte=end_date
            )
            
            total_amount = sum(c.commission_amount for c in unpaid_commissions)
            
            if total_amount < min_payout:
                results.append({
                    'affiliate': affiliate.business_name,
                    'status': 'skipped',
                    'reason': f'Below minimum payout threshold (${min_payout})',
                    'amount': str(total_amount)
                })
                continue
            
            try:
                # Create Stripe transfer
                transfer = stripe.Transfer.create(
                    amount=int(total_amount * 100),  # Convert to cents
                    currency='usd',
                    destination=affiliate.stripe_connect_account_id,
                    description=f"Commission payout for {start_date} to {end_date}",
                    metadata={
                        'affiliate_id': str(affiliate.id),
                        'period_start': str(start_date),
                        'period_end': str(end_date),
                        'commission_count': str(unpaid_commissions.count())
                    }
                )
                
                # Create payout record
                payout = AffiliatePayout.objects.create(
                    affiliate=affiliate,
                    payout_period_start=start_date,
                    payout_period_end=end_date,
                    total_commissions=total_amount,
                    net_payout=total_amount,
                    payment_method='stripe_connect',
                    stripe_transfer_id=transfer.id,
                    payment_reference=transfer.id,
                    status='completed',
                    processed_at=timezone.now(),
                    tax_year=end_date.year
                )
                
                # Update commissions with payout reference
                unpaid_commissions.update(
                    payout=payout,
                    status='paid',
                    paid_at=timezone.now()
                )
                
                # Send payout confirmation email
                send_affiliate_payout_confirmation.delay(str(affiliate.id), str(payout.id))
                
                results.append({
                    'affiliate': affiliate.business_name,
                    'status': 'success',
                    'transfer_id': transfer.id,
                    'amount': str(total_amount),
                    'commissions_paid': unpaid_commissions.count()
                })
                
            except stripe.error.StripeError as e:
                results.append({
                    'affiliate': affiliate.business_name,
                    'status': 'failed',
                    'error': str(e),
                    'amount': str(total_amount)
                })
        
        return Response({
            'success': True,
            'period': f"{start_date} to {end_date}",
            'results': results,
            'total_processed': len(results),
            'total_paid': sum(1 for r in results if r['status'] == 'success')
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payout_dashboard(request):
    """
    Get payout dashboard data for an affiliate
    """
    try:
        # Get affiliate account
        try:
            affiliate = Affiliate.objects.get(user=request.user)
        except Affiliate.DoesNotExist:
            return Response(
                {'error': 'No affiliate account found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get payout statistics
        total_paid = AffiliatePayout.objects.filter(
            affiliate=affiliate,
            status='completed'
        ).aggregate(
            total=models.Sum('net_payout')
        )['total'] or Decimal('0.00')
        
        pending_amount = Commission.objects.filter(
            affiliate=affiliate,
            status='approved',
            payout__isnull=True
        ).aggregate(
            total=models.Sum('commission_amount')
        )['total'] or Decimal('0.00')
        
        # Get recent payouts
        recent_payouts = AffiliatePayout.objects.filter(
            affiliate=affiliate
        ).order_by('-created_at')[:10]
        
        # Get Stripe account status
        stripe_status = 'not_connected'
        if affiliate.stripe_connect_account_id:
            try:
                account = stripe.Account.retrieve(affiliate.stripe_connect_account_id)
                stripe_status = 'active' if account.payouts_enabled else 'pending'
            except:
                stripe_status = 'error'
        
        return Response({
            'total_paid': str(total_paid),
            'pending_amount': str(pending_amount),
            'stripe_status': stripe_status,
            'stripe_account_id': affiliate.stripe_connect_account_id,
            'recent_payouts': [
                {
                    'id': str(p.id),
                    'period': f"{p.payout_period_start} to {p.payout_period_end}",
                    'amount': str(p.net_payout),
                    'status': p.status,
                    'date': p.processed_at.isoformat() if p.processed_at else None
                }
                for p in recent_payouts
            ],
            'payout_settings': {
                'payment_method': affiliate.payment_method,
                'minimum_payout': '50.00',
                'payout_schedule': 'monthly'
            }
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Import for aggregate
from django.db import models