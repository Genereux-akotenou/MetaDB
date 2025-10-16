# Temporary teacher to test pipeline; replace with your LLM later.
from pathlib import Path
import json

CHUNKS = Path("dataset/chunks/chunks.jsonl")
OUT = Path("dataset/qa_autogen/qa.jsonl")

def make_qas(chunk):
    txt = chunk["text"]
    url = chunk["url"]
    lines = [l.strip() for l in txt.splitlines() if ":" in l and len(l.split()) < 40]
    qas = []
    for i, line in enumerate(lines[:5]):
        q = f"What does the field '{line.split(':',1)[0]}' specify?"
        a = f"According to the document, {line}."
        qas.append({
            "id": f"{chunk['chunk_id']}_q{i}",
            "topic": "UNKNOWN",
            "tool": None,
            "version": None,
            "url": url,
            "chunk_id": chunk["chunk_id"],
            "question": q,
            "answer": a,
            "citations": [{"char_start": 0, "char_end": min(len(txt), 300)}],
        })
        return qas

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with CHUNKS.open() as f, OUT.open("w", encoding="utf-8") as g:
        for line in f:
            ch = json.loads(line)
            for qa in make_qas(ch):
                print("autogen done")