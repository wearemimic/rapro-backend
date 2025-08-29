"""
Core Services Package

This package contains business logic services for the RetirementAdvisorPro platform,
including AWS S3 integration, document processing, and compliance features.
"""

from .s3_service import get_s3_service

__all__ = ['get_s3_service']