# GoDaddy DNS Setup for AWS SES - Quick Reference

## 📋 DNS Records to Add

Add these **4 DNS records** in GoDaddy DNS Management:

### ✅ Record 1: TXT (Domain Verification)
```
Type:  TXT
Name:  _amazonses
Value: XY2qv2+uLiyoN8w7Ey+zR5vsaAWRMZjLkeXnO56CvVg=
TTL:   1 Hour
```

### ✅ Record 2: CNAME (DKIM #1)
```
Type:  CNAME
Name:  upepa3ijweasowyzqtt33tq6mcxwax4c._domainkey
Value: upepa3ijweasowyzqtt33tq6mcxwax4c.dkim.amazonses.com
TTL:   1 Hour
```

### ✅ Record 3: CNAME (DKIM #2)
```
Type:  CNAME
Name:  363arxpqukek7rmtuqvuywslumirkdwm._domainkey
Value: 363arxpqukek7rmtuqvuywslumirkdwm.dkim.amazonses.com
TTL:   1 Hour
```

### ✅ Record 4: CNAME (DKIM #3)
```
Type:  CNAME
Name:  fk4kehjwrw5f45weci35otjgjaqvsnot._domainkey
Value: fk4kehjwrw5f45weci35otjgjaqvsnot.dkim.amazonses.com
TTL:   1 Hour
```

---

## 🎯 How Your GoDaddy DNS Should Look After Adding

Your DNS records section should show:

| Type  | Name                                            | Value                                           | TTL    |
|-------|------------------------------------------------|------------------------------------------------|--------|
| TXT   | _amazonses                                      | XY2qv2+uLiyoN8w7Ey+zR5vsaAWRMZjLkeXnO56CvVg=  | 1 Hour |
| CNAME | upepa3ijweasowyzqtt33tq6mcxwax4c._domainkey    | upepa3ijweasowyzqtt33tq6mcxwax4c.dkim.amazonses.com | 1 Hour |
| CNAME | 363arxpqukek7rmtuqvuywslumirkdwm._domainkey    | 363arxpqukek7rmtuqvuywslumirkdwm.dkim.amazonses.com | 1 Hour |
| CNAME | fk4kehjwrw5f45weci35otjgjaqvsnot._domainkey    | fk4kehjwrw5f45weci35otjgjaqvsnot.dkim.amazonses.com | 1 Hour |

---

## ⚠️ Important Notes for GoDaddy

1. **Name field:** Enter ONLY the subdomain part, NOT the full domain
   - ✅ Correct: `_amazonses`
   - ❌ Wrong: `_amazonses.retirementadvisorpro.com`

2. **Value field:** Copy-paste exactly as shown (case-sensitive!)

3. **TTL:** Use `1 Hour` or `3600 seconds` (both are the same)

4. **Don't add a period** at the end of values (GoDaddy adds it automatically)

---

## 🔍 Verify DNS Records (After 20-30 mins)

Run this command to check if records are live:

```bash
./check_dns.sh
```

Or check manually:

```bash
# Check TXT record
dig TXT _amazonses.retirementadvisorpro.com +short

# Check DKIM records
dig CNAME upepa3ijweasowyzqtt33tq6mcxwax4c._domainkey.retirementadvisorpro.com +short
dig CNAME 363arxpqukek7rmtuqvuywslumirkdwm._domainkey.retirementadvisorpro.com +short
dig CNAME fk4kehjwrw5f45weci35otjgjaqvsnot._domainkey.retirementadvisorpro.com +short
```

---

## ✅ Check AWS SES Verification Status

After DNS records propagate (20-30 mins), check verification status:

```bash
aws ses get-identity-verification-attributes \
  --identities retirementadvisorpro.com \
  --region us-east-1
```

**Look for:** `"VerificationStatus": "Success"`

---

## 🆘 Troubleshooting

### DNS records not showing up?
- **Wait 20-30 minutes** - DNS propagation takes time
- Use online DNS checker: https://dnschecker.org/
- Clear your local DNS cache: `sudo dscacheutil -flushcache` (Mac)

### GoDaddy not accepting the value?
- Make sure you're using the **Name** field correctly (subdomain only)
- Don't add quotes around the TXT value
- Copy-paste to avoid typos

### Still not verifying after 1 hour?
- Double-check values match exactly (case-sensitive)
- Try deleting and re-adding the records
- Contact GoDaddy support if DNS manager has issues

---

## 📞 GoDaddy Support

If you have issues:
- **Phone:** 480-505-8877
- **Chat:** Available in GoDaddy dashboard
- **Help:** https://www.godaddy.com/help

---

## ✨ Once Verified

After verification succeeds, you can:
- ✅ Send emails from ANY `@retirementadvisorpro.com` address
- ✅ Better email deliverability (DKIM signed)
- ✅ No "via amazonses.com" in email headers
- ✅ Professional appearance for your emails

---

**Estimated Time:**
- Adding records: 5-10 minutes
- DNS propagation: 20-30 minutes
- **Total: 30-40 minutes** ⏱️
