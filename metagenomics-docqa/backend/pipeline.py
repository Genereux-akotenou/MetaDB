import os
from typing import List, Dict

import httpx


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


def build_qg_prompt(content: str) -> str:
    return (
        "You are an expert in metagenomics. Given the following document chunk, "
        "generate 3 diverse high-quality question-answer pairs grounded in the text. "
        "Each answer must be directly supported by the chunk. Return as JSON lines with keys 'question' and 'answer'.\n\n"
        f"CHUNK:\n{content[:4000]}\n\n"
        "Output 3 lines, each a compact JSON object."
    )


def call_ollama(prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    with httpx.Client(timeout=60) as client:
        r = client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")


def parse_jsonl_lines(text: str) -> List[Dict]:
    import json

    items: List[Dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            # try naive split
            if line.startswith("{") and line.endswith("}") and '"question"' in line and '"answer"' in line:
                try:
                    items.append(json.loads(line))
                except Exception:
                    continue
            else:
                continue
    return items


def generate_qas_for_chunk(content: str) -> List[Dict[str, str]]:
    prompt = build_qg_prompt(content)
    raw = call_ollama(prompt)
    items = parse_jsonl_lines(raw)
    results: List[Dict[str, str]] = []
    for it in items:
        q = str(it.get("question", "")).strip()
        a = str(it.get("answer", "")).strip()
        if q and a:
            results.append({"question": q, "answer": a})
    return results[:3]


