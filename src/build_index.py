import json
from datetime import date

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.ingest import CHUNK_OVERLAP, CHUNK_SIZE, PROJECT_ROOT, build_chunks

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

INDEX_DIR = PROJECT_ROOT / "data" / "index"
INDEX_FILE = INDEX_DIR / "faiss.index"
CHUNKS_FILE = INDEX_DIR / "chunks.json"
INFO_FILE = INDEX_DIR / "index_info.json"


def main():
    _, chunks = build_chunks()
    print(f"\nEmbedding {len(chunks)} chunks with {EMBEDDING_MODEL} ...")

    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [chunk.page_content for chunk in chunks]
    vectors = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,  # makes inner product equal cosine similarity
        show_progress_bar=True,
    )
    vectors = np.asarray(vectors, dtype="float32")

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))

    records = [{"text": chunk.page_content, **chunk.metadata} for chunk in chunks]
    CHUNKS_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    info = {
        "embedding_model": EMBEDDING_MODEL,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "num_chunks": len(records),
        "vector_dimension": int(vectors.shape[1]),
        "built_on": date.today().isoformat(),
    }
    INFO_FILE.write_text(json.dumps(info, indent=2), encoding="utf-8")

    print(f"Saved {index.ntotal} vectors to {INDEX_FILE.relative_to(PROJECT_ROOT)}")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()