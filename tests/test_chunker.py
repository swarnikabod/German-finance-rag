from src.config import Config
from src.ingestion.chunker import chunk_pages


def test_chunker_returns_documents_with_metadata():
    cfg = Config(chunk_size=80, chunk_overlap=10)
    pages = [
        {
            "text": "Dies ist ein Testtext. " * 30,
            "page": 1,
            "source": "ecb_annual_report_2024.pdf",
            "doc_type": "ecb",
            "year": 2024,
        }
    ]
    docs = chunk_pages(pages, cfg)
    assert len(docs) > 1
    assert docs[0].metadata["source"] == "ecb_annual_report_2024.pdf"
    assert docs[0].metadata["page"] == 1

