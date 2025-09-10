# Affiliate Commission Tracking API Documentation

## Overview

The Affiliate Commission Tracking system provides a comprehensive API for managing affiliate programs, tracking conversions, calculating commissions, and processing payouts. This documentation covers all available endpoints, authentication requirements, and usage examples.

## Base URL

```
Production: https://api.retirementadvisorpro.com/api
Development: http://localhost:8000/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Public Endpoints (No Authentication Required)
- Click tracking
- Affiliate portal login
- Password setup

---

## Table of Contents

1. [Affiliate Management](#affiliate-management)
2. [Click Tracking](#click-tracking)
3. [Affiliate Links](#affiliate-links)
4. [Conversions](#conversions)
5. [Commissions](#commissions)
6. [Payouts](#payouts)
7. [Stripe Connect](#stripe-connect)
8. [Affiliate Portal](#affiliate-portal)
9. [Webhooks](#webhooks)

---

## Affiliate Management

### List Affiliates
```http
GET /affiliates/
```

**Query Parameters:**
- `status` (string): Filter by status (pending, active, suspended, terminated)
- `page` (integer): Page number for pagination
- `page_size` (integer): Number of results per page

**Response:**
```json
{
  "count": 25,
  "next": "http://api.example.com/affiliates/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "affiliate_code": "ABC12345",
      "business_name": "Marketing Pro LLC",
      "contact_name": "John Doe",
      "email": "john@marketingpro.com",
      "status": "active",
      "commission_rate_first_month": 20.0,
      "commission_rate_recurring": 5.0,
      "total_earnings": "1250.00",
      "pending_amount": "250.00",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Affiliate
```http
POST /affiliates/
```

**Request Body:**
```json
{
  "business_name": "Marketing Pro LLC",
  "contact_name": "John Doe",
  "email": "john@marketingpro.com",
  "phone": "+1-555-0123",
  "website_url": "https://marketingpro.com",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "commission_type": "percentage",
  "commission_rate_first_month": 20.0,
  "commission_rate_recurring": 5.0
}
```

### Get Affiliate Details
```http
GET /affiliates/{id}/
```

### Update Affiliate
```http
PUT /affiliates/{id}/
PATCH /affiliates/{id}/
```

### Delete Affiliate
```http
DELETE /affiliates/{id}/
```

### Get Affiliate Dashboard
```http
GET /affiliates/{id}/dashboard/
```

**Response:**
```json
{
  "total_clicks": 1523,
  "total_conversions": 47,
  "conversion_rate": 3.08,
  "total_earnings": "5250.00",
  "pending_commissions": "750.00",
  "last_30_days": {
    "clicks": 245,
    "conversions": 8,
    "earnings": "850.00"
  },
  "top_performing_links": [
    {
      "tracking_code": "SPRING2024",
      "clicks": 523,
      "conversions": 15
    }
  ]
}
```

---

## Click Tracking

### Track Click (Public Endpoint)
```http
POST /affiliates/track-click/
```

**Request Body:**
```json
{
  "affiliate_code": "ABC12345",
  "page_url": "https://retirementadvisorpro.com/features",
  "referrer": "https://affiliate-site.com/review"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Click tracked successfully",
  "session_id": "session_a1b2c3d4e5f6"
}
```

### Redirect Tracking (Public)
```http
GET /r/{tracking_code}/
```

Redirects to the destination URL while tracking the click.

**Example:**
```
https://api.retirementadvisorpro.com/r/SPRING2024/
→ Redirects to landing page with UTM parameters
```

---

## Affiliate Links

### List Affiliate Links
```http
GET /affiliates/{id}/links/
```

**Query Parameters:**
- `active_only` (boolean): Show only active links

### Create Affiliate Link
```http
POST /affiliate-links/
```

**Request Body:**
```json
{
  "affiliate": "550e8400-e29b-41d4-a716-446655440000",
  "campaign_name": "Spring 2024 Campaign",
  "destination_url": "/pricing",
  "discount_code": "SPRING20",
  "utm_source": "affiliate",
  "utm_medium": "banner",
  "utm_campaign": "spring2024",
  "max_uses": 100,
  "expires_at": "2024-06-30T23:59:59Z"
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "tracking_code": "SPR2024XYZ",
  "short_url": "https://rap.link/SPR2024XYZ",
  "full_url": "https://retirementadvisorpro.com/pricing?ref=ABC12345&utm_source=affiliate",
  "clicks": 0,
  "conversions": 0,
  "is_active": true
}
```

---

## Conversions

### List Conversions
```http
GET /conversions/
```

**Query Parameters:**
- `affiliate` (UUID): Filter by affiliate
- `start_date` (date): Filter by date range
- `end_date` (date): Filter by date range
- `is_valid` (boolean): Show only valid conversions

### Get Conversion Details
```http
GET /conversions/{id}/
```

### Mark Conversion as Refunded
```http
POST /conversions/{id}/refund/
```

---

## Commissions

### List Commissions
```http
GET /affiliates/{id}/commissions/
```

**Query Parameters:**
- `status` (string): pending, approved, paid, cancelled
- `start_date` (date): Period start date
- `end_date` (date): Period end date

**Response:**
```json
{
  "results": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "conversion_id": "880e8400-e29b-41d4-a716-446655440003",
      "commission_type": "first_month",
      "description": "First month commission for john@example.com",
      "base_amount": "39.99",
      "commission_rate": 0.20,
      "commission_amount": "7.99",
      "status": "approved",
      "period_start": "2024-01-01",
      "period_end": "2024-01-31",
      "created_at": "2024-02-01T00:00:00Z"
    }
  ]
}
```

### Approve Commission
```http
POST /commissions/{id}/approve/
```

### Bulk Approve Commissions
```http
POST /commissions/bulk-approve/
```

**Request Body:**
```json
{
  "commission_ids": [
    "770e8400-e29b-41d4-a716-446655440002",
    "770e8400-e29b-41d4-a716-446655440003"
  ]
}
```

---

## Payouts

### List Payouts
```http
GET /payouts/
```

### Create Manual Payout (Admin Only)
```http
POST /stripe-connect/create-payout/
```

**Request Body:**
```json
{
  "affiliate_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "250.00",
  "currency": "usd",
  "description": "Manual commission payout"
}
```

### Process Batch Payouts (Admin Only)
```http
POST /stripe-connect/batch-payouts/
```

**Request Body:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "min_payout": "50.00"
}
```

**Response:**
```json
{
  "success": true,
  "period": "2024-01-01 to 2024-01-31",
  "results": [
    {
      "affiliate": "Marketing Pro LLC",
      "status": "success",
      "transfer_id": "tr_1234567890",
      "amount": "250.00",
      "commissions_paid": 5
    }
  ],
  "total_processed": 3,
  "total_paid": 3
}
```

---

## Stripe Connect

### Create Connect Account
```http
POST /stripe-connect/create-account/
```

Creates a new Stripe Connect account for the authenticated affiliate.

### Generate Account Link
```http
POST /stripe-connect/account-link/
```

Generates an onboarding link for Stripe Connect setup.

**Response:**
```json
{
  "success": true,
  "url": "https://connect.stripe.com/setup/s/acct_1234567890/abcdefgh",
  "expires_at": 1704067200
}
```

### Check Account Status
```http
GET /stripe-connect/account-status/
```

**Response:**
```json
{
  "status": "active",
  "account_id": "acct_1234567890",
  "charges_enabled": true,
  "payouts_enabled": true,
  "details_submitted": true,
  "requirements": {
    "currently_due": [],
    "eventually_due": [],
    "past_due": []
  }
}
```

### Get Payout Dashboard
```http
GET /stripe-connect/payout-dashboard/
```

**Response:**
```json
{
  "total_paid": "5250.00",
  "pending_amount": "750.00",
  "stripe_status": "active",
  "stripe_account_id": "acct_1234567890",
  "recent_payouts": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "period": "2024-01-01 to 2024-01-31",
      "amount": "250.00",
      "status": "completed",
      "date": "2024-02-01T10:00:00Z"
    }
  ],
  "payout_settings": {
    "payment_method": "stripe_connect",
    "minimum_payout": "50.00",
    "payout_schedule": "monthly"
  }
}
```

---

## Affiliate Portal

### Portal Login (Public)
```http
POST /affiliates/portal-login/
```

**Request Body (with code):**
```json
{
  "email": "john@marketingpro.com",
  "code": "ABC12345"
}
```

**Request Body (with password):**
```json
{
  "email": "john@marketingpro.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "affiliate": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "business_name": "Marketing Pro LLC",
    "email": "john@marketingpro.com"
  },
  "session": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "affiliate": {
      "affiliate_id": "550e8400-e29b-41d4-a716-446655440000",
      "affiliate_code": "ABC12345",
      "name": "Marketing Pro LLC",
      "is_affiliate_portal": true
    }
  }
}
```

### Setup Password (Public)
```http
POST /affiliates/setup-password/
```

**Request Body:**
```json
{
  "email": "john@marketingpro.com",
  "code": "ABC12345",
  "password": "newsecurepassword123"
}
```

---

## Webhooks

### Stripe Webhook
```http
POST /webhooks/stripe/
```

Handles Stripe events for subscription creation and updates. Automatically tracks conversions and creates commission records.

**Headers:**
```
Stripe-Signature: t=1614556800,v1=signature...
```

**Handled Events:**
- `customer.subscription.created` - Tracks new conversions
- `customer.subscription.updated` - Updates subscription status
- `customer.subscription.deleted` - Marks conversions as canceled
- `charge.refunded` - Marks conversions as refunded

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Invalid request data",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred"
}
```

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authenticated users**: 1000 requests per minute
- **Anonymous users**: 100 requests per minute
- **Click tracking**: 10 requests per second per IP

