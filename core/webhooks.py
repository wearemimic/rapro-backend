import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
from decimal import Decimal
import json
import hmac
import hashlib
from datetime import timedelta

from .services.analytics_service import RevenueAnalyticsService
from .affiliate_models import Affiliate, AffiliateConversion, Commission
from .affiliate_emails import send_affiliate_conversion_notification
from .models import KajabiWebhookEvent

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
    except stripe.SignatureVerificationError as e:
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
        
        # Check for affiliate tracking
        track_affiliate_conversion(user, subscription)
        
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


def track_affiliate_conversion(user, subscription):
    """Track affiliate conversion when a subscription is created"""
    try:
        # Check if user has affiliate tracking in their session or metadata
        # This would typically be stored when user signs up through affiliate link
        affiliate_code = None
        
        # Check user metadata for affiliate tracking
        if hasattr(user, 'metadata') and user.metadata:
            affiliate_code = user.metadata.get('affiliate_code')
        
        # If no affiliate code found, check for discount code attribution
        if not affiliate_code and subscription.discount:
            # Check if discount code is associated with an affiliate
            from .affiliate_models import AffiliateDiscountCode
            try:
                discount = AffiliateDiscountCode.objects.get(
                    stripe_coupon_id=subscription.discount.coupon.id,
                    is_active=True
                )
                affiliate_code = discount.affiliate.affiliate_code
            except AffiliateDiscountCode.DoesNotExist:
                pass
        
        if not affiliate_code:
            return  # No affiliate attribution found
        
        # Find the affiliate
        affiliate = Affiliate.objects.get(affiliate_code=affiliate_code, status='active')
        
        # Calculate subscription amount
        subscription_amount = Decimal(str(subscription.items.data[0].price.unit_amount / 100))
        is_annual = subscription.items.data[0].price.recurring.interval == 'year'
        
        # Create conversion record
        conversion = AffiliateConversion.objects.create(
            affiliate=affiliate,
            user=user,
            user_email=user.email,
            subscription_id=subscription.id,
            subscription_amount=subscription_amount,
            subscription_plan='annual' if is_annual else 'monthly',
            conversion_value=subscription_amount * 12 if is_annual else subscription_amount,
            conversion_date=timezone.now().date(),
            is_valid=True
        )
        
        # Calculate commission based on affiliate's commission structure
        commission_rate = affiliate.commission_rate_first_month
        
        if affiliate.commission_type == 'flat':
            commission_amount = affiliate.flat_rate_amount or Decimal('0')
        elif affiliate.commission_type == 'percentage':
            commission_amount = subscription_amount * (commission_rate / 100)
        else:
            # Handle tiered or custom commission
            commission_amount = subscription_amount * (commission_rate / 100)
        
        # Create commission record
        commission = Commission.objects.create(
            affiliate=affiliate,
            conversion=conversion,
            commission_type='first_month',
            description=f"Commission for {user.email} - {subscription.items.data[0].price.recurring.interval}ly plan",
            base_amount=subscription_amount,
            commission_rate=float(commission_rate / 100) if affiliate.commission_type != 'flat' else 0,
            commission_amount=commission_amount,
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            status='pending'
        )
        
        # Update affiliate statistics
        affiliate.total_conversions += 1
        affiliate.total_revenue_generated += conversion.conversion_value
        affiliate.total_commissions_earned += commission_amount
        affiliate.last_activity_at = timezone.now()
        affiliate.save()
        
        # Send conversion notification email to affiliate
        send_affiliate_conversion_notification.delay(str(affiliate.id), str(conversion.id))
        
        logger.info(f"Affiliate conversion tracked for {affiliate.affiliate_code}: {user.email}")
        
    except Affiliate.DoesNotExist:
        logger.warning(f"Affiliate not found for code: {affiliate_code}")
    except Exception as e:
        logger.error(f"Error tracking affiliate conversion: {str(e)}")


# =============================================================================
# KAJABI WEBHOOK HANDLERS FOR NSSA INTEGRATION
# =============================================================================

