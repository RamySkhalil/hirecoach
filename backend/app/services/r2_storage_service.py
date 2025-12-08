"""
Cloudflare R2 Storage Service for file uploads.
Handles CV/resume uploads to R2 bucket.
"""
import os
from typing import Optional, BinaryIO
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    ClientError = Exception
    BotoCoreError = Exception

from app.config import settings


class R2StorageService:
    """Service for uploading files to Cloudflare R2."""
    
    # Allowed file extensions for CVs
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        """Initialize R2 client."""
        if not BOTO3_AVAILABLE:
            raise ValueError("boto3 is required for R2 storage. Install it with: pip install boto3")
        
        self.bucket_name = settings.r2_bucket_name or os.getenv("R2_BUCKET_NAME")
        self.account_id = settings.r2_account_id or os.getenv("R2_ACCOUNT_ID")
        self.access_key_id = settings.r2_access_key_id or os.getenv("R2_ACCESS_KEY_ID")
        self.secret_access_key = settings.r2_secret_access_key or os.getenv("R2_SECRET_ACCESS_KEY")
        self.endpoint_url = settings.r2_endpoint_url or os.getenv("R2_ENDPOINT_URL")
        self.public_url = settings.r2_public_url or os.getenv("R2_PUBLIC_URL")
        
        # Validate configuration
        if not all([self.bucket_name, self.account_id, self.access_key_id, self.secret_access_key]):
            raise ValueError(
                "R2 configuration incomplete. Required: R2_BUCKET_NAME, R2_ACCOUNT_ID, "
                "R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY"
            )
        
        # Initialize S3-compatible client for R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url or f"https://{self.account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name='auto'  # R2 doesn't use regions
        )
    
    def validate_file(self, filename: str, file_size: int) -> tuple[bool, Optional[str]]:
        """
        Validate file before upload.
        
        Returns:
            (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File type not supported. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # Check file size
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size: {self.MAX_FILE_SIZE / 1024 / 1024}MB"
        
        return True, None
    
    def upload_file(
        self,
        file_content: BinaryIO,
        filename: str,
        folder: str = "Applicants",
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload a file to R2.
        
        Args:
            file_content: File-like object (bytes)
            filename: Original filename
            folder: Folder path in bucket (default: "Applicants")
            content_type: MIME type (auto-detected if not provided)
        
        Returns:
            Public URL of uploaded file
        """
        # Generate unique filename to avoid collisions
        file_ext = Path(filename).suffix.lower()
        unique_filename = f"{os.urandom(16).hex()}{file_ext}"
        object_key = f"{folder}/{unique_filename}"
        
        # Auto-detect content type if not provided
        if not content_type:
            content_type_map = {
                ".pdf": "application/pdf",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".doc": "application/msword",
                ".txt": "text/plain"
            }
            content_type = content_type_map.get(file_ext, "application/octet-stream")
        
        try:
            # Upload to R2
            self.s3_client.upload_fileobj(
                file_content,
                self.bucket_name,
                object_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'original_filename': filename
                    }
                }
            )
            
            # Return public URL
            if self.public_url:
                # Custom domain
                return f"{self.public_url.rstrip('/')}/{object_key}"
            else:
                # R2 public URL (requires public bucket or signed URL)
                return f"https://{self.bucket_name}.r2.cloudflarestorage.com/{object_key}"
        
        except ClientError as e:
            raise Exception(f"Failed to upload file to R2: {str(e)}")
        except BotoCoreError as e:
            raise Exception(f"R2 connection error: {str(e)}")
    
    def delete_file(self, object_key: str) -> bool:
        """
        Delete a file from R2.
        
        Args:
            object_key: Full object key (including folder path)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
        except ClientError:
            return False
    
    def get_file_url(self, object_key: str, expires_in: int = 3600) -> str:
        """
        Generate a signed URL for private file access.
        
        Args:
            object_key: Full object key (including folder path)
            expires_in: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Signed URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate signed URL: {str(e)}")


# Singleton instance
_r2_service: Optional[R2StorageService] = None


def get_r2_service() -> Optional[R2StorageService]:
    """
    Get R2 storage service instance.
    Returns None if R2 is not configured (graceful degradation).
    """
    global _r2_service
    
    if _r2_service is None:
        try:
            _r2_service = R2StorageService()
        except ValueError:
            # R2 not configured, return None
            return None
    
    return _r2_service

