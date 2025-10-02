"""
Integração com LangChain PostgreSQL para busca vetorial.

Este módulo implementa a integração com langchain-postgres para realizar
busca por similaridade usando pgvector de forma otimizada.
"""

from typing import List, Dict, Any, Optional
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import DistanceStrategy
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
import numpy as np
from loguru import logger

from .config import settings


class SentenceTransformerEmbeddings(Embeddings):
    """
    Wrapper para sentence-transformers compatível com LangChain.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info(f"SentenceTransformer embeddings initialized: {model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de documentos."""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating document embeddings: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Gera embedding para uma query."""
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise


class LangChainVectorStore:
    """
    Gerenciador de vector store usando LangChain PostgreSQL.
    """
    
    def __init__(self):
        """Inicializa o vector store."""
        self.embeddings = SentenceTransformerEmbeddings(settings.embedding_model_name)
        
        # Configurar connection string para langchain-postgres
        # Garantir que usa o formato postgresql://
        db_url = settings.database_url
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://')
        
        self.connection_string = db_url
        
        # Inicializar PGVector
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            connection=self.connection_string,
            collection_name="ragbot_chunks",
            distance_strategy=DistanceStrategy.COSINE,
            use_jsonb=True
        )
        
        logger.info("LangChain vector store initialized")
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza busca por similaridade com scores.
        
        Args:
            query: Texto da consulta
            k: Número de resultados
            
        Returns:
            List[Dict]: Resultados com scores
        """
        try:
            # Usar o método nativo do PGVector
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'chunk_id': doc.metadata.get('chunk_id'),
                    'content': doc.page_content,
                    'document_name': doc.metadata.get('document_name'),
                    'similarity_score': 1 - score,  # Converter distance para similarity
                    'metadata': doc.metadata
                })
            
            logger.debug(f"Found {len(formatted_results)} similar chunks")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def add_documents_from_db(self, chunks_data: List[Dict[str, Any]]):
        """
        Adiciona documentos existentes do banco para o vector store.
        
        Args:
            chunks_data: Lista de dados dos chunks do banco
        """
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


# Instância global do vector store
langchain_vector_store = None

def get_vector_store() -> LangChainVectorStore:
    """
    Retorna instância singleton do vector store.
    """
    global langchain_vector_store
    if langchain_vector_store is None:
        langchain_vector_store = LangChainVectorStore()
    return langchain_vector_store