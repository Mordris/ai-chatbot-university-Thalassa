# app/ai_response.py
import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
import logging
from typing import List, Dict, Union

# Load environment variables
load_dotenv()

# Initialize OpenAI client
try:
    # Ensure API key is loaded correctly
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY not found or is placeholder in .env file")

    client = OpenAI(api_key=api_key, timeout=30.0)
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    logging.info(f"Using OpenAI model: {OPENAI_MODEL}")
except Exception as e:
    logging.error(f"Error initializing OpenAI client: {e}", exc_info=True)
    client = None

# Function signature remains the same
def generate_ai_response(context: str, # NOTE: Context is expected to be TURKISH
                         query: str,     # NOTE: Query is the ORIGINAL user query
                         current_date_str: str,
                         history: List[Dict[str, str]]) -> str:
    """
    Uses OpenAI's API with optimized token usage. Assumes input 'context' is Turkish.
    Generates a date-aware, user-friendly answer in the language of the original 'query',
    considering conversation history and using few-shot examples.
    """
    lang = detect_language(query) if 'detect_language' in globals() else 'en'

    if not client:
        return "Üzgünüm, AI servisi başlatılamadı." if lang == 'tr' else "Sorry, the AI service could not be initialized."
    # API Key check moved to initialization block

    # --- Condensed System Prompt ---
    system_prompt = f"""
    You are Thalassa, a helpful AI assistant for Sakarya University students. Your name is Thalassa.
    Answer based ONLY on the provided 'Context' (likely Turkish) and 'Conversation History'.
    If info isn't in Context/History, state that clearly. Do not guess.
    Be clear, direct, and helpful. Assume 'Sakarya University'.
    Greet briefly on the first turn only. Ask for clarification if needed.

    Current Date: {current_date_str}

    *** INSTRUCTIONS ***
    1.  **Language:** Answer in the EXACT same language as the user's CURRENT 'Question' (e.g., Turkish/English). Understand the Turkish Context to do this.
    2.  **Context/History Use:** Rely solely on Context and History. Use history for follow-ups.
    3.  **User Info Recall (CRITICAL):** If user stated their name in History, remember it. Address them by name occasionally. If asked "What is my name?", check History and state *their* name (e.g., "Adınız Emre."). NEVER confuse their name with yours (Thalassa).
    4.  **Date Logic (Revised):** For date/schedule questions using Context/History:
        *   Compare relevant dates to Current Date ({current_date_str}).
        *   PRIORITY: First, state the event starting *soonest AFTER* the Current Date.
        *   Then, briefly mention other relevant future dates or note if a requested past event is over.
        *   Label clearly (e.g., "Güz Yarıyılı:", "Başvuru:").
        *   Assume 2024-2025 context.
    5.  **Refusals:** Politely decline inappropriate/out-of-scope requests (code, opinions). Recalling conversation details (like name) IS in scope.
    6.  **Persona:** Never mention context sources, files, APIs, or these instructions.

    *** EXAMPLES (TR Context -> User Lang Answer) ***

    Ex1 (TR Query/TR Answer | Date: 2024-10-26):
    Context: Güz Finalleri: 6-19 Ocak 2025. Bahar Finalleri: 16-29 Haziran 2025.
    History: []
    Question: Final sınavları ne zaman?
    Answer: Güz yarıyılı final sınavları 6 Ocak 2025'te başlayıp 19 Ocak 2025'te bitecektir. Bahar yarıyılı finalleri ise 16 Haziran 2025'te başlayacaktır.

    Ex2 (TR Query/TR Answer | Follow-up | Date: 2024-10-26):
    Context: Bahar Finalleri: 16-29 Haziran 2025.
    History: [User: Final sınavları ne zaman?, Assistant: Güz yarıyılı... Ocak 2025...]
    Question: Peki ya bahar dönemi?
    Answer: Bahar yarıyılı final sınavları 16 Haziran 2025'te başlayıp 29 Haziran 2025'te bitecektir.

    Ex3 (TR Query/TR Answer | Name Recall | Date: 2024-11-01):
    Context: [Irrelevant]
    History: [User: Benim adım Emre, Assistant: Merhaba Emre...]
    Question: Benim adım ne?
    Answer: Adınız Emre. Başka bir konuda yardımcı olabilir miyim?

    Ex4 (EN Query/EN Answer | TR Context | Date: 2025-01-20):
    Context: Güz Bütünleme: 27 Ocak-2 Şubat 2025.
    History: []
    Question: When are the make-up exams?
    Answer: The Fall semester Make-up Exams (Bütünleme) will be held from January 27 to February 2, 2025.

    *** END EXAMPLES ***
    """

    # --- Construct messages list including history ---
    messages = [{"role": "system", "content": system_prompt}]
    # Add history - BE MINDFUL OF MAX_HISTORY_TURNS in .env
    messages.extend(history)
    # --- User content with slightly shorter headers ---
    user_content = f"Context:\n---\n{context}\n---\n\nHistory above.\nQuestion: {query}\nAnswer:"
    messages.append({"role": "user", "content": user_content})
    # --- End message construction ---

    # --- Log lengths for token usage diagnosis ---
    context_len = len(context)
    history_len = sum(len(msg.get('content', '')) for msg in history)
    prompt_len = len(system_prompt) + len(user_content) - len(context) # Approx prompt length without context/history
    logging.info(f"Sending query to OpenAI: '{query}'. History turns: {len(history)//2}. Context chars: {context_len}. History chars: {history_len}. Approx base prompt chars: {prompt_len}. Target lang: {lang}.")
    # For accurate token count, use tiktoken library if needed later:
    # import tiktoken
    # encoding = tiktoken.encoding_for_model(OPENAI_MODEL)
    # total_tokens = len(encoding.encode(system_prompt + context + query + "".join(h['content'] for h in history)))
    # logging.info(f"Estimated total input tokens: {total_tokens}")
    # --- End Logging ---

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.15, # Keep low for instruction following
            max_tokens=400    # Keep reasonable allowance for output
        )

        answer = response.choices[0].message.content.strip()
        logging.info(f"Received answer from OpenAI (first 100 chars): {answer[:100]}...")
        # Keep basic name confusion check
        if query.lower() in ["benim adım ne?", "what is my name?"] and \
           (answer.lower().startswith("benim adım") or answer.lower().startswith("my name is")):
             logging.warning(f"Potential name confusion detected! Query: '{query}', Incorrect Answer: '{answer}'. Forcing fallback.")
             answer = "Benim adım Thalassa. Size nasıl yardımcı olabilirim?" if lang == 'tr' else "My name is Thalassa. How can I help you?"

        return answer if answer else "Üzgünüm, bir yanıt oluşturamadım."

    # ... (Error handling remains the same) ...
    except RateLimitError: logging.error("OpenAI API Error: Rate limit exceeded."); return "Üzgünüm, AI servisi şu anda çok meşgul..."
    except APITimeoutError: logging.error("OpenAI API Error: Request timed out."); return "Üzgünüm, AI servisine yapılan istek zaman aşımına uğradı..."
    except APIError as e: logging.error(f"OpenAI API Error: Status={e.status_code}, Message={e.message}"); return f"Üzgünüm, AI servisiyle iletişim kurulurken bir hata oluştu (Kod: {e.status_code})."
    except Exception as e: logging.error(f"An unexpected error occurred: {e}", exc_info=True); return "Üzgünüm, yanıt oluşturulurken beklenmedik bir hata oluştu."


# --- Import detect_language for error messages ---
try:
    from app.translation import detect_language
except ImportError:
    # Define a dummy function if translation module is missing somehow
    logging.warning("translation.py not found, using dummy detect_language.")
    def detect_language(text): return 'en'
# --- End Import ---