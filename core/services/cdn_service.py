# core/services/cdn_service.py
"""
CDN integration service for static asset optimization
"""

import os
import hashlib
import logging
from urllib.parse import urljoin
from django.conf import settings
from django.templatetags.static import static
from django.core.files.storage import get_storage_class
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CDNService:
    """
    Service for managing CDN integration and static asset optimization
    """
    
    def __init__(self):
        self.cdn_enabled = getattr(settings, 'CDN_ENABLED', False)
        self.cdn_domain = getattr(settings, 'CDN_DOMAIN', '')
        self.aws_cloudfront_distribution = getattr(settings, 'AWS_CLOUDFRONT_DISTRIBUTION_ID', '')
        self.s3_bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        
        # Initialize S3 client if AWS is configured
        if all([self.s3_bucket, settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY]):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
            )
            
            # CloudFront client for cache invalidation
            if self.aws_cloudfront_distribution:
                self.cloudfront_client = boto3.client(
                    'cloudfront',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
        else:
            self.s3_client = None
            self.cloudfront_client = None
    
    def get_static_url(self, path):
        """
        Get the CDN URL for a static file
        """
        if self.cdn_enabled and self.cdn_domain:
            # Use CDN domain
            return urljoin(f"https://{self.cdn_domain}/", path.lstrip('/'))
        else:
            # Fallback to Django static URL
            return static(path)
    
    def optimize_image(self, image_path, quality=85, format='WEBP'):
        """
        Optimize image for web delivery
        """
        try:
            from PIL import Image
            import io
            
            # Open the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Create optimized version
                output = io.BytesIO()
                
                if format.upper() == 'WEBP':
                    img.save(output, format='WEBP', quality=quality, optimize=True)
                elif format.upper() == 'JPEG':
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                else:
                    img.save(output, format=format, optimize=True)
                
                output.seek(0)
                return output.getvalue()
                
        except ImportError:
            logger.warning("Pillow not installed, image optimization disabled")
            return None
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            return None
    
    def upload_to_cdn(self, file_path, cdn_path, content_type=None):
        """
        Upload file to CDN (S3 + CloudFront)
        """
        if not self.s3_client:
            logger.warning("S3 not configured, skipping CDN upload")
            return False
        
        try:
            # Determine content type
            if not content_type:
                content_type = self._get_content_type(file_path)
            
            # Set cache headers for optimization
            extra_args = {
                'ContentType': content_type,
                'CacheControl': self._get_cache_control(file_path),
                'ACL': 'public-read'
            }
            
            # Add compression for text files
            if content_type.startswith(('text/', 'application/javascript', 'application/json')):
                extra_args['ContentEncoding'] = 'gzip'
                # Gzip the content
                file_content = self._gzip_content(file_path)
                
                # Upload gzipped content
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=cdn_path,
                    Body=file_content,
                    **extra_args
                )
            else:
                # Upload file directly
                self.s3_client.upload_file(
                    file_path,
                    self.s3_bucket,
                    cdn_path,
                    ExtraArgs=extra_args
                )
            
            logger.info(f"Uploaded {file_path} to CDN as {cdn_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload {file_path} to CDN: {str(e)}")
            return False
    
    def invalidate_cache(self, paths):
        """
        Invalidate CloudFront cache for specific paths
        """
        if not self.cloudfront_client or not self.aws_cloudfront_distribution:
            logger.warning("CloudFront not configured, skipping cache invalidation")
            return False
        
        try:
            # Ensure paths start with /
            normalized_paths = [f"/{path.lstrip('/')}" for path in paths]
            
            response = self.cloudfront_client.create_invalidation(
                DistributionId=self.aws_cloudfront_distribution,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(normalized_paths),
                        'Items': normalized_paths
                    },
                    'CallerReference': str(hash(tuple(normalized_paths)))
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            logger.info(f"Created CloudFront invalidation {invalidation_id} for {len(paths)} paths")
            return invalidation_id
            
        except ClientError as e:
            logger.error(f"Failed to invalidate CloudFront cache: {str(e)}")
            return False
    
    def sync_static_files(self):
        """
        Sync all static files to CDN
        """
        if not self.s3_client:
            logger.warning("S3 not configured, cannot sync static files")
            return False
        
        from django.contrib.staticfiles import finders
        from django.core.management import call_command
        import tempfile
        import shutil
        
        try:
            # Collect static files to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Collect static files
                call_command('collectstatic', '--noinput', verbosity=0)
                
                static_root = settings.STATIC_ROOT
                if not static_root or not os.path.exists(static_root):
                    logger.error("STATIC_ROOT not configured or doesn't exist")
                    return False
                
                # Upload all static files
                uploaded_count = 0
                for root, dirs, files in os.walk(static_root):
                    for file in files:
                        local_path = os.path.join(root, file)
                        relative_path = os.path.relpath(local_path, static_root)
                        cdn_path = f"static/{relative_path}".replace('\\', '/')
                        
                        if self.upload_to_cdn(local_path, cdn_path):
                            uploaded_count += 1
                
                logger.info(f"Uploaded {uploaded_count} static files to CDN")
                
                # Invalidate cache for updated files
                if uploaded_count > 0:
                    self.invalidate_cache(['/static/*'])
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to sync static files: {str(e)}")
            return False
    
    def get_asset_hash(self, file_path):
        """
        Generate hash for asset versioning
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # Use SHA256 for content hashing (truncated for CDN cache keys)
                return hashlib.sha256(content).hexdigest()[:16]
        except Exception as e:
            logger.error(f"Failed to generate hash for {file_path}: {str(e)}")
            return None
    
    def _get_content_type(self, file_path):
        """
        Determine content type for file
        """
        import mimetypes
        
        content_type, _ = mimetypes.guess_type(file_path)
        
        # Default to application/octet-stream if unknown
        if not content_type:
            content_type = 'application/octet-stream'
        
        return content_type
    
    def _get_cache_control(self, file_path):
        """
        Determine appropriate cache control headers
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        # Long cache for static assets with hashes
        if ext in ['.css', '.js', '.woff', '.woff2', '.ttf', '.eot']:
            return 'public, max-age=31536000, immutable'  # 1 year
        
        # Medium cache for images
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico']:
            return 'public, max-age=2592000'  # 30 days
        
        # Short cache for HTML and other content
        else:
            return 'public, max-age=3600'  # 1 hour
    
    def _gzip_content(self, file_path):
        """
        Gzip file content for compressed upload
        """
        import gzip
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            return gzip.compress(content)
            
        except Exception as e:
            logger.error(f"Failed to gzip {file_path}: {str(e)}")
            return None


