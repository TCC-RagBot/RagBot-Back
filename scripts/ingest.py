import os
import sys
from pathlib import Path
import argparse
from loguru import logger

# Adicionar o diretório pai ao path para importar módulos da app
sys.path.append(str(Path(__file__).parent.parent))

from app.repositories.vector_repository import get_vector_store # Importa a função que busca nossa instância do PGVector
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
    
    # 1. Carregar o PDF usando o loader do LangChain
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    logger.info(f"Documento carregado, {len(documents)} páginas encontradas.")

    # Adicionar metadados úteis (nome do arquivo) a cada página/documento
    for doc in documents:
        doc.metadata["file_name"] = os.path.basename(pdf_path)

    # 2. Dividir o documento em chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Documento dividido em {len(chunks)} chunks.")

    # 3. Adicionar os chunks ao PGVector
    # Esta única função cuida de gerar os embeddings e salvar no banco de dados
    vector_store = get_vector_store().vector_store
    vector_store.add_documents(chunks)
    
    logger.success(f"Documento '{pdf_path}' foi processado e salvo no banco de dados com sucesso!")

def main():
    parser = argparse.ArgumentParser(description="Ingestor de documentos PDF para o RAGBot.")
    parser.add_argument("pdf_path", type=str, help="Caminho para o arquivo PDF a ser processado.")
    args = parser.parse_args()
    
    ingest_pdf(args.pdf_path)

if __name__ == "__main__":
    main()