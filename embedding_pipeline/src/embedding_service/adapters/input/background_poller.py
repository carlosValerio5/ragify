"""Background Poller - Polls SQS queue and processes files."""

import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import Optional
from ...domain.ports import MessageQueuePort
from ...application.services import EmbeddingPipelineService

logger = logging.getLogger(__name__)


class BackgroundPoller:
    """Background task that polls SQS queue and processes files."""
    
    def __init__(
        self,
        message_queue: MessageQueuePort,
        pipeline_service: EmbeddingPipelineService,
        polling_interval: int = 5,
        max_messages_per_poll: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize the background poller.
        
        Args:
            message_queue: MessageQueuePort implementation
            pipeline_service: EmbeddingPipelineService for processing files
            polling_interval: Seconds between polls
            max_messages_per_poll: Maximum messages to receive per poll
            max_retries: Maximum retry attempts before sending to DLQ
        """
        self.message_queue = message_queue
        self.pipeline_service = pipeline_service
        self.polling_interval = polling_interval
        self.max_messages_per_poll = max_messages_per_poll
        self.max_retries = max_retries
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the background polling task."""
        if self._running:
            logger.warning("Background poller is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Background poller started")
    
    async def stop(self):
        """Stop the background polling task."""
        self._running = False
        if self._task:
            await self._task
        logger.info("Background poller stopped")
    
    async def _poll_loop(self):
        """Main polling loop."""
        while self._running:
            try:
                await self._process_messages()
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(self.polling_interval)
    
    async def _process_messages(self):
        """Process messages from the queue."""
        messages = self.message_queue.receive_messages(self.max_messages_per_poll)
        
        if not messages:
            return
        
        logger.info(f"Processing {len(messages)} messages")
        
        for message in messages:
            try:
                await self._process_message(message)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Message will remain in queue and be retried
    
    async def _process_message(self, message: dict):
        """Process a single message."""
        message_body = message.get('Body', '')
        receipt_handle = message.get('ReceiptHandle')
        message_attributes = message.get('MessageAttributes', {})
        
        if not receipt_handle:
            logger.error("Message missing ReceiptHandle")
            return
        
        try:
            # Parse message body to extract S3 bucket and key
            bucket, key = self._extract_s3_info(message_body)
            
            if not bucket or not key:
                logger.error(f"Could not extract S3 info from message: {message_body}")
                # Send to DLQ for manual review
                self._send_to_dlq_with_error(
                    message_body,
                    message_attributes,
                    "INVALID_MESSAGE_FORMAT",
                    "Could not extract S3 bucket and key from message"
                )
                self.message_queue.delete_message(receipt_handle)
                return
            
            # Process the file
            logger.info(f"Processing file: s3://{bucket}/{key}")
            count = await asyncio.to_thread(
                self.pipeline_service.process_file,
                bucket,
                key
            )
            
            logger.info(f"Successfully processed s3://{bucket}/{key}: {count} vectors")
            
            # Delete message from queue after successful processing
            self.message_queue.delete_message(receipt_handle)
            
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            
            logger.error(f"Failed to process message: {error_type}: {error_message}")
            
            # Check if this is a critical error that should go to DLQ immediately
            if self._is_critical_error(e):
                logger.warning("Critical error detected, sending to DLQ immediately")
                self._send_to_dlq_with_error(
                    message_body,
                    message_attributes,
                    error_type,
                    error_message
                )
                self.message_queue.delete_message(receipt_handle)
            else:
                # For non-critical errors, let the message remain in queue
                # SQS visibility timeout will handle retries
                logger.info("Non-critical error, message will remain in queue for retry")
    
    def _extract_s3_info(self, message_body: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract S3 bucket and key from message body.
        
        Supports multiple formats:
        - JSON: {"bucket": "my-bucket", "key": "documents/file.pdf"}
        - S3 event: {"Records": [{"s3": {"bucket": {"name": "..."}, "object": {"key": "..."}}}]}
        
        Args:
            message_body: Message body string
            
        Returns:
            Tuple of (bucket, key) or (None, None) if extraction fails
        """
        try:
            data = json.loads(message_body)
            
            # Format 1: Simple JSON with bucket and key
            if 'bucket' in data and 'key' in data:
                return data['bucket'], data['key']
            
            # Format 2: S3 event format
            if 'Records' in data and isinstance(data['Records'], list):
                if len(data['Records']) > 0:
                    record = data['Records'][0]
                    if 's3' in record:
                        s3_data = record['s3']
                        bucket = s3_data.get('bucket', {}).get('name')
                        key = s3_data.get('object', {}).get('key')
                        if bucket and key:
                            return bucket, key
            
            logger.warning(f"Unsupported message format: {message_body}")
            return None, None
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in message body: {message_body}")
            return None, None
        except Exception as e:
            logger.error(f"Error extracting S3 info: {e}")
            return None, None
    
    def _is_critical_error(self, error: Exception) -> bool:
        """
        Determine if an error is critical (should go to DLQ immediately).
        
        Args:
            error: Exception to check
            
        Returns:
            True if critical, False if retryable
        """
        critical_error_types = (
            'ValueError',
            'KeyError',
            'AttributeError',
            'TypeError',
            'FileNotFoundError',
            'UnicodeDecodeError'
        )
        
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Check error type
        if error_type in critical_error_types:
            return True
        
        # Check error message for critical patterns
        critical_patterns = [
            'invalid',
            'not found',
            'parse',
            'format',
            'decode',
            'unsupported'
        ]
        
        if any(pattern in error_message for pattern in critical_patterns):
            return True
        
        return False
    
    def _send_to_dlq_with_error(
        self,
        message_body: str,
        original_attributes: dict,
        error_type: str,
        error_message: str
    ):
        """Send message to DLQ with error metadata."""
        # Add error metadata to message attributes
        error_attributes = original_attributes.copy() if original_attributes else {}
        error_attributes['ErrorType'] = {
            'DataType': 'String',
            'StringValue': error_type
        }
        error_attributes['ErrorMessage'] = {
            'DataType': 'String',
            'StringValue': error_message
        }
        error_attributes['FailedAt'] = {
            'DataType': 'String',
            'StringValue': datetime.now(UTC).isoformat() + 'Z'
        }
        
        self.message_queue.send_to_dlq(message_body, error_attributes)
