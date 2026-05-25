import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass
class Config:
    embedding_model: str = "intfloat/multilingual-e5-base"
    chunk_size: int = 256
    chunk_overlap: int = 128
    top_k: int = 6
    chroma_persist_dir: Path = field(default_factory=lambda: Path("data/processed/chroma"))
    raw_ecb_dir: Path = field(default_factory=lambda: Path("data/raw/ecb"))
    raw_bafin_dir: Path = field(default_factory=lambda: Path("data/raw/bafin"))
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma3:1b")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_model: str = "gemma3:1b"
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")