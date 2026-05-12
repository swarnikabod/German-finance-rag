from pathlib import Path

from src.ingestion.extractor import extract_pdf_pages


def test_extract_pdf_pages_handles_missing_file():
    missing = Path("does_not_exist.pdf")
    try:
        extract_pdf_pages(missing, "ecb")
        assert False, "Expected an exception for missing file"
    except Exception:
        assert True

