import sys
sys.path.insert(0, ".")
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    encode_kwargs={"normalize_embeddings": True}
)
db = Chroma(persist_directory="data/processed/chroma", embedding_function=embeddings)
q = "deposit facility rate December 2024"
docs = db.similarity_search(q, k=8)
print(f"Results: {len(docs)}")
for d in docs:
    src = d.metadata.get("source", "?")
    pg = d.metadata.get("page", "?")
    print(f"\n--- {src} p{pg} ---")
    print(d.page_content[:300])
