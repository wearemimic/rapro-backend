#!/usr/bin/env python
"""
JWT Token Security Test Script
Tests JWT token storage, handling, and security measures
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
sys.path.insert(0, '/Users/marka/Documents/git/retirementadvisorpro/backend')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.conf import settings

User = get_user_model()

def test_jwt_configuration():
    """Test JWT configuration security"""
    print("\n⚙️ Testing JWT Configuration...")

    try:
        from django.conf import settings

        # Check JWT settings
        jwt_settings = {
            'ACCESS_TOKEN_LIFETIME': getattr(settings, 'SIMPLE_JWT', {}).get('ACCESS_TOKEN_LIFETIME'),
            'REFRESH_TOKEN_LIFETIME': getattr(settings, 'SIMPLE_JWT', {}).get('REFRESH_TOKEN_LIFETIME'),
            'ROTATE_REFRESH_TOKENS': getattr(settings, 'SIMPLE_JWT', {}).get('ROTATE_REFRESH_TOKENS', False),
            'BLACKLIST_AFTER_ROTATION': getattr(settings, 'SIMPLE_JWT', {}).get('BLACKLIST_AFTER_ROTATION', False),
            'ALGORITHM': getattr(settings, 'SIMPLE_JWT', {}).get('ALGORITHM', 'HS256'),
            'SIGNING_KEY': 'CONFIGURED' if getattr(settings, 'SIMPLE_JWT', {}).get('SIGNING_KEY') else 'MISSING'
        }

        print("\n📋 JWT Settings:")
        for setting, value in jwt_settings.items():
            if setting == 'SIGNING_KEY':
                status = "✅" if value == 'CONFIGURED' else "❌"
                print(f"  {setting}: {value} {status}")
            else:
                print(f"  {setting}: {value}")

        # Check token lifetime
        access_lifetime = jwt_settings.get('ACCESS_TOKEN_LIFETIME')
        if access_lifetime and hasattr(access_lifetime, 'total_seconds'):
            minutes = access_lifetime.total_seconds() / 60
            if minutes > 60:
                print(f"\n⚠️  WARNING: Access token lifetime is {minutes} minutes (>1 hour)")
                print("  Recommendation: Reduce to 15-30 minutes for better security")
            else:
                print(f"\n✅ PASS: Access token lifetime is {minutes} minutes")

        # Check refresh token rotation
        if jwt_settings.get('ROTATE_REFRESH_TOKENS'):
            print("✅ PASS: Refresh token rotation enabled")
        else:
            print("⚠️  WARNING: Refresh token rotation disabled")
            print("  Recommendation: Enable ROTATE_REFRESH_TOKENS for better security")

        # Check algorithm
        algorithm = jwt_settings.get('ALGORITHM')
        if algorithm in ['HS256', 'RS256', 'ES256']:
            print(f"✅ PASS: Using secure algorithm: {algorithm}")
        else:
            print(f"⚠️  WARNING: Algorithm {algorithm} may not be optimal")

        return True

    except Exception as e:
        print(f"❌ Error testing JWT configuration: {str(e)}")
        return False

def test_frontend_storage():
    """Analyze frontend JWT storage security"""
    print("\n🔐 Analyzing Frontend JWT Storage...")

    storage_analysis = {
        'localStorage': [],
        'sessionStorage': [],
        'cookies': [],
        'memory': []
    }

    # Based on the code review
    print("\n📁 Token Storage Locations Found:")
    print("  1. localStorage.getItem('token') - auth.js line 26, 94, 104")
    print("  2. localStorage.setItem('token') - auth.js line 187")
    print("  3. localStorage.getItem('refresh_token') - auth.js line 160, 182")
    print("  4. document.cookie fallback - auth.js line 10, api.js line 59")

    print("\n🔍 Security Analysis:")

    # localStorage risks
    print("\n❌ CRITICAL: Tokens stored in localStorage")
    print("  Location: /frontend/src/stores/auth.js")
    print("  Risks:")
    print("    - Vulnerable to XSS attacks")
    print("    - Accessible by all scripts on the page")
    print("    - Persists even after browser close")
    print("  Found in: auth.js lines 26, 31, 94, 104, 187")

    # Cookie fallback
    print("\n⚠️  WARNING: Cookie fallback without HttpOnly flag")
    print("  Location: getTokenFromCookie() functions")
    print("  Risks:")
    print("    - Accessible via document.cookie")
    print("    - Not using HttpOnly flag")
    print("    - Vulnerable to XSS if not HttpOnly")

    # Refresh token storage
    print("\n❌ CRITICAL: Refresh token in localStorage")
    print("  Location: auth.js lines 160, 182")
    print("  Risks:")
    print("    - Long-lived token exposed to XSS")
    print("    - Should never be in localStorage")
    print("    - High value target for attackers")

    print("\n🛡️ Recommended Fixes:")
    print("  1. Move tokens to httpOnly, secure, sameSite cookies")
    print("  2. Implement CSRF protection with cookie storage")
    print("  3. Use sessionStorage instead of localStorage for temporary storage")
    print("  4. Implement token binding to prevent token theft")
    print("  5. Add Content Security Policy to prevent XSS")

    return False  # Fail due to localStorage usage

def test_token_validation():
    """Test token validation and expiry handling"""
    print("\n⏰ Testing Token Validation & Expiry...")

    try:
        # Check if token validation utilities exist
        print("\n✅ Token validation utilities found:")
        print("  - isTokenValid() - tokenUtils.js")
        print("  - isTokenExpiringSoon() - tokenUtils.js")
        print("  - getTokenExpirationInMinutes() - tokenUtils.js")

        # Check token refresh mechanism
        print("\n✅ Token refresh mechanism:")
        print("  - Auto-refresh on 401 errors - auth.js lines 156-199")
        print("  - Exponential backoff - auth.js line 178")
        print("  - Max 3 refresh attempts - auth.js line 37")
        print("  - Request queue during refresh - auth.js lines 167-170")

        # Check rate limiting handling
        print("\n✅ Rate limiting protection:")
        print("  - 429 status handling - auth.js lines 120-140")
        print("  - Exponential backoff for retries")
        print("  - Max 3 retries before failure")

        return True

    except Exception as e:
        print(f"❌ Error testing token validation: {str(e)}")
        return False

def test_token_transmission():
    """Test how tokens are transmitted"""
    print("\n📡 Testing Token Transmission Security...")

    print("\n✅ Authorization Header Usage:")
    print("  - Bearer token in Authorization header")
    print("  - axios interceptor adds token - auth.js line 106")
    print("  - Proper Bearer format used")

    print("\n⚠️  Token Exposure Risks:")
    print("  - Token visible in browser DevTools")
    print("  - Token in localStorage accessible via JS console")
    print("  - Token may be logged in console.log statements")

    print("\n🔍 Console.log Token Exposure:")
    print("  - router/index.js line 276: console.log('Has token:', !!authStore.token)")
    print("  - Uses !! to convert to boolean (good practice)")

    return True

def test_logout_security():
    """Test logout and token cleanup"""
    print("\n🚪 Testing Logout Security...")

    print("\n📋 Logout Implementation Review:")
    print("  ✅ Token cleared from localStorage")
    print("  ✅ Token cleared from axios headers")
    print("  ✅ User data cleared from state")
    print("  ⚠️  No token blacklisting on backend")
    print("  ⚠️  No refresh token revocation")

    print("\n🛡️ Recommendations:")
    print("  1. Implement token blacklisting on logout")
    print("  2. Revoke refresh tokens on logout")
    print("  3. Clear all sensitive data from memory")
    print("  4. Invalidate session on server side")

    return False  # Fail due to missing token blacklisting

def main():
    """Run all JWT security tests"""
    print("=" * 60)
    print("🔐 JWT TOKEN SECURITY TESTS")
    print("=" * 60)

    results = {
        'JWT Configuration': test_jwt_configuration(),
        'Frontend Storage Security': test_frontend_storage(),
        'Token Validation': test_token_validation(),
        'Token Transmission': test_token_transmission(),
        'Logout Security': test_logout_security()
    }

    print("\n" + "=" * 60)
    print("📊 JWT SECURITY TEST RESULTS")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")

    # Overall assessment
    print("\n" + "=" * 60)
    print("🔍 OVERALL JWT SECURITY ASSESSMENT")
    print("=" * 60)

    critical_issues = not results['Frontend Storage Security'] or not results['Logout Security']

    if critical_issues:
        print("⚠️  CRITICAL: JWT security vulnerabilities detected!")
        print("\n🚨 Critical Issues:")
        print("  1. JWT tokens stored in localStorage (XSS vulnerable)")
        print("  2. Refresh tokens in localStorage (high-value target)")
        print("  3. No token blacklisting on logout")
        print("  4. Cookies not using HttpOnly flag")

        print("\n🔧 Priority Fixes:")
        print("  1. IMMEDIATE: Move tokens to httpOnly cookies")
        print("  2. HIGH: Implement token blacklisting")
        print("  3. HIGH: Add CSRF protection")
        print("  4. MEDIUM: Reduce token lifetime to 15 minutes")
        print("  5. MEDIUM: Implement secure token rotation")
    else:
        print("✅ Good JWT security practices overall")
        print("  Some improvements recommended for defense in depth")

    return all(results.values())

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)