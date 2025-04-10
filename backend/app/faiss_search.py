import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
import glob
from dotenv import load_dotenv
import logging
import time

load_dotenv()

# --- Configuration ---
INDEX_FILE = os.getenv("INDEX_FILE", "data/faiss_index.bin")
METADATA_FILE = os.getenv("METADATA_FILE", "data/metadata.npy")
TEXT_FOLDER = os.getenv("TEXT_FOLDER", "extracted_texts")
# --- Use Multilingual Embedding Model ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
# --- Use Cross-Encoder Model ---
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 400))
# --- Retrieval & Re-ranking K values ---
FAISS_RETRIEVAL_K = int(os.getenv("FAISS_RETRIEVAL_K", 10)) # How many to get from FAISS initially
FINAL_CONTEXT_K = int(os.getenv("FINAL_CONTEXT_K", 4)) # How many to send to LLM after re-ranking
# --- End Configuration ---

# --- Initialize models globally (load once) ---
try:
    logging.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    logging.info("Embedding model loaded.")
except Exception as e:
    logging.error(f"Failed to load embedding model {EMBEDDING_MODEL}: {e}", exc_info=True)
    embedding_model = None

try:
    logging.info(f"Loading cross-encoder model: {CROSS_ENCODER_MODEL}")
    cross_encoder_model = CrossEncoder(CROSS_ENCODER_MODEL)
    logging.info("Cross-encoder model loaded.")
except Exception as e:
    logging.error(f"Failed to load cross-encoder model {CROSS_ENCODER_MODEL}: {e}", exc_info=True)
    cross_encoder_model = None
# --- End Model Initialization ---

def load_texts_for_retrieval(text_folder, required_files):
    """Loads content only for specified files."""
    loaded_texts = {}
    if not os.path.isdir(text_folder):
        logging.error(f"Text folder not found during retrieval: {text_folder}")
        return loaded_texts
    for filename in required_files:
        file_path = os.path.join(text_folder, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    loaded_texts[filename] = file.read()
            except Exception as e:
                logging.error(f"Error reading required file {filename} during search: {e}")
        else:
            logging.warning(f"Required file {filename} from metadata not found in {text_folder}")
    return loaded_texts

def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Splits text into smaller chunks by words."""
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def search_faiss(query_en, # Expect English query for search/reranking
                 index_file=INDEX_FILE,
                 metadata_file=METADATA_FILE,
                 text_folder=TEXT_FOLDER,
                 retrieval_k=FAISS_RETRIEVAL_K,
                 final_k=FINAL_CONTEXT_K):
    """
    Search FAISS using an English query, retrieve initial candidates,
    re-rank using a Cross-Encoder, and return the top N most relevant chunks.
    """
    start_time = time.time()
    logging.info(f"Starting FAISS search & re-ranking for query (en): '{query_en[:50]}...'")

    if not embedding_model or not cross_encoder_model:
        logging.error("Search cannot proceed: Embedding or Cross-encoder model not loaded.")
        return ""
    if not os.path.exists(index_file) or not os.path.exists(metadata_file):
         logging.error(f"FAISS index file ({index_file}) or metadata file ({metadata_file}) not found.")
         return ""

    try:
        # 1. Encode the English query using the Multilingual model
        query_embedding = embedding_model.encode([query_en], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding) # Normalize query embedding

        # 2. Load FAISS Index and Metadata
        index = faiss.read_index(index_file)
        metadata = np.load(metadata_file, allow_pickle=True)

        # 3. Perform Initial FAISS Search
        logging.debug(f"Performing FAISS search with retrieval_k={retrieval_k}")
        distances, indices = index.search(query_embedding, retrieval_k)
        faiss_time = time.time()
        logging.debug(f"FAISS search completed in {faiss_time - start_time:.4f} seconds.")

        if indices.size == 0 or indices[0][0] == -1: # Check if search returned anything
            logging.info("FAISS search returned no initial candidates.")
            return ""

        # 4. Retrieve Initial Text Chunks
        initial_chunks_data = [] # Store tuples of (chunk_text, original_metadata_index)
        required_files = set()
        valid_indices = [idx for idx in indices[0] if 0 <= idx < len(metadata)]

        for idx in valid_indices:
            filename, _ = metadata[idx]
            required_files.add(filename)

        # Load only necessary text files
        loaded_texts = load_texts_for_retrieval(text_folder, required_files)

        # Process valid indices to get chunks
        for idx in valid_indices:
            filename, chunk_index = metadata[idx]
            if filename in loaded_texts:
                full_text = loaded_texts[filename]
                chunks = chunk_text(full_text, CHUNK_SIZE)
                if 0 <= chunk_index < len(chunks):
                    initial_chunks_data.append((chunks[chunk_index], idx)) # Keep track of original index if needed
                else:
                    logging.warning(f"Chunk index {chunk_index} out of range for file {filename} (found {len(chunks)} chunks)")

        if not initial_chunks_data:
            logging.info("No valid text chunks retrieved after FAISS search.")
            return ""

        logging.info(f"Retrieved {len(initial_chunks_data)} initial candidates from FAISS.")

        # 5. Re-rank using Cross-Encoder
        logging.debug("Starting cross-encoder re-ranking...")
        cross_encoder_input = [[query_en, chunk_data[0]] for chunk_data in initial_chunks_data]
        cross_scores = cross_encoder_model.predict(cross_encoder_input, show_progress_bar=False)
        rerank_time = time.time()
        logging.debug(f"Cross-encoder prediction completed in {rerank_time - faiss_time:.4f} seconds.")

        # Combine chunks with their scores
        scored_chunks = list(zip([chunk_data[0] for chunk_data in initial_chunks_data], cross_scores))

        # Sort by score (descending)
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        # 6. Select Top N Chunks after Re-ranking
        top_reranked_chunks = [chunk[0] for chunk in scored_chunks[:final_k]]

        end_time = time.time()
        logging.info(f"Search & re-ranking completed in {end_time - start_time:.4f} seconds. Returning {len(top_reranked_chunks)} chunks.")

        # Join the best chunks for the final context
        return "\n---\n".join(top_reranked_chunks)

    except FileNotFoundError as e:
        logging.error(f"FAISS file access error during search: {e}")
        return ""
    except Exception as e:
        logging.error(f"Error during FAISS search or re-ranking: {e}", exc_info=True)
        return ""