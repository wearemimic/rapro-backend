#!/bin/bash
# Script to check if AWS SES DNS records are properly configured

echo "🔍 Checking AWS SES DNS Records for retirementadvisorpro.com"
echo "============================================================"
echo ""

echo "1️⃣ Checking TXT Record (Domain Verification)..."
echo "Expected: XY2qv2+uLiyoN8w7Ey+zR5vsaAWRMZjLkeXnO56CvVg="
echo "Actual:"
dig TXT _amazonses.retirementadvisorpro.com +short
echo ""

echo "2️⃣ Checking DKIM CNAME Record #1..."
echo "Expected: upepa3ijweasowyzqtt33tq6mcxwax4c.dkim.amazonses.com"
echo "Actual:"
dig CNAME upepa3ijweasowyzqtt33tq6mcxwax4c._domainkey.retirementadvisorpro.com +short
echo ""

echo "3️⃣ Checking DKIM CNAME Record #2..."
echo "Expected: 363arxpqukek7rmtuqvuywslumirkdwm.dkim.amazonses.com"
echo "Actual:"
dig CNAME 363arxpqukek7rmtuqvuywslumirkdwm._domainkey.retirementadvisorpro.com +short
echo ""

echo "4️⃣ Checking DKIM CNAME Record #3..."
echo "Expected: fk4kehjwrw5f45weci35otjgjaqvsnot.dkim.amazonses.com"
echo "Actual:"
dig CNAME fk4kehjwrw5f45weci35otjgjaqvsnot._domainkey.retirementadvisorpro.com +short
echo ""

echo "============================================================"
echo "ℹ️  If records show up correctly, AWS will verify them automatically"
echo "ℹ️  Check verification status with:"
echo "    aws ses get-identity-verification-attributes --identities retirementadvisorpro.com --region us-east-1"
echo ""
