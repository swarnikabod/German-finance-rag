import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.ingestion.chunker import chunk_pages
from src.ingestion.downloader import download_ecb_reports, download_bafin_reports, ensure_source_dirs
from src.ingestion.extractor import extract_from_directory
from src.vectorstore.store import get_collection_size, upsert_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest ECB/BaFin PDFs into ChromaDB.")
    parser.add_argument(
        "--source",
        choices=["ecb", "bafin", "all"],
        default="all",
        help="Data source to ingest.",
    )
    args = parser.parse_args()

    config = Config()
    ensure_source_dirs(config)

    if args.source in {"ecb", "all"}:
        print("Downloading ECB reports...")
        download_ecb_reports(config)

    pages = []
    if args.source in {"ecb", "all"}:
        print("Extracting ECB PDFs...")
        pages.extend(extract_from_directory(config.raw_ecb_dir, "ecb"))
    # Find this block in ingest.py and replace it:
    if args.source in {"bafin", "all"}:
        print("Downloading BaFin reports...")
        download_bafin_reports(config)   # ADD THIS LINE
        print("Extracting BaFin PDFs...")
        pages.extend(extract_from_directory(config.raw_bafin_dir, "bafin"))

    print(f"Total documents ingested: {len(pages)}")
    chunks = chunk_pages(pages, config)
    print(f"Total chunks created: {len(chunks)}")

    added = upsert_documents(chunks, config)
    collection_size = get_collection_size(config)
    print(f"Chunks upserted this run: {added}")
    print(f"ChromaDB collection size: {collection_size}")


if __name__ == "__main__":
    main()

