from pathlib import Path
from typing import Dict, List

import fitz


def _extract_year_from_filename(path: Path) -> int | None:
    for token in path.stem.replace("-", "_").split("_"):
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None


def extract_pdf_pages(pdf_path: Path, doc_type: str) -> List[Dict]:
    pages: List[Dict] = []
    with fitz.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if len(text) < 100:
                continue
            pages.append(
                {
                    "text": text,
                    "page": page_idx,
                    "source": pdf_path.name,
                    "doc_type": doc_type,
                    "year": _extract_year_from_filename(pdf_path),
                }
            )
    return pages


def extract_from_directory(directory: Path, doc_type: str) -> List[Dict]:
    extracted: List[Dict] = []
    for pdf_path in sorted(directory.glob("*.pdf")):
        extracted.extend(extract_pdf_pages(pdf_path, doc_type))
    return extracted

