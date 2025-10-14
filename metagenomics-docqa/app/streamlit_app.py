import streamlit as st
import json
from pathlib import Path
from typing import List, Dict, Any


BASE = Path(__file__).resolve().parents[1]
QA_SRC = BASE / "dataset/qa_filtered/qa.filtered.jsonl"
QA_HUMAN = BASE / "dataset/qa_human/qa.human.jsonl"
CHUNKS = BASE / "dataset/chunks/chunks.jsonl"
TOOLLOGS_DST = BASE / "dataset/toollogs/annotated.jsonl"


st.set_page_config(page_title="Genomics Align – Review Portal", layout="wide")
st.title("🔬 Genomics Align – Human Review Portal")


@st.cache_data(show_spinner=False)
def load_jsonl(path: Path) -> List[Dict[str, Any]]:
if not path.exists():
return []
with path.open() as f:
return [json.loads(line) for line in f if line.strip()]


@st.cache_data(show_spinner=False)
def index_chunks() -> Dict[str, Dict[str, Any]]:
return {c["chunk_id"]: c for c in load_jsonl(CHUNKS)}


chunks_idx = index_chunks()


tab1, tab2 = st.tabs(["Doc-grounded QA", "Tool Logs (beta)"])


with tab1:
st.subheader("Doc-grounded Q&A Validation")
qas = load_jsonl(QA_SRC)
st.caption(f"Loaded {len(qas)} items from qa_filtered.")


if not qas:
st.info("No QAs found. Run the dev/scripts pipeline first.")
st.success("Saved to toollogs/annotated.jsonl")