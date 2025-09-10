"""
Simple End-to-End Test for Affiliate System
Tests core functionality with direct model operations
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.affiliate_models import (
    Affiliate, AffiliateLink, AffiliateClick,
    AffiliateConversion, Commission, AffiliatePayout
)

User = get_user_model()


class AffiliateSystemSimpleTest(TestCase):
    """
    Simple tests for affiliate system core functionality
    """
    
    def test_affiliate_workflow(self):
        """Test the complete affiliate workflow with models"""
        
        print("\n" + "="*60)
        print("AFFILIATE SYSTEM END-TO-END TEST")
        print("="*60)
        
        # 1. Create users
        print("\n1. Creating users...")
        admin_user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123',
            username='admin_test'
        )
        affiliate_user = User.objects.create_user(
            email='affiliate@test.com',
            password='testpass123',
            username='affiliate_test'
        )
        customer_user = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            username='customer_test'
        )
        print(f"✓ Created {User.objects.count()} users")
        
        # 2. Create affiliate account
        print("\n2. Creating affiliate account...")
        affiliate = Affiliate.objects.create(
            user=affiliate_user,
            business_name='Test Marketing Agency',
            contact_name='John Doe',
            email='affiliate@testmarketing.com',
            website_url='https://testmarketing.com',
            commission_type='percentage',
            commission_rate_first_month=30.0,
            commission_rate_recurring=10.0,
            payment_method='stripe_connect',
            status='active',
            approved_at=timezone.now(),
            approved_by=admin_user
        )
        print(f"✓ Affiliate created: {affiliate.business_name}")
        print(f"  - Code: {affiliate.affiliate_code}")
        print(f"  - Commission: {affiliate.commission_rate_first_month}% first month, {affiliate.commission_rate_recurring}% recurring")
        
        # 3. Create tracking link
        print("\n3. Creating tracking link...")
        link = AffiliateLink.objects.create(
            affiliate=affiliate,
            campaign_name='Q1 Email Campaign',
            destination_url='/signup',
            utm_source='newsletter',
            utm_medium='email',
            utm_campaign='q1_2025'
        )
        print(f"✓ Link created: {link.campaign_name}")
        print(f"  - Tracking code: {link.tracking_code}")
        print(f"  - Full URL: {link.get_full_url()}")
        
        # 4. Simulate click
        print("\n4. Simulating click tracking...")
        click = AffiliateClick.objects.create(
            affiliate=affiliate,
            link=link,
            session_id='test_session_123',
            tracking_code=link.tracking_code,
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            referrer='https://testmarketing.com/blog'
        )
        
        # Update link click counts
        link.total_clicks += 1
        link.unique_clicks += 1
        link.save()
        
        # Update affiliate click count
        affiliate.total_clicks += 1
        affiliate.save()
        
        print(f"✓ Click tracked from IP: {click.ip_address}")
        print(f"  - Link clicks: {link.total_clicks}")
        print(f"  - Affiliate total clicks: {affiliate.total_clicks}")
        
        # 5. Simulate conversion
        print("\n5. Simulating conversion...")
        subscription_amount = Decimal('99.00')
        
        conversion = AffiliateConversion.objects.create(
            affiliate=affiliate,
            user=customer_user,
            user_email=customer_user.email,
            stripe_subscription_id='sub_test_12345',
            stripe_customer_id='cus_test_12345',
            subscription_amount=subscription_amount,
            subscription_plan='monthly',
            mrr_value=subscription_amount,
            click=click
        )
        
        # Update link conversion count
        link.conversions += 1
        link.save()
        
        # Update affiliate metrics
        affiliate.total_conversions += 1
        affiliate.total_revenue_generated += subscription_amount
        affiliate.save()
        
        print(f"✓ Conversion tracked for: {conversion.user_email}")
        print(f"  - Subscription: ${subscription_amount}/month")
        print(f"  - Affiliate conversions: {affiliate.total_conversions}")
        print(f"  - Total revenue generated: ${affiliate.total_revenue_generated}")
        
        # 6. Calculate commission
        print("\n6. Calculating commission...")
        commission_rate = Decimal(str(affiliate.commission_rate_first_month / 100))
        commission_amount = subscription_amount * commission_rate
        
        commission = Commission.objects.create(
            affiliate=affiliate,
            conversion=conversion,
            commission_type='first_month',
            description=f"First month commission for {customer_user.email}",
            base_amount=subscription_amount,
            commission_rate=float(commission_rate),
            commission_amount=commission_amount,
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            status='approved'
        )
        
        # Update affiliate commission totals
        affiliate.total_commissions_earned += commission_amount
        affiliate.pending_commission_balance += commission_amount
        affiliate.save()
        
        print(f"✓ Commission calculated: ${commission_amount}")
        print(f"  - Rate: {affiliate.commission_rate_first_month}%")
        print(f"  - Status: {commission.status}")
        print(f"  - Pending balance: ${affiliate.pending_commission_balance}")
        
        # 7. Process payout
        print("\n7. Processing payout...")
        payout = AffiliatePayout.objects.create(
            affiliate=affiliate,
            payout_period_start=timezone.now().date(),
            payout_period_end=timezone.now().date(),
            total_commissions=commission_amount,
            net_payout=commission_amount,
            payment_method='stripe_connect',
            stripe_transfer_id='tr_test_12345',
            payment_reference='tr_test_12345',
            status='completed',
            processed_at=timezone.now(),
            tax_year=timezone.now().year
        )
        
        # Update commission with payout reference
        commission.payout = payout
        commission.status = 'paid'
        commission.paid_at = timezone.now()
        commission.save()
        
        # Update affiliate balances
        affiliate.total_commissions_paid += commission_amount
        affiliate.pending_commission_balance -= commission_amount
        affiliate.save()
        
        print(f"✓ Payout processed: ${payout.net_payout}")
        print(f"  - Transfer ID: {payout.stripe_transfer_id}")
        print(f"  - Status: {payout.status}")
        print(f"  - Total paid to date: ${affiliate.total_commissions_paid}")
        print(f"  - Remaining balance: ${affiliate.pending_commission_balance}")
        
        # 8. Verify system state
        print("\n8. Verifying system state...")
        
        # Verify affiliate metrics
        self.assertEqual(affiliate.total_clicks, 1)
        self.assertEqual(affiliate.total_conversions, 1)
        self.assertEqual(affiliate.total_revenue_generated, Decimal('99.00'))
        self.assertEqual(affiliate.total_commissions_earned, Decimal('29.70'))
        self.assertEqual(affiliate.total_commissions_paid, Decimal('29.70'))
        self.assertEqual(affiliate.pending_commission_balance, Decimal('0.00'))
        print("✓ Affiliate metrics verified")
        
        # Verify link metrics
        self.assertEqual(link.total_clicks, 1)
        self.assertEqual(link.conversions, 1)
        print("✓ Link metrics verified")
        
        # Verify commission status
        commission.refresh_from_db()
        self.assertEqual(commission.status, 'paid')
        self.assertIsNotNone(commission.payout)
        self.assertIsNotNone(commission.paid_at)
        print("✓ Commission status verified")
        
        # Verify payout
        self.assertEqual(payout.status, 'completed')
        self.assertEqual(payout.net_payout, Decimal('29.70'))
        print("✓ Payout verified")
        
        print("\n" + "="*60)
        print("✅ AFFILIATE SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nSUMMARY:")
        print(f"  • Affiliate: {affiliate.business_name} ({affiliate.affiliate_code})")
        print(f"  • Tracking Link: {link.campaign_name}")
        print(f"  • Clicks: {affiliate.total_clicks}")
        print(f"  • Conversions: {affiliate.total_conversions}")
        print(f"  • Revenue Generated: ${affiliate.total_revenue_generated}")
        print(f"  • Commissions Earned: ${affiliate.total_commissions_earned}")
        print(f"  • Commissions Paid: ${affiliate.total_commissions_paid}")
        print(f"  • Pending Balance: ${affiliate.pending_commission_balance}")
        print("="*60)
        
        return True


if __name__ == '__main__':
    import django
    from django.test.runner import DiscoverRunner
    
    # Run the test
    runner = DiscoverRunner(verbosity=2)
    runner.run_tests(['core.tests.test_affiliate_simple'])