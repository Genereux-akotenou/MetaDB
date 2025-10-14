import sys, time
from pathlib import Path
import json
import trafilatura


OUT = Path("dataset/raw/raw.jsonl")




def scrape(url: str) -> dict:
html = trafilatura.fetch_url(url)
if not html:
return {"url": url, "ok": False, "reason": "fetch_failed"}
text = trafilatura.extract(html, include_tables=True, include_formatting=True)
if not text:
return {"url": url, "ok": False, "reason": "extract_failed"}
return {
"url": url,
"ok": True,
"title": None,
"text": text,
"retrieved_at": int(time.time()),
}




if __name__ == "__main__":
url = sys.argv[1]
OUT.parent.mkdir(parents=True, exist_ok=True)
rec = scrape(url)
with OUT.open("a", encoding="utf-8") as f:
f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(rec["ok"], rec.get("reason", "ok"))