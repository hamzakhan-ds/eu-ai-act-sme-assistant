from importlib.metadata import version
from pathlib import Path

PACKAGES = [
    "streamlit",
    "langchain-core",
    "langchain-groq",
    "langchain-text-splitters",
    "groq",
    "faiss-cpu",
    "sentence-transformers",
    "transformers",
    "torch",
    "numpy",
    "pdfplumber",
    "python-dotenv",
    "huggingface-hub",
]

lines = ["--extra-index-url https://download.pytorch.org/whl/cpu"]
for name in PACKAGES:
    installed = version(name)
    if name == "torch" and "+" not in installed:
        installed += "+cpu" 
    lines.append(f"{name}=={installed}")

Path("requirements.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))