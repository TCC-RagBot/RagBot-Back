# 🧪 Testes do RagBot-Back

Este diretório contém a suíte de testes para validar o funcionamento do sistema de ingestão de documentos PDF e geração de embeddings do RagBot.

## 📋 Estrutura dos Testes

### Arquivos Principais

- **`test_ingestion.py`** - Testes principais do fluxo de ingestão de PDFs
- **`conftest.py`** - Configurações e fixtures compartilhadas pelos testes
- **`README.md`** - Esta documentação

### Testes Implementados

1. **`test_pdf_loading_with_pypdf`** 📄
   - Verifica se documentos PDF são carregados corretamente
   - Valida metadados e conteúdo das páginas

2. **`test_document_chunking`** ✂️
   - Testa a divisão de documentos em chunks menores
   - Verifica configurações de tamanho e overlap

3. **`test_embeddings_generation`** 🧮
   - Valida a geração de embeddings de 384 dimensões
   - Testa o modelo SentenceTransformer All-MiniLM-L6-v2

4. **`test_database_persistence_mock`** 💾
   - Testa a persistência no banco de dados (com mock)
   - Verifica chamadas corretas ao vector store

5. **`test_end_to_end_ingestion_flow`** 🔄
   - Teste de integração completo do pipeline
   - Valida todo o fluxo desde PDF até embeddings

## 🚀 Como Executar os Testes

### Pré-requisitos

1. **Ambiente Virtual Ativado**:
   ```bash
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

2. **Dependências Instaladas**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Arquivo de Teste**: Certifique-se de que existe o arquivo `pdf-test.pdf` na raiz do projeto.

### Comandos de Execução

#### Executar Todos os Testes
```bash
# Modo básico
python -m pytest tests/

# Com saída verbosa
python -m pytest tests/ -v

# Com prints dos testes visíveis
python -m pytest tests/ -v -s
```

#### Executar Teste Específico
```bash
# Executar apenas um teste
python -m pytest tests/test_ingestion.py::TestPDFIngestion::test_pdf_loading_with_pypdf -v -s

# Executar teste end-to-end
python -m pytest tests/test_ingestion.py::TestPDFIngestion::test_end_to_end_ingestion_flow -v -s
```

#### Executar com Relatório de Cobertura
```bash
# Instalar pytest-cov se necessário
pip install pytest-cov

# Executar com cobertura
python -m pytest tests/ --cov=app --cov-report=html
```

## 📊 Saída Esperada dos Testes

Quando os testes executam com sucesso, você verá saídas como:

```
✅ PDF carregado com sucesso: 1 páginas, 3219 caracteres totais
✅ Documento dividido em 4 chunks (tamanho médio: 912 chars)
✅ Embeddings gerados com sucesso: 3 vetores de 384D (valores: -0.141 a 0.152)
✅ Persistência no banco mockada com sucesso

🔄 Executando teste end-to-end do fluxo de ingestão...
📄 Passo 1: Carregando PDF...
✂️ Passo 2: Criando chunks...
🧮 Passo 3: Gerando embeddings...
✅ Teste end-to-end concluído com sucesso!
📊 Resumo: 1 páginas → 4 chunks → pipeline completo!

======================== 5 passed in 10.52s ========================
```

## ⚙️ Configurações de Teste

### Fixtures Disponíveis (conftest.py)

- **`test_pdf_path`**: Caminho para o arquivo PDF de teste
- **`mock_database`**: Mock para operações de banco de dados
- **`setup_test_environment`**: Configuração global do ambiente de teste

### Variáveis de Ambiente para Teste

Os testes configuram automaticamente as seguintes variáveis:

```python
DATABASE_URL="postgresql://test:test@localhost/test"
GOOGLE_API_KEY="test-key"
```

## 🔧 Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
# Verifique se está no ambiente virtual correto
which python
pip list | grep langchain
```

### Erro: "PDF de teste não encontrado"
```bash
# Certifique-se de que o arquivo existe na raiz
ls -la pdf-test.pdf
```

### Erro: "Dependências não instaladas"
```bash
# Reinstale as dependências
pip install -r requirements.txt --upgrade
```

### Performance Lenta
- O primeiro teste de embeddings pode ser mais lento (download do modelo)
- Testes subsequentes são mais rápidos devido ao cache

## 📝 Adicionando Novos Testes

Para adicionar novos testes:

1. **Crie métodos na classe `TestPDFIngestion`**:
   ```python
   def test_nova_funcionalidade(self, test_pdf_path):
       """Descrição do teste"""
       # Seu código de teste aqui
       assert condição, "Mensagem de erro"
   ```

2. **Use fixtures do conftest.py** quando necessário

3. **Mantenha prints informativos** mas concisos

4. **Execute os testes** para validar:
   ```bash
   python -m pytest tests/ -v -s
   ```

## 📚 Documentação Adicional

- [Documentação do pytest](https://docs.pytest.org/)
- [LangChain Testing](https://python.langchain.com/docs/guides/testing/)
- [SentenceTransformers](https://www.sbert.net/)

---

**Última atualização**: 7 de outubro de 2025