from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TreeNode:
    node_id: str
    title: str
    level: int
    content: str
    summary: str = ""
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)


@dataclass
class ChunkRecord:
    chunk_id: str
    doc_id: str
    section_title: str
    heading_path: str
    content: str
    level: int
    node_id: str