@csrf_exempt
@require_POST
def kajabi_webhook(request):
    """
    Handle incoming webhooks from Kajabi for NSSA partnership.
    Events: purchase.created, subscription.canceled, subscription.renewed, subscription.expired

    Authentication:
    - Bearer Token: Send "Authorization: Bearer <token>" header (for testing/simple integration)
    - HMAC Signature: Send "X-Kajabi-Signature" header (production Kajabi webhooks)
    """
    payload = request.body

    try:
        payload_data = json.loads(payload)
        event_type = payload_data.get('type')
        event_id = payload_data.get('id', '')

        logger.info(f"📩 Received Kajabi webhook: {event_type} (ID: {event_id})")

        # Verify authentication (bearer token OR HMAC signature)
        if not verify_kajabi_auth(request):
            logger.error("❌ Kajabi webhook authentication failed")
            return HttpResponse(status=401)

        # Check for duplicate event (idempotency)
        if KajabiWebhookEvent.objects.filter(event_id=event_id).exists():
            logger.info(f"⚠️ Duplicate Kajabi webhook event {event_id}, skipping")
            return JsonResponse({'status': 'duplicate', 'message': 'Event already processed'}, status=200)

        # Log the webhook event
        webhook_event = KajabiWebhookEvent.objects.create(
            event_id=event_id,
            event_type=event_type,
            payload=payload_data,
            processed=False
        )

        # Route to appropriate handler
        try:
            if event_type == 'offer.purchased':
                handle_kajabi_purchase(payload_data, webhook_event)
            elif event_type == 'member.subscription.canceled':
                handle_kajabi_subscription_canceled(payload_data, webhook_event)
            elif event_type == 'member.subscription.renewed':
                handle_kajabi_subscription_renewed(payload_data, webhook_event)
            elif event_type == 'member.subscription.expired':
                handle_kajabi_subscription_expired(payload_data, webhook_event)
            else:
                logger.info(f"ℹ️ Unhandled Kajabi event type: {event_type}")
                webhook_event.processed = True
                webhook_event.processed_at = timezone.now()
                webhook_event.save()

            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            logger.error(f"❌ Error processing Kajabi webhook: {str(e)}", exc_info=True)
            webhook_event.error_message = str(e)
            webhook_event.save()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in Kajabi webhook payload: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"❌ Unexpected error in Kajabi webhook: {str(e)}", exc_info=True)
        return HttpResponse(status=500)


