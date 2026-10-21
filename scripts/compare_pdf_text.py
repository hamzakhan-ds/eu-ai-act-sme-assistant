from pathlib import Path

import pdfplumber
from pypdf import PdfReader

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

SAMPLES = [
    ("01-ai-act-regulation-2024-1689.pdf", 9),
    ("04-guidelines-prohibited-ai-practices.pdf", 20),
]

def show(label, text):
    print(f"\n {label} ")
    print(text[:700])

for filename, page_index in SAMPLES:
    path = RAW_DIR / filename
    page_label = f"{filename}, page {page_index +1}"

    reader = PdfReader(path)
    page = reader.pages[page_index]
    show(f"{page_label} | pypdf plain", page.extract_text())
    show(f"{page_label} | pypdf layout", page.extract_text(extraction_mode="layout"))

    with pdfplumber.open(path) as pdf:
        show(f"{page_label} | pdfplumber", pdf.pages[page_index].extract_text())