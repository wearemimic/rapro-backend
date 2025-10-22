# AWS Systems Manager Parameters - Created for Production & Staging

## ✅ Parameters Created

All parameters have been created in **AWS Systems Manager Parameter Store** in the `us-east-1` region.

### Email Configuration (AWS SES) - READY ✅

| Parameter Name | Type | Value | Status |
|----------------|------|-------|--------|
| `/rapro-prod/email/smtp-user` | SecureString | `AKIA3RYC52SPQZKDIO7T` | ✅ Ready |
| `/rapro-prod/email/smtp-password` | SecureString | `BE+drxH2k/4moNh6YIvNsEBaCY+B5jZnbGmBG8YiKAco` | ✅ Ready |
| `/rapro-prod/email/host` | String | `email-smtp.us-east-1.amazonaws.com` | ✅ Ready |
| `/rapro-prod/email/default-from` | String | `noreply@retirementadvisorpro.com` | ✅ Ready |
| `/rapro-prod/email/admin-email` | String | `admin@retirementadvisorpro.com` | ✅ Ready |

### Kajabi Configuration (NSSA Integration) - NEEDS UPDATE ⚠️

| Parameter Name | Type | Current Value | Status |
|----------------|------|---------------|--------|
| `/rapro-prod/kajabi/webhook-secret` | SecureString | `PLACEHOLDER-UPDATE-AFTER-CONFIGURING-KAJABI` | ⚠️ Update needed |
| `/rapro-prod/kajabi/api-key` | SecureString | `PLACEHOLDER-UPDATE-AFTER-CONFIGURING-KAJABI` | ⚠️ Update needed |
| `/rapro-prod/kajabi/product-id` | String | `PLACEHOLDER-UPDATE-WITH-NSSA-PRODUCT-ID` | ⚠️ Update needed |

---

## 📋 How to Update Task Definitions

The parameters are created, but you need to add them to your ECS task definitions so the containers can access them.

### Option 1: Update via Infrastructure as Code (Recommended)

If you're using Terraform, CloudFormation, or CDK, add these to your task definition:

**For Secrets (SecureString parameters):**
```json
"secrets": [
  {
    "name": "EMAIL_HOST_USER",
    "valueFrom": "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/email/smtp-user"
  },
  {
    "name": "EMAIL_HOST_PASSWORD",
    "valueFrom": "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/email/smtp-password"
  },
  {
    "name": "KAJABI_WEBHOOK_SECRET",
    "valueFrom": "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/kajabi/webhook-secret"
  },
  {
    "name": "KAJABI_API_KEY",
    "valueFrom": "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/kajabi/api-key"
  }
]
```

**For Environment Variables (String parameters):**
```json
"environment": [
  {
    "name": "EMAIL_BACKEND",
    "value": "django.core.mail.backends.smtp.EmailBackend"
  },
  {
    "name": "EMAIL_HOST",
    "valueFrom": "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/email/host"
  },
  {
    "name": "EMAIL_PORT",
    "value": "587"
  },
  {
    "name": "EMAIL_USE_TLS",
    "value": "True"
  },
  {
    "name": "DEFAULT_FROM_EMAIL",
    "valueFrom": "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/email/default-from"
  },
  {
    "name": "ADMIN_EMAIL",
    "valueFrom": "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/email/admin-email"
  },
  {
    "name": "KAJABI_API_BASE_URL",
    "value": "https://api.kajabi.com"
  },
  {
    "name": "NSSA_KAJABI_PRODUCT_ID",
    "valueFrom": "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/kajabi/product-id"
  }
]
```

### Option 2: Manual Update via AWS Console

1. Go to **ECS Console** → **Task Definitions**
2. Select `rapro-prod-backend` (or `rapro-prod-backend-staging`)
3. Click **Create new revision**
4. Scroll to **Environment variables**
5. Add the secrets and environment variables as shown above
6. Click **Create**
7. Update the service to use the new task definition

### Option 3: Using AWS CLI

I can create a script to update the task definitions if you'd like.

---