def verify_bearer_token(request):
    """
    Verify bearer token authentication.
    Checks for "Authorization: Bearer <token>" header.
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')

    if not auth_header.startswith('Bearer '):
        return False

    token = auth_header[7:]  # Remove "Bearer " prefix

    # Check if bearer token is configured
    if not hasattr(settings, 'KAJABI_WEBHOOK_BEARER_TOKEN') or not settings.KAJABI_WEBHOOK_BEARER_TOKEN:
        return False

    # Compare tokens using constant-time comparison
    return hmac.compare_digest(token, settings.KAJABI_WEBHOOK_BEARER_TOKEN)


def verify_kajabi_signature(request):
    """
    Verify the Kajabi webhook HMAC signature.
    Kajabi typically sends a signature in the X-Kajabi-Signature header.
    """
    signature = request.META.get('HTTP_X_KAJABI_SIGNATURE')
    if not signature:
        return False

    # Check if HMAC secret is configured
    if not hasattr(settings, 'KAJABI_WEBHOOK_SECRET') or not settings.KAJABI_WEBHOOK_SECRET:
        return False

    secret = settings.KAJABI_WEBHOOK_SECRET
    payload = request.body

    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


def verify_kajabi_auth(request):
    """
    Verify Kajabi webhook authentication.
    Accepts either bearer token OR HMAC signature.
    """
    # Try bearer token first (simpler for testing)
    if verify_bearer_token(request):
        logger.info("✅ Kajabi webhook authenticated via bearer token")
        return True

    # Try HMAC signature (production Kajabi)
    if verify_kajabi_signature(request):
        logger.info("✅ Kajabi webhook authenticated via HMAC signature")
        return True

    # No valid authentication found
    logger.warning("⚠️ Kajabi webhook authentication failed - no valid bearer token or signature")
    return False


def handle_kajabi_purchase(payload, webhook_event):
    """
    Handle new purchase from Kajabi (NSSA membership).
    Creates new user account or links existing account to NSSA.
    """
    try:
        # Extract member and offer data from Kajabi payload
        member = payload.get('member', {})
        offer = payload.get('offer', {})

        email = member.get('email')
        first_name = member.get('first_name', '')
        last_name = member.get('last_name', '')
        kajabi_member_id = member.get('id')
        kajabi_offer_id = offer.get('id')
        kajabi_offer_name = offer.get('name', 'NSSA Annual Membership')

        if not email:
            raise ValueError("No email found in Kajabi webhook payload")

        logger.info(f"🔍 Processing Kajabi purchase for: {email}")

        # Check if user already exists
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            # Link existing account to NSSA
            logger.info(f"👤 Existing user found: {email}. Linking to NSSA...")

            # Update metadata to include NSSA partnership
            if not existing_user.metadata:
                existing_user.metadata = {}

            existing_user.metadata.update({
                'partner': 'NSSA',
                'partner_name': 'National Social Security Advisors',
                'source': 'kajabi',
                'kajabi_member_id': kajabi_member_id,
                'kajabi_offer_id': kajabi_offer_id,
                'kajabi_offer_name': kajabi_offer_name,
                'nssa_linked_at': timezone.now().isoformat(),
            })

            # Mark subscription as active if not already
            if existing_user.subscription_status != 'active':
                existing_user.subscription_status = 'active'
                existing_user.subscription_plan = 'nssa_annual'
                existing_user.subscription_end_date = timezone.now() + timedelta(days=365)

            existing_user.save()

            webhook_event.user = existing_user
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            # Send admin notification - existing user linked
            send_nssa_existing_user_notification(existing_user)

            logger.info(f"✅ Existing user {email} linked to NSSA successfully")

        else:
            # Create new user account
            logger.info(f"➕ Creating new NSSA user: {email}")

            new_user = User.objects.create(
                email=email,
                username=email,
                first_name=first_name,
                last_name=last_name,
                is_active=False,  # Inactive until password is set
                subscription_status='active',
                subscription_plan='nssa_annual',
                subscription_end_date=timezone.now() + timedelta(days=365),
                auth_provider='kajabi',
                metadata={
                    'partner': 'NSSA',
                    'partner_name': 'National Social Security Advisors',
                    'source': 'kajabi',
                    'kajabi_member_id': kajabi_member_id,
                    'kajabi_offer_id': kajabi_offer_id,
                    'kajabi_offer_name': kajabi_offer_name,
                    'signup_date': timezone.now().isoformat(),
                }
            )

            webhook_event.user = new_user
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            # Generate password setup token
            password_token = generate_password_setup_token(new_user)

            # Send welcome email with password setup link
            send_nssa_welcome_email(new_user, password_token)

            # Send admin notification - new signup
            send_nssa_new_signup_notification(new_user)

            logger.info(f"✅ New NSSA user created: {email}")

    except Exception as e:
        logger.error(f"❌ Error handling Kajabi purchase: {str(e)}", exc_info=True)
        webhook_event.error_message = str(e)
        webhook_event.save()
        raise


def handle_kajabi_subscription_canceled(payload, webhook_event):
    """
    Handle subscription cancellation from Kajabi.
    Keep access until end of billing period.
    """
    try:
        member = payload.get('member', {})
        email = member.get('email')

        if not email:
            raise ValueError("No email found in Kajabi webhook payload")

        logger.info(f"⚠️ Processing Kajabi cancellation for: {email}")

        user = User.objects.filter(email=email).first()
        if not user:
            logger.warning(f"User not found for Kajabi cancellation: {email}")
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.error_message = f"User not found: {email}"
            webhook_event.save()
            return

        # Mark as canceled but keep access until end date
        user.subscription_status = 'canceled'

        # Set end date to current end date or 30 days from now
        if not user.subscription_end_date or user.subscription_end_date < timezone.now():
            user.subscription_end_date = timezone.now() + timedelta(days=30)

        user.save()

        webhook_event.user = user
        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()
        webhook_event.save()

        logger.info(f"✅ Subscription canceled for {email}, access until {user.subscription_end_date}")

    except Exception as e:
        logger.error(f"❌ Error handling Kajabi cancellation: {str(e)}", exc_info=True)
        webhook_event.error_message = str(e)
        webhook_event.save()
        raise


def handle_kajabi_subscription_renewed(payload, webhook_event):
    """
    Handle subscription renewal from Kajabi.
    Reactivate subscription and extend end date.
    """
    try:
        member = payload.get('member', {})
        email = member.get('email')

        if not email:
            raise ValueError("No email found in Kajabi webhook payload")

        logger.info(f"🔄 Processing Kajabi renewal for: {email}")

        user = User.objects.filter(email=email).first()
        if not user:
            logger.warning(f"User not found for Kajabi renewal: {email}")
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.error_message = f"User not found: {email}"
            webhook_event.save()
            return

        # Reactivate subscription
        user.subscription_status = 'active'
        user.subscription_end_date = timezone.now() + timedelta(days=365)
        user.save()

        webhook_event.user = user
        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()
        webhook_event.save()

        logger.info(f"✅ Subscription renewed for {email} until {user.subscription_end_date}")

    except Exception as e:
        logger.error(f"❌ Error handling Kajabi renewal: {str(e)}", exc_info=True)
        webhook_event.error_message = str(e)
        webhook_event.save()
        raise


def handle_kajabi_subscription_expired(payload, webhook_event):
    """
    Handle subscription expiration from Kajabi.
    Mark subscription as expired and disable access.
    """
    try:
        member = payload.get('member', {})
        email = member.get('email')

        if not email:
            raise ValueError("No email found in Kajabi webhook payload")

        logger.info(f"❌ Processing Kajabi expiration for: {email}")

        user = User.objects.filter(email=email).first()
        if not user:
            logger.warning(f"User not found for Kajabi expiration: {email}")
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.error_message = f"User not found: {email}"
            webhook_event.save()
            return

        # Mark as expired
        user.subscription_status = 'expired'
        user.subscription_end_date = timezone.now()
        user.save()

        webhook_event.user = user
        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()
        webhook_event.save()

        logger.info(f"✅ Subscription expired for {email}")

    except Exception as e:
        logger.error(f"❌ Error handling Kajabi expiration: {str(e)}", exc_info=True)
        webhook_event.error_message = str(e)
        webhook_event.save()
        raise


def generate_password_setup_token(user):
    """
    Generate a secure token for password setup.
    Token expires in 24 hours.
    """
    import secrets
    token = secrets.token_urlsafe(32)

    # Store token in user metadata with expiration
    if not user.metadata:
        user.metadata = {}

    user.metadata['password_setup_token'] = token
    user.metadata['password_setup_token_expires'] = (timezone.now() + timedelta(hours=24)).isoformat()
    user.save()

    return token


def send_nssa_welcome_email(user, password_token):
    """Send welcome email to new NSSA member with password setup link"""
    try:
        frontend_url = settings.FRONTEND_URL
        # Token-only URL for better security (no PII in URL)
        password_setup_url = f"{frontend_url}/nssa/setup-password?token={password_token}"

        subject = "Welcome to Your NSSA Retirement Advisor Pro Account!"

        # Plain text version (fallback)
        text_message = f"""
