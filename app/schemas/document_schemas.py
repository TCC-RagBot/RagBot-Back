from pydantic import BaseModel, Field
from uuid import UUID


class DocumentUploadResponse(BaseModel):
    document_id: UUID = Field(..., description="ID do documento")
    filename: str = Field(..., description="Nome do arquivo")
    chunks_created: int = Field(..., ge=0, description="Número de chunks criados")
    processing_time: float = Field(..., ge=0.0, description="Tempo de processamento")
    status: str = Field(..., description="Status do processamento")