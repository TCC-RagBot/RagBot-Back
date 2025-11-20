import os
import sys
from pathlib import Path
import argparse
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))

from app.repositories.vector_repository import get_vector_store
from app.repositories.document_repository import DocumentRepository
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def ingest_pdf(pdf_path: str):
    """
    Processa um único arquivo PDF e o adiciona ao vector store do LangChain.
    """
    if not os.path.exists(pdf_path):
        logger.error(f"Arquivo não encontrado: {pdf_path}")
        return

    logger.info(f"Iniciando processamento do arquivo: {pdf_path}")
    
    filename = os.path.basename(pdf_path)
    file_size_bytes = os.path.getsize(pdf_path)
    
    # Verificar se o documento já foi processado
    doc_repo = DocumentRepository()
    if doc_repo.document_exists(filename):
        logger.warning(f"Documento '{filename}' já existe no banco de dados. Abortando.")
        return
    
    # 1. Carregar o PDF usando o loader do LangChain
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    logger.info(f"Documento carregado, {len(documents)} páginas encontradas.")

    # Adicionar metadados úteis (nome do arquivo) a cada página/documento
    for doc in documents:
        doc.metadata["file_name"] = filename

    # 2. Dividir o documento em chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Documento dividido em {len(chunks)} chunks.")

    # 3. Adicionar os chunks ao PGVector
    # Esta única função cuida de gerar os embeddings e salvar no banco de dados
    vector_store = get_vector_store().vector_store
    vector_store.add_documents(chunks)
    
    # 4. Salvar metadados do documento na tabela documents
    document_id = doc_repo.save_document_metadata(
        filename=filename,
        chunks_count=len(chunks),
        file_size_bytes=file_size_bytes
    )
    
    logger.success(f"Documento '{filename}' processado com sucesso!")
    logger.success(f"  - ID: {document_id}")
    logger.success(f"  - Chunks: {len(chunks)}")
    logger.success(f"  - Tamanho: {file_size_bytes} bytes")

def main():
    parser = argparse.ArgumentParser(description="Ingestor de documentos PDF para o RAGBot.")
    parser.add_argument("pdf_path", type=str, help="Caminho para o arquivo PDF a ser processado.")
    args = parser.parse_args()
    
    ingest_pdf(args.pdf_path)

if __name__ == "__main__":
    main()