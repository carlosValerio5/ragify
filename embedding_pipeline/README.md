# Embedding Pipeline Service

A hexagonal architecture Python module for processing files from S3, extracting embeddings, and storing them in a vector database.

## Architecture

This module follows hexagonal architecture principles with dependency injection:

- **Domain Layer**: Core business logic, entities, and ports (interfaces)
- **Application Layer**: Use cases and orchestration
- **Adapters Layer**: External integrations (SQS, S3, Pinecone, model2vec)
- **Main**: Dependency injection composition root

## Features

- Polls SQS queue for file processing notifications
- Loads files from S3 using LangChain S3FileLoader
- Splits documents into chunks using RecursiveCharacterTextSplitter
- Generates embeddings using model2vec (minishlab/potion-base-4M)
- Stores vectors in Pinecone (swappable via VectorDatabasePort)
- Dead letter queue (DLQ) support for failed processing
- FastAPI endpoints for manual triggers and health checks
- Background polling with configurable intervals

## Setup

1. Install dependencies:
```bash
pipenv install
```

2. Configure environment variables (see `.env` example):
```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
SQS_QUEUE_URL=https://sqs.region.amazonaws.com/account/queue
SQS_DLQ_URL=https://sqs.region.amazonaws.com/account/dlq
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=your_index
```

3. Run the service:
```bash
python -m src.embedding_service.main
```

## Configuration

All configuration is managed through `config.py` using pydantic-settings. Settings can be provided via:
- Environment variables
- `.env` file
- Direct instantiation

## API Endpoints

- `POST /embedding/trigger` - Manually trigger file processing
- `GET /embedding/health` - Health check (includes vector DB status)
- `GET /embedding/status` - Service status

## SQS Message Format

The service expects SQS messages in one of these formats:

**Simple JSON:**
```json
{
  "bucket": "my-bucket",
  "key": "documents/file.pdf"
}
```

**S3 Event Format:**
```json
{
  "Records": [{
    "s3": {
      "bucket": {"name": "my-bucket"},
      "object": {"key": "documents/file.pdf"}
    }
  }]
}
```

## Error Handling

- Non-critical errors: Messages remain in queue for retry (handled by SQS visibility timeout)
- Critical errors: Messages are immediately sent to DLQ with error metadata
- DLQ messages include: original message body, error type, error message, and timestamp

## Dependencies

See `Pipfile` for complete list. Key dependencies:
- langchain-community
- langchain-text-splitters
- model2vec
- pinecone
- fastapi
- boto3
