
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_STORE_PATH = PROJECT_ROOT / "database" / "vector_store"

load_dotenv(PROJECT_ROOT / ".env")


def search_vectors(question: str, k: int = 4) -> list[dict]:
    if not VECTOR_STORE_PATH.exists():
        raise FileNotFoundError(
            f"FAISS vector store not found: {VECTOR_STORE_PATH}"
        )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    results = vector_store.similarity_search_with_score(
        question,
        k=k,
    )

    retrieved_chunks = []

    for document, distance in results:
        retrieved_chunks.append({
            "content": document.page_content,
            "page": document.metadata.get("page"),
            "score": float(distance),
        })

    return retrieved_chunks


if __name__ == "__main__":
    question = "Which service handles recommendations?"
    results = search_vectors(question)

    for result in results:
        print(f"\nPage: {result['page']}")
        print(f"Distance: {result['score']:.4f}")
        print(result["content"][:300])
