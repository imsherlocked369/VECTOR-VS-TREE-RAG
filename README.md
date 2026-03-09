# Vector vs Tree RAG

This project compares three QA pipelines over the same data:

- `Vector-RAG`
- `Vector-RAG + rerank`
- `Tree-RAG`

The UI is a Streamlit app backed by:

- `Qdrant` for vector search
- `Ollama` for generation and tree traversal decisions

## Repository Layout

- `src/src/ui/app.py`: Streamlit UI
- `src/src/vector_rag/*`: chunking, indexing, retrieval, reranking
- `src/src/tree_rag/*`: tree traversal and answer generation
- `src/src/ingest/*`: PDF parsing and tree building
- `data/trees/*.json`: tree docs consumed by indexer/UI

## Docker Quickstart

### 1. Prepare env file

```powershell
Copy-Item .env.example .env
```

Edit `.env` if you want a different model or retrieval settings.

### 2. Start containers

```powershell
docker compose up -d --build
```

Services:

- Streamlit UI: `http://localhost:8501`
- Qdrant: `http://localhost:6333`
- Ollama API: `http://localhost:11434`

### 3. Pull Ollama model (first run)

```powershell
docker compose exec ollama ollama pull qwen3:4b-instruct-2507-q4_K_M
```

If you changed `OLLAMA_MODEL` in `.env`, pull that model instead.

### 4. Build / refresh vector index

```powershell
docker compose --profile tools run --rm indexer
```

The indexer reads tree files from `data/trees/*.json` and writes vectors to Qdrant.

## Local (Non-Docker) Run

```powershell
conda create -n tree-rag python=3.11 -y
conda activate tree-rag
pip install -r requirements.txt

docker compose up -d qdrant
ollama serve
ollama pull qwen3:4b-instruct-2507-q4_K_M

$env:PYTHONPATH="src"
python -m src.vector_rag.index_qdrant
streamlit run src/src/ui/app.py
```

## Push to GitHub

If this folder is not yet a git repo:

```powershell
git init
git add .
git commit -m "Containerize app with Docker Compose"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

If repo already exists:

```powershell
git add .
git commit -m "Containerize app with Docker Compose"
git push
```
