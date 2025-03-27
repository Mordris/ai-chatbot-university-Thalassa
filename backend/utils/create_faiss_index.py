import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import glob

# Configuration
TEXT_FOLDER = "extracted_texts"
INDEX_FILE = "data/faiss_index.bin"
METADATA_FILE = "data/metadata.npy"
CHUNK_SIZE = 500  # You can adjust this value if needed
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # Sentence Transformer model

# Load text files from the folder
def load_texts(text_folder):
    texts = []
    for file_path in glob.glob(os.path.join(text_folder, "*.txt")):
        with open(file_path, 'r', encoding='utf-8') as file:
            texts.append(file.read())
    return texts

# Split text into smaller chunks
def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Splits text into smaller chunks."""
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# Create and save the FAISS index
def create_faiss_index(text_folder, index_file, model_name=MODEL_NAME, chunk_size=CHUNK_SIZE):
    """Extracts text, creates embeddings, and saves FAISS index."""
    model = SentenceTransformer(model_name)

    documents = []
    metadata = []

    # Load text files and split into chunks
    for filename in os.listdir(text_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(text_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                text_chunks = chunk_text(text, chunk_size)
                for i, chunk in enumerate(text_chunks):
                    documents.append(chunk)
                    metadata.append((filename, i))

    # Generate embeddings for the text chunks
    embeddings = model.encode(documents, convert_to_numpy=True)

    # Create the FAISS index (using L2 distance)
    dimension = embeddings.shape[1]  # Embedding dimensions (length of the embedding vector)
    index = faiss.IndexFlatL2(dimension)  # L2 distance flat index

    # Normalize the embeddings (FAISS works better with normalized vectors)
    faiss.normalize_L2(embeddings)

    # Add embeddings to the index
    index.add(embeddings)

    # Save the FAISS index to a file
    faiss.write_index(index, index_file)

    # Save the metadata (document references) to a file
    np.save(METADATA_FILE, np.array(metadata, dtype=object))

    print(f"FAISS index created and saved to {index_file}")
    print(f"Metadata saved to {METADATA_FILE}")

if __name__ == "__main__":
    # Run the index creation
    create_faiss_index(TEXT_FOLDER, INDEX_FILE)
