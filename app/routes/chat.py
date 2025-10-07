import uuid
from fastapi import APIRouter, HTTPException, status, File, UploadFile
from datetime import datetime
from loguru import logger

from ..config.settings import settings
from ..config.constants import APP_NAME, APP_VERSION
from ..schemas.chat import (
    ChatRequest, ChatResponse, DocumentUploadResponse, 
    HealthResponse
)
from ..repositories.conversation_repository import db_manager
from ..services.chat_service import chat_service
from ..services.document_service import document_service

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


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
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


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        logger.info(f"Starting document upload: {file.filename}")
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do arquivo é obrigatório"
            )
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas arquivos PDF são suportados"
            )
        
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo está vazio"
            )
        
        result = await document_service.process_document_upload(content, file.filename)
        
        if result.status.startswith("error"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.status
            )
        
        logger.success(
            f"Document upload completed: {file.filename} "
            f"({result.chunks_created} chunks, {result.processing_time:.2f}s)"
        )
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error for {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar documento: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages")
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
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "message": "Endpoint em desenvolvimento"
    }