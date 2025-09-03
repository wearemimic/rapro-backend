# backend/core/billing_views.py

import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_details(request):
    """
    Get user's subscription details, billing history, and payment methods
    """
    try:
        user = request.user
        
        # Check if user has Stripe customer ID
        if not user.stripe_customer_id:
            return Response({
                'subscription': None,
                'invoices': [],
                'payment_method': None,
                'message': 'No billing information found'
            })
        
        # Get subscription details
        subscription_data = None
        if user.stripe_subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
                
                # Handle both new (items-based) and old (plan-based) subscription formats
                plan_name = 'Monthly Plan'
                amount = 0
                interval = 'month'
                
                if hasattr(subscription, 'items') and hasattr(subscription.items, 'data') and subscription.items.data:
                    # New format with items
                    item = subscription.items.data[0]
                    plan_name = item.price.nickname or 'Monthly Plan'
                    amount = item.price.unit_amount / 100
                    interval = item.price.recurring.interval
                elif hasattr(subscription, 'plan') and subscription.plan:
                    # Old format with plan
                    plan_name = subscription.plan.get('nickname') or f"${subscription.plan.get('amount', 0) / 100:.2f}/{subscription.plan.get('interval', 'month')}"
                    amount = subscription.plan.get('amount', 0) / 100
                    interval = subscription.plan.get('interval', 'month')
                
                # Determine effective status for display
                effective_status = subscription.status
                if subscription.status == 'active' and getattr(subscription, 'cancel_at_period_end', False):
                    effective_status = 'canceled_pending'
                
                subscription_data = {
                    'stripe_subscription_id': subscription.id,
                    'stripe_customer_id': user.stripe_customer_id,
                    'status': subscription.status,
                    'effective_status': effective_status,
                    'current_period_start': getattr(subscription, 'current_period_start', subscription.created),
                    'current_period_end': getattr(subscription, 'current_period_end', None),
                    'plan_name': plan_name,
                    'amount': amount,
                    'interval': interval,
                    'created': subscription.created,
                    'canceled_at': getattr(subscription, 'canceled_at', None),
                    'cancel_at_period_end': getattr(subscription, 'cancel_at_period_end', False),
                }
            except stripe.error.StripeError as e:
                logger.error(f"Failed to retrieve subscription: {str(e)}")
        
        # Get billing history (invoices)
        invoices_data = []
        try:
            invoices = stripe.Invoice.list(
                customer=user.stripe_customer_id,
                limit=12  # Last 12 invoices
            )
            
            for invoice in invoices.data:
                invoices_data.append({
                    'id': invoice.id,
                    'amount_paid': invoice.amount_paid,
                    'amount_due': invoice.amount_due,
                    'created': invoice.created,
                    'status': invoice.status,
                    'description': invoice.description,
                    'invoice_pdf': invoice.invoice_pdf,
                    'hosted_invoice_url': invoice.hosted_invoice_url,
                    'period_start': invoice.period_start,
                    'period_end': invoice.period_end,
                })
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve invoices: {str(e)}")
        
        # Get default payment method
        payment_method_data = None
        try:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
            if customer.invoice_settings.default_payment_method:
                payment_method = stripe.PaymentMethod.retrieve(
                    customer.invoice_settings.default_payment_method
                )
                if payment_method.type == 'card':
                    payment_method_data = {
                        'id': payment_method.id,
                        'type': payment_method.type,
                        'last4': payment_method.card.last4,
                        'brand': payment_method.card.brand,
                        'exp_month': payment_method.card.exp_month,
                        'exp_year': payment_method.card.exp_year,
                    }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve payment method: {str(e)}")
        
        return Response({
            'subscription': subscription_data,
            'invoices': invoices_data,
            'payment_method': payment_method_data,
        })
        
    except Exception as e:
        logger.error(f"Billing details error: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve billing information'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """
    Cancel user's subscription at period end
    """
    try:
        user = request.user
        
        if not user.stripe_subscription_id:
            return Response(
                {'error': 'No active subscription found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cancellation reason and feedback (optional)
        reason = request.data.get('reason', '')
        feedback = request.data.get('feedback', '')
        
        # Cancel subscription at period end
        subscription = stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=True,
            metadata={
                'cancellation_reason': reason,
                'cancellation_feedback': feedback,
                'canceled_by': user.email,
                'canceled_at': datetime.utcnow().isoformat()
            }
        )
        
        # Update user's subscription status (but keep as 'active' until period end)
        # We'll let webhooks or periodic tasks handle setting to 'canceled' when it actually ends
        if subscription.status != 'active':
            user.subscription_status = subscription.status
            user.save()
        
        logger.info(f"Subscription {user.stripe_subscription_id} canceled for user {user.email}")
        
        return Response({
            'success': True,
            'message': 'Subscription canceled successfully. Access will continue until the end of the current billing period.',
            'cancel_at_period_end': subscription.cancel_at_period_end,
            'current_period_end': getattr(subscription, 'current_period_end', None)
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe cancellation error: {str(e)}")
        return Response(
            {'error': f'Failed to cancel subscription: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Cancellation error: {str(e)}")
        return Response(
            {'error': 'Failed to cancel subscription'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactivate_subscription(request):
    """
    Reactivate a canceled subscription
    """
    try:
        user = request.user
        
        if not user.stripe_subscription_id:
            return Response(
                {'error': 'No subscription found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reactivate subscription by removing cancel_at_period_end
        subscription = stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        # Update user's subscription status
        user.subscription_status = subscription.status
        user.save()
        
        logger.info(f"Subscription {user.stripe_subscription_id} reactivated for user {user.email}")
        
        return Response({
            'success': True,
            'message': 'Subscription reactivated successfully',
            'status': subscription.status
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe reactivation error: {str(e)}")
        return Response(
            {'error': f'Failed to reactivate subscription: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Reactivation error: {str(e)}")
        return Response(
            {'error': 'Failed to reactivate subscription'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_payment_method(request):
    """
    Create a Stripe setup intent for updating payment method
    """
    try:
        user = request.user
        
        if not user.stripe_customer_id:
            return Response(
                {'error': 'No customer record found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create setup intent for payment method update
        setup_intent = stripe.SetupIntent.create(
            customer=user.stripe_customer_id,
            usage='off_session'
        )
        
        return Response({
            'client_secret': setup_intent.client_secret,
            'setup_intent_id': setup_intent.id
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Setup intent creation error: {str(e)}")
        return Response(
            {'error': f'Failed to setup payment method update: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Payment method update error: {str(e)}")
        return Response(
            {'error': 'Failed to setup payment method update'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_invoice(request, invoice_id):
    """
    Get invoice download URL
    """
    try:
        user = request.user
        
        # Verify the invoice belongs to this customer
        invoice = stripe.Invoice.retrieve(invoice_id)
        
        if invoice.customer != user.stripe_customer_id:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'download_url': invoice.invoice_pdf,
            'hosted_url': invoice.hosted_invoice_url
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Invoice retrieval error: {str(e)}")
        return Response(
            {'error': 'Invoice not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Download invoice error: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve invoice'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )