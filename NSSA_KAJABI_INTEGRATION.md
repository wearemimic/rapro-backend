# NSSA/Kajabi Integration - Complete Documentation

## 🎯 Overview

This integration allows **National Social Security Advisors (NSSA)** to sell annual memberships ($299/year) through Kajabi, with automatic user provisioning in Retirement Advisor Pro.

**Key Features:**
- ✅ Automatic user account creation from Kajabi purchases
- ✅ Secure password setup flow via email
- ✅ Subscription lifecycle management (cancel, renew, expire)
- ✅ Admin notifications for new signups
- ✅ Existing user linkage support
- ✅ Complete audit trail of all webhook events
- ✅ Admin tools for subscription verification

---

## 📋 Table of Contents

1. [How It Works](#how-it-works)
2. [Deployment Guide](#deployment-guide)
3. [Testing Guide](#testing-guide)
4. [Admin Tools](#admin-tools)
5. [Troubleshooting](#troubleshooting)
6. [API Documentation](#api-documentation)

---

## How It Works

### User Flow

```
1. User purchases NSSA membership on Kajabi ($299/year)
                    ↓
2. Kajabi sends webhook → POST /api/webhook/kajabi/
                    ↓
3. Backend creates/updates user account:
   - New user: Creates account (inactive)
   - Existing user: Links to NSSA
                    ↓
4. Emails sent:
   - User: Welcome email with password setup link
   - Admin: Notification of new signup/linkage
                    ↓
5. User clicks setup link → /nssa/setup-password
                    ↓
6. User sets password → Account activated
                    ↓
7. User logged in → Redirected to dashboard
                    ↓
8. User has full access to platform!
```

### Technical Flow

**Webhook Events:**
- `offer.purchased` → Create or link user account
- `member.subscription.canceled` → Mark canceled, keep access until end date
- `member.subscription.renewed` → Reactivate subscription
- `member.subscription.expired` → Expire subscription, disable access

**Database Tracking:**
```python
User {
    email: "user@example.com"
    auth_provider: "kajabi"
    subscription_status: "active" | "canceled" | "expired"
    subscription_plan: "nssa_annual"
    subscription_end_date: "2026-01-20T00:00:00Z"
    metadata: {
        "partner": "NSSA",
        "kajabi_member_id": "mem_123",
        "kajabi_offer_id": "off_456",
        "signup_date": "2025-01-20T12:00:00Z"
    }
}
```

---

## Deployment Guide

### Prerequisites

1. **AWS Account** (for email via SES)
2. **Kajabi Account** (with admin access)
3. **Production Environment** (Django backend + Vue.js frontend)

### Step 1: Configure AWS SES (15 minutes)

**Why AWS SES?**
- Extremely cost-effective ($0.10/1,000 emails after free tier)
- 99.9% uptime SLA
- Built-in bounce/complaint handling
- First 62,000 emails/month FREE (when sending from EC2)

**Setup:**

1. Go to [AWS SES Console](https://console.aws.amazon.com/ses/)

2. **Verify Domain:**
   - Click "Verified identities" → "Create identity"
   - Select "Domain"
   - Enter: `retirementadvisorpro.com`
   - AWS provides DNS records (TXT, CNAME, MX)
   - Add these to your DNS provider
   - Wait 10-20 minutes for verification

3. **Create SMTP Credentials:**
   - Click "SMTP Settings"
   - Click "Create SMTP Credentials"
   - Save username and password securely

4. **Move out of Sandbox** (if in sandbox):
   - Click "Account dashboard"
   - Click "Request production access"
   - Fill out form (usually approved in 24-48 hours)

### Step 2: Set Environment Variables (5 minutes)

Add to your production environment:

```bash
# Email Configuration (AWS SES)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com  # Your SES region
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-ses-smtp-username>
EMAIL_HOST_PASSWORD=<your-ses-smtp-password>
DEFAULT_FROM_EMAIL=noreply@retirementadvisorpro.com
ADMIN_EMAIL=<your-admin-email@domain.com>

# Kajabi Configuration
KAJABI_WEBHOOK_SECRET=<from-kajabi-webhook-settings>
KAJABI_API_KEY=<from-kajabi-api-settings>
KAJABI_API_BASE_URL=https://api.kajabi.com
NSSA_KAJABI_PRODUCT_ID=<nssa-product-id-from-kajabi>

# Frontend URL
FRONTEND_URL=https://app.retirementadvisorpro.com
```

**How to get Kajabi credentials:**

1. **Webhook Secret:**
   - Log into Kajabi
   - Go to Settings → Webhooks
   - Click "Add Webhook" or edit existing
   - Copy the "Webhook Secret"

2. **API Key:**
   - Go to Settings → Integrations → API
   - Generate new API key
   - Save securely

3. **Product ID:**
   - Go to Products → NSSA Annual Membership
   - Look in URL or product settings
   - Format: `prod_xxxxx` or numeric ID

### Step 3: Run Database Migrations (2 minutes)

```bash
# Connect to production server
ssh your-production-server

# Navigate to backend directory
cd /path/to/rapro-backend

# Activate virtual environment (if using one)
source venv/bin/activate

# Run migrations
python manage.py migrate

# Verify migrations
python manage.py showmigrations core

# Should see:
# [X] 0043_add_kajabi_auth_provider
# [X] 0044_kajabiwebhookevent
```

### Step 4: Configure Kajabi Webhook (5 minutes)

1. Log into Kajabi admin panel

2. Go to **Settings → Webhooks**

3. Click **"Add Webhook"**

4. Configure:
   - **Webhook URL:** `https://api.retirementadvisorpro.com/api/webhook/kajabi/`
   - **Events to subscribe:**
     - ✅ `offer.purchased`
     - ✅ `member.subscription.canceled`
     - ✅ `member.subscription.renewed`
     - ✅ `member.subscription.expired`
   - **Webhook Secret:** Copy this and save to environment variables

5. Click **Save**

6. **Test webhook** using Kajabi's test feature (see Testing Guide below)

### Step 5: Verify Installation (5 minutes)

**Check 1: Admin Panel Access**
```
https://api.retirementadvisorpro.com/admin/core/kajabiwebhookevent/
```
Should see empty list (no events yet)

**Check 2: API Endpoints**
```bash
# Test webhook endpoint (should return 405 Method Not Allowed for GET)
curl https://api.retirementadvisorpro.com/api/webhook/kajabi/

# Test password setup page
curl https://app.retirementadvisorpro.com/nssa/setup-password
```

**Check 3: Email Configuration**
```python
# Django shell
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test',
    'noreply@retirementadvisorpro.com',
    ['your-email@domain.com'],
)

# Check your inbox
```

---

## Testing Guide

### Test 1: Manual Webhook Test (Recommended)

**Using Kajabi's Test Feature:**

1. Go to Kajabi → Settings → Webhooks
2. Find your webhook
3. Click "Test" button
4. Select event: `offer.purchased`
5. Click "Send Test"

**Expected Result:**
- Kajabi sends test event
- Your webhook receives it
- Check Django admin → Kajabi Webhook Events
- Should see new event with `processed=True`

### Test 2: Create Test Purchase

**Using Kajabi:**

1. Create a test member with a **unique email** (e.g., `test+1@yourdomain.com`)
2. Manually enroll them in NSSA product
3. Kajabi triggers real webhook

**Expected Result:**
- User created in your database
- Welcome email sent to test email
- Admin notification sent to you
- Check Django admin → Users → filter by `auth_provider=kajabi`

### Test 3: Password Setup Flow

1. Check email inbox for test user
2. Click password setup link
3. Should redirect to: `https://app.retirementadvisorpro.com/nssa/setup-password?token=xxx&email=xxx`
4. Set password
5. Should auto-login and redirect to dashboard

### Test 4: Subscription Cancellation

1. In Kajabi, cancel the test subscription
2. Webhook fires: `member.subscription.canceled`
3. Check user in Django admin:
   - `subscription_status` should be `canceled`
   - `subscription_end_date` should be set (30 days from now or billing period end)
   - User should still have access until end date

### Test 5: Existing User Linkage

1. Create a user directly in your database with email `existing@test.com`
2. Purchase NSSA membership in Kajabi with same email
3. Webhook fires
4. Check Django admin:
   - User's `metadata` should now include `partner: NSSA`
   - `subscription_status` updated to `active`
   - Admin receives "existing user linked" notification

---

## Admin Tools

### 1. View All NSSA Users

**API Endpoint:**
```bash
GET /api/admin/nssa-users/

# With filters
GET /api/admin/nssa-users/?subscription_status=active
GET /api/admin/nssa-users/?is_active=true
GET /api/admin/nssa-users/?page=1&page_size=50
```

**Django Admin:**
```
/admin/core/customuser/
Filter: auth_provider = "kajabi"
```

### 2. Verify Subscription Status

Checks current status in Kajabi and compares with database.

**API Endpoint:**
```bash
GET /api/admin/users/<user_id>/verify-kajabi-subscription/
```

**Response:**
```json
{
  "user": {
    "id": 123,
    "email": "user@example.com",
    "kajabi_member_id": "mem_456"
  },
  "database_status": {
    "subscription_status": "active",
    "subscription_plan": "nssa_annual",
    "subscription_end_date": "2026-01-20T00:00:00Z"
  },
  "kajabi_status": {
    "is_active": true,
    "status": "active",
    "subscriptions": [...]
  },
  "mismatch": false,
  "recommended_action": null
}
```

### 3. Sync Subscription Status

Updates database to match Kajabi's current status.

**API Endpoint:**
```bash
POST /api/admin/users/<user_id>/sync-kajabi-subscription/
```

**Response:**
```json
{
  "success": true,
  "message": "Subscription status synced successfully",
  "old_status": "canceled",
  "new_status": "active"
}
```

### 4. View Webhook Event Log

**Django Admin:**
```
/admin/core/kajabiwebhookevent/
```

**Features:**
- See all incoming webhooks
- Processing status (pending, processed, error)
- Full payload inspection
- Error messages
- Filter by event type, user, date

---

## Troubleshooting

### Issue: Webhook not receiving events

**Check:**
1. Webhook URL configured correctly in Kajabi
2. HTTPS certificate valid
3. Firewall/security groups allow traffic
4. Check server logs: `tail -f /var/log/django/error.log`

**Test:**
```bash
# Test webhook endpoint is accessible
curl -X POST https://api.retirementadvisorpro.com/api/webhook/kajabi/ \
  -H "Content-Type: application/json" \
  -d '{"type": "test", "id": "123"}'

# Should return 200 or 400, not timeout
```

### Issue: Webhook signature verification fails

**Check:**
1. `KAJABI_WEBHOOK_SECRET` environment variable set correctly
2. Secret matches Kajabi settings
3. Check Django logs for signature mismatch errors

**Temporarily disable** (for debugging only):
```python
# In core/webhooks.py kajabi_webhook function
# Comment out signature verification temporarily
# if hasattr(settings, 'KAJABI_WEBHOOK_SECRET') and settings.KAJABI_WEBHOOK_SECRET:
#     if not verify_kajabi_signature(request):
#         ...
```

### Issue: Emails not sending

**Check:**
1. AWS SES credentials correct
2. Domain verified in SES
3. Not in SES sandbox (can only send to verified emails)
4. Check SES sending statistics in AWS console

**Test:**
```python
python manage.py shell

from django.core.mail import send_mail
send_mail('Test', 'Test message', 'noreply@retirementadvisorpro.com', ['your-email@domain.com'])
```

### Issue: User created but email not received

**Check:**
1. Email went to spam folder
2. Check SES bounce/complaint metrics
3. Verify `FRONTEND_URL` environment variable correct
4. Check Django logs for email errors

**Manual resend:**
```python
from core.kajabi_views import *
from core.models import CustomUser

user = CustomUser.objects.get(email='user@example.com')
token = generate_password_setup_token(user)
send_nssa_welcome_email(user, token)
```

### Issue: Password setup link expired

**User sees:** "Token has expired. Please request a new setup link."

**Solution:** User clicks "Resend" on setup page, or admin manually triggers:

```bash
POST /api/kajabi/resend-setup-email/
{
  "email": "user@example.com"
}
```

### Issue: Duplicate webhook events

**Symptoms:** Same event processed multiple times

**Protection:** Built-in idempotency check using `event_id`

**Check:** Django admin → Kajabi Webhook Events → Look for duplicate `event_id`

---

## API Documentation

### Webhook Endpoint

```
POST /api/webhook/kajabi/
```

**Authentication:** Webhook signature (HMAC-SHA256)

**Events Handled:**
- `offer.purchased`
- `member.subscription.canceled`
- `member.subscription.renewed`
- `member.subscription.expired`

**Request Body:**
```json
{
  "type": "offer.purchased",
  "id": "evt_123456",
  "member": {
    "id": "mem_789",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "offer": {
    "id": "off_456",
    "name": "NSSA Annual Membership"
  }
}
```

**Response:**
```json
{
  "status": "success"
}
```

### Password Setup Endpoints

**Set Password:**
```
POST /api/kajabi/setup-password/
```

**Request:**
```json
{
  "email": "user@example.com",
  "token": "secure-token-from-email",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password set successfully",
  "user": {
    "email": "user@example.com",
    "first_name": "John",
    "partner": "NSSA"
  }
}
```

**Resend Setup Email:**
```
POST /api/kajabi/resend-setup-email/
```

**Request:**
```json
{
  "email": "user@example.com"
}
```

### Admin Endpoints

**List NSSA Users:**
```
GET /api/admin/nssa-users/?page=1&page_size=50&subscription_status=active
```

**Verify Subscription:**
```
GET /api/admin/users/<user_id>/verify-kajabi-subscription/
```

**Sync Subscription:**
```
POST /api/admin/users/<user_id>/sync-kajabi-subscription/
```

---

## Security Notes

- ✅ Webhook signature verification (HMAC-SHA256)
- ✅ Password setup tokens expire in 24 hours
- ✅ Idempotent webhook processing
- ✅ httpOnly cookies for JWT tokens
- ✅ Admin endpoints require admin authentication
- ✅ Complete audit trail in `KajabiWebhookEvent` model

---

## Support

**Technical Issues:**
- Check Django logs: `/var/log/django/error.log`
- Check webhook event log: Django admin → Kajabi Webhook Events
- Check email delivery: AWS SES Console → Sending Statistics

**Business/Account Issues:**
- Contact NSSA support
- Contact Kajabi support

**Bug Reports:**
- Create GitHub issue with:
  - Webhook event ID
  - User email (if applicable)
  - Error message from logs
  - Steps to reproduce

---

## Changelog

**v1.0.0 - 2025-01-20**
- Initial release
- Basic webhook handling
- Password setup flow
- Admin tools

---

## License

Proprietary - Retirement Advisor Pro
© 2025 All Rights Reserved
