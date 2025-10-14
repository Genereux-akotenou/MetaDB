from pathlib import Path
import json
from jsonschema import validate, ValidationError


SRC = Path("dataset/qa_autogen/qa.jsonl")
DST = Path("dataset/qa_filtered/qa.filtered.jsonl")


SCHEMA = {
"type": "object",
"required": ["id", "url", "chunk_id", "question", "answer", "citations"],
"properties": {
"id": {"type": "string"},
"topic": {"type": ["string", "null"]},
"tool": {"type": ["string", "null"]},
"version": {"type": ["string", "null"]},
"url": {"type": "string"},
"chunk_id": {"type": "string"},
"question": {"type": "string", "minLength": 8},
"answer": {"type": "string", "minLength": 8},
"citations": {
"type": "array",
"minItems": 1,
"items": {
"type": "object",
"required": ["char_start", "char_end"],
"properties": {
"char_start": {"type": ["integer", "null"]},
"char_end": {"type": ["integer", "null"]},
},
},
},
},
}




def ok(qa):
try:
validate(qa, SCHEMA)
except ValidationError:
return False
if "http" not in qa["url"]:
return False
bad = ["as an ai", "i cannot", "sorry"]
if any(w in qa["answer"].lower() for w in bad):
return False
return True




if __name__ == "__main__":
DST.parent.mkdir(parents=True, exist_ok=True)
kept = 0
with SRC.open() as f, DST.open("w", encoding="utf-8") as g:
for line in f:
qa = json.loads(line)
if ok(qa):
g.write(json.dumps(qa, ensure_ascii=False) + "\n")
kept += 1
print("kept", kept)