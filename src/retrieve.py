import json

import faiss
from sentence_transformers import SentenceTransformer

from src.build_index import CHUNKS_FILE, EMBEDDING_MODEL, INDEX_FILE

# Instruction the bge model expects in front of search questions (not passages)
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
TOP_K = 4


class Retriever:
    """Loads the index once, then answers search requests."""

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = faiss.read_index(str(INDEX_FILE))
        self.chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
        if self.index.ntotal != len(self.chunks):
            raise ValueError("Index and chunks file are out of sync. Rebuild the index.")

    def search(self, question, k=TOP_K):
        """Return the k most similar chunks, each with a similarity score."""
        vector = self.model.encode([QUERY_PREFIX + question], normalize_embeddings=True)
        scores, ids = self.index.search(vector.astype("float32"), k)
        return [
            {**self.chunks[i], "score": float(score)}
            for score, i in zip(scores[0], ids[0])
            if i != -1
        ]


def main():
    retriever = Retriever()
    test_questions = [
        "When do the obligations for high-risk AI systems listed in Annex III apply?",
        "What does AI literacy mean?",
        "Is emotion recognition in the workplace prohibited?",
        "Do I have to tell users they are talking to a chatbot?",
    ]
    for question in test_questions:
        print(f"\n=== {question}")
        for result in retriever.search(question):
            print(
                f"  [{result['score']:.3f}] doc {result['doc_id']}, "
                f"page {result['page_number']} ({result['source_type']})"
            )
            print("     " + result["text"][:160].replace("\n", " "))


if __name__ == "__main__":
    main()