# 📄 Pasta de Documentos PDF

**Esta pasta é onde você deve colocar os arquivos PDF para serem processados pelo RAGBot.**

## 🚀 Como usar (SUPER SIMPLES):

### **Passo 1: Adicionar PDFs**
- Arraste e solte seus arquivos PDF nesta pasta
- Ou copie manualmente os arquivos .pdf aqui

### **Passo 2: Processar documentos**
```bash
# Comando mais simples (processa todos PDFs desta pasta)
python scripts/ingest.py

# OU usando o executável do venv diretamente
.\venv\Scripts\python.exe scripts/ingest.py
```

## ✅ Arquivos Suportados
- ✅ **PDF (.pdf)** - Formato principal suportado
- ❌ **Word (.docx)** - Não suportado ainda
- ❌ **Texto (.txt)** - Não suportado ainda
- ❌ **Imagens** - Não suportado

## 📊 O que acontece durante o processamento:

1. 📖 **Extração de texto** do PDF página por página
2. ✂️ **Chunking inteligente** - divide em pedaços de ~1000 caracteres
3. 🧠 **Geração de embeddings** - vetores de 384 dimensões
4. 💾 **Armazenamento** no PostgreSQL com índices vetoriais
5. ✅ **Pronto para chat!** - documento disponível para perguntas

## 📝 Exemplo de Saída:
```
INFO | Processing PDF: documents\exemplo.pdf
INFO | Extracted 15,248 characters from 8 pages  
INFO | Created 32 chunks for document exemplo.pdf
SUCCESS | PDF processed successfully in 6.42s
```

## 💡 Dicas:

- **📁 Tamanho**: PDFs de até 50MB funcionam bem
- **📄 Páginas**: Sem limite, mas mais páginas = mais tempo
- **🔤 Texto**: PDFs com texto real (não imagens escaneadas)
- **🌐 Idioma**: Funciona melhor com português e inglês
- **🔄 Reprocessamento**: Executar novamente não duplica dados

## 🆘 Problemas?

- **Pasta vazia**: Coloque pelo menos 1 PDF aqui
- **Erro de permissão**: Certifique-se de que os arquivos não estão abertos
- **PDF corrompido**: Teste abrir o PDF antes de processar
- **Muito lento**: PDFs com muitas imagens demoram mais
- Após o processamento, os documentos ficarão disponíveis para consulta via chat

## Estrutura após processamento:
Cada PDF será:
1. **Lido e texto extraído**
2. **Dividido em chunks menores**
3. **Convertido em embeddings vetoriais**
4. **Armazenado no banco PostgreSQL**

---
*Mantenha esta pasta organizada para facilitar o gerenciamento dos documentos.*