.PHONY: e2e app clean

venv:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

e2e_:
	source .venv/bin/activate && \
	python dev/scripts/scrape_one.py https://github.com/OpenGene/fastp ; \
	python dev/scripts/scrape_one.py https://github.com/DerrickWood/kraken2 ; \
	python dev/scripts/scrape_one.py https://github.com/biobakery/MetaPhlAn ; \
	python dev/scripts/chunk_raw.py ; \
	python dev/scripts/qg_teacher_stub.py ; \
	python dev/scripts/validate_and_filter.py

e2e:
	source .venv/bin/activate && \
	python dev/scripts/scrape_one.py https://github.com/OpenGene/fastp ; \
	python dev/scripts/chunk_raw.py ; \
	python dev/scripts/qg_teacher_stub.py

app:
	streamlit run app/streamlit_app.py

clean:
	rm -f dataset/raw/*.jsonl dataset/chunks/*.jsonl dataset/qa_autogen/*.jsonl dataset/qa_filtered/*.jsonl dataset/qa_human/*.jsonl