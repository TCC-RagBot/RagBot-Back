from pydantic import BaseModel, Field
from uuid import UUID
from typing import List

class DocumentUploadResponse(BaseModel):
    document_id: UUID = Field(..., description="ID do documento")
    filename: str = Field(..., description="Nome do arquivo")
    chunks_created: int = Field(..., ge=0, description="Número de chunks criados")
    processing_time: float = Field(..., ge=0.0, description="Tempo de processamento")
    status: str = Field(..., description="Status do processamento")

class DocumentInfo(BaseModel):
    id: UUID = Field(..., description="ID do documento")
    filename: str = Field(..., description="Nome do arquivo")
    file_size_kb: float = Field(..., ge=0.0, description="Tamanho do arquivo em KB")
    uploaded_at: str = Field(..., description="Data de upload no formato brasileiro")

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo] = Field(..., description="Lista de documentos")
    total_documents: int = Field(..., ge=0, description="Total de documentos")

class DocumentDeleteResponse(BaseModel):
    document_id: UUID = Field(..., description="ID do documento excluído")
    filename: str = Field(..., description="Nome do arquivo excluído")
    message: str = Field(..., description="Mensagem de confirmação")
    success: bool = Field(..., description="Status da exclusão")