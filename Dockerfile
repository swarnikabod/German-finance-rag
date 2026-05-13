FROM python:3.11-slim

WORKDIR /app

# System deps for PyMuPDF and ChromaDB
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Download embedding model at build time so startup is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')"

# Download ChromaDB from HuggingFace Hub at build time
RUN python -c "
from huggingface_hub import snapshot_download
import shutil, os
path = snapshot_download(repo_id='swarnikabod/german-finance-rag-db', repo_type='dataset')
os.makedirs('data/processed', exist_ok=True)
shutil.copytree(path, 'data/processed/chroma', dirs_exist_ok=True)
print('ChromaDB downloaded')
"

EXPOSE 7860

CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=7860", "--server.address=0.0.0.0"]
