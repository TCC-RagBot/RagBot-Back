"""
Integração com LangChain PostgreSQL para busca vetorial.
"""

from typing import List, Dict, Any
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import DistanceStrategy
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from loguru import logger

from ..config.settings import settings
from ..config.constants import EMBEDDING_MODEL_NAME

class SentenceTransformerEmbeddings(Embeddings):
    """
    Wrapper para sentence-transformers compatível com LangChain.
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info(f"SentenceTransformer embeddings initialized: {model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating document embeddings: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise


class LangChainVectorStore:
    
    def __init__(self):
        self.embeddings = SentenceTransformerEmbeddings(EMBEDDING_MODEL_NAME)
        
        db_url = settings.database_url
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        self.connection_string = db_url
        
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            connection=self.connection_string,
            collection_name="ragbot_chunks",
            distance_strategy=DistanceStrategy.COSINE,
            use_jsonb=True
        )
        
        self._ensure_vector_tables_exist()
        
        logger.info("LangChain vector store initialized")
    
    def _ensure_vector_tables_exist(self):
        try:
            self.vector_store.similarity_search("test", k=1)
        except Exception as e:
            logger.debug(f"Vector tables will be created on first use: {e}")
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
       
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'chunk_id': doc.metadata.get('chunk_id'),
                    'content': doc.page_content,
                    'document_name': doc.metadata.get('file_name', 'Documento desconhecido'),
                    'similarity_score': 1 - score, 
                    'metadata': doc.metadata
                })
            
            logger.debug(f"Found {len(formatted_results)} similar chunks")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def add_documents_from_db(self, chunks_data: List[Dict[str, Any]]):
        try:
            documents = []
            for chunk in chunks_data:
                doc = Document(
                    page_content=chunk['content'],
                    metadata={
                        'chunk_id': str(chunk['id']),
                        'document_name': chunk['document_name'],
                        'document_id': str(chunk['document_id'])
                    }
                )
                documents.append(doc)
            
            if documents:
                self.vector_store.add_documents(documents)
                logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise


langchain_vector_store = None

def get_vector_store() -> LangChainVectorStore:
    global langchain_vector_store
    if langchain_vector_store is None:
        langchain_vector_store = LangChainVectorStore()
    return langchain_vector_store