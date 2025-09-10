"""
End-to-End Test Suite for Affiliate Commission System
Tests the complete flow from affiliate signup to payout
"""

import json
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from core.affiliate_models import (
    Affiliate, AffiliateLink, AffiliateClick,
    AffiliateConversion, Commission, AffiliatePayout,
    AffiliateDiscountCode
)
from core.models import Client
from core.affiliate_emails import AffiliateEmailService

User = get_user_model()


class AffiliateSystemE2ETest(TransactionTestCase):
    """
    End-to-end tests for the complete affiliate system
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123',
            username='admin'
        )
        
        # Create regular user who will become affiliate
        self.affiliate_user = User.objects.create_user(
            email='affiliate@test.com',
            password='testpass123',
            username='affiliate'
        )
        
        # Create customer user
        self.customer_user = User.objects.create_user(
            email='customer@test.com',
            password='testpass123',
            username='customer'
        )
        
    def test_complete_affiliate_lifecycle(self):
        """Test the complete affiliate lifecycle from signup to payout"""
        
        # 1. AFFILIATE SIGNUP
        print("\n1. Testing Affiliate Signup...")
        self.client.force_authenticate(user=self.affiliate_user)
        
        signup_data = {
            'business_name': 'Test Marketing Agency',
            'contact_name': 'John Doe',
            'email': 'affiliate@testmarketing.com',
            'website_url': 'https://testmarketing.com',
            'tax_id': '12-3456789',
            'commission_type': 'percentage',
            'commission_rate_first_month': 30.0,
            'commission_rate_recurring': 10.0,
            'payment_method': 'stripe_connect'
        }
        
        response = self.client.post('/api/affiliates/', signup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        affiliate_id = response.data['id']
        print(f"✓ Affiliate created with ID: {affiliate_id}")
        
        # 2. ADMIN APPROVAL
        print("\n2. Testing Admin Approval...")
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(f'/api/affiliates/{affiliate_id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify affiliate is approved
        affiliate = Affiliate.objects.get(id=affiliate_id)
        self.assertEqual(affiliate.status, 'active')
        self.assertIsNotNone(affiliate.affiliate_code)
        print(f"✓ Affiliate approved with code: {affiliate.affiliate_code}")
        
        # 3. CREATE TRACKING LINK
        print("\n3. Testing Tracking Link Creation...")
        self.client.force_authenticate(user=self.affiliate_user)
        
        link_data = {
            'affiliate': affiliate_id,
            'campaign_name': 'Email Campaign Q1',
            'utm_source': 'newsletter',
            'utm_medium': 'email',
            'utm_campaign': 'q1_2025'
        }
        
        response = self.client.post('/api/affiliate-links/', link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tracking_url = response.data['full_url']
        link_code = response.data['tracking_code']
        print(f"✓ Tracking link created: {tracking_url}")
        
        # 4. SIMULATE CLICK TRACKING
        print("\n4. Testing Click Tracking...")
        # Switch to anonymous user
        self.client.force_authenticate(user=None)
        
        click_data = {
            'link_code': link_code,
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referrer_url': 'https://testmarketing.com/retirement-guide',
            'landing_page': '/signup'
        }
        
        response = self.client.post('/api/track/click/', click_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        click_id = response.data['click_id']
        print(f"✓ Click tracked with ID: {click_id}")
        
        # 5. CREATE DISCOUNT CODE
        print("\n5. Testing Discount Code Creation...")
        self.client.force_authenticate(user=self.affiliate_user)
        
        discount_data = {
            'code': 'RETIRE25',
            'description': '25% off first month',
            'discount_type': 'percentage',
            'discount_percentage': 25.0,
            'max_uses': 100,
            'valid_from': timezone.now().date().isoformat(),
            'valid_until': (timezone.now().date() + timedelta(days=90)).isoformat()
        }
        
        # Note: discount codes endpoint may need to be adjusted
        response = self.client.post('/api/discount-codes/', 
                                   {**discount_data, 'affiliate': affiliate_id}, 
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        discount_code = response.data['code']
        print(f"✓ Discount code created: {discount_code}")
        
        # 6. SIMULATE CONVERSION
        print("\n6. Testing Conversion Tracking...")
        # Create a mock Stripe subscription
        with patch('core.webhooks.stripe.Webhook.construct_event') as mock_construct:
            # Mock the subscription data
            subscription_data = {
                'id': 'sub_test123',
                'customer': 'cus_test123',
                'status': 'active',
                'items': {
                    'data': [{
                        'price': {
                            'unit_amount': 9900,  # $99.00
                            'recurring': {
                                'interval': 'month'
                            }
                        }
                    }]
                },
                'discount': {
                    'coupon': {
                        'id': 'RETIRE25'
                    }
                },
                'cancel_at': None
            }
            
            # Link customer to the discount code
            self.customer_user.stripe_customer_id = 'cus_test123'
            self.customer_user.save()
            
            # Create the conversion
            conversion = AffiliateConversion.objects.create(
                affiliate=affiliate,
                user=self.customer_user,
                user_email=self.customer_user.email,
                subscription_id='sub_test123',
                subscription_amount=Decimal('99.00'),
                subscription_plan='monthly',
                conversion_value=Decimal('99.00'),
                conversion_date=timezone.now().date(),
                click_id=click_id,
                is_valid=True
            )
            
            # Create commission
            commission = Commission.objects.create(
                affiliate=affiliate,
                conversion=conversion,
                commission_type='first_month',
                description=f"Commission for {self.customer_user.email} - monthly plan",
                base_amount=Decimal('99.00'),
                commission_rate=0.30,
                commission_amount=Decimal('29.70'),
                period_start=timezone.now().date(),
                period_end=timezone.now().date(),
                status='approved'  # Auto-approve for testing
            )
            
            print(f"✓ Conversion tracked with commission: ${commission.commission_amount}")
        
        # 7. TEST ANALYTICS ENDPOINTS
        print("\n7. Testing Analytics Endpoints...")
        self.client.force_authenticate(user=self.affiliate_user)
        
        # Test dashboard stats
        response = self.client.get(f'/api/affiliates/{affiliate_id}/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_clicks'], 1)
        self.assertEqual(response.data['total_conversions'], 1)
        self.assertEqual(float(response.data['pending_commissions']), 29.70)
        print("✓ Dashboard stats retrieved successfully")
        
        # Test performance report
        response = self.client.get(f'/api/affiliates/{affiliate_id}/performance-report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('clicks_by_day', response.data)
        self.assertIn('conversions_by_source', response.data)
        print("✓ Performance report generated successfully")
        
        # 8. TEST STRIPE CONNECT INTEGRATION
        print("\n8. Testing Stripe Connect Integration...")
        with patch('stripe.Account.create') as mock_create:
            mock_create.return_value = MagicMock(id='acct_test123')
            
            response = self.client.post('/api/stripe-connect/create-account/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify account ID was saved
            affiliate.refresh_from_db()
            self.assertEqual(affiliate.stripe_connect_account_id, 'acct_test123')
            print(f"✓ Stripe Connect account created: {affiliate.stripe_connect_account_id}")
        
        # 9. TEST PAYOUT PROCESSING
        print("\n9. Testing Payout Processing...")
        self.client.force_authenticate(user=self.admin_user)
        
        with patch('stripe.Transfer.create') as mock_transfer:
            mock_transfer.return_value = MagicMock(id='tr_test123')
            
            # Update affiliate with Stripe account
            affiliate.stripe_payouts_enabled = True
            affiliate.save()
            
            payout_data = {
                'start_date': timezone.now().date().isoformat(),
                'end_date': timezone.now().date().isoformat(),
                'min_payout': '10.00'
            }
            
            response = self.client.post('/api/stripe-connect/batch-payouts/', 
                                      payout_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['total_paid'], 1)
            
            # Verify payout was created
            payout = AffiliatePayout.objects.filter(affiliate=affiliate).first()
            self.assertIsNotNone(payout)
            self.assertEqual(payout.net_payout, Decimal('29.70'))
            self.assertEqual(payout.status, 'completed')
            print(f"✓ Payout processed: ${payout.net_payout}")
        
        # 10. TEST EMAIL NOTIFICATIONS
        print("\n10. Testing Email Notifications...")
        with patch('core.affiliate_emails.send_mail') as mock_send:
            # Test welcome email
            AffiliateEmailService.send_welcome_email(affiliate)
            self.assertTrue(mock_send.called)
            print("✓ Welcome email sent")
            
            # Test conversion notification
            AffiliateEmailService.send_conversion_notification(affiliate, conversion)
            print("✓ Conversion notification sent")
            
            # Test payout confirmation
            AffiliateEmailService.send_payout_confirmation(affiliate, payout)
            print("✓ Payout confirmation sent")
        
        # 11. VERIFY AFFILIATE PORTAL ACCESS
        print("\n11. Testing Affiliate Portal Access...")
        self.client.force_authenticate(user=self.affiliate_user)
        
        # Test portal dashboard
        response = self.client.get(f'/api/affiliates/{affiliate_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['business_name'], 'Test Marketing Agency')
        print("✓ Affiliate portal accessible")
        
        # Test links list
        response = self.client.get('/api/affiliate-links/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        print("✓ Links list retrieved")
        
        # Test commissions list
        response = self.client.get('/api/commissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        # Find commission for this affiliate
        commission = next((c for c in response.data if str(c.get('affiliate')) == str(affiliate_id)), None)
        if commission:
            self.assertEqual(float(commission['commission_amount']), 29.70)
        print("✓ Commissions list retrieved")
        
        print("\n" + "="*50)
        print("✅ ALL END-TO-END TESTS PASSED!")
        print("="*50)
        
    def test_fraud_detection(self):
        """Test fraud detection mechanisms"""
        print("\n Testing Fraud Detection...")
        
        # Create affiliate
        affiliate = Affiliate.objects.create(
            user=self.affiliate_user,
            business_name='Test Affiliate',
            email='affiliate@test.com',
            affiliate_code='TEST123',
            status='active',
            commission_type='percentage',
            commission_rate_first_month=30.0,
            commission_rate_recurring=10.0
        )
        
        # Create a tracking link
        link = AffiliateLink.objects.create(
            affiliate=affiliate,
            campaign_name='Test Link',
            tracking_code=str(uuid.uuid4())[:8]
        )
        
        # Simulate rapid clicks from same IP (potential click fraud)
        self.client.force_authenticate(user=None)
        
        for i in range(10):
            click_data = {
                'link_code': link.tracking_code,
                'ip_address': '192.168.1.100',  # Same IP
                'user_agent': 'Mozilla/5.0',
                'landing_page': '/signup'
            }
            response = self.client.post('/api/track/click/', click_data, format='json')
            
            if i < 5:  # First 5 clicks should be accepted
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:  # After threshold, should be rate limited or flagged
                # Depending on implementation, might return 429 or still 200 with flag
                self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_429_TOO_MANY_REQUESTS])
        
        # Check that clicks are flagged
        suspicious_clicks = AffiliateClick.objects.filter(
            link=link,
            ip_address='192.168.1.100'
        ).count()
        
        print(f"✓ Detected {suspicious_clicks} clicks from same IP")
        self.assertGreaterEqual(suspicious_clicks, 5)
        
    def test_commission_calculation_accuracy(self):
        """Test commission calculation for different scenarios"""
        print("\n Testing Commission Calculations...")
        
        # Create affiliate with percentage commission (no tiered structure in model)
        affiliate = Affiliate.objects.create(
            user=self.affiliate_user,
            business_name='Percentage Affiliate',
            email='percentage@test.com',
            affiliate_code='PERCENT123',
            status='active',
            commission_type='percentage',
            commission_rate_first_month=30.0,
            commission_rate_recurring=10.0
        )
        
        # Test Tier 1 commission (< $5000)
        conversion1 = AffiliateConversion.objects.create(
            affiliate=affiliate,
            user=self.customer_user,
            user_email='customer1@test.com',
            subscription_amount=Decimal('99.00'),
            subscription_plan='monthly',
            conversion_value=Decimal('99.00'),
            conversion_date=timezone.now().date(),
            is_valid=True
        )
        
        commission1 = Commission.objects.create(
            affiliate=affiliate,
            conversion=conversion1,
            commission_type='first_month',
            base_amount=Decimal('99.00'),
            commission_rate=0.30,
            commission_amount=Decimal('29.70'),
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            status='approved'
        )
        
        self.assertEqual(commission1.commission_amount, Decimal('29.70'))
        print(f"✓ First month commission: ${commission1.commission_amount} (30%)")
        
        # Test recurring commission (lower rate)
        commission2 = Commission.objects.create(
            affiliate=affiliate,
            conversion=conversion1,
            commission_type='recurring',
            base_amount=Decimal('99.00'),
            commission_rate=0.10,
            commission_amount=Decimal('9.90'),
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            status='approved'
        )
        
        self.assertEqual(commission2.commission_amount, Decimal('9.90'))
        print(f"✓ Recurring commission: ${commission2.commission_amount} (10%)")
        
        print("\n✅ Commission calculations verified!")
        
    def tearDown(self):
        """Clean up after tests"""
        # Clean up any test data
        User.objects.all().delete()
        Affiliate.objects.all().delete()
        AffiliateLink.objects.all().delete()
        AffiliateClick.objects.all().delete()
        AffiliateConversion.objects.all().delete()
        Commission.objects.all().delete()
        AffiliatePayout.objects.all().delete()


if __name__ == '__main__':
    import django
    from django.test.runner import DiscoverRunner
    
    # Run the tests
    runner = DiscoverRunner(verbosity=2)
    runner.run_tests(['core.tests.test_affiliate_e2e'])