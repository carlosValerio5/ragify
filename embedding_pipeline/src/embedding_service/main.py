"""Main application entry point with dependency injection composition."""

import logging
import sys
import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Add parent directory to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from config.config import settings
from config.logging_config import setup_logging
from .domain.ports import (
    MessageQueuePort,
    DocumentLoaderPort,
    TextSplitterPort,
    EmbeddingModelPort,
    VectorDatabasePort
)
from .adapters.input.sqs_poller import SQSPollerAdapter
from .adapters.input.background_poller import BackgroundPoller
from .adapters.input.api_router import create_api_router
from .adapters.output.s3_loader import S3FileLoaderAdapter
from .adapters.output.text_splitter import RecursiveTextSplitterAdapter
from .adapters.output.embedding_model import Model2VecAdapter
from .adapters.output.pinecone_adapter import PineconeAdapter
from .application.services import EmbeddingPipelineService

# Configure logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


# Global instances for lifespan management
background_poller: BackgroundPoller = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    global background_poller
    
    # Startup
    logger.info("Starting embedding pipeline service...")
    
    # Start background poller
    if background_poller:
        await background_poller.start()
        logger.info("Background poller started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down embedding pipeline service...")
    
    # Stop background poller
    if background_poller:
        await background_poller.stop()
        logger.info("Background poller stopped")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application with dependency injection.
    
    Returns:
        Configured FastAPI application
    """
    # Instantiate adapters (output)
    logger.info("Initializing adapters...")
    
    s3_loader = S3FileLoaderAdapter(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )
    
    splitter = RecursiveTextSplitterAdapter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    embedder = Model2VecAdapter(
        model_name=settings.embedding_model_name
    )
    
    vector_db = PineconeAdapter(
        api_key=settings.pinecone_api_key,
        index_name=settings.pinecone_index_name,
        dimension=settings.pinecone_dimension,
        cloud=settings.pinecone_cloud,
        region=settings.pinecone_region
    )
    
    # Instantiate adapters (input)
    sqs_poller = SQSPollerAdapter(
        queue_url=settings.sqs_queue_url,
        dlq_url=settings.sqs_dlq_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )
    
    # Inject into service
    pipeline_service = EmbeddingPipelineService(
        document_loader=s3_loader,
        text_splitter=splitter,
        embedding_model=embedder,
        vector_database=vector_db
    )
    
    # Create background poller
    global background_poller
    background_poller = BackgroundPoller(
        message_queue=sqs_poller,
        pipeline_service=pipeline_service,
        polling_interval=settings.polling_interval,
        max_messages_per_poll=settings.max_messages_per_poll,
        max_retries=settings.max_retries
    )
    
    # Create FastAPI app
    app = FastAPI(
        title="Embedding Pipeline Service",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Include API router
    api_router = create_api_router(pipeline_service, vector_db)
    app.include_router(api_router)
    
    logger.info("Application created successfully")
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.embedding_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_config=None
    )
