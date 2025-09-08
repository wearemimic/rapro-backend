# Stripe Configuration for AWS Staging/Production

## Overview
The application uses Stripe for payment processing. Stripe keys are managed through AWS Systems Manager (SSM) Parameter Store for security.

## Configuration Architecture

### Local Development
- Stripe keys are loaded from `.env` file
- Settings automatically use `.env` values when `ENVIRONMENT` is not set or is `development`

### Staging/Production (AWS)
- Stripe keys are stored in AWS SSM Parameter Store
- ECS Task Definitions reference these SSM parameters as secrets
- Settings require these environment variables when `ENVIRONMENT` is `staging` or `production`

## Required Stripe Configuration

### Environment Variables/SSM Parameters

1. **STRIPE_SECRET_KEY** (Secret)
   - SSM Path: `/rapro-prod/stripe/secret-key`
   - Your Stripe secret key (starts with `sk_live_` or `sk_test_`)
   - Required for backend API operations

2. **STRIPE_PUBLISHABLE_KEY** (Public)
   - Configured in task definition as environment variable
   - Your Stripe publishable key (starts with `pk_live_` or `pk_test_`)
   - Used by frontend for Stripe.js

3. **STRIPE_WEBHOOK_SECRET** (Secret)
   - SSM Path: `/rapro-prod/stripe/webhook-secret`
   - Webhook endpoint secret for validating Stripe events
   - Format: `whsec_...`

4. **STRIPE_MONTHLY_PRICE_ID** (Public)
   - SSM Path: `/rapro-prod/stripe/monthly-price-id`
   - Stripe Price ID for monthly subscription
   - Format: `price_...`

5. **STRIPE_ANNUAL_PRICE_ID** (Public)
   - SSM Path: `/rapro-prod/stripe/annual-price-id`
   - Stripe Price ID for annual subscription
   - Format: `price_...`

## How to Update SSM Parameters

### Using AWS CLI

```bash
# Update Stripe Secret Key
aws ssm put-parameter \
  --name "/rapro-prod/stripe/secret-key" \
  --value "sk_live_YOUR_SECRET_KEY" \
  --type "SecureString" \
  --overwrite \
  --region us-east-1

# Update Stripe Webhook Secret
aws ssm put-parameter \
  --name "/rapro-prod/stripe/webhook-secret" \
  --value "whsec_YOUR_WEBHOOK_SECRET" \
  --type "SecureString" \
  --overwrite \
  --region us-east-1

# Update Monthly Price ID
aws ssm put-parameter \
  --name "/rapro-prod/stripe/monthly-price-id" \
  --value "price_YOUR_MONTHLY_PRICE_ID" \
  --type "String" \
  --overwrite \
  --region us-east-1

# Update Annual Price ID
aws ssm put-parameter \
  --name "/rapro-prod/stripe/annual-price-id" \
  --value "price_YOUR_ANNUAL_PRICE_ID" \
  --type "String" \
  --overwrite \
  --region us-east-1
```

### Using AWS Console

1. Navigate to AWS Systems Manager → Parameter Store
2. Search for parameters starting with `/rapro-prod/stripe/`
3. Click on each parameter and choose "Edit"
4. Update the value with your actual Stripe keys
5. Save changes

### After Updating Parameters

After updating SSM parameters, you need to restart the ECS services to pick up the new values:

```bash
# Force new deployment of backend service
aws ecs update-service \
  --cluster rapro-prod-staging \
  --service rapro-prod-backend-staging \
  --force-new-deployment \
  --region us-east-1

# Force new deployment of celery worker
aws ecs update-service \
  --cluster rapro-prod-staging \
  --service rapro-prod-celery-worker-staging \
  --force-new-deployment \
  --region us-east-1
```

## Getting Your Stripe Keys

### From Stripe Dashboard

1. Log into [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to Developers → API keys
3. Copy your keys:
   - **Publishable key**: Visible directly
   - **Secret key**: Click "Reveal test/live key" to view
4. For webhook secret:
   - Go to Developers → Webhooks
   - Click on your webhook endpoint
   - Click "Reveal" under Signing secret

### Creating Price IDs

1. In Stripe Dashboard, go to Products
2. Create a product for your subscription
3. Add pricing:
   - Monthly price
   - Annual price
4. Copy the Price IDs (format: `price_...`)

## Testing Stripe Integration

### Local Testing
```bash
# Test with curl
curl -X POST http://localhost:8000/api/validate-coupon/ \
  -H "Content-Type: application/json" \
  -d '{"coupon_code": "TEST100", "plan": "monthly"}'
```

### Staging Testing
```bash
# Test on staging
curl -X POST https://staging.retirementadvisorpro.com/api/validate-coupon/ \
  -H "Content-Type: application/json" \
  -d '{"coupon_code": "TEST100", "plan": "monthly"}'
```

## Available Test Coupons

For testing, these coupon codes are available in the live Stripe account:
- `TEST100` - 100% off forever
- `FREEMONTH` - First month free
- `SAVE50` - 50% off forever
- `LIMITEDTIME24` - 50% off forever

## Troubleshooting

### Stripe API Not Working on Staging/Production

1. Check if SSM parameters are set correctly:
```bash
aws ssm get-parameter --name "/rapro-prod/stripe/secret-key" --with-decryption --region us-east-1
```

2. Check ECS task logs for errors:
```bash
aws logs tail /ecs/rapro-prod-backend-staging --follow --region us-east-1
```

3. Verify environment variables in running task:
```bash
# Get task ARN
TASK_ARN=$(aws ecs list-tasks --cluster rapro-prod-staging --service-name rapro-prod-backend-staging --query 'taskArns[0]' --output text --region us-east-1)

# Describe task to see environment
aws ecs describe-tasks --cluster rapro-prod-staging --tasks $TASK_ARN --region us-east-1
```

### Common Issues

1. **"Invalid API Key provided"**: The STRIPE_SECRET_KEY in SSM is incorrect or not set
2. **"No such coupon"**: The coupon code doesn't exist in your Stripe account
3. **"Unable to validate coupon"**: Network issue or Stripe API is down

## Security Best Practices

1. **Never commit Stripe keys to Git**
2. **Use different keys for development/staging/production**
3. **Rotate keys regularly**
4. **Use webhook signatures to validate events**
5. **Restrict SSM parameter access to necessary roles only**