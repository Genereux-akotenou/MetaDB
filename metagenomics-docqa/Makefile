.PHONY: setup e2e app api clean

setup:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

e2e_:
	.venv/bin/python dev/scripts/scrape_one.py https://github.com/OpenGene/fastp
	.venv/bin/python dev/scripts/scrape_one.py https://github.com/DerrickWood/kraken2
	.venv/bin/python dev/scripts/scrape_one.py https://github.com/biobakery/MetaPhlAn
	.venv/bin/python dev/scripts/chunk_raw.py
	.venv/bin/python dev/scripts/qg_teacher_stub.py
	.venv/bin/python dev/scripts/validate_and_filter.py

e2e:
	.venv/bin/python dev/scripts/scrape_one.py https://github.com/OpenGene/fastp
	.venv/bin/python dev/scripts/chunk_raw.py
	.venv/bin/python dev/scripts/qg_teacher_stub.py

serve:
	.venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

clean:
	rm -f dataset/raw/*.jsonl dataset/chunks/*.jsonl dataset/qa_autogen/*.jsonl dataset/qa_filtered/*.jsonl dataset/qa_human/*.jsonl