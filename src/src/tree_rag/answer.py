from ollama import chat
from src.common.config import settings


def answer_from_context(question: str, context: str, citation: str = "") -> str:
    prompt = f"""
Answer the question only from the provided context.

For conceptual questions, give 2 to 4 distinct points if the evidence supports them.
Do not collapse everything into one sentence if multiple defining ideas are present.
If the context supports only one point, say so.

Return:
1. concise answer
2. evidence note

Question:
{question}

Context:
{context}

Citation:
{citation}

Return:
- concise answer
- one short evidence note
""".strip()

    response = chat(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]