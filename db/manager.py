from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from app.config.settings import settings


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("Database manager initialized")
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

db_manager = DatabaseManager()