#!/usr/bin/env python
"""
Test script for affiliate tracking system
Run this script to test the affiliate tracking functionality
"""

import os
import sys
import django
import json
import uuid
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.affiliate_models import Affiliate, AffiliateClick, AffiliateConversion, Commission
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

def test_affiliate_tracking():
    """Test the complete affiliate tracking flow"""
    
    print("=" * 80)
    print("AFFILIATE TRACKING SYSTEM TEST")
    print("=" * 80)
    
    # 1. Create a test affiliate
    print("\n1. Creating test affiliate...")
    affiliate = Affiliate.objects.create(
        business_name="Test Affiliate Business",
        contact_name="Test Affiliate",
        email=f"test-affiliate-{uuid.uuid4().hex[:8]}@example.com",
        commission_rate_first_month=Decimal("20.00"),
        commission_rate_recurring=Decimal("5.00"),
        commission_type="percentage",
        status="active"
    )
    print(f"   ✅ Created affiliate: {affiliate.business_name} with code: {affiliate.affiliate_code}")
    
    # 2. Simulate a click tracking
    print("\n2. Simulating click tracking...")
    click = AffiliateClick.objects.create(
        affiliate=affiliate,
        session_id=f"session_{uuid.uuid4().hex[:16]}",
        tracking_code=affiliate.affiliate_code,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 Test Browser",
        referrer="https://google.com"
    )
    print(f"   ✅ Tracked click ID: {click.id}")
    
    # 3. Create a test user with affiliate attribution
    print("\n3. Creating user with affiliate attribution...")
    test_user = User.objects.create_user(
        username=f"test-user-{uuid.uuid4().hex[:8]}",
        email=f"test-user-{uuid.uuid4().hex[:8]}@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
        metadata={
            "affiliate_code": affiliate.affiliate_code,
            "affiliate_tracked_at": timezone.now().isoformat()
        }
    )
    print(f"   ✅ Created user: {test_user.email}")
    print(f"   📊 Metadata: {test_user.metadata}")
    
    # 4. Simulate a conversion (subscription creation)
    print("\n4. Simulating conversion...")
    conversion = AffiliateConversion.objects.create(
        affiliate=affiliate,
        click=click,
        user=test_user,
        user_email=test_user.email,
        stripe_subscription_id=f"sub_test_{uuid.uuid4().hex[:12]}",
        stripe_customer_id=f"cus_test_{uuid.uuid4().hex[:12]}",
        subscription_plan="monthly",
        subscription_amount=Decimal("39.99"),
        mrr_value=Decimal("39.99"),
        attribution_type="direct"
    )
    print(f"   ✅ Created conversion ID: {conversion.id}")
    print(f"   💰 Subscription amount: ${conversion.subscription_amount}")
    
    # 5. Calculate and create commission
    print("\n5. Calculating commission...")
    if affiliate.commission_type == "percentage":
        commission_amount = (conversion.subscription_amount * affiliate.commission_rate_first_month) / 100
    else:
        commission_amount = affiliate.flat_rate_amount or Decimal("0.00")
    
    commission = Commission.objects.create(
        affiliate=affiliate,
        conversion=conversion,
        commission_type="first_month",
        description=f"First month commission for {test_user.email}",
        base_amount=conversion.subscription_amount,
        commission_rate=affiliate.commission_rate_first_month / 100,
        commission_amount=commission_amount,
        status="pending",
        period_start=(timezone.now() - timedelta(days=30)).date(),
        period_end=timezone.now().date()
    )
    print(f"   ✅ Created commission ID: {commission.id}")
    print(f"   💵 Commission amount: ${commission.commission_amount}")
    print(f"   📊 Commission rate: {affiliate.commission_rate_first_month}%")
    
    # 6. Check affiliate statistics
    print("\n6. Affiliate Statistics:")
    total_clicks = AffiliateClick.objects.filter(affiliate=affiliate).count()
    total_conversions = AffiliateConversion.objects.filter(affiliate=affiliate).count()
    total_commission = Commission.objects.filter(
        affiliate=affiliate
    ).aggregate(
        total=models.Sum('commission_amount')
    )['total'] or Decimal("0.00")
    
    print(f"   📈 Total clicks: {total_clicks}")
    print(f"   🎯 Total conversions: {total_conversions}")
    print(f"   💰 Total commission earned: ${total_commission}")
    
    # 7. Test the tracking endpoint
    print("\n7. Testing click tracking endpoint...")
    from django.test import Client
    client = Client()
    response = client.post('/api/affiliates/track-click/', 
        json.dumps({
            'affiliate_code': affiliate.affiliate_code,
            'page_url': 'https://retirementadvisorpro.com/register',
            'referrer': 'https://affiliate-site.com'
        }),
        content_type='application/json'
    )
    print(f"   📡 Response status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Click tracking endpoint working")
    else:
        print(f"   ❌ Click tracking failed: {response.content}")
    
    # 8. Clean up test data
    print("\n8. Cleaning up test data...")
    Commission.objects.filter(affiliate=affiliate).delete()
    AffiliateConversion.objects.filter(affiliate=affiliate).delete()
    AffiliateClick.objects.filter(affiliate=affiliate).delete()
    test_user.delete()
    affiliate.delete()
    print("   ✅ Test data cleaned up")
    
    print("\n" + "=" * 80)
    print("✅ AFFILIATE TRACKING TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    from django.db import models
    test_affiliate_tracking()