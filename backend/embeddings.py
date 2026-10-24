
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from chunking import create_chunks


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def build_vector_store():
    """Create embeddings and save the FAISS index locally."""

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to the project-root .env file."
        )

    chunks = create_chunks(
        str(PROJECT_ROOT / "data" / "spotify_web_app_architecture.pdf")
    )

    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"]
            }
        )
        for chunk in chunks
    ]

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vector_store = FAISS.from_documents(documents, embeddings)

    store_path = PROJECT_ROOT / "database" / "vector_store"
    store_path.mkdir(parents=True, exist_ok=True)

    vector_store.save_local(str(store_path))

    print(f"Chunks indexed: {len(documents)}")
    print(f"FAISS index saved to: {store_path}")


if __name__ == "__main__":
    build_vector_store()
