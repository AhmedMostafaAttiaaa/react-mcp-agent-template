import os

import ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.environ["OLLAMA_HOST"]

client = ollama.Client(host=OLLAMA_HOST)

print(f"--- Models available at {OLLAMA_HOST} ---")
models = client.list()["models"]
for model in models:
    print(model["model"])

# Save model list to a small markdown file for easy reference when switching models
md_path = "models.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write(f"# Ollama models available at `{OLLAMA_HOST}`\n\n")
    f.write("| Model name | Size (GB) |\n")
    f.write("|---|---|\n")
    for model in models:
        size_gb = model.get("size", 0) / (1024 ** 3)
        f.write(f"| `{model['model']}` | {size_gb:.1f} |\n")

print(f"\nSaved model list to {md_path}")
