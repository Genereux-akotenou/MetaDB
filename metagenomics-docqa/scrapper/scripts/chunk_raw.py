from pathlib import Path
import json
import tiktoken

RAW = Path("dataset/raw/raw.jsonl")
OUT = Path("dataset/chunks/chunks.jsonl")
enc = tiktoken.get_encoding("cl100k_base")

def chunk_text(text, url, min_tok=400, max_tok=800, stride=160):
    toks = enc.encode(text)
    for i in range(0, len(toks), stride):
        window = toks[i:i + max_tok]
        if len(window) < min_tok:
            break
        chunk_text = enc.decode(window)

        yield {
            "chunk_id": f"{abs(hash(url))}_{i}",
            "url": url,
            "char_start": None,
            "char_end": None,
            "text": chunk_text,
        }

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print('--')
    with RAW.open() as f, OUT.open("a", encoding="utf-8") as g:
        for line in f:
            print(line)
            rec = json.loads(line)
            print(rec)
            if not rec.get("ok"):
                continue
            print('--')
            for ch in chunk_text(rec["text"], rec["url"]):
                g.write(json.dumps(ch, ensure_ascii=False) + "\n")
                print("chunked")