import json

import faiss
from sentence_transformers import CrossEncoder, SentenceTransformer

from src.build_index import CHUNKS_FILE, EMBEDDING_MODEL, INDEX_FILE
from src.rewrite import rewrite_question

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CANDIDATES = 20 
BINDING_POOL = 150 
TOP_K = 4 


def is_binding(chunk):
    return chunk["source_type"].startswith("Binding law")


class Retriever:

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.reranker = CrossEncoder(RERANK_MODEL)
        self.index = faiss.read_index(str(INDEX_FILE))
        self.chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
        if self.index.ntotal != len(self.chunks):
            raise ValueError("Index and chunks file are out of sync. Rebuild the index.")
        self.last_query = None

    def _vector_search(self, query, n):
        vector = self.model.encode([QUERY_PREFIX + query], normalize_embeddings=True)
        scores, ids = self.index.search(vector.astype("float32"), n)
        return [
            {**self.chunks[i], "chunk_id": int(i), "score": float(score)}
            for score, i in zip(scores[0], ids[0])
            if i != -1
        ]

    def _candidates(self, queries, n):
        merged = {}
        for query in queries:
            for hit in self._vector_search(query, n):
                existing = merged.get(hit["chunk_id"])
                if existing is None or hit["score"] > existing["score"]:
                    merged[hit["chunk_id"]] = hit
        return sorted(merged.values(), key=lambda hit: hit["score"], reverse=True)

    def _rerank(self, query, hits):
        if not hits:
            return hits
        scores = self.reranker.predict([(query, hit["text"]) for hit in hits])
        for hit, score in zip(hits, scores):
            hit["rerank_score"] = float(score)
        return sorted(hits, key=lambda hit: hit["rerank_score"], reverse=True)

    def _best_binding(self, queries, rerank_query, exclude):
        deep = self._candidates(queries, BINDING_POOL)
        binding = [h for h in deep if is_binding(h) and h["chunk_id"] not in exclude][:10]
        ranked = self._rerank(rerank_query, binding)
        return ranked[0] if ranked else None

    def search(self, question, k=TOP_K, rewrite=True, ensure_binding=True, candidates=CANDIDATES):
        query = rewrite_question(question) if rewrite else question
        self.last_query = query
        queries = [question] if query == question else [question, query]

        hits = self._candidates(queries, max(candidates, k))

        rerank_query = " ".join(queries)
        hits = self._rerank(rerank_query, hits)
        top = hits[:k]

        if ensure_binding and not any(is_binding(hit) for hit in top):
            binding = self._best_binding(queries, rerank_query, {hit["chunk_id"] for hit in top})
            if binding:
                top[-1] = binding
        return top


def main():
    retriever = Retriever()
    test_questions = [
        "When do the obligations for high-risk AI systems listed in Annex III apply?",
        "What does AI literacy mean?",
        "Is emotion recognition in the workplace prohibited?",
        "Do I have to tell users they are talking to a chatbot?",
    ]
    for question in test_questions:
        results = retriever.search(question)
        print(f"\n=== {question}")
        print(f"    Search query: {retriever.last_query}")
        for result in results:
            print(
                f"  [{result['rerank_score']:6.2f}] doc {result['doc_id']}, "
                f"page {result['page_number']} ({result['source_type']})"
            )
            print("     " + result["text"][:160].replace("\n", " "))


if __name__ == "__main__":
    main()