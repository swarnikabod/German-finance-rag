from typing import Iterable, List, Set, Tuple

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import Config
from src.embeddings.model import get_embeddings

def get_vectorstore(config: Config) -> Chroma:
    config.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name="german_finance_rag",
        embedding_function=get_embeddings(config),
        persist_directory=str(config.chroma_persist_dir),
    )


def _doc_key(doc: Document) -> Tuple[str, int | None]:
    return str(doc.metadata.get("source", "")), doc.metadata.get("page")


def upsert_documents(docs: Iterable[Document], config: Config) -> int:
    vectorstore = get_vectorstore(config)
    docs_list = list(docs)
    batch_size = 500
    total_added = 0
    for i in range(0, len(docs_list), batch_size):
        batch = docs_list[i:i + batch_size]
        vectorstore.add_documents(batch)
        total_added += len(batch)
        print(f"  Embedded {total_added}/{len(docs_list)} chunks...")
    return total_added

def get_retriever(config):
    db = get_vectorstore(config)
    return db.as_retriever(
        search_type="similarity",   # changed from "mmr"
        search_kwargs={"k": config.top_k},
    )


def get_collection_size(config: Config) -> int:
    return get_vectorstore(config)._collection.count()

