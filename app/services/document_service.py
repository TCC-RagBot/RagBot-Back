import time
import uuid
from loguru import logger
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..config.constants import MAX_FILE_SIZE_MB, CHUNK_SIZE, CHUNK_OVERLAP
from ..repositories.vector_repository import get_vector_store
from ..repositories.document_repository import document_repository
from ..schemas.chat import DocumentUploadResponse


class DocumentService:
    
    def __init__(self):
        self.vector_store = get_vector_store()
        logger.info("Document service initialized")
    
    def _validate_file(self, content: bytes, filename: str) -> None:
        if not filename.lower().endswith('.pdf'):
            raise ValueError("Apenas arquivos PDF são suportados")
        
        max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_size_bytes:
            raise ValueError(f"Arquivo muito grande. Máximo: {MAX_FILE_SIZE_MB}MB")
        
        if len(content) == 0:
            raise ValueError("Arquivo está vazio")
        
        if document_repository.document_exists(filename):
            raise ValueError(f"Documento '{filename}' já foi processado anteriormente")
        
        logger.info(f"File validation passed: {filename} ({len(content)} bytes)")
    
    def _process_pdf_to_chunks(self, content: bytes, filename: str) -> list:
        logger.info(f"Starting PDF processing: {filename}")
        
        temp_file_path = None
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            loader = PyPDFLoader(temp_file_path)
            
            documents = loader.load()
            logger.info(f"PDF loaded successfully: {len(documents)} pages found")
            
            for doc in documents:
                doc.metadata["file_name"] = filename
                doc.metadata["source"] = "api_upload"
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Document chunked successfully: {len(chunks)} chunks created")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            raise ValueError(f"Erro ao processar PDF: {str(e)}")
        
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"Temporary file cleaned up: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file: {e}")
    
    def _store_chunks_and_embeddings(self, chunks: list, filename: str) -> int:
        try:
            logger.info(f"Storing {len(chunks)} chunks for {filename}")
            
            self.vector_store.vector_store.add_documents(chunks)
            
            logger.success(f"Successfully stored {len(chunks)} chunks with embeddings")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error storing chunks for {filename}: {e}")
            raise ValueError(f"Erro ao armazenar embeddings: {str(e)}")
    
    async def process_document_upload(self, content: bytes, filename: str) -> DocumentUploadResponse:
        start_time = time.time()
        
        try:
            logger.info(f"Starting document upload process: {filename}")
            
            self._validate_file(content, filename)
            
            chunks = self._process_pdf_to_chunks(content, filename)
            
            chunks_stored = self._store_chunks_and_embeddings(chunks, filename)
            
            document_id = document_repository.save_document_metadata(
                filename=filename,
                chunks_count=chunks_stored,
                file_size_bytes=len(content)
            )
            
            processing_time = time.time() - start_time
            
            logger.success(
                f"Document processing completed: {filename} "
                f"({chunks_stored} chunks, {processing_time:.2f}s)"
            )
            
            return DocumentUploadResponse(
                document_id=document_id,
                filename=filename,
                chunks_created=chunks_stored,
                processing_time=processing_time,
                status="success"
            )
            
        except ValueError:
            raise
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Unexpected error processing {filename}: {e}")
            
            return DocumentUploadResponse(
                document_id=uuid.uuid4(),  
                filename=filename,
                chunks_created=0,
                processing_time=processing_time,
                status=f"error: {str(e)}"
            )

document_service = DocumentService()