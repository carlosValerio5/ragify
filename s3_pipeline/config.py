from pydantic_settings import BaseSettings
from typing import Optional
import os
from app.secrets_manager import SecretsManager
from logging import INFO, WARNING, ERROR, CRITICAL

LOG_LEVELS = {
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL
}

class Settings(BaseSettings):
    # Secrets Manager configuration
    secret_name: Optional[str] = None
    secret_region: str = "us-east-1"
    
    # S3 credentials (loaded from secrets manager or env vars)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    s3_region: str = "us-east-1"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    log_level: int = LOG_LEVELS["INFO"]

    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from Secrets Manager or environment variables."""
        # Try Secrets Manager first if secret_name is provided
        if self.secret_name:
            try:
                secrets_manager = SecretsManager(
                    secret_name=self.secret_name,
                    region_name=self.secret_region
                )
                credentials = secrets_manager.get_s3_credentials()
                self.aws_access_key_id = credentials['aws_access_key_id']
                self.aws_secret_access_key = credentials['aws_secret_access_key']
                self.s3_bucket_name = credentials['s3_bucket_name']
                self.s3_region = credentials.get('s3_region', self.s3_region)
                return
            except Exception as e:
                raise ValueError(
                    f"Failed to load credentials from Secrets Manager: {e}"
                ) from e
        
        # Fallback to environment variables
        self.aws_access_key_id = self.aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = self.aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.s3_bucket_name = self.s3_bucket_name or os.getenv('S3_BUCKET_NAME')
        self.s3_region = self.s3_region or os.getenv('S3_REGION', 'us-east-1')
        
        # Validate that all required credentials are present
        if not self.aws_access_key_id:
            raise ValueError("aws_access_key_id is required (set SECRET_NAME or AWS_ACCESS_KEY_ID)")
        if not self.aws_secret_access_key:
            raise ValueError("aws_secret_access_key is required (set SECRET_NAME or AWS_SECRET_ACCESS_KEY)")
        if not self.s3_bucket_name:
            raise ValueError("s3_bucket_name is required (set SECRET_NAME or S3_BUCKET_NAME)")


settings = Settings()
