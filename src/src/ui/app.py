import glob
import streamlit as st

from src.common.config import settings
from src.vector_rag.retrieve import VectorRetriever
from src.vector_rag.rerank import Reranker
from src.tree_rag.traverse import TreeNavigator
from src.tree_rag.answer import answer_from_context

st.set_page_config(page_title="Tree vs Vector RAG", layout="wide")
st.title("Tree-RAG vs Vector-RAG")

question = st.text_input("Ask a question about your indexed documents")


def build_answer_context(hits: list[dict], selected_k: int = 5, max_chars: int = 3000):
    selected = hits[:selected_k]
    context_parts = []
    citations = []

    for i, hit in enumerate(selected, start=1):
        title = hit.get("section_title", "Untitled section")
        heading_path = hit.get("heading_path", "").strip()
        content = hit.get("content", "").strip()
        if not content:
            continue

        heading_line = f"\nPath: {heading_path}" if heading_path else ""
        context_parts.append(f"[{i}] {title}{heading_line}\n{content}")
        citations.append(heading_path or title)

    if not context_parts:
        return "", ""

    context = "\n\n".join(context_parts)[:max_chars]
    citation = " > ".join(citations)
    return context, citation


if st.button("Run") and question:
    vector = VectorRetriever()
    reranker = Reranker()

    col1, col2, col3 = st.columns(3)

    vec_hits = vector.search(question, top_k=settings.top_k)
    reranked_hits = reranker.rerank(
        question,
        vec_hits,
        candidate_k=settings.rerank_candidate_k,
        top_k=settings.rerank_top_k,
    )

    vec_context, vec_citation = build_answer_context(
        vec_hits,
        selected_k=settings.rerank_top_k,
    )
    rerank_context, rerank_citation = build_answer_context(
        reranked_hits,
        selected_k=settings.rerank_top_k,
    )

    vec_answer = (
        answer_from_context(question, vec_context, citation=vec_citation)
        if vec_context
        else "No supporting context retrieved."
    )
    rerank_answer = (
        answer_from_context(question, rerank_context, citation=rerank_citation)
        if rerank_context
        else "No supporting context retrieved."
    )

    with col1:
        st.subheader("Vector-RAG")
        st.markdown("**Answer**")
        st.write(vec_answer)
        st.markdown("**Top evidence chunks**")
        for hit in vec_hits[: settings.rerank_top_k]:
            st.markdown(f"**{hit['section_title']}**")
            if hit.get("heading_path"):
                st.caption(hit["heading_path"])
            st.write(hit["content"][:350] + "...")

    with col2:
        st.subheader("Vector + Rerank")
        st.markdown("**Answer**")
        st.write(rerank_answer)
        st.markdown("**Top evidence chunks**")
        for hit in reranked_hits[: settings.rerank_top_k]:
            st.markdown(f"**{hit['section_title']}**")
            if hit.get("heading_path"):
                st.caption(hit["heading_path"])
            st.write(hit["content"][:350] + "...")

    tree_files = glob.glob("data/trees/*.json")
    if tree_files:
        nav = TreeNavigator(tree_files[0])
        result = nav.traverse(question)

        with col3:
            st.subheader("Tree-RAG")
            st.write("Chosen path:")
            for step in result["path"]:
                st.write(f"- {step['title']} ({step['reason']})")

            answer = answer_from_context(
                question,
                result["evidence"][:3000],
                citation=" > ".join([p["title"] for p in result["path"]]),
            )
            st.markdown("**Answer**")
            st.write(answer)
