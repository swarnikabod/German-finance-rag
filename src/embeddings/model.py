from src.config import Config
from src.embeddings.jina_embeddings import JinaEmbeddings


def get_embeddings(config: Config):
    return JinaEmbeddings(model_name=config.embedding_model)