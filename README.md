# RAGBot Backend

Backend API para sistema RAG (Retrieval-Augmented Generation) desenvolvido como TCC de Engenharia de Software.

## 📋 Descrição

O RAGBot é um sistema que permite ingestão de documentos PDF e chat interativo baseado exclusivamente no conteúdo dos documentos processados. Utiliza embeddings para busca semântica e integração com OpenAI para geração de respostas.

## 🏗️ Arquitetura

- **FastAPI**: Framework web moderno e rápido para APIs
- **PostgreSQL + pgvector**: Banco de dados com suporte a operações vetoriais
- **LangChain**: Orquestração de IA e processamento de documentos
- **sentence-transformers**: Geração de embeddings (all-MiniLM-L6-v2)
- **Google Gemini API**: Geração de respostas (Gemini Pro)

## 📁 Estrutura do Projeto

```
backend/
├── .env.example          # Exemplo de variáveis de ambiente
├── .gitignore           # Arquivos a serem ignorados pelo Git
├── requirements.txt     # Dependências Python
├── docker-compose.yml   # Configuração do banco PostgreSQL
├── README.md           # Este arquivo
│
├── db/
│   └── init.sql        # Schema do banco de dados
│
├── documents/          # Pasta para arquivos PDF (criada automaticamente)
│   └── README.md       # Instruções da pasta
│
├── app/                # Módulo principal da aplicação
│   ├── __init__.py     # Inicialização do módulo
│   ├── main.py         # Aplicação FastAPI e endpoints
│   ├── config.py       # Configurações e variáveis de ambiente
│   ├── schemas.py      # Modelos Pydantic para API
│   ├── crud.py         # Operações de banco de dados
│   └── services.py     # Lógica de negócio (RAG, embeddings, etc.)
│
└── scripts/            # Scripts offline
    ├── __init__.py
    └── ingest.py       # Script de ingestão de PDFs
```

## 🚀 Configuração e Instalação

### 1. Clonar e configurar ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env

# Editar .env com suas configurações:
# - DATABASE_URL: String de conexão PostgreSQL (já configurada para Docker)
# - GEMINI_API_KEY: Sua chave da API Google Gemini
# - Outras configurações conforme necessário
```

### 3. Configurar banco de dados

```bash
# Subir PostgreSQL com Docker
docker-compose up -d

# O banco será inicializado automaticamente com o schema em db/init.sql
```

## 📊 Uso

### Executar API

```bash
# Desenvolvimento
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

- **Documentação Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Ingestão de Documentos (Offline)

```bash
# COMANDO PADRÃO: Processar todos PDFs da pasta 'documents/'
python scripts/ingest.py

# Processar um único PDF específico
python scripts/ingest.py --pdf-path caminho/para/documento.pdf

# Processar todos PDFs de uma pasta específica
python scripts/ingest.py --pdf-folder caminho/para/pasta/

# Com logging detalhado
python scripts/ingest.py --verbose
```

**💡 Dica**: Basta colocar seus PDFs na pasta `documents/` e executar `python scripts/ingest.py` - é o jeito mais simples!

### Endpoints da API

#### Chat Interativo
```http
POST /chat
Content-Type: application/json

{
    "message": "Qual é o tema principal do documento?",
    "conversation_id": null,
    "max_chunks": 5
}
```

#### Health Check
```http
GET /health
```

#### Upload de Documento (Opcional)
```http
POST /upload
Content-Type: multipart/form-data

file: [arquivo.pdf]
```

## 🔧 Desenvolvimento

### Estrutura dos Módulos

- **`app/main.py`**: Aplicação FastAPI, endpoints, middleware
- **`app/config.py`**: Configurações centralizadas
- **`app/schemas.py`**: Modelos Pydantic para validação
- **`app/crud.py`**: Operações de banco de dados
- **`app/services.py`**: Lógica de negócio (RAG, embeddings)
- **`scripts/ingest.py`**: Processamento offline de PDFs

### Fluxo de Dados

1. **Ingestão** (Offline):
   - PDF → Extração de texto → Chunks → Embeddings → PostgreSQL

2. **Chat** (Online):
   - Pergunta → Embedding → Busca similaridade → Chunks relevantes → Prompt → Gemini → Resposta

## 📋 Schema do Banco

- **`documents`**: Documentos completos
- **`chunks`**: Pedaços de texto com embeddings
- **`conversations`**: Sessões de chat
- **`messages`**: Mensagens e respostas
- **`message_source_chunks`**: Relação entre mensagens e chunks utilizados

## 🎯 Próximos Passos

1. Instalar dependências: `pip install -r requirements.txt`
2. Configurar `.env` com suas credenciais
3. Subir banco de dados: `docker-compose up -d`
4. Testar conexão: executar API e acessar `/health`
5. Fazer ingestão de alguns PDFs de teste
6. Testar endpoint `/chat` com perguntas

## 📝 Licença

Projeto desenvolvido como TCC de Engenharia de Software.

---

**Autor**: [Seu Nome]  
**Data**: Outubro 2025