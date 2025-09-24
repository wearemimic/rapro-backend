#!/usr/bin/env python3
"""
Cache Poisoning and DNS Rebinding Security Tests

This script tests for cache poisoning vulnerabilities in CloudFront
and DNS rebinding protections.
"""

import requests
import json
import socket
import time
from urllib.parse import urlparse

def test_cache_poisoning():
    """Test for cache poisoning vulnerabilities"""
    print("\n=== Testing Cache Poisoning Vulnerabilities ===\n")

    test_urls = [
        "https://d1fxppmbbcb093.cloudfront.net/",
        "https://app.retirementadvisorpro.com/",
        "https://staging.retirementadvisorpro.com/"
    ]

    # Headers that could be used for cache poisoning
    poisoning_headers = {
        'X-Forwarded-Host': 'evil.com',
        'X-Forwarded-Scheme': 'nothttps',
        'X-Forwarded-Port': '8080',
        'X-Original-URL': 'http://evil.com',
        'X-Rewrite-URL': '/admin',
        'X-HTTP-Host-Override': 'evil.com',
        'Host': 'evil.com',
    }

    results = []

    for url in test_urls:
        print(f"Testing: {url}")
        for header_name, header_value in poisoning_headers.items():
            try:
                # Send request with poisoning header
                response = requests.get(
                    url,
                    headers={header_name: header_value},
                    timeout=5,
                    allow_redirects=False
                )

                # Check if the header was reflected or cached
                reflected = False
                if 'Location' in response.headers:
                    if header_value in response.headers['Location']:
                        reflected = True
                        print(f"  ⚠️  {header_name}: Reflected in Location header")

                if header_value in response.text[:1000]:  # Check first 1000 chars
                    reflected = True
                    print(f"  ⚠️  {header_name}: Reflected in response body")

                if not reflected:
                    print(f"  ✅ {header_name}: Not reflected")

                results.append({
                    'url': url,
                    'header': header_name,
                    'reflected': reflected,
                    'status_code': response.status_code
                })

            except Exception as e:
                print(f"  ❌ {header_name}: Error - {str(e)}")
                results.append({
                    'url': url,
                    'header': header_name,
                    'error': str(e)
                })

        # Test cache key manipulation
        print("\n  Testing cache key manipulation:")
        try:
            # Test with query parameters
            response1 = requests.get(f"{url}?test=1", timeout=5)
            response2 = requests.get(f"{url}?test=2", timeout=5)

            if response1.headers.get('X-Cache') != response2.headers.get('X-Cache'):
                print("  ✅ Different cache keys for different query params")
            else:
                print("  ⚠️  Same cache key for different query params")

        except Exception as e:
            print(f"  ❌ Cache key test failed: {str(e)}")

        print()

    return results


