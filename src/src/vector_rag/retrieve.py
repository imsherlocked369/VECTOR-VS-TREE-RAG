from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from src.common.config import settings


class VectorRetriever:
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.embedder = SentenceTransformer(settings.embed_model)

    def _search_points(self, query_vector: list[float], top_k: int):
        # qdrant-client >= 1.17 removed `search` in favor of `query_points`.
        if hasattr(self.client, "search"):
            return self.client.search(
                collection_name=settings.qdrant_collection,
                query_vector=query_vector,
                limit=top_k,
            )

        response = self.client.query_points(
            collection_name=settings.qdrant_collection,
            query=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        return response.points

    def search(self, question: str, top_k: int | None = None):
        top_k = top_k or settings.top_k
        qvec = self.embedder.encode(question).tolist()

        results = self._search_points(qvec, top_k)

        return [
            {
                "score": r.score,
                "chunk_id": r.payload.get("chunk_id", ""),
                "doc_id": r.payload.get("doc_id", ""),
                "section_title": r.payload.get("section_title", ""),
                "heading_path": r.payload.get("heading_path", ""),
                "content": r.payload.get("content", ""),
                "node_id": r.payload.get("node_id", ""),
            }
            for r in results
        ]