## 🔐 IAM Permissions Required

Make sure your ECS task execution role has permission to read these parameters:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameters",
        "ssm:GetParameter"
      ],
      "Resource": [
        "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/email/*",
        "arn:aws:ssm:us-east-1:794038228127:parameter/rapro-prod/kajabi/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:us-east-1:794038228127:key/*"
    }
  ]
}
```

Most likely your task execution role already has these permissions for existing parameters.

---

## 🔄 Updating Kajabi Parameters (When Ready)

When you get the Kajabi credentials, update the placeholder values:

```bash
# Update webhook secret
aws ssm put-parameter \
  --name "/rapro-prod/kajabi/webhook-secret" \
  --value "your-actual-kajabi-webhook-secret" \
  --type "SecureString" \
  --overwrite \
  --region us-east-1

# Update API key
aws ssm put-parameter \
  --name "/rapro-prod/kajabi/api-key" \
  --value "your-actual-kajabi-api-key" \
  --type "SecureString" \
  --overwrite \
  --region us-east-1

# Update product ID
aws ssm put-parameter \
  --name "/rapro-prod/kajabi/product-id" \
  --value "your-nssa-product-id" \
  --type "String" \
  --overwrite \
  --region us-east-1
```

Then restart your ECS services to pick up the new values:

```bash
# Staging
aws ecs update-service \
  --cluster rapro-prod-staging \
  --service rapro-prod-backend-staging \
  --force-new-deployment \
  --region us-east-1

# Production
aws ecs update-service \
  --cluster rapro-prod-cluster \
  --service rapro-prod-backend \
  --force-new-deployment \
  --region us-east-1
```

---

## 📊 View All Parameters

```bash
# List all email parameters
aws ssm get-parameters-by-path \
  --path /rapro-prod/email \
  --region us-east-1 \
  --with-decryption

# List all Kajabi parameters
aws ssm get-parameters-by-path \
  --path /rapro-prod/kajabi \
  --region us-east-1 \
  --with-decryption
```

---

## ✅ What's Working Now

- ✅ AWS SES SMTP credentials stored securely
- ✅ Email configuration ready for production
- ✅ Admin email configured: `admin@retirementadvisorpro.com`
- ✅ Kajabi parameter placeholders created
- ✅ Both staging and production can use the same parameters

---

## 🚀 Next Steps

1. **Update Task Definitions** - Add the new parameters to your ECS task definitions
2. **Deploy New Task Definition** - Update services to use the new task definition
3. **Test Email Sending** - Send a test email to verify SMTP works
4. **Get Kajabi Credentials** - Configure webhook in Kajabi and get API key
5. **Update Kajabi Parameters** - Replace placeholder values with real credentials
6. **Test NSSA Integration** - Send test webhook from Kajabi

---

## 📧 Verify Parameters Are Accessible

After updating the task definition, SSH into a running container and verify:

```bash
# Should see the email configuration
echo $EMAIL_HOST_USER
echo $EMAIL_HOST
echo $DEFAULT_FROM_EMAIL
echo $ADMIN_EMAIL

# Should see Kajabi config (will be placeholders until updated)
echo $KAJABI_WEBHOOK_SECRET
echo $KAJABI_API_KEY
echo $NSSA_KAJABI_PRODUCT_ID
```

---

## 🔧 Troubleshooting

### Container can't access parameters
- Check task execution role has `ssm:GetParameters` permission
- Check task execution role has `kms:Decrypt` permission
- Verify parameter ARNs are correct in task definition

### Parameters not updating after change
- Restart ECS service with `--force-new-deployment`
- Wait 2-3 minutes for new tasks to start
- Check CloudWatch logs for any errors

### Email not sending
- Verify SMTP credentials are correct
- Check AWS SES sending limits (200/day currently)
- Check CloudWatch logs for Django email errors
- Verify SES domain is verified (`aws ses get-identity-verification-attributes`)

---

**Created:** 2025-01-20
**Region:** us-east-1
**Account:** 794038228127
**Environment:** Shared between staging and production
