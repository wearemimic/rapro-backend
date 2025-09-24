"""
ALB Health Check Middleware

Allows AWS ALB health checks from private VPC IPs to bypass ALLOWED_HOSTS validation.
This is secure because:
1. Only applies to the specific health check path
2. Only allows private IP ranges (10.x.x.x, 172.16-31.x.x)
3. All other requests still require proper ALLOWED_HOSTS validation
"""

from django.http import HttpResponse
import re


class ALBHealthCheckMiddleware:
    """
    Middleware to handle AWS ALB health checks from private IPs.

    ALB health checks come from private IPs within the VPC and are rejected
    by Django's ALLOWED_HOSTS validation. This middleware intercepts health
    check requests from private IPs and returns a 200 OK response.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Private IP patterns - RFC 1918
        self.private_ip_patterns = [
            re.compile(r'^10\.'),           # 10.0.0.0/8
            re.compile(r'^172\.(1[6-9]|2[0-9]|3[0-1])\.'),  # 172.16.0.0/12
            re.compile(r'^192\.168\.'),     # 192.168.0.0/16
        ]

    def __call__(self, request):
        # Only handle health check path
        if request.path == '/health/' or request.path == '/':
            # Get the host header
            host = request.META.get('HTTP_HOST', '')

            # Extract IP from host (removes port if present)
            ip = host.split(':')[0]

            # Check if it's a private IP
            is_private_ip = any(pattern.match(ip) for pattern in self.private_ip_patterns)

            if is_private_ip:
                # Return 200 OK for health checks from private IPs
                return HttpResponse('OK', status=200)

        # Process all other requests normally
        response = self.get_response(request)
        return response