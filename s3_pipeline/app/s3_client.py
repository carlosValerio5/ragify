import boto3
import uuid
from datetime import datetime, UTC
from typing import BinaryIO
from app.config import settings

# Supported file types and their S3 Content-Type mappings
SUPPORTED_EXTENSIONS = ('.txt', '.md', '.pdf')
CONTENT_TYPE_MAP = {
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.pdf': 'application/pdf',
}


def _get_file_type(filename: str) -> tuple[str, str]:
    """Get file extension and content type from filename."""
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    content_type = CONTENT_TYPE_MAP.get(ext, 'application/octet-stream')
    return ext, content_type


def upload_document_to_s3(file: BinaryIO, filename: str) -> dict:
    """
    Upload a document (txt, md, or pdf) to S3 with metadata.

    Args:
        file: File-like object containing document data
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

    # Determine file type and content type from filename
    file_ext, content_type = _get_file_type(filename)

    # Prepare metadata (S3 metadata values must be ASCII strings)
    upload_timestamp = datetime.now(UTC).isoformat() + "Z"
    metadata = {
        'original_filename': filename,
        'upload_timestamp': upload_timestamp,
        'file_extension': file_ext,
        'content_type': content_type,
    }

    # Reset file pointer to beginning
    file.seek(0)

    # Upload to S3
    s3_client.upload_fileobj(
        file,
        settings.s3_bucket_name,
        s3_key,
        ExtraArgs={
            'ContentType': content_type,
            'Metadata': metadata
        }
    )

    return {
        's3_key': s3_key,
        'metadata': metadata
    }


# Backward compatibility alias
upload_pdf_to_s3 = upload_document_to_s3
