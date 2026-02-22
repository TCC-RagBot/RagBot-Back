# RAGBot Backend

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)

Backend API para sistema RAG (Retrieval-Augmented Generation) desenvolvido como TCC de Engenharia de Software.

## Sobre o Projeto

RAGBot é um sistema de chat que processa documentos PDF e responde perguntas com base no conteúdo dos documentos carregados. O sistema implementa:

- Ingestão de documentos PDF
- Busca semântica através de embeddings vetoriais
- Chat contextual usando Google Gemini API
- Respostas baseadas exclusivamente no conteúdo fornecido

## Stack Tecnológica

### Backend
- FastAPI - Framework web
- Python 3.11+
- LangChain - Orquestração de IA e processamento de documentos
- Pydantic - Validação de dados

### Banco de Dados
- PostgreSQL 16 - Banco de dados
- pgvector - Extensão para operações vetoriais

### Inteligência Artificial
- sentence-transformers - Geração de embeddings (all-MiniLM-L6-v2)
- Google Gemini API - Modelo de linguagem para respostas

### DevOps
- Docker & Docker Compose - Containerização e orquestração
- pytest - Testes automatizados

## Estrutura do Projeto

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
│   ├── main.py         # Entry point da aplicação FastAPI
│   ├── config/         # Configurações da aplicação
│   │   ├── settings.py # Variáveis de ambiente e configurações
│   │   └── constants.py # Constantes e parâmetros da aplicação
│   ├── routes/         # Endpoints da API
│   │   ├── __init__.py
│   │   └── chat.py     # Rotas do chat e upload de documentos
│   ├── schemas/        # Modelos Pydantic para validação
│   │   └── chat.py     # Schemas para requests/responses
│   ├── services/       # Lógica de negócio
│   │   └── chat_service.py # Serviço principal do RAG
│   └── repositories/   # Camada de dados
│       ├── conversation_repository.py # Operações de banco
│       └── vector_repository.py       # Busca vetorial
│
└── scripts/            # Scripts offline
    ├── __init__.py
    └── ingest.py       # Script de ingestão de PDFs
```

## Arquitetura

O projeto é totalmente containerizado com Docker Compose. Dois containers são orquestrados:

1. **ragbot_db** - PostgreSQL 16 com extensão pgvector
2. **ragbot_backend** - API FastAPI (Python 3.11)

Os containers se comunicam internamente pela rede Docker. O banco é inicializado automaticamente com o schema definido em `db/init.sql`.

## Instalação e Execução

### Pré-requisitos

- Docker & Docker Compose - [Instalação](https://docs.docker.com/get-docker/)
- Google Gemini API Key - [Obter aqui](https://ai.google.dev/)

### 1. Clonar o Repositório

```bash
git clone <https://github.com/TCC-RagBot/RagBot-Back.git>
cd RagBot-Back
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Editar o arquivo `.env` e preencher:
- `GEMINI_API_KEY` - Sua chave de API do Google Gemini
- As demais variáveis já possuem valores padrão configurados

### 3. Iniciar com Docker

```bash
# Iniciar todos os containers
docker compose up
```

Os containers iniciarão automaticamente:
- PostgreSQL estará pronto na porta 5433 (interno: 5432)
- API FastAPI estará acessível em http://localhost:8000

Acesse:
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Desenvolvimento Local sem Docker

O banco de dados deve estar rodando em Docker:

```bash
docker compose up db
```

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Iniciar API
python -m app.main
```

### 4. Ingerir Documentos

Coloque os arquivos PDF na pasta `documents/` e execute dentro do container backend:

```bash
# Executa ingestão dentro do container
docker compose exec backend python scripts/ingest.py "documents/seu-documento.pdf"
```

## Testes

```bash
#Executar testes no Container
docker compose exec backend pytest tests/ -v

# Executar todos os testes no ambiente virtual
python -m pytest tests/ -v

```

## Parar os Containers

```bash
# Parar containers mantendo volumes de dados
docker compose stop

# Remover containers (dados persistem nos volumes)
docker compose down

# Remover tudo incluindo volumes (apaga dados do banco)
docker compose down -v
```

## Licença

Projeto desenvolvido como TCC de Engenharia de Software.

---