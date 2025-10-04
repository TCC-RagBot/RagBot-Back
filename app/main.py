"""
Aplicação principal FastAPI para o sistema RAGBot.

Este módulo define a aplicação FastAPI com todos os endpoints,
middleware e configurações necessárias para o funcionamento
do sistema de chat RAG.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .config.settings import settings
from .schemas.chat import ErrorResponse
from .repositories.conversation_repository import db_manager
from .api.routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Verificar conexão com banco de dados
    if not db_manager.test_connection():
        logger.error("Failed to connect to database!")
        raise RuntimeError("Database connection failed")
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAGBot application...")


# Configuração da aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API para sistema RAG (Retrieval-Augmented Generation)",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(chat_router)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware para logging de todas as requisições."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handler para erros 404."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Endpoint não encontrado",
            detail=f"O endpoint {request.url.path} não existe"
        ).model_dump()
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handler para erros internos do servidor."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Erro interno do servidor",
            detail="Ocorreu um erro inesperado. Tente novamente mais tarde."
        ).model_dump()
    )





if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )