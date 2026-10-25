import pdfplumber

from src.ingest import RAW_DIR, load_sources

DOCS_WITH_TABLES = {"04", "05"}


def main():
    for src in load_sources():
        if src["doc_id"] not in DOCS_WITH_TABLES:
            continue
        with pdfplumber.open(RAW_DIR / src["filename"]) as pdf:
            for index, page in enumerate(pdf.pages):
                for table in page.find_tables():
                    rows = table.extract()
                    columns = len(rows[0]) if rows else 0
                    print(f"\nDoc {src['doc_id']}, page {index + 1}: {len(rows)} rows x {columns} columns")
                    for row in rows[:3]:
                        line = " | ".join(" ".join((cell or "").split()) for cell in row)
                        print("   " + line[:250])
                page.close()


if __name__ == "__main__":
    main()