import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .config.settings import settings
from .config.constants import APP_NAME, APP_VERSION
from .schemas.shared_schemas import ErrorResponse
from db.manager import db_manager

from .routes.core_routes import router as core_router
from .routes.chat_routes import router as chat_router
from .routes.document_routes import router as document_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando {APP_NAME} v{APP_VERSION}")
    if not db_manager.test_connection():
        logger.error("Falha ao conectar com o banco de dados!")
        raise RuntimeError("Conexão com o banco de dados falhou")
    logger.info("Aplicação iniciada com sucesso")
    yield
    logger.info("Finalizando aplicação RAGBot...")

async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Tempo: {process_time:.4f}s"
    )
    return response

async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Endpoint não encontrado",
            detail=f"O endpoint {request.url.path} não existe"
        ).model_dump()
    )

async def internal_error_handler(request: Request, exc):
    logger.error(f"Erro interno do servidor: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Erro interno do servidor",
            detail="Ocorreu um erro inesperado. Tente novamente mais tarde."
        ).model_dump()
    )

def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="Backend API para sistema RAG (Retrieval-Augmented Generation)",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(log_requests)

    app.exception_handler(404)(not_found_handler)
    app.exception_handler(500)(internal_error_handler)

    app.include_router(core_router, tags=["Sistema"])
    app.include_router(chat_router, tags=["Chat"])
    app.include_router(document_router, tags=["Documentos"])

    return app