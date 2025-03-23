import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import glob

def load_texts(text_folder):
    """Loads all text files in the given folder."""
    texts = []
    for file_path in glob.glob(os.path.join(text_folder, "*.txt")):
        with open(file_path, 'r', encoding='utf-8') as file:
            texts.append(file.read())
    return texts

def chunk_text(text, chunk_size=500):
    """Splits text into smaller chunks."""
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def search_faiss(query, index_file, metadata_file, text_folder, model_name="sentence-transformers/all-MiniLM-L6-v2", top_k=3):
    """Search FAISS for the most relevant document chunks."""
    # Load texts and metadata
    texts = load_texts(text_folder)
    model = SentenceTransformer(model_name)
    
    # Encode query
    query_embedding = model.encode([query])
    
    # Load the FAISS index
    index = faiss.read_index(index_file)
    
    # Search FAISS
    _, indices = index.search(query_embedding, top_k)
    metadata = np.load(metadata_file, allow_pickle=True)

    # Convert NumPy array to a list
    results = [tuple(metadata[idx]) for idx in indices[0] if idx < len(metadata)]  # Avoid out-of-range errors
    
    return results if results else ["Üzgünüm, bu konuda yeterli bilgiye sahip değilim."]
