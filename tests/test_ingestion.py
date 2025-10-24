"""
Testes para o fluxo de ingestão de documentos PDF
"""
import pytest # type: ignore
from pathlib import Path
from unittest.mock import MagicMock, patch
import os
import sys

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

from langchain_community.document_loaders import PyPDFLoader # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
from app.repositories.vector_repository import SentenceTransformerEmbeddings


class TestPDFIngestion:
    """
    Classe de testes para o processo de ingestão de documentos PDF
    """
    
    def test_pdf_loading_with_pypdf(self, test_pdf_path):
        """
        Teste 1: Verificar se o documento PDF é lido corretamente pelo Python
        """
        # Verificar se o arquivo existe
        assert os.path.exists(test_pdf_path), f"Arquivo PDF de teste não encontrado: {test_pdf_path}"
        
        # Carregar o PDF usando PyPDFLoader (mesmo que o script de ingestão usa)
        loader = PyPDFLoader(test_pdf_path)
        documents = loader.load()
        
        # Verificações básicas
        assert documents is not None, "Documentos não foram carregados"
        assert len(documents) > 0, "Nenhuma página foi encontrada no PDF"
        
        # Verificar se cada documento tem conteúdo
        total_chars = 0
        for i, doc in enumerate(documents):
            assert hasattr(doc, 'page_content'), f"Documento {i} não tem atributo 'page_content'"
            assert hasattr(doc, 'metadata'), f"Documento {i} não tem atributo 'metadata'"
            assert len(doc.page_content.strip()) > 0, f"Página {i} está vazia"
            total_chars += len(doc.page_content)
            
        print(f"✅ PDF carregado com sucesso: {len(documents)} páginas, {total_chars} caracteres totais")
    
    def test_document_chunking(self, test_pdf_path):
        """
        Teste 2: Verificar se o documento é transformado em chunks pela biblioteca LangChain
        """
        # Carregar o PDF primeiro
        loader = PyPDFLoader(test_pdf_path)
        documents = loader.load()
        
        # Dividir em chunks usando as mesmas configurações do script
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=150
        )
        chunks = text_splitter.split_documents(documents)
        
        # Verificações
        assert chunks is not None, "Chunks não foram gerados"
        assert len(chunks) > 0, "Nenhum chunk foi criado"
        assert len(chunks) >= len(documents), "Número de chunks deve ser >= número de páginas"
        
        # Verificar propriedades dos chunks e calcular estatísticas
        chunk_sizes = []
        for i, chunk in enumerate(chunks):
            assert hasattr(chunk, 'page_content'), f"Chunk {i} não tem conteúdo"
            assert hasattr(chunk, 'metadata'), f"Chunk {i} não tem metadata"
            assert len(chunk.page_content) <= 1200, f"Chunk {i} muito grande (>1200 chars): {len(chunk.page_content)}"
            assert len(chunk.page_content.strip()) > 0, f"Chunk {i} está vazio"
            chunk_sizes.append(len(chunk.page_content))
        
        avg_size = sum(chunk_sizes) // len(chunk_sizes)
        print(f"✅ Documento dividido em {len(chunks)} chunks (tamanho médio: {avg_size} chars)")
    
    def test_embeddings_generation(self):
        """
        Teste 3: Verificar se são gerados embeddings de 384 dimensões pelo modelo All-mini-LM-l6-v2
        """
        # Criar instância do modelo de embeddings
        embeddings_model = SentenceTransformerEmbeddings()
        
        # Texto de teste
        test_texts = [
            "Este é um texto de exemplo para testar embeddings.",
            "Outro texto para verificar a geração de vetores.",
            "Documento de teste com conteúdo relevante."
        ]
        
        # Gerar embeddings
        embeddings = embeddings_model.embed_documents(test_texts)
        
        # Verificações
        assert embeddings is not None, "Embeddings não foram gerados"
        assert len(embeddings) == len(test_texts), f"Número de embeddings ({len(embeddings)}) != número de textos ({len(test_texts)})"
        
        # Verificar dimensões (All-MiniLM-L6-v2 produz embeddings de 384 dimensões)
        for i, embedding in enumerate(embeddings):
            assert isinstance(embedding, list), f"Embedding {i} não é uma lista"
            assert len(embedding) == 384, f"Embedding {i} tem {len(embedding)} dimensões, esperado 384"
            assert all(isinstance(x, (int, float)) for x in embedding), f"Embedding {i} contém valores não numéricos"
        
        # Testar embedding de query individual
        query_embedding = embeddings_model.embed_query("Texto de consulta de teste")
        assert isinstance(query_embedding, list), "Query embedding não é uma lista"
        assert len(query_embedding) == 384, f"Query embedding tem {len(query_embedding)} dimensões, esperado 384"
        
        # Calcular algumas estatísticas dos embeddings para o print
        first_embedding = embeddings[0]
        min_val = min(first_embedding)
        max_val = max(first_embedding)
        
        print(f"✅ Embeddings gerados com sucesso: {len(embeddings)} vetores de 384D (valores: {min_val:.3f} a {max_val:.3f})")
    
    @patch('app.repositories.vector_repository.LangChainVectorStore')
    def test_database_persistence_mock(self, mock_vector_store_class, test_pdf_path):
        """
        Teste 4: Verificar se os dados são enviados para o banco (usando mock)
        """
        # Configurar mock
        mock_vector_store_instance = MagicMock()
        mock_vector_store_class.return_value.vector_store = mock_vector_store_instance
        
        # Simular o fluxo de ingestão
        from scripts.ingest import ingest_pdf
        
        # Executar a função de ingestão
        ingest_pdf(test_pdf_path)
        
        # Verificar se add_documents foi chamado
        mock_vector_store_instance.add_documents.assert_called_once()
        
        # Verificar se foi chamado com argumentos corretos (lista de documentos)
        call_args = mock_vector_store_instance.add_documents.call_args[0][0]
        assert isinstance(call_args, list), "add_documents deve ser chamado com uma lista"
        assert len(call_args) > 0, "Lista de documentos não pode estar vazia"
        
        print("✅ Persistência no banco mockada com sucesso")
    
    def test_end_to_end_ingestion_flow(self, test_pdf_path):
        """
        Teste 5: Teste de integração completo do fluxo de ingestão
        """
        print("\n🔄 Executando teste end-to-end do fluxo de ingestão...")
        
        # Passo 1: Carregar PDF
        print("📄 Passo 1: Carregando PDF...")
        # Carregar PDF para validação
        loader = PyPDFLoader(test_pdf_path)
        documents = loader.load()
        assert len(documents) > 0, "Nenhum documento foi carregado"
        
        self.test_pdf_loading_with_pypdf(test_pdf_path)
        
        # Passo 2: Criar chunks
        print("✂️ Passo 2: Criando chunks...")
        # Criar chunks para validação
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = text_splitter.split_documents(documents)
        assert len(chunks) > 0, "Nenhum chunk foi gerado"
        
        self.test_document_chunking(test_pdf_path)
        
        # Passo 3: Gerar embeddings
        print("🧮 Passo 3: Gerando embeddings...")
        self.test_embeddings_generation()
        
        print("✅ Teste end-to-end concluído com sucesso!")
        print(f"📊 Resumo: {len(documents)} páginas → {len(chunks)} chunks → pipeline completo!")


if __name__ == "__main__":
    # Permitir execução direta do arquivo de teste
    pytest.main([__file__, "-v"])