class StaticAssetOptimizer:
    """
    Optimize static assets for production deployment
    """
    
    def __init__(self):
        self.cdn_service = CDNService()
    
    def optimize_css(self, css_content):
        """
        Minify CSS content
        """
        try:
            # Simple CSS minification
            import re
            
            # Remove comments
            css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
            
            # Remove extra whitespace
            css_content = re.sub(r'\s+', ' ', css_content)
            css_content = re.sub(r';\s*}', '}', css_content)
            css_content = re.sub(r'{\s*', '{', css_content)
            css_content = re.sub(r';\s*', ';', css_content)
            
            return css_content.strip()
            
        except Exception as e:
            logger.error(f"CSS optimization failed: {str(e)}")
            return css_content
    
    def optimize_js(self, js_content):
        """
        Minify JavaScript content (basic implementation)
        """
        try:
            # Basic JS minification - for production use a proper minifier
            import re
            
            # Remove single line comments
            js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
            
            # Remove multi-line comments
            js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
            
            # Remove extra whitespace
            js_content = re.sub(r'\s+', ' ', js_content)
            
            return js_content.strip()
            
        except Exception as e:
            logger.error(f"JavaScript optimization failed: {str(e)}")
            return js_content
    
    def create_sprite_sheet(self, image_paths, output_path):
        """
        Create CSS sprite sheet from multiple images
        """
        try:
            from PIL import Image
            
            # Load images
            images = []
            for path in image_paths:
                img = Image.open(path)
                images.append((img, os.path.basename(path)))
            
            # Calculate sprite dimensions
            total_width = sum(img[0].width for img in images)
            max_height = max(img[0].height for img in images)
            
            # Create sprite sheet
            sprite = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))
            
            # Paste images and generate CSS
            css_rules = []
            x_offset = 0
            
            for img, filename in images:
                sprite.paste(img, (x_offset, 0))
                
                # Generate CSS rule
                class_name = os.path.splitext(filename)[0]
                css_rules.append(f"""
                    .sprite-{class_name} {{
                        background-position: -{x_offset}px 0;
                        width: {img.width}px;
                        height: {img.height}px;
                    }}
                """)
                
                x_offset += img.width
            
            # Save sprite sheet
            sprite.save(output_path, format='PNG', optimize=True)
            
            # Generate CSS
            css_content = f"""
                .sprite {{
                    background-image: url('{output_path}');
                    background-repeat: no-repeat;
                    display: inline-block;
                }}
                
                {''.join(css_rules)}
            """
            
            return css_content
            
        except ImportError:
            logger.warning("Pillow not installed, sprite generation disabled")
            return None
        except Exception as e:
            logger.error(f"Sprite generation failed: {str(e)}")
            return None


# Global CDN service instance
cdn_service = CDNService()