def test_dns_rebinding():
    """Test for DNS rebinding vulnerabilities"""
    print("\n=== Testing DNS Rebinding Protections ===\n")

    domains = [
        "retirementadvisorpro.com",
        "app.retirementadvisorpro.com",
        "staging.retirementadvisorpro.com"
    ]

    results = []

    for domain in domains:
        print(f"Testing: {domain}")

        try:
            # Resolve the domain
            ip_addresses = socket.gethostbyname_ex(domain)[2]
            print(f"  IP addresses: {ip_addresses}")

            # Check for private IP addresses
            private_ips = []
            for ip in ip_addresses:
                parts = ip.split('.')
                if parts[0] == '10' or \
                   (parts[0] == '172' and 16 <= int(parts[1]) <= 31) or \
                   (parts[0] == '192' and parts[1] == '168') or \
                   parts[0] == '127':
                    private_ips.append(ip)
                    print(f"  ⚠️  Private IP detected: {ip}")

            if not private_ips:
                print(f"  ✅ No private IPs in DNS response")

            # Test for DNS TTL (Time To Live)
            # Low TTL could indicate rebinding vulnerability
            import subprocess
            result = subprocess.run(
                ['dig', '+noall', '+answer', domain],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '\tA\t' in line or '\tAAAA\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            ttl = int(parts[1])
                            if ttl < 60:
                                print(f"  ⚠️  Very low TTL detected: {ttl} seconds")
                            elif ttl < 300:
                                print(f"  ⚠️  Low TTL detected: {ttl} seconds")
                            else:
                                print(f"  ✅ TTL is reasonable: {ttl} seconds")

            # Check Host header validation
            print(f"\n  Testing Host header validation:")

            if ip_addresses:
                # Try to access with IP directly
                try:
                    response = requests.get(
                        f"http://{ip_addresses[0]}",
                        headers={'Host': 'evil.com'},
                        timeout=5,
                        allow_redirects=False
                    )

                    if response.status_code < 400:
                        print(f"  ⚠️  Accepts arbitrary Host header with IP access")
                    else:
                        print(f"  ✅ Rejects arbitrary Host header (status: {response.status_code})")

                except Exception as e:
                    print(f"  ✅ Cannot access directly by IP (good)")

            results.append({
                'domain': domain,
                'ip_addresses': ip_addresses,
                'private_ips': private_ips,
                'protected': len(private_ips) == 0
            })

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append({
                'domain': domain,
                'error': str(e)
            })

        print()

    return results


def test_cdn_security_headers():
    """Test CDN security headers"""
    print("\n=== Testing CDN Security Headers ===\n")

    urls = [
        "https://app.retirementadvisorpro.com/",
        "https://staging.retirementadvisorpro.com/"
    ]

    security_headers = {
        'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
        'X-Content-Type-Options': ['nosniff'],
        'X-XSS-Protection': ['1; mode=block'],
        'Strict-Transport-Security': ['max-age='],
        'Content-Security-Policy': None,  # Just check existence
        'Referrer-Policy': ['no-referrer', 'strict-origin'],
        'Cache-Control': ['no-cache', 'no-store', 'must-revalidate', 'private']
    }

    results = []

    for url in urls:
        print(f"Testing: {url}")

        try:
            response = requests.get(url, timeout=5)
            headers = response.headers

            for header_name, expected_values in security_headers.items():
                if header_name in headers:
                    header_value = headers[header_name]

                    if expected_values is None:
                        print(f"  ✅ {header_name}: Present")
                    else:
                        found = False
                        for expected in expected_values:
                            if expected.lower() in header_value.lower():
                                found = True
                                break

                        if found:
                            print(f"  ✅ {header_name}: {header_value}")
                        else:
                            print(f"  ⚠️  {header_name}: {header_value} (unexpected value)")
                else:
                    print(f"  ❌ {header_name}: Missing")

            # Check cache control
            cache_control = headers.get('Cache-Control', '')
            if 'no-store' in cache_control or 'private' in cache_control:
                print(f"  ✅ Cache-Control prevents caching of sensitive data")
            else:
                print(f"  ⚠️  Cache-Control may allow caching: {cache_control}")

            results.append({
                'url': url,
                'headers': dict(headers),
                'status': 'secure' if 'X-Frame-Options' in headers else 'vulnerable'
            })

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append({
                'url': url,
                'error': str(e)
            })

        print()

    return results


def main():
    """Run all cache and DNS security tests"""
    print("=" * 60)
    print("Cache Poisoning and DNS Security Test Suite")
    print("=" * 60)

    all_results = {}

    # Run cache poisoning tests
    cache_results = test_cache_poisoning()
    all_results['cache_poisoning'] = cache_results

    # Run DNS rebinding tests
    dns_results = test_dns_rebinding()
    all_results['dns_rebinding'] = dns_results

    # Run CDN security header tests
    cdn_results = test_cdn_security_headers()
    all_results['cdn_headers'] = cdn_results

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    # Cache poisoning summary
    vulnerable_cache = [r for r in cache_results if r.get('reflected')]
    if vulnerable_cache:
        print("\n⚠️  Cache Poisoning Vulnerabilities Found:")
        for vuln in vulnerable_cache:
            print(f"  - {vuln['url']}: {vuln['header']}")
    else:
        print("\n✅ No cache poisoning vulnerabilities detected")

    # DNS rebinding summary
    vulnerable_dns = [r for r in dns_results if r.get('private_ips')]
    if vulnerable_dns:
        print("\n⚠️  DNS Rebinding Risks Found:")
        for vuln in vulnerable_dns:
            print(f"  - {vuln['domain']}: Private IPs {vuln['private_ips']}")
    else:
        print("\n✅ No DNS rebinding vulnerabilities detected")

    # CDN headers summary
    missing_headers = []
    for result in cdn_results:
        if 'headers' in result:
            headers = result['headers']
            if 'X-Frame-Options' not in headers:
                missing_headers.append(result['url'])

    if missing_headers:
        print("\n⚠️  Missing security headers on:")
        for url in missing_headers:
            print(f"  - {url}")
    else:
        print("\n✅ Security headers properly configured")

    print("\n" + "=" * 60)

    # Save results
    with open('cache_dns_security_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print("\nDetailed results saved to: cache_dns_security_results.json")

    return 0 if not (vulnerable_cache or vulnerable_dns or missing_headers) else 1


if __name__ == "__main__":
    exit(main())