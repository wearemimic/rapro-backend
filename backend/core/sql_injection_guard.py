"""
SQL Injection Prevention Guard
Provides middleware and utilities to prevent SQL injection attacks
"""

import re
import logging
from django.core.exceptions import SuspiciousOperation
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SQLInjectionGuardMiddleware(MiddlewareMixin):
    """
    Middleware to detect and prevent SQL injection attempts in request parameters
    """

    # Common SQL injection patterns
    SQL_PATTERNS = [
        # SQL keywords that shouldn't appear in normal input
        r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute|script|javascript)\b',
        # Common SQL injection techniques
        r'(\-\-|\/\*|\*\/|xp_|sp_|0x)',
        # SQL functions that are commonly exploited
        r'\b(concat|char|ascii|substring|length|md5|sha1|sha2|benchmark|sleep|load_file)\b',
        # Hex encoding attempts
        r'0x[0-9a-f]+',
        # Multiple spaces (often used to bypass filters)
        r'\s{2,}',
        # SQL operators
        r'(\|\||&&|!=|<>)',
        # Suspicious comment patterns
        r'(#|\-\-\+|\/\*!\d+)',
        # Time-based blind SQL injection
        r'\b(waitfor|delay|pg_sleep)\b',
        # Stacked queries
        r';\s*(select|insert|update|delete|drop)',
    ]

    # Compile patterns for efficiency
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in SQL_PATTERNS]

    def process_request(self, request):
        """Check all request parameters for SQL injection attempts"""

        # Skip checking for trusted paths (admin, static files, etc.)
        trusted_paths = ['/static/', '/media/', '/admin/']
        if any(request.path.startswith(path) for path in trusted_paths):
            return None

        # Check GET parameters
        for key, value in request.GET.items():
            if self._is_sql_injection_attempt(str(value)):
                logger.error(f"SQL injection attempt detected in GET parameter '{key}': {value[:100]}")
                raise SuspiciousOperation(f"Potential SQL injection detected in parameter: {key}")

        # Check POST parameters
        if request.method == 'POST' and hasattr(request, 'POST'):
            for key, value in request.POST.items():
                if self._is_sql_injection_attempt(str(value)):
                    logger.error(f"SQL injection attempt detected in POST parameter '{key}': {value[:100]}")
                    raise SuspiciousOperation(f"Potential SQL injection detected in parameter: {key}")

        return None

    def _is_sql_injection_attempt(self, value):
        """Check if a value contains SQL injection patterns"""
        if not value:
            return False

        # Normalize the value (lowercase, remove excessive whitespace)
        normalized = ' '.join(value.lower().split())

        # Check against SQL patterns
        for pattern in self.compiled_patterns:
            if pattern.search(normalized):
                return True

        # Check for encoded characters that might be SQL
        if self._contains_encoded_sql(value):
            return True

        return False

    def _contains_encoded_sql(self, value):
        """Check for encoded SQL injection attempts"""
        # Check for URL encoded SQL keywords
        url_encoded_patterns = [
            '%27',  # single quote
            '%22',  # double quote
            '%3B',  # semicolon
            '%2D%2D',  # --
            '%23',  # #
            '%2F%2A',  # /*
        ]

        for pattern in url_encoded_patterns:
            if pattern in value:
                return True

        # Check for HTML entity encoded SQL
        html_encoded_patterns = [
            '&quot;',
            '&#39;',
            '&#x27;',
            '&lt;script',
        ]

        for pattern in html_encoded_patterns:
            if pattern.lower() in value.lower():
                return True

        return False


class SecureQueryBuilder:
    """
    Helper class to build secure parameterized queries
    """

    @staticmethod
    def sanitize_identifier(identifier):
        """
        Sanitize database identifiers (table names, column names)
        Only allows alphanumeric characters and underscores
        """
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', identifier):
            raise ValueError(f"Invalid identifier: {identifier}")
        return identifier

    @staticmethod
    def build_where_clause(conditions, operator='AND'):
        """
        Build a secure WHERE clause with parameterized values

        Args:
            conditions: dict of column_name: value pairs
            operator: 'AND' or 'OR' to join conditions

        Returns:
            tuple of (where_clause, params)
        """
        if not conditions:
            return '', []

        clauses = []
        params = []

        for column, value in conditions.items():
            # Sanitize column name
            safe_column = SecureQueryBuilder.sanitize_identifier(column)

            if value is None:
                clauses.append(f"{safe_column} IS NULL")
            elif isinstance(value, (list, tuple)):
                placeholders = ', '.join(['%s'] * len(value))
                clauses.append(f"{safe_column} IN ({placeholders})")
                params.extend(value)
            else:
                clauses.append(f"{safe_column} = %s")
                params.append(value)

        where_clause = f" {operator} ".join(clauses)
        return where_clause, params

    @staticmethod
    def execute_safe_query(query_template, params=None):
        """
        Execute a parameterized query safely

        Args:
            query_template: SQL query with %s placeholders
            params: tuple or list of parameters

        Returns:
            Query results
        """
        with connection.cursor() as cursor:
            cursor.execute(query_template, params or [])
            return cursor.fetchall()


def validate_input_type(value, expected_type, field_name):
    """
    Validate that input matches expected type

    Args:
        value: Input value to validate
        expected_type: Expected Python type
        field_name: Name of field for error messages

    Raises:
        ValueError: If type doesn't match
    """
    if not isinstance(value, expected_type):
        raise ValueError(f"Invalid type for {field_name}: expected {expected_type.__name__}, got {type(value).__name__}")
    return value


def escape_like_pattern(pattern):
    """
    Escape special characters in LIKE patterns

    Args:
        pattern: LIKE pattern to escape

    Returns:
        Escaped pattern safe for use in LIKE queries
    """
    # Escape special LIKE characters
    pattern = pattern.replace('\\', '\\\\')
    pattern = pattern.replace('%', '\\%')
    pattern = pattern.replace('_', '\\_')
    pattern = pattern.replace('[', '\\[')
    return pattern


def validate_sort_column(column, allowed_columns):
    """
    Validate that a sort column is in the allowed list

    Args:
        column: Column name to sort by
        allowed_columns: List of allowed column names

    Returns:
        Validated column name

    Raises:
        ValueError: If column not in allowed list
    """
    if column not in allowed_columns:
        raise ValueError(f"Invalid sort column: {column}")
    return column