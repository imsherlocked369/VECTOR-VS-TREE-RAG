import json
from pathlib import Path
from src.common.models import ChunkRecord


def split_text(text: str, max_chars: int = 1200, overlap: int = 150):
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def build_heading_paths(nodes: list[dict]) -> dict[str, str]:
    node_map = {n["node_id"]: n for n in nodes}
    path_cache: dict[str, str] = {}

    def resolve(node_id: str) -> str:
        if node_id in path_cache:
            return path_cache[node_id]

        node = node_map.get(node_id)
        if not node:
            return ""

        title = (node.get("title") or "").strip()
        parent_id = node.get("parent_id")

        if parent_id and parent_id in node_map:
            parent_path = resolve(parent_id)
            full_path = f"{parent_path} > {title}" if parent_path else title
        else:
            full_path = title

        path_cache[node_id] = full_path
        return full_path

    for node_id in node_map:
        resolve(node_id)

    return path_cache


def build_chunks_from_tree(tree_json_path: str):
    payload = json.loads(Path(tree_json_path).read_text(encoding="utf-8"))
    doc_id = payload["doc_id"]
    nodes = payload["nodes"]
    heading_paths = build_heading_paths(nodes)

    records = []
    counter = 0

    for node in nodes:
        if not node["content"].strip():
            continue
        node_id = node["node_id"]
        for piece in split_text(node["content"]):
            counter += 1
            records.append(
                ChunkRecord(
                    chunk_id=f"{doc_id}_c{counter}",
                    doc_id=doc_id,
                    section_title=node["title"],
                    heading_path=heading_paths.get(node_id, node["title"]),
                    content=piece,
                    level=node["level"],
                    node_id=node_id,
                )
            )
    return records
