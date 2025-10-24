# RAGBot Backend 🤖

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)

Backend API para sistema RAG (Retrieval-Augmented Generation) desenvolvido como TCC de Engenharia de Software.

## 📋 Sobre o Projeto

O **RAGBot** é um sistema completo de chat inteligente que processa documentos PDF e responde perguntas baseado **exclusivamente** no conteúdo dos documentos carregados. Utiliza técnicas avançadas de IA para:

- 📄 **Ingestão inteligente** de documentos PDF
- 🔍 **Busca semântica** com embeddings vetoriais  
- 💬 **Chat contextual** usando Google Gemini AI
- 🎯 **Respostas precisas** baseadas apenas no conteúdo fornecido

## 🏗️ Stack Tecnológica

### **Backend**
- **FastAPI** - Framework web moderno e rápido
- **Python 3.11+** - Linguagem principal
- **LangChain** - Orquestração de IA e processamento de documentos
- **Pydantic** - Validação de dados e configurações

### **Banco de Dados**
- **PostgreSQL 15+** - Banco de dados principal
- **pgvector** - Extensão para operações vetoriais
- **Docker Compose** - Orquestração de containers

### **Inteligência artificial**
- **sentence-transformers** - Geração de embeddings (all-MiniLM-L6-v2)  
- **Google Gemini AI** - Modelo de linguagem para geração de respostas

### **DevOps & Qualidade**
- **Docker** - Containerização
- **pytest** - Testes automatizados
- **Swagger** - Documentação da API

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

## 🚀 Instalação e Configuração

### **Pré-requisitos**

Antes de começar, certifique-se de ter instalado:

- 🐍 **Python 3.11+** - [Download aqui](https://www.python.org/downloads/)
- 🐳 **Docker & Docker Compose** - [Instalar Docker](https://docs.docker.com/get-docker/)
- 🔑 **Google Gemini API Key** - [Obter aqui](https://ai.google.dev/)

### **1️⃣ Clonar o Repositório**

```bash
git clone <https://github.com/TCC-RagBot/RagBot-Back.git>
cd RagBot-Back
```

### **2️⃣ Configurar Ambiente Virtual**

```bash
# Criar ambiente virtual com Python 3.11
python -m venv venv

# Ativar ambiente virtual
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Verificar se está ativo (deve aparecer (venv) no prompt)
python --version  # Deve mostrar Python 3.11+
```

### **3️⃣ Instalar Dependências**

```bash
# Atualizar pip para a versão mais recente
python -m pip install --upgrade pip

# Instalar todas as dependências do projeto
pip install -r requirements.txt

# Verificar instalação (deve listar ~88 pacotes)
pip list
```

### **4️⃣ Configurar Variáveis de Ambiente**

```bash
# Copiar arquivo de exemplo
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

**Editar arquivo `.env`** com suas configurações:

### **5️⃣ Configurar Banco de Dados**

```bash
# Subir PostgreSQL com Docker Compose
docker-compose up -d

# Verificar se está rodando
docker ps

```

O banco será inicializado automaticamente com:
- ✅ PostgreSQL 15
- ✅ Extensão pgvector
- ✅ Schema completo (tabelas documents, chunks, etc.)
- ✅ Usuário: `tccrag` / Senha: `tcc123` / DB: `ragbot_db`

## 🎮 Como Usar

### **6️⃣ Iniciar a API**

```bash
# IMPORTANTE: Certifique-se de que o ambiente virtual está ativo!

# Método 1: Execução direta (RECOMENDADO)
python -m app.main

```

✅ **API funcionando!** Acesse:
- 🏠 **API Base**: http://localhost:8000
- 📚 **Documentação Swagger**: http://localhost:8000/docs  
- 📖 **ReDoc**: http://localhost:8000/redoc
- ❤️ **Health Check**: http://localhost:8000/health

### **7️⃣ Testar Conexões**

```bash
# Testar health check (deve retornar status: healthy)
curl http://localhost:8000/health

# Ou acesse no navegador: http://localhost:8000/health
```

### **8️⃣ Ingerir Documentos (OBRIGATÓRIO para usar o chat)**

```bash
# Colocar PDFs na pasta documents/ e executar:
python scripts/ingest.py

# OU usando o executável do venv diretamente:
.\venv\Scripts\python.exe scripts/ingest.py
```

## 🧪 Executar Testes

O projeto inclui uma suíte completa de testes automatizados para validar o funcionamento do sistema de ingestão de PDFs e geração de embeddings.

### **Executar Todos os Testes**

```bash
# Modo básico - apenas resultados
python -m pytest tests/

# Modo verboso - com detalhes dos testes
python -m pytest tests/ -v

# Com prints dos testes visíveis (RECOMENDADO)
python -m pytest tests/ -v -s
```

### **Executar Teste Específico**

```bash
# Teste completo end-to-end (RECOMENDADO para validação geral)
python -m pytest tests/test_ingestion.py::TestPDFIngestion::test_end_to_end_ingestion_flow -v -s

# Teste de carregamento de PDF apenas
python -m pytest tests/test_ingestion.py::TestPDFIngestion::test_pdf_loading_with_pypdf -v -s
```

### **Saída Esperada dos Testes** 

Quando tudo está funcionando corretamente, você verá:

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

### **Pré-requisitos para Testes**

- ✅ Ambiente virtual ativo
- ✅ Dependências instaladas (`pip install -r requirements.txt`)  
- ✅ Arquivo `pdf-test.pdf` na raiz do projeto (incluído no repositório)

📚 **Documentação completa dos testes**: Veja [`tests/README.md`](./tests/README.md) para informações detalhadas.

## 📄 Licença

Projeto desenvolvido para o **TCC de Engenharia de Software**.

---