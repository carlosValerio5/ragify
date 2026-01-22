"""API Router - FastAPI endpoints for manual triggers and status."""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from ...application.services import EmbeddingPipelineService
from ...domain.ports import VectorDatabasePort

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embedding")


class ProcessFileRequest(BaseModel):
    """Request model for manual file processing."""
    bucket: str
    key: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    vector_db_healthy: bool


class StatusResponse(BaseModel):
    """Status response."""
    service: str
    status: str


def create_api_router(
    pipeline_service: EmbeddingPipelineService,
    vector_database: VectorDatabasePort
) -> APIRouter:
    """
    Create and configure the API router.
    
    Args:
        pipeline_service: EmbeddingPipelineService instance
        vector_database: VectorDatabasePort instance
        
    Returns:
        Configured APIRouter
    """
    @router.post("/trigger", response_model=dict)
    async def trigger_processing(
        request: ProcessFileRequest,
        background_tasks: BackgroundTasks
    ):
        """
        Manually trigger processing of a file.
        
        Args:
            request: ProcessFileRequest with bucket and key
            background_tasks: FastAPI background tasks
            
        Returns:
            Success response with processing status
        """
        try:
            logger.info(f"Manual trigger for s3://{request.bucket}/{request.key}")
            
            # Process in background
            def process():
                try:
                    count = pipeline_service.process_file(request.bucket, request.key)
                    logger.info(f"Manual processing completed: {count} vectors")
                    return count
                except Exception as e:
                    logger.error(f"Manual processing failed: {e}")
                    raise
            
            background_tasks.add_task(process)
            
            return {
                "status": "processing",
                "message": f"File processing started for s3://{request.bucket}/{request.key}",
                "bucket": request.bucket,
                "key": request.key
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger processing: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to trigger processing: {str(e)}"
            )
    
    @router.get("/health", response_model=HealthResponse)
    async def health_check():
        """
        Health check endpoint.
        
        Returns:
            Health status including vector database health
        """
        try:
            vector_db_healthy = vector_database.health_check()
            
            return HealthResponse(
                status="healthy" if vector_db_healthy else "degraded",
                vector_db_healthy=vector_db_healthy
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthResponse(
                status="unhealthy",
                vector_db_healthy=False
            )
    
    @router.get("/status", response_model=StatusResponse)
    async def status():
        """
        Service status endpoint.
        
        Returns:
            Service status information
        """
        return StatusResponse(
            service="embedding_pipeline",
            status="running"
        )
    
    return router
