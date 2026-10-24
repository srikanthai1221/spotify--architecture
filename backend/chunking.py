
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pdf_processor import extract_pdf_text


def create_chunks(pdf_path: str) -> list[dict]:
    """Split extracted PDF pages into smaller text chunks."""

    pages = extract_pdf_text(pdf_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_index, chunk_text in enumerate(page_chunks):
            chunks.append({
                "text": chunk_text,
                "page": page["page"],
                "chunk_id": f"page_{page['page']}_chunk_{chunk_index}"
            })

    return chunks


if __name__ == "__main__":
    chunks = create_chunks("data/spotify_web_app_architecture.pdf")

    print(f"Total chunks created: {len(chunks)}")

    for chunk in chunks[:3]:
        print(f"\nChunk ID: {chunk['chunk_id']}")
        print(f"Page: {chunk['page']}")
        print(f"Text: {chunk['text'][:250]}")
