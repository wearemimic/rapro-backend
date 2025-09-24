"""
Mock S3 Service for Local Development
Stores documents locally instead of AWS S3 for testing
"""

import os
import hashlib
import mimetypes
import json
import shutil
from datetime import datetime
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class MockS3Service:
    """
    Mock S3 service that stores files locally for development
    """
    
    def __init__(self):
        """Initialize mock S3 service with local storage"""
        self.storage_path = os.path.join(settings.MEDIA_ROOT, 'documents')
        os.makedirs(self.storage_path, exist_ok=True)
        logger.info(f"Using local storage for documents at: {self.storage_path}")
    
    def _validate_bucket_access(self):
        """Mock validation - always succeeds"""
        return True
    
    def _generate_s3_key(self, filename: str, advisor_id: str, document_type: str = 'general') -> str:
        """Generate a unique storage key for the document"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = os.path.splitext(filename)[1]
        unique_id = uuid4().hex[:8]
        return f"advisors/{advisor_id}/{document_type}/{timestamp}_{unique_id}{file_extension}"
    
    def _calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def upload_document(
        self,
        file_content: bytes,
        filename: str,
        advisor_id: str,
        document_type: str = 'general',
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mock upload document to local storage
        """
        try:
            # Generate storage key
            s3_key = self._generate_s3_key(filename, advisor_id, document_type)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_content)
            
            # Determine content type
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Save file locally
            file_path = os.path.join(self.storage_path, s3_key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Save metadata
            if metadata:
                metadata_path = f"{file_path}.metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f)
            
            logger.info(f"Document uploaded successfully: {s3_key}")
            
            return {
                's3_key': s3_key,
                'file_hash': file_hash,
                'file_size': len(file_content),
                'content_type': content_type,
                'location': file_path,
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            raise
    
    def download_document(self, s3_key: str) -> bytes:
        """
        Mock download document from local storage
        """
        try:
            file_path = os.path.join(self.storage_path, s3_key)
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Document not found: {s3_key}")
            
            with open(file_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to download document {s3_key}: {str(e)}")
            raise
    
    def delete_document(self, s3_key: str) -> bool:
        """
        Mock delete document from local storage
        """
        try:
            file_path = os.path.join(self.storage_path, s3_key)
            metadata_path = f"{file_path}.metadata.json"
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            logger.info(f"Document deleted: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {s3_key}: {str(e)}")
            return False
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        http_method: str = 'get_object'
    ) -> str:
        """
        Generate a mock presigned URL for local files
        """
        # For local development, return a direct URL to the file
        return f"/media/documents/{s3_key}"
    
    def copy_document(self, source_key: str, dest_key: str) -> bool:
        """
        Copy document within local storage
        """
        try:
            source_path = os.path.join(self.storage_path, source_key)
            dest_path = os.path.join(self.storage_path, dest_key)
            
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source document not found: {source_key}")
            
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(source_path, dest_path)
            
            # Copy metadata if exists
            source_metadata = f"{source_path}.metadata.json"
            if os.path.exists(source_metadata):
                dest_metadata = f"{dest_path}.metadata.json"
                shutil.copy2(source_metadata, dest_metadata)
            
            logger.info(f"Document copied from {source_key} to {dest_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy document: {str(e)}")
            return False


# Create singleton instance
_mock_s3_service = None

def get_s3_service():
    """Get or create the mock S3 service instance"""
    global _mock_s3_service
    if _mock_s3_service is None:
        _mock_s3_service = MockS3Service()
    return _mock_s3_service