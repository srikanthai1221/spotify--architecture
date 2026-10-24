
import pymupdf
from pathlib import Path


def extract_pdf_text(pdf_path: str) -> list[dict]:
    """Extract text from a PDF and preserve page numbers."""
    file_path = Path(pdf_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path.resolve()}")

    pages = []

    with pymupdf.open(file_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page": page_number,
                    "text": text
                })

    return pages


if __name__ == "__main__":
    pdf_path = "data/spotify_web_app_architecture.pdf"
    pages = extract_pdf_text(pdf_path)

    print(f"Pages extracted: {len(pages)}")

    for page in pages:
        print(f"\n--- Page {page['page']} ---")
        print(page["text"][:300])
