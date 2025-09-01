import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

from .services.analytics_service import RevenueAnalyticsService

logger = logging.getLogger(__name__)
User = get_user_model()

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload received from Stripe: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature from Stripe: {str(e)}")
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'customer.subscription.created':
        handle_subscription_created(event.data.object)
    elif event.type == 'customer.subscription.updated':
        handle_subscription_updated(event.data.object)
    elif event.type == 'customer.subscription.deleted':
        handle_subscription_deleted(event.data.object)
    elif event.type == 'invoice.payment_succeeded':
        handle_payment_succeeded(event.data.object)
    elif event.type == 'invoice.payment_failed':
        handle_payment_failed(event.data.object)
    else:
        logger.info(f"Unhandled event type: {event.type}")

    return HttpResponse(status=200)

def handle_subscription_created(subscription):
    try:
        user = User.objects.get(stripe_customer_id=subscription.customer)
        user.stripe_subscription_id = subscription.id
        user.subscription_status = subscription.status
        user.subscription_plan = 'monthly' if subscription.items.data[0].price.recurring.interval == 'month' else 'annual'
        
        # Set end date for fixed-length subscriptions
        if subscription.cancel_at:
            user.subscription_end_date = timezone.datetime.fromtimestamp(subscription.cancel_at)
        
        user.save()
        logger.info(f"Subscription created successfully for user {user.email}")
        
        # Trigger revenue analytics recalculation
        trigger_revenue_analytics()
        
    except User.DoesNotExist:
        logger.error(f"User not found for Stripe customer ID: {subscription.customer}")
    except Exception as e:
        logger.error(f"Error handling subscription creation: {str(e)}")

def handle_subscription_updated(subscription):
    try:
        user = User.objects.get(stripe_subscription_id=subscription.id)
        user.subscription_status = subscription.status
        
        # Update plan if changed
        new_plan = 'monthly' if subscription.items.data[0].price.recurring.interval == 'month' else 'annual'
        if user.subscription_plan != new_plan:
            user.subscription_plan = new_plan
        
        # Update end date if applicable
        if subscription.cancel_at:
            user.subscription_end_date = timezone.datetime.fromtimestamp(subscription.cancel_at)
        else:
            user.subscription_end_date = None
        
        user.save()
        logger.info(f"Subscription updated successfully for user {user.email}")
        
        # Trigger revenue analytics recalculation
        trigger_revenue_analytics()
        
    except User.DoesNotExist:
        logger.error(f"User not found for Stripe subscription ID: {subscription.id}")
    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")

def handle_subscription_deleted(subscription):
    try:
        user = User.objects.get(stripe_subscription_id=subscription.id)
        user.subscription_status = 'canceled'
        user.subscription_end_date = timezone.now()
        user.save()
        logger.info(f"Subscription canceled successfully for user {user.email}")
        
        # Trigger revenue analytics recalculation
        trigger_revenue_analytics()
        
    except User.DoesNotExist:
        logger.error(f"User not found for Stripe subscription ID: {subscription.id}")
    except Exception as e:
        logger.error(f"Error handling subscription deletion: {str(e)}")

def handle_payment_succeeded(invoice):
    try:
        user = User.objects.get(stripe_customer_id=invoice.customer)
        logger.info(f"Payment succeeded for user {user.email}")
    except User.DoesNotExist:
        logger.error(f"User not found for Stripe customer ID: {invoice.customer}")
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")

def handle_payment_failed(invoice):
    try:
        user = User.objects.get(stripe_customer_id=invoice.customer)
        user.subscription_status = 'past_due'
        user.save()
        logger.info(f"Payment failed for user {user.email}, status updated to past_due")
        
        # Trigger revenue analytics recalculation
        trigger_revenue_analytics()
        
    except User.DoesNotExist:
        logger.error(f"User not found for Stripe customer ID: {invoice.customer}")
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")


def trigger_revenue_analytics():
    """Trigger recalculation of revenue analytics after subscription changes"""
    try:
        revenue_service = RevenueAnalyticsService()
        today = timezone.now().date()
        
        # Recalculate key metrics
        revenue_service.calculate_mrr(today)
        revenue_service.calculate_arr(today)
        revenue_service.calculate_churn_rate(today)
        revenue_service.calculate_arpu(today)
        
        logger.info("Revenue analytics recalculated after subscription change")
        
    except Exception as e:
        logger.error(f"Error triggering revenue analytics: {str(e)}") 