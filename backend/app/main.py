import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from datetime import date
import uuid # For session IDs
from typing import List, Dict, Optional # For type hinting

# Import your functions
from app.faiss_search import search_faiss
from app.ai_response import generate_ai_response
from app.translation import detect_language, translate_to_english

# Load environment variables
load_dotenv()
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", 3)) # Max User+Assistant pairs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="Thalassa AI Assistant API (Enhanced RAG)")

# --- Simple In-Memory Conversation History Store ---
# WARNING: This is for demonstration ONLY. It's not persistent, not scalable,
#          and will lose history if the server restarts.
#          Use a database or proper session management in production.
conversation_memory: Dict[str, List[Dict[str, str]]] = {}
# --- End Memory Store ---

# CORS Middleware
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Thalassa AI Assistant API (Enhanced RAG)"}

@app.get("/chat")
async def chat(query: str,
               session_id: Optional[str] = Query(None, description="Unique ID for the conversation session.")):
    """
    Enhanced Chatbot API endpoint: Handles context retrieval with re-ranking,
    conversation history, date awareness, and few-shot prompting via OpenAI.
    Returns the answer along with the session ID.
    """
    MAX_QUERY_LENGTH = 200

    # --- Session ID Handling ---
    if session_id is None:
        session_id = str(uuid.uuid4())
        logging.info(f"No session ID provided, generated new one: {session_id}")
    else:
        logging.info(f"Using existing session ID: {session_id}")
    # --- End Session ID Handling ---

    if not query or query.isspace():
        logging.warning(f"[{session_id}] Received empty query.")
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if len(query) > MAX_QUERY_LENGTH:
        logging.warning(f"[{session_id}] Query exceeds maximum length: {len(query)} chars.")
        raise HTTPException(
            status_code=400,
            detail=f"Message cannot exceed {MAX_QUERY_LENGTH} characters."
        )

    logging.info(f"[{session_id}] Received original query: '{query}'")

    # Get Current Date
    today_str = date.today().strftime("%Y-%m-%d")
    logging.info(f"[{session_id}] Current date for context: {today_str}")

    # 1. Detect Language
    original_lang = detect_language(query)
    logging.info(f"[{session_id}] Detected language: {original_lang}")

    # 2. Translate Query to English FOR FAISS SEARCH (if necessary)
    if original_lang != "en":
        search_query, _ = translate_to_english(query)
        logging.info(f"[{session_id}] Translated query for search/re-ranking: '{search_query}'")
    else:
        search_query = query

    # 3. Search FAISS & Re-rank for Context using the ENGLISH query
    logging.info(f"[{session_id}] Searching FAISS & re-ranking with English query...")
    # search_faiss internally uses FINAL_CONTEXT_K from env/defaults now
    context = search_faiss(search_query)

    if context:
        logging.info(f"[{session_id}] FAISS search & re-ranking returned context based on '{search_query}'.")
    else:
        logging.warning(f"[{session_id}] FAISS search & re-ranking returned no relevant context for '{search_query}'.")
        context = "İlgili bağlam bilgisi bulunamadı." if original_lang == 'tr' else "No relevant context found."

    # --- Retrieve Conversation History ---
    history = conversation_memory.get(session_id, [])
    logging.info(f"[{session_id}] Retrieved history length: {len(history)//2} turns.")
    # --- End History Retrieval ---

    # 4. Generate AI Response using OpenAI (passing history and date)
    logging.info(f"[{session_id}] Generating AI response for original query: '{query}' with history and date...")
    final_answer = generate_ai_response(context, query, today_str, history)
    logging.info(f"[{session_id}] AI response generated.")

    # --- Update Conversation History ---
    # Ensure history doesn't grow indefinitely
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": final_answer})
    # Keep only the last MAX_HISTORY_TURNS * 2 messages (user + assistant)
    if len(history) > MAX_HISTORY_TURNS * 2:
        history = history[-(MAX_HISTORY_TURNS * 2):]
    conversation_memory[session_id] = history
    logging.info(f"[{session_id}] Updated history. New length: {len(history)//2} turns.")
    # --- End History Update ---

    # 5. Return the response including the session ID
    return {"query": query, "answer": final_answer, "session_id": session_id}


# Direct run block
if __name__ == "__main__":
    import uvicorn
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        print("\nERROR: OPENAI_API_KEY not set.\n")
    else:
        # Check other critical dependencies maybe
        try:
             import faiss
             import sentence_transformers
             import langdetect
             import requests
             from datetime import date
             import uuid
        except ImportError as e:
             print(f"\nERROR: Missing dependency: {e}. Run 'pip install -r requirements.txt'.\n")
        else:
             print("--- Starting FastAPI Server ---")
             print(f"Max History Turns: {MAX_HISTORY_TURNS}")
             print(f"Embedding Model: {os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-mpnet-base-v2')}")
             print(f"Cross Encoder Model: {os.getenv('CROSS_ENCODER_MODEL', 'cross-encoder/ms-marco-MiniLM-L-6-v2')}")
             print(f"LLM Model: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
             uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)