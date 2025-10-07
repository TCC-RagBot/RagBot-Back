"""
Operações mínimas de banco de dados para conversas e mensagens.

Este módulo contém apenas as operações essenciais que não são cobertas
pelo LangChain, focando em conversas e mensagens do sistema de chat.
"""

import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from ..config.settings import settings


class MinimalDatabaseManager:
    """
    Gerenciador minimalista para operações de conversa e mensagens.
    
    Operações de documentos e chunks são gerenciadas pelo LangChain.
    """
    
    def __init__(self):
        """Inicializa o gerenciador do banco de dados."""
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("Minimal database manager initialized")
    
    def get_session(self) -> Session:
        """Cria uma nova sessão do banco de dados."""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def create_conversation(self, user_id: Optional[str] = None) -> uuid.UUID:
        """Cria uma nova conversa."""
        with self.get_session() as session:
            try:
                conversation_id = uuid.uuid4()
                query = text("""
                    INSERT INTO conversations (id, created_at)
                    VALUES (:id, :created_at)
                """)
                
                session.execute(query, {
                    'id': conversation_id,
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
                      assistant_response: str, source_chunks: List = None) -> uuid.UUID:
        """Cria mensagens na conversa (user + assistant)."""
        with self.get_session() as session:
            try:
                # Criar mensagem do usuário
                user_message_id = uuid.uuid4()
                user_query = text("""
                    INSERT INTO messages (id, conversation_id, role, content, created_at)
                    VALUES (:id, :conversation_id, :role, :content, :created_at)
                """)
                
                session.execute(user_query, {
                    'id': user_message_id,
                    'conversation_id': conversation_id,
                    'role': 'user',
                    'content': user_message,
                    'created_at': datetime.now()
                })
                
                # Criar mensagem do assistente
                assistant_message_id = uuid.uuid4()
                assistant_query = text("""
                    INSERT INTO messages (id, conversation_id, role, content, created_at)
                    VALUES (:id, :conversation_id, :role, :content, :created_at)
                """)
                
                session.execute(assistant_query, {
                    'id': assistant_message_id,
                    'conversation_id': conversation_id,
                    'role': 'assistant',
                    'content': assistant_response,
                    'created_at': datetime.now()
                })
                
                session.commit()
                logger.info(f"Messages created - User: {user_message_id}, Assistant: {assistant_message_id}")
                return assistant_message_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating message: {e}")
                raise


# Instância global do gerenciador minimalista
db_manager = MinimalDatabaseManager()