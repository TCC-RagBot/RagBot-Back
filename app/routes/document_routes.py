from fastapi import APIRouter, HTTPException, status, File, UploadFile
from loguru import logger

from ..schemas.document_schemas import DocumentUploadResponse
from ..services.document_service import document_service

router = APIRouter()


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