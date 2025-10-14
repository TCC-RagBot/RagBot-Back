from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from .shared_schemas import SourceChunk


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Mensagem do usuário", example="O que é pênalti?")
    conversation_id: Optional[UUID] = Field(None, description="ID da conversa")
    max_chunks: int = Field(..., ge=1, le=10, description="Máximo de chunks a recuperar", example=5)


class ChatResponse(BaseModel):
    response: str = Field(..., description="Resposta gerada")
    conversation_id: UUID = Field(..., description="ID da conversa")
    message_id: UUID = Field(..., description="ID da mensagem")
    sources: List[SourceChunk] = Field(default_factory=list, description="Chunks de origem")
    processing_time: float = Field(..., ge=0.0, description="Tempo de processamento")