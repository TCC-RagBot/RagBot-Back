"""
Modelos de dados Pydantic para a API RAGBot.

Este módulo define os esquemas de dados (schemas) utilizados pela API
para validação de requests e responses. Utiliza Pydantic para garantir
a integridade e validação dos dados.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class ChatRequest(BaseModel):
    """
    Schema para requisições de chat.
    
    Attributes:
        message: A mensagem/pergunta do usuário
        conversation_id: ID opcional da conversa (para continuidade)
        max_chunks: Número máximo de chunks a recuperar (opcional)
    """
    message: str = Field(..., min_length=1, max_length=1000, description="Mensagem do usuário")
    conversation_id: Optional[UUID] = Field(None, description="ID da conversa")
    max_chunks: Optional[int] = Field(5, ge=1, le=10, description="Máximo de chunks a recuperar")


class SourceChunk(BaseModel):
    """
    Schema para chunks de origem utilizados na resposta.
    
    Attributes:
        content: Conteúdo do chunk
        document_name: Nome do documento de origem
        page_number: Número da página (se aplicável)
        similarity_score: Score de similaridade com a pergunta
    """
    content: str = Field(..., description="Conteúdo do chunk")
    document_name: str = Field(..., description="Nome do documento")
    page_number: Optional[int] = Field(None, description="Número da página")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Score de similaridade")


class ChatResponse(BaseModel):
    """
    Schema para respostas de chat.
    
    Attributes:
        response: Resposta gerada pelo sistema
        conversation_id: ID da conversa
        message_id: ID da mensagem
        sources: Lista de chunks utilizados como fonte
        processing_time: Tempo de processamento em segundos
    """
    response: str = Field(..., description="Resposta gerada")
    conversation_id: UUID = Field(..., description="ID da conversa")
    message_id: UUID = Field(..., description="ID da mensagem")
    sources: List[SourceChunk] = Field(default_factory=list, description="Chunks de origem")
    processing_time: float = Field(..., ge=0.0, description="Tempo de processamento")


class DocumentUploadResponse(BaseModel):
    """
    Schema para resposta de upload de documento.
    
    Attributes:
        document_id: ID único do documento processado
        filename: Nome do arquivo
        chunks_created: Número de chunks criados
        processing_time: Tempo de processamento
        status: Status do processamento
    """
    document_id: UUID = Field(..., description="ID do documento")
    filename: str = Field(..., description="Nome do arquivo")
    chunks_created: int = Field(..., ge=0, description="Número de chunks criados")
    processing_time: float = Field(..., ge=0.0, description="Tempo de processamento")
    status: str = Field(..., description="Status do processamento")


class HealthResponse(BaseModel):
    """
    Schema para resposta de health check.
    
    Attributes:
        status: Status da aplicação
        timestamp: Timestamp da verificação
        version: Versão da aplicação
        database_status: Status da conexão com o banco
    """
    status: str = Field(..., description="Status da aplicação")
    timestamp: str = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da aplicação")
    database_status: str = Field(..., description="Status do banco de dados")


class ErrorResponse(BaseModel):
    """
    Schema para respostas de erro.
    
    Attributes:
        error: Mensagem de erro
        detail: Detalhes adicionais do erro
        timestamp: Timestamp do erro
    """
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes do erro")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp do erro")