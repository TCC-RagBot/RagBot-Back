"""
Configurações da aplicação RAGBot.

Este módulo contém todas as configurações necessárias para a aplicação,
incluindo configurações de banco de dados, API keys, e parâmetros do sistema RAG.
Utiliza Pydantic Settings para validação e carregamento das variáveis de ambiente.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Classe de configurações da aplicação RAGBot.
    
    Carrega as configurações de variáveis de ambiente utilizando Pydantic Settings.
    Todas as configurações são validadas automaticamente.
    """
    
    # Configurações da aplicação
    app_name: str = "aaa"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Configurações do banco de dados
    database_url: str
    
    # Configurações da Gemini AI
    gemini_api_key: str
    
    # Configurações do modelo de embedding
    embedding_model_name: str = "all-MiniLM-L6-v2"
    
    # Configurações do chat/RAG
    max_chunks_retrieved: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Configurações do servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Configurações de segurança
    secret_key: str
    
    # Configurações de logging
    log_level: str = "INFO"
    
    # Configurações de documentos
    documents_folder: str = "documents"
    
    class Config:
        """Configuração do Pydantic Settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instância global das configurações
settings = Settings()