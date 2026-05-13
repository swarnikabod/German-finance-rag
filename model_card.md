# Model Card — German Financial Document RAG

> Retrieval-Augmented Generation system for ECB and BaFin regulatory documents.
> Built for financial analysts, risk teams, and compliance professionals in the EU.

---

## 1. Model Details

| Property | Value |
|----------|-------|
| System type | Retrieval-Augmented Generation (RAG) |
| Embedding model | `intfloat/multilingual-e5-base` |
| LLM | Gemma3:1b via Ollama (local) / Llama-3.1-8b via Groq (deployed) |
| Vector store | ChromaDB (persistent local index) |
| Chunk size | 256 tokens, 128 overlap |
| Retrieval | Top-6 similarity search |
| Languages | English, German |
| Version | 1.0.0 |
| Last updated | May 2026 |
| Author | Swarnika Boddula |

---

## 2. Intended Use

**Primary use cases:**
- Retrieval-augmented Q&A over ECB and BaFin public regulatory documents
- Analyst workflows: rapid document navigation with evidence-backed citations
- Compliance research: locating specific regulatory requirements with page references
- Due diligence support: querying monetary policy decisions and supervisory guidance

**Out-of-scope uses:**
- Autonomous legal or investment decision-making without human review
- Processing of confidential, non-public, or proprietary documents
- Trading signal generation or market prediction
- Replacing qualified legal or regulatory counsel

---

## 3. Data Sources

| Document | Publisher | Language | Year | Public |
|----------|-----------|----------|------|--------|
| ECB Annual Report | European Central Bank | EN | 2023, 2024 | ✅ |
| ECB Annual Accounts | European Central Bank | EN | 2024 | ✅ |
| ECB Financial Stability Review | European Central Bank | EN | Nov 2024, May 2025, Nov 2025 | ✅ |
| BaFin Annual Report | Federal Financial Supervisory Authority | EN + DE | 2023, 2024 | ✅ |

All source documents are publicly available on official ECB and BaFin websites.
No proprietary, confidential, or personally identifiable information is processed.

---

## 4. EU AI Act Compliance Assessment

This system falls under the **EU Artificial Intelligence Act (Regulation 2024/1689)**,
which entered into force August 2024 and applies from August 2026.

### 4.1 Risk Classification

Under Article 6 and Annex III, this system is assessed as **Limited Risk** (not High Risk) because:
- It does not make autonomous decisions affecting individuals' rights or access to services
- It operates as a decision-support tool requiring mandatory human review
- It does not process biometric data, credit scoring, or employment decisions
- Source documents are public regulatory publications, not personal data

However, if deployed in a context where outputs directly influence **credit decisions, regulatory filings, or compliance determinations**, the system would require reclassification as **High Risk** under Annex III, point 5(b) (AI systems used in management of critical infrastructure) or point 6 (employment and workers management).

### 4.2 Article 13 — Transparency Requirements

*"Providers shall ensure that high-risk AI systems are designed and developed in such a way as to ensure that their operation is sufficiently transparent to enable deployers to interpret the system's output and use it appropriately."*

This system implements transparency through:

**Source citation:** Every answer includes the source document filename and page number, enabling the analyst to verify the claim directly against the original regulatory text.

**Context display:** Retrieved chunks are shown alongside the answer in the UI, allowing the user to assess retrieval quality and identify potential hallucinations.

**Model disclosure:** The sidebar explicitly states the embedding model (`multilingual-e5-base`), LLM (`Gemma3:1b`), vector database (ChromaDB), chunk size, and retrieval parameters — all factors that influence output quality.

**Confidence signalling:** The system is instructed to explicitly state when the answer cannot be found in the indexed corpus, rather than generating unsupported responses.

### 4.3 Article 14 — Human Oversight

*"High-risk AI systems shall be designed and developed in such a way, including with appropriate human-machine interface tools, that they can be effectively overseen by natural persons."*

Measures implemented:
- All outputs are labelled as AI-generated and require analyst review before downstream use
- Page-level citations enable spot-checking against source documents within seconds
- The system cannot execute trades, file regulatory reports, or take any autonomous action
- No output is cached or reused without re-retrieval from current document versions
- Clear labelling in the UI: "RAG Response · [model name]" — not presented as authoritative fact

### 4.4 Article 9 — Risk Management

