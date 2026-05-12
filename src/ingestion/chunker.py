from typing import Dict, List

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import Config


def chunk_pages(pages: List[Dict], config: Config) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    documents: List[Document] = []
    for page in pages:
        chunks = splitter.split_text(page["text"])
        metadata = {k: v for k, v in page.items() if k != "text"}
        for chunk in chunks:
            documents.append(Document(page_content=chunk, metadata=metadata))
    return documents

