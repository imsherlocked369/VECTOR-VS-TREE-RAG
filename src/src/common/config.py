from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "rag_chunks")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma3")
    embed_model: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    rerank_model: str = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    top_k: int = int(os.getenv("TOP_K", "20"))
    rerank_candidate_k: int = int(os.getenv("RERANK_CANDIDATE_K", "15"))
    rerank_top_k: int = int(os.getenv("RERANK_TOP_K", "5"))
    tree_max_depth: int = int(os.getenv("TREE_MAX_DEPTH", "4"))
    tree_children_per_step: int = int(os.getenv("TREE_CHILDREN_PER_STEP", "8"))
    data_dir: str = os.getenv("DATA_DIR", "./data")


settings = Settings()
