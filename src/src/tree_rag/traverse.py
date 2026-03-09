import json
from pathlib import Path
from ollama import chat
from src.common.config import settings


class TreeNavigator:
    def __init__(self, tree_json_path: str):
        payload = json.loads(Path(tree_json_path).read_text(encoding="utf-8"))
        self.doc_id = payload["doc_id"]
        self.nodes = {n["node_id"]: n for n in payload["nodes"]}
        self.roots = [n for n in payload["nodes"] if n["parent_id"] is None]

    def _pick_child(self, question: str, candidates: list[dict]) -> dict:
        candidate_text = "\n".join(
            [
                f'- id: {c["node_id"]} | title: {c["title"]} | summary: {c["summary"][:220]}'
                for c in candidates
            ]
        )

        prompt = f"""
You are choosing the most relevant document section for a question.

Question:
{question}

Candidates:
{candidate_text}

Return only valid JSON:
{{
  "selected_node_id": "candidate-id",
  "reason": "one short sentence"
}}
""".strip()

        response = chat(
            model=settings.ollama_model,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response["message"]["content"]
        return json.loads(content)

    def traverse(self, question: str):
        current_candidates = self.roots
        chosen_path = []
        depth = 0

        while current_candidates and depth < settings.tree_max_depth:
            limited = current_candidates[: settings.tree_children_per_step]
            choice = self._pick_child(question, limited)
            selected_id = choice["selected_node_id"]

            if selected_id not in self.nodes:
                break

            selected_node = self.nodes[selected_id]
            chosen_path.append(
                {
                    "node_id": selected_node["node_id"],
                    "title": selected_node["title"],
                    "reason": choice.get("reason", ""),
                }
            )

            child_ids = selected_node.get("children", [])
            current_candidates = [self.nodes[cid] for cid in child_ids if cid in self.nodes]
            depth += 1

            if not child_ids:
                return {
                    "path": chosen_path,
                    "evidence": selected_node["content"],
                    "leaf": selected_node,
                }

        leaf = self.nodes[chosen_path[-1]["node_id"]] if chosen_path else None
        return {
            "path": chosen_path,
            "evidence": leaf["content"] if leaf else "",
            "leaf": leaf,
        }