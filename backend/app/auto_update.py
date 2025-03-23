import os
import time
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.faiss_search import chunk_text, INDEX_FILE, METADATA_FILE

TEXT_FOLDER = "extracted_texts"
CHECK_INTERVAL = 60  # Check for new files every 60 seconds
CHUNK_SIZE = 500  

# Load FAISS index & embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
index = faiss.read_index(INDEX_FILE)
metadata = np.load(METADATA_FILE, allow_pickle=True).tolist()

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def update_faiss():
    """Scans for new PDFs, extracts text, and adds them to FAISS."""
    new_files = [f for f in os.listdir(TEXT_FOLDER) if f.endswith(".pdf")]
    
    if not new_files:
        return

    print(f"📂 Found {len(new_files)} new PDFs! Updating FAISS...")

    new_chunks = []
    new_metadata = []
    
    for filename in new_files:
        pdf_path = os.path.join(TEXT_FOLDER, filename)
        text = extract_text_from_pdf(pdf_path)
        text_chunks = chunk_text(text, CHUNK_SIZE)
        
        for i, chunk in enumerate(text_chunks):
            new_chunks.append(chunk)
            new_metadata.append((filename, i))

    # Convert to embeddings & update FAISS
    embeddings = model.encode(new_chunks, convert_to_numpy=True)
    index.add(embeddings)
    metadata.extend(new_metadata)

    # Save updated FAISS index
    faiss.write_index(index, INDEX_FILE)
    np.save(METADATA_FILE, np.array(metadata, dtype=object))

    print("✅ FAISS updated with new documents!")

# Continuously check for new PDFs
if __name__ == "__main__":
    print("🔄 Auto-update script running...")
    while True:
        update_faiss()
        time.sleep(CHECK_INTERVAL)
