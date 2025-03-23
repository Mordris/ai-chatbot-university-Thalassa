import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from app.faiss_search import search_faiss
from app.ai_response import generate_ai_response
from app.translation import translate_to_english, translate_to_turkish, detect_language

app = FastAPI()

# Allow CORS for React app running on localhost:3000
origins = [
    "http://localhost:3000",  # Allow React frontend on this origin
]

# Add CORS middleware to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Can also use ["*"] to allow all origins (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/chat")
def chat(query: str):
    """Chatbot API: Detects query language, validates length, searches FAISS, and returns response."""
    
    if len(query) > 100:
        return {"error": "Message cannot exceed 100 characters."}

    logging.info(f"Received query: {query}")
    
    # Detect language
    original_lang = detect_language(query)
    logging.info(f"Detected language: {original_lang}")

    # Translate Turkish queries to English for better performance
    if original_lang == "tr":
        translated_query, _ = translate_to_english(query)
        logging.info(f"Translated query to English: {translated_query}")
    else:
        translated_query = query  # No translation needed if it's already in English

    # Search FAISS
    results = search_faiss(translated_query, "data/faiss_index.bin", "data/metadata.npy", "extracted_texts")

    if isinstance(results, list) and results[0] != "Üzgünüm, bu konuda yeterli bilgiye sahip değilim.":
        context = "\n".join([f"{r[0]}, Chunk: {r[1]}" for r in results])
        logging.info(f"FAISS returned {len(results)} relevant results.")
    else:
        context = ""
        logging.warning("FAISS did not return useful information. AI will generate an answer.")

    # Generate AI response (in English since query is in English)
    answer = generate_ai_response(context, translated_query)

    # Translate the response back to Turkish if the original query was in Turkish
    if original_lang == "tr":
        logging.info("Translating response back to Turkish.")
        answer = translate_to_turkish(answer)

    return {"query": query, "answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