Welcome to Retirement Advisor Pro, {user.first_name}!

Thank you for joining through the National Social Security Advisors (NSSA).

Your account has been created and you're almost ready to start planning your retirement strategy.

To activate your account, please click the link below to set your password:
{password_setup_url}

This link will expire in 24 hours.

Once you've set your password, you'll have full access to:
• Comprehensive retirement planning tools
• Social Security optimization strategies
• Client portal for secure client collaboration
• Professional report generation
• And much more!

If you have any questions, please contact our support team at support@retirementadvisorpro.com.

Best regards,
The Retirement Advisor Pro Team
"""

        # HTML version
        html_message = render_to_string('emails/nssa_welcome.html', {
            'first_name': user.first_name,
            'email': user.email,
            'setup_url': password_setup_url,
        })

        send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@retirementadvisorpro.com',
            [user.email],
            fail_silently=False,
            html_message=html_message,
        )

        logger.info(f"📧 Welcome email sent to {user.email}")

    except Exception as e:
        logger.error(f"❌ Error sending NSSA welcome email: {str(e)}", exc_info=True)


def send_nssa_new_signup_notification(user):
    """Send admin notification for new NSSA signup"""
    try:
        admin_email = settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else 'admin@retirementadvisorpro.com'

        subject = f"🎉 New NSSA Member Signup: {user.email}"

        message = f"""
New NSSA Member Signup!

Email: {user.email}
Name: {user.first_name} {user.last_name}
Partner: NSSA (National Social Security Advisors)
Subscription: NSSA Annual Membership ($299)
Signup Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
Kajabi Member ID: {user.metadata.get('kajabi_member_id', 'N/A')}

The user has been sent a welcome email with password setup instructions.

Account Status: Pending password setup
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@retirementadvisorpro.com',
            [admin_email],
            fail_silently=False,
        )

        logger.info(f"📧 Admin notification sent for new NSSA signup: {user.email}")

    except Exception as e:
        logger.error(f"❌ Error sending admin notification: {str(e)}", exc_info=True)


def send_nssa_existing_user_notification(user):
    """Send admin notification when existing user is linked to NSSA"""
    try:
        admin_email = settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else 'admin@retirementadvisorpro.com'

        subject = f"🔗 Existing User Linked to NSSA: {user.email}"

        message = f"""
Existing User Linked to NSSA!

Email: {user.email}
Name: {user.first_name} {user.last_name}
Partner: NSSA (National Social Security Advisors)
Original Signup Date: {user.date_joined.strftime('%Y-%m-%d')}
NSSA Link Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
Kajabi Member ID: {user.metadata.get('kajabi_member_id', 'N/A')}

This user already had an account and has now purchased through NSSA.
Their account has been linked to the NSSA partnership.

Current Subscription Status: {user.subscription_status}
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@retirementadvisorpro.com',
            [admin_email],
            fail_silently=False,
        )

        logger.info(f"📧 Admin notification sent for existing user linked to NSSA: {user.email}")

    except Exception as e:
        logger.error(f"❌ Error sending admin notification: {str(e)}", exc_info=True) 