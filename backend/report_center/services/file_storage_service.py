"""
Report Center File Storage and CDN Delivery Service
Handles file storage, retrieval, and delivery for generated reports
"""

import os
import logging
import hashlib
import mimetypes
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.urls import reverse

from core.services.s3_service import S3DocumentService
from ..models import Report, ReportTemplate

logger = logging.getLogger(__name__)


class ReportFileStorageService:
    """
    Manages file storage and delivery for Report Center files including
    generated reports, template previews, and chart exports
    """
    
    def __init__(self):
        self.storage_config = getattr(settings, 'REPORT_CENTER_STORAGE', {})
        self.use_s3 = getattr(settings, 'USE_S3_STORAGE', False)
        
        # Initialize S3 service if configured
        if self.use_s3:
            try:
                self.s3_service = S3DocumentService()
                self.s3_available = True
            except Exception as e:
                logger.warning(f"S3 service unavailable, falling back to local storage: {str(e)}")
                self.s3_available = False
        else:
            self.s3_available = False
        
        # Ensure local storage directories exist
        self._ensure_local_directories()
    
    def _ensure_local_directories(self):
        """Ensure all local storage directories exist"""
        
        directories = [
            self.storage_config.get('GENERATED_REPORTS', 
                os.path.join(settings.MEDIA_ROOT, 'report_center/generated_reports/')),
            self.storage_config.get('PDF_REPORTS', 
                os.path.join(settings.MEDIA_ROOT, 'report_center/generated_reports/pdf/')),
            self.storage_config.get('PPTX_REPORTS', 
                os.path.join(settings.MEDIA_ROOT, 'report_center/generated_reports/pptx/')),
            self.storage_config.get('TEMPLATE_PREVIEWS', 
                os.path.join(settings.MEDIA_ROOT, 'report_center/template_previews/')),
            self.storage_config.get('CHART_EXPORTS', 
                os.path.join(settings.MEDIA_ROOT, 'report_center/chart_exports/')),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def store_generated_report(self, report: Report, file_path: str, file_format: str) -> Dict[str, Any]:
        """
        Store generated report file and return access information
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Report file not found: {file_path}")
            
            # Generate storage key
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_extension = 'pdf' if file_format == 'pdf' else 'pptx'
            storage_key = f"reports/{report.created_by.id}/{report.client.id if report.client else 'no-client'}/{report.id}_{timestamp}.{file_extension}"
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_hash = self._calculate_file_hash(file_path)
            
            if self.s3_available:
                # Store in S3
                result = self._store_to_s3(file_path, storage_key, file_format)
                storage_location = 's3'
            else:
                # Store locally
                result = self._store_locally(file_path, storage_key, file_format)
                storage_location = 'local'
            
            if result['success']:
                # Generate access URLs
                access_info = self._generate_access_urls(storage_key, file_format, storage_location)
                
                return {
                    'success': True,
                    'storage_key': storage_key,
                    'storage_location': storage_location,
                    'file_size': file_size,
                    'file_hash': file_hash,
                    'file_format': file_format,
                    'access_urls': access_info,
                    'expires_at': timezone.now() + timedelta(days=30)  # 30-day access
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Report storage failed for report {report.id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _store_to_s3(self, file_path: str, storage_key: str, file_format: str) -> Dict[str, Any]:
        """Store file to S3 bucket"""
        
        try:
            # Determine content type
            content_type = 'application/pdf' if file_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            
            # Upload to S3 with encryption
            with open(file_path, 'rb') as file_data:
                result = self.s3_service.upload_file(
                    file_obj=file_data,
                    key=storage_key,
                    content_type=content_type,
                    metadata={
                        'file_format': file_format,
                        'uploaded_at': timezone.now().isoformat(),
                        'service': 'report_center'
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"S3 storage failed for {storage_key}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _store_locally(self, file_path: str, storage_key: str, file_format: str) -> Dict[str, Any]:
        """Store file to local filesystem"""
        
        try:
            # Determine target directory
            if file_format == 'pdf':
                target_dir = self.storage_config.get('PDF_REPORTS')
            else:
                target_dir = self.storage_config.get('PPTX_REPORTS')
            
            # Generate local path
            local_filename = os.path.basename(storage_key)
            local_path = os.path.join(target_dir, local_filename)
            
            # Copy file to storage location
            import shutil
            shutil.copy2(file_path, local_path)
            
            return {
                'success': True,
                'local_path': local_path,
                'storage_key': storage_key
            }
            
        except Exception as e:
            logger.error(f"Local storage failed for {storage_key}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_access_urls(self, storage_key: str, file_format: str, storage_location: str) -> Dict[str, str]:
        """Generate access URLs for stored files"""
        
        access_urls = {}
        
        try:
            if storage_location == 's3' and self.s3_available:
                # Generate S3 presigned URLs
                access_urls['download'] = self.s3_service.generate_presigned_url(
                    storage_key, 
                    expiration=86400  # 24 hours
                )
                access_urls['view'] = access_urls['download']  # Same for S3
                
            else:
                # Generate local URLs
                media_url = getattr(settings, 'MEDIA_URL', '/media/')
                relative_path = storage_key.replace('reports/', 'report_center/generated_reports/')
                
                access_urls['download'] = urljoin(media_url, relative_path)
                access_urls['view'] = access_urls['download']
            
            # Add API endpoint URLs
            base_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
            access_urls['api_download'] = f"{base_url}/api/report-center/reports/download/{storage_key.split('/')[-1]}/"
            
            return access_urls
            
        except Exception as e:
            logger.error(f"Access URL generation failed for {storage_key}: {str(e)}")
            return {}
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for integrity checking"""
        
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"File hash calculation failed for {file_path}: {str(e)}")
            return ''
    
    def get_file_download_info(self, storage_key: str) -> Dict[str, Any]:
        """
        Get download information for a stored file
        """
        try:
            if self.s3_available:
                # Check if file exists in S3
                try:
                    response = self.s3_service.s3_client.head_object(
                        Bucket=self.s3_service.bucket_name,
                        Key=storage_key
                    )
                    
                    return {
                        'exists': True,
                        'size': response['ContentLength'],
                        'last_modified': response['LastModified'],
                        'content_type': response['ContentType'],
                        'download_url': self.s3_service.generate_presigned_url(storage_key),
                        'storage_location': 's3'
                    }
                except ClientError:
                    return {'exists': False, 'storage_location': 's3'}
            else:
                # Check local filesystem
                local_path = self._get_local_path_from_key(storage_key)
                
                if os.path.exists(local_path):
                    stat = os.stat(local_path)
                    content_type, _ = mimetypes.guess_type(local_path)
                    
                    media_url = getattr(settings, 'MEDIA_URL', '/media/')
                    relative_path = storage_key.replace('reports/', 'report_center/generated_reports/')
                    download_url = urljoin(media_url, relative_path)
                    
                    return {
                        'exists': True,
                        'size': stat.st_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime),
                        'content_type': content_type,
                        'download_url': download_url,
                        'storage_location': 'local'
                    }
                else:
                    return {'exists': False, 'storage_location': 'local'}
            
        except Exception as e:
            logger.error(f"File info retrieval failed for {storage_key}: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
    def _get_local_path_from_key(self, storage_key: str) -> str:
        """Convert storage key to local filesystem path"""
        
        # Remove 'reports/' prefix and add to appropriate directory
        relative_path = storage_key.replace('reports/', '')
        
        if storage_key.endswith('.pdf'):
            base_dir = self.storage_config.get('PDF_REPORTS')
        elif storage_key.endswith('.pptx'):
            base_dir = self.storage_config.get('PPTX_REPORTS')
        else:
            base_dir = self.storage_config.get('GENERATED_REPORTS')
        
        return os.path.join(base_dir, os.path.basename(storage_key))
    
    def cleanup_old_files(self, days_old: int = 30) -> Dict[str, Any]:
        """
        Clean up old report files older than specified days
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days_old)
            cleanup_stats = {
                'files_checked': 0,
                'files_deleted': 0,
                'bytes_freed': 0,
                'errors': []
            }
            
            if self.s3_available:
                # Clean up S3 files
                s3_stats = self._cleanup_s3_files(cutoff_date)
                cleanup_stats.update(s3_stats)
            else:
                # Clean up local files
                local_stats = self._cleanup_local_files(cutoff_date)
                cleanup_stats.update(local_stats)
            
            logger.info(f"File cleanup completed: {cleanup_stats['files_deleted']} files deleted, "
                       f"{cleanup_stats['bytes_freed']} bytes freed")
            
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"File cleanup failed: {str(e)}")
            return {
                'files_checked': 0,
                'files_deleted': 0,
                'bytes_freed': 0,
                'errors': [str(e)]
            }
    
    def _cleanup_s3_files(self, cutoff_date: datetime) -> Dict[str, Any]:
        """Clean up old files from S3"""
        
        stats = {'files_checked': 0, 'files_deleted': 0, 'bytes_freed': 0, 'errors': []}
        
        try:
            # List objects in reports/ prefix
            paginator = self.s3_service.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.s3_service.bucket_name, Prefix='reports/'):
                for obj in page.get('Contents', []):
                    stats['files_checked'] += 1
                    
                    # Check if file is older than cutoff
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date.replace(tzinfo=None):
                        try:
                            # Delete from S3
                            self.s3_service.s3_client.delete_object(
                                Bucket=self.s3_service.bucket_name,
                                Key=obj['Key']
                            )
                            
                            stats['files_deleted'] += 1
                            stats['bytes_freed'] += obj['Size']
                            
                        except Exception as e:
                            stats['errors'].append(f"Failed to delete {obj['Key']}: {str(e)}")
            
            return stats
            
        except Exception as e:
            logger.error(f"S3 cleanup failed: {str(e)}")
            stats['errors'].append(str(e))
            return stats
    
    def _cleanup_local_files(self, cutoff_date: datetime) -> Dict[str, Any]:
        """Clean up old local files"""
        
        stats = {'files_checked': 0, 'files_deleted': 0, 'bytes_freed': 0, 'errors': []}
        
        try:
            # Check each storage directory
            directories = [
                self.storage_config.get('PDF_REPORTS'),
                self.storage_config.get('PPTX_REPORTS'),
                self.storage_config.get('CHART_EXPORTS')
            ]
            
            for directory in directories:
                if not directory or not os.path.exists(directory):
                    continue
                
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    
                    if os.path.isfile(file_path):
                        stats['files_checked'] += 1
                        
                        # Check file age
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if file_mtime < cutoff_date.replace(tzinfo=None):
                            try:
                                file_size = os.path.getsize(file_path)
                                os.remove(file_path)
                                
                                stats['files_deleted'] += 1
                                stats['bytes_freed'] += file_size
                                
                            except Exception as e:
                                stats['errors'].append(f"Failed to delete {file_path}: {str(e)}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Local cleanup failed: {str(e)}")
            stats['errors'].append(str(e))
            return stats
    
    def get_storage_usage_stats(self) -> Dict[str, Any]:
        """
        Get storage usage statistics for Report Center
        """
        try:
            stats = {
                'storage_type': 's3' if self.s3_available else 'local',
                'total_files': 0,
                'total_size_bytes': 0,
                'by_format': {
                    'pdf': {'count': 0, 'size_bytes': 0},
                    'pptx': {'count': 0, 'size_bytes': 0},
                    'charts': {'count': 0, 'size_bytes': 0}
                },
                'by_age': {
                    'last_24h': {'count': 0, 'size_bytes': 0},
                    'last_week': {'count': 0, 'size_bytes': 0},
                    'last_month': {'count': 0, 'size_bytes': 0},
                    'older': {'count': 0, 'size_bytes': 0}
                }
            }
            
            if self.s3_available:
                # Get S3 stats
                s3_stats = self._get_s3_usage_stats()
                stats.update(s3_stats)
            else:
                # Get local stats
                local_stats = self._get_local_usage_stats()
                stats.update(local_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Storage stats calculation failed: {str(e)}")
            return {'error': str(e)}
    
    def _get_s3_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics from S3"""
        
        stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'by_format': {
                'pdf': {'count': 0, 'size_bytes': 0},
                'pptx': {'count': 0, 'size_bytes': 0},
                'charts': {'count': 0, 'size_bytes': 0}
            }
        }
        
        try:
            paginator = self.s3_service.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.s3_service.bucket_name, Prefix='reports/'):
                for obj in page.get('Contents', []):
                    stats['total_files'] += 1
                    stats['total_size_bytes'] += obj['Size']
                    
                    # Categorize by format
                    if obj['Key'].endswith('.pdf'):
                        stats['by_format']['pdf']['count'] += 1
                        stats['by_format']['pdf']['size_bytes'] += obj['Size']
                    elif obj['Key'].endswith('.pptx'):
                        stats['by_format']['pptx']['count'] += 1
                        stats['by_format']['pptx']['size_bytes'] += obj['Size']
                    elif obj['Key'].endswith('.png'):
                        stats['by_format']['charts']['count'] += 1
                        stats['by_format']['charts']['size_bytes'] += obj['Size']
            
            return stats
            
        except Exception as e:
            logger.error(f"S3 stats calculation failed: {str(e)}")
            return stats
    
    def _get_local_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics from local filesystem"""
        
        stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'by_format': {
                'pdf': {'count': 0, 'size_bytes': 0},
                'pptx': {'count': 0, 'size_bytes': 0},
                'charts': {'count': 0, 'size_bytes': 0}
            }
        }
        
        try:
            directories = [
                (self.storage_config.get('PDF_REPORTS'), 'pdf'),
                (self.storage_config.get('PPTX_REPORTS'), 'pptx'),
                (self.storage_config.get('CHART_EXPORTS'), 'charts')
            ]
            
            for directory, format_type in directories:
                if not directory or not os.path.exists(directory):
                    continue
                
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        
                        stats['total_files'] += 1
                        stats['total_size_bytes'] += file_size
                        
                        stats['by_format'][format_type]['count'] += 1
                        stats['by_format'][format_type]['size_bytes'] += file_size
            
            return stats
            
        except Exception as e:
            logger.error(f"Local stats calculation failed: {str(e)}")
            return stats
    
    def create_download_link(self, report: Report, link_expires_hours: int = 24) -> Dict[str, Any]:
        """
        Create secure download link for a report
        """
        try:
            if not report.file_path:
                return {
                    'success': False,
                    'error': 'Report file not available'
                }
            
            # Extract storage key from file path
            storage_key = self._extract_storage_key(report.file_path)
            
            if not storage_key:
                return {
                    'success': False,
                    'error': 'Invalid file path format'
                }
            
            # Get file info
            file_info = self.get_file_download_info(storage_key)
            
            if not file_info.get('exists'):
                return {
                    'success': False,
                    'error': 'Report file not found in storage'
                }
            
            # Generate secure download token (simplified)
            import secrets
            download_token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(hours=link_expires_hours)
            
            # In a production system, you'd store this token in Redis or database
            # For now, we'll include it in the response
            
            return {
                'success': True,
                'download_url': file_info.get('download_url'),
                'download_token': download_token,
                'expires_at': expires_at.isoformat(),
                'file_size': file_info.get('size'),
                'content_type': file_info.get('content_type'),
                'filename': f"{report.title}_{report.id}.{'pdf' if 'pdf' in report.file_path else 'pptx'}"
            }
            
        except Exception as e:
            logger.error(f"Download link creation failed for report {report.id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_storage_key(self, file_path: str) -> Optional[str]:
        """Extract storage key from file path"""
        
        try:
            # For local files, convert to storage key format
            if 'report_center' in file_path:
                # Extract relative path from media directory
                media_root = settings.MEDIA_ROOT
                if file_path.startswith(media_root):
                    relative_path = os.path.relpath(file_path, media_root)
                    # Convert to S3-style key
                    return relative_path.replace('report_center/generated_reports/', 'reports/')
            
            # If it's already a storage key format, return as-is
            if file_path.startswith('reports/'):
                return file_path
            
            return None
            
        except Exception as e:
            logger.error(f"Storage key extraction failed for {file_path}: {str(e)}")
            return None
    
    def store_template_preview(self, template: ReportTemplate, preview_image_path: str) -> Dict[str, Any]:
        """
        Store template preview image
        """
        try:
            if not os.path.exists(preview_image_path):
                raise FileNotFoundError(f"Preview image not found: {preview_image_path}")
            
            # Generate storage key for preview
            storage_key = f"template_previews/{template.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            if self.s3_available:
                # Store in S3
                with open(preview_image_path, 'rb') as file_data:
                    result = self.s3_service.upload_file(
                        file_obj=file_data,
                        key=storage_key,
                        content_type='image/png',
                        metadata={
                            'template_id': str(template.id),
                            'template_name': template.name,
                            'service': 'report_center'
                        }
                    )
                
                if result['success']:
                    preview_url = self.s3_service.generate_presigned_url(storage_key, expiration=86400 * 7)  # 7 days
                    return {
                        'success': True,
                        'storage_key': storage_key,
                        'preview_url': preview_url,
                        'storage_location': 's3'
                    }
                else:
                    return result
            else:
                # Store locally
                preview_dir = self.storage_config.get('TEMPLATE_PREVIEWS')
                local_filename = f"template_{template.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                local_path = os.path.join(preview_dir, local_filename)
                
                import shutil
                shutil.copy2(preview_image_path, local_path)
                
                # Generate URL
                media_url = getattr(settings, 'MEDIA_URL', '/media/')
                preview_url = urljoin(media_url, f'report_center/template_previews/{local_filename}')
                
                return {
                    'success': True,
                    'storage_key': storage_key,
                    'preview_url': preview_url,
                    'local_path': local_path,
                    'storage_location': 'local'
                }
            
        except Exception as e:
            logger.error(f"Template preview storage failed for template {template.id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class CDNDeliveryService:
    """
    Handles CDN delivery and caching for report files
    """
    
    def __init__(self):
        self.cdn_enabled = getattr(settings, 'USE_CDN', False)
        self.cdn_base_url = getattr(settings, 'CDN_BASE_URL', '')
    
    def get_cdn_url(self, storage_key: str) -> Optional[str]:
        """
        Get CDN URL for a stored file
        """
        if not self.cdn_enabled or not self.cdn_base_url:
            return None
        
        try:
            # Construct CDN URL
            cdn_url = urljoin(self.cdn_base_url, storage_key)
            return cdn_url
            
        except Exception as e:
            logger.error(f"CDN URL generation failed for {storage_key}: {str(e)}")
            return None
    
    def invalidate_cdn_cache(self, storage_keys: List[str]) -> Dict[str, Any]:
        """
        Invalidate CDN cache for specified files
        """
        try:
            if not self.cdn_enabled:
                return {
                    'success': True,
                    'message': 'CDN not enabled, no cache to invalidate'
                }
            
            # In a real implementation, this would connect to CloudFront or similar CDN
            # to invalidate specific files
            
            logger.info(f"CDN cache invalidation requested for {len(storage_keys)} files")
            
            return {
                'success': True,
                'invalidated_count': len(storage_keys),
                'storage_keys': storage_keys
            }
            
        except Exception as e:
            logger.error(f"CDN cache invalidation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }