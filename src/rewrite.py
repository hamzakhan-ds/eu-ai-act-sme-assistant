import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

REWRITE_MODEL = os.getenv("REWRITE_MODEL", "openai/gpt-oss-20b")

SYSTEM_PROMPT = (
    "You rewrite a user's question about the EU AI Act as a short search query that uses "
    "the wording of the legal text. Use only terms that relate to this specific question. "
    "Do not add unrelated legal terms, article numbers the user did not mention, or the "
    "words 'AI Act' or 'search query'. Do not answer the question. "
    "Reply with the search query only: one line, at most 20 words."
)

EXAMPLES = [
    (
        "Do we need to label AI-generated images on our website?",
        "obligation to disclose that image content has been artificially generated or manipulated",
    ),
    (
        "What fines can we get for breaking the rules?",
        "penalties and administrative fines for infringements of obligations",
    ),
    (
        "Who counts as a deployer?",
        "definition of deployer of an AI system",
    ),
]

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=REWRITE_MODEL,
            temperature=0,
            max_tokens=400,
            reasoning_effort="low",
        )
    return _llm


def _build_messages(question):
    """System rules, then the worked examples as a conversation, then the real question."""
    messages = [("system", SYSTEM_PROMPT)]
    for example_question, example_query in EXAMPLES:
        messages.append(("human", example_question))
        messages.append(("ai", example_query))
    messages.append(("human", question))
    return messages


def rewrite_question(question):
    try:
        response = _get_llm().invoke(_build_messages(question))
        query = str(response.content).strip()
        return query or question
    except Exception as error:
        print(f"[rewrite] failed, using the original question: {error}")
        return question