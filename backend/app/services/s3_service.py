import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
import uuid
import os
from pathlib import Path

class S3Service:
    def __init__(self):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.AWS_ACCESS_KEY_ID != "placeholder":
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket = settings.AWS_S3_BUCKET
            self.use_local = False
        else:
            # Use local file storage for development
            self.s3_client = None
            self.bucket = None
            self.use_local = True
            self.local_upload_dir = Path("/app/uploads")
            self.local_upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        if self.use_local:
            # Local file storage
            file_id = str(uuid.uuid4())
            file_path = self.local_upload_dir / f"{file_id}_{filename}"
            
            with open(file_path, "wb") as f:
                f.write(file_data)
            
            return f"/uploads/{file_id}_{filename}"
        
        # S3 storage
        if not self.s3_client:
            raise Exception("S3 is not configured")
        
        try:
            file_key = f"uploads/{uuid.uuid4()}/{filename}"
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=file_key,
                Body=file_data,
                ContentType=content_type,
                ACL='public-read'
            )
            return f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        except ClientError as e:
            print(f"S3 upload error: {e}")
            raise Exception("Failed to upload file")
    
    async def delete_file(self, file_url: str):
        if self.use_local:
            # Local file deletion
            filename = file_url.split("/")[-1]
            file_path = self.local_upload_dir / filename
            if file_path.exists():
                file_path.unlink()
            return
        
        if not self.s3_client:
            raise Exception("S3 is not configured")
        
        try:
            file_key = file_url.split(f"{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_key)
        except ClientError as e:
            print(f"S3 delete error: {e}")
            raise Exception("Failed to delete file")
    
    async def generate_presigned_url(self, file_key: str, expiration: int = 3600) -> str:
        if self.use_local:
            # For local files, just return the path
            return f"/uploads/{file_key}"
        
        if not self.s3_client:
            raise Exception("S3 is not configured")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"S3 presigned URL error: {e}")
            raise Exception("Failed to generate presigned URL")
