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

### **Backend**
- **FastAPI** - Framework web moderno e rápido
- **Python 3.11+** - Linguagem principal
- **LangChain** - Orquestração de IA e processamento de documentos
- **Pydantic** - Validação de dados e configurações

### **Banco de Dados**
- **PostgreSQL 15+** - Banco de dados principal
- **pgvector** - Extensão para operações vetoriais
- **Docker Compose** - Orquestração de containers

### **Inteligência Artificial**
- **sentence-transformers** - Geração de embeddings (all-MiniLM-L6-v2)  
- **Google Gemini AI** - Modelo de linguagem para geração de respostas

### **DevOps & Qualidade**
- **Docker** - Containerização
- **pytest** - Testes automatizados
- **Swagger** - Documentação da API

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

## Instalação e Configuração

### Pré-requisitos

- Python 3.11 (obrigatório - não use 3.12 ou 3.13) - [Download](https://www.python.org/downloads/release/python-3118/)
- Docker & Docker Compose - [Instrução de instalação](https://docs.docker.com/get-docker/)
- Google Gemini API Key - [Obter aqui](https://ai.google.dev/)

### 1. Clonar o Repositório

```bash
git clone <https://github.com/TCC-RagBot/RagBot-Back.git>
cd RagBot-Back
```

### 2. Configurar Ambiente Virtual

```bash
# Verificar versão do Python
python --version

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Editar o arquivo `.env` com suas configurações:

### 5. Configurar Banco de Dados

```bash
# Iniciar banco de dados com Docker Compose
docker-compose up -d

# Verificar containers
docker ps
```

O banco será inicializado automaticamente com PostgreSQL 15, extensão pgvector e schema completo.

Credenciais padrão:
- Usuário: `tccrag`
- Senha: `tcc123`
- Banco de dados: `ragbot_db`

## Como Usar

### 6. Iniciar a API

```bash
# Iniciar a API
python -m app.main
```

API disponível em:
- Base: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### 7. Testar Conexões

```bash
# Testar health check
curl http://localhost:8000/health
```

### 8. Ingerir Documentos

Antes de usar o chat, coloque os arquivos PDF na pasta `documents/` e execute:

```bash
python scripts/ingest.py "documents/seu-documento.pdf"
```

## Testes

### Executar Todos os Testes

```bash
# Executar todos os testes
python -m pytest tests/

# Modo verboso
python -m pytest tests/ -v

# Modo verboso com saída do console
python -m pytest tests/ -v -s
```

### Executar Teste Específico

```bash
# Teste end-to-end de ingestão
python -m pytest tests/test_ingestion.py::TestPDFIngestion::test_end_to_end_ingestion_flow -v -s

# Teste de carregamento de PDF
python -m pytest tests/test_ingestion.py::TestPDFIngestion::test_pdf_loading_with_pypdf -v -s
```

### Saída Esperada

Saída bem-sucedida dos testes:

```
PDF carregado: 1 páginas, 3219 caracteres totais
Documento dividido em 4 chunks (tamanho médio: 912 chars)  
Embeddings gerados: 3 vetores de 384D

======================== 5 passed in 10.52s ========================
```

### Pré-requisitos para Testes

- Ambiente virtual ativo
- Dependências instaladas
- Arquivo `pdf-test.pdf` na raiz do projeto

Ver [tests/README.md](./tests/README.md) para documentação completa.

## Licença

Projeto desenvolvido como TCC de Engenharia de Software.

---