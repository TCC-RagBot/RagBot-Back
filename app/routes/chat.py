"""
Rotas da API RAGBot.

Este módulo contém todos os endpoints da aplicação,
organizados por funcionalidade.
"""

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

# Router principal
router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    """
    Endpoint raiz da API.
    
    Returns:
        dict: Informações básicas da API
    """
    return {
        "message": f"Bem-vindo ao {APP_NAME}!",
        "version": APP_VERSION,
        "docs": "/docs" if settings.debug else "Documentação disponível apenas em modo debug"
    }


@router.get("/health", response_model=HealthResponse)
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


@router.post("/upload", response_model=DocumentUploadResponse)
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
    # TODO: Implementar recuperação de mensagens
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "message": "Endpoint em desenvolvimento"
    }