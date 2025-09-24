"""
Email notification system for affiliate program
Handles welcome emails, conversion notifications, payout confirmations, etc.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class AffiliateEmailService:
    """Service class for sending affiliate-related emails"""
    
    @staticmethod
    def send_welcome_email(affiliate):
        """
        Send welcome email to new affiliate
        """
        subject = "Welcome to RetirementAdvisorPro Affiliate Program!"
        
        context = {
            'affiliate_name': affiliate.contact_name,
            'business_name': affiliate.business_name,
            'affiliate_code': affiliate.affiliate_code,
            'portal_url': f"{settings.FRONTEND_URL}/affiliate/portal/login",
            'dashboard_url': f"{settings.FRONTEND_URL}/affiliate/portal/dashboard",
            'support_email': 'affiliates@retirementadvisorpro.com'
        }
        
        # Plain text content
        text_content = f"""
        Welcome to the RetirementAdvisorPro Affiliate Program!
        
        Hi {affiliate.contact_name},
        
        Thank you for joining our affiliate program! We're excited to have {affiliate.business_name} as our partner.
        
        Your affiliate details:
        - Affiliate Code: {affiliate.affiliate_code}
        - Commission Rate (First Month): {affiliate.commission_rate_first_month}%
        - Commission Rate (Recurring): {affiliate.commission_rate_recurring}%
        
        Getting Started:
        1. Access your dashboard: {context['portal_url']}
        2. Create tracking links for your campaigns
        3. Share your unique affiliate links
        4. Track your performance in real-time
        
        Your first login:
        - Email: {affiliate.email}
        - Code: {affiliate.affiliate_code}
        
        After your first login, you'll be prompted to set up a password.
        
        Need help? Contact us at {context['support_email']}
        
        Best regards,
        The RetirementAdvisorPro Team
        """
        
        # HTML content (you can create a template for this)
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Welcome to the RetirementAdvisorPro Affiliate Program!</h2>
                
                <p>Hi {affiliate.contact_name},</p>
                
                <p>Thank you for joining our affiliate program! We're excited to have <strong>{affiliate.business_name}</strong> as our partner.</p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Your Affiliate Details:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li>📊 <strong>Affiliate Code:</strong> <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px;">{affiliate.affiliate_code}</code></li>
                        <li>💰 <strong>First Month Commission:</strong> {affiliate.commission_rate_first_month}%</li>
                        <li>🔄 <strong>Recurring Commission:</strong> {affiliate.commission_rate_recurring}%</li>
                    </ul>
                </div>
                
                <h3>Getting Started:</h3>
                <ol>
                    <li>Access your dashboard at <a href="{context['portal_url']}">{context['portal_url']}</a></li>
                    <li>Create tracking links for your campaigns</li>
                    <li>Share your unique affiliate links</li>
                    <li>Track your performance in real-time</li>
                </ol>
                
                <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin-top: 0;">First Login Credentials:</h4>
                    <p><strong>Email:</strong> {affiliate.email}<br>
                    <strong>Code:</strong> <code style="background: #c3e6cb; padding: 2px 6px; border-radius: 3px;">{affiliate.affiliate_code}</code></p>
                    <p style="margin-bottom: 0;"><em>You'll be prompted to set up a password after your first login.</em></p>
                </div>
                
                <p>Need help? Contact us at <a href="mailto:{context['support_email']}">{context['support_email']}</a></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                
                <p style="color: #6c757d; font-size: 14px;">
                    Best regards,<br>
                    The RetirementAdvisorPro Team
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[affiliate.email],
                html_message=html_content,
                fail_silently=False
            )
            logger.info(f"Welcome email sent to affiliate {affiliate.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send welcome email to {affiliate.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_approval_email(affiliate):
        """
        Send email when affiliate is approved
        """
        subject = "Your Affiliate Application Has Been Approved!"
        
        text_content = f"""
        Great news, {affiliate.contact_name}!
        
        Your affiliate application for {affiliate.business_name} has been approved.
        
        You can now:
        - Access your affiliate dashboard
        - Create tracking links
        - Start earning commissions
        
        Login at: {settings.FRONTEND_URL}/affiliate/portal/login
        
        Best regards,
        The RetirementAdvisorPro Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[affiliate.email],
                fail_silently=False
            )
            logger.info(f"Approval email sent to affiliate {affiliate.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send approval email to {affiliate.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_conversion_notification(affiliate, conversion):
        """
        Send email notification for new conversion
        """
        commission_amount = (conversion.subscription_amount * affiliate.commission_rate_first_month) / 100
        
        subject = "🎉 New Conversion! You've Earned a Commission"
        
        text_content = f"""
        Congratulations {affiliate.contact_name}!
        
        You've just earned a new commission:
        
        Conversion Details:
        - Customer: {conversion.user_email}
        - Plan: {conversion.subscription_plan}
        - Subscription Amount: ${conversion.subscription_amount}
        - Your Commission: ${commission_amount:.2f}
        - Date: {conversion.conversion_date.strftime('%B %d, %Y')}
        
        This commission will be included in your next payout.
        
        View your dashboard: {settings.FRONTEND_URL}/affiliate/portal/dashboard
        
        Keep up the great work!
        
        Best regards,
        The RetirementAdvisorPro Team
        """
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #28a745;">🎉 New Conversion! You've Earned a Commission</h2>
                
                <p>Congratulations {affiliate.contact_name}!</p>
                
                <p>You've just earned a new commission:</p>
                
                <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #155724;">Conversion Details:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0;"><strong>Customer:</strong></td>
                            <td>{conversion.user_email}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Plan:</strong></td>
                            <td>{conversion.subscription_plan.title()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Subscription:</strong></td>
                            <td>${conversion.subscription_amount}</td>
                        </tr>
                        <tr style="border-top: 2px solid #28a745;">
                            <td style="padding: 8px 0;"><strong>Your Commission:</strong></td>
                            <td style="font-size: 18px; color: #28a745;"><strong>${commission_amount:.2f}</strong></td>
                        </tr>
                    </table>
                </div>
                
                <p>This commission will be included in your next payout.</p>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/affiliate/portal/dashboard" 
                       style="background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Your Dashboard
                    </a>
                </p>
                
                <p>Keep up the great work!</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                
                <p style="color: #6c757d; font-size: 14px;">
                    Best regards,<br>
                    The RetirementAdvisorPro Team
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[affiliate.email],
                html_message=html_content,
                fail_silently=False
            )
            logger.info(f"Conversion notification sent to affiliate {affiliate.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send conversion notification to {affiliate.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_payout_confirmation(affiliate, payout):
        """
        Send email confirmation when payout is processed
        """
        subject = f"💰 Payout Processed: ${payout.net_payout}"
        
        text_content = f"""
        Hi {affiliate.contact_name},
        
        Your commission payout has been processed!
        
        Payout Details:
        - Amount: ${payout.net_payout}
        - Period: {payout.payout_period_start} to {payout.payout_period_end}
        - Payment Method: {payout.payment_method}
        - Transaction ID: {payout.stripe_transfer_id or payout.payment_reference}
        - Date: {payout.processed_at.strftime('%B %d, %Y')}
        
        The funds should appear in your account within 2-3 business days.
        
        View your payout history: {settings.FRONTEND_URL}/affiliate/portal/dashboard
        
        Thank you for being a valued partner!
        
        Best regards,
        The RetirementAdvisorPro Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[affiliate.email],
                fail_silently=False
            )
            logger.info(f"Payout confirmation sent to affiliate {affiliate.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send payout confirmation to {affiliate.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_monthly_statement(affiliate, month, year, stats):
        """
        Send monthly performance statement
        """
        subject = f"Your {month} {year} Affiliate Statement"
        
        text_content = f"""
        Hi {affiliate.contact_name},
        
        Here's your affiliate performance summary for {month} {year}:
        
        Performance Metrics:
        - Total Clicks: {stats['clicks']}
        - Conversions: {stats['conversions']}
        - Conversion Rate: {stats['conversion_rate']:.2f}%
        - Total Earnings: ${stats['earnings']}
        - Pending Commissions: ${stats['pending']}
        - Paid Out: ${stats['paid']}
        
        Top Performing Links:
        {chr(10).join([f"- {link['name']}: {link['clicks']} clicks, {link['conversions']} conversions" for link in stats['top_links'][:5]])}
        
        View full report: {settings.FRONTEND_URL}/affiliate/portal/dashboard
        
        Keep up the great work!
        
        Best regards,
        The RetirementAdvisorPro Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[affiliate.email],
                fail_silently=False
            )
            logger.info(f"Monthly statement sent to affiliate {affiliate.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send monthly statement to {affiliate.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_stripe_connect_reminder(affiliate):
        """
        Send reminder to complete Stripe Connect setup
        """
        subject = "Action Required: Complete Your Payment Setup"
        
        text_content = f"""
        Hi {affiliate.contact_name},
        
        We noticed you haven't completed your payment setup yet.
        
        To receive commission payouts, you need to connect your Stripe account.
        This only takes a few minutes:
        
        1. Login to your affiliate dashboard
        2. Click on "Payment Setup"
        3. Follow the Stripe onboarding process
        
        Complete your setup: {settings.FRONTEND_URL}/affiliates/{affiliate.id}/stripe-connect
        
        Once completed, you'll be able to receive automatic monthly payouts.
        
        Need help? Contact us at affiliates@retirementadvisorpro.com
        
        Best regards,
        The RetirementAdvisorPro Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[affiliate.email],
                fail_silently=False
            )
            logger.info(f"Stripe Connect reminder sent to affiliate {affiliate.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Stripe Connect reminder to {affiliate.email}: {str(e)}")
            return False


# Celery tasks for async email sending
from celery import shared_task

@shared_task
def send_affiliate_welcome_email(affiliate_id):
    """Celery task to send welcome email"""
    from .affiliate_models import Affiliate
    try:
        affiliate = Affiliate.objects.get(id=affiliate_id)
        AffiliateEmailService.send_welcome_email(affiliate)
    except Affiliate.DoesNotExist:
        logger.error(f"Affiliate {affiliate_id} not found for welcome email")

@shared_task
def send_affiliate_conversion_notification(affiliate_id, conversion_id):
    """Celery task to send conversion notification"""
    from .affiliate_models import Affiliate, AffiliateConversion
    try:
        affiliate = Affiliate.objects.get(id=affiliate_id)
        conversion = AffiliateConversion.objects.get(id=conversion_id)
        AffiliateEmailService.send_conversion_notification(affiliate, conversion)
    except (Affiliate.DoesNotExist, AffiliateConversion.DoesNotExist) as e:
        logger.error(f"Failed to send conversion notification: {str(e)}")

@shared_task
def send_affiliate_payout_confirmation(affiliate_id, payout_id):
    """Celery task to send payout confirmation"""
    from .affiliate_models import Affiliate, AffiliatePayout
    try:
        affiliate = Affiliate.objects.get(id=affiliate_id)
        payout = AffiliatePayout.objects.get(id=payout_id)
        AffiliateEmailService.send_payout_confirmation(affiliate, payout)
    except (Affiliate.DoesNotExist, AffiliatePayout.DoesNotExist) as e:
        logger.error(f"Failed to send payout confirmation: {str(e)}")

@shared_task
def send_monthly_affiliate_statements():
    """Celery task to send monthly statements to all active affiliates"""
    from .affiliate_models import Affiliate, AffiliateClick, AffiliateConversion, Commission
    from datetime import date, timedelta
    from dateutil.relativedelta import relativedelta
    
    # Calculate last month
    today = date.today()
    last_month = today - relativedelta(months=1)
    start_date = date(last_month.year, last_month.month, 1)
    end_date = date(today.year, today.month, 1) - timedelta(days=1)
    
    month_name = last_month.strftime('%B')
    year = last_month.year
    
    active_affiliates = Affiliate.objects.filter(status='active')
    
    for affiliate in active_affiliates:
        # Calculate stats for the month
        clicks = AffiliateClick.objects.filter(
            affiliate=affiliate,
            clicked_at__date__gte=start_date,
            clicked_at__date__lte=end_date
        ).count()
        
        conversions = AffiliateConversion.objects.filter(
            affiliate=affiliate,
            conversion_date__date__gte=start_date,
            conversion_date__date__lte=end_date
        ).count()
        
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
        
        earnings = Commission.objects.filter(
            affiliate=affiliate,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).aggregate(total=models.Sum('commission_amount'))['total'] or Decimal('0.00')
        
        pending = Commission.objects.filter(
            affiliate=affiliate,
            status='pending'
        ).aggregate(total=models.Sum('commission_amount'))['total'] or Decimal('0.00')
        
        paid = Commission.objects.filter(
            affiliate=affiliate,
            status='paid',
            paid_at__date__gte=start_date,
            paid_at__date__lte=end_date
        ).aggregate(total=models.Sum('commission_amount'))['total'] or Decimal('0.00')
        
        # Get top performing links
        from django.db.models import Count
        top_links = AffiliateLink.objects.filter(
            affiliate=affiliate
        ).annotate(
            click_count=Count('click_events'),
            conversion_count=Count('click_events__conversion')
        ).order_by('-click_count')[:5]
        
        stats = {
            'clicks': clicks,
            'conversions': conversions,
            'conversion_rate': conversion_rate,
            'earnings': earnings,
            'pending': pending,
            'paid': paid,
            'top_links': [
                {
                    'name': link.campaign_name,
                    'clicks': link.click_count,
                    'conversions': link.conversion_count
                }
                for link in top_links
            ]
        }
        
        AffiliateEmailService.send_monthly_statement(affiliate, month_name, year, stats)
        logger.info(f"Monthly statement sent to {affiliate.email}")


# Import for aggregate functions
from django.db import models