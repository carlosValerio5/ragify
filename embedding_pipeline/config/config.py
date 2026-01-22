"""Configuration settings for the embedding pipeline."""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from logging import INFO, WARNING, ERROR, CRITICAL
import logging

logger = logging.getLogger(__name__)

LOG_LEVELS = {
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL
}


class Settings(BaseSettings):
    """Settings for the embedding pipeline service."""
    
    # Secrets Manager configuration
    secret_name: Optional[str] = None
    secret_region: str = "us-east-1"
    secrets_manager: Optional[object] = None  # SecretsManagerPort instance (injected via kwargs)
    secrets_manager: Optional[object] = None  # SecretsManagerPort instance (injected)
    
    # AWS credentials (S3 and SQS)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # SQS configuration
    sqs_queue_url: Optional[str] = None
    sqs_dlq_url: Optional[str] = None
    
    # S3 configuration
    s3_bucket_name: Optional[str] = None
    
    # Pinecone configuration
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = None
    pinecone_dimension: int = 256  # potion-base-4M produces 256-dimensional vectors
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    
    # Polling configuration
    polling_interval: int = 5  # seconds
    max_messages_per_poll: int = 10
    max_retries: int = 3
    
    # Text splitting configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Embedding model configuration
    embedding_model_name: str = "minishlab/potion-base-4M"
    
    # FastAPI configuration
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
        self._load_from_env()
        self._validate()
    
    def _load_credentials(self):
        """Load credentials from Secrets Manager or environment variables."""
        # Try Secrets Manager first if secret_name is provided
        if self.secret_name:
            try:
                # Use injected secrets_manager if provided, otherwise create AWS adapter
                if self.secrets_manager is None:
                    # Lazy import to avoid circular dependencies
                    import sys
                    import os
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
                    from src.embedding_service.adapters.output.secrets_manager_adapter import AWSSecretsManagerAdapter
                    secrets_manager = AWSSecretsManagerAdapter(
                        secret_name=self.secret_name,
                        region_name=self.secret_region
                    )
                else:
                    secrets_manager = self.secrets_manager
                
                credentials = secrets_manager.get_embedding_pipeline_credentials()
                
                # Set credentials from Secrets Manager
                self.aws_access_key_id = credentials.get('aws_access_key_id')
                self.aws_secret_access_key = credentials.get('aws_secret_access_key')
                self.aws_region = credentials.get('aws_region', self.aws_region)
                self.sqs_queue_url = credentials.get('sqs_queue_url')
                self.sqs_dlq_url = credentials.get('sqs_dlq_url')
                self.s3_bucket_name = credentials.get('s3_bucket_name') or self.s3_bucket_name
                self.pinecone_api_key = credentials.get('pinecone_api_key')
                self.pinecone_index_name = credentials.get('pinecone_index_name')
                
                return
            except Exception as e:
                logger.warning(
                    f"Failed to load credentials from Secrets Manager: {e}. "
                    "Falling back to environment variables."
                )
        
        # Fallback to environment variables (handled in _load_from_env)
    
    def _load_from_env(self):
        """Load values from environment variables if not set."""
        self.secret_name = self.secret_name or os.getenv('SECRET_NAME')
        self.secret_region = self.secret_region or os.getenv('SECRET_REGION', 'us-east-1')
        
        self.aws_access_key_id = self.aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = self.aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = self.aws_region or os.getenv('AWS_REGION', 'us-east-1')
        
        self.sqs_queue_url = self.sqs_queue_url or os.getenv('SQS_QUEUE_URL')
        self.sqs_dlq_url = self.sqs_dlq_url or os.getenv('SQS_DLQ_URL')
        
        self.s3_bucket_name = self.s3_bucket_name or os.getenv('S3_BUCKET_NAME')
        
        self.pinecone_api_key = self.pinecone_api_key or os.getenv('PINECONE_API_KEY')
        self.pinecone_index_name = self.pinecone_index_name or os.getenv('PINECONE_INDEX_NAME')
        
        self.polling_interval = int(os.getenv('POLLING_INTERVAL', self.polling_interval))
        self.max_messages_per_poll = int(os.getenv('MAX_MESSAGES_PER_POLL', self.max_messages_per_poll))
        self.max_retries = int(os.getenv('MAX_RETRIES', self.max_retries))
        
        self.chunk_size = int(os.getenv('CHUNK_SIZE', self.chunk_size))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', self.chunk_overlap))
        
        self.embedding_model_name = os.getenv('EMBEDDING_MODEL_NAME', self.embedding_model_name)
    
    def _validate(self):
        """Validate required settings."""
        if not self.aws_access_key_id:
            raise ValueError(
                "aws_access_key_id is required (set SECRET_NAME or AWS_ACCESS_KEY_ID)"
            )
        if not self.aws_secret_access_key:
            raise ValueError(
                "aws_secret_access_key is required (set SECRET_NAME or AWS_SECRET_ACCESS_KEY)"
            )
        if not self.sqs_queue_url:
            raise ValueError(
                "sqs_queue_url is required (set SECRET_NAME or SQS_QUEUE_URL)"
            )
        if not self.sqs_dlq_url:
            raise ValueError(
                "sqs_dlq_url is required (set SECRET_NAME or SQS_DLQ_URL)"
            )
        if not self.pinecone_api_key:
            raise ValueError(
                "pinecone_api_key is required (set SECRET_NAME or PINECONE_API_KEY)"
            )
        if not self.pinecone_index_name:
            raise ValueError(
                "pinecone_index_name is required (set SECRET_NAME or PINECONE_INDEX_NAME)"
            )


# Create settings instance (secrets_manager can be injected via kwargs if needed)
settings = Settings()
