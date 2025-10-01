# Pasta para Documentos PDF

Esta pasta é destinada aos arquivos PDF que serão processados pelo sistema RAGBot.

## Como usar:

1. **Adicione seus arquivos PDF nesta pasta**
2. **Execute o comando de ingestão padrão:**
   ```bash
   python scripts/ingest.py --pdf-folder documents
   ```

## Arquivos suportados:
- ✅ Arquivos PDF (.pdf)
- ❌ Outros formatos não são suportados atualmente

## Notas:
- Os arquivos serão processados em ordem alfabética
- Documentos grandes podem levar mais tempo para processar
- O sistema criará chunks de texto e embeddings automaticamente
- Após o processamento, os documentos ficarão disponíveis para consulta via chat

## Estrutura após processamento:
Cada PDF será:
1. **Lido e texto extraído**
2. **Dividido em chunks menores**
3. **Convertido em embeddings vetoriais**
4. **Armazenado no banco PostgreSQL**

---
*Mantenha esta pasta organizada para facilitar o gerenciamento dos documentos.*