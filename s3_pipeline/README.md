# PDF to S3 Ingestion Pipeline

A FastAPI-based REST API that accepts PDF file uploads and stores them in AWS S3 with metadata for downstream RAG processing.

## Features

- REST API endpoint for PDF file uploads
- Automatic validation of PDF files
- S3 storage with metadata (filename, upload timestamp)
- Unique file naming using UUIDs
- Basic error handling

## Prerequisites

- Python 3.8+
- pipenv (install with `pip install pipenv`)
- AWS account with S3 bucket
- AWS access credentials

## Installation

1. Clone or navigate to the project directory:
```bash
cd RAG
```

2. Install dependencies using pipenv (this creates a virtual environment automatically):
```bash
pipenv install
```

## Configuration

You can configure credentials in two ways:

### Option 1: AWS Secrets Manager (Recommended)

The application can retrieve credentials from AWS Secrets Manager. Create a secret in AWS Secrets Manager with the following JSON structure:

```json
{
  "aws_access_key_id": "your_access_key_id",
  "aws_secret_access_key": "your_secret_access_key",
  "s3_bucket_name": "your_bucket_name",
  "s3_region": "us-east-1"
}
```

Then create a `.env` file with:

```
SECRET_NAME=your_secret_name
SECRET_REGION=us-east-1
```

**Note:** The AWS credentials used to access Secrets Manager should be configured via AWS credentials file (`~/.aws/credentials`), environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`), or IAM role (if running on EC2/Lambda).

### Option 2: Environment Variables (Fallback)

Alternatively, you can provide credentials directly via environment variables. Create a `.env` file with:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
S3_BUCKET_NAME=your_bucket_name
S3_REGION=us-east-1
```

The application will prioritize Secrets Manager if `SECRET_NAME` is set, otherwise it will fall back to environment variables.

## Usage

1. Start the server using pipenv:
```bash
pipenv run python3 -m app.main
```

   Or activate the virtual environment first:
```bash
pipenv shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Upload a PDF file using curl:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf"
```

3. Or use the interactive API docs:
   - Navigate to `http://localhost:8000/docs` in your browser
   - Use the Swagger UI to test the `/upload` endpoint

## API Endpoints

### POST /upload
Uploads a PDF file to S3.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing the PDF

**Response (Success - 200):**
```json
{
  "status": "success",
  "s3_key": "documents/550e8400-e29b-41d4-a716-446655440000_example.pdf",
  "metadata": {
    "original_filename": "example.pdf",
    "upload_timestamp": "2026-01-14T10:30:00Z"
  }
}
```

**Error Responses:**
- `400`: Invalid file type (not a PDF)
- `500`: S3 upload failure

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Project Structure

```
RAG/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and upload endpoint
│   ├── config.py            # S3 and app configuration
│   ├── s3_client.py         # S3 upload logic
│   └── secrets_manager.py   # AWS Secrets Manager integration
├── Pipfile                  # pipenv dependencies
├── Pipfile.lock             # pipenv lock file (auto-generated)
└── README.md
```

## Environment Variables

### Secrets Manager Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_NAME` | Name of the secret in AWS Secrets Manager | No* |
| `SECRET_REGION` | AWS region where the secret is stored | No (default: us-east-1) |

### Direct Credentials (Fallback)

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes* |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes* |
| `S3_BUCKET_NAME` | Target S3 bucket name | Yes* |
| `S3_REGION` | AWS region | No (default: us-east-1) |

*Either `SECRET_NAME` OR the direct credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`) are required.

## S3 File Structure

Uploaded files are stored in S3 with the following structure:
- **Key format**: `documents/{uuid}_{original_filename}`
- **Content-Type**: `application/pdf`
- **Metadata**: Contains `original_filename` and `upload_timestamp`

## Error Handling

The API validates:
- File extension (must be `.pdf`)
- Content type (must be `application/pdf`)

Upload errors are caught and returned as 500 responses with error details.

## Next Steps

After files are uploaded to S3, they can be processed by your RAG system using the returned `s3_key` to retrieve the file.
