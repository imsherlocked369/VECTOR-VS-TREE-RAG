import json
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from src.common.config import settings
from src.vector_rag.chunker import build_chunks_from_tree


def main():
    client = QdrantClient(url=settings.qdrant_url)
    embedder = SentenceTransformer(settings.embed_model)

    tree_files = list(Path("data/trees").glob("*.json"))
    all_chunks = []
    for file in tree_files:
        all_chunks.extend(build_chunks_from_tree(str(file)))

    if not all_chunks:
        raise RuntimeError("No chunks found. Build trees first.")

    sample_vec = embedder.encode(["hello"])[0]
    dim = len(sample_vec)

    if client.collection_exists(settings.qdrant_collection):
        client.delete_collection(settings.qdrant_collection)
    client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    texts = [c.content for c in all_chunks]
    vectors = embedder.encode(texts, show_progress_bar=True)

    points = []
    for i, (chunk, vector) in enumerate(zip(all_chunks, vectors)):
        points.append(
            PointStruct(
                id=i,
                vector=vector.tolist(),
                payload={
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "section_title": chunk.section_title,
                    "heading_path": chunk.heading_path,
                    "content": chunk.content,
                    "level": chunk.level,
                    "node_id": chunk.node_id,
                },
            )
        )

    client.upsert(collection_name=settings.qdrant_collection, points=points)
    print(f"Indexed {len(points)} chunks into Qdrant.")


if __name__ == "__main__":
    main()
