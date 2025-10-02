"""
Serviços de lógica de negócio para o sistema RAGBot.

Este módulo contém a implementação da lógica principal do sistema RAG,
incluindo processamento de embeddings, geração de respostas e
orquestração dos fluxos de chat e ingestão de documentos.
"""

import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from loguru import logger

from .config import settings
from .crud import db_manager
from .schemas import ChatResponse, SourceChunk


class EmbeddingService:
    """
    Serviço para geração de embeddings utilizando sentence-transformers.
    
    Responsável por converter texto em vetores utilizando o modelo
    especificado nas configurações (all-MiniLM-L6-v2 por padrão).
    """
    
    def __init__(self):
        """Inicializa o serviço de embeddings."""
        self.model = SentenceTransformer(settings.embedding_model_name)
        logger.info(f"Embedding service initialized with model: {settings.embedding_model_name}")
    
    def encode_text(self, text: str) -> List[float]:
        """
        Converte texto em vetor de embedding.
        
        Args:
            text: Texto a ser convertido
            
        Returns:
            List[float]: Vetor de embedding
        """
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            raise
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Converte uma lista de textos em embeddings.
        
        Args:
            texts: Lista de textos
            
        Returns:
            List[List[float]]: Lista de vetores de embedding
        """
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error encoding batch: {e}")
            raise


class DocumentProcessingService:
    """
    Serviço para processamento de documentos e criação de chunks.
    
    Utiliza LangChain para dividir documentos em pedaços menores
    e prepará-los para armazenamento vetorial.
    """
    
    def __init__(self):
        """Inicializa o serviço de processamento de documentos."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        self.embedding_service = EmbeddingService()
        logger.info("Document processing service initialized")
    
    def process_text(self, text: str, filename: str, metadata: Dict[str, Any] = None) -> uuid.UUID:
        """
        Processa um texto completo, criando documento e chunks.
        
        Args:
            text: Conteúdo completo do documento
            filename: Nome do arquivo
            metadata: Metadados adicionais
            
        Returns:
            UUID: ID do documento criado
        """
        try:
            # Criar documento no banco
            document_id = db_manager.create_document(filename, text, metadata)
            
            # Dividir texto em chunks
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Created {len(chunks)} chunks for document {filename}")
            
            # Processar cada chunk
            chunk_texts = []
            for i, chunk_content in enumerate(chunks):
                chunk_texts.append(chunk_content)
            
            # Gerar embeddings em batch
            embeddings = self.embedding_service.encode_batch(chunk_texts)
            
            # Salvar chunks no banco
            for i, (chunk_content, embedding) in enumerate(zip(chunk_texts, embeddings)):
                chunk_metadata = {"chunk_index": i, "total_chunks": len(chunks)}
                if metadata:
                    chunk_metadata.update(metadata)
                
                db_manager.create_chunk(
                    document_id=document_id,
                    content=chunk_content,
                    embedding=embedding,
                    metadata=chunk_metadata
                )
            
            logger.info(f"Document {filename} processed successfully")
            return document_id
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise


class ChatService:
    """
    Serviço principal para o sistema de chat RAG.
    
    Orquestra o fluxo completo: recebe pergunta, busca chunks relevantes,
    gera prompt e obtém resposta da OpenAI.
    """
    
    def __init__(self):
        """Inicializa o serviço de chat."""
        self.embedding_service = EmbeddingService()
        # Configurar Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Inicializar LangChain vector store
        from .langchain_vector import get_vector_store
        self.vector_store = get_vector_store()
        
        logger.info("Chat service initialized with Gemini and LangChain")
    
    def _build_prompt(self, user_question: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        Constrói o prompt para a OpenAI com base na pergunta e chunks relevantes.
        
        Args:
            user_question: Pergunta do usuário
            relevant_chunks: Lista de chunks relevantes
            
        Returns:
            str: Prompt formatado
        """
        context = "\n\n".join([
            f"Documento: {chunk['document_name']}\nConteúdo: {chunk['content']}"
            for chunk in relevant_chunks
        ])
        
        prompt = f"""Você é um assistente especializado em responder perguntas baseadas exclusivamente no conteúdo dos documentos fornecidos.

INSTRUÇÕES:
1. Responda APENAS com base no conteúdo dos documentos fornecidos abaixo
2. Se a pergunta não puder ser respondida com base nos documentos, diga claramente que não há informações suficientes
3. Cite sempre os documentos utilizados na resposta
4. Seja preciso e objetivo

CONTEXTO DOS DOCUMENTOS:
{context}

PERGUNTA DO USUÁRIO:
{user_question}

RESPOSTA:"""
        
        return prompt
    
    async def process_chat(self, user_message: str, conversation_id: Optional[uuid.UUID] = None,
                          max_chunks: int = None) -> ChatResponse:
        """
        Processa uma mensagem de chat e retorna a resposta.
        
        Args:
            user_message: Mensagem do usuário
            conversation_id: ID da conversa (opcional)
            max_chunks: Número máximo de chunks a recuperar
            
        Returns:
            ChatResponse: Resposta estruturada do chat
        """
        start_time = time.time()
        
        try:
            # Criar nova conversa se necessário
            if not conversation_id:
                conversation_id = db_manager.create_conversation()
            
            # Buscar chunks relevantes usando LangChain PostgreSQL
            chunk_limit = max_chunks or settings.max_chunks_retrieved
            relevant_chunks = self.vector_store.similarity_search_with_score(user_message, k=chunk_limit)
            
            if not relevant_chunks:
                logger.warning("No relevant chunks found for query")
                response_text = "Desculpe, não encontrei informações relevantes nos documentos disponíveis para responder sua pergunta."
                source_chunks = []
            else:
                # Construir prompt
                prompt = self._build_prompt(user_message, relevant_chunks)
                
                # Gerar resposta com Gemini
                response = self.model.generate_content(prompt)
                response_text = response.text
                
                # Preparar chunks de origem
                source_chunks = [
                    SourceChunk(
                        chunk_id=chunk['chunk_id'],
                        content=chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                        document_name=chunk['document_name'],
                        page_number=chunk.get('page_number'),
                        similarity_score=chunk['similarity_score']
                    )
                    for chunk in relevant_chunks
                ]
            
            # Salvar mensagem no banco
            source_chunk_ids = [chunk['chunk_id'] for chunk in relevant_chunks]
            message_id = db_manager.create_message(
                conversation_id=conversation_id,
                user_message=user_message,
                assistant_response=response_text,
                source_chunks=source_chunk_ids
            )
            
            processing_time = time.time() - start_time
            
            return ChatResponse(
                response=response_text,
                conversation_id=conversation_id,
                message_id=message_id,
                sources=source_chunks,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            raise


# Instâncias globais dos serviços
embedding_service = EmbeddingService()
document_processing_service = DocumentProcessingService()
chat_service = ChatService()