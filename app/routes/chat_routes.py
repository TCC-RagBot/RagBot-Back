import uuid
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from ..schemas.chat_schemas import ChatRequest, ChatResponse
from ..services.chat_service import chat_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        response = await chat_service.process_chat(
            user_message=request.message,
            max_chunks=request.max_chunks,
            conversation_id=request.conversation_id
        )
        
        logger.info(f"Chat response generated successfully in {response.processing_time:.4f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar chat: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: uuid.UUID):
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "message": "Endpoint em desenvolvimento"
    }