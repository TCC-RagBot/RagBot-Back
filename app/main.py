import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .config.settings import settings
from .config.constants import APP_NAME, APP_VERSION, DEFAULT_HOST, DEFAULT_PORT
from .schemas.shared_schemas import ErrorResponse
from db.manager import db_manager
from .routes.core_routes import router as core_router
from .routes.chat_routes import router as chat_router
from .routes.document_routes import router as document_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    if not db_manager.test_connection():
        logger.error("Failed to connect to database!")
        raise RuntimeError("Database connection failed")
    
    logger.info("Application started successfully")
    
    yield
    
    logger.info("Shutting down RAGBot application...")


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

app.include_router(core_router)
app.include_router(chat_router)
app.include_router(document_router)

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Endpoint não encontrado",
            detail=f"O endpoint {request.url.path} não existe"
        ).model_dump()
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
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
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        timeout_keep_alive=60,  
        timeout_graceful_shutdown=30
    )