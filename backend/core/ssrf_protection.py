"""
SSRF (Server-Side Request Forgery) Protection Module
Validates and sanitizes URLs for external requests
"""

import ipaddress
import re
import socket
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class SSRFProtection:
    """
    Service to prevent SSRF attacks by validating URLs and destinations
    """

    # Blocked IP ranges (private and reserved)
    BLOCKED_IP_RANGES = [
        ipaddress.ip_network('0.0.0.0/8'),        # Current network
        ipaddress.ip_network('10.0.0.0/8'),       # Private
        ipaddress.ip_network('100.64.0.0/10'),    # Shared Address Space
        ipaddress.ip_network('127.0.0.0/8'),      # Loopback
        ipaddress.ip_network('169.254.0.0/16'),   # Link local
        ipaddress.ip_network('172.16.0.0/12'),    # Private
        ipaddress.ip_network('192.0.0.0/24'),     # IETF Protocol Assignments
        ipaddress.ip_network('192.168.0.0/16'),   # Private
        ipaddress.ip_network('198.18.0.0/15'),    # Network benchmark tests
        ipaddress.ip_network('224.0.0.0/4'),      # Multicast
        ipaddress.ip_network('240.0.0.0/4'),      # Reserved
        ipaddress.ip_network('255.255.255.255/32'), # Broadcast
        # IPv6 ranges
        ipaddress.ip_network('::1/128'),          # Loopback
        ipaddress.ip_network('fc00::/7'),         # Unique local
        ipaddress.ip_network('fe80::/10'),        # Link local
        ipaddress.ip_network('ff00::/8'),         # Multicast
    ]

    # Blocked hostnames
    BLOCKED_HOSTNAMES = [
        'localhost',
        'localhost.localdomain',
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        'metadata.google.internal',  # GCP metadata
        'metadata.aws',  # AWS metadata
        '169.254.169.254',  # Cloud metadata IP
    ]

    # Allowed protocols
    ALLOWED_PROTOCOLS = ['http', 'https']

    # Allowed domains for external requests (whitelist)
    ALLOWED_DOMAINS = [
        'auth0.com',
        'stripe.com',
        'googleapis.com',
        'google.com',
        'microsoft.com',
        'outlook.com',
        'office365.com',
        'graph.microsoft.com',
        'login.microsoftonline.com',
    ]

    @classmethod
    def validate_url(cls, url, allow_redirects=False):
        """
        Validate a URL for SSRF protection

        Args:
            url: URL to validate
            allow_redirects: Whether to allow redirects

        Returns:
            tuple (is_safe, sanitized_url)
        """
        if not url:
            return False, None

        try:
            # Parse URL
            parsed = urlparse(url)

            # Check protocol
            if parsed.scheme not in cls.ALLOWED_PROTOCOLS:
                logger.warning(f"Blocked URL with invalid protocol: {parsed.scheme}")
                return False, None

            # Check hostname
            hostname = parsed.hostname
            if not hostname:
                logger.warning("Blocked URL with no hostname")
                return False, None

            # Check against blocked hostnames
            if hostname.lower() in cls.BLOCKED_HOSTNAMES:
                logger.warning(f"Blocked URL with forbidden hostname: {hostname}")
                return False, None

            # Check if hostname is in allowed domains
            if not cls._is_allowed_domain(hostname):
                logger.warning(f"Blocked URL with non-whitelisted domain: {hostname}")
                return False, None

            # Resolve hostname to IP and check
            try:
                # Get IP address
                ip_address = socket.gethostbyname(hostname)
                ip = ipaddress.ip_address(ip_address)

                # Check against blocked IP ranges
                for blocked_range in cls.BLOCKED_IP_RANGES:
                    if ip in blocked_range:
                        logger.warning(f"Blocked URL resolving to private IP: {ip}")
                        return False, None

            except (socket.gaierror, ValueError) as e:
                logger.warning(f"Could not resolve hostname {hostname}: {e}")
                return False, None

            # Additional checks for suspicious patterns
            if cls._contains_suspicious_patterns(url):
                logger.warning(f"Blocked URL with suspicious patterns: {url}")
                return False, None

            # URL is safe
            return True, url

        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False, None

    @classmethod
    def _is_allowed_domain(cls, hostname):
        """
        Check if hostname is in allowed domains

        Args:
            hostname: Hostname to check

        Returns:
            bool: True if allowed
        """
        hostname = hostname.lower()

        # Check exact match or subdomain match
        for allowed_domain in cls.ALLOWED_DOMAINS:
            if hostname == allowed_domain or hostname.endswith(f'.{allowed_domain}'):
                return True

        return False

    @classmethod
    def _contains_suspicious_patterns(cls, url):
        """
        Check for suspicious patterns in URL

        Args:
            url: URL to check

        Returns:
            bool: True if suspicious
        """
        suspicious_patterns = [
            r'@',  # Username in URL (potential bypass)
            r'\[',  # IPv6 literal (often used for bypasses)
            r'0x',  # Hex encoding
            r'0o',  # Octal encoding
            r'%00',  # Null byte
            r'%0d%0a',  # CRLF injection
            r'\.\./',  # Directory traversal
            r'file://',  # File protocol
            r'gopher://',  # Gopher protocol
            r'dict://',  # Dict protocol
            r'ftp://',  # FTP protocol
            r'jar://',  # Java archive
        ]

        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, url_lower):
                return True

        return False

    @classmethod
    def safe_request(cls, url, method='GET', **kwargs):
        """
        Make a safe HTTP request with SSRF protection

        Args:
            url: URL to request
            method: HTTP method
            **kwargs: Additional arguments for requests

        Returns:
            Response object or None if blocked
        """
        import requests

        # Validate URL
        is_safe, sanitized_url = cls.validate_url(url)
        if not is_safe:
            logger.error(f"Blocked unsafe request to: {url}")
            return None

        # Set safe defaults
        kwargs.setdefault('timeout', 10)  # 10 second timeout
        kwargs.setdefault('allow_redirects', False)  # No redirects by default

        # Make request
        try:
            if method == 'GET':
                return requests.get(sanitized_url, **kwargs)
            elif method == 'POST':
                return requests.post(sanitized_url, **kwargs)
            elif method == 'PUT':
                return requests.put(sanitized_url, **kwargs)
            elif method == 'DELETE':
                return requests.delete(sanitized_url, **kwargs)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None


def validate_webhook_url(url):
    """
    Validate a webhook URL for registration

    Args:
        url: Webhook URL to validate

    Returns:
        bool: True if valid
    """
    # Must be HTTPS
    parsed = urlparse(url)
    if parsed.scheme != 'https':
        return False

    # Must not be localhost or private IP
    is_safe, _ = SSRFProtection.validate_url(url)
    return is_safe


def sanitize_redirect_url(url, allowed_hosts):
    """
    Sanitize a redirect URL to prevent open redirects

    Args:
        url: Redirect URL
        allowed_hosts: List of allowed redirect hosts

    Returns:
        Sanitized URL or None if invalid
    """
    if not url:
        return None

    # Parse URL
    parsed = urlparse(url)

    # Check if relative URL (safe)
    if not parsed.netloc:
        return url

    # Check if host is allowed
    if parsed.netloc.lower() in [h.lower() for h in allowed_hosts]:
        return url

    # Invalid redirect
    logger.warning(f"Blocked redirect to unauthorized host: {parsed.netloc}")
    return None