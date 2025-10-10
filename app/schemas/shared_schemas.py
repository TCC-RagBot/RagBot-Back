from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HealthResponse(BaseModel):
    status: str = Field(..., description="Status da aplicação")
    timestamp: str = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da aplicação")
    database_status: str = Field(..., description="Status do banco de dados")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes do erro")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp do erro")


class SourceChunk(BaseModel):
    content: str = Field(..., description="Conteúdo do chunk")
    document_name: str = Field(..., description="Nome do documento")
    page_number: Optional[int] = Field(None, description="Número da página")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Score de similaridade")