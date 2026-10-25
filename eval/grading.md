# Evaluation grading

**Method.** 10 new questions, not used during development, covering definitions, prohibitions,
obligations, dates, penalties, scope, an unanswerable question and an off-topic question.
The system was not changed after running them. Each answer was graded on correctness,
whether cited pages support the claims, and whether binding law was cited for legal questions.
Four citations were spot-checked against the source PDFs.

| # | Category | Correct | Citations supported | Binding law cited | Notes |
|---|---|---|---|---|---|
| 1 | Definition | Yes | Yes (p.5 verified) | Yes | Accurate Article 3(1) definition |
| 2 | Prohibition | Partial | Yes | Yes | Gives one of two conditions for the social scoring ban; misnames the AI Act as amended by itself |
| 3 | Prohibition | Partial | Yes | Yes | Opens with "Yes" although the default is prohibition; omits the three permitted purposes and prior authorisation |
| 4 | Penalties | Yes | Yes (p.116 verified) | Yes | EUR 35 million or 7% of worldwide turnover |
| 5 | Transparency | Yes | Yes | Yes | Deepfake disclosure duty and exceptions |
| 6 | Obligations | Partial | Yes (p.38 verified) | Yes | Incomplete list; applies a public-authority registration duty to all deployers |
| 7 | Dates | Yes | Partial | No | Correct date; several supporting claims uncited; cites guidance only |
| 8 | Scope | Yes | Yes | No | Correct; inserted binding passage (p.94, Article 75) was unrelated |
| 9 | Unanswerable | Yes | n/a | n/a | Correctly said the sources do not contain this |
| 10 | Off-topic | Yes | n/a | n/a | Declined by the relevance gate (score -9.45) |

## Summary

- Correct: 7 of 10; partially correct: 3; wrong: 0
- Refusals: 2 of 2 handled correctly (no invented answers)
- Binding law cited on legal questions: 6 of 8
- Response time: 2.6 to 4.8 seconds

## Weaknesses found

1. Incomplete answers for provisions with many parts (Q3, Q6): only 4 passages reach the model.
2. Misleading framing despite mostly correct facts (Q3).
3. Occasional uncited claims added from the model's general knowledge (Q7).
4. The binding-law guarantee can insert an irrelevant passage (Q8). Planned fix: only insert
   a binding passage whose re-ranker score is above the relevance threshold.

## Caveats

10 questions is a small sample. Grading was done by the author with partial verification
against the source PDFs, not by independent legal experts.