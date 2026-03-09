from sentence_transformers import CrossEncoder
from src.common.config import settings


class Reranker:
    def __init__(self):
        self.model = CrossEncoder(settings.rerank_model)

    @staticmethod
    def _build_rerank_text(doc: dict) -> str:
        title = (doc.get("section_title") or "").strip()
        heading_path = (doc.get("heading_path") or "").strip()
        content = (doc.get("content") or "").strip()

        parts = []
        if title:
            parts.append(f"Section title: {title}")
        if heading_path and heading_path != title:
            parts.append(f"Heading path: {heading_path}")
        if content:
            parts.append(f"Content: {content}")
        return "\n".join(parts)

    def rerank(
        self,
        question: str,
        docs: list[dict],
        top_k: int | None = None,
        candidate_k: int | None = None,
    ):
        candidate_k = candidate_k or settings.rerank_candidate_k
        top_k = top_k or settings.rerank_top_k
        candidates = docs[:candidate_k]
        if not candidates:
            return []

        pairs = [[question, self._build_rerank_text(d)] for d in candidates]
        scores = self.model.predict(pairs)

        rescored = []
        for doc, score in zip(candidates, scores):
            item = dict(doc)
            item["rerank_score"] = float(score)
            rescored.append(item)

        rescored.sort(key=lambda x: x["rerank_score"], reverse=True)
        return rescored[:top_k]
