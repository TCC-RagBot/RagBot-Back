"""
Funções CRUD para interação com o banco de dados PostgreSQL.

Este módulo contém todas as operações de banco de dados para o sistema RAGBot,
incluindo operações para documentos, chunks, conversas e mensagens.
Utiliza SQLAlchemy para interação com PostgreSQL e pgvector para operações vetoriais.
"""

import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy import create_engine, text, select, insert, update, delete
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import numpy as np
from loguru import logger

from .config import settings


class DatabaseManager:
    """
    Gerenciador de conexões e operações com o banco de dados.
    
    Responsável por todas as operações CRUD e queries vetoriais
    necessárias para o funcionamento do sistema RAG.
    """
    
    def __init__(self):
        """Inicializa o gerenciador do banco de dados."""
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("Database manager initialized")
    
    def get_session(self) -> Session:
        """
        Cria uma nova sessão do banco de dados.
        
        Returns:
            Session: Sessão do SQLAlchemy
        """
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados.
        
        Returns:
            bool: True se a conexão for bem-sucedida
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def create_document(self, filename: str, content: str, metadata: Dict[str, Any] = None) -> uuid.UUID:
        """
        Cria um novo documento no banco de dados.
        
        Args:
            filename: Nome do arquivo
            content: Conteúdo completo do documento
            metadata: Metadados adicionais do documento
            
        Returns:
            UUID: ID do documento criado
        """
        with self.get_session() as session:
            try:
                document_id = uuid.uuid4()
                query = text("""
                    INSERT INTO documents (id, filename, content, metadata, created_at)
                    VALUES (:id, :filename, :content, :metadata, :created_at)
                """)
                
                session.execute(query, {
                    'id': document_id,
                    'filename': filename,
                    'content': content,
                    'metadata': metadata or {},
                    'created_at': datetime.now()
                })
                
                session.commit()
                logger.info(f"Document created with ID: {document_id}")
                return document_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating document: {e}")
                raise
    
    def create_chunk(self, document_id: uuid.UUID, content: str, embedding: List[float], 
                    page_number: Optional[int] = None, metadata: Dict[str, Any] = None) -> uuid.UUID:
        """
        Cria um novo chunk no banco de dados.
        
        Args:
            document_id: ID do documento pai
            content: Conteúdo do chunk
            embedding: Vetor de embedding do chunk
            page_number: Número da página (opcional)
            metadata: Metadados adicionais
            
        Returns:
            UUID: ID do chunk criado
        """
        with self.get_session() as session:
            try:
                chunk_id = uuid.uuid4()
                query = text("""
                    INSERT INTO chunks (id, document_id, content, embedding, page_number, metadata, created_at)
                    VALUES (:id, :document_id, :content, :embedding, :page_number, :metadata, :created_at)
                """)
                
                session.execute(query, {
                    'id': chunk_id,
                    'document_id': document_id,
                    'content': content,
                    'embedding': embedding,
                    'page_number': page_number,
                    'metadata': metadata or {},
                    'created_at': datetime.now()
                })
                
                session.commit()
                logger.debug(f"Chunk created with ID: {chunk_id}")
                return chunk_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating chunk: {e}")
                raise
    
    def similarity_search(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza busca por similaridade vetorial.
        
        Args:
            query_embedding: Vetor de embedding da query
            limit: Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de chunks similares com scores
        """
        with self.get_session() as session:
            try:
                query = text("""
                    SELECT 
                        c.id,
                        c.content,
                        c.page_number,
                        c.metadata,
                        d.filename,
                        1 - (c.embedding <=> :query_embedding) as similarity_score
                    FROM chunks c
                    JOIN documents d ON c.document_id = d.id
                    ORDER BY c.embedding <=> :query_embedding
                    LIMIT :limit
                """)
                
                result = session.execute(query, {
                    'query_embedding': query_embedding,
                    'limit': limit
                })
                
                chunks = []
                for row in result:
                    chunks.append({
                        'chunk_id': row.id,
                        'content': row.content,
                        'page_number': row.page_number,
                        'metadata': row.metadata,
                        'document_name': row.filename,
                        'similarity_score': float(row.similarity_score)
                    })
                
                logger.debug(f"Found {len(chunks)} similar chunks")
                return chunks
                
            except Exception as e:
                logger.error(f"Error in similarity search: {e}")
                raise
    
    def create_conversation(self, user_id: Optional[str] = None) -> uuid.UUID:
        """
        Cria uma nova conversa.
        
        Args:
            user_id: ID do usuário (opcional)
            
        Returns:
            UUID: ID da conversa criada
        """
        with self.get_session() as session:
            try:
                conversation_id = uuid.uuid4()
                query = text("""
                    INSERT INTO conversations (id, user_id, created_at)
                    VALUES (:id, :user_id, :created_at)
                """)
                
                session.execute(query, {
                    'id': conversation_id,
                    'user_id': user_id,
                    'created_at': datetime.now()
                })
                
                session.commit()
                logger.info(f"Conversation created with ID: {conversation_id}")
                return conversation_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating conversation: {e}")
                raise
    
    def create_message(self, conversation_id: uuid.UUID, user_message: str, 
                      assistant_response: str, source_chunks: List[uuid.UUID]) -> uuid.UUID:
        """
        Cria uma nova mensagem na conversa.
        
        Args:
            conversation_id: ID da conversa
            user_message: Mensagem do usuário
            assistant_response: Resposta do assistente
            source_chunks: Lista de IDs dos chunks utilizados como fonte
            
        Returns:
            UUID: ID da mensagem criada
        """
        with self.get_session() as session:
            try:
                message_id = uuid.uuid4()
                
                # Criar a mensagem
                message_query = text("""
                    INSERT INTO messages (id, conversation_id, user_message, assistant_response, created_at)
                    VALUES (:id, :conversation_id, :user_message, :assistant_response, :created_at)
                """)
                
                session.execute(message_query, {
                    'id': message_id,
                    'conversation_id': conversation_id,
                    'user_message': user_message,
                    'assistant_response': assistant_response,
                    'created_at': datetime.now()
                })
                
                # Criar as relações com os chunks
                for chunk_id in source_chunks:
                    source_query = text("""
                        INSERT INTO message_source_chunks (id, message_id, chunk_id, created_at)
                        VALUES (:id, :message_id, :chunk_id, :created_at)
                    """)
                    
                    session.execute(source_query, {
                        'id': uuid.uuid4(),
                        'message_id': message_id,
                        'chunk_id': chunk_id,
                        'created_at': datetime.now()
                    })
                
                session.commit()
                logger.info(f"Message created with ID: {message_id}")
                return message_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating message: {e}")
                raise


# Instância global do gerenciador de banco
db_manager = DatabaseManager()