"""
Script de ingestão de documentos PDF para o sistema RAGBot.

Este script processa arquivos PDF de uma pasta local, divide o conteúdo
em chunks, gera embeddings e armazena tudo no banco de dados PostgreSQL
com pgvector para futuras consultas de similaridade.

Uso:
    python scripts/ingest.py --pdf-path caminho/para/arquivo.pdf
    python scripts/ingest.py --pdf-folder caminho/para/pasta/
"""

import os
import sys
import argparse
import time
from pathlib import Path
from typing import List, Optional

# Adicionar o diretório pai ao path para importar módulos da app
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from pypdf import PdfReader

from app.config import settings
from app.services import document_processing_service
from app.crud import db_manager


class PDFIngestService:
    """
    Serviço especializado para ingestão de documentos PDF.
    
    Responsável por ler arquivos PDF, extrair texto e
    processá-los através do sistema de chunks e embeddings.
    """
    
    def __init__(self):
        """Inicializa o serviço de ingestão."""
        logger.info("PDF Ingest Service initialized")
    
    def extract_text_from_pdf(self, pdf_path: str) -> tuple[str, dict]:
        """
        Extrai texto de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            tuple: (texto_completo, metadados)
        """
        try:
            reader = PdfReader(pdf_path)
            
            # Extrair metadados
            metadata = {
                "num_pages": len(reader.pages),
                "file_size": os.path.getsize(pdf_path),
                "file_path": pdf_path
            }
            
            # Adicionar metadados do PDF se disponíveis
            if reader.metadata:
                metadata.update({
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                    "subject": reader.metadata.get("/Subject", ""),
                    "creator": reader.metadata.get("/Creator", "")
                })
            
            # Extrair texto de todas as páginas
            full_text = ""
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        full_text += f"\n\n--- Página {page_num} ---\n\n"
                        full_text += page_text
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    continue
            
            if not full_text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            logger.info(f"Extracted {len(full_text)} characters from {metadata['num_pages']} pages")
            return full_text.strip(), metadata
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            raise
    
    def process_pdf_file(self, pdf_path: str) -> str:
        """
        Processa um único arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            str: ID do documento criado
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            start_time = time.time()
            
            # Verificar se arquivo existe
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Extrair texto e metadados
            text, metadata = self.extract_text_from_pdf(pdf_path)
            
            # Obter nome do arquivo
            filename = os.path.basename(pdf_path)
            
            # Processar documento (criar chunks e embeddings)
            document_id = document_processing_service.process_text(
                text=text,
                filename=filename,
                metadata=metadata
            )
            
            processing_time = time.time() - start_time
            logger.success(
                f"PDF processed successfully in {processing_time:.2f}s - "
                f"Document ID: {document_id}"
            )
            
            return str(document_id)
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
    
    def process_pdf_folder(self, folder_path: str) -> List[str]:
        """
        Processa todos os arquivos PDF de uma pasta.
        
        Args:
            folder_path: Caminho para a pasta com PDFs
            
        Returns:
            List[str]: Lista de IDs dos documentos criados
        """
        try:
            folder = Path(folder_path)
            if not folder.exists() or not folder.is_dir():
                raise ValueError(f"Folder not found or not a directory: {folder_path}")
            
            # Encontrar todos os arquivos PDF
            pdf_files = list(folder.glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"No PDF files found in {folder_path}")
                return []
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            # Processar cada arquivo
            document_ids = []
            for pdf_file in pdf_files:
                try:
                    doc_id = self.process_pdf_file(str(pdf_file))
                    document_ids.append(doc_id)
                except Exception as e:
                    logger.error(f"Failed to process {pdf_file}: {e}")
                    continue
            
            logger.success(f"Successfully processed {len(document_ids)} out of {len(pdf_files)} PDFs")
            return document_ids
            
        except Exception as e:
            logger.error(f"Error processing PDF folder {folder_path}: {e}")
            raise


def main():
    """Função principal do script de ingestão."""
    parser = argparse.ArgumentParser(
        description="Ingest PDF documents into RAGBot database"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--pdf-path",
        type=str,
        help="Path to a single PDF file to process"
    )
    group.add_argument(
        "--pdf-folder", 
        type=str,
        help="Path to folder containing PDF files to process"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    try:
        # Verificar conexão com banco de dados
        logger.info("Testing database connection...")
        if not db_manager.test_connection():
            logger.error("Failed to connect to database. Check your DATABASE_URL.")
            sys.exit(1)
        
        # Inicializar serviço de ingestão
        ingest_service = PDFIngestService()
        
        # Processar PDFs
        if args.pdf_path:
            logger.info(f"Processing single PDF: {args.pdf_path}")
            document_id = ingest_service.process_pdf_file(args.pdf_path)
            logger.success(f"Document created with ID: {document_id}")
            
        elif args.pdf_folder:
            logger.info(f"Processing PDF folder: {args.pdf_folder}")
            document_ids = ingest_service.process_pdf_folder(args.pdf_folder)
            logger.success(f"Created {len(document_ids)} documents")
            
            if document_ids:
                logger.info("Document IDs created:")
                for doc_id in document_ids:
                    logger.info(f"  - {doc_id}")
        
        logger.success("Ingest process completed successfully!")
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ingest process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()