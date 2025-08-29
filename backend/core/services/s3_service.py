"""
AWS S3 Integration Service for Document Management

This service provides secure document storage and management using AWS S3,
with FINRA compliance features including encryption, audit logging, and 
retention policies.
"""

import boto3
import hashlib
import mimetypes
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from botocore.exceptions import ClientError, NoCredentialsError
from uuid import uuid4
import os

logger = logging.getLogger(__name__)


class S3DocumentService:
    """
    Secure S3 document management service with FINRA compliance features
    """
    
    def __init__(self):
        """Initialize S3 client with configuration"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
            )
            self.bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'retirementadvisorpro-documents')
            self.default_encryption = getattr(settings, 'AWS_S3_ENCRYPTION', 'AES256')
            self.max_file_size = getattr(settings, 'MAX_UPLOAD_SIZE', 50 * 1024 * 1024)  # 50MB default
            
            # Validate bucket exists and is accessible
            self._validate_bucket_access()
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Check settings configuration.")
            raise ValidationError("AWS S3 service unavailable: Missing credentials")
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {str(e)}")
            raise ValidationError(f"AWS S3 service unavailable: {str(e)}")
    
    def _validate_bucket_access(self) -> None:
        """Validate that the S3 bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                raise ValidationError(f"S3 bucket '{self.bucket_name}' does not exist")
            elif error_code == 403:
                raise ValidationError(f"Access denied to S3 bucket '{self.bucket_name}'")
            else:
                raise ValidationError(f"Cannot access S3 bucket: {str(e)}")
    
    def generate_secure_key(self, advisor_id: str, filename: str, document_type: str = 'general') -> str:
        """
        Generate secure S3 object key with advisor isolation
        
        Args:
            advisor_id: Unique advisor identifier
            filename: Original filename
            document_type: Category of document
            
        Returns:
            Secure S3 object key path
        """
        # Generate unique identifier to prevent collisions
        unique_id = str(uuid4())
        
        # Extract file extension
        _, ext = os.path.splitext(filename)
        
        # Create hierarchical path for organization
        date_prefix = datetime.now().strftime('%Y/%m')
        secure_filename = f"{unique_id}{ext}"
        
        return f"advisors/{advisor_id}/{document_type}/{date_prefix}/{secure_filename}"
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content for integrity verification"""
        return hashlib.sha256(file_content).hexdigest()
    
    def validate_file(self, file_content: bytes, filename: str) -> Tuple[bool, str]:
        """
        Validate file for security and compliance requirements
        
        Args:
            file_content: File binary content
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(file_content) > self.max_file_size:
            return False, f"File size {len(file_content)} exceeds maximum allowed {self.max_file_size}"
        
        # Check for empty files
        if len(file_content) == 0:
            return False, "File is empty"
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        
        # Define allowed MIME types for financial documents
        allowed_types = [
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/csv',
            'image/jpeg',
            'image/png',
            'image/tiff'
        ]
        
        if mime_type not in allowed_types:
            return False, f"File type {mime_type} not allowed for upload"
        
        # Basic malware detection - check for suspicious patterns
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'onload=',
            b'onclick=',
            b'eval(',
            b'exec(',
            b'<?php'
        ]
        
        file_content_lower = file_content.lower()
        for pattern in suspicious_patterns:
            if pattern in file_content_lower:
                return False, "File contains potentially malicious content"
        
        return True, ""
    
    def upload_document(
        self, 
        file_content: bytes, 
        filename: str, 
        advisor_id: str,
        document_type: str = 'general',
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload document to S3 with security and compliance features
        
        Args:
            file_content: File binary content
            filename: Original filename
            advisor_id: Advisor ID for isolation
            document_type: Document category
            metadata: Additional metadata to store
            
        Returns:
            Dictionary with upload results including S3 key, hash, etc.
        """
        try:
            # Validate file
            is_valid, error_msg = self.validate_file(file_content, filename)
            if not is_valid:
                raise ValidationError(f"File validation failed: {error_msg}")
            
            # Generate secure key and calculate hash
            s3_key = self.generate_secure_key(advisor_id, filename, document_type)
            file_hash = self.calculate_file_hash(file_content)
            
            # Prepare metadata
            upload_metadata = {
                'original-filename': filename,
                'advisor-id': advisor_id,
                'document-type': document_type,
                'file-hash': file_hash,
                'upload-timestamp': timezone.now().isoformat(),
                'content-length': str(len(file_content))
            }
            
            if metadata:
                upload_metadata.update(metadata)
            
            # Get MIME type for proper content type
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Upload to S3 with encryption
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=upload_metadata,
                ServerSideEncryption=self.default_encryption,
                StorageClass='STANDARD_IA'  # Cost-effective for infrequently accessed documents
            )
            
            # Get file info for response
            file_size = len(file_content)
            
            logger.info(f"Successfully uploaded document {filename} to S3 key {s3_key}")
            
            return {
                's3_key': s3_key,
                'file_hash': file_hash,
                'file_size': file_size,
                'content_type': content_type,
                'upload_timestamp': timezone.now(),
                'metadata': upload_metadata
            }
            
        except ClientError as e:
            error_msg = f"AWS S3 error during upload: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during document upload: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
    
    def download_document(self, s3_key: str, advisor_id: str) -> Tuple[bytes, Dict[str, Any]]:
        """
        Download document from S3 with advisor access control
        
        Args:
            s3_key: S3 object key
            advisor_id: Advisor ID for access validation
            
        Returns:
            Tuple of (file_content, metadata)
        """
        try:
            # Verify advisor has access to this document
            if not s3_key.startswith(f'advisors/{advisor_id}/'):
                raise ValidationError("Access denied: Document does not belong to advisor")
            
            # Download object
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            
            file_content = response['Body'].read()
            metadata = response.get('Metadata', {})
            
            # Verify file integrity if hash is available
            stored_hash = metadata.get('file-hash')
            if stored_hash:
                calculated_hash = self.calculate_file_hash(file_content)
                if stored_hash != calculated_hash:
                    logger.warning(f"File integrity check failed for {s3_key}")
                    raise ValidationError("File integrity verification failed")
            
            logger.info(f"Successfully downloaded document from S3 key {s3_key}")
            
            return file_content, {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'metadata': metadata
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise ValidationError("Document not found")
            else:
                error_msg = f"AWS S3 error during download: {str(e)}"
                logger.error(error_msg)
                raise ValidationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during document download: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
    
    def delete_document(self, s3_key: str, advisor_id: str) -> bool:
        """
        Delete document from S3 with advisor access control
        
        Args:
            s3_key: S3 object key
            advisor_id: Advisor ID for access validation
            
        Returns:
            True if successfully deleted
        """
        try:
            # Verify advisor has access to this document
            if not s3_key.startswith(f'advisors/{advisor_id}/'):
                raise ValidationError("Access denied: Document does not belong to advisor")
            
            # Delete object
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            
            logger.info(f"Successfully deleted document from S3 key {s3_key}")
            return True
            
        except ClientError as e:
            error_msg = f"AWS S3 error during deletion: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during document deletion: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
    
    def generate_presigned_url(
        self, 
        s3_key: str, 
        advisor_id: str, 
        expiration: int = 3600,
        download: bool = True
    ) -> str:
        """
        Generate presigned URL for secure document access
        
        Args:
            s3_key: S3 object key
            advisor_id: Advisor ID for access validation
            expiration: URL expiration time in seconds (default 1 hour)
            download: Whether URL is for download (True) or upload (False)
            
        Returns:
            Presigned URL string
        """
        try:
            # Verify advisor has access to this document
            if not s3_key.startswith(f'advisors/{advisor_id}/'):
                raise ValidationError("Access denied: Document does not belong to advisor")
            
            # Generate presigned URL
            if download:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=expiration
                )
            else:
                url = self.s3_client.generate_presigned_url(
                    'put_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=expiration
                )
            
            logger.info(f"Generated presigned URL for S3 key {s3_key}")
            return url
            
        except ClientError as e:
            error_msg = f"AWS S3 error generating presigned URL: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error generating presigned URL: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
    
    def list_documents(
        self, 
        advisor_id: str, 
        document_type: Optional[str] = None,
        prefix: Optional[str] = None,
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List documents for an advisor with optional filtering
        
        Args:
            advisor_id: Advisor ID for filtering
            document_type: Optional document type filter
            prefix: Optional additional prefix filter
            max_keys: Maximum number of keys to return
            
        Returns:
            List of document information dictionaries
        """
        try:
            # Build prefix for advisor isolation
            base_prefix = f'advisors/{advisor_id}/'
            if document_type:
                base_prefix += f'{document_type}/'
            if prefix:
                base_prefix += prefix
            
            # List objects
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=base_prefix,
                MaxKeys=max_keys
            )
            
            documents = []
            for obj in response.get('Contents', []):
                # Get object metadata
                try:
                    head_response = self.s3_client.head_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    metadata = head_response.get('Metadata', {})
                except ClientError:
                    metadata = {}
                
                documents.append({
                    's3_key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"'),
                    'storage_class': obj.get('StorageClass', 'STANDARD'),
                    'original_filename': metadata.get('original-filename', 'Unknown'),
                    'document_type': metadata.get('document-type', 'general'),
                    'file_hash': metadata.get('file-hash'),
                    'metadata': metadata
                })
            
            logger.info(f"Listed {len(documents)} documents for advisor {advisor_id}")
            return documents
            
        except ClientError as e:
            error_msg = f"AWS S3 error listing documents: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error listing documents: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
    
    def get_storage_stats(self, advisor_id: str) -> Dict[str, Any]:
        """
        Get storage statistics for an advisor
        
        Args:
            advisor_id: Advisor ID
            
        Returns:
            Dictionary with storage statistics
        """
        try:
            documents = self.list_documents(advisor_id)
            
            total_size = sum(doc['size'] for doc in documents)
            total_documents = len(documents)
            
            # Group by document type
            type_stats = {}
            for doc in documents:
                doc_type = doc['document_type']
                if doc_type not in type_stats:
                    type_stats[doc_type] = {'count': 0, 'size': 0}
                type_stats[doc_type]['count'] += 1
                type_stats[doc_type]['size'] += doc['size']
            
            return {
                'total_documents': total_documents,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'type_breakdown': type_stats,
                'updated_at': timezone.now()
            }
            
        except Exception as e:
            error_msg = f"Error calculating storage stats: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)


# Global instance for use throughout the application - initialized lazily
s3_service = None

def get_s3_service():
    """Get S3 service instance with lazy initialization"""
    global s3_service
    if s3_service is None:
        # Check if AWS credentials are configured
        aws_key = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
        aws_secret = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
        
        if aws_key and aws_secret:
            # Use real S3 service if credentials are available
            try:
                s3_service = S3DocumentService()
                logger.info("Using AWS S3 service for document storage")
            except Exception as e:
                logger.warning(f"Failed to initialize S3 service, falling back to mock: {e}")
                from .mock_s3_service import MockS3Service
                s3_service = MockS3Service()
        else:
            # Use mock service for local development
            logger.info("AWS credentials not configured, using mock S3 service for local storage")
            from .mock_s3_service import MockS3Service
            s3_service = MockS3Service()
    
    return s3_service