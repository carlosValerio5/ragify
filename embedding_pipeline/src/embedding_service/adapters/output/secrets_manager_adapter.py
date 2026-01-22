"""AWS Secrets Manager Adapter - Implements SecretsManagerPort using AWS Secrets Manager."""

import boto3
import json
import logging
from typing import Dict, Optional
from botocore.exceptions import ClientError
from ...domain.ports import SecretsManagerPort

logger = logging.getLogger(__name__)


class AWSSecretsManagerAdapter(SecretsManagerPort):
    """Adapter for AWS Secrets Manager operations."""
    
    def __init__(self, secret_name: str, region_name: str = "us-east-1"):
        """
        Initialize the AWS Secrets Manager adapter.
        
        Args:
            secret_name: Name of the secret in AWS Secrets Manager
            region_name: AWS region where the secret is stored
        """
        self.secret_name = secret_name
        self.region_name = region_name
        self._client = None
        self._cached_secret: Optional[Dict[str, str]] = None
    
    @property
    def client(self):
        """Lazy initialization of Secrets Manager client."""
        if self._client is None:
            self._client = boto3.client(
                'secretsmanager',
                region_name=self.region_name
            )
        return self._client
    
    def _get_secret(self) -> Dict[str, str]:
        """
        Retrieve secret from AWS Secrets Manager.
        Caches the result to avoid repeated API calls.
        
        Returns:
            dict: Secret values as a dictionary
            
        Raises:
            ValueError: If secret cannot be retrieved or parsed
        """
        if self._cached_secret is not None:
            return self._cached_secret
        
        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise ValueError(
                    f"Secret '{self.secret_name}' not found in AWS Secrets Manager"
                ) from e
            elif error_code == 'InvalidRequestException':
                raise ValueError(
                    f"Invalid request for secret '{self.secret_name}': {e}"
                ) from e
            elif error_code == 'InvalidParameterException':
                raise ValueError(
                    f"Invalid parameter for secret '{self.secret_name}': {e}"
                ) from e
            elif error_code == 'DecryptionFailureException':
                raise ValueError(
                    f"Failed to decrypt secret '{self.secret_name}': {e}"
                ) from e
            elif error_code == 'InternalServiceErrorException':
                raise ValueError(
                    f"AWS Secrets Manager service error for '{self.secret_name}': {e}"
                ) from e
            else:
                raise ValueError(
                    f"Error retrieving secret '{self.secret_name}': {e}"
                ) from e
        
        # Parse the secret string (assuming JSON format)
        try:
            secret_string = response['SecretString']
            secret_dict = json.loads(secret_string)
            self._cached_secret = secret_dict
            return secret_dict
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse secret '{self.secret_name}' as JSON: {e}"
            ) from e
    
    def get_embedding_pipeline_credentials(self) -> Dict[str, str]:
        """
        Retrieve all credentials needed for embedding pipeline from secret.
        
        Expected secret keys:
        - aws_access_key_id
        - aws_secret_access_key
        - aws_region (optional, defaults to us-east-1)
        - sqs_queue_url
        - sqs_dlq_url
        - s3_bucket_name (optional)
        - pinecone_api_key
        - pinecone_index_name
        
        Returns:
            dict: Contains all credential fields
            
        Raises:
            ValueError: If required keys are missing
        """
        secret = self._get_secret()
        
        required_keys = [
            'aws_access_key_id',
            'aws_secret_access_key',
            'sqs_queue_url',
            'sqs_dlq_url',
            'pinecone_api_key',
            'pinecone_index_name'
        ]
        missing_keys = [key for key in required_keys if key not in secret]
        
        if missing_keys:
            raise ValueError(
                f"Secret '{self.secret_name}' missing required keys: {', '.join(missing_keys)}"
            )
        
        return {
            'aws_access_key_id': secret['aws_access_key_id'],
            'aws_secret_access_key': secret['aws_secret_access_key'],
            'aws_region': secret.get('aws_region', 'us-east-1'),
            'sqs_queue_url': secret['sqs_queue_url'],
            'sqs_dlq_url': secret['sqs_dlq_url'],
            's3_bucket_name': secret.get('s3_bucket_name'),
            'pinecone_api_key': secret['pinecone_api_key'],
            'pinecone_index_name': secret['pinecone_index_name']
        }