---

## Pagination

List endpoints support pagination using the following parameters:

- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)

**Response includes:**
```json
{
  "count": 150,
  "next": "https://api.example.com/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Filtering and Sorting

Most list endpoints support filtering and sorting:

**Common Filters:**
- `status`: Filter by status
- `start_date`: Filter by date range start
- `end_date`: Filter by date range end
- `search`: Text search across relevant fields

**Sorting:**
- `ordering`: Field to sort by (prefix with `-` for descending)
- Example: `?ordering=-created_at` (newest first)

---

## Integration Examples

### JavaScript/Node.js

```javascript
// Track a click
const trackClick = async (affiliateCode) => {
  const response = await fetch('https://api.retirementadvisorpro.com/api/affiliates/track-click/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      affiliate_code: affiliateCode,
      page_url: window.location.href,
      referrer: document.referrer
    })
  });
  
  const data = await response.json();
  console.log('Click tracked:', data.session_id);
};

// Get affiliate dashboard
const getAffiliateDashboard = async (token, affiliateId) => {
  const response = await fetch(`https://api.retirementadvisorpro.com/api/affiliates/${affiliateId}/dashboard/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  return data;
};
```

### Python

```python
import requests

# Track a click
def track_click(affiliate_code, page_url, referrer):
    url = "https://api.retirementadvisorpro.com/api/affiliates/track-click/"
    payload = {
        "affiliate_code": affiliate_code,
        "page_url": page_url,
        "referrer": referrer
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Process batch payouts
def process_payouts(token, start_date, end_date):
    url = "https://api.retirementadvisorpro.com/api/stripe-connect/batch-payouts/"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "min_payout": "50.00"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

### cURL

```bash
# Track a click
curl -X POST https://api.retirementadvisorpro.com/api/affiliates/track-click/ \
  -H "Content-Type: application/json" \
  -d '{
    "affiliate_code": "ABC12345",
    "page_url": "https://retirementadvisorpro.com",
    "referrer": "https://google.com"
  }'

# Get affiliate dashboard
curl -X GET https://api.retirementadvisorpro.com/api/affiliates/550e8400-e29b-41d4-a716-446655440000/dashboard/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Testing

### Test Affiliate Codes

For testing in development environment:

- `TEST1234` - Active affiliate with high conversion rate
- `TEST5678` - Pending affiliate awaiting approval
- `TEST9999` - Suspended affiliate

### Test Stripe Accounts

Use Stripe test mode account IDs:
- `acct_1234567890TEST` - Fully verified account
- `acct_0987654321TEST` - Pending verification

---

## Changelog

### Version 1.0.0 (January 2025)
- Initial release
- Affiliate management endpoints
- Click tracking and attribution
- Commission calculation
- Stripe Connect integration
- Affiliate portal authentication

---

## Support

For API support, please contact:
- Email: api-support@retirementadvisorpro.com
- Documentation: https://docs.retirementadvisorpro.com/api/affiliates
- Status Page: https://status.retirementadvisorpro.com

---

## Terms of Use

By using the Affiliate API, you agree to:
1. Not exceed rate limits
2. Properly secure authentication credentials
3. Comply with data protection regulations
4. Report security vulnerabilities responsibly

For complete terms, visit: https://retirementadvisorpro.com/api-terms