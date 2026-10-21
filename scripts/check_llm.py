import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

model_name = os.getenv("LLM_MODEL")
if not os.getenv("GROQ_API_KEY") or not model_name:
    raise SystemExit("Missing GROQ_API_KEY or LLM_MODEL in .env")

print(f"Testing model: {model_name}")

llm = ChatGroq(model=model_name, temperature=0)
response = llm.invoke("Reply with exactly these words: Connection successful")

print("Response from the model:")
print(response.content)