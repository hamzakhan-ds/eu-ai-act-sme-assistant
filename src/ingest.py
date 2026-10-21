import csv
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SOURCES_CSV = PROJECT_ROOT / "data" / "sources.csv"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

def load_sources():
    with open(SOURCES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_documents(sources):
    pages=[]
    for src in sources:
        pdf_path= RAW_DIR / src["filename"]
        if not pdf_path.exists():
            raise FileNotFoundError(f"Listed in sources.csv but missing: {pdf_path}")

        doc_pages = PyPDFLoader(str(pdf_path)).load()
        for page in doc_pages:
            page.metadata.update(
                {
                    "doc_id": src["doc_id"],
                    "title": src["title"],
                    "source_type": src["source_type"],
                    "url": src["url"],
                    "page_number": page.metadata.get("page", 0) + 1,
                }
            )
        print(f"Loaded {len(doc_pages):>3} pages from {src['filename']}")
        pages.extend(doc_pages)
    return pages

def split_documents(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )
    return splitter.split_documents(pages)

def main():
    sources = load_sources()
    pages = load_documents(sources)

    print(f"\nTotal pages: {len(pages)}")
    empty_pages = [p for p in pages if not p.page_content.strip()]
    print(f"Pages with no text: {len(empty_pages)}")

    chunks = split_documents(pages)
    average = sum(len(c.page_content) for c in chunks)/len(chunks)
    print(f"Total chunks: {len(empty_pages)}")
    print(f"Average chunk length: {average:.0f} characters")

    ai_act_pages = [p for p in pages if p.metadata["doc_id"]=="01"]
    sample = ai_act_pages[9].page_content
    print("\n AI Act, page 10: first 500 characters")
    print(sample[:500])
    print("\n AI Act, page 10: last 300 characters")
    print(sample[-300:])

    print("\n Example Chunk")
    example = chunks[200]
    print(example.metadata)
    print(example.page_content)

if __name__ == "__main__":
    main()