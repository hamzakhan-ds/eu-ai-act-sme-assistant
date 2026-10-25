import time

from src.retrieve import Retriever

CASES = [
    (
        "When do the obligations for high-risk AI systems listed in Annex III apply?",
        "2 December 2027",
        {"01", "02"},
    ),
    (
        "Is emotion recognition in the workplace prohibited?",
        "infer emotions of a natural person in the areas of workplace",
        {"01"},  # the AI Act itself, not the guidance
    ),
    (
        "Do I have to tell users they are talking to a chatbot?",
        "interact directly with natural persons",
        {"01", "05"},  # Article 50, or the Article 50 guidelines
    ),
    (
        "What does AI literacy mean?",  # regression check: this already worked
        "means skills, knowledge and understanding",
        {"01"},
    ),
]


def normalise(text):
    return " ".join(text.split()).lower()


def is_correct(result, phrase, docs):
    return result["doc_id"] in docs and phrase.lower() in normalise(result["text"])


def report(label, results, phrase, docs, seconds):
    found = "YES" if any(is_correct(r, phrase, docs) for r in results) else "NO"
    print(f"  {label}: correct passage included: {found} ({seconds:.1f} s)")
    for result in results:
        marker = "*" if is_correct(result, phrase, docs) else " "
        print(f"    {marker} doc {result['doc_id']}, page {result['page_number']} ({result['source_type']})")


def main():
    retriever = Retriever()
    for question, phrase, docs in CASES:
        print(f"\n=== {question}")

        start = time.perf_counter()
        without = retriever.search(question, rewrite=False)
        report("Without rewriting", without, phrase, docs, time.perf_counter() - start)

        start = time.perf_counter()
        with_rewrite = retriever.search(question, rewrite=True)
        print(f"  Rewritten query: {retriever.last_query}")
        report("With rewriting   ", with_rewrite, phrase, docs, time.perf_counter() - start)


if __name__ == "__main__":
    main()