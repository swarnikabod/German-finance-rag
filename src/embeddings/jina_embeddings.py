from typing import List
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings


class JinaEmbeddings(Embeddings):
    def __init__(self, model_name: str = "intfloat/multilingual-e5-base"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # E5 models need "passage: " prefix for documents
        prefixed = [f"passage: {t}" for t in texts]
        return self.model.encode(
            prefixed,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

    def embed_query(self, text: str) -> List[float]:
        # E5 models need "query: " prefix for queries
        return self.model.encode(
            f"query: {text}",
            normalize_embeddings=True,
        ).tolist()