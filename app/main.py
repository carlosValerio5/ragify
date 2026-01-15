from app import logging_config
from fastapi import FastAPI
import uvicorn
import logging

from app.config import settings
from app.routers import main_router, pipeline_router
from app.logging_config import setup_logging, handler

app = FastAPI(title="PDF Ingestion Pipeline", version="1.0.0")
app.include_router(main_router.router)
app.include_router(pipeline_router.router)

setup_logging()
if __name__ == "__main__":
    for name in logging.root.manager.loggerDict:
        if name in ("uvicorn"):
            uvicorn_logger = logging.getLogger(name)
            uvicorn_logger.handlers.clear()
            uvicorn_logger.addHandler(handler)
            uvicorn_logger.setLevel(settings.log_level)

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.reload, log_config=None)