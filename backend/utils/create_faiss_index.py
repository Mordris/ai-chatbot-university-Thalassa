import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import glob
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# --- Configuration ---
TEXT_FOLDER = os.getenv("TEXT_FOLDER", "extracted_texts")
INDEX_FILE = os.getenv("INDEX_FILE", "data/faiss_index.bin")
METADATA_FILE = os.getenv("METADATA_FILE", "data/metadata.npy")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 200))
# --- Use Multilingual Model ---
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
# --- End Configuration ---

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)

def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Splits text into smaller chunks by words."""
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def create_faiss_index(text_folder, index_file, metadata_file, model_name=MODEL_NAME, chunk_size=CHUNK_SIZE):
    """Extracts text, creates embeddings using the specified model, and saves FAISS index."""
    logging.info(f"Starting FAISS index creation process...")
    logging.info(f"--- Using Embedding Model: {model_name} ---") # Highlight model change
    logging.info(f"Text folder: {text_folder}")
    logging.info(f"Chunk size: {chunk_size} words")

    try:
        model = SentenceTransformer(model_name)
        logging.info(f"Successfully loaded model '{model_name}'.")
    except Exception as e:
        logging.error(f"Failed to load SentenceTransformer model '{model_name}': {e}", exc_info=True)
        return

    documents = []
    metadata = [] # Stores tuples of (filename, chunk_index)

    if not os.path.isdir(text_folder):
        logging.error(f"Text folder not found: {text_folder}")
        return

    # Load text files and split into chunks
    logging.info("Loading and chunking text files...")
    found_files = False
    for filename in os.listdir(text_folder):
        if filename.endswith(".txt"):
            # Avoid indexing the merged file itself if it exists
            if filename == 'hepsi.txt':
                continue
            found_files = True
            file_path = os.path.join(text_folder, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    if not text or text.isspace():
                        logging.warning(f"Skipping empty file: {filename}")
                        continue

                    text_chunks = chunk_text(text, chunk_size)
                    logging.info(f"Processed '{filename}': {len(text_chunks)} chunks created.")

                    for i, chunk in enumerate(text_chunks):
                        documents.append(chunk)
                        metadata.append((filename, i)) # Store filename and chunk index
            except Exception as e:
                logging.error(f"Failed to read or process file {filename}: {e}")

    if not found_files:
        logging.warning(f"No .txt files found in {text_folder} to index.")
        # Consider creating empty index/metadata if needed downstream
        return

    if not documents:
        logging.error("No documents could be processed into chunks. Aborting index creation.")
        return

    # Generate embeddings for the text chunks
    logging.info(f"Generating embeddings for {len(documents)} chunks (this may take time)...")
    try:
        embeddings = model.encode(documents, convert_to_numpy=True, show_progress_bar=True)
    except Exception as e:
        logging.error(f"Failed to encode documents: {e}", exc_info=True)
        return

    # Create the FAISS index (using L2 distance)
    dimension = embeddings.shape[1]
    # Use IndexFlatIP (Inner Product) which is equivalent to Cosine Similarity for normalized vectors
    index = faiss.IndexFlatIP(dimension)
    logging.info(f"Created FAISS index with dimension: {dimension} using IndexFlatIP.")

    # Normalize the embeddings (essential for IndexFlatIP / Cosine Similarity)
    logging.info("Normalizing embeddings...")
    faiss.normalize_L2(embeddings)

    # Add embeddings to the index
    logging.info("Adding embeddings to the index...")
    index.add(embeddings)
    logging.info(f"Successfully added {index.ntotal} vectors to the index.")

    # Save the FAISS index to a file
    logging.info(f"Saving FAISS index to {index_file}...")
    try:
        faiss.write_index(index, index_file)
        logging.info("FAISS index saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save FAISS index: {e}")
        return

    # Save the metadata
    logging.info(f"Saving metadata to {metadata_file}...")
    try:
        np.save(metadata_file, np.array(metadata, dtype=object))
        logging.info("Metadata saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save metadata: {e}")

    logging.info("FAISS index creation process completed.")

if __name__ == "__main__":
    create_faiss_index(TEXT_FOLDER, INDEX_FILE, METADATA_FILE)