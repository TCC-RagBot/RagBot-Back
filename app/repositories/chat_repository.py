import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy import text
from loguru import logger

from db.manager import db_manager


class ChatRepository:
    def __init__(self):
        self.db_manager = db_manager
        logger.info("Chat repository initialized")
    
    def create_conversation(self, user_id: Optional[str] = None) -> uuid.UUID:
        with self.db_manager.get_session() as session:
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
        with self.db_manager.get_session() as session:
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