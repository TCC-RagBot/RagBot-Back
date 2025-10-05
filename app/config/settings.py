"""
Configurações da aplicação RAGBot.

Contém apenas as configurações essenciais de infraestrutura e ambiente.
Parâmetros específicos de algoritmos estão definidos como constantes no código.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações de infraestrutura da aplicação RAGBot.
    
    Carrega apenas configurações críticas do ambiente (secrets, URLs, etc).
    """
    database_url: str
    gemini_api_key: str
    secret_key: str
    debug: bool = False
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()