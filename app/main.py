"""
Aplicação principal FastAPI para o sistema RAGBot.

Este módulo define a aplicação FastAPI com todos os endpoints,
middleware e configurações necessárias para o funcionamento
do sistema de chat RAG.
"""

import time
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from loguru import logger

from .config import settings
from .schemas import (
    ChatRequest, ChatResponse, DocumentUploadResponse, 
    HealthResponse, ErrorResponse
)
from .services import chat_service, document_processing_service
from .crud import db_manager


# Configuração da aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API para sistema RAG (Retrieval-Augmented Generation)",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        ).dict()
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
        ).dict()
    )


# Endpoints
@app.get("/", response_model=dict)
async def root():
    """
    Endpoint raiz da API.
    
    Returns:
        dict: Informações básicas da API
    """
    return {
        "message": f"Bem-vindo ao {settings.app_name}!",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentação disponível apenas em modo debug"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint para verificação de saúde da aplicação.
    
    Returns:
        HealthResponse: Status da aplicação e componentes
    """
    try:
        # Verificar conexão com banco de dados
        db_status = "healthy" if db_manager.test_connection() else "unhealthy"
        
        return HealthResponse(
            status="healthy" if db_status == "healthy" else "degraded",
            timestamp=datetime.now(),
            version=settings.app_version,
            database_status=db_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version=settings.app_version,
            database_status="error"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal para chat interativo.
    
    Recebe uma pergunta do usuário e retorna uma resposta baseada
    nos documentos processados utilizando o sistema RAG.
    
    Args:
        request: Dados da requisição de chat
        
    Returns:
        ChatResponse: Resposta estruturada do chat
        
    Raises:
        HTTPException: Em caso de erro no processamento
    """
    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        response = await chat_service.process_chat(
            user_message=request.message,
            conversation_id=request.conversation_id,
            max_chunks=request.max_chunks
        )
        
        logger.info(f"Chat response generated successfully in {response.processing_time:.4f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar chat: {str(e)}"
        )


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Endpoint para upload e processamento de documentos.
    
    NOTA: Este endpoint está implementado para completude da API,
    mas o processamento de documentos é normalmente feito offline
    através do script de ingestão.
    
    Args:
        file: Arquivo PDF a ser processado
        
    Returns:
        DocumentUploadResponse: Resultado do processamento
        
    Raises:
        HTTPException: Em caso de erro no processamento
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas arquivos PDF são suportados"
            )
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # TODO: Implementar processamento de PDF
        # Por enquanto, retorna uma resposta mock
        logger.warning("PDF processing not implemented yet - returning mock response")
        
        return DocumentUploadResponse(
            document_id=uuid.uuid4(),
            filename=file.filename,
            chunks_created=0,
            processing_time=0.0,
            status="pending - use ingest script for processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar documento: {str(e)}"
        )


@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: uuid.UUID):
    """
    Endpoint para recuperar mensagens de uma conversa.
    
    Args:
        conversation_id: ID da conversa
        
    Returns:
        dict: Lista de mensagens da conversa
        
    Note:
        Este endpoint seria implementado conforme necessidade
        da interface frontend
    """
    # TODO: Implementar recuperação de mensagens
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "message": "Endpoint em desenvolvimento"
    }


# Evento de startup
@app.on_event("startup")
async def startup_event():
    """Evento executado no startup da aplicação."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Verificar conexão com banco de dados
    if not db_manager.test_connection():
        logger.error("Failed to connect to database!")
        raise RuntimeError("Database connection failed")
    
    logger.info("Application started successfully")


# Evento de shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no shutdown da aplicação."""
    logger.info("Shutting down application...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )