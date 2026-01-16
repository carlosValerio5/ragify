from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import mimetypes
from app.s3_client import upload_pdf_to_s3

router = APIRouter(prefix="/documents")

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file to S3.
    
    Args:
        file: PDF file to upload
        
    Returns:
        JSON response with s3_key and metadata
    """
    # Validate file extension
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="File must be a PDF. Only .pdf files are accepted."
        )
    
    # Validate content type
    content_type = file.content_type
    if content_type and content_type != 'application/pdf':
        # Also check mimetype as fallback
        guessed_type, _ = mimetypes.guess_type(file.filename)
        if guessed_type != 'application/pdf':
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type: {content_type}. Expected application/pdf."
            )
    
    try:
        # Upload to S3
        result = upload_pdf_to_s3(file.file, file.filename)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "s3_key": result['s3_key'],
                "metadata": result['metadata']
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to S3: {str(e)}"
        )