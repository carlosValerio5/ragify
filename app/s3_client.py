import boto3
import uuid
from datetime import datetime, UTC
from typing import BinaryIO
from app.config import settings


def upload_pdf_to_s3(file: BinaryIO, filename: str) -> dict:
    """
    Upload a PDF file to S3 with metadata.
    
    Args:
        file: File-like object containing PDF data
        filename: Original filename
        
    Returns:
        dict: Contains s3_key and metadata
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.s3_region
    )
    
    # Generate unique S3 key
    file_uuid = str(uuid.uuid4())
    s3_key = f"documents/{file_uuid}_{filename}"
    
    # Prepare metadata
    upload_timestamp = datetime.now(UTC).isoformat() + "Z"
    metadata = {
        'original_filename': filename,
        'upload_timestamp': upload_timestamp
    }
    
    # Reset file pointer to beginning
    file.seek(0)
    
    # Upload to S3
    s3_client.upload_fileobj(
        file,
        settings.s3_bucket_name,
        s3_key,
        ExtraArgs={
            'ContentType': 'application/pdf',
            'Metadata': metadata
        }
    )
    
    return {
        's3_key': s3_key,
        'metadata': metadata
    }