Known risks and mitigations:

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Hallucination (answer not grounded in context) | Medium | High | Source citations; explicit "not found" fallback; prompt grounding instructions |
| Retrieval failure (relevant chunk not retrieved) | Medium | Medium | Top-6 retrieval; 256-token chunks with 128 overlap; multilingual embeddings |
| Outdated information (new regulatory guidance not indexed) | High | Medium | Document version tracking in metadata; regular re-ingestion pipeline |
| Misuse for autonomous compliance decisions | Low | Very High | UI labelling; model card; terms of use |
| Cross-lingual retrieval errors (DE/EN mismatch) | Low | Medium | multilingual-e5-base trained on 100 languages; BaFin docs indexed in both EN and DE |

### 4.5 Article 10 — Data Governance

- Training data: embedding model pre-trained on public multilingual corpus (not financial-specific)
- Inference data: public ECB and BaFin documents only
- No personal data processed at any stage
- No data logging or retention of user queries in production deployment
- ChromaDB stored locally; no data sent to third parties except LLM inference API (Groq)

### 4.6 GDPR Considerations

- No personal data collected from users
- Query text sent to Groq API for inference — covered by Groq's data processing agreement
- Users should not input personal or confidential information into the query interface

---

## 5. Performance Evaluation

Evaluated on 20-question financial analyst QA set covering ECB monetary policy,
balance sheet items, BaFin regulatory requirements, and financial stability risks.

| Model configuration | Avg score | p50 latency | p95 latency |
|--------------------|-----------|-------------|-------------|
| Baseline: all-MiniLM-L6-v2 (English-only) | 0.113 | 39.7s | 69.8s |
| **Improved: multilingual-e5-base** | **0.142** | **~15s** | **~30s** |
| Delta | **+25.7%** | **-62%** | **-57%** |

*Score = keyword overlap between RAG answer and ground truth. Simple metric — RAGAS faithfulness evaluation planned for v1.1.*

**Key finding:** Switching from English-only to multilingual embeddings improved retrieval quality by 26% and reduced latency by 62%, primarily because ECB and BaFin documents contain German regulatory terminology that English-only models embed poorly.

---

## 6. Limitations

**Document coverage:** Answers are bounded by indexed documents. The BaFin 2025 Annual Report (expected June 2026) is not yet available and will be added on publication.

**Table extraction:** PyMuPDF extracts tables as plain text, which degrades structured data retrieval (e.g., balance sheet line items). Future work: table-aware extraction using `pdfplumber`.

**Chunk boundary effects:** Financial figures that span sentence boundaries may be split across chunks, reducing retrieval precision for specific numerical queries.

**LLM quality:** Gemma3:1b (local) produces adequate but not expert-level financial analysis. Production deployment should use a larger model (Claude, GPT-4, or Llama-3-70b) for higher-stakes queries.

**Language asymmetry:** German-language queries against English-only chunks (and vice versa) perform slightly worse than same-language retrieval despite multilingual embeddings.

---

## 7. Fairness and Bias Analysis

**Linguistic bias:** The corpus is predominantly English with German versions of BaFin reports. Queries in German against English-only ECB documents may retrieve slightly less relevant context.

**Temporal bias:** The corpus covers 2023–2025. Regulatory positions evolve; older documents may contradict current guidance without clear signals to the user.

**Institutional bias:** Only ECB and BaFin documents are indexed. Other relevant regulators (EBA, ESRB, Bundesbank) are not represented in v1.0.

**Mitigation roadmap:**
- Add EBA and ESRB publications in v1.1
- Add document date to source citations so users can assess recency
- Add Bundesbank Monthly Reports for macroeconomic context

---

## 8. Regulatory Alignment

| Framework | Alignment status |
|-----------|-----------------|
| EU AI Act (2024/1689) | Limited Risk — compliant as decision-support tool |
| GDPR (2016/679) | Compliant — no personal data processed |
| Basel IV (CRR3) | Not applicable — tool does not perform capital calculations |
| DORA (2022/2554) | Partially applicable — ICT risk documentation recommended for production deployment |
| MaRisk (BaFin) | Not applicable to the tool itself; tool assists in querying MaRisk requirements |

---

## 9. Contact and Governance

**Author:** Swarnika Boddula
**LinkedIn:** [linkedin.com/in/swarnika-boddula-1b5166209](https://www.linkedin.com/in/swarnika-boddula-1b5166209/)
**Repository:** [github.com/swarnikabod/German-finance-rag](https://github.com/swarnikabod/German-finance-rag)

For questions about deployment in regulated environments, data governance, or EU AI Act
compliance assessment, please contact via LinkedIn.

---

*This model card follows the Model Card framework (Mitchell et al., 2019) adapted for
EU AI Act compliance documentation requirements.*