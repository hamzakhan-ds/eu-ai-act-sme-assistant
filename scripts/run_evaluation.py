import csv
import time
from pathlib import Path

from src.answer import Assistant

QUESTIONS_FILE = Path("eval/questions.csv")
RESULTS_FILE = Path("eval/results.md")
PAUSE_SECONDS = 20


def main():
    with QUESTIONS_FILE.open(newline="", encoding="utf-8") as f:
        questions = list(csv.DictReader(f))

    assistant = Assistant()
    lines = ["# Evaluation results", ""]

    for position, row in enumerate(questions, start=1):
        start = time.perf_counter()
        result = assistant.ask(row["question"])
        seconds = time.perf_counter() - start

        lines.append(f"## Q{row['id']}. {row['question']}")
        lines.append(
            f"*Category: {row['category']} · Expected: {row['expected']} · "
            f"Time: {seconds:.1f} s · Best relevance: {result['best_score']:.2f}*"
        )
        lines.append("")
        lines.append(result["answer"])
        lines.append("")
        lines.append("**Sources:**")
        if result["sources"]:
            for s in result["sources"]:
                lines.append(f"- [{s['number']}] {s['title']}, page {s['page']} ({s['source_type']})")
        else:
            lines.append("- (none)")
        lines.append("")

        print(f"Q{row['id']} done ({seconds:.1f} s)")
        if position < len(questions):
            time.sleep(PAUSE_SECONDS)

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved results to {RESULTS_FILE}")


if __name__ == "__main__":
    main()