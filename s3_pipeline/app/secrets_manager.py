import boto3
import json
from typing import Dict, Optional
from botocore.exceptions import ClientError


class SecretsManager:
    """AWS Secrets Manager client for retrieving S3 credentials."""
    
    def __init__(self, secret_name: str, region_name: str = "us-east-1"):
        """
        Initialize Secrets Manager client.
        
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
    
    def get_secret(self) -> Dict[str, str]:
        """
        Retrieve secret from AWS Secrets Manager.
        Caches the result to avoid repeated API calls.
        
        Returns:
            dict: Secret values as a dictionary
            
        Raises:
            ClientError: If secret cannot be retrieved
            ValueError: If secret value cannot be parsed
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
    
    def get_s3_credentials(self) -> Dict[str, str]:
        """
        Retrieve S3 credentials from secret.
        Expects secret to contain: aws_access_key_id, aws_secret_access_key, s3_bucket_name
        
        Returns:
            dict: Contains aws_access_key_id, aws_secret_access_key, s3_bucket_name
        """
        secret = self.get_secret()
        
        required_keys = ['aws_access_key_id', 'aws_secret_access_key', 's3_bucket_name']
        missing_keys = [key for key in required_keys if key not in secret]
        
        if missing_keys:
            raise ValueError(
                f"Secret '{self.secret_name}' missing required keys: {', '.join(missing_keys)}"
            )
        
        return {
            'aws_access_key_id': secret['aws_access_key_id'],
            'aws_secret_access_key': secret['aws_secret_access_key'],
            's3_bucket_name': secret['s3_bucket_name'],
            's3_region': secret.get('s3_region', 'us-east-1')
        }
