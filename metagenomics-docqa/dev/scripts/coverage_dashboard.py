import pandas as pd
from pathlib import Path
import json


TAX = Path("metadata/taxonomy.csv")
QA = Path("dataset/qa_filtered/qa.filtered.jsonl")


if __name__ == "__main__":
tax = pd.read_csv(TAX)
rows = []
if QA.exists():
with QA.open() as f:
for line in f:
r = json.loads(line)
rows.append({"topic": r.get("topic", "UNKNOWN")})
df = pd.DataFrame(rows)
counts = df.value_counts("topic").rename_axis("topic").reset_index(name="count") if len(df) else pd.DataFrame({"topic":[],"count":[]})
merged = tax.merge(counts, on="topic", how="left").fillna({"count": 0})
merged["progress"] = (merged["count"] / merged["quota"]).clip(0, 1)
print(merged.sort_values("progress", ascending=False).to_string(index=False))