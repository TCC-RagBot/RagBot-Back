"""
Constantes de configuração do algoritmo RAG.

Este módulo contém constantes relacionadas aos parâmetros do algoritmo RAG,
que são valores fixos no código e não dependem do ambiente.
"""

# Configurações do modelo de embedding
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Configurações de processamento de documentos
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Configurações de busca e retrieval
MAX_CHUNKS_RETRIEVED = 5

# Configurações da aplicação
APP_NAME = "RAGBot"
APP_VERSION = "1.0.0"

# Configurações de servidor (padrões)
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

# Configurações de documentos
DOCUMENTS_FOLDER = "documents"