import argparse
import json
import re
from pathlib import Path
from src.common.models import TreeNode

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def naive_summary(text: str, limit: int = 220) -> str:
    text = " ".join(text.split())
    return text[:limit] + ("..." if len(text) > limit else "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Parsed JSON from parse_pdf.py")
    parser.add_argument("--output", required=True, help="Tree JSON output")
    args = parser.parse_args()

    parsed = json.loads(Path(args.input).read_text(encoding="utf-8"))
    markdown = parsed["markdown"]
    doc_id = parsed["doc_id"]

    lines = markdown.splitlines()
    nodes = []
    stack = []
    current_node = None
    node_counter = 0

    def close_current():
        nonlocal current_node
        if current_node:
            current_node.summary = naive_summary(current_node.content)
            nodes.append(current_node)
            current_node = None

    for line in lines:
        match = HEADING_RE.match(line.strip())
        if match:
            close_current()
            hashes, title = match.groups()
            level = len(hashes)
            node_counter += 1
            node_id = f"{doc_id}_n{node_counter}"

            while stack and stack[-1]["level"] >= level:
                stack.pop()

            parent_id = stack[-1]["node_id"] if stack else None

            current_node = TreeNode(
                node_id=node_id,
                title=title.strip(),
                level=level,
                content="",
                parent_id=parent_id,
            )

            stack.append({"node_id": node_id, "level": level})
        else:
            if current_node:
                current_node.content += line + "\n"

    close_current()

    node_map = {n.node_id: n for n in nodes}
    for node in nodes:
        if node.parent_id and node.parent_id in node_map:
            node_map[node.parent_id].children.append(node.node_id)

    tree_payload = {
        "doc_id": doc_id,
        "source_path": parsed["source_path"],
        "nodes": [
            {
                "node_id": n.node_id,
                "title": n.title,
                "level": n.level,
                "content": n.content.strip(),
                "summary": n.summary,
                "parent_id": n.parent_id,
                "children": n.children,
            }
            for n in nodes
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(tree_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved tree to {out_path}")


if __name__ == "__main__":
    main()