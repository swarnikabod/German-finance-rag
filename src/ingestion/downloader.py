import requests
from pathlib import Path
from src.config import Config

ECB_PDFS = {
    "ecb_annual_report_2024.pdf": "https://www.ecb.europa.eu/pub/pdf/annrep/ecb.ar2024~8402d8191f.en.pdf",
    "ecb_annual_report_2023.pdf": "https://www.ecb.europa.eu/pub/pdf/annrep/ecb.ar2023~d033c21ac2.en.pdf",
    "ecb_annual_accounts_2024.pdf": "https://www.ecb.europa.eu/pub/pdf/annrep/ecb.annualaccounts2024~718377b1c1.en.pdf",
    # 2025 Financial Stability Reviews — most current docs available
    "ecb_fsr_nov2025.pdf": "https://www.ecb.europa.eu/press/financial-stability-publications/fsr/pdf/ecb.fsr202511~263b5810d4.en.pdf",
    "ecb_fsr_may2025.pdf": "https://www.ecb.europa.eu/press/financial-stability-publications/fsr/pdf/ecb.fsr202505~0cde5244f6.en.pdf",
    "ecb_fsr_nov2024.pdf": "https://www.ecb.europa.eu/pub/pdf/fsr/ecb.fsr202411~dd60fc02c3.en.pdf",
}

BAFIN_PDFS = {
    # Latest available — 2025 report publishes May 2026
    "bafin_annual_report_2024_en.pdf": "https://www.bafin.de/SharedDocs/Downloads/EN/Jahresbericht/dl_jb_2024_en.pdf?__blob=publicationFile&v=2",
    "bafin_annual_report_2023_en.pdf": "https://www.bafin.de/SharedDocs/Downloads/EN/Jahresbericht/dl_jb_2023_en.pdf?__blob=publicationFile&v=3",
    "bafin_annual_report_2022_en.pdf": "https://www.bafin.de/SharedDocs/Downloads/EN/Jahresbericht/dl_jb_2022_en.pdf?__blob=publicationFile&v=8",
    # German versions for Jina-DE embedding quality
    "bafin_annual_report_2024_de.pdf": "https://www.bafin.de/SharedDocs/Downloads/DE/Jahresbericht/dl_jb_2024.pdf?__blob=publicationFile&v=7",
    "bafin_annual_report_2023_de.pdf": "https://www.bafin.de/SharedDocs/Downloads/DE/Jahresbericht/dl_jb_2023.pdf?__blob=publicationFile&v=9",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/pdf,*/*",
}


def ensure_source_dirs(config: Config) -> None:
    config.raw_ecb_dir.mkdir(parents=True, exist_ok=True)
    config.raw_bafin_dir.mkdir(parents=True, exist_ok=True)


def _download_batch(pdf_dict: dict, output_dir: Path, source_name: str) -> None:
    for filename, url in pdf_dict.items():
        dest = output_dir / filename
        if dest.exists():
            print(f"  ✓ Already exists: {filename}")
            continue
        print(f"  ↓ Downloading {filename}...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=120)
            r.raise_for_status()
            dest.write_bytes(r.content)
            print(f"  ✓ Saved {filename} ({len(r.content) // 1024} KB)")
        except Exception as e:
            print(f"  ✗ Failed {filename}: {e}")


def download_ecb_reports(config: Config) -> None:
    _download_batch(ECB_PDFS, config.raw_ecb_dir, "ECB")


def download_bafin_reports(config: Config) -> None:
    _download_batch(BAFIN_PDFS, config.raw_bafin_dir, "BaFin")