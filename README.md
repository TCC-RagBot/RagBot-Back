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

## 🚀 Instalação e Configuração

### **Pré-requisitos**

Antes de começar, certifique-se de ter instalado:

- 🐍 **Python 3.11+** - [Download aqui](https://www.python.org/downloads/)
- 🐳 **Docker & Docker Compose** - [Instalar Docker](https://docs.docker.com/get-docker/)
- 🔑 **Google Gemini API Key** - [Obter aqui](https://ai.google.dev/)

### **1️⃣ Clonar o Repositório**

```bash
git clone <https://github.com/TCC-RagBot/RagBot-Back.git>
cd backend
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

> 🔑 **Como obter Google Gemini API Key:**
> 1. Acesse [Google AI Studio](https://ai.google.dev/)
> 2. Faça login com sua conta Google
> 3. Clique em "Get API Key"
> 4. Copie a chave e cole no arquivo `.env`

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

# Iniciar servidor de desenvolvimento
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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

## � Licença

Projeto desenvolvido para o **TCC de Engenharia de Software**.

---