# Model Card

## Model Details
- **Primary embedding model:** `jinaai/jina-embeddings-v2-base-de`
- **Task:** bilingual German/English retrieval embeddings for regulatory finance documents
- **Vector store:** ChromaDB (persistent local index)

## Intended Use
- Retrieval-augmented question answering over ECB and BaFin public annual reports.
- Support for analyst workflows, document navigation, and evidence-backed summaries.
- Not intended for autonomous legal or investment decision making.

## Data Sources
- ECB public annual reports and annual accounts PDFs.
- BaFin public annual reports and regulatory publications.
- All content should come from public, non-confidential sources.

## Limitations
- Quality depends on OCR/text extraction quality of PDFs.
- Answers are limited to indexed documents; missing documents produce incomplete coverage.
- Citation quality depends on chunking granularity and metadata integrity.

## EU AI Act Considerations
- **Transparency:** system is RAG-based and should expose cited sources for each claim.
- **Human oversight:** outputs require analyst review before downstream action.
- **Traceability:** metadata (source + page) retained for auditability.

## Fairness Analysis
- Placeholder: Add domain-specific fairness and bias assessment for multilingual regulatory content.
