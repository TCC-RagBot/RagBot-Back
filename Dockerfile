FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# PyTorch CPU-only para evitar baixar ~2GB de bibliotecas CUDA
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Pré-download do modelo de embedding para não baixar toda vez que o container iniciar
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
