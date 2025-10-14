# METAGENOMICS-DOCQA

End-to-end pipeline to collect, process, and human-validate datasets for genomics LLM alignment.

## Run
- See Quick start in the root canvas or `Makefile` targets `e2e` and `app`.



## Project layout

```py
metagenomics-docqa/
├─ README.md
├─ requirements.txt
├─ Makefile
├─ metadata/
│ ├─ taxonomy.csv
│ └─ sources.csv
├─ dataset/
│ ├─ raw/ # scraped pages (jsonl)
│ ├─ chunks/ # 400–800 token chunks (jsonl)
│ ├─ qa_autogen/ # teacher-generated QAs (jsonl)
│ ├─ qa_filtered/ # schema-validated & auto-filtered QAs (jsonl)
│ └─ qa_human/ # human-reviewed QAs (jsonl)
├─ dev/
│ ├─ scripts/
│ │ ├─ scrape_one.py
│ │ ├─ chunk_raw.py
│ │ ├─ qg_teacher_stub.py
│ │ ├─ validate_and_filter.py
│ │ ├─ coverage_dashboard.py
│ │ └─ utils_io.py
│ └─ prompts/
│ ├─ teacher_qg.txt
│ └─ verifier_faithfulness.txt
└─ app/
└─ streamlit_app.py
```

## 2 Quick start

### 1- Create & activate env
python -m venv .venv && source .venv/bin/activate


### 2- Install deps
pip install -r requirements.txt


### 3- Seed metadata
mkdir -p metadata dataset/{raw,chunks,qa_autogen,qa_filtered,qa_human,planner,toollogs}
cp metadata/taxonomy.csv metadata/sources.csv /tmp 2>/dev/null || true # (placeholders below)


### 4- Run minimal E2E on a few URLs
```bash
python dev/scripts/scrape_one.py https://github.com/OpenGene/fastp
python dev/scripts/scrape_one.py https://github.com/DerrickWood/kraken2
python dev/scripts/scrape_one.py https://github.com/biobakery/MetaPhlAn
python dev/scripts/chunk_raw.py
python dev/scripts/qg_teacher_stub.py
python dev/scripts/validate_and_filter.py
```

### 5- Launch human review portal

```bash
streamlit run app/streamlit_app.py
```