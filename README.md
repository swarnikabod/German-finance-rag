# German Finance RAG

RAG pipeline for German financial/regulatory documents (ECB + BaFin).  
It ingests PDFs, extracts and chunks text, embeds with German/English-capable models, stores vectors in ChromaDB, and serves citation-grounded answers via Streamlit.

## Architecture

```text
            +---------------------------+
            | ECB/BaFin PDF Documents  |
            +-------------+-------------+
                          |
                          v
                +---------+---------+
                | PyMuPDF Extractor |
                +---------+---------+
                          |
                          v
          +---------------+----------------+
          | Recursive Text Chunker (512/64)|
          +---------------+----------------+
                          |
                          v
            +-------------+-------------+
            | Embeddings (Jina-DE etc.) |
            +-------------+-------------+
                          |
                          v
                 +--------+--------+
                 | ChromaDB Store  |
                 +--------+--------+
                          |
                          v
             +------------+-------------+
             | Retriever + Claude RAG   |
             +------------+-------------+
                          |
                          v
                 +--------+--------+
                 | Streamlit Chat  |
                 +-----------------+
```

## Quickstart

1. `python -m venv .venv && .venv\\Scripts\\activate`
2. `pip install -r requirements.txt`
3. `python scripts/ingest.py --source ecb` then `streamlit run app/streamlit_app.py`

## Embedding Model Comparison

| Model | Strengths | Weaknesses | Recommended Use |
|---|---|---|---|
| `all-MiniLM-L6-v2` | Fast, lightweight baseline | Weaker German finance semantics | Quick prototyping |
| `jinaai/jina-embeddings-v2-base-de` | Strong DE/EN bilingual retrieval, long context support | Higher compute cost | Default production baseline |
| `FinanceMTEB/FinE5` | Finance-tuned retrieval quality | May require model-specific tuning | Finance-heavy corpora experiments |

## RAGAS Metrics (Placeholder)

| Pipeline | Faithfulness | Answer Relevancy | Context Precision | Context Recall |
|---|---:|---:|---:|---:|
| Baseline (MiniLM) | TBD | TBD | TBD | TBD |
| Improved (Jina-DE) | TBD | TBD | TBD | TBD |

## Live Demo

- Placeholder: [Add Streamlit deployment URL](https://example.com)
