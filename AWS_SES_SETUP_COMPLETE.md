# AWS SES Setup - COMPLETE ✅

## Setup Status

✅ **Domain Identity Created**: retirementadvisorpro.com (Pending DNS verification)
✅ **DKIM Tokens Generated**: 3 tokens for email authentication
✅ **SMTP User Created**: ses-smtp-user-rapro
✅ **SMTP Credentials Generated**: Ready to use
✅ **Account Status**: OUT OF SANDBOX (can send to any email)
✅ **Email Address Verified**: noreply@retirementadvisorpro.com (check inbox)

**Current Limits:**
- 200 emails per 24 hours
- 1 email per second
- Can send to ANY email address (not in sandbox!)

---

## 🔐 SMTP Credentials (SAVE THESE SECURELY!)

### For Django settings.py / Environment Variables:

```bash
# AWS SES SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=AKIA3RYC52SPQZKDIO7T
EMAIL_HOST_PASSWORD=BE+drxH2k/4moNh6YIvNsEBaCY+B5jZnbGmBG8YiKAco
DEFAULT_FROM_EMAIL=noreply@retirementadvisorpro.com
ADMIN_EMAIL=<your-admin-email>
```

**⚠️ IMPORTANT: Keep EMAIL_HOST_PASSWORD secret! Never commit to git.**

---

## 📋 DNS Records to Add (REQUIRED for Domain Verification)

Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.) and add these records:

### 1. Domain Verification (TXT Record)

```
Type: TXT
Name: _amazonses.retirementadvisorpro.com
Value: XY2qv2+uLiyoN8w7Ey+zR5vsaAWRMZjLkeXnO56CvVg=
TTL: 1800 (or 30 minutes)
```

### 2. DKIM Authentication (3 CNAME Records)

**DKIM Record 1:**
```
Type: CNAME
Name: upepa3ijweasowyzqtt33tq6mcxwax4c._domainkey.retirementadvisorpro.com
Value: upepa3ijweasowyzqtt33tq6mcxwax4c.dkim.amazonses.com
TTL: 1800
```

**DKIM Record 2:**
```
Type: CNAME
Name: 363arxpqukek7rmtuqvuywslumirkdwm._domainkey.retirementadvisorpro.com
Value: 363arxpqukek7rmtuqvuywslumirkdwm.dkim.amazonses.com
TTL: 1800
```

**DKIM Record 3:**
```
Type: CNAME
Name: fk4kehjwrw5f45weci35otjgjaqvsnot._domainkey.retirementadvisorpro.com
Value: fk4kehjwrw5f45weci35otjgjaqvsnot.dkim.amazonses.com
TTL: 1800
```

**Note:** Some DNS providers require you to omit the domain name from the "Name" field. If so, use:
- For TXT: `_amazonses`
- For DKIM: `upepa3ijweasowyzqtt33tq6mcxwax4c._domainkey` (without .retirementadvisorpro.com)

---

## ✅ Verification Checklist

### Step 1: Add DNS Records (10-15 minutes)
- [ ] Log into your DNS provider
- [ ] Add TXT record for domain verification
- [ ] Add 3 CNAME records for DKIM
- [ ] Wait 10-20 minutes for DNS propagation

### Step 2: Check Email Inbox
- [ ] Check inbox for noreply@retirementadvisorpro.com
- [ ] You should receive a verification email from AWS
- [ ] Click the verification link in the email

### Step 3: Verify DNS Records Added (After 20 mins)
```bash
# Check TXT record
dig TXT _amazonses.retirementadvisorpro.com

# Check DKIM records
dig CNAME upepa3ijweasowyzqtt33tq6mcxwax4c._domainkey.retirementadvisorpro.com
dig CNAME 363arxpqukek7rmtuqvuywslumirkdwm._domainkey.retirementadvisorpro.com
dig CNAME fk4kehjwrw5f45weci35otjgjaqvsnot._domainkey.retirementadvisorpro.com
```

### Step 4: Check Verification Status
```bash
# Run this command after DNS records are added (wait 20-30 mins)
aws ses get-identity-verification-attributes --identities retirementadvisorpro.com --region us-east-1

# Look for: "VerificationStatus": "Success"
```

