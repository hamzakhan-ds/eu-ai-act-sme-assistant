import streamlit as st

from src.answer import Assistant
from src.ingest import load_sources

MAX_QUESTIONS_PER_SESSION = 10
MAX_QUESTION_LENGTH = 500  
GITHUB_URL = "https://github.com/hamzakhan-ds/eu-ai-act-sme-assistant"

st.set_page_config(page_title="EU AI Act Assistant for SMEs", page_icon="⚖️")


@st.cache_resource(show_spinner="Loading the assistant (first visit only)...")
def load_assistant():
    return Assistant()


def show_sources(sources):
    if not sources:
        return
    lines = [
        f"[{s['number']}] [{s['title']}]({s['url']}), page {s['page']} · *{s['source_type']}*"
        for s in sources
    ]
    with st.expander("Sources"):
        st.markdown("\n\n".join(lines))


with st.sidebar:
    st.header("About")
    st.markdown(
        "This assistant answers questions about the **EU AI Act** using only official "
        "EU documents. It finds the most relevant passages, then an AI model writes an "
        "answer that cites them."
    )
    st.subheader("Sources")
    for source in load_sources():
        st.markdown(f"- [{source['title']}]({source['url']}) · *{source['source_type']}*")
    st.caption("Reused under the European Commission's reuse policy (Decision 2011/833/EU).")
    st.markdown(f"[View the code on GitHub]({GITHUB_URL})")

st.title("EU AI Act Assistant for SMEs")
st.caption("Plain-English answers about the EU AI Act, with citations to official sources.")
st.warning(
    "**Not legal advice.** This is an unofficial portfolio project and can make mistakes. "
    "Always check the cited sources. Please don't enter personal or confidential "
    "information: questions are sent to an external AI service to generate answers."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            show_sources(message.get("sources", []))

questions_asked = sum(1 for m in st.session_state.messages if m["role"] == "user")

if questions_asked >= MAX_QUESTIONS_PER_SESSION:
    st.info(
        f"You've reached the limit of {MAX_QUESTIONS_PER_SESSION} questions for this session. "
        "This keeps the free service available for everyone."
    )
elif question := st.chat_input("Ask a question about the EU AI Act..."):
    if len(question) > MAX_QUESTION_LENGTH:
        st.error(f"Please keep your question under {MAX_QUESTION_LENGTH} characters.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching the sources..."):
                result = load_assistant().ask(question)
            st.markdown(result["answer"])
            show_sources(result["sources"])

        st.session_state.messages.append(
            {"role": "assistant", "content": result["answer"], "sources": result["sources"]}
        )