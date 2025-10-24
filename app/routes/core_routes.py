from fastapi import APIRouter
from datetime import datetime
from loguru import logger

from ..config.settings import settings
from ..config.constants import APP_NAME, APP_VERSION
from ..schemas.shared_schemas import HealthResponse
from db.manager import db_manager

router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    return {
        "message": f"Bem-vindo ao {APP_NAME}!",
        "version": APP_VERSION,
        "docs": "/docs" if settings.debug else "Documentação disponível apenas em modo debug"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        db_status = "healthy" if db_manager.test_connection() else "unhealthy"
        
        return HealthResponse(
            status="healthy" if db_status == "healthy" else "degraded",
            timestamp=datetime.now().isoformat(),
            version=APP_VERSION,
            database_status=db_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version=APP_VERSION,
            database_status="error"
        )