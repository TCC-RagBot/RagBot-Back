import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import text
from loguru import logger
from db.manager import db_manager

class DocumentRepository:
    def __init__(self):
        self.db_manager = db_manager
        logger.info("Document repository initialized")
    
    def document_exists(self, filename: str) -> bool:
        with self.db_manager.get_session() as session:
            try:
                query = text("""
                    SELECT COUNT(*) as count
                    FROM documents 
                    WHERE filename = :filename
                """)
                
                result = session.execute(query, {'filename': filename})
                count = result.scalar()
                
                exists = count > 0
                logger.debug(f"Document exists check for '{filename}': {exists}")
                return exists
                
            except Exception as e:
                logger.warning(f"Error checking document existence (assuming false): {e}")
                return False
    

    
    def save_document_metadata(self, filename: str, chunks_count: int, 
                             file_size_bytes: int) -> uuid.UUID:
        with self.db_manager.get_session() as session:
            try:
                document_id = uuid.uuid4()
                
                query = text("""
                    INSERT INTO documents (id, filename, chunks_count, file_size_bytes, processed_at, created_at)
                    VALUES (:id, :filename, :chunks_count, :file_size_bytes, :processed_at, :created_at)
                """)
                
                session.execute(query, {
                    'id': document_id,
                    'filename': filename,
                    'chunks_count': chunks_count,
                    'file_size_bytes': file_size_bytes,
                    'processed_at': datetime.now(),
                    'created_at': datetime.now()
                })
                
                session.commit()
                
                logger.info(f"Document metadata saved: {filename} ({chunks_count} chunks)")
                
                return document_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error saving document metadata: {e}")
                raise
    
    def get_document_info(self, document_id: uuid.UUID) -> Optional[dict]:
        with self.db_manager.get_session() as session:
            try:
                query = text("""
                    SELECT id, filename, chunks_count, file_size_bytes, 
                           processed_at, created_at
                    FROM documents 
                    WHERE id = :document_id
                """)
                
                result = session.execute(query, {'document_id': document_id})
                row = result.fetchone()
                
                if row:
                    return {
                        'id': row.id,
                        'filename': row.filename,
                        'chunks_count': row.chunks_count,
                        'file_size_bytes': row.file_size_bytes,
                        'processed_at': row.processed_at,
                        'created_at': row.created_at
                    }
                
                return None
                
            except Exception as e:
                logger.error(f"Error getting document info: {e}")
                return None

document_repository = DocumentRepository()