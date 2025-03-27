import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL","http://localhost:11434/api/generate")

INDEX_FILE = "data/faiss_index.bin"
METADATA_FILE = "data/metadata.npy"
TEXT_FOLDER = "extracted_texts"
CHUNK_SIZE = 500