### Step 5: Update Production Environment
```bash
# Add SMTP credentials to your production .env file or secrets manager
EMAIL_HOST_USER=AKIA3RYC52SPQZKDIO7T
EMAIL_HOST_PASSWORD=BE+drxH2k/4moNh6YIvNsEBaCY+B5jZnbGmBG8YiKAco
```

### Step 6: Test Email Sending
```bash
# SSH into production server
python manage.py shell

# Test email
from django.core.mail import send_mail
send_mail(
    'Test Email from SES',
    'This is a test email from AWS SES.',
    'noreply@retirementadvisorpro.com',
    ['your-email@domain.com'],
    fail_silently=False,
)

# Check your inbox!
```

---

## 🎯 Quick Start (For Immediate Testing)

### Option 1: Use Verified Email Address
Once you verify `noreply@retirementadvisorpro.com` (check inbox), you can immediately send emails FROM this address to ANY address.

### Option 2: Test with Django (After adding SMTP credentials)
```python
# In Django shell
from django.core.mail import send_mail

send_mail(
    subject='NSSA Welcome Test',
    message='Testing AWS SES integration for NSSA/Kajabi!',
    from_email='noreply@retirementadvisorpro.com',
    recipient_list=['test@example.com'],
    fail_silently=False,
)
```

---

## 📊 AWS SES Dashboard

**Check your SES stats:**
https://console.aws.amazon.com/ses/home?region=us-east-1#/account

**Monitor:**
- Sending statistics (emails sent, bounces, complaints)
- Reputation metrics
- Sending quota

---

## 🔧 Troubleshooting

### DNS Records Not Showing Up
- Wait 20-30 minutes for DNS propagation
- Check with different DNS checker: https://dnschecker.org/
- Verify you added records to the correct domain

### Email Bouncing
- Check sender email is verified (either domain or specific email)
- Check recipient email is valid
- Check AWS SES bounce notifications

### SMTP Authentication Failed
- Double-check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Ensure you copied the password correctly (case-sensitive)
- Verify IAM user has SES sending permissions

### Rate Limit Exceeded
- Current limit: 200 emails/day, 1 email/second
- Request limit increase in AWS SES console if needed

---

## 📈 Increasing Limits (If Needed)

If you need more than 200 emails/day:

1. Go to: https://console.aws.amazon.com/ses/home?region=us-east-1#/account
2. Click "Request a sending limit increase"
3. Fill out form:
   - New daily sending limit: e.g., 10,000
   - Describe your use case: "Transactional emails for retirement planning SaaS platform (welcome emails, notifications, password resets)"
4. Usually approved within 24-48 hours

---

## 💰 Cost Estimate

**AWS SES Pricing:**
- First 62,000 emails/month: **FREE** (when sending from EC2)
- After: $0.10 per 1,000 emails
- Data transfer: $0.12/GB (negligible for transactional emails)

**For NSSA Integration:**
- Estimated: 100-500 users/month
- Email volume: ~1,000-2,000 emails/month
- **Cost: $0-2/month**

---

## ✅ Next Steps

1. **Add DNS records** (do this now!)
2. **Wait 20-30 minutes** for DNS propagation
3. **Verify email inbox** for noreply@retirementadvisorpro.com
4. **Check verification status** with AWS CLI command above
5. **Add SMTP credentials to production** environment variables
6. **Test email sending** with Django shell
7. **Deploy NSSA/Kajabi integration** (webhook + password setup)

---

## 🆘 Support

**AWS SES Issues:**
- AWS Support Console: https://console.aws.amazon.com/support/
- SES Documentation: https://docs.aws.amazon.com/ses/

**DNS Issues:**
- Contact your domain registrar support
- Use DNS checker: https://dnschecker.org/

**Integration Issues:**
- Check Django logs
- Check AWS SES sending statistics
- Review NSSA_KAJABI_INTEGRATION.md

---

## 📝 Notes

- Account already OUT OF SANDBOX ✅
- Can send to any email address ✅
- SMTP credentials created and ready ✅
- Domain verification pending DNS records
- Email address verification sent to noreply@retirementadvisorpro.com

**Created:** 2025-01-20
**Region:** us-east-1
**Account:** 794038228127
**IAM User:** ses-smtp-user-rapro
