"""SQS Poller Adapter - Implements MessageQueuePort using boto3 SQS client."""

import logging
import json
import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Optional
from ...domain.ports import MessageQueuePort

logger = logging.getLogger(__name__)


class SQSPollerAdapter(MessageQueuePort):
    """Adapter for SQS queue operations using boto3."""
    
    def __init__(
        self,
        queue_url: str,
        dlq_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = "us-east-1"
    ):
        """
        Initialize the SQS poller adapter.
        
        Args:
            queue_url: URL of the main SQS queue
            dlq_url: URL of the dead letter queue
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
        """
        self.queue_url = queue_url
        self.dlq_url = dlq_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        
        # Initialize SQS client
        self.sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        logger.info(f"Initialized SQS poller for queue: {queue_url}")
        logger.info(f"DLQ configured: {dlq_url}")
    
    def receive_messages(self, max_messages: int = 10) -> List[Dict]:
        """
        Receive messages from the queue.
        
        Args:
            max_messages: Maximum number of messages to receive (max 10 for SQS)
            
        Returns:
            List of message dictionaries containing:
            - 'Body': message body (str)
            - 'ReceiptHandle': receipt handle for deletion (str)
            - 'MessageAttributes': optional message attributes (dict)
        """
        if max_messages > 10:
            max_messages = 10
            logger.warning("SQS max_messages limited to 10")
        
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20,  # Long polling
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            logger.debug(f"Received {len(messages)} messages from queue")
            return messages
            
        except ClientError as e:
            logger.error(f"Failed to receive messages from SQS: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error receiving messages: {e}")
            raise
    
    def delete_message(self, receipt_handle: str) -> None:
        """
        Delete a message from the queue.
        
        Args:
            receipt_handle: Receipt handle from the received message
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.debug("Message deleted from queue")
        except ClientError as e:
            logger.error(f"Failed to delete message from SQS: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting message: {e}")
            raise
    
    def send_to_dlq(
        self,
        message_body: str,
        original_message_attributes: Dict
    ) -> None:
        """
        Send a failed message to the dead letter queue.
        
        Args:
            message_body: Original message body
            original_message_attributes: Original message attributes including error metadata
        """
        try:
            # Prepare message attributes for DLQ
            message_attributes = {}
            if original_message_attributes:
                # Copy original attributes
                for key, value in original_message_attributes.items():
                    if isinstance(value, dict) and 'StringValue' in value:
                        message_attributes[key] = {
                            'DataType': value.get('DataType', 'String'),
                            'StringValue': value['StringValue']
                        }
            
            # Send to DLQ
            response = self.sqs_client.send_message(
                QueueUrl=self.dlq_url,
                MessageBody=message_body,
                MessageAttributes=message_attributes if message_attributes else None
            )
            
            logger.info(f"Message sent to DLQ: {response.get('MessageId')}")
            
        except ClientError as e:
            logger.error(f"Failed to send message to DLQ: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message to DLQ: {e}")
            raise
