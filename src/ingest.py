import csv
import re
from pathlib import Path

import pdfplumber
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SOURCES_CSV = PROJECT_ROOT / "data" / "sources.csv"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


CONSOLIDATED_HEADER = re.compile(r"^\s*0\d{4}R\d{4}\s+—\s+EN\s+—.*$", re.MULTILINE)

OJ_FOOTER = re.compile(r"^\s*ELI:\s*http\S+\s+\d+/\d+\s*$", re.MULTILINE)

OJ_HEADER = re.compile(
    r"^\s*(Official Journal EN|of the European Union L series|EN"
    r"|OJ L, \d{1,2}\.\d{1,2}\.\d{4}|\d{4}/\d{1,4} \d{1,2}\.\d{1,2}\.\d{4})\s*$",
    re.MULTILINE,
)
AMENDMENT_MARKER = re.compile(r"[▼►][A-Z]\d*|◄")

PAGE_NUMBER_LINE = re.compile(r"^\s*\d{1,3}\s*$", re.MULTILINE)
MULTI_SPACE = re.compile(r"[ \t]{2,}")
EXTRA_BLANK_LINES = re.compile(r"\n{3,}")

NOISE_CHECKS = {
    "consolidated header": re.compile(r"— EN — \d{2}\.\d{2}\.\d{4}"),
    "OJ footer": OJ_FOOTER,
    "OJ header": OJ_HEADER,
    "amendment markers": re.compile(r"[▼►◄]"),
}


def clean_text(text):
    """Remove headers, footers, amendment markers and extra whitespace."""
    text = CONSOLIDATED_HEADER.sub("", text)
    text = OJ_FOOTER.sub("", text)
    text = OJ_HEADER.sub("", text)
    text = AMENDMENT_MARKER.sub("", text)
    text = PAGE_NUMBER_LINE.sub("", text)
    text = MULTI_SPACE.sub(" ", text)
    text = EXTRA_BLANK_LINES.sub("\n\n", text)
    return text.strip()


def load_sources():
    """Read sources.csv and return one dictionary per document."""
    with open(SOURCES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_pages(sources):
    """Extract and clean the text of every PDF page, with metadata."""
    pages = []
    for src in sources:
        pdf_path = RAW_DIR / src["filename"]
        if not pdf_path.exists():
            raise FileNotFoundError(f"Listed in sources.csv but missing: {pdf_path}")

        page_count = 0
        with pdfplumber.open(pdf_path) as pdf:
            for index, pdf_page in enumerate(pdf.pages):
                text = clean_text(pdf_page.extract_text() or "")
                pdf_page.close()  # free memory after each page
                if not text:
                    continue
                pages.append(
                    Document(
                        page_content=text,
                        metadata={
                            "doc_id": src["doc_id"],
                            "filename": src["filename"],
                            "title": src["title"],
                            "source_type": src["source_type"],
                            "url": src["url"],
                            "page_number": index + 1,  # PDF page, counted from 1
                        },
                    )
                )
                page_count += 1
        print(f"Loaded {page_count:>3} pages from {src['filename']}")
    return pages


def split_pages(pages):
    """Split each page into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(pages)


def build_chunks():
    """Run the full pipeline: sources -> cleaned pages -> chunks."""
    sources = load_sources()
    pages = load_pages(sources)
    return pages, split_pages(pages)


def show_page(pages, doc_id, page_number, length=400):
    """Print the start of one cleaned page, to check the cleaning."""
    for page in pages:
        if page.metadata["doc_id"] == doc_id and page.metadata["page_number"] == page_number:
            print(f"\n--- Doc {doc_id}, page {page_number} (cleaned) ---")
            print(page.page_content[:length])
            return
    print(f"\n--- Doc {doc_id}, page {page_number}: not found ---")


def main():
    pages, chunks = build_chunks()

    print(f"\nTotal pages with text: {len(pages)}")
    print(f"Total chunks: {len(chunks)}")
    average = sum(len(c.page_content) for c in chunks) / len(chunks)
    print(f"Average chunk length: {average:.0f} characters")

    print("\nNoise check (each should be 0):")
    for name, pattern in NOISE_CHECKS.items():
        found = [c for c in chunks if pattern.search(c.page_content)]
        print(f"  {name}: {len(found)}")
        if found:
            example = found[0]
            print(f"    Example from doc {example.metadata['doc_id']}, page {example.metadata['page_number']}:")
            print("    " + example.page_content[:200].replace("\n", " | "))

    show_page(pages, "02", 1)
    show_page(pages, "02", 5)
    show_page(pages, "02", 20)


if __name__ == "__main__":
    main()